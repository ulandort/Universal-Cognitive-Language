"""Free regression tests for optional, immutable, indexed FR-1 UCL roles."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'benchmarks'),str(ROOT/'tools'),str(ROOT/'src')]
import formula_roles_experiment as e
import sap_portable as p
import native_author as n
import ucl

class TestFormulaRoles(unittest.TestCase):
    def test_paired_same_packet_and_bounded_overhead(self):
        for i in range(len(e.FIXTURES)):
            f=e.fixture(i)
            a,b=f['without'],f['with']
            self.assertEqual(p.decode(a),p.decode(b))
            self.assertNotIn('formula_roles',a)
            self.assertEqual([x['role'] for x in b['formula_roles']],f['gold_roles'])
            self.assertEqual(len(b['formula_roles']),2)
            self.assertLess(len(ucl.canon(b))-len(ucl.canon(a)),180)
            self.assertNotEqual(a['checksum'],b['checksum'])
            self.assertEqual(a['packet']['integrity'],b['packet']['integrity'])
    def test_invalid_indices_duplicates_operators_rejected(self):
        f=e.fixture(0);old=f['with']
        for broken in (
            [{'act':'t9','index':'0','role':'hypothesis'}],
            [{'act':'t9','index':True,'role':'hypothesis'}],
            [{'act':'t9','index':-1,'role':'hypothesis'}],
            [{'act':'t9','index':999,'role':'hypothesis'}],
            [{'act':'unknown','index':0,'role':'hypothesis'}],
            [{'act':'t9','index':0,'role':'new-glyph'}],
            [{'act':'t9','index':0,'role':'hypothesis'}]*2
        ):
            with self.assertRaises(ValueError):
                p.encode(f['with']['packet'],formula_roles=broken)
        bad=copy.deepcopy(old)
        bad['formula_roles'][0]['role']='quotation'
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):
            p.decode(bad)
        bad['checksum']=p.envelope_checksum(bad)
        self.assertEqual(p.decode(bad),f['without']['packet'])
        # The checker verifies role shape and integrity, not intent truth.
        self.assertEqual(f['with']['packet']['integrity'],bad['packet']['integrity'])
    def test_dry_run_is_non_paid_and_both_arms_scored(self):
        out=e.run(dry_run=True,cap=.001)
        self.assertEqual(out['status'],'dry_run')
        self.assertEqual(out['estimated_cost_usd'],0)
        self.assertEqual(out['by_arm']['plain']['attempted'],10)
        self.assertEqual(out['by_arm']['annotated']['attempted'],10)
        self.assertEqual(out['by_arm']['plain']['exact_roles'],10)
        self.assertEqual(out['by_arm']['annotated']['exact_roles'],10)
        self.assertTrue(all(row['added_bytes']<180 for row in out['rows']))
    def test_budget_prevents_any_paid_requests(self):
        r=e.run(client=None,dry_run=False,cap=.000001)
        self.assertEqual(r['status'],'budget_stop')
        self.assertEqual(r['rows'],[])
    def test_role_does_not_assert_truth(self):
        env=e.fixture(2)['with']
        self.assertIn('counterexample',[x['role'] for x in env['formula_roles']])
        self.assertIn('quotation',[x['role'] for x in env['formula_roles']])
        self.assertIn('novelty',env['structural_rules']['rules']['semantic_verification'])
        self.assertNotIn('truth',env['formula_roles'][0])

if __name__=='__main__':unittest.main()
