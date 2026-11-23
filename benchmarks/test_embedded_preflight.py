"""Portable .txt self-contained local authoring guide compatibility and security."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src'),str(ROOT/'benchmarks')]
import ucl,sap_portable as s
from native_author import contrib_template

class LocalAuthoringGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=ucl.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text(encoding='utf8'))
    def test_new_txt_self_contained_without_registry(self):
        e=s.encode(self.packet)
        self.assertEqual(s.decode(json.loads(json.dumps(e))),self.packet)
        guide=e['structural_rules']['rules']['type_rules']['local_authoring_preflight']
        self.assertIn('target.path=[0] (integer)',guide)
        self.assertIn('UCL strings',guide)
        self.assertIn('no network',guide)
        self.assertLess(len(guide),450)
        self.assertEqual(e['structural_rules']['sha256'],s.rules_hash(e['structural_rules']['rules']))
        print('UCL2_PINNED_RULES_SHA='+s.rules_hash(s.RULES))
    def test_authentic_legacy_rules_still_decode(self):
        e=s.encode(self.packet)
        e['structural_rules']['rules']=copy.deepcopy(s.LEGACY_RULES)
        e['structural_rules']['sha256']=s.rules_hash(s.LEGACY_RULES)
        e['checksum']=s.envelope_checksum(e)
        self.assertEqual(s.decode(e),self.packet)
    def test_modified_rules_rejected_even_with_recomputed_hashes(self):
        e=s.encode(self.packet)
        e['structural_rules']['rules']['type_rules']['local_authoring_preflight']='not the authentic guide'
        e['structural_rules']['sha256']=s.rules_hash(e['structural_rules']['rules'])
        e['checksum']=s.envelope_checksum(e)
        with self.assertRaisesRegex(ValueError,'unknown or altered'):
            s.decode(e)
    def test_structural_example_does_not_encourage_string_path(self):
        contribution=contrib_template('clarke-1.0')
        self.assertEqual(contribution['acknowledgements'][0]['target']['path'],[0])
        self.assertIs(type(contribution['acknowledgements'][0]['target']['path'][0]),int)

if __name__=='__main__':unittest.main()
