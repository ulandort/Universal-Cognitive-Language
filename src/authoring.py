"""Append authored contributions to the UCL typed record."""

import core


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

