"""Cold-recipient source fidelity: exactly same original CG-2 facts across formats."""
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cold_recipient_attack as m

class ColdRecipientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('CG2_SOURCE_PATH')
        if not source or not Path(source).is_file():
            raise unittest.SkipTest('Authentic CG-2 source artifact is supplied by research workflow')
        cls.env,cls.packet=m.seed(source)
        cls.source=source
    def test_origin_is_real_stable_packet_and_definitions_distinct(self):
        self.assertEqual(self.env['format'],'UCL/2.0-SAP1-PORTABLE')
        self.assertEqual(self.packet['discourse']['current'],'t16')
        self.assertEqual(len(self.packet['discourse']['acts']),15)
        ids=[self.packet['definitions'][g]['id'] for g in 'ECFGIK']
        self.assertEqual(len(set(ids)),6)
    def test_identical_original_facts_and_balanced_conditions(self):
        structured=json.loads(m.structured_record(self.packet))
        self.assertEqual(structured['discourse'],self.packet['discourse'])
        self.assertEqual(structured['definitions'],self.packet['definitions'])
        self.assertEqual(structured['acknowledgements'],self.packet['acknowledgements'])
        order=list(m.order())
        self.assertEqual(len(order),8)
        for f in m.FORMATS:
            for c in m.CONDITIONS:
                self.assertEqual(sum(x[2]==f and x[1]==c for x in order),2)
    def test_all_eight_keys_independently_scored(self):
        correct=json.dumps({'answers':{k:v[2] for k,v in m.QUESTIONS.items()}})
        score,error=m.score(correct)
        self.assertIsNone(error)
        self.assertEqual(sum(score.values()),8)
        self.assertIsNone(m.score('{"answers":{"latest":"d"}}')[0])
        self.assertIsNone(m.score('{"latest":"d"}')[0])
    def test_dry_run_no_api_calls_eight_expected_responses(self):
        x=m.run(self.source,dry_run=True,cap=3.5)
        self.assertEqual(x['status'],'dry_run')
        self.assertEqual(x['attempted_calls'],8)
        self.assertEqual(x['estimated_cost_usd'],0)
        self.assertEqual(sum(y['correct'] for y in x['cases']),64)
        self.assertEqual(x['by_format']['ucl2']['strict_total'],32)
        self.assertEqual(x['by_format']['structured_english']['strict_total'],32)
    def test_hard_budget_cap(self):
        with self.assertRaises(ValueError):m.run(self.source,dry_run=True,cap=3.51)

if __name__=='__main__':unittest.main()
