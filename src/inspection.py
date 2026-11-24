"""Produce a local human-readable view of a validated UCL packet."""

import core


def _display(value, limit=300):
    # Escape terminal controls and keep each packet-supplied value on one line.
    prefix = value[:limit]
    escaped = ''.join(c if c.isprintable() else ascii(c)[1:-1] for c in prefix)
    return escaped + ('…' if len(value) > limit else '')


def describe_packet(packet):
    definitions = packet['definitions']
    acts = packet['discourse']['acts']
    history = packet['history']
    acts_by_id = {act['id']: act for act in acts}
    first_use = {}
    recent_symbols = set()
    for position, act in enumerate(acts):
        parser = core.Parser(definitions)
        for expression in act['expressions']:
            parser.parse(expression)
        for glyph in parser.used.intersection(definitions):
            first_use.setdefault(glyph, act['id'])
            if position >= len(acts) - 5:
                recent_symbols.add(glyph)

    lines = [
        f'UCL/2.0 Portable | {len(acts)} retained acts | {len(definitions)} defined symbols',
        f'History: {history["status"]} ({len(history["omissions"])} omission records)',
        f'Recorded summary: {_display(history["summary"])}',
        '',
        'Defined symbols',
    ]
    for glyph, entry in sorted(definitions.items()):
        definition = entry['definition']
        usage = _display(first_use[glyph]) if glyph in first_use else 'none'
        recent = ' | used recently' if glyph in recent_symbols else ''
        lines.append(f'  {_display(glyph)} ({definition["kind"]}) {_display(definition["gloss"])}'
                     f' | first retained act expression: {usage}{recent}')
    lines.extend(('', f'Recent acts ({min(5, len(acts))} of {len(acts)})'))
    for act in acts[-5:]:
        references = ', '.join(_display(ref) for ref in act['references'])
        detail = f' → {references}' if references else ''
        lines.append(f'  {_display(act["id"])} {_display(act["speaker"])} '
                     f'({act["kind"]}){detail} | {_display(act["text"])}')

    acks = packet['acknowledgements']
    lines.extend(('', f'Recorded acknowledgements ({min(10, len(acks))} of {len(acks)})'))
    for ack in acks[-10:]:
        target = ack['target']
        author = acts_by_id[ack['by']]
        if 'claim' in target:
            binding = packet['claims'][target['claim']]
            tree = core.resolve_claim_path(core.Parser(definitions), binding['expression'], target['path'])
            scope = (f'{_display(target["claim"])} path {target["path"]} '
                     f'(from {_display(binding["act"])}) {_display(core.render(tree))}')
        else:
            act = acts_by_id[target['act']]
            index = target['expression_index']
            scope = _display(act['id'])
            if index is not None:
                scope += f' expression {index} {_display(act["expressions"][index])}'
        qualification = ack['qualification']
        condition = qualification['expression'] if isinstance(qualification, dict) else qualification
        suffix = f' | condition: {_display(condition)}' if condition else ''
        lines.append(f'  {_display(author["speaker"])} ({_display(author["id"])}) '
                     f'{_display(ack["action"])} → {scope}{suffix}')

    lines.extend(('', 'Recorded open issues'))
    lines.extend(f'  {_display(issue)}' for issue in history['unresolved'])
    if not history['unresolved']:
        lines.append('  None recorded')
    if history['omissions']:
        lines.extend(('', 'Disclosed omissions'))
        lines.extend(f'  {_display(item["scope"])}: {_display(item["not_preserved"])}'
                     for item in history['omissions'])
    return '\n'.join(lines)
