"""Deterministic long-discussion fixture. Generating it uses no model or network."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import core
import ucl
from inspection import focused_context

CAVEAT = '~[$independent_inputs][A]'
ACKNOWLEDGEMENT = 'condition37'
AUDIT_PHRASE = 'independent-input control'


def make_packet(turns=1000, *, archived=False):
    if not 1000 <= turns or (not archived and turns > core.MAX_LONG_ACTS):
        raise ValueError('the long-join fixture needs at least 1,000 acts; use --pack above 4,096')
    seed = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/challenge.txt'))
    draft = core.draft_from_packet(seed)
    draft['definitions']['$independent_inputs'] = {
        'definition': {'kind': 'predicate', 'args': ['D'],
                       'gloss': 'The pattern persists under independent variation of the inputs.'},
    }
    for n in range(9, turns + 1):
        act_id = f't{n}'
        acts = draft['discourse']['acts']
        if n == turns:
            acts.append({
                'id': act_id, 'speaker': 'Coordinator', 'kind': 'question',
                'references': ['t760', 't1'],
                'text': 'Can a repeatable pattern count as evidence for speculative convergence under the recorded eligibility condition? Find the exact original qualification before replying.',
                'expressions': ['~[B][A]'],
                'details': {'targets': ['What condition did the earlier participant attach to using B as evidence?'],
                            'answer_kind': 'open', 'alternatives': []},
            })
            continue

        references = {37: ['t1'], 400: ['t37'], 760: ['t400']}.get(n, ['t1'])
        text = {
            37: 'Only count the pattern B as evidence after an independent-input control. Shared inputs must vary independently and the pattern must persist.',
            400: 'Reconsider how repeatability is measured. The earlier eligibility caveat still applies.',
            760: 'Distinguish stability across runs from whether the pattern tells us anything about the speculative property.',
        }.get(n, f'Hypothetical observation {n}. This tests a descriptive pattern and leaves the original hypothesis open.')
        acts.append({
            'id': act_id, 'speaker': 'Reviewer' if n == 37 else 'Participant',
            'kind': 'response', 'references': references, 'text': text,
            'expressions': [CAVEAT if n == 37 else '~[B][A]'],
            'details': {'responds_to': references[0], 'stance': 'mixed'},
        })
        draft['acknowledgements'].append({
            'id': ACKNOWLEDGEMENT if n == 37 else f'ack{n}',
            'by': act_id, 'action': 'qualify' if n == 37 else 'received',
            'target': {'claim': 'theory', 'path': [1]},
            'qualification': {'expression': CAVEAT, 'explanation': text} if n == 37 else None,
            'replacement': None, 'note': '',
        })

    draft['discourse']['current'] = f't{turns}'
    draft.update(orientation='Q', explanation='~[B][A]', conclusion='~[B][A]')
    draft['history']['summary'] = f'Synthetic {turns}-act conversation with a recorded eligibility caveat and later revisions.'
    if archived:
        import portable
        from history_archive import pack

        packet = core.build(draft, version=core.LONG_VERSION, archived=True)
        return pack(portable.encode(packet, archived=True), packet)
    return ucl.encode_portable(core.build(draft, version=core.LONG_VERSION))


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--out', type=Path, required=True)
    args.add_argument('--turns', type=int, default=1000)
    args.add_argument('--pack', action='store_true', help='generate and archive an offline stress fixture')
    options = args.parse_args()
    envelope = make_packet(options.turns, archived=options.pack)
    raw = ucl.portable_json_bytes(envelope)
    options.out.write_bytes(raw)
    packet = ucl.decode_portable(envelope)
    excerpt = focused_context(packet, claim_id='theory', path=[1])
    assert any(ack['id'] == ACKNOWLEDGEMENT for ack in excerpt['acknowledgements'])
    print(json.dumps({
        'acts': options.turns, 'packet_bytes': len(raw), 'claim_excerpt_bytes': len(core.canon(excerpt)),
        'archive_blocks': len(envelope.get('archive', {}).get('blocks', [])),
        'packet_sha256': packet['integrity']['sha256'],
    }))


if __name__ == '__main__':
    main()
