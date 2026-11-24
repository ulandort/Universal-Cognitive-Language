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

    def test_handoff_opens_each_requested_block_only_once(self):
        with patch.object(history_archive, '_open_block', wraps=history_archive._open_block) as opened:
            brief = history_archive.inspect_archive_handoff(self.packed, claim_id='theory', path=[1])
            self.assertEqual(opened.call_count, 0)
            self.assertEqual(brief['archive_blocks_opened'], 0)
            brief = history_archive.inspect_archive_handoff(
                self.packed, claim_id='theory', path=[1], act_ids=['t1850', 't1851', 't1850'],
            )
            self.assertEqual(opened.call_count, 1)
        self.assertFalse(brief['whole_packet_audited'])
        self.assertEqual(brief['archive_blocks_opened'], 1)
        self.assertEqual(brief['current_state']['retained_act_count'], 4096)
        issues = self.packed['packet']['history']['unresolved']
        self.assertEqual(brief['open_issue'], {
            'text': issues[-1], 'source': f'/packet/history/unresolved/{len(issues) - 1}',
        })
        self.assertEqual(brief['claim']['scope']['path'], [1])
        self.assertTrue(any(ack['author_act'] == 't37' and ack['ack_id'] == 'condition37'
                            for ack in brief['claim']['acknowledgements']))
        self.assertEqual([entry['act'] for entry in brief['requested_acts']],
                         self.packet['discourse']['acts'][1849:1851])

    def test_current_state_preserves_stances_without_opening_archive_blocks(self):
        from inspection import compare_packets, current_state

        with patch.object(history_archive, '_open_block',
                          side_effect=AssertionError('state does not need archived contents')):
            state = history_archive.inspect_archive(self.packed, state=True)
        self.assertFalse(state['whole_packet_audited'])
        self.assertEqual(state['retained_act_count'], 4096)
        self.assertLess(state['readable_act_count'], state['retained_act_count'])
        self.assertEqual(state['latest_stances'], current_state(self.packet)['latest_stances'])
        self.assertEqual(state['pinned_act_count'], 1)
        delta = compare_packets(self.packet, ucl.decode_portable(self.packed))
        self.assertEqual(delta['new_act_count'], 0)
        self.assertEqual(delta['stance_changes'], [])

    def test_size_pressure_can_pack_a_partial_batch_without_hiding_the_tail(self):
        source = make_packet(1010)
        packet = ucl.decode_portable(source)
        self.assertIs(history_archive.pack(source, packet), source)
        with patch.object(history_archive, 'PRESSURE_BYTES', 1):
            packed = history_archive.pack(source, packet)
        self.assertEqual(len(packed['archive']['blocks']), 1)
        self.assertEqual(packed['packet']['discourse']['acts'][-1000:], packet['discourse']['acts'][-1000:])
        self.assertEqual(ucl.decode_portable(packed), packet)

    def test_packing_keeps_the_retraction_and_the_original_ack_readable(self):
        draft = core.draft_from_packet(self.packet)
        draft['discourse']['acts'][399]['speaker'] = 'Reviewer'
        draft['acknowledgements'].append({
            'id': 'retract400', 'by': 't400', 'target': {'ack': 'condition37'},
            'action': 'retract', 'qualification': None, 'replacement': None, 'note': '',
        })
        packet = core.build(draft, version=core.RETRACTION_VERSION)
        packed = history_archive.pack(ucl.encode_portable(packet), packet)
        self.assertIn('archive', packed)
        with patch.object(history_archive, '_open_block', side_effect=AssertionError('avoid gzip lookup')):
            state = history_archive.inspect_archive(packed, state=True)
            excerpt = history_archive.inspect_archive(packed, claim_id='theory', path=[1])
        self.assertEqual(state['recent_retractions'][-1]['retracts'], 'condition37')
        self.assertTrue(state['recent_retractions'][-1]['cleared_current_stance'])
        self.assertTrue({'retract400', 'condition37'} <= {ack['id'] for ack in excerpt['acknowledgements']})
        briefing = history_archive.inspect_archive_handoff(packed, claim_id='theory', path=[1])
        retraction, = briefing['current_state']['recent_retractions']
        self.assertEqual((retraction['ack_id'], retraction['author_act'], retraction['retracts']),
                         ('retract400', 't400', 'condition37'))
        self.assertEqual(ucl.decode_portable(packed), packet)
        with tempfile.TemporaryDirectory() as directory:
            before = Path(directory) / 'packed-23.txt'
            after = Path(directory) / 'packed-24.txt'
            before.write_bytes(ucl.portable_json_bytes(packed))
            subprocess.run([sys.executable, str(ROOT / 'src/ucl.py'), 'upgrade', str(before), str(after)],
                           check=True, capture_output=True, timeout=40)
            upgraded = ucl.read_json_file(after, limit=ucl.MAX_PORTABLE_JSON)
            self.assertEqual(upgraded['format'], ucl.PORTABLE_FORMAT)
            self.assertEqual(upgraded['archive'], packed['archive'])
            expanded = ucl.decode_portable(upgraded)
            self.assertEqual(expanded, core.upgrade_packet(packet))

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
