"""Offline real-seed tests of full 50-turn history and advisory interpretation metadata."""
import json,os,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import autonomous_50 as a
import sap_portable

@unittest.skipUnless(os.environ.get('L50_SEED'),'The genuine L25 seed is required')
class L50Tests(unittest.TestCase):
    def setUp(self):
        self.seed=os.environ['L50_SEED']
        self.packet=a.load_seed(self.seed)
        self.state={'packet':self.packet,
                    'wire':json.dumps(sap_portable.encode(self.packet)),
                    'delivered_count':0}
    def test_genuine_50_turn_synthetic_full_history(self):
        result=a.run(self.seed,dry_run=True,turns=50,cap=.01)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(result['delivered'],50)
        self.assertEqual(result['first_attempt_valid'],50)
        self.assertEqual(result['total_api_attempts'],50)
        self.assertEqual(result['checkpoint_references_validated'],5)
        self.assertGreater(result['last_wire_bytes'],result['first_wire_bytes'])
        last=sap_portable.decode(json.loads(result['cases'][-1]['handoff']))
        self.assertEqual(len(last['discourse']['acts']),93)
        self.assertEqual(len(last['acknowledgements']),89)
        self.assertEqual(last['history']['status'],'fully-expanded')
        self.assertEqual(last['definitions'],self.packet['definitions'])
        self.assertEqual(last['discourse']['acts'][:43],self.packet['discourse']['acts'])
        self.assertEqual(result['cases'][0]['speaker'],'hal-1.0')
    def test_short_or_null_or_missing_interpretation_is_advisory(self):
        raw=json.loads(a.synthetic(self.state,0,'hal-1.0'))
        for v in ('OK',None,''):
            raw['interpretation']=v
            obj,packet,wire=a.validate(json.dumps(raw),self.state,0,'hal-1.0')
            self.assertEqual(packet['discourse']['current'],'t44')
        del raw['interpretation']
        obj,packet,wire=a.validate(json.dumps(raw),self.state,0,'hal-1.0')
        self.assertEqual(packet['discourse']['current'],'t44')
    def test_invalid_ack_path_and_invalid_ucl_formula_remain_rejected(self):
        raw=json.loads(a.synthetic(self.state,0,'hal-1.0'))
        raw['authored']['acknowledgements'][0]['target']['path']=['0']
        with self.assertRaisesRegex(ValueError,'INTEGER'):
            a.validate(json.dumps(raw),self.state,0,'hal-1.0')
        raw=json.loads(a.synthetic(self.state,0,'hal-1.0'))
        raw['authored']['explanation']='BAD[~[C][A]]'
        with self.assertRaises((ValueError,TypeError)):
            a.validate(json.dumps(raw),self.state,0,'hal-1.0')
    def test_no_overwriting_preexisting_definitions(self):
        raw=json.loads(a.synthetic(self.state,0,'hal-1.0'))
        raw['authored']['new_definitions']={}
        with self.assertRaises((ValueError,TypeError)):
            a.validate(json.dumps(raw),self.state,0,'hal-1.0')
    def test_no_paid_call_when_cost_reservation_exceeds_cap(self):
        result=a.run(self.seed,client=None,dry_run=False,turns=50,cap=.000001)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['total_api_attempts'],0)

if __name__=='__main__':unittest.main()
