"""Derive a state ledger from a validated UCL Portable packet."""

import core


STANCE_ACTIONS = core.RETRACTABLE_ACK_ACTIONS | {'withdraw'}
STATE_LIMIT = 12
COMPACT_DIFF_LIMIT = 8


def _stance_key(entry):
    return (entry['speaker'], entry['source_act'], entry['expression_index'], tuple(entry['path']))


def _resolve_target(packet, acts_by_id, target):
    if 'claim' in target:
        binding = packet['claims'][target['claim']]
        path = target['path']
        parser = core.Parser(packet['definitions'])
        tree = core.resolve_claim_path(parser, binding['expression'], path)
        return binding['act'], binding['expression_index'], path, core.render(tree)

    act_id = target['act']
    index = target['expression_index']
    expression = acts_by_id[act_id]['expressions'][index] if index is not None else None
    return act_id, index, [], expression


def _ack_scope(ack, acks_by_id):
    if ack['action'] == 'retract':
        return acks_by_id[ack['target']['ack']]['target']
    return ack['target']


def _retraction_fields(ack, acks_by_id):
    if ack['action'] == 'retract':
        original = acks_by_id[ack['target']['ack']]
        return {'retracts': original['id'], 'original_ack_act': original['by']}
    return {}


def _new_definitions(packet, previous, *, operation='--since'):
    old_acts = previous['discourse']['acts']
    acts = packet['discourse']['acts']
    versions = (previous['guide']['version'], packet['guide']['version'])
    stable_versions = (core.LONG_VERSION, *core.RETRACTION_VERSIONS)
    same_semantics = versions[0] == versions[1] or (
        all(version in stable_versions for version in versions)
        and stable_versions.index(versions[0]) < stable_versions.index(versions[1])
    )
    if (not same_semantics or
            acts[:len(old_acts)] != old_acts or
            any(packet[field].get(key) != value
                for field in ('definitions', 'claims', 'domains')
                for key, value in previous[field].items())):
        raise ValueError(f'{operation} requires an earlier packet from the same retained conversation')
    return sorted(packet['definitions'].keys() - previous['definitions'].keys())


def focused_context(packet, *, act_id=None, claim_id=None, path=None):
    """Return a bounded excerpt of a validated packet, with exact source records."""
    acts = packet['discourse']['acts']
    by_id = {act['id']: act for act in acts}
    acks_by_id = {ack['id']: ack for ack in packet['acknowledgements']}
    definitions = packet['definitions']
    parser = core.Parser(definitions)
    scope = None
    if claim_id is not None:
        binding = packet['claims'].get(claim_id)
        if binding is None:
            raise ValueError(f'claim not found: {claim_id}')
        act_id = binding['act']
        tree = core.resolve_claim_path(parser, binding['expression'], path or [])
        scope = {'claim': claim_id, **binding, 'path': path, 'selected_expression': core.render(tree)}

    act = by_id.get(act_id)
    if act is None:
        raise ValueError(f'act not found: {act_id}')
    bound_claims = {
        name: binding for name, binding in packet['claims'].items()
        if binding['act'] == act_id and (scope is None or binding['expression_index'] == scope['expression_index'])
    }
    for expression in act['expressions']:
        parser.parse(expression)
    if act['kind'] == 'conditional':
        for expression in [act['details']['antecedent'], *act['details']['consequents']]:
            parser.parse(expression)
    for record in act.get('vocabulary', []):
        parser.used.add(record['definition'])
        if record.get('successor') is not None:
            parser.used.add(record['successor'])

    def related(ack):
        target = _ack_scope(ack, acks_by_id)
        if scope is None and ack['by'] == act_id:
            return True
        if 'claim' in target:
            return target['claim'] in bound_claims and (path is None or target['path'] == path)
        return target['act'] == act_id and (scope is None or (
            not path and target['expression_index'] == scope['expression_index']
        ))

    positions = {act['id']: index for index, act in enumerate(acts)}
    matches = sorted((ack for ack in packet['acknowledgements'] if related(ack)),
                     key=lambda ack: positions[ack['by']])
    selected = matches
    if len(matches) > 12:
        substantive = [ack for ack in matches if ack['action'] in STANCE_ACTIONS or ack['action'] == 'retract']
        selected = substantive or matches
        if len(selected) > 12:
            selected = [*selected[:2], *selected[-10:]]
    acknowledgements = []
    for ack in selected:
        source, index, target_path, expression = _resolve_target(packet, by_id, _ack_scope(ack, acks_by_id))
        if expression is not None:
            origin = by_id[source]['expressions'][index]
            parser.parse(origin)
        qualification = ack['qualification']
        if isinstance(qualification, dict):
            parser.parse(qualification['expression'])
        if ack['action'].startswith('ext:'):
            parser.used.add(ack['action'][4:])
        acknowledgements.append({
            **ack, 'speaker': by_id[ack['by']]['speaker'], 'source_act': source,
            'expression_index': index, 'path': target_path, 'expression': expression,
            **_retraction_fields(ack, acks_by_id),
        })

    aliases = parser.used.intersection(definitions)
    for alias in list(aliases):
        definition = definitions[alias]['definition']
        aliases.update(definition.get('args', []))
        aliases.update(definition[field] for field in ('sort', 'returns') if field in definition)
    return {
        'view': 'selected excerpt',
        'packet_sha256': packet['integrity']['sha256'],
        'history_status': packet['history']['status'],
        'retained_act_count': len(acts),
        'current_act': packet['discourse']['current'],
        'act': act,
        'claim_scope': scope,
        'claim_ids_at_source': sorted(bound_claims)[:12],
        'claim_count_at_source': len(bound_claims),
        'acknowledgements': acknowledgements,
        'matching_acknowledgement_count': len(matches),
        'definitions': {alias: definitions[alias] for alias in sorted(aliases)},
        'domains': {alias: packet['domains'][alias] for alias in sorted(aliases) if alias in packet['domains']},
    }


