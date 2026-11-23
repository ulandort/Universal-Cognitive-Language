"""CG-2: full eight-turn stable UCL/2.0 concept genesis + challenge, offline oracle tests."""
import json,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import genesis_challenge_8 as cg
import sap_portable as portable
import ucl
import native_author as n

class CG2Tests(unittest.TestCase):
    def test_eight_turn_offline_continuity_and_immutability(self):
        r=cg.run(dry_run=True,turns=8,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['attempted_turns'],8)
        self.assertEqual(r['delivered'],8)
        self.assertEqual(r['first_attempt_valid'],8)
        self.assertEqual(r['new_definitions_created'],4)
        self.assertEqual(r['receipts_verified'],7)
        original=ucl.load_json(n.BASELINE.read_text())
        old_ids=set(original['definitions'])
        earlier_acts=original['discourse']['acts']
        for i,row in enumerate(r['cases']):
            self.assertTrue(row['valid'])
            wire=json.loads(row['handoff'])
            self.assertEqual(wire['format'],'UCL/2.0-SAP1-PORTABLE')
            p=portable.decode(wire)
            self.assertEqual(len(p['discourse']['acts']),len(earlier_acts)+1)
            self.assertEqual(p['discourse']['acts'][:-1],earlier_acts)
            self.assertEqual(p['history']['status'],'fully-expanded')
            for symbol in old_ids:
                self.assertEqual(p['definitions'][symbol],original['definitions'][symbol])
            earlier_acts=p['discourse']['acts']
        self.assertEqual(len(earlier_acts),len(original['discourse']['acts'])+8)
    def test_no_extra_budget_or_unapproved_turn_count(self):
        with self.assertRaisesRegex(ValueError,'exactly 8'):
            cg.run(dry_run=True,turns=6)
        with self.assertRaisesRegex(ValueError,'cap'):
            cg.run(dry_run=True,cap=5.5)
    def test_actual_novel_definitions_are_required_in_first_four_turns(self):
        p=ucl.load_json(n.BASELINE.read_text())
        st={'packet':p,'wire':json.dumps(portable.encode(p)),
            'last_act':None,'last_concept':None,'invented':set(),'failed':0}
        for turn in range(4):
            draft=json.loads(cg.synthetic(turn,n.MODELS[turn%2],st))
            self.assertEqual(len(draft['authored']['new_definitions']),1)
            if turn==0:
                draft['authored']['new_definitions']={}
                with self.assertRaises(ValueError):
                    cg.validate_response(json.dumps(draft),st,turn,n.MODELS[turn%2])
    def test_thoughtful_challenge_without_forced_agreement(self):
        p=ucl.load_json(n.BASELINE.read_text())
        st={'packet':p,'wire':json.dumps(portable.encode(p)),
            'last_act':None,'last_concept':None,'invented':set(),'failed':0}
        prompt=cg.make_messages(st,4,'clarke-1.0')[1]['content']
        self.assertIn('Challenge a prior claim',prompt)
        self.assertIn('Distinguish conceptual assumptions',prompt)
        self.assertNotIn('at least 20 characters',prompt)

if __name__=='__main__':unittest.main()
