import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from long_join import ACKNOWLEDGEMENT, CAVEAT, ROOT, core, make_packet, ucl


class LongJoinTests(unittest.TestCase):
    def test_lookup_and_continue_at_one_thousand_acts(self):
        envelope = make_packet()
        packet = ucl.decode_portable(envelope)
        self.assertEqual(len(packet['discourse']['acts']), 1000)
        with self.assertRaisesRegex(ValueError, 'discourse act cap'):
            core.build(core.draft_from_packet(packet), version=core.DEPENDENCY_VERSION)
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / 'conversation.txt'
            raw = ucl.portable_json_bytes(envelope)
            incoming.write_bytes(raw)
            command = [sys.executable, str(ROOT / 'src/ucl.py'), 'inspect', str(incoming)]
            result = subprocess.run(
                [*command, '--claim', 'theory', '--path', '1'], check=True, capture_output=True, timeout=20,
            )
            excerpt = json.loads(result.stdout)
            self.assertEqual(excerpt['claim_scope']['selected_expression'], '~[B][A]')
            self.assertGreater(excerpt['matching_acknowledgement_count'], 900)
            self.assertLessEqual(len(excerpt['acknowledgements']), 12)
            condition = next(ack for ack in excerpt['acknowledgements'] if ack['id'] == ACKNOWLEDGEMENT)
            self.assertEqual((condition['by'], condition['qualification']['expression']), ('t37', CAVEAT))
            self.assertEqual(excerpt['definitions']['$independent_inputs'],
                             packet['definitions']['$independent_inputs'])
            self.assertIn('D', excerpt['domains'])
            self.assertLess(len(result.stdout), len(raw) // 30)
            previous = subprocess.run(
                [*command, '--act', 't37'], check=True, capture_output=True, timeout=20,
            )
            self.assertEqual(json.loads(previous.stdout)['act'], packet['discourse']['acts'][36])
            other_scope = subprocess.run(
                [*command, '--claim', 'theory', '--path', '0'], check=True, capture_output=True, timeout=20,
            )
            other_acks = json.loads(other_scope.stdout)
            self.assertNotIn(ACKNOWLEDGEMENT, {ack['id'] for ack in other_acks['acknowledgements']})

            reply = {
                'act': {'id': 't1001', 'kind': 'response', 'speaker': 'New participant',
                        'references': ['t1000', 't37'], 'expressions': [CAVEAT],
                        'text': 'The independent-input control is the recorded condition.',
                        'details': {'responds_to': 't1000', 'stance': 'mixed'}},
                'orientation': 'L', 'explanation': CAVEAT, 'conclusion': CAVEAT,
                'history_summary': 'All 1,000 prior acts retained with one scoped response.',
            }
            outgoing = Path(directory) / 'joined.txt'
            subprocess.run(
                [sys.executable, str(ROOT / 'src/ucl.py'), 'continue', str(incoming), str(outgoing)],
                input=core.canon(reply), check=True, capture_output=True, timeout=20,
            )
            joined = ucl.decode_portable(ucl.read_json_file(outgoing, limit=ucl.MAX_PORTABLE_JSON))
            self.assertEqual(joined['discourse']['acts'][:-1], packet['discourse']['acts'])
            self.assertEqual(joined['definitions'], packet['definitions'])
            self.assertEqual(incoming.read_bytes(), raw)
            if shutil.which('node'):
                subprocess.run(
                    ['node', str(ROOT / 'tools/check_ucl_portable.js'), str(outgoing)],
                    check=True, capture_output=True, timeout=20,
                )


if __name__ == '__main__':
    unittest.main()
