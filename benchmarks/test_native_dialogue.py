"""Free offline tests for four-turn directly native UCL authored dialogues."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_dialogue as d
import native_author as n

class TestNativeDialogue(unittest.TestCase):
    def test_full_offline_24_turns(self):
        result=d.run(dry_run=True,directions=2,cap=.01)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(result['completed_turns'],24)
        self.assertEqual(result['estimated_cost_usd'],0)
        for fmt in n.FORMATS:
            x=result['by_format'][fmt]
            self.assertEqual(x['turns'],8)
            self.assertEqual(x['valid_generated_messages'],8)
            self.assertEqual(x['invalid_generated_messages'],0)
            self.assertEqual(x['receipt_correct'],6)
            self.assertEqual(x['receipt_scored'],6)
        ucl_cases=[r for r in result['cases'] if r['format']=='ucl_native']
        self.assertTrue(all(r['author_task_correct'] is True for r in ucl_cases))
        self.assertEqual([r['model'] for r in ucl_cases[:4]],['clarke-1.0','hal-1.0','clarke-1.0','hal-1.0'])
        self.assertEqual([r['model'] for r in ucl_cases[4:]],['hal-1.0','clarke-1.0','hal-1.0','clarke-1.0'])
        self.assertEqual(ucl_cases[3]['last_delivered_act'],'t11')

    def test_receipt_schema_and_sender_type(self):
        good={'action':'reject','path':0,'signal_sense':'conceptual-hint','evidence':'none'}
        self.assertEqual(d.parse_turn(json.dumps({'receipt':good,'authored':'A short English statement.'}),
                                      'english',True)[0],good)
        for obj,fmt,has in [
            ({'receipt':None,'authored':'An original statement.'},'english',True),
            ({'receipt':good,'authored':'An original statement.'},'english',False),
            ({'receipt':good,'authored':'not structured'},'ucl_native',True),
            ({'receipt':good,'authored':{}},'english',True)]:
            with self.assertRaises(ValueError):d.parse_turn(json.dumps(obj),fmt,has)

    def test_budget_stop_before_spending(self):
        result=d.run(client=None,dry_run=False,directions=1,cap=.000001)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['completed_turns'],0)

    def test_authoring_templates_match_actual_turn(self):
        base=n.ucl.load_json(n.BASELINE.read_text())
        state={'packet':base,'history':[],'prior_case':n.CASES[0],
               'last_act':'t9','failed':0}
        messages=d.messages('ucl_native',1,n.CASES[1],'hal-1.0',state)
        self.assertIn('t10',messages[-1]['content'])
        self.assertIn('x6',messages[-1]['content'])
        self.assertIn('Full prior valid UCL packet',messages[-1]['content'])

if __name__=='__main__':unittest.main()
