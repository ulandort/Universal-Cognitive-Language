"""Offline cross-language conformance for the exact proposed UCL/2.0 Portable wire."""
import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'src'),str(ROOT/'benchmarks')]
import ucl,sap_portable as sp
import core,portable

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
        self.assertEqual(guide_sha,'ZFIZCtsxvrSp7PH12QlsH2re08Xd_kS78JKFunwYO_M')
    def test_python_and_js_reject_tamper(self):
        obj=sp.encode(self.packet)
        obj['packet']['integrity']['sha256']='not-the-authentic-hash'
        with self.assertRaises(ValueError):sp.decode(obj)
        self.assertNotEqual(self.run_js(obj).returncode,0)
    def test_both_reject_rehashed_modified_inner_guide(self):
        obj=sp.encode(self.packet)
        obj['packet']['guide']['version']='forged version'
        obj['packet']['integrity']['sha256']=ucl.packet_id(obj['packet'])
        obj['checksum']=sp.envelope_checksum(obj)
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

    def test_supported_guide_and_rules_pins(self):
        draft = core.draft_from_packet(self.packet)
        for record in draft['definitions'].values():
            record.pop('id')
        for version in portable.FORMAT_BY_VERSION:
            with self.subTest(version=version):
                envelope = portable.encode(core.build(draft, version=version))
                checked = self.run_js(envelope)
                self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_portable_clis_reject_nonconforming_json_at_the_input_boundary(self):
        valid = portable.encode(core.upgrade_packet(self.packet))
        # Keep the negative fixtures permanently invalid and assert the parser error.
        sample = {**valid, 'packet': {'sample': [1]}, 'checksum': 'fixture'}
        raw = core.canon(sample)
        cases = (
            ('duplicate checksum', b'"checksum":"fixture"', b'"checksum":"first","checksum":"fixture"',
             ('duplicate JSON key', 'duplicate JSON key')),
            ('duplicate format', b'"format":', b'"format":"fixture","format":',
             ('duplicate JSON key', 'duplicate JSON key')),
            ('decimal number', b'"sample":[1]', b'"sample":[1.0]',
             ('fractional numbers must be decimal strings', 'noninteger or unsafe JSON number')),
            ('exponent number', b'"sample":[1]', b'"sample":[1e0]',
             ('fractional numbers must be decimal strings', 'noninteger or unsafe JSON number')),
        )
        commands = (
            [sys.executable, str(ROOT / 'src/ucl.py'), 'check'],
            ['node', str(ROOT / 'tools/check_ucl_portable.js')],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wire.txt'
            path.write_bytes(core.canon(valid))
            for command in commands:
                result = subprocess.run([*command, path], capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
            for name, token, replacement, errors in cases:
                self.assertIn(token, raw)
                path.write_bytes(raw.replace(token, replacement, 1))
                for command, error in zip(commands, errors, strict=True):
                    with self.subTest(case=name, checker=command[0]):
                        result = subprocess.run([*command, path], capture_output=True, text=True, timeout=15)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(error, result.stderr)

    def test_shared_json_reader_obeys_canonical_scalar_rules(self):
        reader = ("const fs=require('node:fs');"
                  "const {parseUclJson,canonical}=require('./tools/check_ucl.js');"
                  "try{process.stdout.write(canonical(parseUclJson(fs.readFileSync(0))))}"
                  "catch(error){console.error(error.message);process.exitCode=1}")
        text = '{"\ue000":1,"\U00010000":"x","a":[true,null,-0]}'
        for raw in (json.dumps(json.loads(text)).encode(), text.encode()):
            result = subprocess.run(['node', '-e', reader], cwd=ROOT, input=raw,
                                    capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, core.canon(core.parse_json(raw)))
        for raw in (b'{"key":1,"\\u006bey":2}', b'[1.0]', b'[1e2]', b'[9007199254740992]',
                    b'"\xff"', b'"\\ud800"'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    core.canon(core.parse_json(raw))
                result = subprocess.run(['node', '-e', reader], cwd=ROOT, input=raw,
                                        capture_output=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)

if __name__=='__main__':unittest.main()
