"""SAP-1 UCL/2.0 self-contained portable conformance and tampering tests."""
import sys,unittest,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src')]
import ucl
import ucl2_portable as p

class TestPortableUCL2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=ucl.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text())
    def test_full_guide_profile_history_and_symbols_embedded(self):
        env=p.encode(self.original)
        self.assertEqual(env['packet']['guide'],self.original['guide'])
        self.assertEqual(env['packet']['discourse']['acts'],self.original['discourse']['acts'])
        self.assertIn('authoring_contribution_schema',env['structural_profile'])
        self.assertIn('symbolic_grammar',env['structural_profile'])
        self.assertIn('extension_policy',env['structural_profile']['invariants'])
        self.assertTrue(p.check(env)['self_contained'])
        self.assertEqual(p.decode(json.loads(json.dumps(env))),self.original)
        self.assertNotIn('url',env)
    def test_compromised_profile_rejected_even_with_recomputed_envelope_hash(self):
        x=p.encode(self.original)
        x['structural_profile']['symbolic_grammar']['examples']['not_P']='NON_STANDARD'
        x['structural_profile_sha256']=p.profile_digest(x['structural_profile'])
        x['integrity']={'sha256':p.envelope_digest(x)}
        with self.assertRaisesRegex(ValueError,'profile not the locally recognized'):
            p.check(x)
    def test_tampering_detected_and_entire_packet_still_validated(self):
        e=p.encode(self.original)
        x=copy.deepcopy(e)
        x['structural_profile_sha256']='x'
        with self.assertRaisesRegex(ValueError,'profile hash'):
            p.check(x)
        x=copy.deepcopy(e)
        x['packet']['integrity']['sha256']='x'
        x['integrity']={'sha256':p.envelope_digest(x)}
        with self.assertRaises(ValueError):p.check(x)
        x=copy.deepcopy(e)
        x['packet']['guide']={}
        x['integrity']={'sha256':p.envelope_digest(x)}
        with self.assertRaises(ValueError):p.check(x)
    def test_repeatable_canonical_hashes(self):
        a=p.encode(self.original)
        b=p.encode(json.loads(json.dumps(self.original,sort_keys=False)))
        self.assertEqual(a['integrity']['sha256'],b['integrity']['sha256'])
        self.assertEqual(a['structural_profile_sha256'],b['structural_profile_sha256'])
        self.assertEqual(p.profile_digest(p.AUTHORING_PROFILE),a['structural_profile_sha256'])
    def test_metadata_limited_to_explicit_schema_and_no_central_dependency(self):
        e=p.encode(self.original)
        e['central_registry']='example'
        with self.assertRaises(ValueError):p.check(e)

if __name__=='__main__':unittest.main()