def derive_ledger(packet, previous=None, *, recent_usage_only=False):
    """Project retained records without inferring agreement or question resolution."""
    definitions = packet['definitions']
    acts = packet['discourse']['acts']
    history = packet['history']
    acts_by_id = {act['id']: act for act in acts}
    positions = {act['id']: index for index, act in enumerate(acts)}

    latest = {}
    withdrawals = []
    retractions = []
    recent_acknowledgements = []
    acknowledgements = sorted(packet['acknowledgements'], key=lambda ack: positions[ack['by']])
    acks_by_id = {ack['id']: ack for ack in acknowledgements}
    for position, ack in enumerate(acknowledgements):
        is_stance = ack['action'] in STANCE_ACTIONS
        is_retraction = ack['action'] == 'retract'
        is_recent = position >= len(acknowledgements) - 10
        if not (is_stance or is_retraction or is_recent):
            continue
        speaker = acts_by_id[ack['by']]['speaker']
        act_id, index, path, expression = _resolve_target(packet, acts_by_id, _ack_scope(ack, acks_by_id))
        entry = {
            'speaker': speaker,
            'by': ack['by'],
            'acknowledgement': ack['id'],
            'action': ack['action'],
            'target': ack['target'],
            'source_act': act_id,
            'expression_index': index,
            'path': path,
            'expression': expression,
            'qualification': ack['qualification'],
            'replacement': ack['replacement'],
            **_retraction_fields(ack, acks_by_id),
        }
        if is_recent:
            recent_acknowledgements.append(entry)
        if is_retraction:
            key = _stance_key(entry)
            clears_stance = latest.get(key, {}).get('acknowledgement') == entry['retracts']
            entry['cleared_current_stance'] = clears_stance
            retractions.append(entry)
            if clears_stance:
                del latest[key]
                latest[key] = entry
        if not is_stance:
            continue
        key = _stance_key(entry)
        latest.pop(key, None)
        latest[key] = entry
        if ack['action'] == 'withdraw':
            withdrawals.append(entry)

    first_use = {}
    recent_uses = {}
    vocabulary = []
    for position, act in enumerate(acts):
        is_recent = position >= len(acts) - 5
        if is_recent or not recent_usage_only:
            parser = core.Parser(definitions)
            for expression in act['expressions']:
                parser.parse(expression)
            for glyph in parser.used.intersection(definitions):
                first_use.setdefault(glyph, act['id'])
                if is_recent:
                    recent_uses.setdefault(glyph, []).append(act['id'])
        for entry in act.get('vocabulary', []):
            alias = entry['definition']
            record = {**entry, 'act': act['id'], 'speaker': act['speaker'],
                      'definition_id': definitions[alias]['id']}
            if entry['action'] == 'retire':
                successor = entry['successor']
                record['successor_id'] = definitions[successor]['id'] if successor is not None else None
            else:
                record['expression'] = act['expressions'][entry['expression_index']]
            vocabulary.append(record)

    ledger = {
        'ledger_version': 1,
        'packet_sha256': packet['integrity']['sha256'],
        'history_status': history['status'],
        'retained_act_count': len(acts),
        'recorded_summary': history['summary'],
        'recorded_open_issues': history['unresolved'],
        'questions': [
            {'act': act['id'], 'speaker': act['speaker'], 'targets': act['details']['targets']}
            for act in acts if act['kind'] == 'question'
        ],
        'omissions': history['omissions'],
        'stances': list(latest.values()),
        'withdrawals': withdrawals,
        'retractions': retractions,
        'recent_acknowledgements': recent_acknowledgements,
        'vocabulary': vocabulary,
        'symbols': [
            {
                'symbol': glyph,
                'definition_id': entry['id'],
                'kind': entry['definition']['kind'],
                'gloss': entry['definition']['gloss'],
                'first_retained_expression_act': first_use.get(glyph),
                'used_in_recent_acts': glyph in recent_uses,
                'recent_expression_acts': recent_uses.get(glyph, []),
            }
            for glyph, entry in sorted(definitions.items())
        ],
    }
    if previous is not None:
        ledger['comparison'] = {
            'previous_packet_sha256': previous['integrity']['sha256'],
            'added_symbols': _new_definitions(packet, previous),
        }
    return ledger


