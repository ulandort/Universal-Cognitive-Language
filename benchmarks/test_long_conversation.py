"""Free deterministic regression checks for the 10-turn benchmark."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import long_conversation as long
import ucl


class TestLongConversation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets=long.build_packets()

    def test_full_history_and_distinct_semantics(self):
        p=self.packets[10]
        self.assertEqual(len(p['discourse']['acts']),18)
        self.assertEqual(p['history']['status'],'fully-expanded')
        self.assertNotEqual(p['definitions']['C']['id'],p['definitions']['P']['id'])
        self.assertEqual(p['discourse']['current'],'t18')
        ucl.check(p)

    def test_all_four_formats_both_checkpoints(self):
        for checkpoint,p in self.packets.items():
            for fmt in long.FORMATS:
                s=long.fmt_content(fmt,p)
                self.assertTrue(s)
                msgs=long.messages(fmt,p,checkpoint)
                self.assertTrue(msgs[-1]['content'].endswith('}'))
                self.assertIn('QUESTIONS', msgs[-1]['content'])
                if fmt.startswith('ucl_'):
                    wire=json.loads(s)
                    rec=long.guide_profiles.decode(wire,p['guide'] if fmt=='ucl_compact' else None)
                    self.assertEqual(ucl.canon(rec),ucl.canon(p))

    def test_answers_exact_and_wrong(self):
        for cp,qs in long.PROBES.items():
            ans={'answers':{k:val[2] for k,val in qs.items()}}
            self.assertTrue(all(long.evaluate_answer(json.dumps(ans),cp).values()))
            self.assertIsNone(long.evaluate_answer('{}',cp))
            self.assertIsNone(long.evaluate_answer('not-json',cp))

    def test_free_dry_run(self):
        out=long.run(cap=.01,dry_run=True)
        self.assertEqual(out['status'],'dry_run')
        self.assertEqual(out['completed'],8)
        self.assertEqual(out['questions_total'],24)
        self.assertEqual(out['questions_correct'],24)
        self.assertEqual(out['estimated_cost_usd'],0)

    def test_cap_rules(self):
        for invalid in (0,-1,3):
            with self.assertRaises(ValueError):long.run(cap=invalid,dry_run=True)


if __name__=='__main__':unittest.main()