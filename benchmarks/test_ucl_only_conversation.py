"""Offline tests: native UCL-only conversation, SAP-1 and model-owned repair."""
import json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ucl_only_conversation as u
import structural_authoring as sap
import native_author as n
import ucl

class TestUclOnlyConversation(unittest.TestCase):
    def test_eight_turn_one_direction(self):
        r=u.run(dry_run=True,turns=8,directions=1,cap=.01,max_repairs=2)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['formats_requested'],['ucl_native'])
        self.assertEqual(r['structural_profile'],sap.PROFILE)
        self.assertEqual(len(r['cases']),8)
        self.assertEqual(r['conversations'][0]['valid_packets'],8)
        self.assertEqual(r['conversations'][0]['max_consecutive_valid_packets'],8)
        self.assertEqual(r['conversations'][0]['receipts_correct'],7)
        self.assertEqual(r['total_estimated_cost_usd'],0)
        self.assertEqual(r['api_calls_attempted'],8)
        self.assertTrue(all(a['valid'] for x in r['cases'] for a in x['attempts']))
    def test_two_directions_and_budget_stop(self):
        r=u.run(dry_run=True,turns=4,directions=2,cap=.01)
        self.assertEqual(len(r['conversations']),2)
        self.assertEqual([x['starting_model'] for x in r['conversations']],
                         ['clarke-1.0','hal-1.0'])
        r=u.run(client=None,cap=.000001,turns=4,directions=1)
        self.assertEqual(r['status'],'budget_stop')
        self.assertEqual(r['api_calls_attempted'],0)
    def test_sap_rejects_unbound_ack_without_fixing_it(self):
        parent=u.ucl.load_json(n.BASELINE.read_text())
        state={'packet':parent,'last_intent':None}
        raw=u.synthetic_response(0,'clarke-1.0',
                         {'last_intent':None,'last_act':None})
        obj=json.loads(raw)
        obj['authored']['acknowledgements'][0]['id']='invented'
        with self.assertRaisesRegex(sap.StructuralProfileError,'ACK id'):
            u.validate_candidate(json.dumps(obj),'clarke-1.0',state,0)
        obj['authored']['acknowledgements'][0]['id']='x5'
        obj['authored']['explanation']='?[~[P][A]]'
        with self.assertRaises((ValueError,TypeError)):
            u.validate_candidate(json.dumps(obj),'clarke-1.0',state,0)
    def test_one_model_corrects_with_explicit_validation_feedback(self):
        base=u.ucl.load_json(n.BASELINE.read_text())
        mockstate={'last_intent':None,'last_act':None}
        good=json.loads(u.synthetic_response(0,'clarke-1.0',mockstate))
        bad=json.loads(json.dumps(good))
        bad['authored']['acknowledgements'][0]['id']='wrong'
        calls=[]
        class Fake:
            def create(self,**kwargs):
                calls.append(kwargs)
                text=json.dumps(bad if len(calls)==1 else good)
                return SimpleNamespace(choices=[SimpleNamespace(
                    message=SimpleNamespace(content=text),finish_reason='stop')],
                    usage=SimpleNamespace(prompt_tokens=150,completion_tokens=250))
        fake=SimpleNamespace(chat=SimpleNamespace(completions=Fake()))
        r=u.run(client=fake,cap=10,turns=2,directions=1,max_repairs=1)
        self.assertEqual(r['status'],'complete')
        self.assertEqual(r['conversations'][0]['valid_packets'],1)
        self.assertTrue(r['cases'][0]['repaired_and_delivered'])
        self.assertEqual(r['cases'][0]['attempts'][0]['failure_type'],'structural_profile_rejection')
        self.assertTrue(r['cases'][0]['attempts'][1]['valid'])
        self.assertIn('Exact error:',calls[1]['messages'][-1]['content'])
        self.assertEqual(r['api_calls_attempted'],3)
    def test_stable_profile_permits_novel_formulas_but_not_unknown_glyphs(self):
        base=u.ucl.load_json(n.BASELINE.read_text())
        state={'packet':base,'last_intent':None}
        obj=json.loads(u.synthetic_response(0,'clarke-1.0',
                                          {'last_intent':None,'last_act':None}))
        obj['authored']['act']['expressions']=['![~[P][A]]']
        obj['authored']['explanation']=obj['authored']['conclusion']='![~[P][A]]'
        _,_,packet,_=u.validate_candidate(json.dumps(obj),'clarke-1.0',state,0)
        self.assertEqual(packet['discourse']['acts'][-1]['expressions'],['![~[P][A]]'])
        obj['authored']['explanation']='NEW_OPERATOR[~[P][A]]'
        with self.assertRaises((ValueError,TypeError)):
            u.validate_candidate(json.dumps(obj),'clarke-1.0',state,0)

if __name__=='__main__':unittest.main()
