"""Offline orchestration checks: native authoring + dialogue with single shared cap."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_suite as s

class TestNativeSuite(unittest.TestCase):
    def test_complete_free_double_direction_suite(self):
        out=s.suite(dry_run=True,cases=4,directions=2,strict=True,multi_turn=True,cap=10)
        self.assertEqual(out['status'],'dry_run')
        self.assertEqual(out['total_estimated_cost_usd'],0)
        self.assertEqual(out['spending_guard_usd'],10)
        self.assertEqual(out['per_stage']['one_hop_and_strict']['completed_tasks'],26)
        self.assertEqual(out['per_stage']['multi_turn_native_dialogue']['completed_turns'],24)
        self.assertTrue(all(x.get('end_to_end_success') is True
                            for x in out['per_stage']['one_hop_and_strict']['cases']))
    def test_one_stage_mode_and_guard(self):
        out=s.suite(dry_run=True,cases=2,directions=1,strict=False,multi_turn=False,cap=5)
        self.assertEqual(out['status'],'dry_run')
        self.assertIsNone(out['per_stage']['multi_turn_native_dialogue'])
        self.assertEqual(out['per_stage']['one_hop_and_strict']['completed_tasks'],6)
        with self.assertRaises(ValueError):s.suite(dry_run=True,cap=10.01)
if __name__=='__main__':unittest.main()
