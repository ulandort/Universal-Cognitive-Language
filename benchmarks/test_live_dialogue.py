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
        self.assertEqual(len(d.plan(1,8)),24)
        self.assertEqual(d.MAX_OUTPUT,4096)
        for bad in (0,3,True):
            with self.assertRaises(ValueError):d.plan(bad,4)
        with self.assertRaises(ValueError):d.plan(1,9)

    def test_parsing_and_invalid_intents(self):
        good={'receipt':None,'intent':{'action':'reject','path':0,'signal_sense':'conceptual-hint','evidence':'none'},'message':'I reject only the hypothetical first property. Signal means a conceptual hint; no example is offered.'}
        self.assertEqual(d.parse_agent(json.dumps(good),False)['intent']['path'],0)
        with self.assertRaises(ValueError):d.parse_agent(json.dumps(good),True)
        bad=dict(good);bad['intent']={'action':'reject','path':True,'signal_sense':'conceptual-hint','evidence':'none'}
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
            for facet in ('action','path','signal_sense','evidence'):
                self.assertEqual(stats['component_accuracy'][facet]['correct'],10)
        self.assertEqual(r['by_format']['ucl_portable']['valid_ucl_packets'],12)
        self.assertTrue(all(x['receipt_correct'] is True for x in r['cases'] if x['turn']>0))
        self.assertEqual([x['model'] for x in r['cases'] if x['trial']==1 and x['format']=='ucl_portable'][:2],['hal-1.0','clarke-1.0'])

    def test_mock_provider_misinterpretation_is_scored(self):
        class Fake:
            def __init__(self):self.n=0
            def create(self,**kwargs):
                self.n+=1
                receipt=None if (self.n-1)%4==0 else {'action':'reject','path':1,'signal_sense':'instrument-reading','evidence':'hypothetical-example'}
                obj={'receipt':receipt,'intent':{'action':'accept','path':0,'signal_sense':'conceptual-hint','evidence':'none'},
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

    def test_ambiguity_and_epistemic_challenges_are_embedded(self):
        self.assertIn('CONCEPTUAL',d.SCENARIO)
        self.assertIn('MEASURABLE',d.SCENARIO)
        self.assertIn('hypothetical example',d.SCENARIO.lower())
        self.assertIn('PROVEN',d.STIMULI[2])
        self.assertIn('replaced',d.STIMULI[4])
        self.assertEqual(set(d.SENSES),{'conceptual-hint','instrument-reading'})
        self.assertEqual(set(d.EVIDENCE),{'none','hypothetical-example'})
        self.assertIn('claimed-empirical-proof',d.RECEIPT_EVIDENCE)
        self.assertIn('ambiguous',d.RECEIPT_SENSES)
        role=d.MODELS[1]
        msg=d.agent_messages('english',0,None,[],None,role)[-1]['content']
        self.assertIn('You are '+role,msg)

    def test_semantic_facets_must_be_complete_and_independent(self):
        intent={'action':'adopt-for-discussion','path':1,'signal_sense':'conceptual-hint','evidence':'hypothetical-example'}
        parsed={'receipt':intent,'intent':intent,'message':'I provisionally discuss B. Signal is a conceptual hint; imagine an illustrative case, not observation.'}
        self.assertEqual(d.parse_agent(json.dumps(parsed),True)['receipt'],intent)
        bad=dict(parsed);bad['intent']={**intent,'evidence':'established'}
        with self.assertRaises(ValueError):d.parse_agent(json.dumps(bad),True)
        bad=dict(parsed);bad['receipt']={**intent,'signal_sense':'confused'}
        with self.assertRaises(ValueError):d.parse_agent(json.dumps(bad),True)
        false_claim={**intent,'evidence':'claimed-empirical-proof'}
        bad=dict(parsed);bad['receipt']=false_claim
        self.assertEqual(d.parse_agent(json.dumps(bad),True)['receipt']['evidence'],'claimed-empirical-proof')
        flagged=dict(parsed);flagged['receipt']={**intent,'signal_sense':'ambiguous'}
        self.assertEqual(d.parse_agent(json.dumps(flagged),True)['receipt']['signal_sense'],'ambiguous')

    def test_facets_score_separately_when_main_target_correct(self):
        rows=[{'format':'ucl_portable','agent_valid':True,'receipt_correct':False,
               'receipt_components_correct':{'action':True,'path':True,'signal_sense':False,'evidence':True},
               'usage':{'input':200,'output':100}}]
        scores=d.summarize(rows,.005,'complete')['by_format']['ucl_portable']
        self.assertEqual(scores['receipts_correct'],0)
        self.assertEqual(scores['component_accuracy']['action']['correct'],1)
        self.assertEqual(scores['component_accuracy']['signal_sense']['correct'],0)

    def test_budget_stop_before_api_call(self):
        class Fail:
            def create(self,**kwargs):
                raise AssertionError('Must stop before calling the provider')
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=Fail().create)))
        result=d.run(client=client,cap=.000001,turns=4)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['completed'],0)

if __name__=='__main__':unittest.main()
