"""Verify installable Agent Skills metadata and documented UCL/2.0 CLI paths.

This check is standard-library only; it does not install npx, fetch dependencies,
or invoke any hosted interpreter.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/ucl-portable/SKILL.md'
WORKFLOWS=ROOT/'skills/ucl-portable/references/WORKFLOWS.md'

class UCLAgentSkillTests(unittest.TestCase):
    def test_open_agent_skills_frontmatter(self):
        body=SKILL.read_text(encoding='utf-8')
        self.assertTrue(body.startswith('---\n'))
        head,sep,prose=body[4:].partition('\n---\n')
        self.assertTrue(sep,'frontmatter closing separator required')
        keys={}
        for ln in head.splitlines():
            k,colon,v=ln.partition(':')
            self.assertEqual(colon,':','YAML metadata must be simple key:value')
            self.assertNotIn(k,keys)
            keys[k]=v.strip()
        self.assertEqual(keys['name'],'ucl-portable')
        self.assertGreater(len(keys['description']),40)
        self.assertLessEqual(len(keys['description']),1024)
        self.assertEqual(keys['license'],'Apache-2.0')
        self.assertTrue(set(keys).issubset({
            'name','description','license','compatibility','allowed-tools','metadata'}))
        self.assertIn('UCL/2.4-SAP1-PORTABLE',prose)
        self.assertIn('references/WORKFLOWS.md',prose)
        self.assertLess(len(body.splitlines()),500)
    def test_self_contained_skill_paths_and_installation(self):
        s=SKILL.read_text(encoding='utf-8')
        w=WORKFLOWS.read_text(encoding='utf-8')
        self.assertTrue(WORKFLOWS.is_file())
        self.assertIn('npx skills add ulandort/Universal-Cognitive-Language --skill ucl-portable',w)
        for p in ('src/ucl.py','src/core.py','src/portable.py','tools/author.py',
                  'docs/UCL_2_0_SPECIFICATION.md'):
            self.assertTrue((ROOT/p).is_file(),p)
        self.assertIn('src/ucl.py check',w)
        self.assertIn('src/ucl.py encode',w)
        self.assertIn('src/ucl.py decode',w)
        self.assertIn('tools/author.py',w)
        self.assertIn('not the protocol implementation',s)
        self.assertIn('not cryptographic proof',w)
        self.assertIn('Never assume skill installation automatically installs',w)
    def test_agent_skill_example_is_verified_locally(self):
        # Run the documented offline conversion and check, without a hosted AI.
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            packet=Path(t)/'example.txt'
            reference=ROOT/'examples/cross_model_conversation_8_turns.json'
            cmds=[
               [sys.executable,str(ROOT/'src/ucl.py'),'encode',str(reference),str(packet)],
               [sys.executable,str(ROOT/'src/ucl.py'),'check',str(packet)]
            ]
            for cmd in cmds:
                p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
                self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('VALID UCL/2.0 Portable',p.stdout)

if __name__=='__main__':
    unittest.main()
