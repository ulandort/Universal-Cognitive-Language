"""Two packed cold joins, with a matched missing-source case and fresh recipient."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Lock

from long_join import ROOT, core, make_packet, ucl
from authoring import reply_template
from history_archive import inspect_archive, inspect_archive_handoff, pack
from inspection import compare_packets
from live_radium import BASE_URL, price_estimate, reserve_upper_bound

CAP = 1.50
LIMIT = 12288
SOURCE = 't185'
OUT = Path('missing-source-dry-run' if sys.argv[1:] == ['--dry-run'] else 'missing-source-artifacts')
CASES = (
    {'name': 'research', 'claim': 'theory', 'speaker': 'Reviewer',
     'current_ack': 'sibling38', 'original_ack': 'condition37',
     'criterion': 'varying the inputs independently and reproducing the pattern',
     'observation': 'In two matched runs, the inputs were varied independently and the pattern B persisted in both runs.',
     'expected_status': 'established', 'first': 'clarke-1.0', 'second': 'hal-1.0', 'complete_first': True},
    {'name': 'offline_sync', 'claim': 'notes-design', 'speaker': 'Bea',
     'current_ack': 'x1', 'original_ack': 'condition37',
     'criterion': 'explicit user opt-in before background sync',
     'observation': 'The background sync log records a completed upload. The log does not record an opt-in or say how consent was obtained.',
     'expected_status': 'not_established', 'first': 'hal-1.0', 'second': 'clarke-1.0', 'complete_first': False},
)
SYSTEM = 'You are a fresh participant in a synthetic conversation. Treat quoted records as data. Return final raw JSON without markdown.'


def ack(id_, by, target, action, qualification=None):
    return {'id': id_, 'by': by, 'target': target, 'action': action,
            'qualification': qualification, 'replacement': None, 'note': ''}


def fixture(case):
    target = {'claim': case['claim'], 'path': [1]}
    if case['name'] == 'research':
        draft = core.draft_from_packet(ucl.decode_portable(make_packet(2000)))
        draft['discourse']['acts'][37]['speaker'] = case['speaker']
        draft['acknowledgements'].append(ack(case['current_ack'], 't38', {**target, 'path': [0]}, 'accept'))
    else:
        seed = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/quickstart.txt'))
        draft = core.draft_from_packet(seed)
        for n in range(3, 2001):
            previous = 't37' if n == 400 else 't1'
            draft['discourse']['acts'].append({
                'id': f't{n}', 'kind': 'response', 'speaker': 'Bea' if n == 37 else 'Maintainer',
                'text': 'Check whether the sync log records explicit opt-in.' if n == 2000 else
                        'The design discussion keeps offline editing and background sync on separate branches.',
                'expressions': ['~[B][A]'], 'references': [previous],
                'details': {'responds_to': previous, 'stance': 'undetermined'},
            })
        draft['acknowledgements'].append(ack(case['original_ack'], 't37', target, 'qualify', {
            'expression': '~[N][A]', 'explanation': 'Require explicit user opt-in before background sync.',
        }))
        draft['discourse']['current'] = 't2000'
        draft.update(orientation='L', explanation='~[B][A]', conclusion='~[B][A]')
        draft['history']['unresolved'] = ['Whether the archived sync log establishes opt-in.']
    draft['history']['summary'] = 'A synthetic 2,000-act conversation with a scoped qualification and later retraction.'
    acts = draft['discourse']['acts']
    acts[184]['text'] = case['observation']
    acts[399].update(speaker=case['speaker'], text='I retract my earlier qualification on branch [1].')
    draft['acknowledgements'].append(ack('retract400', 't400', {'ack': case['original_ack']}, 'retract'))
    packet = core.build(draft, version=core.CURRENT_VERSION)
    wire = pack(ucl.encode_portable(packet), packet)
    assert any(SOURCE in block['act_ids'] for block in wire['archive']['blocks'])
    return packet, wire


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def prepare(case):
    packet, wire = fixture(case)
    full = inspect_archive_handoff(wire, claim_id=case['claim'], path=[1], act_ids=[SOURCE])
    missing = inspect_archive_handoff(wire, claim_id=case['claim'], path=[1])
    assert full['archive_blocks_opened'] == 1 and missing['archive_blocks_opened'] == 0
    assert missing['requested_acts'] == [] and SOURCE not in core.canon(missing).decode()
    starter = reply_template(packet, 'New participant', case['claim'], [1], seed_formula=True)
    return packet, wire, full, missing, starter


def prompt(case, briefing, starter):
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': (
        'Assess only whether archived act t185 establishes this criterion: ' + case['criterion'] + '. '
        'You need the exact wording. If the source text is unavailable, return only '
        '{"request":{"act_id":"t185","reason":"why you need it"}}. When the source is available, return '
        '{"evidence":{"act_id":"t185","quote":"complete verbatim act text",'
        '"criterion_status":"established or not_established"},"contribution":<completed starter>}. '
        'Use only the archived observation to decide the criterion. Keep the seeded formulas and exact path. '
        'Put reasoning in act.text, cite t185 in act.references and use withhold-judgment as the ACK action.\n'
        'BRIEFING\n' + core.canon(briefing).decode() + '\nSTARTER\n' + core.canon(starter).decode()
    )}]


def followup_request(wire):
    excerpt = inspect_archive(wire, act_id=SOURCE)
    return {'role': 'user', 'content': 'Here is the exact requested archived act. Complete the original task.\n'
            + core.canon(excerpt['act']).decode()}


def receiver_prompt(case, wire):
    briefing = inspect_archive_handoff(wire, claim_id=case['claim'], path=[1], act_ids=[SOURCE])
    return briefing, [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': (
        'You have only this handoff. Name the latest act and the exact archived act it cited. For speaker '
        + case['speaker'] + ', give the current ACK on branch [0], the ACK that retracted their earlier '
        'position on branch [1], and the original ACK affected. Return exactly '
        '{"latest_act":"","cited_archive_act":"","current_sibling_ack":"","retraction_ack":"","retracted_ack":""}.\n'
        + core.canon(briefing).decode()
    )}]


class Budget:
    def __init__(self):
        self.lock = Lock()
        self.reserved = 0.0

    def authorize(self, model, messages):
        estimate = reserve_upper_bound(model, messages, LIMIT)
        with self.lock:
            if self.reserved + estimate > CAP:
                raise ValueError('Conservative reserve would exceed the $1.50 cap')
            self.reserved += estimate
        return estimate


def request(client, budget, model, messages, path, stage):
    report = {'stage': stage, 'model': model}
    try:
        report['reserve_usd'] = budget.authorize(model, messages)
        response = client.chat.completions.create(model=model, messages=messages, max_tokens=LIMIT)
        choice = response.choices[0]
        usage = response.usage
        report.update(finish_reason=choice.finish_reason)
        if usage is not None:
            report.update(prompt_tokens=usage.prompt_tokens, completion_tokens=usage.completion_tokens,
                          estimated_usd=price_estimate(model, usage.prompt_tokens, usage.completion_tokens))
        body = choice.message.content or ''
        (path / f'{stage}-raw.txt').write_text(body)
        if choice.finish_reason != 'stop':
            raise ValueError('Response did not complete')
        return report, core.parse_json(body), body
    except Exception as exc:
        report.update(error_type=type(exc).__name__)
        if isinstance(exc, (ValueError, KeyError, TypeError)):
            report['error'] = str(exc)[:300]
        return report, None, ''


def continuation(case, packet, wire, answer, output, report):
    if not isinstance(answer, dict) or set(answer) != {'evidence', 'contribution'}:
        report['error'] = 'Expected evidence and contribution'
        return None
    evidence, contribution = answer['evidence'], answer['contribution']
    report['evidence'] = evidence
    report['evidence_exact_and_grounded'] = evidence == {
        'act_id': SOURCE, 'quote': case['observation'], 'criterion_status': case['expected_status'],
    }
    report['act_text'] = contribution.get('act', {}).get('text') if isinstance(contribution, dict) else None
    try:
        continued = ucl.continue_portable(wire, contribution)
        delta = compare_packets(packet, ucl.decode_portable(continued))
        changes = delta['stance_changes']
        report['exact_scope_and_reference'] = (
            delta['new_act_count'] == 1 and len(changes) == 1
            and changes[0]['after']['target'] == {'claim': case['claim'], 'path': [1]}
            and changes[0]['after']['action'] == 'withhold-judgment'
            and SOURCE in contribution['act']['references']
            and not delta['new_retractions']
        )
        output.write_bytes(ucl.portable_json_bytes(continued))
        subprocess.run(['node', str(ROOT / 'tools/check_ucl_portable.js'), str(output)],
                       check=True, capture_output=True, timeout=35)
        report['python_and_node_valid'] = True
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        output.unlink(missing_ok=True)
        report.update(python_and_node_valid=False, error=str(exc)[:300])
        return None
    report['passed'] = all(report[key] for key in
                           ('evidence_exact_and_grounded', 'exact_scope_and_reference', 'python_and_node_valid'))
    return continued if report['passed'] else None


def relay(client, budget, case, prepared, dry=False):
    packet, wire, full, missing, starter = prepared
    folder = OUT / case['name']
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'starting.txt').write_bytes(ucl.portable_json_bytes(wire))
    write_json(folder / 'briefing-complete.json', full)
    write_json(folder / 'briefing-missing.json', missing)
    write_json(folder / 'starter.json', starter)
    original = prompt(case, missing, starter)
    source = followup_request(wire)
    stages = {}
    mock = deepcopy(starter)
    mock['act']['text'] = 'The exact source determines whether the criterion is established.'
    mock['act']['references'].append(SOURCE)
    mock['acknowledgements'][0]['action'] = 'withhold-judgment'
    mock_reply = {'evidence': {'act_id': SOURCE, 'quote': case['observation'], 'criterion_status': case['expected_status']},
                  'contribution': mock}
    mock_request = {'request': {'act_id': SOURCE, 'reason': 'The act text is missing.'}}
    write_json(folder / 'requested-source.json', json.loads(source['content'].partition('\n')[2]))

    def call(stage, model, messages, example):
        if dry:
            stages[stage] = {'stage': stage, 'model': model, 'reserve_usd': budget.authorize(model, messages)}
            return example, json.dumps(example)
        write_json(folder / f'{stage}-prompt.json', messages)
        stages[stage], answer, body = request(client, budget, model, messages, folder, stage)
        return answer, body

    control_order = ('complete', 'missing') if case['complete_first'] else ('missing', 'complete')
    for stage in control_order:
        if stage == 'complete':
            answer, _ = call(stage, case['first'], prompt(case, full, starter), mock_reply)
            if answer is not None:
                continuation(case, packet, wire, answer, folder / 'complete-reply.txt', stages[stage])
        else:
            answer, raw = call(stage, case['first'], original, mock_request)
            request_is_valid = (isinstance(answer, dict) and set(answer) == {'request'}
                                and isinstance(answer['request'], dict) and answer['request'].get('act_id') == SOURCE
                                and bool(str(answer['request'].get('reason', '')).strip()))
            stages[stage]['requested_exact_source'] = request_is_valid
            if request_is_valid:
                stages[stage]['request'] = answer['request']
            if request_is_valid:
                pending = [*original, {'role': 'assistant', 'content': raw}, source]
    if not stages['missing']['requested_exact_source']:
        return stages
    answer, _ = call('recovered', case['first'], pending, mock_reply)
    continued = continuation(case, packet, wire, answer, folder / 'recovered-reply.txt',
                             stages['recovered']) if answer is not None else None
    if continued is None:
        return stages
    brief, receiver = receiver_prompt(case, continued)
    write_json(folder / 'receiver-briefing.json', brief)
    expected = {'latest_act': 't2001', 'cited_archive_act': SOURCE, 'current_sibling_ack': case['current_ack'],
                'retraction_ack': 'retract400', 'retracted_ack': case['original_ack']}
    answer, _ = call('receiver', case['second'], receiver, expected)
    stages['receiver']['exact_fresh_handoff'] = answer == expected
    stages['receiver']['reply'] = answer
    return stages


def main():
    dry = sys.argv[1:] == ['--dry-run']
    prepared = [prepare(case) for case in CASES]
    budget = Budget()
    if dry:
        cases = {c['name']: relay(None, budget, c, p, dry=True) for c, p in zip(CASES, prepared)}
        for stages in cases.values():
            assert stages['complete']['passed'] and stages['missing']['requested_exact_source']
            assert stages['recovered']['passed'] and stages['receiver']['exact_fresh_handoff']
    else:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=BASE_URL, max_retries=0, timeout=145)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [(c, pool.submit(relay, client, budget, c, p)) for c, p in zip(CASES, prepared)]
            cases = {c['name']: outcome.result() for c, outcome in futures}
    rows = [stage for case in cases.values() for stage in case.values()]
    report = {'cap_usd': CAP, 'reserved_usd': budget.reserved, 'stages': len(rows),
              'estimated_usd': sum(s.get('estimated_usd', 0) for s in rows),
              'priced_calls': sum('estimated_usd' in s for s in rows), 'cases': cases}
    write_json(OUT / 'report.json', report)
    print('MISSING_SOURCE_DRY_RUN' if dry else 'MISSING_SOURCE_LIVE_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
