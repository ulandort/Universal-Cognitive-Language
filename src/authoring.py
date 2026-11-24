"""Append authored contributions to the UCL typed record."""

from collections.abc import Mapping

import core


def _checked(field, validator, *args, **kwargs):
    try:
        return validator(*args, **kwargs)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f'{field}: {exc}') from exc


def preflight(parent, contribution, *, archived=False):
    """Check the editable contribution with the same grammar used by build."""
    core.need(isinstance(contribution, dict), 'draft must be a JSON object')
    required = {'act', 'orientation', 'explanation', 'conclusion'}
    if missing := required - contribution.keys():
        raise ValueError('draft is missing fields: ' + ', '.join(sorted(missing)))
    core.need('declaration' not in contribution,
              'remove draft.declaration. continue generates the declaration layer from symbol usage')
    version = core.packet_version(parent)
    definitions = dict(parent['definitions'])
    additions = contribution.get('new_definitions', {})
    core.need(isinstance(additions, dict), 'draft.new_definitions must map aliases directly to definition objects')
    if overwritten := definitions.keys() & additions.keys():
        raise ValueError('draft.new_definitions cannot replace existing aliases: ' + ', '.join(sorted(overwritten)))
    if additions:
        definitions.update({alias: {'definition': definition} for alias, definition in additions.items()})
        _checked('draft.new_definitions (use bare objects with kind and gloss)', core._validate_definition_shapes,
                 definitions, version)
    claims = contribution.get('claims', {})
    core.need(isinstance(claims, dict), 'draft.claims must be an object of new claim bindings')
    if overwritten := parent['claims'].keys() & claims.keys():
        raise ValueError('draft.claims cannot replace existing bindings: ' + ', '.join(sorted(overwritten)))

    parser = core.Parser(definitions)
    prior = parent['discourse']['acts']
    act = contribution['act']
    core.need(isinstance(act, dict), 'draft.act must be an object')
    if missing := {'id', 'kind', 'speaker', 'references', 'text', 'expressions', 'details'} - act.keys():
        raise ValueError('draft.act is missing fields: ' + ', '.join(sorted(missing)))
    _checked('draft.act', core.validate_discourse, {'current': act['id'], 'acts': [act]}, definitions,
             parser, version=version, archived=archived, prior_acts=prior)
    types = {'orientation': ('orientation',), 'explanation': ('prop',), 'conclusion': ('prop', 'epistemic')}
    for field, expected in types.items():
        source = contribution[field]
        core.need(isinstance(source, str) and bool(source), f'draft.{field} needs a UCL expression string')
        tree = _checked(f'draft.{field}', parser.parse, source)
        core.need(tree[1] in expected, f'draft.{field} must be ' + ' or '.join(expected))
    role = definitions[contribution['orientation']]['definition']['role']
    core.need(core.orientation_matches(role, act['kind']),
              f'draft.orientation role {role} disagrees with act.kind {act["kind"]}')
    acknowledgements = contribution.get('acknowledgements', [])
    core.need(isinstance(acknowledgements, list), 'draft.acknowledgements must be an array')
    if acknowledgements:
        prior_ids = {ack['id'] for ack in parent['acknowledgements']}
        for index, ack in enumerate(acknowledgements):
            if isinstance(ack, Mapping) and isinstance(ack.get('id'), str) and ack['id'] in prior_ids:
                raise ValueError(f'draft.acknowledgements[{index}].id duplicates an earlier ACK: {ack["id"]}')
        _checked('draft.acknowledgements', core.validate_acknowledgements, acknowledgements,
                 {'acts': [*prior, act]}, definitions, parser, {**parent['claims'], **claims},
                 version=version, archived=archived)


def reply_template(parent, speaker, claim, path, *, alias=None, domain=None):
    """Seed a reply with exact references and leave its authorship to the participant."""
    binding = parent['claims'].get(claim)
    core.need(binding is not None, f'claim not found: {claim}')
    core.need(0 < len(speaker) <= 120, 'speaker must contain 1 to 120 characters')
    definitions = parent['definitions']
    core.resolve_claim_path(core.Parser(definitions), binding['expression'], path)
    acts = parent['discourse']['acts']

    def next_id(records, prefix):
        used = {record['id'] for record in records}
        number = len(used) + 1
        while f'{prefix}{number}' in used:
            number += 1
        return f'{prefix}{number}'

    orientation = next((symbol for symbol, entry in sorted(definitions.items())
                        if entry['definition'].get('kind') == 'orientation'
                        and entry['definition']['role'] == 'response'), None)
    core.need(orientation is not None, 'a response orientation must be defined to use this template')
    current = parent['discourse']['current']
    act_id = next_id(acts, 't')
    draft = {
        'act': {'id': act_id, 'kind': 'response', 'speaker': speaker,
                'references': list(dict.fromkeys((current, binding['act']))),
                'text': '', 'expressions': [],
                'details': {'responds_to': current, 'stance': 'undetermined'}},
        'orientation': orientation,
        'explanation': '', 'conclusion': '',
        'acknowledgements': [{
            'id': next_id(parent['acknowledgements'], 'x'), 'by': act_id,
            'target': {'claim': claim, 'path': path}, 'action': 'received',
            'qualification': None, 'replacement': None, 'note': '',
        }],
    }
    if alias is not None:
        core.need(alias not in definitions, f'alias already defined: {alias}')
        if domain is not None:
            core.need(domain in parent['domains'], f'domain not found: {domain}')
        example = {'kind': 'predicate', 'args': [domain] if domain is not None else [], 'gloss': 'example'}
        _checked('concept alias', core._validate_definition_shapes,
                 {**definitions, alias: {'definition': example}}, core.packet_version(parent))
        draft['new_definitions'] = {alias: {**example, 'gloss': ''}}
    return draft


def author(parent, contribution, *, archived=False):
    draft=core.draft_from_packet(parent, archived=archived)
    acts=draft['discourse']['acts']
    act=contribution['act']
    if act['id'] in {x['id'] for x in acts}:raise ValueError('new act ID must be unique')
    for glyph,definition in contribution.get('new_definitions',{}).items():
        if glyph in draft['definitions']:raise ValueError('cannot overwrite immutable glyph '+glyph)
        draft['definitions'][glyph]={'definition':definition}
        if definition['kind']=='domain':draft['domains'][glyph]=contribution.get('new_domains',{}).get(glyph,{'mode':'open','members':None})
    acts.append(act)
    draft['discourse']['current']=act['id']
    draft['acknowledgements'].extend(contribution.get('acknowledgements',[]))
    draft['revisions'].extend(contribution.get('revisions',[]))
    draft['claims'].update(contribution.get('claims',{}))
    draft['viewpoints'].extend(contribution.get('viewpoints',[]))
    draft['orientation']=contribution['orientation']
    draft['explanation']=contribution['explanation']
    draft['conclusion']=contribution['conclusion']
    if 'context_updates' in contribution:draft['context'].update(contribution['context_updates'])
    hist=draft['history']
    hist['summary']=contribution.get('history_summary',hist['summary']+' New act '+act['id']+' appended.')
    hist['unresolved'].extend(contribution.get('new_unresolved',[]))
    return core.build(draft, version=core.packet_version(parent), archived=archived)