def compare_packets(previous, packet, *, compact=False):
    """Return a deterministic delta between an earlier packet and its continuation."""
    added_symbols = _new_definitions(packet, previous, operation='diff')
    for field in ('acknowledgements', 'revisions', 'viewpoints'):
        prior = previous[field]
        if packet[field][:len(prior)] != prior:
            raise ValueError(f'diff requires the earlier {field} to be preserved in order')
    before = derive_ledger(previous, recent_usage_only=True)
    after = derive_ledger(packet, recent_usage_only=True)
    previous_stances = {_stance_key(entry): entry for entry in before['stances']}
    stance_changes = []
    for entry in after['stances']:
        old = previous_stances.get(_stance_key(entry))
        meaning_fields = ('action', 'qualification', 'replacement', 'retracts')
        if old is None or any(old.get(field) != entry.get(field) for field in meaning_fields):
            stance_changes.append({'before': old, 'after': entry})

    old_issues = set(before['recorded_open_issues'])
    new_issues = set(after['recorded_open_issues'])
    new_acts = packet['discourse']['acts'][before['retained_act_count']:]
    new_acknowledgements = packet['acknowledgements'][len(previous['acknowledgements']):]
    new_ack_ids = {ack['id'] for ack in new_acknowledgements}
    delta = {
        'diff_version': 1,
        'previous_packet_sha256': before['packet_sha256'],
        'packet_sha256': after['packet_sha256'],
        'new_act_count': len(new_acts),
        'new_acknowledgement_count': len(new_acknowledgements),
        'new_definitions': {alias: packet['definitions'][alias] for alias in added_symbols},
        'new_claims': {claim: packet['claims'][claim] for claim in sorted(packet['claims'].keys() - previous['claims'].keys())},
        'new_definition_revisions': packet['revisions'][len(previous['revisions']):],
        'retirements': [entry for entry in after['vocabulary'][len(before['vocabulary']):] if entry['action'] == 'retire'],
        'stance_changes': stance_changes,
        'new_retractions': [entry for entry in after['retractions'] if entry['acknowledgement'] in new_ack_ids],
        'new_questions': [{'act': act['id'], 'targets': act['details']['targets']}
                          for act in new_acts if act['kind'] == 'question'],
        'recorded_open_issues_added': sorted(new_issues - old_issues),
        'recorded_open_issues_removed': sorted(old_issues - new_issues),
    }
    return _compact_delta(delta, new_acts) if compact else delta


