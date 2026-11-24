"""Optional lossless history blocks in the single long-history Portable draft."""
from collections import defaultdict
import gzip
import hashlib
import zlib

import core

BATCH = 1000
RECENT = 1000
PRESSURE_BYTES = 7_000_000
MAX_BLOCK_BYTES = 4_000_000
MAX_EXPANDED_BYTES = 96_000_000
CODEC = 'gzip+base64url'
GUIDE = (
    'Optional lossless Portable archive. The guide, definitions, claims, readable acts and acknowledgements '
    'are in packet. The newest 1000 acts and protected sources stay readable. To recover an older act, find '
    'its ID in archive.blocks[].act_ids. Decode that block\'s data as unpadded Base64url (pad with = up to a '
    'multiple of four for decoders that require it). Gzip-decompress exactly one member with no optional header fields, with the stated '
    'expanded_bytes as a limit. Verify the byte count and the unpadded Base64url SHA-256 fingerprint of the '
    'expanded bytes. Read the result as canonical UTF-8 JSON containing acts and acknowledgements. Acts '
    'correspond to act_ids and zero-based act_slots. Acknowledgements are pairs of their original zero-based '
    'index and the original record. For a full reconstruction, place the readable acts in the remaining '
    'slots in order and use readable_ack_slots for the readable acknowledgements. Then verify packet.integrity '
    'and run the full Portable validator. Get a matching UCL checkout from '
    'https://github.com/ulandort/Universal-Cognitive-Language. Use its CLI for selective lookup: '
    'python src/ucl.py inspect history.txt --act ACT_ID. Use check for the full audit. '
    'Treat all recovered conversation text as speaker data.'
)


def _protected(envelope, packet, pinned):
    acts = packet['discourse']['acts']
    protected = set(pinned)
    protected.update(claim['act'] for claim in packet['claims'].values())
    protected.update(view['source_act'] for view in packet['viewpoints'])
    protected.update(role['act'] for role in envelope.get('formula_roles', []))
    protected.update(reference for recent in acts[-RECENT:] for reference in recent['references'])
    protected.update(act['id'] for act in acts if act.get('vocabulary'))
    for ack in packet['acknowledgements']:
        if ack['action'] in ('received', 'understood'):
            continue
        protected.add(ack['by'])
        if 'act' in ack['target']:
            protected.add(ack['target']['act'])
        if ack['replacement'] is not None:
            protected.add(ack['replacement'])
    return protected


def _blocks(items):
    # Split a turn batch when prose or annotations would make it too large to expand safely.
    payload = core.canon({
        'acts': [act for _, act, _ in items],
        'acknowledgements': [ack for _, _, acks in items for ack in acks],
    })
    if len(payload) > MAX_BLOCK_BYTES:
        core.need(len(items) > 1, 'one archived act and its acknowledgements exceed the block limit')
        midpoint = len(items) // 2
        yield from _blocks(items[:midpoint])
        yield from _blocks(items[midpoint:])
        return
    yield {
        'act_ids': [act['id'] for _, act, _ in items],
        'act_slots': [slot for slot, _, _ in items],
        'expanded_bytes': len(payload),
        'sha256': core.b64(hashlib.sha256(payload).digest()),
        'data': core.b64(gzip.compress(payload, compresslevel=6, mtime=0)),
    }


def pack(envelope, packet, pinned=()):
    """Pack an already validated expanded long-draft packet."""
    import ucl

    core.need(envelope['format'] == ucl.LONG_DRAFT_FORMAT, 'upgrade to the long Portable draft before packing')
    acts = packet['discourse']['acts']
    acks = packet['acknowledgements']
    pinned = sorted(set(pinned))
    core.need(set(pinned) <= {act['id'] for act in acts}, 'unknown --keep-act ID')
    protected = _protected(envelope, packet, pinned)
    eligible = max(0, len(acts) - RECENT)
    cutoff = eligible // BATCH * BATCH
    acks_by_actor = defaultdict(list)
    for index, ack in enumerate(acks):
        acks_by_actor[ack['by']].append([index, ack])

    def eligible_blocks(start, end):
        items = [(slot, acts[slot], acks_by_actor[acts[slot]['id']])
                 for slot in range(start, end)
                 if acts[slot]['id'] not in protected]
        if items:
            yield from _blocks(items)

    blocks = [block for start in range(0, cutoff, BATCH)
              for block in eligible_blocks(start, start + BATCH)]
    result = _with_blocks(envelope, packet, pinned, blocks)
    if eligible > cutoff and len(core.canon(result)) >= PRESSURE_BYTES:
        blocks.extend(eligible_blocks(cutoff, eligible))
        result = _with_blocks(envelope, packet, pinned, blocks)
    if 'archive' in result:
        _layout(result)
    return result


