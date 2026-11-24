import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from long_join import CAVEAT, ROOT, core, make_packet, ucl
import history_archive
import portable


class HistoryArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = make_packet(4096)
        cls.packet = ucl.decode_portable(cls.source)
        cls.packed = history_archive.pack(cls.source, cls.packet, pinned=['t500'])

    def test_pack_round_trips_the_expanded_packet_and_protects_sources(self):
        packed = self.packed
        readable = {act['id'] for act in packed['packet']['discourse']['acts']}
        self.assertTrue({'t1', 't37', 't500', 't760', 't3097', 't4096'} <= readable)
        self.assertNotIn('t1850', readable)
        self.assertEqual(len(packed['archive']['blocks']), 3)
        self.assertEqual(core.canon(ucl.decode_portable(packed)), core.canon(self.packet))
        rendered = ucl.portable_json_bytes(packed)
        self.assertLess(rendered.index(b'"archive_guide"'), rendered.index(b'"archive"'))
        self.assertLess(rendered.index(b'"packet"'), rendered.index(b'"archive"'))
        self.assertLess(len(rendered), len(core.canon(self.source)))

        with patch.object(history_archive, '_open_block', wraps=history_archive._open_block) as opened:
            selected = history_archive.inspect_archive(packed, act_id='t1850')
            self.assertEqual(selected['act'], self.packet['discourse']['acts'][1849])
            self.assertFalse(selected['whole_packet_audited'])
            self.assertEqual(opened.call_count, 1)
            claim = history_archive.inspect_archive(packed, claim_id='theory', path=[1])
            self.assertTrue(any(ack['by'] == 't37' for ack in claim['acknowledgements']))
            self.assertEqual(opened.call_count, 1)

    def test_rejects_corrupt_and_oversized_blocks(self):
        for field, value, diagnostic in (
            ('sha256', 'A' * 43, 'archive block SHA-256 mismatch'),
            ('expanded_bytes', 1, 'archive block expanded byte count'),
            ('expanded_bytes', history_archive.MAX_BLOCK_BYTES + 1, 'archive block expanded size'),
        ):
            with self.subTest(field=field, value=value):
                altered = copy.deepcopy(self.packed)
                altered['archive']['blocks'][0][field] = value
                altered['checksum'] = portable.envelope_checksum(altered)
                with self.assertRaisesRegex(ValueError, diagnostic):
                    ucl.decode_portable(altered)

    def test_size_pressure_can_pack_a_partial_batch_without_hiding_the_tail(self):
        source = make_packet(1010)
        packet = ucl.decode_portable(source)
        self.assertIs(history_archive.pack(source, packet), source)
        with patch.object(history_archive, 'PRESSURE_BYTES', 1):
            packed = history_archive.pack(source, packet)
        self.assertEqual(len(packed['archive']['blocks']), 1)
        self.assertEqual(packed['packet']['discourse']['acts'][-1000:], packet['discourse']['acts'][-1000:])
        self.assertEqual(ucl.decode_portable(packed), packet)

    def test_cli_continues_past_the_unpacked_act_ceiling(self):
        reply = {
            'act': {'id': 't4097', 'kind': 'response', 'speaker': 'New participant',
                    'references': ['t4096', 't37'], 'expressions': [CAVEAT],
                    'text': 'The original qualification remains relevant.',
                    'details': {'responds_to': 't4096', 'stance': 'mixed'}},
            'orientation': 'L', 'explanation': CAVEAT, 'conclusion': CAVEAT,
        }
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / 'archive.txt'
            outgoing = Path(directory) / 'continued.txt'
            incoming.write_bytes(ucl.portable_json_bytes(self.packed))
            cli = [sys.executable, str(ROOT / 'src/ucl.py')]
            subprocess.run([*cli, 'continue', str(incoming), str(outgoing)], input=core.canon(reply),
                           check=True, capture_output=True, timeout=40)
            result = json.loads(outgoing.read_bytes())
            joined = ucl.decode_portable(result)
            self.assertEqual(len(joined['discourse']['acts']), 4097)
            self.assertEqual(joined['discourse']['acts'][:-1], self.packet['discourse']['acts'])
            self.assertEqual(joined['definitions'], self.packet['definitions'])
            self.assertIn('t500', result['archive']['pinned'])
            if shutil.which('node'):
                subprocess.run(['node', str(ROOT / 'tools/check_ucl_portable.js'), str(outgoing)],
                               check=True, capture_output=True, timeout=30)


if __name__ == '__main__':
    unittest.main()
