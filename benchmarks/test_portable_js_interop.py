"""Offline cross-language conformance for the exact proposed UCL/2.0 Portable wire."""
import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src'),str(ROOT/'benchmarks')]
import ucl,sap_portable as sp

@unittest.skipUnless(shutil.which('node'),'Node.js needed for independent JS conformance')
class PortableJavaScriptInterop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=ucl.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text(encoding='utf8'))
    def run_js(self,obj):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wire.txt'
            p.write_text(json.dumps(obj,ensure_ascii=True),encoding='utf8')
            return subprocess.run(['node',str(ROOT/'tools/check_ucl_portable.js'),str(p)],
                                  text=True,capture_output=True,timeout=15)
    def test_python_and_js_both_accept_complete_portable(self):
        obj=sp.encode(self.packet)
        self.assertEqual(sp.decode(obj),self.packet)
        js=self.run_js(obj)
        self.assertEqual(js.returncode,0,js.stderr)
        result=json.loads(js.stdout)
        self.assertEqual(result['packet_sha256'],self.packet['integrity']['sha256'])
        self.assertEqual(result['rules_sha256'],obj['structural_rules']['sha256'])
        self.assertEqual(result['discourse_acts'],len(self.packet['discourse']['acts']))
        guide_sha=subprocess.run(['node','-e',"const {hash}=require('./tools/check_ucl.js');console.log(hash('UCL-GUIDE-PIN-2\\n',JSON.parse(process.argv[1])))",json.dumps(self.packet['guide'])],cwd=ROOT,text=True,capture_output=True,timeout=15,check=True).stdout.strip()
        print('UCL2_PINNED_GUIDE_SHA='+guide_sha)
    def test_python_and_js_reject_tamper(self):
        obj=sp.encode(self.packet)
        obj['packet']['integrity']['sha256']='not-the-authentic-hash'
        with self.assertRaises(ValueError):sp.decode(obj)
        self.assertNotEqual(self.run_js(obj).returncode,0)
    def test_both_reject_rehashed_unknown_rules(self):
        obj=sp.encode(self.packet)
        obj['structural_rules']['rules']['type_rules']['local_authoring_preflight']='silently rewrite semantics'
        obj['structural_rules']['sha256']=sp.rules_hash(obj['structural_rules']['rules'])
        obj['checksum']=sp.envelope_checksum(obj)
        with self.assertRaises(ValueError):sp.decode(obj)
        self.assertNotEqual(self.run_js(obj).returncode,0)
    def test_formula_roles_agree_and_both_reject_duplicate(self):
        act=self.packet['discourse']['acts'][0]['id']
        valid=[{'act':act,'index':0,'role':'hypothesis'}]
        obj=sp.encode(self.packet,formula_roles=valid)
        self.assertEqual(sp.decode(obj),self.packet)
        self.assertEqual(self.run_js(obj).returncode,0)
        obj['formula_roles']=valid+valid
        obj['checksum']=sp.envelope_checksum(obj)
        with self.assertRaises(ValueError):sp.decode(obj)
        self.assertNotEqual(self.run_js(obj).returncode,0)

if __name__=='__main__':unittest.main()