def _compact_delta(delta, new_acts):
    def stance(record):
        if record is None:
            return None
        qualification = record['qualification']
        if isinstance(qualification, dict):
            qualification = qualification['expression']
        return {
            'ack': record['acknowledgement'], 'by': record['by'], 'action': record['action'],
            'qualification_preview': qualification[:160] if qualification is not None else None,
            'replacement': record['replacement'],
        }

    def scope(record):
        return {key: record[key] for key in ('speaker', 'target', 'source_act', 'expression_index', 'path')}

    acts = [{'id': act['id'], 'kind': act['kind'], 'speaker': act['speaker']}
            for act in new_acts[-COMPACT_DIFF_LIMIT:]]
    changes = [
        {**scope(change['after']), 'before': stance(change['before']), 'after': stance(change['after'])}
        for change in delta['stance_changes'][-COMPACT_DIFF_LIMIT:]
    ]
    retractions = [
        {**scope(entry), 'ack': entry['acknowledgement'], 'by': entry['by'],
         'retracts': entry['retracts'], 'cleared_current_stance': entry['cleared_current_stance']}
        for entry in delta['new_retractions'][-COMPACT_DIFF_LIMIT:]
    ]
    definitions = [
        {'alias': alias, 'id': record['id'], 'kind': record['definition']['kind'],
         'gloss_preview': record['definition']['gloss'][:160]}
        for alias, record in sorted(delta['new_definitions'].items())[:COMPACT_DIFF_LIMIT]
    ]
    return {
        'view': 'compact packet diff', 'diff_version': delta['diff_version'],
        'previous_packet_sha256': delta['previous_packet_sha256'], 'packet_sha256': delta['packet_sha256'],
        'counts': {
            'new_acts': delta['new_act_count'], 'new_acknowledgements': delta['new_acknowledgement_count'],
            **{key: len(delta[key]) for key in (
                'stance_changes', 'new_retractions', 'new_definitions', 'new_claims',
                'new_definition_revisions', 'retirements', 'new_questions',
                'recorded_open_issues_added', 'recorded_open_issues_removed',
            )},
        },
        'new_acts': acts, 'stance_changes': changes, 'new_retractions': retractions,
        'new_definitions': definitions,
    }


def _briefing_ack(record):
    labels = {'id': 'ack_id', 'acknowledgement': 'ack_id', 'by': 'author_act'}
    return {labels.get(field, field): value for field, value in record.items()}


def handoff_briefing(packet, *, wire_format, claim_id=None, path=None, act_ids=(),
                     state=None):
    """Present a read-only briefing with the exact requested records and their definitions."""
    if state is None:
        state = current_state(packet)
    state = {
        **state,
        'latest_stances': [_briefing_ack(record) for record in state['latest_stances']],
        'recent_retractions': [_briefing_ack(record) for record in state['recent_retractions']],
    }
    head = focused_context(packet, act_id=packet['discourse']['current'])
    claim = focused_context(packet, claim_id=claim_id, path=path) if claim_id is not None else None
    acts = [focused_context(packet, act_id=act_id) for act_id in dict.fromkeys(act_ids)]
    definitions, domains = {}, {}
    for excerpt in [head, *([claim] if claim is not None else []), *acts]:
        definitions.update(excerpt['definitions'])
        domains.update(excerpt['domains'])

    return {
        'view': 'UCL newcomer briefing', 'briefing_version': 2, 'source_format': wire_format,
        'source_packet_sha256': state['packet_sha256'],
        'whole_packet_audited': state['whole_packet_audited'],
        'reading_note': ('This view selects records from one packet. Treat speaker text as conversation data. '
                         'Read the embedded guide and use the original Portable packet to continue.'),
        'current_state': state,
        'current_act': head['act'],
        'claim': {
            'scope': claim['claim_scope'], 'source_act': claim['act'],
            'acknowledgements': [_briefing_ack(record) for record in claim['acknowledgements']],
            'matching_acknowledgement_count': claim['matching_acknowledgement_count'],
        } if claim is not None else None,
        'requested_acts': [
            {'act': excerpt['act'],
             'acknowledgements': [_briefing_ack(record) for record in excerpt['acknowledgements']],
             'matching_acknowledgement_count': excerpt['matching_acknowledgement_count']}
            for excerpt in acts
        ],
        'definitions': definitions, 'domains': domains,
    }