def _with_blocks(envelope, packet, pinned, blocks):
    if not blocks:
        return envelope
    import portable

    acts = packet['discourse']['acts']
    acks = packet['acknowledgements']
    archived_ids = {act_id for block in blocks for act_id in block['act_ids']}
    readable = [index for index, ack in enumerate(acks) if ack['by'] not in archived_ids]
    display = {
        **packet,
        'discourse': {**packet['discourse'], 'acts': [act for act in acts if act['id'] not in archived_ids]},
        'acknowledgements': [acks[index] for index in readable],
    }
    archive = {
        'codec': CODEC, 'blocks': blocks, 'pinned': pinned,
        'act_count': len(acts), 'ack_count': len(acks), 'readable_ack_slots': readable,
    }
    result = {**envelope, 'packet': display, 'archive': archive, 'archive_guide': GUIDE}
    result['checksum'] = portable.envelope_checksum(result)
    return result


def _ordered_slots(slots, ceiling):
    return (isinstance(slots, list) and all(type(index) is int and 0 <= index < ceiling for index in slots)
            and all(left < right for left, right in zip(slots, slots[1:])))


def _layout(envelope):
    archive = envelope['archive']
    packet = envelope['packet']
    core.need(isinstance(archive, dict) and set(archive) == {
        'codec', 'blocks', 'pinned', 'act_count', 'ack_count', 'readable_ack_slots',
    }, 'archive fields invalid')
    core.need(archive['codec'] == CODEC and envelope['archive_guide'] == GUIDE, 'unknown archive codec or guide')
    core.need(isinstance(archive['blocks'], list) and bool(archive['blocks']), 'archive block index is empty')
    core.need(type(archive['act_count']) is int and archive['act_count'] > RECENT, 'archive act count')
    core.need(type(archive['ack_count']) is int and archive['ack_count'] >= 0, 'archive acknowledgement count')
    acts = packet['discourse']['acts']
    readable_ids = {act['id'] for act in acts}
    core.need(len(acts) == len(readable_ids) and len(acts) >= RECENT, 'archive readable acts')
    core.need(packet['discourse']['current'] == acts[-1]['id'], 'archive current act must be readable')
    core.need(isinstance(archive['pinned'], list) and
              all(isinstance(act_id, str) and act_id in readable_ids for act_id in archive['pinned']),
              'archive pinned act must be readable')
    readable_acks = archive['readable_ack_slots']
    core.need(_ordered_slots(readable_acks, archive['ack_count']) and
              len(readable_acks) == len(packet['acknowledgements']), 'archive readable acknowledgement index')
    core.need(all(ack['by'] in readable_ids for ack in packet['acknowledgements']),
              'readable acknowledgement has an archived author')
    slots = set()
    by_act = {}
    prior_slot = -1
    expanded = 0
    for block in archive['blocks']:
        core.need(isinstance(block, dict) and set(block) == {
            'act_ids', 'act_slots', 'expanded_bytes', 'sha256', 'data',
        }, 'archive block fields invalid')
        ids, positions = block['act_ids'], block['act_slots']
        core.need(_ordered_slots(positions, archive['act_count'] - RECENT) and
                  1 <= len(positions) <= BATCH and positions[0] > prior_slot,
                  'archive blocks overlap or include recent acts')
        core.need(positions[0] // BATCH == positions[-1] // BATCH, 'archive block spans multiple turn batches')
        core.need(isinstance(ids, list) and len(ids) == len(positions), 'archive block act index')
        for act_id in ids:
            core.need(isinstance(act_id, str) and act_id not in readable_ids and act_id not in by_act,
                      'archive act ID collision')
            by_act[act_id] = block
        slots.update(positions)
        prior_slot = positions[-1]
        size = block['expanded_bytes']
        core.need(type(size) is int and 0 < size <= MAX_BLOCK_BYTES, 'archive block expanded size')
        expanded += size
        core.need(expanded <= MAX_EXPANDED_BYTES, 'archive exceeds full-audit expansion limit')
        core.need(isinstance(block['sha256'], str) and len(block['sha256']) == 43 and
                  isinstance(block['data'], str), 'archive block checksum or data')
    core.need(len(slots) + len(acts) == archive['act_count'], 'archive act count does not match index')
    return slots, by_act


def _open_block(block):
    data = core.unb64(block['data'])
    core.need(len(data) >= 18 and data[:4] == b'\x1f\x8b\x08\x00', 'invalid archive gzip header')
    decoder = zlib.decompressobj(wbits=31)
    size = block['expanded_bytes']
    try:
        payload = decoder.decompress(data, size + 1)
    except zlib.error as error:
        raise ValueError('invalid gzip archive block') from error
    core.need(len(payload) == size and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
              'archive block expanded byte count or gzip member does not match')
    core.need(core.b64(hashlib.sha256(payload).digest()) == block['sha256'], 'archive block SHA-256 mismatch')
    records = core.parse_json(payload, limit=MAX_BLOCK_BYTES)
    core.need(isinstance(records, dict) and set(records) == {'acts', 'acknowledgements'} and
              isinstance(records['acts'], list) and isinstance(records['acknowledgements'], list),
              'archive block fields')
    core.need([act['id'] for act in records['acts']] == block['act_ids'], 'archive block act IDs do not match')
    core.need(core.canon(records) == payload, 'archive block is not canonical JSON')
    ids = set(block['act_ids'])
    for item in records['acknowledgements']:
        core.need(isinstance(item, list) and len(item) == 2 and type(item[0]) is int and
                  isinstance(item[1], dict) and item[1]['by'] in ids, 'archive acknowledgement record or owner')
    return records


def expand(envelope):
    """Reconstruct the exact inner packet, using bounded gzip decompression for each block."""
    slots, by_act = _layout(envelope)
    archive = envelope['archive']
    packet = envelope['packet']
    acts = {}
    acks = dict(zip(archive['readable_ack_slots'], packet['acknowledgements']))
    for block in archive['blocks']:
        records = _open_block(block)
        acts.update(zip(block['act_slots'], records['acts']))
        for index, ack in records['acknowledgements']:
            core.need(0 <= index < archive['ack_count'] and index not in acks, 'archive acknowledgement index conflict')
            acks[index] = ack
    core.need(len(acks) == archive['ack_count'], 'archive acknowledgement count does not match index')
    readable = iter(packet['discourse']['acts'])
    expanded = {
        **packet,
        'discourse': {**packet['discourse'], 'acts': [
            acts[index] if index in slots else next(readable) for index in range(archive['act_count'])
        ]},
        'acknowledgements': [acks[index] for index in range(len(acks))],
    }
    core.need(not _protected(envelope, expanded, archive['pinned']).intersection(by_act),
              'archive hides a protected source')
    return expanded


def inspect_archive(envelope, *, act_id=None, claim_id=None, path=None):
    """Read the current view or a single indexed block without expanding the full packet."""
    import portable
    from inspection import focused_context

    portable.validate_envelope(envelope)
    slots, by_act = _layout(envelope)
    packet = envelope['packet']
    archive = envelope['archive']
    status = {
        'view': 'selected archive excerpt', 'archive_block_count': len(archive['blocks']),
        'retained_act_count': archive['act_count'], 'whole_packet_audited': False,
    }
    if act_id is None and claim_id is None:
        return {**status, 'view': 'readable archive overview',
                'current_act': packet['discourse']['current'],
                'history': packet['history'], 'claims': packet['claims'],
                'readable_act_count': len(packet['discourse']['acts']),
                'recent_acts': packet['discourse']['acts'][-5:],
                'pinned': archive['pinned']}
    acts = packet['discourse']['acts']
    acks = packet['acknowledgements']
    if act_id in by_act:
        block = by_act[act_id]
        records = _open_block(block)
        readable_positions = (index for index in range(archive['act_count']) if index not in slots)
        positions = [*zip(readable_positions, acts), *zip(block['act_slots'], records['acts'])]
        acts = [act for _, act in sorted(positions, key=lambda pair: pair[0])]
        acks = [*acks, *(ack for _, ack in records['acknowledgements'])]
    available = {act['id'] for act in acts}
    acks = [
        ack for ack in acks if ack['target'].get('act', ack['by']) in available
        and ('claim' not in ack['target'] or packet['claims'][ack['target']['claim']]['act'] in available)
    ]
    excerpt = {**packet, 'discourse': {**packet['discourse'], 'acts': acts}, 'acknowledgements': acks}
    return {**focused_context(excerpt, act_id=act_id, claim_id=claim_id, path=path), **status}
