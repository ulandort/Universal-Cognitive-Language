#!/usr/bin/env python3
"""UCL Portable public API and CLI.

The validated inner glyph grammar remains in core.py, while the complete
self-contained Portable wire lives in portable.py.
"""
from __future__ import annotations
from core import *  # Preserve existing public typed-grammar API exactly.
import core as _core
import argparse
import json
import sys
from tempfile import NamedTemporaryFile
from pathlib import Path

VERSION='UCL/2.1'
PORTABLE_FORMAT='UCL/2.1-SAP1-PORTABLE'
LEGACY_PORTABLE_FORMAT='UCL/2.0-SAP1-PORTABLE'
INNER_GRAMMAR_VERSION=_core.DEPENDENCY_VERSION
MAX_PORTABLE_JSON=8_000_000

def __getattr__(name):
    """Retain access to internal helper names used by older local consumers."""
    return getattr(_core,name)

def encode_portable(packet, *, formula_roles=None):
    import portable
    return portable.encode(packet,formula_roles=formula_roles)

def decode_portable(envelope):
    import portable
    return portable.decode(envelope)

def check_portable(envelope):
    import portable
    packet=portable.decode(envelope)
    return {'status':'VALID '+portable.label(envelope['format']),
            'format':envelope['format'],
            'packet':_core.check(packet)}

def continue_portable(envelope, contribution):
    """Append an authored draft to a verified Portable envelope."""
    from authoring import author

    parent = decode_portable(envelope)
    if not isinstance(contribution, dict):
        raise ValueError('draft must be a JSON object')
    required = {'act', 'orientation', 'explanation', 'conclusion'}
    missing = required - contribution.keys()
    if missing:
        raise ValueError('draft is missing fields: ' + ', '.join(sorted(missing)))
    claims = contribution.get('claims', {})
    if not isinstance(claims, dict):
        raise ValueError('draft.claims must be an object of new claim bindings')
    if overwritten := parent['claims'].keys() & claims.keys():
        raise ValueError('draft.claims cannot replace existing bindings: ' + ', '.join(sorted(overwritten)))

    packet = author(parent, contribution)
    result = encode_portable(packet, formula_roles=envelope.get('formula_roles'))
    decode_portable(result)
    return result

def portable_json_bytes(envelope):
    data = _core.canon(envelope)
    if len(data) > MAX_PORTABLE_JSON:
        raise ValueError(f'Portable JSON output exceeds {MAX_PORTABLE_JSON} bytes')
    return data

def _write_handoff(source, output, result):
    import portable

    if source.resolve() == output.resolve() or (output.exists() and source.samefile(output)):
        raise ValueError('choose a different output file to preserve the incoming packet')
    data = portable_json_bytes(result)
    with NamedTemporaryFile(dir=output.parent, delete=False) as temp:
        staged = Path(temp.name)
        try:
            temp.write(data)
            temp.close()
            staged.replace(output)
        finally:
            staged.unlink(missing_ok=True)
    print('VALID ' + portable.label(result['format']), output)


def _continue_cli(args):
    if len(args) != 4:
        raise ValueError('Usage: python src/ucl.py continue incoming.txt next.txt < contribution.json')
    source, output = map(Path, args[2:])
    envelope = _core.read_json_file(source, limit=MAX_PORTABLE_JSON)
    if sys.stdin.isatty():
        print('Paste the JSON contribution, then press Ctrl-D (Ctrl-Z then Enter on Windows).', file=sys.stderr)
    try:
        contribution = _core.read_json(sys.stdin.buffer)
    except ValueError as exc:
        raise ValueError(f'draft on stdin: {exc}') from exc
    _write_handoff(source, output, continue_portable(envelope, contribution))

def main(args):
    """Dispatch current and archived Portable packets by their version markers."""
    import portable
    if len(args) > 1 and args[1] == 'continue':
        _continue_cli(args)
        return
    if len(args)<3:
        raise ValueError('Usage: python src/ucl.py check file.txt | encode inner.json portable.txt | decode portable.txt inner.json | continue incoming.txt next.txt < contribution.json | inspect portable.txt [--json] [--since earlier.txt] | upgrade old.txt current.txt | build/canonicalize/draft ...')
    command=args[1]
    if command=='check' and len(args)==3:
        data=_core.read_json_file(args[2], limit=MAX_PORTABLE_JSON)
        if isinstance(data,dict) and data.get('format') in (PORTABLE_FORMAT, LEGACY_PORTABLE_FORMAT):
            print(json.dumps(check_portable(data),indent=2))
        else:
            print(json.dumps(_core.check(data),indent=2))
    elif command=='inspect':
        from inspection import derive_ledger, describe_packet

        parser = argparse.ArgumentParser(prog='python src/ucl.py inspect')
        parser.add_argument('packet', help='Portable packet to inspect')
        parser.add_argument('--json', action='store_true', help='emit the derived ledger as JSON')
        parser.add_argument('--since', metavar='EARLIER_PACKET', help='compare against an earlier retained packet')
        options = parser.parse_args(args[2:])
        envelope = _core.read_json_file(options.packet, limit=MAX_PORTABLE_JSON)
        packet = decode_portable(envelope)
        previous = None
        if options.since:
            previous = decode_portable(_core.read_json_file(options.since, limit=MAX_PORTABLE_JSON))
        if options.json:
            print(json.dumps(derive_ledger(packet, previous), indent=2))
        else:
            print(describe_packet(packet, portable.label(envelope['format']), previous))
    elif command=='encode' and len(args)==4:
        source=_core.read_json_file(args[2], limit=MAX_PORTABLE_JSON)
        result=encode_portable(source)
        Path(args[3]).write_bytes(portable_json_bytes(result))
        print('VALID ' + portable.label(result['format']), args[3])
    elif command=='decode' and len(args)==4:
        source=_core.read_json_file(args[2], limit=MAX_PORTABLE_JSON)
        result=decode_portable(source)
        Path(args[3]).write_bytes(_core.canon(result))
        print('VALID ' + portable.label(source['format']), args[3])
    elif command=='upgrade' and len(args)==4:
        source, output = map(Path, args[2:])
        envelope = _core.read_json_file(source, limit=MAX_PORTABLE_JSON)
        packet = _core.upgrade_packet(decode_portable(envelope))
        result = encode_portable(packet, formula_roles=envelope.get('formula_roles'))
        _write_handoff(source, output, result)
    elif command=='build' and len(args)==4:
        draft = _core.read_json_file(args[2])
        packet = _core.build(draft, version=_core.draft_version(draft))
        Path(args[3]).write_text(_core.dump_json(packet, pretty=True), encoding='utf-8')
        print(json.dumps(_core.check(packet), indent=2))
    else:
        _core.main(args)

if __name__=='__main__':
    try:main(sys.argv)
    except (ValueError,TypeError,KeyError,UnicodeError,OSError) as e:
        sys.exit('REJECTED: '+str(e))
