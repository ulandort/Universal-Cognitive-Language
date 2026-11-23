"""Offline cold-start and tamper tests for self-contained UCL 2.0 SAP-1 Portable."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src'),str(ROOT/'benchmarks')]
import sap_portable as p
import native_author as n
import ucl
import ucl_only_conversation as run

class TestSelfContainedSAP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=ucl.load_json(n.BASELINE.read_text(encoding='utf-8'))
    def test_portable_roundtrip_is_self_contained_without_external_guide(self):
        env=p.encode(self.baseline)
        data=json.loads(json.dumps(env))
        self.assertEqual(p.decode(data),self.baseline)
        self.assertEqual(data['format'],p.FORMAT)
        self.assertIn('guide',data['packet'])
        self.assertIn('definitions',data['packet'])
        self.assertIn('discourse',data['packet'])
        self.assertIn('history',data['packet'])
        self.assertIn('reference_rules',data['structural_rules']['rules'])
        self.assertIn('typed_formula_examples',data['structural_rules']['rules'])
        self.assertIn('language_extension_policy',data['structural_rules']['rules'])
        self.assertNotIn('reference_uri',json.dumps(data))
        self.assertNotIn('https://',json.dumps(data))
        self.assertEqual(len(data['structural_rules']['sha256']),43)
    def test_tamper_rule_hash_and_envelope_hash(self):
        valid=p.encode(self.baseline)
        altered=copy.deepcopy(valid)
        altered['structural_rules']['rules']['reference_rules']['ack_id']='Anything allowed'
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):
            p.decode(altered)
        altered['structural_rules']['sha256']=p.rules_hash(
            altered['structural_rules']['rules'])
        altered['checksum']=p.envelope_checksum(altered)
        with self.assertRaisesRegex(ValueError,'unknown or altered'):
            p.decode(altered)
        altered=copy.deepcopy(valid)
        altered['packet']['history']['summary']='forged history'
        with self.assertRaisesRegex(ValueError,'envelope checksum mismatch'):
            p.decode(altered)
        altered=copy.deepcopy(valid)
        altered['checksum']='forged'
        with self.assertRaisesRegex(ValueError,'envelope checksum mismatch'):
            p.decode(altered)
    def test_complete_eight_turn_offline_emits_v2_wire(self):
        result=run.run(dry_run=True,turns=8,directions=1,cap=.001,max_repairs=2)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(result['transport_format'],p.FORMAT)
        self.assertTrue(result['structural_rules_embedded'])
        self.assertEqual(result['conversations'][0]['valid_packets'],8)
        self.assertEqual(result['conversations'][0]['max_consecutive_valid_packets'],8)
        for row in result['cases']:
            env=json.loads(row['handoff'])
            packet=p.decode(env)
            self.assertEqual(row['self_contained_profile_hash'],
                             env['structural_rules']['sha256'])
            self.assertEqual(packet['discourse']['acts'][-1]['id'],'t'+str(9+row['turn']))
            self.assertEqual(env['structural_rules']['rules']['id'],'UCL/2.0-SAP-1')
            self.assertIn('epistemic',env['structural_rules']['rules']['type_rules'])
    def test_proposals_do_not_invent_new_normative_operators(self):
        env=p.encode(self.baseline)
        policy=env['structural_rules']['rules']['language_extension_policy']
        self.assertIn('NOT silently valid',policy['new_core_operators'])
        self.assertIn('no_central_registry',policy)

if __name__=='__main__':unittest.main()
