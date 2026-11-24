"""UCL/2.0 public-source-layout regression; no wire/semantic migration."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import ucl,core,portable
class SourceLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=core.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text(encoding='utf8'))
    def test_public_version_and_original_grammar(self):
        self.assertEqual(ucl.VERSION,'UCL/2.0')
        self.assertEqual(ucl.PORTABLE_FORMAT,portable.FORMAT)
        self.assertEqual(ucl.INNER_GRAMMAR_VERSION,'UCL/1.0')
        self.assertEqual(ucl.CORE,core.CORE)
        self.assertEqual(ucl.check(self.packet),core.check(self.packet))
        self.assertEqual(ucl.packet_id(self.packet),core.packet_id(self.packet))
    def test_exact_portable_bytes_and_checksum_not_modified_by_reorganization(self):
        sys.path.insert(0,str(ROOT/'tools'))
        import sap_portable as legacy_entry
        old=legacy_entry.encode(self.packet)
        new=portable.encode(self.packet)
        self.assertEqual(old,new)
        self.assertEqual(ucl.canon(old),core.canon(new))
        self.assertEqual(ucl.decode_portable(old),self.packet)
        self.assertEqual(ucl.check_portable(new)['status'],'VALID UCL/2.0 Portable')
        self.assertEqual(new['format'],'UCL/2.0-SAP1-PORTABLE')
    def test_legacy_tool_cli_and_new_cli_produce_exact_same_wire(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'src.txt',Path(d)/'tool.txt'
            p=ROOT/'examples/cross_model_conversation_8_turns.json'
            for command,out in [(ROOT/'src/ucl.py',a),(ROOT/'tools/sap_portable.py',b)]:
                proc=subprocess.run([sys.executable,str(command),'encode',str(p),str(out)],
                                    text=True,capture_output=True,timeout=20)
                self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            q=subprocess.run([sys.executable,str(ROOT/'src/ucl.py'),'check',str(a)],
                             text=True,capture_output=True,timeout=20)
            self.assertEqual(q.returncode,0,q.stderr)
            self.assertIn('VALID UCL/2.0 Portable',q.stdout)
            legacy=subprocess.run([sys.executable,str(ROOT/'src/ucl.py'),'check',str(p)],
                                  text=True,capture_output=True,timeout=20)
            self.assertEqual(legacy.returncode,0,legacy.stderr)
            self.assertIn('VALID UCL/1.0',legacy.stdout)
            restore=Path(d)/'restored.json'
            dec=subprocess.run([sys.executable,str(ROOT/'src/ucl.py'),'decode',str(a),str(restore)],
                               text=True,capture_output=True,timeout=20)
            self.assertEqual(dec.returncode,0,dec.stderr)
            self.assertEqual(core.load_json(restore.read_text()),self.packet)
    def test_exact_authoring_schema_shared_by_core_and_tool_import(self):
        import structural_authoring as canonical
        sys.path.insert(0,str(ROOT/'benchmarks'))
        # Benchmark compatibility import by file location to avoid module cache masking.
        import importlib.util
        loc=ROOT/'benchmarks/structural_authoring.py'
        spec=importlib.util.spec_from_file_location('old_bench_sap',loc)
        old=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        self.assertEqual(canonical.ACTIONS,old.ACTIONS)
        self.assertEqual(canonical.CONTRIBUTION_FIELDS,old.CONTRIBUTION_FIELDS)
        self.assertEqual(canonical.PROFILE,old.PROFILE)
    def test_malformed_portable_still_rejected_without_rewriting(self):
        wire=portable.encode(self.packet)
        wire['packet']['integrity']['sha256']='modified'
        with self.assertRaises(ValueError):ucl.decode_portable(wire)

    def test_continue_cli_preserves_history_and_rejects_rewritten_claims(self):
        contribution = json.loads((ROOT / 'examples/contribution_example.json').read_text(encoding='utf-8'))
        roles = [{'act': 't1', 'index': 0, 'role': 'hypothesis'}]
        wire = portable.encode(self.packet, formula_roles=roles)
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / 'incoming.txt'
            outgoing = Path(directory) / 'outgoing.txt'
            incoming.write_bytes(core.canon(wire))
            command = [sys.executable, str(ROOT / 'src/ucl.py'), 'continue', str(incoming), str(outgoing)]
            invalid = dict(contribution, claims={'theory': self.packet['claims']['theory']})
            rejected = subprocess.run(command, input=json.dumps(invalid), text=True, capture_output=True, timeout=20)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('cannot replace existing bindings: theory', rejected.stderr)
            self.assertFalse(outgoing.exists())

            accepted = subprocess.run(command, input=json.dumps(contribution), text=True, capture_output=True, timeout=20)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            result = json.loads(outgoing.read_bytes())
            packet = portable.decode(result)
            self.assertEqual(result['formula_roles'], roles)
            self.assertEqual(packet['discourse']['acts'], self.packet['discourse']['acts'] + [contribution['act']])
            self.assertEqual(packet['claims'], self.packet['claims'])
            self.assertEqual(packet['definitions'], self.packet['definitions'])
            self.assertEqual(incoming.read_bytes(), core.canon(wire))

if __name__=='__main__':unittest.main()
