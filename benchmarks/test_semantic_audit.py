"""SVP-1 protects novelty; independent local audit never rejects a UCL packet."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'benchmarks'),str(ROOT/'src')]
import sap_portable as portable
import semantic_audit as audit
import native_author as n
import ucl

class TestSVP1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=ucl.load_json(n.BASELINE.read_text())
    def test_svp_embedded_but_no_verdicts_bloat_or_central_service(self):
        env=portable.encode(self.packet)
        svp=env['structural_rules']['rules']['semantic_verification']
        self.assertEqual(svp['id'],'UCL/2.0-SVP-1-DRAFT')
        self.assertFalse(svp['no_silent_semantic_repair'] is False)
        self.assertIn('novel-or-unresolved',svp['verdicts'])
        self.assertIn('not-assessed',svp['verdicts'])
        self.assertIn('NEVER reject',svp['novelty'])
        self.assertNotIn('audit_results',env)
        self.assertNotIn('semantic_verdict',env)
        self.assertEqual(portable.decode(env),self.packet)
    def test_unfamiliar_but_well_typed_hypothesis_preserved(self):
        formula='|[~[P][A]][![~[B][A]]]'
        x=audit.analyze_expression(formula,self.packet['definitions'])
        self.assertEqual(x['verdict'],'formally-consistent-under-assumptions')
        self.assertIn('witness',x)
    def test_real_contradiction_only_under_explicit_assumptions(self):
        formula='![~[P][A]]'
        x=audit.analyze_expression(formula,self.packet['definitions'],
                                   assumptions=['~[P][A]'])
        self.assertEqual(x['verdict'],'demonstrated-contradiction-under-assumptions')
        self.assertEqual(x['assumptions'],['~[P][A]'])
        y=audit.analyze_expression(formula,self.packet['definitions'])
        self.assertEqual(y['verdict'],'formally-consistent-under-assumptions')
    def test_novel_syntactically_valid_formula_not_rejected_or_rewritten(self):
        env=portable.encode(self.packet)
        before=json.dumps(env,sort_keys=True)
        report=audit.audit(env)
        self.assertEqual(json.dumps(env,sort_keys=True),before)
        self.assertTrue(report['independent_sidecar'])
        self.assertFalse(report['transport_packet_modified'])
        self.assertTrue(all(x['natural_language_alignment']=='not-assessed'
                            for x in report['observations']))
        self.assertTrue(all(x['novelty'].startswith('unresolved')
                            for x in report['observations']))
        self.assertEqual(report['packet_checksum'],env['checksum'])
    def test_bad_verification_policy_detected(self):
        env=portable.encode(self.packet)
        env['structural_rules']['rules']['semantic_verification']['novelty']='reject any unknown hypothesis'
        with self.assertRaises(ValueError):
            portable.decode(env)
    def test_limited_computation_degrades_to_not_assessed(self):
        f='&[~[P][A]][~[B][A]]'
        x=audit.analyze_expression(f,self.packet['definitions'],atom_limit=1)
        self.assertEqual(x['verdict'],'not-assessed')

if __name__=='__main__':unittest.main()
