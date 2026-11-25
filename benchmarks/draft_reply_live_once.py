"""Replay Hal's evidence task with an explicit short reply and guarded UCL assembly."""
import json
import os
from pathlib import Path
import subprocess
import sys

import cold_source_map_once as fixture

live = fixture.live
CAP = 0.45
live.CAP = CAP
MODEL = 'hal-1.0'
DRY = sys.argv[1:] == ['--dry-run']
OUT = Path('draft-reply-dry' if DRY else 'draft-reply-live')
SOURCE = fixture.SOURCE
SCOPE = {'claim': fixture.CLAIM, 'path': fixture.PATH}
ACTION = 'withhold-judgment'
CLI = [sys.executable, str(live.ROOT / 'src/ucl.py')]


def verify(wire, briefing, answer):
    fields = {'observation_act', 'quote', 'criterion_status', 'decision'}
    if not isinstance(answer, dict) or set(answer) != fields:
        raise ValueError('Return exactly observation_act, quote, criterion_status, and decision.')
    exact_quote = answer['observation_act'] == SOURCE and answer['quote'] == fixture.EVIDENCE
    grounded = answer['criterion_status'] == 'not_established'
    decision = answer['decision']
    if not isinstance(decision, dict):
        raise ValueError('decision must be an object containing claim, path, action, text, and references.')
    if any(decision.get(key) != value for key, value in SCOPE.items()):
        raise ValueError('The decision must use the same claim and path as the selected branch.')
    digest = briefing['source_packet_sha256']
    basis = OUT / 'starting.txt'
    output = OUT / 'continued.txt'
    result = subprocess.run(
        [*CLI, 'draft-reply', str(basis), '--speaker', 'New participant',
         '--expect-ack-action', ACTION, '--expect-packet-sha256', digest],
        input=live.core.canon(decision), capture_output=True, timeout=45,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode().strip())
    draft = live.core.parse_json(result.stdout)
    if not exact_quote or not grounded or SOURCE not in decision['references']:
        raise ValueError('Quote the original observation exactly, cite its act ID, and distinguish insufficient from missing evidence.')
    (OUT / 'contribution.json').write_bytes(result.stdout)
    local = subprocess.run(
        [*CLI, 'continue', str(basis), str(output), '--expect-packet-sha256', digest],
        input=result.stdout, capture_output=True, text=False, timeout=45,
    )
    if local.returncode:
        raise ValueError(local.stderr.decode().strip())
    node = subprocess.run(['node', str(live.ROOT / 'tools/check_ucl_portable.js'), str(output)],
                          capture_output=True, text=True, timeout=30)
    if node.returncode:
        raise ValueError(node.stderr.strip())
    after = live.ucl.decode_portable(live.ucl.read_json_file(output, limit=live.ucl.MAX_PORTABLE_JSON))
    parent = live.ucl.decode_portable(wire)
    delta = fixture.compare_packets(parent, after)
    changes = delta['stance_changes']
    if (node.stdout and json.loads(node.stdout)['packet_sha256'] == after['integrity']['sha256']
            and delta['new_act_count'] == 1 and len(changes) == 1
            and changes[0]['after']['action'] == ACTION and changes[0]['after']['target'] == SCOPE):
        return {'both_validators': True, 'exact_quote': exact_quote, 'criterion_status': answer['criterion_status'],
                'action': decision['action'], 'response_details_stance': draft['act']['details']['stance'],
                'branch': SCOPE, 'recorded_reasoning': after['discourse']['acts'][-1]['text']}
    raise ValueError('The resulting packet did not match the requested stance and branch.')


def main():
    base = live.ucl.decode_portable(live.make_packet(2000))
    _, wire, briefing, prompts = fixture.prepare(base, 'observation_present')
    selected = {**SCOPE, 'request': [fixture.RULE, SOURCE]}
    focused = fixture.inspect_archive_handoff(wire, claim_id=fixture.CLAIM, path=fixture.PATH, act_ids=selected['request'])
    records = [entry['act'] for entry in focused['requested_acts']]
    prompts += [{'role': 'assistant', 'content': live.dump(selected)}, {'role': 'user', 'content': (
        'Final response. No further lookups are available. Decide what the observation establishes. '
        'Return one raw JSON object with observation_act, quote (exact full observation text), criterion_status, '
        'and decision. The decision object has exactly claim, path, action, text, and references. '
        'Keep the selected claim and path. Cite the observation in references and explain your reasoning in text. '
        'If the observation exists but the criterion is unmet, use criterion_status "not_established" and '
        'choose action "withhold-judgment". The tool fills the UCL response fields from your explicit choice. '
        'Return JSON only with no Markdown fence.\nRETRIEVED RECORDS\n' + live.dump(records)
    )}]
    OUT.mkdir(exist_ok=True)
    (OUT / 'starting.txt').write_bytes(live.ucl.portable_json_bytes(wire))
    client = None
    if not DRY:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=live.BASE_URL,
                        max_retries=0, timeout=145)
    budget = live.Budget()
    mock = {'observation_act': SOURCE, 'quote': fixture.EVIDENCE, 'criterion_status': 'not_established',
            'decision': {**SCOPE, 'action': ACTION, 'text': 'The runs used shared inputs.', 'references': [SOURCE]}}
    attempts = []
    for index in range(2):
        stats, answer, _ = live.call(client, budget, MODEL, prompts, 14336, OUT, f'attempt-{index + 1}', mock=mock)
        attempts.append(stats)
        try:
            stats.update(verify(wire, briefing, answer))
            break
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            stats['feedback'] = str(exc)[:600]
            if isinstance(answer, dict):
                prompts.append({'role': 'assistant', 'content': live.dump(answer)})
            prompts.append({'role': 'user', 'content': 'Review this feedback and return the corrected JSON object. '
                            'Use the existing sources and do not add fields. Feedback: ' + stats['feedback']})
    if DRY:
        assert attempts[0]['both_validators']
    report = {'attempts': attempts, 'cap_usd': CAP, 'reserved_usd': budget.reserved,
              'estimated_usd': sum(call.get('estimated_usd', 0) for call in attempts)}
    live.save(OUT / 'report.json', report)
    print('DRAFT_REPLY_DRY' if DRY else 'DRAFT_REPLY_LIVE', json.dumps(report))


if __name__ == '__main__':
    main()
