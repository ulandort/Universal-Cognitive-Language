"""Free exploratory dialogue tests, no provider calls."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_exploration as e
import native_author as n
import ucl

class TestNativeExploration(unittest.TestCase):
    def test_free_choice_three_protocols_and_two_directions(self):
        result=e.run(dry_run=True,cap=.01,turns=4,directions=2)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(result['total_estimated_cost_usd'],0)
        self.assertEqual(len(result['cases']),24)
        for fmt in n.FORMATS:
            stats=result['by_format'][fmt]
            self.assertEqual(stats['turns'],8)
            self.assertEqual(stats['valid_authored'],8)
            self.assertEqual(stats['receipts_correct'],6)
            self.assertEqual(stats['receipts_scored'],6)
        self.assertEqual(result['by_format']['ucl_native']['self_report_explicit_structure_matches'],8)
        self.assertIsNone([r for r in result['cases'] if r['format']=='english'][0]['self_report_matches_explicit_structure'])

    def test_no_seeded_oracle_and_no_auto_provider(self):
        base=ucl.load_json(n.BASELINE.read_text())
        state={'history':[],'packet':base,'last_intent':None,'last_act':None,'failed':0}
        p=e.make_prompt('ucl_native',0,'clarke-1.0',state)[-1]['content']
        self.assertIn('choose freely',p)
        self.assertIn('unexpected distinctions',p)
        self.assertNotIn('Your task: communicate ONLY your stance',p)
        self.assertIn('ACK target',p)

    def test_no_prior_ucl_receipt_is_explicitly_null(self):
        base=ucl.load_json(n.BASELINE.read_text())
        state={'history':[],'packet':base,'last_intent':None,'last_act':None,'failed':2}
        msg=e.make_prompt('ucl_native',2,'clarke-1.0',state)[-1]['content']
        self.assertIn('Set receipt to JSON null',msg)
        self.assertIn('historical UCL act',msg)

    def test_timeout_is_logged_and_next_turn_continues(self):
        from types import SimpleNamespace
        class Fake:
            def __init__(self):self.calls=0
            def create(self,**kwargs):
                self.calls+=1
                if self.calls==1:raise TimeoutError('mock timeout')
                return SimpleNamespace(
                  choices=[SimpleNamespace(
                    message=SimpleNamespace(content='{"receipt":null,"intent":{"action":"reject","path":0,"signal_sense":"conceptual-hint","evidence":"none"},"authored":"I reject only P. Signal is conceptual, not proven; no evidence is offered."}'),
                    finish_reason='stop')],
                  usage=SimpleNamespace(prompt_tokens=100,completion_tokens=100))
        fake=Fake()
        api=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake.create)))
        out=e.run(api,cap=10,turns=2,directions=1)
        self.assertEqual(out['status'],'complete')
        self.assertEqual(len(out['cases']),6)
        self.assertTrue(out['cases'][0]['provider_charge_unknown'])
        self.assertEqual(out['cases'][0]['failure_type'],'api_TimeoutError')
        self.assertTrue(out['cases'][1]['valid'])
        self.assertTrue(out['cases'][1]['resumed_after_failure'])
        self.assertIn('estimated_cost_caveat',out)

    def test_invalid_private_intent_rejected(self):
        obj={'receipt':None,'intent':{'action':'made-up','path':0,
             'signal_sense':'conceptual-hint','evidence':'none'},'authored':'A valid sentence.'}
        import json
        with self.assertRaises(ValueError):e.parse_response(json.dumps(obj),'english',False)

    def test_small_budget_never_calls_api(self):
        out=e.run(client=None,cap=.000001,turns=2,directions=1)
        self.assertEqual(out['status'],'budget_stop')
        self.assertEqual(out['cases'],[])

if __name__=='__main__':unittest.main()
