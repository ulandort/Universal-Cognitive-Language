"""UCL-only test: no English controls, native valid packet relay."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ucl_only_conversation as u

class TestUclOnlyConversation(unittest.TestCase):
    def test_eight_turn_one_direction(self):
        result=u.run(dry_run=True,turns=8,directions=1,cap=.01)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(result['formats_requested'],['ucl_native'])
        self.assertEqual(set(result['by_format']),{'ucl_native'})
        self.assertEqual(len(result['cases']),8)
        self.assertEqual(result['conversations'][0]['valid_packets'],8)
        self.assertEqual(result['conversations'][0]['max_consecutive_valid_packets'],8)
        self.assertEqual(result['conversations'][0]['receipts_correct'],7)
        self.assertEqual(result['total_estimated_cost_usd'],0)
        self.assertTrue(all(r['valid'] for r in result['cases']))
    def test_two_directions_and_budget_stop(self):
        result=u.run(dry_run=True,turns=4,directions=2,cap=.001)
        self.assertEqual(len(result['conversations']),2)
        self.assertEqual([x['starting_model'] for x in result['conversations']],
                         ['clarke-1.0','hal-1.0'])
        result=u.run(dry_run=False,client=None,cap=.000001,turns=4,directions=1)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['cases'],[])
if __name__=='__main__':unittest.main()
