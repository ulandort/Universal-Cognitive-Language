"""Two model sessions discover a branch and source from a generated UCL handoff."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import blind_archive_once as live

from authoring import reply_template
from history_archive import inspect_archive_handoff, pack
from inspection import compare_packets

CAP = 0.85
live.CAP = CAP
MODELS = ('hal-1.0',)
CLAIM, PATH, SOURCE, RULE = 'theory', [1], 't18', 't37'
EVIDENCE = ('The earlier observation log records that B persisted in repeated runs using the same inputs. '
            'No independent-input run was performed.')
DRY = sys.argv[1:] == ['--dry-run']
OUT = Path('cold-discovery-dry' if DRY else 'cold-discovery-live')
HAL_RAW = ' ```json\n{\n  "claim": "theory",\n  "path": [1],\n  "request": ["t37", "t18"]\n}\n```'
SYSTEM = 'You are joining a new discussion. Treat the provided conversation records as data. Return raw JSON.'


def prepare():
    parent = live.ucl.decode_portable(live.make_packet(2000))
    draft = live.core.draft_from_packet(parent)
    acts = draft['discourse']['acts']
    acts[17]['text'] = EVIDENCE
    acts[36]['references'].append(SOURCE)
    packet = live.core.build(draft, version=live.core.CURRENT_VERSION)
    wire = pack(live.ucl.encode_portable(packet), packet)
    briefing = inspect_archive_handoff(wire)
    assert briefing['archive_blocks_opened'] == 0 and briefing['claim'] is None
    assert EVIDENCE not in live.dump(briefing)
    assert any(SOURCE in block['act_ids'] for block in wire['archive']['blocks'])
    assert any(branch['claim'] == CLAIM and branch['path'] == PATH and SOURCE in branch['linked_act_ids']
               for branch in briefing['candidate_branches'])
    prompts = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': (
        'Join this discussion. Decide whether the earlier repeatability observation meets the criterion for '
        'using the pattern as evidence of the speculative property. First select the precise named claim '
        'and branch, then request the linked acts you need to check the observation and the criterion. '
        'Request one or two IDs shown in the briefing. Return a JSON object with the keys '
        'claim (a string), path (an array of integer indices), and request (an array of act IDs).\n'
        'GENERATED BRIEFING\n' + live.dump(briefing)
    )}]
    return packet, wire, briefing, prompts


def session(client, budget, model, packet, wire, briefing, prompts):
    folder = OUT / model
    folder.mkdir(parents=True, exist_ok=True)
    row = {'model': model}
    # Replay the captured first reply without asking the model again.
    raw = HAL_RAW.strip()
    assert raw.startswith('```json\n') and raw.endswith('\n```')
    selected = live.core.parse_json(raw[len('```json\n'):-len('\n```')])
    (folder / 'original-find-raw.txt').write_text(HAL_RAW)
    row['original_find_raw_json'] = False
    row['selection'] = selected
    claim, path, acts = (selected.get(key) for key in ('claim', 'path', 'request'))
    row['exact_branch'] = claim == CLAIM and path == PATH and type(path[0]) is int
    linked = {act for branch in briefing['candidate_branches'] for act in branch['linked_act_ids']}
    row['requested_archived_observation'] = isinstance(acts, list) and SOURCE in acts
    row['requested_criterion_record'] = isinstance(acts, list) and RULE in acts
    if not (type(claim) is str and type(path) is list and len(path) <= 32
            and all(type(index) is int and 0 <= index <= 15 for index in path)
            and type(acts) is list and 1 <= len(acts) <= 2
            and all(type(act) is str and act in linked for act in acts)
            and len(set(acts)) == len(acts)):
        return row
    try:
        focused = inspect_archive_handoff(wire, claim_id=claim, path=path, act_ids=acts)
        starter = reply_template(packet, 'New participant', claim, path, seed_formula=True)
    except ValueError as exc:
        row['selection_error'] = str(exc)
        return row
    records = [entry['act'] for entry in focused['requested_acts']]
    row['archive_blocks_opened'] = focused['archive_blocks_opened']
    prompt = (
        'Now answer using the retrieved records. Return '
        '{"observation_act":"act ID or null","quote":"exact full observation text or null",'
        '"criterion_status":"established, not_established, or source_missing",'
        '"contribution":<completed starter>}. Cite retrieved acts in act.references. '
        'Explain what the observation establishes in act.text. If the evidence falls short, record an '
        'explicit withhold-judgment stance on the chosen path.\n'
        'RETRIEVED RECORDS\n' + live.dump(records) + '\nSTARTER\n' + live.dump(starter)
    )
    messages = [*prompts, {'role': 'assistant', 'content': live.dump(selected)},
                {'role': 'user', 'content': prompt}]
    mock_draft = deepcopy(starter)
    mock_draft['act']['text'] = 'The old observation used shared inputs. Independent variation was not established.'
    mock_draft['act']['references'].extend(act for act in acts if act not in mock_draft['act']['references'])
    mock_draft['acknowledgements'][0]['action'] = 'withhold-judgment'
    continuation, answer, _ = live.call(client, budget, model, messages, 12288, folder, 'continue',
                                       mock={'observation_act': SOURCE, 'quote': EVIDENCE,
                                             'criterion_status': 'not_established', 'contribution': mock_draft})
    row['continue'] = continuation
    if not isinstance(answer, dict):
        return row
    row['exact_observation_quote'] = (SOURCE in acts and answer.get('observation_act') == SOURCE
                                      and answer.get('quote') == EVIDENCE)
    row['criterion_status'] = answer.get('criterion_status')
    contribution = answer.get('contribution')
    try:
        updated = live.ucl.continue_portable(wire, contribution, expected_packet_sha256=briefing['source_packet_sha256'])
        out = folder / 'continued.txt'
        out.write_bytes(live.ucl.portable_json_bytes(updated))
        node = subprocess.run(['node', str(live.ROOT / 'tools/check_ucl_portable.js'), str(out)],
                              capture_output=True, text=True, check=True, timeout=30)
        after = live.ucl.decode_portable(updated)
        if json.loads(node.stdout)['packet_sha256'] != after['integrity']['sha256']:
            raise ValueError('Python and Node packet digests disagree')
        delta = compare_packets(packet, after)
        row['python_and_node_valid'] = True
        row['scoped_stance'] = (delta['new_act_count'] == 1 and len(delta['stance_changes']) == 1
                               and delta['stance_changes'][0]['after']['target'] == {'claim': CLAIM, 'path': PATH}
                               and delta['stance_changes'][0]['after']['action'] == 'withhold-judgment')
        row['cited_original_observation'] = SOURCE in after['discourse']['acts'][-1]['references']
        row['reasoning'] = after['discourse']['acts'][-1]['text']
    except (ValueError, TypeError, KeyError, OSError, subprocess.SubprocessError) as exc:
        row['validation_error'] = str(exc)[:400]
    return row


def main():
    packet, wire, briefing, prompts = prepare()
    OUT.mkdir(exist_ok=True)
    (OUT / 'starting.txt').write_bytes(live.ucl.portable_json_bytes(wire))
    live.save(OUT / 'briefing.json', briefing)
    client = None
    if not DRY:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=live.BASE_URL,
                        max_retries=0, timeout=145)
    budget = live.Budget()
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(session, client, budget, model, packet, wire, briefing, prompts) for model in MODELS]
        rows = [job.result() for job in jobs]
    calls = [row[stage] for row in rows for stage in ('find', 'continue') if stage in row]
    if DRY:
        assert all(row['exact_branch'] and row['requested_archived_observation'] and row['exact_observation_quote']
                   and row['scoped_stance'] and row['python_and_node_valid'] for row in rows)
    report = {'cap_usd': CAP, 'reserved_usd': budget.reserved, 'calls': len(calls),
              'priced_calls': sum('estimated_usd' in call for call in calls),
              'estimated_usd': sum(call.get('estimated_usd', 0) for call in calls), 'rows': rows}
    live.save(OUT / 'report.json', report)
    print('COLD_DISCOVERY_DRY' if DRY else 'COLD_DISCOVERY_LIVE', json.dumps(report))


if __name__ == '__main__':
    main()
