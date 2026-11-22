"""No-cost tests for truly model-authored UCL semantic data and strict full packet challenge."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_author as n
import ucl

class TestNativeAuthor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=ucl.load_json(n.BASELINE.read_text())

    def test_four_independent_challenges_and_two_directions(self):
        self.assertEqual(n.FORMATS,('english','structured_english','ucl_native'))
        self.assertEqual(len(n.CASES),4)
        self.assertEqual(len(n.layout(4,2,True)),26)  # 24 sender/receiver pairs + 2 strict
        self.assertEqual(len(n.layout(2,1,False)),6)
        for i in range(4):
            for d in (0,1):
                case,sender,receiver=n.fixture(i,d)
                self.assertNotEqual(sender,receiver)
                self.assertIn('P AND B',n.task_text(case))
        for kwargs in ({'cases':3},{'directions':3}):
            with self.assertRaises(ValueError):n.layout(**kwargs)

    def test_prompts_constrain_ambiguous_enums_and_native_references(self):
        case,sender,_=n.fixture(1,0)
        st=n.sender_messages('structured_english',case,sender,self.base)[-1]['content']
        self.assertIn('INTEGER 1 for B',st)
        self.assertIn('hypothetical-example',st)
        native=n.sender_messages('ucl_native',case,sender,self.base)[-1]['content']
        self.assertIn('{"claim":"theory","path":[1]}',native)
        self.assertIn('~[B][A]',native)
        self.assertEqual(n.MAX_OUTPUT,16384)

    def test_dry_run_all_formats_and_strict_no_cost(self):
        r=n.run(dry_run=True,cap=.001,cases=4,directions=2,strict=True)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['completed_tasks'],26)
        self.assertEqual(r['estimated_cost_usd'],0)
        for fmt in n.FORMATS:
            self.assertEqual(r['by_format'][fmt]['tasks'],8)
            self.assertEqual(r['by_format'][fmt]['end_to_end_success'],8)
            self.assertEqual(r['by_format'][fmt]['receivers_correct'],8)
        self.assertEqual(r['by_format']['ucl_strict_full']['end_to_end_success'],2)

    def test_no_semantic_repairs_and_no_english_to_ucl_conversion(self):
        case,sender,_=n.fixture(0,0)
        obj=n.contrib_template(sender)
        obj['act']['text']='I reject P. The signal is a conceptual hint, not a measured reading.'
        obj['act']['expressions']=['~[P][A]']
        obj['explanation']='~[P][A]'
        obj['conclusion']='~[P][A]'
        obj['acknowledgements'][0]['target']['path']=[0]
        obj['acknowledgements'][0]['action']='reject'
        obj['acknowledgements'][0]['note']=obj['act']['text']
        wire,p,meta=n.normalise_sender('ucl_native',json.dumps(obj),self.base,sender)
        self.assertTrue(meta['author_valid'])
        ucl.check(p)
        self.assertEqual(p['discourse']['acts'][-1]['text'],obj['act']['text'])
        self.assertEqual(p['acknowledgements'][-1]['action'],'reject')
        self.assertEqual(p['acknowledgements'][-1]['target']['path'],[0])
        self.assertIn('ucl',wire.lower())
        obj['explanation']='![~[P][A]]'
        obj['conclusion']='![~[P][A]]'
        obj['act']['expressions']=['![~[P][A]]']
        _,negated_packet,negmeta=n.normalise_sender('ucl_native',json.dumps(obj),self.base,sender)
        self.assertTrue(negmeta['formula_differs_from_positive_atom'])
        self.assertEqual(negated_packet['discourse']['acts'][-1]['expressions'],['![~[P][A]]'])
        self.assertEqual(negated_packet['acknowledgements'][-1]['target']['path'],[0])
        obj['acknowledgements'][0]['action']='made-up-action'
        with self.assertRaises(ValueError):
            n.normalise_sender('ucl_native',json.dumps(obj),self.base,sender)

    def test_failure_types_reported_without_claiming_semantic_errors(self):
        self.assertEqual(n.classify_failure('', 'length', ValueError('bad')),
                         'output_token_exhaustion')
        self.assertEqual(n.classify_failure('{', 'stop',
                         json.JSONDecodeError('incomplete','{',0)), 'invalid_json')
        self.assertEqual(n.classify_failure('{}', 'stop',
                         n.NativeValidationError('invalid UCL')),
                         'ucl_validator_rejection')
        self.assertEqual(n.classify_failure('{}', 'stop',ValueError('shape')),
                         'author_schema_rejection')

    def test_strict_grade_rejects_forged_integrity_and_missing_history(self):
        case,sender,_=n.fixture(0,0)
        self.assertFalse(n.strict_grade('{}',case,self.base,sender)['valid'])
        p=dict(self.base)
        p['integrity']={'sha256':'forged'}
        self.assertFalse(n.strict_grade(json.dumps(p),case,self.base,sender)['valid'])

    def test_scoring_detects_wrong_meaning_separately_from_format(self):
        case=n.CASES[1]
        ans={k:case[k] for k in n.FIELDS}
        self.assertTrue(n.judge_receiver(json.dumps(ans),case)['correct'])
        ans['evidence']='none'
        scored=n.judge_receiver(json.dumps(ans),case)
        self.assertTrue(scored['valid'])
        self.assertFalse(scored['correct'])
        self.assertTrue(scored['facets']['path'])
        self.assertFalse(scored['facets']['evidence'])
        self.assertFalse(n.judge_receiver('invalid',case)['valid'])

    def test_pre_call_budget_prevents_any_expense(self):
        class Never:
            def create(self,**kwargs):raise AssertionError('unexpected API usage')
        api=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=Never().create)))
        result=n.run(api,cap=.00001,cases=2,directions=1,strict=False)
        self.assertEqual(result['status'],'budget_stop')
        self.assertEqual(result['completed_tasks'],0)

    def test_no_repair_of_invalid_sender_output(self):
        class Fake:
            def __init__(self):self.n=0
            def create(self,**kwargs):
                self.n+=1
                # Deliberately malformed sender outputs. No second model invocation
                # is made for an invalid handoff; do not autocorrect.
                return SimpleNamespace(choices=[SimpleNamespace(
                    message=SimpleNamespace(content='{}'),finish_reason='stop')],
                    usage=SimpleNamespace(prompt_tokens=90,completion_tokens=45))
        fake=Fake()
        api=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake.create)))
        result=n.run(api,cap=10,cases=2,directions=1,strict=False)
        self.assertEqual(result['status'],'complete')
        self.assertEqual(result['completed_tasks'],6)
        self.assertEqual(fake.n,6)
        self.assertTrue(all(x['author_valid'] is False for x in result['cases']))

if __name__=='__main__':unittest.main()
