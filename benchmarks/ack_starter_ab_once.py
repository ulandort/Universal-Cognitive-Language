"""Replay two original Hal continuations and vary only the seeded ACK action."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import zipfile

import blind_archive_once as trial
from live_radium import reserve_upper_bound

CAP = 0.70
MODEL = 'hal-1.0'
LIMIT = 12288
OUT = Path('ack-starter-ab-dry-run' if sys.argv[1:] == ['--dry-run'] else 'ack-starter-ab-artifacts')
RETRIEVALS = {
    'insufficient': ' {"request":["t286"]}',
    'refined_meaning': ' {"request":["t185"]}',
}


def prepare(case, base):
    prepared = trial.fixture(base, case)
    _, wire, briefing, catalog, _, starter = prepared
    initial = trial.initial(case, briefing, catalog)
    raw = RETRIEVALS[case['name']]
    ids = json.loads(raw)['request']
    records, control = trial.followup(wire, ids, starter)
    changed = deepcopy(starter)
    assert changed['acknowledgements'][0]['action'] == 'received'
    changed['acknowledgements'][0]['action'] = 'withhold-judgment'
    _, seeded = trial.followup(wire, ids, changed)
    original_json = trial.dump(starter)
    revised_json = trial.dump(changed)
    assert revised_json == original_json.replace('"action":"received"', '"action":"withhold-judgment"', 1)
    assert seeded['content'] == control['content'].replace(original_json, revised_json)
    history = [*initial, {'role': 'assistant', 'content': raw}]
    return case, prepared, records, {'default': [*history, control], 'seeded': [*history, seeded]}


def run_case(client, budget, ready, order):
    case, prepared, records, messages = ready
    _, wire, _, _, symbols, starter = prepared
    rows = []
    for arm in order:
        folder = OUT / case['name'] / arm
        folder.mkdir(parents=True, exist_ok=True)
        trial.save(folder / 'prompt.json', messages[arm])
        (folder / 'starting.txt').write_bytes(trial.ucl.portable_json_bytes(wire))
        draft = deepcopy(starter)
        draft['act']['text'] = 'Dry-run validation of the recorded branch.'
        draft['act']['references'].append(case['wanted'])
        draft['acknowledgements'][0]['action'] = 'received' if arm == 'default' else 'withhold-judgment'
        mock = {'evidence': {'act_id': case['wanted'], 'quote': records[0]['text'],
                             'criterion_status': case['status'], **symbols}, 'contribution': draft}
        result, answer, _ = trial.call(client, budget, MODEL, messages[arm], LIMIT, folder, 'continue', mock=mock)
        result.update(case=case['name'], arm=arm)
        if answer is not None:
            trial.assessment(case, prepared, records, answer, folder, result)
            try:
                result['ack_action'] = answer['contribution']['acknowledgements'][0]['action']
            except (KeyError, IndexError, TypeError):
                pass
            result['requested_action_used'] = result.get('ack_action') == 'withhold-judgment'
        rows.append(result)
    return rows


def main():
    dry = sys.argv[1:] == ['--dry-run']
    base = trial.ucl.decode_portable(trial.make_packet(2000))
    cases = [prepare(case, base) for case in trial.CASES if case['name'] in RETRIEVALS]
    orders = [('default', 'seeded'), ('seeded', 'default')]
    estimated_max = sum(reserve_upper_bound(MODEL, prompt, LIMIT) for item in cases for prompt in item[3].values())
    if estimated_max > CAP:
        raise SystemExit('No calls made: conservative reserve exceeds the cap')
    budget = trial.Budget()
    if len(sys.argv) == 3 and sys.argv[1] == '--verify-original':
        with zipfile.ZipFile(sys.argv[2]) as archive:
            for case, _, _, messages in cases:
                recorded = json.loads(archive.read(f'{case["name"]}/hal-1.0/continue-prompt.json'))
                assert messages['default'] == recorded, case['name']
        print('Verified exact original continuation prompts for both cases.')
        return
    if dry:
        results = [row for case, order in zip(cases, orders, strict=True)
                   for row in run_case(None, budget, case, order)]
        assert all(r['python_and_node_valid'] and r['exact_decisive_source'] for r in results)
        assert all(r['requested_action_used'] == (r['arm'] == 'seeded') for r in results)
    else:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=trial.BASE_URL, max_retries=0, timeout=145)
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(run_case, client, budget, case, order) for case, order in zip(cases, orders, strict=True)]
            results = [row for job in jobs for row in job.result()]
    report = {
        'model': MODEL, 'cap_usd': CAP, 'reserved_usd': budget.reserved,
        'priced_calls': sum('estimated_usd' in row for row in results),
        'estimated_usd': sum(row.get('estimated_usd', 0) for row in results), 'rows': results,
    }
    trial.save(OUT / 'report.json', report)
    print('ACK_AB_DRY_RUN' if dry else 'ACK_AB_LIVE_RESULT', json.dumps(report))


if __name__ == '__main__':
    main()
