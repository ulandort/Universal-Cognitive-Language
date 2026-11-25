"""Replay the original six-turn autonomous dialogue, Portable arm only."""
import json
import os
from pathlib import Path
import subprocess
import sys

import live_dialogue as original

from authoring import draft_scoped_reply
from inspection import compare_packets

CAP = 0.60
DRY = sys.argv[1:] == ['--dry-run']
OUT = Path('six-turn-dry' if DRY else 'six-turn-live')
ucl = original.ucl
original.FORMATS = ('ucl_portable',)
exposures = []
packet_count = 0


def current_handoff(fmt, intent, note, packet, turn, speaker):
    """Use the current Portable envelope and current stance authoring from explicit intent."""
    global packet_count
    if ucl.packet_version(packet) != ucl.CURRENT_VERSION:
        packet = ucl.upgrade_packet(packet)
    source = ucl.encode_portable(packet)
    digest = packet['integrity']['sha256']
    scope = {'claim': 'theory', 'path': [intent['path']]}
    decision = {**scope, 'action': intent['action'], 'text': note, 'references': ['t1']}
    draft = draft_scoped_reply(packet, speaker, decision, expected_ack_action=intent['action'])
    next_wire = ucl.continue_portable(source, draft, expected_packet_sha256=digest)
    rendered = ucl.portable_json_bytes(next_wire)
    target = OUT / f'turn-{turn + 1}.txt'
    target.write_bytes(rendered)
    node = subprocess.run(['node', str(original.ROOT / 'tools/check_ucl_portable.js'), str(target)],
                          capture_output=True, text=True, timeout=30)
    if node.returncode:
        target.unlink()
        raise ValueError(node.stderr.strip())
    next_packet = ucl.decode_portable(next_wire)
    delta = compare_packets(packet, next_packet)
    ack = next_packet['acknowledgements'][-1]
    if (json.loads(node.stdout)['packet_sha256'] != next_packet['integrity']['sha256']
            or delta['new_act_count'] != 1 or delta['new_acknowledgement_count'] != 1
            or ack['target'] != scope or ack['action'] != intent['action']):
        target.unlink()
        raise ValueError('portable continuation changed the wrong scope or earlier retained record')
    packet_count += 1
    return rendered.decode(), next_packet


def reserve_dialogue_calls(client, model, messages, cap, spent, dry_run=False):
    reserve = original.reserve_upper_bound(model, messages, original.MAX_OUTPUT)
    exposure = spent + reserve
    if exposure > cap:
        return None, spent, 'budget_stop'
    exposures.append(exposure)
    result, updated, error = charge_model(client, model, messages, cap, spent, dry_run)
    # Hold the full reservation when the provider returns an unpriced error.
    return result, exposure if error == 'api_error' else updated, error


charge_model = original.call_and_charge
original.call_and_charge = reserve_dialogue_calls
original.encoded_handoff = current_handoff


def main():
    OUT.mkdir(exist_ok=True)
    client = None
    if not DRY:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=original.BASE_URL,
                        max_retries=0, timeout=145)
    report = original.run(client=client, cap=CAP, dry_run=DRY, trials=1, turns=6)
    report['cap_usd'] = CAP
    report['max_estimated_exposure_usd'] = max(exposures, default=0)
    report['node_and_python_packets'] = packet_count
    if DRY:
        conservative = 0.0
        for row in report['cases']:
            messages = [{'content': original.SYSTEM}, {'content': row['prompt']}]
            conservative += original.reserve_upper_bound(row['model'], messages, original.MAX_OUTPUT)
        report['six_call_dry_reserve'] = conservative
        assert conservative < CAP, conservative
        assert report['completed'] == 6 and packet_count == 6
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    summary = {key: report[key] for key in (
        'status', 'completed', 'estimated_cost_usd', 'cap_usd', 'max_estimated_exposure_usd', 'node_and_python_packets', 'by_format')}
    if DRY:
        summary['six_call_dry_reserve'] = report['six_call_dry_reserve']
    summary['turns'] = [{key: row.get(key) for key in (
        'turn', 'model', 'agent_valid', 'packet_valid', 'receipt_correct', 'semantic_mismatch', 'failure_type',
        'recovered', 'recovery_skipped', 'validation_error')} for row in report['cases']]
    print('SIX_TURN_DRY' if DRY else 'SIX_TURN_LIVE', json.dumps(summary))


if __name__ == '__main__':
    main()
