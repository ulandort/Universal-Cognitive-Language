"""Offline unit tests. Never call a paid endpoint."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import live_radium as lr
import ucl

class TestLiveRadium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=ucl.load_json(lr.BASELINE.read_text())
        ucl.check(cls.base)

    def test_all_mock_handoffs(self):
        for caseid in range(4):
            c=lr.case_for(caseid)
            for fmt in lr.FORMATS:
                if fmt=='english': msg='I reject only the property B statement.'
                elif fmt=='structured_english':msg=json.dumps({'claim_id':'theory','target_path':[c['path']],'action':c['action'],'note':'Stance for testing.'})
                else:msg=json.dumps({'action':c['action'],'path':c['path'],'note':'Stance for testing.'})
                h,meta=lr.build_handoff(fmt,c,msg,self.base)
                self.assertTrue(meta['syntax_ok'])
                self.assertTrue(h)
                messages=lr.receiver_messages(fmt,h,self.base)
                self.assertIn('MESSAGE:',messages[-1]['content'])
                if fmt.startswith('ucl_'):
                    wire=json.loads(h)
                    self.assertEqual(wire['profile'],fmt.replace('ucl_',''))
                    rec=lr.guide_profiles.decode(wire,self.base['guide'] if fmt=='ucl_compact' else None)
                    self.assertEqual(rec['acknowledgements'][-1]['target']['path'],[c['path']])
                    self.assertEqual(rec['acknowledgements'][-1]['action'],c['action'])

    def test_missing_reference_and_modified_hash(self):
        c=lr.case_for(0)
        with self.assertRaises(ValueError):
            lr.build_handoff('ucl_compact',c,json.dumps({'action':'reject','path':8,'note':'bad'}),self.base)
        with self.assertRaises(ValueError):
            lr.build_handoff('structured_english',c,'{"claim_id":"theory","target_path":[9],"action":"reject","note":"bad"}',self.base)

    def test_dry_run_zero_cost(self):
        r=lr.run(None,trials=4,cap=0.50,dry_run=True)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['completed'],16)
        self.assertEqual(r['failures'],0)
        self.assertEqual(r['spent_usd_estimate'],0)

    def test_sender_intent_scored_independently(self):
        case={'claim_id':'theory','path':0,'action':'reject'}
        self.assertTrue(lr.score_authored('ucl_portable',case,'{"action":"reject","path":0,"note":"ok"}'))
        self.assertFalse(lr.score_authored('ucl_portable',case,'{"action":"reject","path":1,"note":"wrong target"}'))
        self.assertFalse(lr.score_authored('structured_english',case,'{"claim_id":"theory","target_path":[0],"action":"adopt-for-discussion","note":"wrong stance"}'))
        self.assertIsNone(lr.score_authored('english',case,'I reject the P component, not B.'))
        self.assertFalse(lr.score_authored('ucl_compact',case,''))
        self.assertEqual(lr.failure_kind('', 'length', 'sender'),'sender_empty_output_length')

    def test_clarke_first_and_later_role_swap(self):
        self.assertEqual(lr.MODEL_CHOICES[0],'clarke-1.0')
        self.assertEqual(lr.MODEL_CHOICES[1],'hal-1.0')
        self.assertEqual(lr.case_for(0)['path'],0)
        self.assertEqual(lr.case_for(2)['path'],1)

    def test_budget_guards(self):
        with self.assertRaises(ValueError):lr.run(None,9,.5,True)
        with self.assertRaises(ValueError):lr.run(None,1,10,True)
        self.assertGreater(lr.reserve_upper_bound('hal-1.0',[{'content':'hello'}]),0)

if __name__=='__main__':unittest.main()