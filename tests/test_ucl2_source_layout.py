"""UCL/2.0 public-source-layout regression; no wire/semantic migration."""
import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import ucl,core,portable
class SourceLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=core.load_json((ROOT/'examples/cross_model_conversation_8_turns.json').read_text(encoding='utf8'))
    def test_public_version_and_original_grammar(self):
        self.assertEqual(ucl.VERSION,'UCL/2.4')
        self.assertEqual(ucl.PORTABLE_FORMAT,portable.CURRENT_FORMAT)
        self.assertEqual(ucl.INNER_GRAMMAR_VERSION,'UCL/1.4')
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

    def test_challenge_templates_preflight_and_state_diff(self):
        challenge = ROOT / 'examples/challenge.txt'
        fixture = json.loads((ROOT / 'examples/challenge_reply.json').read_text())
        cli = [sys.executable, str(ROOT / 'src/ucl.py')]

        def run(*args, draft=None, check=True):
            return subprocess.run([*cli, *map(str, args)], input=json.dumps(draft) if draft else None,
                                  text=True, capture_output=True, check=check, timeout=20)

        args = ('template', challenge, '--speaker', 'New participant', '--claim', 'theory', '--path', '1')
        stance = json.loads(run(*args).stdout)
        self.assertNotIn('new_definitions', stance)
        self.assertEqual(stance['acknowledgements'][0]['target'], {'claim': 'theory', 'path': [1]})
        self.assertEqual(stance['act']['references'], ['t8', 't1'])
        self.assertEqual(stance['explanation'], '')
        seeded = json.loads(run(*args, '--seed-formula').stdout)
        self.assertEqual((seeded['explanation'], seeded['conclusion']), ('~[B][A]', '~[B][A]'))
        self.assertEqual(seeded['act']['text'], '')
        self.assertEqual(seeded['acknowledgements'][0]['action'], 'received')
        concept = json.loads(run(*args, '--concept', '$control_sensitive', '--domain', 'D').stdout)
        self.assertEqual(concept['new_definitions']['$control_sensitive']['args'], ['D'])
        self.assertNotIn('declaration', concept)
        self.assertIn('PREFLIGHT PASSED', run('preflight', challenge, draft=fixture).stdout)

        for invalid, message in (
            ({**fixture, 'declaration': ''}, 'generates the declaration layer'),
            ({**fixture, 'new_definitions': {'$control_sensitive': {'definition': {}}}}, 'bare objects'),
            ({**fixture, 'acknowledgements': [{**fixture['acknowledgements'][0],
                'target': {'claim': 'theory', 'path': ['1']}}]}, 'subclaim path invalid'),
            ({**fixture, 'acknowledgements': [{**fixture['acknowledgements'][0],
                'qualification': {'expression': '~[B][A]'}}]}, 'invalid acknowledgement qualification'),
        ):
            with self.subTest(message=message):
                rejected = run('preflight', challenge, draft=invalid, check=False)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn(message, rejected.stderr)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'next.txt'
            run('continue', challenge, output, draft=fixture)
            state = json.loads(run('inspect', output, '--state').stdout)
            self.assertTrue(state['whole_packet_audited'])
            self.assertEqual(state['current_act'], 't9')
            self.assertEqual(state['latest_stances'][-1]['source_act'], 't1')
            delta_text = run('diff', challenge, output).stdout
            self.assertEqual(delta_text, run('diff', challenge, output).stdout)
            delta = json.loads(delta_text)
            self.assertEqual(delta['new_act_count'], 1)
            self.assertEqual(list(delta['new_definitions']), ['$control_sensitive'])
            self.assertEqual(delta['stance_changes'][0]['after']['action'], 'qualify')
            self.assertEqual(delta['stance_changes'][0]['after']['path'], [1])
            brief_text = run('inspect', output, '--handoff', '--claim', 'theory', '--path', '1',
                             '--include-act', 't2').stdout
            brief = json.loads(brief_text)
            self.assertEqual(brief['claim']['scope']['path'], [1])
            self.assertEqual(brief['claim']['source_act']['id'], 't1')
            self.assertEqual(brief['requested_acts'][0]['act']['id'], 't2')
            self.assertEqual(brief['current_act']['id'], 't9')
            self.assertIn('$control_sensitive', brief['definitions'])
            self.assertTrue(brief['whole_packet_audited'])
            compact_text = run('diff', challenge, output, '--compact').stdout
            compact = json.loads(compact_text)
            self.assertLess(len(compact_text), len(delta_text))
            self.assertEqual(compact['counts']['stance_changes'], 1)
            self.assertEqual(compact['new_acts'][0]['id'], 't9')
            self.assertEqual(compact['new_definitions'][0]['id'], delta['new_definitions']['$control_sensitive']['id'])
            self.assertEqual(compact['stance_changes'][0]['after']['action'], 'qualify')
            rejected = run('diff', output, challenge, check=False)
            self.assertIn('same retained conversation', rejected.stderr)

    def test_template_seeds_only_standalone_propositions(self):
        from authoring import reply_template

        packet = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/challenge.txt'))
        binding = packet['claims']['theory']
        binding['expression'] = '{[#0][D][~[B][#0]]'
        with self.assertRaisesRegex(ValueError, 'Choose an enclosing claim path'):
            reply_template(packet, 'New participant', 'theory', [2], seed_formula=True)
        draft = reply_template(packet, 'New participant', 'theory', [], seed_formula=True)
        self.assertEqual(draft['explanation'], binding['expression'])
        binding['expression'] = '?[~[B][A]]'
        with self.assertRaisesRegex(ValueError, 'requires a proposition'):
            reply_template(packet, 'New participant', 'theory', [], seed_formula=True)

    def test_exact_ack_retraction_and_cross_version_diff(self):
        from authoring import reply_template
        from inspection import compare_packets, current_state, focused_context

        old = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/challenge.txt'))
        upgraded = core.upgrade_packet(old)
        self.assertEqual(upgraded['definitions'], old['definitions'])
        current = ucl.encode_portable(upgraded)
        with self.assertRaisesRegex(ValueError, 'requires Portable 2.3'):
            reply_template(old, 'D', None, [], retract='x4')
        draft = reply_template(upgraded, 'D', None, [], retract='x4')
        draft['act']['text'] = 'I retract the stance recorded in x4.'
        draft.update(explanation='~[B][A]', conclusion='~[B][A]')
        next_wire = ucl.continue_portable(current, draft)
        after = ucl.decode_portable(next_wire)
        delta = compare_packets(old, after)
        self.assertEqual(after['acknowledgements'][:-1], old['acknowledgements'])
        self.assertEqual(delta['new_retractions'][0]['retracts'], 'x4')
        self.assertEqual(delta['stance_changes'][0]['before']['acknowledgement'], 'x4')
        self.assertEqual(delta['stance_changes'][0]['after']['path'], [1])
        stances = current_state(after)['latest_stances']
        self.assertTrue(any(a['acknowledgement'] == 'x3' for a in stances))
        self.assertEqual(stances[-1]['action'], 'retract')
        self.assertEqual(stances[-1]['status'], 'retracted')
        excerpt = focused_context(after, claim_id='theory', path=[1])
        self.assertEqual(excerpt['acknowledgements'][-1]['original_ack_act'], 't8')

        newer_draft = copy.deepcopy(draft)
        newer = newer_draft['acknowledgements'][0]
        newer.update(action='accept', target={'claim': 'theory', 'path': [1]})
        accepted = ucl.continue_portable(current, newer_draft)
        older_retraction = copy.deepcopy(draft)
        older_retraction['act'].update(id='t10')
        older_retraction['acknowledgements'][0].update(id='x6', by='t10')
        behind = ucl.decode_portable(ucl.continue_portable(accepted, older_retraction))
        delta = compare_packets(ucl.decode_portable(accepted), behind)
        self.assertFalse(delta['new_retractions'][0]['cleared_current_stance'])
        self.assertEqual(delta['stance_changes'], [])
        surviving = current_state(behind)['latest_stances'][-1]
        self.assertEqual((surviving['status'], surviving['acknowledgement']), ('current', 'x5'))
        newest_retraction = copy.deepcopy(older_retraction)
        newest_retraction['acknowledgements'][0]['target']['ack'] = 'x5'
        cleared = ucl.decode_portable(ucl.continue_portable(accepted, newest_retraction))
        cleared_stance = current_state(cleared)['latest_stances'][-1]
        self.assertEqual(cleared_stance['action'], 'retract')
        self.assertEqual(cleared_stance['retracts'], 'x5')
        with self.assertRaisesRegex(ValueError, 'already retracted'):
            ucl.continue_portable(next_wire, older_retraction)

        bad = copy.deepcopy(draft)
        bad['act']['speaker'] = 'A'
        for label, wire in [('Python', current), ('previous version', ucl.encode_portable(old))]:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, 'another speaker|requires Portable 2.3'):
                    ucl.continue_portable(wire, bad)
        bad['act']['speaker'] = 'D'
        bad['acknowledgements'][0]['target']['ack'] = 'x5'
        with self.assertRaisesRegex(ValueError, 'existing stance ACK'):
            ucl.continue_portable(current, bad)
        bad['acknowledgements'][0]['target']['ack'] = 'x4'
        bad['acknowledgements'][0]['qualification'] = 'invalid for a retraction'
        with self.assertRaisesRegex(ValueError, 'null qualification and replacement'):
            ucl.continue_portable(current, bad)

        if shutil.which('node'):
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'portable.txt'
                js = ['node', str(ROOT / 'tools/check_ucl_portable.js'), str(path)]
                path.write_bytes(core.canon(next_wire))
                subprocess.run(js, check=True, capture_output=True, timeout=20)
                altered = copy.deepcopy(next_wire)
                altered_packet = altered['packet']
                altered_packet['discourse']['acts'][-1]['speaker'] = 'A'
                altered_packet['integrity']['sha256'] = core.packet_id(altered_packet)
                altered['checksum'] = portable.envelope_checksum(altered)
                path.write_bytes(core.canon(altered))
                rejected = subprocess.run(js, text=True, capture_output=True, timeout=20)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn('retraction ownership', rejected.stderr)

    def test_retract_and_take_a_new_stance_in_one_act(self):
        from inspection import compare_packets, current_state

        previous = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/challenge.txt'))
        previous = core.upgrade_packet(previous)
        draft = ucl.read_json_file(ROOT / 'examples/challenge_retraction.json')
        draft['act']['text'] = 'I retract x4 and withhold judgment on branch [1].'
        draft['acknowledgements'].append({
            'id': 'x6', 'by': 't9', 'target': {'claim': 'theory', 'path': [1]},
            'action': 'withhold-judgment', 'qualification': None, 'replacement': None, 'note': '',
        })
        packet = ucl.decode_portable(ucl.continue_portable(ucl.encode_portable(previous), draft))
        self.assertEqual(packet['acknowledgements'][-2:], draft['acknowledgements'])
        state = current_state(packet)
        stance = state['latest_stances'][-1]
        self.assertEqual((stance['status'], stance['acknowledgement']), ('current', 'x6'))
        self.assertEqual(state['recent_retractions'][-1]['retracts'], 'x4')
        delta = compare_packets(previous, packet)
        self.assertEqual(delta['new_retractions'][0]['acknowledgement'], 'x5')
        self.assertEqual(delta['stance_changes'][0]['after']['acknowledgement'], 'x6')

    def test_plain_upgrade_preserves_23_retraction_and_definition_ids(self):
        from inspection import compare_packets

        old = ucl.decode_portable(ucl.read_json_file(ROOT / 'examples/challenge.txt'))
        legacy = core.build(core.draft_from_packet(old), version=core.RETRACTION_VERSION)
        contribution = ucl.read_json_file(ROOT / 'examples/challenge_retraction.json')
        retracted = ucl.decode_portable(ucl.continue_portable(ucl.encode_portable(legacy), contribution))
        upgraded = core.upgrade_packet(retracted)
        self.assertIn('reply_authoring', upgraded['guide'])
        self.assertEqual({k: v for k, v in retracted.items() if k not in {'guide', 'integrity'}},
                         {k: v for k, v in upgraded.items() if k not in {'guide', 'integrity'}})
        self.assertEqual(compare_packets(retracted, upgraded)['new_act_count'], 0)
        self.assertEqual(ucl.encode_portable(upgraded)['format'], ucl.PORTABLE_FORMAT)

    def test_portable_cli_rejects_ambiguous_and_oversized_json(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / 'packet.txt'
            wire = core.canon(portable.encode(self.packet))
            duplicate = wire.replace(b'"profile":"portable"', b'"profile":"portable","profile":"portable"', 1)
            self.assertNotEqual(duplicate, wire)
            for source, error in (
                (duplicate, "duplicate JSON key: 'profile'"),
                (b' ' * (ucl.MAX_PORTABLE_JSON + 1), 'JSON input exceeds'),
            ):
                packet.write_bytes(source)
                for entry in ('src/ucl.py', 'tools/sap_portable.py'):
                    command = [sys.executable, str(ROOT / entry), 'check', str(packet)]
                    result = subprocess.run(command, text=True, capture_output=True, timeout=20)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('REJECTED: ' + error, result.stderr)

            packet.write_bytes(wire)
            output = Path(directory) / 'next.txt'
            command = [sys.executable, str(ROOT / 'src/ucl.py'), 'continue', str(packet), str(output)]
            result = subprocess.run(command, input='{"act":{},"act":{}}', text=True, capture_output=True, timeout=20)
            self.assertIn("REJECTED: draft on stdin: duplicate JSON key: 'act'", result.stderr)
            self.assertFalse(output.exists())

    def test_inspect_challenge_reports_new_definition_and_exact_acknowledgement(self):
        cli = [sys.executable, str(ROOT / 'src/ucl.py')]
        incoming = ROOT / 'examples/challenge.txt'
        draft = (ROOT / 'examples/challenge_reply.json').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            outgoing = Path(directory) / 'next.txt'
            continued = subprocess.run(
                [*cli, 'continue', str(incoming), str(outgoing)],
                input=draft, text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(continued.returncode, 0, continued.stderr)
            inspected = subprocess.run(
                [*cli, 'inspect', str(outgoing)], text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            self.assertIn('9 retained acts | 12 defined symbols', inspected.stdout)
            self.assertIn('$control_sensitive (predicate)', inspected.stdout)
            self.assertIn('first retained act expression: t9', inspected.stdout)
            self.assertIn('theory path [1] (from t1) ~[B][A] | condition: ~[$control_sensitive][A]', inspected.stdout)
            self.assertIn('counterexample for $control_sensitive', inspected.stdout)
            before = portable.decode(json.loads(incoming.read_bytes()))
            after = portable.decode(json.loads(outgoing.read_bytes()))
            self.assertEqual(after['discourse']['acts'][:-1], before['discourse']['acts'])
            self.assertEqual({glyph: after['definitions'][glyph] for glyph in before['definitions']},
                             before['definitions'])
            self.assertLess(inspected.stdout.index('Concept index'), inspected.stdout.index('Recorded open issues'))
            comparison = subprocess.run(
                [*cli, 'inspect', str(outgoing), '--since', str(incoming), '--json'],
                text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(comparison.returncode, 0, comparison.stderr)
            ledger = json.loads(comparison.stdout)
            self.assertEqual(ledger['comparison']['added_symbols'], ['$control_sensitive'])
            symbol = next(item for item in ledger['symbols'] if item['symbol'] == '$control_sensitive')
            self.assertEqual(symbol['recent_expression_acts'], ['t9'])
            unrelated = subprocess.run(
                [*cli, 'inspect', str(outgoing), '--since', str(ROOT / 'examples/quickstart.txt')],
                text=True, capture_output=True, timeout=20,
            )
            self.assertNotEqual(unrelated.returncode, 0)
            self.assertIn('same retained conversation', unrelated.stderr)

    def test_state_ledger_resolves_exact_stances_through_a_long_history(self):
        starter = json.loads((ROOT / 'examples/quickstart.txt').read_bytes())
        draft = core.draft_from_packet(portable.decode(starter))
        acts = draft['discourse']['acts']
        for turn in range(3, 56):
            speaker = 'Ari' if turn == 53 else 'Bea'
            acts.append({
                'id': f't{turn}', 'kind': 'response', 'speaker': speaker,
                'references': ['t1'], 'text': 'Continuing the design discussion.',
                'expressions': ['~[B][A]'],
                'details': {'responds_to': 't1', 'stance': 'undetermined'},
            })
        acts[51].update(kind='question', details={
            'targets': ['When should background sync run?'],
            'answer_kind': 'open', 'alternatives': [],
        })
        draft['discourse']['current'] = 't55'

        def ack(number, turn, action, target, qualification=None):
            return {
                'id': f'x{number}', 'by': f't{turn}', 'action': action, 'target': target,
                'qualification': qualification, 'replacement': None, 'note': '',
            }

        whole_claim = {'claim': 'notes-design', 'path': []}
        sync_branch = {'claim': 'notes-design', 'path': [1]}
        draft['acknowledgements'].extend([
            ack(3, 54, 'withhold-judgment', sync_branch),
            ack(4, 55, 'received', sync_branch),
            ack(5, 4, 'reject', whole_claim),
            ack(6, 3, 'accept', {'act': 't1', 'expression_index': 0}),
            ack(7, 53, 'withdraw', sync_branch),
            ack(8, 54, 'qualify', sync_branch, {'expression': '~[N][A]', 'explanation': ''}),
        ])

        envelope = portable.encode(core.build(draft, version=core.packet_version(starter['packet'])))
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / 'long.txt'
            incoming.write_bytes(core.canon(envelope))
            cli = [sys.executable, str(ROOT / 'src/ucl.py'), 'inspect', str(incoming)]
            result = subprocess.run([*cli, '--json'], text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            ledger = json.loads(result.stdout)
            self.assertEqual(ledger['retained_act_count'], 55)
            self.assertEqual(ledger['packet_sha256'], envelope['packet']['integrity']['sha256'])
            self.assertEqual(ledger['recorded_open_issues'], draft['history']['unresolved'])
            self.assertEqual([question['act'] for question in ledger['questions']], ['t52'])
            by_scope = {(item['speaker'], tuple(item['path'])): item for item in ledger['stances']}
            self.assertEqual(
                {scope: item['acknowledgement'] for scope, item in by_scope.items()},
                {('Bea', (0,)): 'x1', ('Bea', ()): 'x5', ('Ari', (1,)): 'x7', ('Bea', (1,)): 'x8'},
            )
            self.assertEqual(by_scope['Bea', (1,)]['expression'], '~[B][A]')
            self.assertEqual([withdrawal['acknowledgement'] for withdrawal in ledger['withdrawals']], ['x7'])
            self.assertEqual(ledger['recent_acknowledgements'][-1]['action'], 'received')
            rendered = subprocess.run(cli, text=True, capture_output=True, timeout=20)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertLess(rendered.stdout.index('Latest recorded stances'),
                            rendered.stdout.index('Recent acts (5 of 55)'))
            self.assertEqual(incoming.read_bytes(), core.canon(envelope))

    def test_dependency_ids_follow_domains_across_aliases_and_membership_changes(self):
        initial = portable.decode(json.loads((ROOT / 'examples/quickstart.txt').read_bytes()))
        draft = core.draft_from_packet(initial)
        for entry in draft['definitions'].values():
            del entry['id']
        draft['definitions']['F'] = {
            'definition': {'kind': 'function', 'args': ['D'], 'returns': 'D', 'gloss': 'Transforms a notes app.'},
        }
        draft['definitions']['O'] = {
            'definition': {'kind': 'order', 'sort': 'D', 'role': 'edit latency', 'gloss': 'Orders apps by edit latency.'},
        }
        draft['domains']['D'] = {'mode': 'finite', 'members': ['😀', 'notes-app', 'é']}
        original = core.build(copy.deepcopy(draft), version=core.DEPENDENCY_VERSION)
        draft['domains']['D']['members'].reverse()
        reordered = core.build(copy.deepcopy(draft), version=core.DEPENDENCY_VERSION)
        self.assertEqual(original['definitions'], reordered['definitions'])

        draft['definitions']['Y'] = draft['definitions'].pop('D')
        draft['domains']['Y'] = draft['domains'].pop('D')
        draft['definitions']['A']['definition']['sort'] = 'Y'
        draft['definitions']['O']['definition']['sort'] = 'Y'
        draft['definitions']['F']['definition']['returns'] = 'Y'
        for alias in ('B', 'F', 'N', 'P'):
            draft['definitions'][alias]['definition']['args'] = ['Y']
        renamed = core.build(copy.deepcopy(draft), version=core.DEPENDENCY_VERSION)
        self.assertEqual(original['definitions']['D']['id'], renamed['definitions']['Y']['id'])
        for alias in ('A', 'B', 'F', 'N', 'O', 'P'):
            self.assertEqual(original['definitions'][alias]['id'], renamed['definitions'][alias]['id'])

        draft['domains']['Y']['members'].append('another-notes-app')
        expanded = core.build(draft, version=core.DEPENDENCY_VERSION)
        self.assertNotEqual(renamed['definitions']['Y']['id'], expanded['definitions']['Y']['id'])
        for alias in ('A', 'B', 'F', 'N', 'O', 'P'):
            self.assertNotEqual(renamed['definitions'][alias]['id'], expanded['definitions'][alias]['id'])
        self.assertEqual(renamed['definitions']['L']['id'], expanded['definitions']['L']['id'])
        wire = portable.encode(expanded)
        wire['packet']['definitions']['P']['id'] = renamed['definitions']['P']['id']
        wire['packet']['integrity']['sha256'] = core.packet_id(wire['packet'])
        wire['checksum'] = portable.envelope_checksum(wire)
        with self.assertRaisesRegex(ValueError, 'definition SHA-256 mismatch P'):
            portable.decode(wire)

        if shutil.which('node'):
            with tempfile.TemporaryDirectory() as directory:
                packet_file = Path(directory) / 'packet.txt'
                command = ['node', str(ROOT / 'tools/check_ucl_portable.js'), str(packet_file)]
                packet_file.write_bytes(core.canon(portable.encode(reordered)))
                accepted = subprocess.run(command, text=True, capture_output=True, timeout=20)
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                packet_file.write_bytes(core.canon(wire))
                rejected = subprocess.run(command, text=True, capture_output=True, timeout=20)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn('definition hash P', rejected.stderr)

    def test_upgrade_preserves_history_and_formula_roles_and_updates_revision_ids(self):
        sample = ROOT / 'examples/cross_model_conversation_13_turns.json'
        archived = core.load_json(sample.read_text(encoding='utf-8'))
        roles = [{'act': 't1', 'index': 0, 'role': 'hypothesis'}]
        original_wire = portable.encode(archived, formula_roles=roles)
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / 'archived.txt'
            outgoing = Path(directory) / 'upgraded.txt'
            incoming.write_bytes(core.canon(original_wire))
            command = [sys.executable, str(ROOT / 'src/ucl.py'), 'upgrade', str(incoming), str(outgoing)]
            result = subprocess.run(command, text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            revised_wire = json.loads(outgoing.read_bytes())
            self.assertEqual(revised_wire['format'], ucl.PORTABLE_FORMAT)
            self.assertEqual(revised_wire['formula_roles'], roles)
            current = portable.decode(revised_wire)
            for field in ('discourse', 'claims', 'acknowledgements', 'history'):
                self.assertEqual(current[field], archived[field])
            for revision in current['revisions']:
                self.assertEqual(revision['old_id'], current['definitions'][revision['old_glyph']]['id'])
                self.assertEqual(revision['new_id'], current['definitions'][revision['new_glyph']]['id'])
            self.assertNotEqual(current['revisions'], archived['revisions'])
            self.assertEqual(core.upgrade_packet(current), current)
            self.assertEqual(incoming.read_bytes(), core.canon(original_wire))

    def test_cli_build_uses_current_ids_for_fresh_drafts(self):
        archived_draft = core.draft_from_packet(self.packet)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'draft.json'
            output = Path(directory) / 'inner.json'
            command = [sys.executable, str(ROOT / 'src/ucl.py'), 'build', str(source), str(output)]
            source.write_bytes(core.canon(archived_draft))
            archived = subprocess.run(command, text=True, capture_output=True, timeout=20)
            self.assertEqual(archived.returncode, 0, archived.stderr)
            self.assertEqual(core.load_json(output.read_bytes()), self.packet)
            for record in archived_draft['definitions'].values():
                del record['id']
            source.write_bytes(core.canon(archived_draft))
            fresh = subprocess.run(command, text=True, capture_output=True, timeout=20)
            self.assertEqual(fresh.returncode, 0, fresh.stderr)
            current = core.load_json(output.read_bytes())
            self.assertEqual(current, core.upgrade_packet(self.packet))
            crossed = portable.encode(self.packet)
            crossed['packet'] = current
            crossed['checksum'] = portable.envelope_checksum(crossed)
            with self.assertRaisesRegex(ValueError, 'inner guide version does not match'):
                portable.decode(crossed)

    def test_named_aliases_expand_the_catalog_and_coexist_with_a_lone_dollar(self):
        initial = portable.decode(json.loads((ROOT / 'examples/quickstart.txt').read_bytes()))
        draft = core.draft_from_packet(initial)
        definitions = draft['definitions']
        for alias in ('$', '$background_sync', '$background_sync2', '$' + 'a' * 64):
            definitions[alias] = {
                'definition': {'kind': 'predicate', 'args': ['D'], 'gloss': 'Behavior ' + alias},
            }
        while len(definitions) < core.MAX_DEFINITIONS:
            alias = f'$behavior_{len(definitions)}'
            definitions[alias] = {
                'definition': {'kind': 'predicate', 'args': ['D'], 'gloss': 'Behavior ' + alias},
            }
        draft['conclusion'] = '&[~[$][A]][&[~[$background_sync][A]][~[$background_sync2][A]]]'
        packet = core.build(draft, version=core.DEPENDENCY_VERSION)
        self.assertEqual(len(packet['definitions']), 512)
        self.assertIn('$:', packet['body'])
        self.assertIn('$background_sync:', packet['body'])
        self._check_node_portable(portable.encode(packet))
        with self.assertRaisesRegex(ValueError, 'catalog size'):
            core.build(draft)
        draft['definitions']['$overflow'] = definitions['$']
        with self.assertRaisesRegex(ValueError, 'catalog size'):
            core.build(draft, version=core.DEPENDENCY_VERSION)

    def test_retirement_preserves_definitions_and_examples(self):
        starter = json.loads((ROOT / 'examples/challenge.txt').read_bytes())
        contributed = json.loads((ROOT / 'examples/challenge_reply.json').read_bytes())
        prior = portable.decode(ucl.continue_portable(starter, contributed))
        retiring = {
            'act': {
                'id': 't10', 'kind': 'response', 'speaker': 'New participant',
                'references': ['t9'], 'text': 'I will use the new term going forward.',
                'expressions': ['~[$matched_control][A]'],
                'details': {'responds_to': 't9', 'stance': 'mixed'},
                'vocabulary': [
                    {'action': 'retire', 'definition': '$control_sensitive', 'successor': '$matched_control'},
                    {'action': 'example', 'definition': '$matched_control', 'expression_index': 0},
                ],
            },
            'orientation': 'L',
            'explanation': '~[$matched_control][A]',
            'conclusion': '~[$matched_control][A]',
            'new_definitions': {
                '$matched_control': {
                    'kind': 'predicate', 'args': ['D'], 'gloss': 'Shows a result that differs from a matched control.',
                },
            },
        }
        envelope = ucl.continue_portable(portable.encode(prior), retiring)
        result = portable.decode(envelope)
        self.assertEqual(result['definitions']['$control_sensitive'], prior['definitions']['$control_sensitive'])
        self.assertEqual(result['discourse']['acts'][:-1], prior['discourse']['acts'])
        from inspection import derive_ledger
        indexed = derive_ledger(result)['vocabulary']
        self.assertEqual([entry['action'] for entry in indexed], ['counterexample', 'retire', 'example'])
        self.assertEqual(indexed[0]['definition_id'], indexed[1]['definition_id'])
        self.assertEqual(indexed[1]['successor_id'], indexed[2]['definition_id'])
        self._check_node_portable(envelope)
        retiring['act']['vocabulary'][1]['definition'] = '$control_sensitive'
        with self.assertRaisesRegex(ValueError, 'expression must use its definition'):
            ucl.continue_portable(portable.encode(prior), retiring)

    def test_embedded_template_can_author_a_complete_contribution(self):
        starter = json.loads((ROOT / 'examples/challenge.txt').read_bytes())
        draft = json.loads((ROOT / 'examples/challenge_reply.json').read_bytes())
        incoming = ucl.continue_portable(starter, draft)
        rules = incoming['structural_rules']['rules']
        template = copy.deepcopy(rules['reply_template']['contribution'])
        template['act']['speaker'] = 'Template reader'
        template['act']['vocabulary'][1]['definition'] = '$control_sensitive'
        result = ucl.continue_portable(incoming, template)
        packet = portable.decode(result)
        self.assertEqual(packet['discourse']['current'], 't10')
        self.assertIn('$example_predicate', packet['definitions'])
        self.assertEqual(packet['acknowledgements'][-1]['target'], {'claim': 'theory', 'path': [1]})
        self.assertNotIn('reply_template', portable.encode(self.packet)['structural_rules']['rules'])
        self._check_node_portable(result)

    def _check_node_portable(self, envelope):
        if not shutil.which('node'):
            return
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / 'packet.txt'
            packet.write_bytes(core.canon(envelope))
            checked = subprocess.run(
                ['node', str(ROOT / 'tools/check_ucl_portable.js'), str(packet)],
                text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_portable_encode_and_node_accept_a_valid_packet_over_one_megabyte(self):
        envelope = json.loads((ROOT / 'examples/quickstart.txt').read_bytes())
        draft = core.draft_from_packet(portable.decode(envelope))
        for turn in range(3, 76):
            draft['discourse']['acts'].append({
                'id': f't{turn}', 'speaker': 'Ari', 'kind': 'response',
                'references': ['t1'], 'text': 'a' * 14000, 'expressions': ['~[P][A]'],
                'details': {'responds_to': 't1', 'stance': 'mixed'},
            })
        draft['discourse']['current'] = 't75'
        packet = core.build(draft, version=core.DEPENDENCY_VERSION)
        inner = core.canon(packet)
        self.assertGreater(len(inner), core.MAX_EXPANDED)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'large-inner.json'
            outgoing = Path(directory) / 'large-portable.txt'
            source.write_bytes(inner)
            process = subprocess.run(
                [sys.executable, str(ROOT / 'src/ucl.py'), 'encode', str(source), str(outgoing)],
                text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(outgoing.read_bytes())
            self.assertEqual(portable.decode(result), packet)
            self._check_node_portable(result)

if __name__=='__main__':unittest.main()
