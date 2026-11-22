"""Free conformance tests for CG-1's native new-definition and receipt pipeline."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'src')]
import concept_genesis as cg
import native_author as n
import ucl
import sap_portable

class CG1Tests(unittest.TestCase):
    def initial(self):
        pkt=ucl.load_json(n.BASELINE.read_text())
        return {'packet':pkt,'wire':json.dumps(sap_portable.encode(pkt)),
                'last_act':None,'last_concept':None,'invented':set(),'failed':0}
    def test_full_dry_run_six_turns(self):
        r=cg.run(dry_run=True,turns=6,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['delivered'],6)
        self.assertEqual(r['first_attempt_valid'],6)
        self.assertEqual(r['new_definitions_created'],2)
        self.assertEqual(r['receipts_verified'],5)
        self.assertEqual(r['estimated_cost_usd'],0)
        self.assertEqual(r['api_attempts'],6)
    def test_first_turn_requires_actual_new_definition(self):
        st=self.initial();x=json.loads(cg.synthetic(0,'clarke-1.0',st))
        x['authored']['new_definitions']={}
        with self.assertRaisesRegex(ValueError,'requires one novel'):
            cg.validate_response(json.dumps(x),st,0,'clarke-1.0')
    def test_missing_formula_use_is_rejected(self):
        st=self.initial();x=json.loads(cg.synthetic(0,'clarke-1.0',st))
        x['authored']['act']['expressions']=['~[P][A]']
        x['authored']['explanation']=x['authored']['conclusion']='~[P][A]'
        with self.assertRaisesRegex(ValueError,'not used'):
            cg.validate_response(json.dumps(x),st,0,'clarke-1.0')
    def test_wrong_or_overwritten_glyph_is_rejected(self):
        st=self.initial();x=json.loads(cg.synthetic(0,'clarke-1.0',st))
        x['authored']['new_definitions']['P']=x['authored']['new_definitions'].pop('C')
        with self.assertRaisesRegex(ValueError,'unused'):
            cg.validate_response(json.dumps(x),st,0,'clarke-1.0')
    def test_valid_first_turn_full_portable_roundtrip(self):
        st=self.initial();obj,p,wire,new=cg.validate_response(
            cg.synthetic(0,'clarke-1.0',st),st,0,'clarke-1.0')
        self.assertEqual(new,['C'])
        self.assertEqual(p['definitions']['C']['id'],ucl.definition_id(obj['authored']['new_definitions']['C']))
        self.assertEqual(sap_portable.decode(json.loads(wire)),p)
        self.assertEqual(p['definitions']['P'],st['packet']['definitions']['P'])
        self.assertEqual(len(p['discourse']['acts']),len(st['packet']['discourse']['acts'])+1)
    def test_budget_prevents_any_paid_requests(self):
        r=cg.run(client=None,dry_run=False,turns=4,cap=.000001)
        self.assertEqual(r['status'],'budget_stop')
        self.assertEqual(r['api_attempts'],0)

if __name__=='__main__':unittest.main()
