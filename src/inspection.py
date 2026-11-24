"""Derive a state ledger from a validated UCL Portable packet."""

import core


STANCE_ACTIONS = frozenset((
    'accept', 'reject', 'qualify', 'adopt-for-discussion', 'withhold-judgment', 'withdraw',
))


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


def _new_definitions(packet, previous):
    old_acts = previous['discourse']['acts']
    acts = packet['discourse']['acts']
    if (packet['guide']['version'] != previous['guide']['version'] or
            acts[:len(old_acts)] != old_acts or
            any(packet[field].get(key) != value
                for field in ('definitions', 'claims', 'domains')
                for key, value in previous[field].items())):
        raise ValueError('--since requires an earlier packet from the same retained conversation')
    return sorted(packet['definitions'].keys() - previous['definitions'].keys())


def derive_ledger(packet, previous=None):
    """Project retained records without inferring agreement or question resolution."""
    definitions = packet['definitions']
    acts = packet['discourse']['acts']
    history = packet['history']
    acts_by_id = {act['id']: act for act in acts}
    positions = {act['id']: index for index, act in enumerate(acts)}

    latest = {}
    withdrawals = []
    recent_acknowledgements = []
    acknowledgements = sorted(packet['acknowledgements'], key=lambda ack: positions[ack['by']])
    for position, ack in enumerate(acknowledgements):
        is_stance = ack['action'] in STANCE_ACTIONS
        is_recent = position >= len(acknowledgements) - 10
        if not is_stance and not is_recent:
            continue
        speaker = acts_by_id[ack['by']]['speaker']
        act_id, index, path, expression = _resolve_target(packet, acts_by_id, ack['target'])
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
        }
        if is_recent:
            recent_acknowledgements.append(entry)
        if not is_stance:
            continue
        key = (speaker, act_id, index, tuple(path))
        latest.pop(key, None)
        latest[key] = entry
        if ack['action'] == 'withdraw':
            withdrawals.append(entry)

    first_use = {}
    recent_uses = {}
    vocabulary = []
    for position, act in enumerate(acts):
        parser = core.Parser(definitions)
        for expression in act['expressions']:
            parser.parse(expression)
        for glyph in parser.used.intersection(definitions):
            first_use.setdefault(glyph, act['id'])
            if position >= len(acts) - 5:
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

    displayed_acks = {entry['acknowledgement'] for entry in ledger['stances'] + ledger['withdrawals']}
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
