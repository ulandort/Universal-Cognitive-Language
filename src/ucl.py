#!/usr/bin/env python3
"""UCL/2.0 public API and CLI.

The validated inner glyph grammar remains in core.py, while the complete
self-contained UCL/2.0 Portable wire lives in portable.py. This entry point
exposes both without altering glyph semantics, canonical hashes, or packets.
"""
from __future__ import annotations
from core import *  # Preserve existing public typed-grammar API exactly.
import core as _core
import json
import sys
from tempfile import NamedTemporaryFile
from pathlib import Path

VERSION='UCL/2.0'
PORTABLE_FORMAT='UCL/2.0-SAP1-PORTABLE'
INNER_GRAMMAR_VERSION=_core.VERSION

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
    return {'status':'VALID UCL/2.0 Portable',
            'format':portable.FORMAT,
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

def _continue_cli(args):
    if len(args) != 4:
        raise ValueError('Usage: python src/ucl.py continue incoming.txt next.txt < contribution.json')
    source, output = map(Path, args[2:])
    if source.resolve() == output.resolve() or (output.exists() and source.samefile(output)):
        raise ValueError('choose a different output file to preserve the incoming packet')
    envelope = json.loads(source.read_text(encoding='utf-8'))
    if sys.stdin.isatty():
        print('Paste the JSON contribution, then press Ctrl-D (Ctrl-Z then Enter on Windows).', file=sys.stderr)
    try:
        contribution = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise ValueError(f'draft on stdin: {exc}') from exc
    result = continue_portable(envelope, contribution)
    with NamedTemporaryFile(dir=output.parent, delete=False) as temp:
        staged = Path(temp.name)
        try:
            temp.write(_core.canon(result))
            temp.close()
            staged.replace(output)
        finally:
            staged.unlink(missing_ok=True)
    print('VALID UCL/2.0 Portable', output)

def main(args):
    """CLI defaults to recognizing the complete UCL/2.0 Portable format.

    Existing inner-packet commands remain available unchanged, including
    build, canonicalize, and draft, for reproducibility of archived examples.
    """
    if len(args) > 1 and args[1] == 'continue':
        _continue_cli(args)
        return
    if len(args)<3:
        raise ValueError('Usage: python src/ucl.py check file.txt | encode inner.json portable.txt | decode portable.txt inner.json | continue incoming.txt next.txt < contribution.json | build/canonicalize/draft ...')
    command=args[1]
    if command=='check' and len(args)==3:
        data=json.loads(Path(args[2]).read_text(encoding='utf-8'))
        if isinstance(data,dict) and data.get('format')==PORTABLE_FORMAT:
            print(json.dumps(check_portable(data),indent=2))
        else:
            _core.main(args)
    elif command=='encode' and len(args)==4:
        source=_core.load_json(Path(args[2]).read_text(encoding='utf-8'))
        result=encode_portable(source)
        Path(args[3]).write_bytes(_core.canon(result))
        print('VALID UCL/2.0 Portable',args[3])
    elif command=='decode' and len(args)==4:
        source=json.loads(Path(args[2]).read_text(encoding='utf-8'))
        result=decode_portable(source)
        Path(args[3]).write_bytes(_core.canon(result))
        print('VALID UCL/2.0 Portable',args[3])
    else:
        _core.main(args)

if __name__=='__main__':
    try:main(sys.argv)
    except (ValueError,TypeError,KeyError,UnicodeError,OSError) as e:
        sys.exit('REJECTED: '+str(e))
