"""CCR-1 free conformance oracle using authentic externally model-authored CG-2."""
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cold_continuation as c
import sap_portable

class ColdContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=os.environ.get('CG2_SOURCE_PATH')
        if not cls.source or not Path(cls.source).is_file():
            raise unittest.SkipTest('Authentic CG-2 source supplied by workflow')
        cls.env,cls.packet=c.seed(cls.source)
    def test_live_source_lineage_exact_and_six_hashes(self):
        self.assertEqual(self.packet['discourse']['current'],'t16')
        self.assertEqual(len(self.packet['discourse']['acts']),15)
        ids=[self.packet['definitions'][g]['id'] for g in c.RECEIPT_GLYPHS]
        self.assertEqual(len(set(ids)),6)
    def test_eight_pairwise_independent_challenges(self):
        cases=list(c.cases())
        self.assertEqual(len(cases),8)
        self.assertEqual(set(x[1] for x in cases),set(c.MODELS))
        for task in range(4):
            self.assertEqual(sum(x[0]==task for x in cases),2)
    def test_dry_run_full_packet_validation_and_no_edited_history(self):
        r=c.run(self.source,dry_run=True,max_repairs=1,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['delivered'],8)
        self.assertEqual(r['first_try_valid'],8)
        self.assertEqual(r['exact_six_definition_receipts'],8)
        self.assertEqual(r['estimated_cost_usd'],0)
        self.assertEqual(r['api_attempts'],8)
        for row in r['cases']:
            self.assertEqual(row['history_acts'],16)
            wire=json.loads(row['handoff'])
            self.assertEqual(wire['format'],'UCL/2.0-SAP1-PORTABLE')
            packet=sap_portable.decode(wire)
            self.assertEqual(packet['definitions'],self.packet['definitions'])
            self.assertEqual(packet['discourse']['acts'][:-1],self.packet['discourse']['acts'])
            self.assertEqual(packet['history']['status'],'fully-expanded')
    def test_wrong_definition_identity_rejected(self):
        raw=json.loads(c.synthetic(self.packet,c.MODELS[0]))
        raw['receipt']['G']='a-definitely-false-id'
        with self.assertRaisesRegex(ValueError,'immutable concept IDs'):
            c.validate(json.dumps(raw),self.packet,c.MODELS[0])
    def test_no_formal_relationship_rejected(self):
        raw=json.loads(c.synthetic(self.packet,c.MODELS[0]))
        raw['authored']['act']['expressions']=['~[G][A]','~[I][A]']
        raw['authored']['explanation']='~[G][A]'
        raw['authored']['conclusion']='~[I][A]'
        with self.assertRaisesRegex(ValueError,'compound relation'):
            c.validate(json.dumps(raw),self.packet,c.MODELS[0])
    def test_authoring_remains_budget_bounded(self):
        with self.assertRaisesRegex(ValueError,'3.75'):
            c.run(self.source,dry_run=True,cap=4.01)
        with self.assertRaisesRegex(ValueError,'max repairs'):
            c.run(self.source,dry_run=True,max_repairs=9)
if __name__=='__main__':unittest.main()
