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

def main(args):
    """CLI defaults to recognizing the complete UCL/2.0 Portable format.

    Existing inner-packet commands remain available unchanged, including
    build, canonicalize, and draft, for reproducibility of archived examples.
    """
    if len(args)<3:
        raise ValueError('Usage: python src/ucl.py check file.txt | encode inner.json portable.txt | decode portable.txt inner.json | build/canonicalize/draft ...')
    command=args[1]
    if command=='check' and len(args)==3:
        data=_core.load_json(Path(args[2]).read_text(encoding='utf-8'))
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
        source=_core.load_json(Path(args[2]).read_text(encoding='utf-8'))
        result=decode_portable(source)
        Path(args[3]).write_bytes(_core.canon(result))
        print('VALID UCL/2.0 Portable',args[3])
    else:
        _core.main(args)

if __name__=='__main__':
    try:main(sys.argv)
    except (ValueError,TypeError,KeyError,UnicodeError,OSError) as e:
        sys.exit('REJECTED: '+str(e))
