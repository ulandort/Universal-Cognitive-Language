import sys,copy,json,unittest,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import ucl
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.small=ucl.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text());cls.long=ucl.load_json((ROOT/'examples/cross_model_conversation_13_turns.json').read_text())
    def test_plain_roundtrip(self):
        self.assertEqual(ucl.load_json(ucl.dump_json(self.small)),self.small)
    def test_canonical_roundtrip(self):
        self.assertEqual(ucl.load_json(ucl.canon(self.long).decode('ascii')),self.long)
    def test_build_draft(self):
        self.assertEqual(ucl.build(ucl.draft_from_packet(self.small)),self.small)
    def test_bad_hash(self):
        q=copy.deepcopy(self.small);q['integrity']['sha256']='fake'
        with self.assertRaises(ValueError):ucl.check(q)
    def test_wrong_definition_identity(self):
        q=copy.deepcopy(self.small);q['definitions']['P']['definition']['gloss']='new undisclosed meaning';q['integrity']['sha256']=ucl.packet_id(q)
        with self.assertRaises(ValueError):ucl.check(q)
    def test_condense_preserves_claim_acks(self):
        d=ucl.draft_from_packet(self.small)
        with self.assertRaises(ValueError):ucl.condense_draft(d,['t1'],'Condense older acts')
    def test_condense_unreferenced(self):
        d=ucl.draft_from_packet(self.small)
        # t6 is referenced by t7 synthesis; cannot be dropped.
        with self.assertRaises(ValueError):ucl.condense_draft(d,['t6'],'Condense older acts')
    def test_incremental_author(self):
        sys.path.insert(0,str(ROOT/'tools'))
        import author
        c=json.loads((ROOT/'examples/contribution_example.json').read_text())
        q=author.author(self.small,c)
        self.assertEqual(q['discourse']['current'],'t9')
        self.assertEqual(ucl.check(q)['status'],'VALID UCL/1.0')
    def test_cross_language_canonical(self):
        if subprocess.run(['which','node'],capture_output=True).returncode: self.skipTest('node unavailable')
        f=ROOT/'examples/cross_model_conversation_13_turns.cjson'
        r=subprocess.run(['node',str(ROOT/'tools/check_ucl.js'),str(f)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_tool_cli(self):
        r=subprocess.run([sys.executable,str(ROOT/'src/ucl.py'),'check',str(ROOT/'examples/cross_model_conversation_8_turns.json')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
if __name__=='__main__':unittest.main()
