"""Free preregistered exact-key comparison and 2.0 wire tests."""
import json,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import ucl2_vs_structured as t
import sap_portable
import ucl

class UCL2ComparisonTests(unittest.TestCase):
    def test_identical_fact_fixtures_and_keyed_questions(self):
        packets=t.build_packets()
        self.assertEqual(set(packets),{10,25})
        for checkpoint,pkt in packets.items():
            ucl.check(pkt)
            self.assertEqual(sap_portable.decode(json.loads(t.format_record('ucl2_stable',pkt))),pkt)
            structured=json.loads(t.format_record('structured_english',pkt))
            self.assertEqual(len(structured['acts']),len(pkt['discourse']['acts']))
            self.assertEqual(structured['acknowledgements'],pkt['acknowledgements'])
            self.assertEqual(structured['claims'],pkt['claims'])
            self.assertEqual(set(structured['definitions']),set(pkt['definitions']))
            for key in pkt['definitions']:
                self.assertEqual(structured['definitions'][key]['id'],pkt['definitions'][key]['id'])
            expected={k:q[2] for k,q in t.QUESTIONS[checkpoint].items()}
            results=t.score(json.dumps({'answers':expected}),checkpoint)
            self.assertEqual(sum(results.values()),len(expected))
    def test_full_matched_two_repetition_oracle(self):
        r=t.run(dry_run=True,repetitions=2,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['completed'],16)
        self.assertEqual(r['questions_total'],112)
        self.assertEqual(r['questions_correct'],112)
        self.assertEqual(set(r['by_format']),{'ucl2_stable','structured_english'})
        self.assertEqual(r['by_format']['ucl2_stable']['total'],56)
        self.assertEqual(r['by_format']['structured_english']['total'],56)
        self.assertEqual(r['estimated_cost_usd'],0)
        for group in {(x['repetition'],x['checkpoint'],x['model']) for x in r['cases']}:
            formats=[x['format'] for x in r['cases'] if (x['repetition'],x['checkpoint'],x['model'])==group]
            self.assertEqual(set(formats),{'ucl2_stable','structured_english'})
    def test_budget_and_invalid_answer(self):
        with self.assertRaises(ValueError):t.run(dry_run=True,cap=3.6)
        with self.assertRaises(ValueError):t.run(dry_run=True,repetitions=4)
        self.assertIsNone(t.score('',10))
        self.assertIsNone(t.score('{"answers":{"original_p":"b"}}',10))

if __name__=='__main__':unittest.main()