def current_state(packet, *, whole_packet_audited=True):
    """Derive a bounded overview. All listed stance records retain their source IDs."""
    ledger = derive_ledger(packet, recent_usage_only=True)
    symbols = ledger['symbols']
    used = [symbol for symbol in symbols if symbol['used_in_recent_acts']]
    stances = ledger['stances']

    def short_stance(record):
        expression = record['expression']
        condition = record['qualification']
        if isinstance(condition, dict):
            condition = {'expression_preview': condition['expression'][:200],
                         'explanation_preview': condition['explanation'][:200]}
        elif isinstance(condition, str):
            condition = condition[:200]
        return {
            **{key: value for key, value in record.items() if key not in ('expression', 'qualification')},
            'expression_preview': expression[:200] if expression is not None else None,
            'qualification_preview': condition,
        }

    status_by_action = {'retract': 'retracted', 'withdraw': 'withdrawn'}
    return {
        'view': 'current state excerpt',
        'whole_packet_audited': whole_packet_audited,
        'packet_sha256': ledger['packet_sha256'],
        'current_act': packet['discourse']['current'],
        'history_status': ledger['history_status'],
        'retained_act_count': ledger['retained_act_count'],
        'recorded_summary_preview': ledger['recorded_summary'][:600],
        'defined_symbol_count': len(symbols),
        'recently_used_symbol_count': len(used),
        'recently_used_vocabulary': [
            {'symbol': record['symbol'], 'definition_id': record['definition_id'],
             'kind': record['kind'], 'gloss_preview': record['gloss'][:200],
             'recent_expression_acts': record['recent_expression_acts']}
            for record in used[:STATE_LIMIT]
        ],
        'recorded_open_issue_count': len(ledger['recorded_open_issues']),
        'recorded_open_issue_previews': [issue[:200] for issue in ledger['recorded_open_issues'][:STATE_LIMIT]],
        'readable_question_count': len(ledger['questions']),
        'recent_readable_questions': [
            {'act': record['act'], 'speaker': record['speaker'],
             'target_count': len(record['targets']),
             'target_previews': [target[:200] for target in record['targets'][:3]]}
            for record in ledger['questions'][-5:]
        ],
        'latest_stance_count': len(stances),
        'latest_stances': [
            {'status': status_by_action.get(record['action'], 'current'), **short_stance(record)}
            for record in stances[-STATE_LIMIT:]
        ],
        'retraction_count': len(ledger['retractions']),
        'recent_retractions': [short_stance(record) for record in ledger['retractions'][-5:]],
        'retirement_count': sum(record['action'] == 'retire' for record in ledger['vocabulary']),
        'recent_retirements': [record for record in ledger['vocabulary'] if record['action'] == 'retire'][-5:],
    }


def _display(value, limit=300):
    # Escape terminal controls and keep each packet-supplied value on one line.
    prefix = value[:limit]
    escaped = ''.join(c if c.isprintable() else ascii(c)[1:-1] for c in prefix)
    return escaped + ('…' if len(value) > limit else '')


def _format_acknowledgement(entry):
    target = entry['target']
    source = _display(entry['source_act'])
    if 'claim' in target:
        scope = f'{_display(target["claim"])} path {entry["path"]} (from {source})'
    elif entry['expression_index'] is not None:
        scope = f'{source} expression {entry["expression_index"]}'
    else:
        scope = source
    if entry['expression'] is not None:
        scope += f' {_display(entry["expression"])}'
    qualification = entry['qualification']
    condition = qualification['expression'] if isinstance(qualification, dict) else qualification
    suffix = f' | condition: {_display(condition)}' if condition else ''
    if 'retracts' in entry:
        suffix += f' | retracts ACK {_display(entry["retracts"])}'
    if entry['replacement'] is not None:
        suffix += f' | proposed replacement: {_display(entry["replacement"])}'
    return (f'  {_display(entry["speaker"])} ({_display(entry["by"])}) {_display(entry["action"])}'
            f' → {scope}{suffix} | ACK {_display(entry["acknowledgement"])}')


def _format_retirement(entry):
    speaker = _display(entry['speaker'])
    act = _display(entry['act'])
    alias = _display(entry['definition'])
    successor = entry['successor']
    suffix = f' | suggested successor: {_display(successor)}' if successor is not None else ''
    return f'  {speaker} ({act}) retires {alias} for their use{suffix}'


def _concept_overview(ledger):
    symbols = ledger['symbols']
    recently_used = [symbol for symbol in symbols if symbol['used_in_recent_acts']]
    retired = [record for record in ledger['vocabulary'] if record['action'] == 'retire']
    lines = [
        'Concept index',
        f'  {len(symbols)} defined | {len(recently_used)} used in the last five retained acts'
        f' | {len(retired)} speaker retirement records',
    ]
    comparison = ledger.get('comparison')
    if comparison is not None:
        added = comparison['added_symbols']
        names = ', '.join(_display(alias) for alias in added[:8])
        more = f' (+{len(added) - 8} more)' if len(added) > 8 else ''
        lines.append(f'  Added since earlier packet ({len(added)}): {names or "none"}{more}')
    if recently_used:
        lines.append(f'  Recently used ({min(8, len(recently_used))} of {len(recently_used)})')
        for symbol in recently_used[:8]:
            acts = ', '.join(_display(act) for act in symbol['recent_expression_acts'])
            lines.append(f'    {_display(symbol["symbol"])} | {acts}')
    if retired:
        lines.append(f'  Latest retirement records ({min(3, len(retired))} of {len(retired)})')
        lines.extend(_format_retirement(entry) for entry in retired[-3:])
    return lines


