"""Offline validation of live-generated dialogue; never contacts Radium."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
import live_dialogue as d
import ucl

class TestLiveDialogue(unittest.TestCase):
    def test_arm_scope_and_schedule(self):
        self.assertEqual(d.FORMATS,('english','structured_english','ucl_portable'))
        self.assertEqual(len(d.plan(1,6)),18)
        self.assertEqual(len(d.plan(2,4)),24)
        for bad in (0,3,True):
            with self.assertRaises(ValueError):d.plan(bad,4)
        with self.assertRaises(ValueError):d.plan(1,9)

    def test_parsing_and_invalid_intents(self):
        good={'receipt':None,'intent':{'action':'reject','path':0},'message':'I reject only the hypothetical first property.'}
        self.assertEqual(d.parse_agent(json.dumps(good),False)['intent']['path'],0)
        with self.assertRaises(ValueError):d.parse_agent(json.dumps(good),True)
        bad=dict(good);bad['intent']={'action':'reject','path':True}
        with self.assertRaises(ValueError):d.parse_agent(json.dumps(bad),False)

    def test_offline_simulated_conversations(self):
        r=d.run(dry_run=True,cap=.01,trials=2,turns=6)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['completed'],36)
        self.assertEqual(r['estimated_cost_usd'],0)
        for fmt,stats in r['by_format'].items():
            self.assertEqual(stats['calls'],12)
            self.assertEqual(stats['valid_agent_outputs'],12)
            self.assertEqual(stats['receipts_scored'],10)
            self.assertEqual(stats['receipts_correct'],10)
        self.assertEqual(r['by_format']['ucl_portable']['valid_ucl_packets'],12)
        self.assertTrue(all(x['receipt_correct'] is True for x in r['cases'] if x['turn']>0))
        self.assertEqual([x['model'] for x in r['cases'] if x['trial']==1 and x['format']=='ucl_portable'][:2],['hal-1.0','clarke-1.0'])

    def test_mock_provider_misinterpretation_is_scored(self):
        class Fake:
            def __init__(self):self.n=0
            def create(self,**kwargs):
                self.n+=1
                receipt=None if (self.n-1)%4==0 else {'action':'reject','path':1}
                obj={'receipt':receipt,'intent':{'action':'accept','path':0},
                     'message':'I accept only P for discussion, without evidence of truth.'}
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(obj)),finish_reason='stop')],
                          usage=SimpleNamespace(prompt_tokens=80,completion_tokens=90))
        obj=Fake()
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=obj.create)))
        r=d.run(client=client,cap=4,turns=4)
        self.assertEqual(r['completed'],12)
        self.assertEqual(r['status'],'complete')
        self.assertTrue(any(x.get('receipt_correct') is False for x in r['cases']))
        self.assertGreater(r['estimated_cost_usd'],0)

    def test_budget_stop_before_api_call(self):
        class Fail:
            def create(self,**kwargs):
                raise AssertionError('Must stop before calling the provider')
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=Fail().create)))
        result=d.run(client=client,cap=.000001,turns=4)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['completed'],0)

if __name__=='__main__':unittest.main()
