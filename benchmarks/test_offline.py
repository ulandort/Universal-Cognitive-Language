"""Built-in regression checks for UCLBench."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'benchmarks'),str(ROOT/'tools'),str(ROOT/'src')]
import ucl
import guide_profiles
import offline_suite
import lrc_experimental as lrc

class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=ucl.load_json((ROOT/'examples/cross_model_conversation_13_turns.json').read_text())
    def test_portable_roundtrip(self):
        q=guide_profiles.decode(guide_profiles.encode(self.p,'portable'))
        self.assertEqual(ucl.canon(q),ucl.canon(self.p))
    def test_compact_roundtrip(self):
        q=guide_profiles.decode(guide_profiles.encode(self.p,'compact'),self.p['guide'])
        self.assertEqual(ucl.canon(q),ucl.canon(self.p))
    def test_compact_without_guide_fails(self):
        with self.assertRaises(ValueError):guide_profiles.decode(guide_profiles.encode(self.p,'compact'))
    def test_deterministic_benchmark(self):
        a=offline_suite.execute(13,30);b=offline_suite.execute(13,30)
        self.assertEqual(a,b);self.assertEqual(a['failed'],0)
    def test_lrc_identity_fallback(self):
        result=lrc.encode_if_smaller(self.p,'portable')
        self.assertEqual(ucl.canon(lrc.decode_if_needed(result)), ucl.canon(self.p))
        self.assertFalse(lrc.is_envelope(result))
    def test_lrc_repetition_and_tamper(self):
        payload={'repeated':['a distinct and quite long fictional explanation for repeated testing']*12}
        wire=lrc.encode_if_smaller(payload, 'portable')
        self.assertTrue(lrc.is_envelope(wire))
        self.assertEqual(lrc.decode(wire),payload)
        altered=__import__('copy').deepcopy(wire)
        key=next(iter(altered['refs']))
        altered['refs'][key]['value']='changed'
        with self.assertRaises(ValueError):lrc.decode(altered)
    def test_existing_release_conformance(self):
        self.assertEqual(ucl.check(self.p)['status'],'VALID UCL/1.0')
if __name__=='__main__':unittest.main()