def describe_packet(packet, label, previous=None):
    ledger = derive_ledger(packet, previous)
    acts = packet['discourse']['acts']
    lines = [
        f'{label} | {len(acts)} retained acts | {len(ledger["symbols"])} defined symbols',
        f'Packet SHA-256: {ledger["packet_sha256"]}',
        f'History: {ledger["history_status"]} ({len(ledger["omissions"])} omission records)',
        'Speaker names and statements are unauthenticated.',
        f'Recorded summary: {_display(ledger["recorded_summary"])}',
        '',
    ]
    lines.extend(_concept_overview(ledger))
    lines.extend(('', 'Recorded open issues'))
    lines.extend(f'  {_display(issue)}' for issue in ledger['recorded_open_issues'])
    if not ledger['recorded_open_issues']:
        lines.append('  None recorded')

    lines.extend(('', 'Latest recorded stances by speaker and exact target'))
    lines.extend(_format_acknowledgement(entry) for entry in ledger['stances'])
    if not ledger['stances']:
        lines.append('  None recorded')
    lines.extend(('', 'Recorded withdrawals'))
    lines.extend(_format_acknowledgement(entry) for entry in ledger['withdrawals'])
    if not ledger['withdrawals']:
        lines.append('  None recorded')

    if ledger['retractions']:
        lines.extend(('', 'Recorded ACK retractions'))
        lines.extend(_format_acknowledgement(entry) for entry in ledger['retractions'])
    displayed_acks = {entry['acknowledgement']
                      for key in ('stances', 'withdrawals', 'retractions') for entry in ledger[key]}
    other_acks = [entry for entry in ledger['recent_acknowledgements']
                  if entry['acknowledgement'] not in displayed_acks]
    if other_acks:
        lines.extend(('', 'Other recent acknowledgements'))
        lines.extend(_format_acknowledgement(entry) for entry in other_acks)

    examples = [entry for entry in ledger['vocabulary'] if entry['action'] != 'retire']
    if examples:
        lines.extend(('', f'Recent examples and counterexamples ({min(10, len(examples))} of {len(examples)})'))
        for entry in examples[-10:]:
            source = f'{_display(entry["speaker"])} ({_display(entry["act"])})'
            alias = _display(entry['definition'])
            lines.append(f'  {source} {entry["action"]} for {alias} | {_display(entry["expression"])}')

    questions = ledger['questions']
    lines.extend(('', f'Recent retained questions ({min(5, len(questions))} of {len(questions)})'))
    for question in questions[-5:]:
        for target in question['targets']:
            lines.append(f'  {_display(question["act"])} {_display(question["speaker"])} | {_display(target)}')

    lines.extend(('', 'Defined symbols'))
    added = set(ledger.get('comparison', {}).get('added_symbols', []))
    for symbol in ledger['symbols']:
        first = symbol['first_retained_expression_act']
        usage = _display(first) if first is not None else 'none'
        recent = ', '.join(_display(act) for act in symbol['recent_expression_acts'])
        recent = f' | recent acts: {recent}' if recent else ''
        new = ' | added since earlier packet' if symbol['symbol'] in added else ''
        lines.append(f'  {_display(symbol["symbol"])} ({symbol["kind"]}) {_display(symbol["gloss"])}'
                     f' | ID: {symbol["definition_id"]} | first retained act expression: {usage}{recent}{new}')

    lines.extend(('', f'Recent acts ({min(5, len(acts))} of {len(acts)})'))
    for act in acts[-5:]:
        references = ', '.join(_display(ref) for ref in act['references'])
        detail = f' → {references}' if references else ''
        lines.append(f'  {_display(act["id"])} {_display(act["speaker"])} '
                     f'({act["kind"]}){detail} | {_display(act["text"])}')

    if ledger['omissions']:
        lines.extend(('', 'Disclosed omissions'))
        lines.extend(f'  {_display(item["scope"])}: {_display(item["not_preserved"])}'
                     for item in ledger['omissions'])
    return '\n'.join(lines)
