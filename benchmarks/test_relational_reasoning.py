"""RR-1 deterministic regression tests (use RR1_SEED for genuine CG-1 artifact)."""
import copy,json,os,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import relational_reasoning as rr
import sap_portable

@unittest.skipUnless(os.environ.get('RR1_SEED'),'Set RR1_SEED to the genuine CG-1 final handoff JSON')
class RR1Tests(unittest.TestCase):
    def setUp(self):
        self.path=os.environ['RR1_SEED']
        self.base=rr.load_seed(self.path)
        self.state={'packet':self.base,'wire':json.dumps(sap_portable.encode(self.base)),
                    'last_act':None}
    def test_six_turns_uses_real_invented_definitions(self):
        x=rr.run(self.path,dry_run=True,turns=6,cap=.01)
        self.assertEqual(x['status'],'dry_run')
        self.assertEqual(x['delivered'],6)
        self.assertEqual(x['compound_relations_delivered'],6)
        self.assertEqual(x['paraphrases_for_human_review'],5)
    def test_rejects_single_concept_atom(self):
        obj=json.loads(rr.synthetic(self.state,0,'clarke-1.0'))
        obj['authored']['act']['expressions']=['~[C][A]']
        obj['authored']['explanation']=obj['authored']['conclusion']='~[C][A]'
        with self.assertRaisesRegex(ValueError,'compound'):
            rr.validate(json.dumps(obj),self.state,0,'clarke-1.0')
    def test_does_not_allow_changed_definition(self):
        obj=json.loads(rr.synthetic(self.state,0,'clarke-1.0'))
        obj['authored']['new_definitions']={'Y':{'kind':'predicate','args':['D'],
             'gloss':'Unauthorized extra definition'}}
        with self.assertRaises((ValueError,TypeError)):
            rr.validate(json.dumps(obj),self.state,0,'clarke-1.0')
    def test_full_packet_preserves_genuine_definitions(self):
        obj,p,w,c=rr.validate(rr.synthetic(self.state,0,'clarke-1.0'),self.state,0,'clarke-1.0')
        self.assertEqual(p['definitions'],self.base['definitions'])
        self.assertEqual(sap_portable.decode(json.loads(w)),p)
        self.assertEqual(len(p['discourse']['acts']),15)
    def test_budget_guard_prevents_paid_calls(self):
        r=rr.run(self.path,client=None,dry_run=False,turns=4,cap=.000001)
        self.assertEqual(r['status'],'budget_stop')
        self.assertEqual(r['api_calls'],0)

if __name__=='__main__':unittest.main()
