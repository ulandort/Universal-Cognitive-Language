#!/usr/bin/env python3
"""UCL/2.0 experimental LOCAL EXACT reference compression. Not part of UCL/1.0.

No history is summarized or removed. All content needed for restoration is in the
same envelope, except that optional compact-guide mode requires a LOCAL matching
full guide already present (or a portable-mode retry).
"""
from __future__ import annotations
import base64
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
# No remote or absolute-path dependency; no guide lookup is performed.
MARKER = '$ucl_ref'
PROFILE = 'UCL-LRC/0.1-prototype'


def canon(x):
    return json.dumps(x, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def b64_sha(data):
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')


def ref_hash(value):
    return b64_sha(b'UCL-LRC-REF-1\n' + canon(value))


def walk_values(node):
    """Any JSON subtree except bare numerical/boolean/null scalars is a candidate."""
    if isinstance(node, (dict, list, str)):
        yield node
    if isinstance(node, dict):
        for v in node.values():
            yield from walk_values(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_values(v)


def reject_existing_markers(node):
    if isinstance(node, dict):
        if MARKER in node:
            raise ValueError('Reserved reference marker exists in uncompressed payload')
        for v in node.values():
            reject_existing_markers(v)
    elif isinstance(node, list):
        for v in node:
            reject_existing_markers(v)


def replace_equal(node, match_bytes, refname):
    if isinstance(node, (dict, list, str)) and canon(node) == match_bytes:
        return {MARKER: refname}
    if isinstance(node, dict):
        return {k: replace_equal(v, match_bytes, refname) for k, v in node.items()}
    if isinstance(node, list):
        return [replace_equal(v, match_bytes, refname) for v in node]
    return node


def build_envelope(source, payload, entries, profile):
    return {'format': PROFILE, 'profile': profile,
            'payload': payload, 'refs': entries,
            'original_canonical_sha256': b64_sha(canon(source)),
            'original_canonical_length': len(canon(source))}


def encode(source, profile, max_entries=80):
    reject_existing_markers(source)
    payload = copy.deepcopy(source)
    entries = {}
    # Only accept substitutions that actually reduce the COMPLETE canonical envelope.
    # Greedy algorithm reruns the candidate scan after every accepted substitution.
    for _ in range(max_entries):
        candidates = {}
        counts = Counter()
        for value in walk_values(payload):
            if isinstance(value, dict) and MARKER in value:
                continue
            vbytes = canon(value)
            if len(vbytes) < 10:
                continue
            counts[vbytes] += 1
            candidates[vbytes] = value
        repeated = [(raw, candidates[raw]) for raw, count in counts.items() if count > 1]
        if not repeated:
            break
        current = len(canon(build_envelope(source, payload, entries, profile)))
        chosen = None
        best_size = current
        new_id = 'r' + str(len(entries))
        for raw, value in repeated:
            new_payload = replace_equal(payload, raw, new_id)
            new_entries = {**entries, new_id: {'sha256': ref_hash(value), 'value': value}}
            trial_size = len(canon(build_envelope(source, new_payload, new_entries, profile)))
            if trial_size < best_size:
                chosen = (new_payload, new_entries)
                best_size = trial_size
        if chosen is None:
            break
        payload, entries = chosen
    return build_envelope(source, payload, entries, profile)


def decode(envelope, max_bytes=1048576, max_refs=1000):
    if envelope.get('format') != PROFILE:
        raise ValueError('Unsupported LRC envelope format')
    if envelope.get('profile') not in ('portable', 'compact'):
        raise ValueError('Unknown guide profile')
    entries = envelope.get('refs')
    if not isinstance(entries, dict) or len(entries) > max_refs:
        raise ValueError('Invalid reference dictionary size')
    for name, record in entries.items():
        if not isinstance(name, str) or not name.startswith('r') or not name[1:].isdigit():
            raise ValueError('Invalid dictionary reference name')
        if not isinstance(record, dict) or set(record) != {'sha256', 'value'}:
            raise ValueError('Malformed dictionary entry')
        reject_existing_markers(record['value'])
        if record['sha256'] != ref_hash(record['value']):
            raise ValueError('Dictionary entry failed SHA-256 verification')
    def expand(node, depth=0):
        if depth > 120:
            raise ValueError('Exceeded expansion nesting bound')
        if isinstance(node, dict):
            if MARKER in node:
                if len(node) != 1 or not isinstance(node[MARKER], str):
                    raise ValueError('Malformed reference marker')
                key = node[MARKER]
                if key not in entries:
                    raise ValueError('Missing dictionary reference')
                return copy.deepcopy(entries[key]['value'])
            return {k: expand(v, depth+1) for k, v in node.items()}
        if isinstance(node, list):
            return [expand(v, depth+1) for v in node]
        return node
    restored = expand(envelope['payload'])
    restored_bytes = canon(restored)
    if len(restored_bytes) > max_bytes:
        raise ValueError('Expanded packet exceeds bound')
    if len(restored_bytes) != envelope['original_canonical_length']:
        raise ValueError('Original length mismatch')
    if b64_sha(restored_bytes) != envelope['original_canonical_sha256']:
        raise ValueError('Original packet SHA-256 mismatch')
    return restored




def encode_if_smaller(source, profile='portable'):
    """Return lossless LRC envelope only when it reduces canonical byte size."""
    envelope = encode(source, profile)
    return envelope if len(canon(envelope)) < len(canon(source)) else source


def is_envelope(value):
    return isinstance(value, dict) and value.get('format') == PROFILE


def decode_if_needed(value):
    return decode(value) if is_envelope(value) else value