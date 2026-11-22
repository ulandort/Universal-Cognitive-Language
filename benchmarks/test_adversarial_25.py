"""Purely offline tests for scripted adversarial 25-event benchmark."""
import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
import adversarial_25 as b
import ucl


class TestAdversarial25(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.states=b.build_packets()

    def test_exact_25_new_turns_no_omissions(self):
        self.assertEqual(len(b.ADDITIONAL),15)
        self.assertEqual(len(b.pilot.EVENTS)+len(b.ADDITIONAL),25)
        self.assertEqual(len(self.states[25]['discourse']['acts']),33)
        self.assertEqual(self.states[25]['history']['status'],'fully-expanded')
        self.assertEqual(self.states[25]['history']['omissions'],[])
        self.assertEqual(self.states[25]['discourse']['current'],'t33')
        self.assertEqual(self.states[10]['discourse']['current'],'t18')
        for p in self.states.values():ucl.check(p)

    def test_immutable_definitions(self):
        original=self.states[10]['definitions']
        latest=self.states[25]['definitions']
        for glyph in ('P','B','C'):
            self.assertEqual(original[glyph],latest[glyph])
        self.assertEqual(len({latest[g]['id'] for g in ('P','B','C','E','F')}),5)
        self.assertNotIn('E',original)
        self.assertNotIn('F',original)

    def test_precise_acknowledgement_attributions(self):
        p=self.states[25]
        ack_by={a['by']:a for a in p['acknowledgements']}
        self.assertEqual(ack_by['t23']['target'],{'act':'t11','expression_index':0})
        self.assertEqual(ack_by['t24']['target'],{'claim':'theory','path':[0]})
        self.assertEqual(ack_by['t30']['target'],{'act':'t20','expression_index':0})
        self.assertEqual(ack_by['t31']['target'],{'claim':'theory','path':[1]})
        self.assertEqual(ack_by['t33']['action'],'adopt-for-discussion')

    def test_roundtrip_profiles_and_history_equivalence(self):
        for checkpoint,p in self.states.items():
            for fmt in b.FORMATS:
                wire=b.format_record(fmt,p)
                self.assertGreater(len(wire),0)
                msgs=b.request_messages(fmt,p,checkpoint)
                self.assertEqual(msgs[-1]['role'],'user')
                if fmt.startswith('ucl_'):
                    dec=b.guide_profiles.decode(json.loads(wire),p['guide'] if fmt=='ucl_compact' else None)
                    self.assertEqual(ucl.canon(dec),ucl.canon(p))
                elif fmt=='english':
                    self.assertIn('Original P',wire)
                    if checkpoint==25:self.assertIn('Definition E',wire)
                elif fmt=='structured_english':
                    self.assertIn('acknowledgements',wire)

    def test_scoring_rejects_bad_formats(self):
        for checkpoint,questions in b.QUESTIONS.items():
            correct={'answers':{k:v[2] for k,v in questions.items()}}
            self.assertTrue(all(b.score(json.dumps(correct),checkpoint).values()))
            self.assertIsNone(b.score('{}',checkpoint))
            self.assertIsNone(b.score('Here are the answers...',checkpoint))
            self.assertIsNone(b.score(json.dumps({'answers':{'wrong':'a'}}),checkpoint))
            incorrect=copy.deepcopy(correct)
            key=next(iter(questions))
            incorrect['answers'][key]='d' if questions[key][2]!='d' else 'a'
            self.assertFalse(b.score(json.dumps(incorrect),checkpoint)[key])

    def test_balanced_checkpoints_models_formats(self):
        r=b.run(dry_run=True,cap=.01)
        self.assertEqual(r['status'],'dry_run')
        self.assertEqual(r['completed'],16)
        self.assertEqual(r['questions_total'],112)
        self.assertEqual(r['questions_correct'],112)
        self.assertEqual(r['estimated_cost_usd'],0)
        keys={(v['checkpoint'],v['model'],v['format']) for v in r['cases']}
        self.assertEqual(len(keys),16)
        self.assertEqual({k[0] for k in keys},{10,25})
        self.assertEqual({k[1] for k in keys},set(b.MODELS))

    def test_mock_api_and_wrong_response_tracking(self):
        class FakeAPI:
            def __init__(self):self.i=0
            def create(self,**kw):
                # Emulate a model that always produces a valid JSON but takes
                # first listed option; no expected-answer leakage into messages.
                keys=b.QUESTIONS[(10 if self.i<8 else 25)]
                self.i+=1
                msg=json.dumps({'answers':{k:'a' for k in keys}})
                return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=msg),finish_reason='stop')],
                                       usage=SimpleNamespace(prompt_tokens=100,completion_tokens=50))
        fake=FakeAPI()
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake.create)))
        result=b.run(client=client,cap=2,dry_run=False)
        self.assertEqual(result['completed'],16)
        self.assertEqual(result['status'],'complete')
        self.assertLess(result['questions_correct'],112)
        self.assertGreater(result['estimated_cost_usd'],0)

    def test_cap_and_guards(self):
        for cap in (0,-1,2.01):
            with self.assertRaises(ValueError):b.run(cap=cap,dry_run=True)
        self.assertGreater(b.reserve_upper_bound('hal-1.0',b.request_messages('ucl_portable',self.states[25],25),b.MAX_OUTPUT),0)


if __name__=='__main__':unittest.main()