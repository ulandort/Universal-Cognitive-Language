"""Free L25 packet/history/stress conformance tests using authentic RR-1 seed."""
import json,os,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import autonomous_25 as a
import sap_portable

@unittest.skipUnless(os.environ.get('L25_SEED'),'Real RR-1 seed required for L25 regression')
class L25Tests(unittest.TestCase):
    def setUp(self):
        self.seed=os.environ['L25_SEED']
        self.packet=a.load_seed(self.seed)
        self.state={'packet':self.packet,
                    'wire':json.dumps(sap_portable.encode(self.packet)),
                    'delivered_count':0}
    def test_full_25_turn_dry_run_history_no_condensation(self):
        r=a.run(self.seed,dry_run=True,turns=25,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['delivered'],25)
        self.assertEqual(r['first_attempt_valid'],25)
        self.assertEqual(r['checkpoint_references_validated'],5)
        self.assertEqual(r['total_api_attempts'],25)
        self.assertGreater(r['last_wire_bytes'],r['first_wire_bytes'])
        packet=sap_portable.decode(json.loads(r['cases'][-1]['handoff']))
        self.assertEqual(len(packet['discourse']['acts']),45)
        self.assertEqual(packet['history']['status'],'fully-expanded')
        self.assertEqual(len(packet['acknowledgements']),41)
        self.assertEqual(packet['definitions'],self.packet['definitions'])
        self.assertEqual(packet['discourse']['acts'][:20],self.packet['discourse']['acts'])
    def test_rejects_mutation_and_missing_ack(self):
        response=json.loads(a.synthetic(self.state,0,'clarke-1.0'))
        response['authored']['acknowledgements']=[]
        with self.assertRaises((ValueError,TypeError)):
            a.validate(json.dumps(response),self.state,0,'clarke-1.0')
        response=json.loads(a.synthetic(self.state,0,'clarke-1.0'))
        response['authored']['new_definitions']={}
        with self.assertRaises((ValueError,TypeError)):
            a.validate(json.dumps(response),self.state,0,'clarke-1.0')
    def test_rejects_undelivered_receipt(self):
        response=json.loads(a.synthetic(self.state,0,'clarke-1.0'))
        response['interpretation']='An invented preceding stress conversation that was never delivered.'
        with self.assertRaisesRegex(ValueError,'must be null'):
            a.validate(json.dumps(response),self.state,0,'clarke-1.0')
    def test_budget_stop_before_paid_calls(self):
        r=a.run(self.seed,client=None,dry_run=False,cap=.000001)
        self.assertEqual(r['status'],'budget_stop')
        self.assertEqual(r['total_api_attempts'],0)

if __name__=='__main__':unittest.main()
