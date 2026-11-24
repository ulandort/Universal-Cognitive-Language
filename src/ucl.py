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
import re
import sys
from tempfile import NamedTemporaryFile
from pathlib import Path

VERSION='UCL/2.3'
PORTABLE_FORMAT='UCL/2.3-SAP1-PORTABLE'
V22_PORTABLE_FORMAT='UCL/2.2-SAP1-PORTABLE'
V21_PORTABLE_FORMAT='UCL/2.1-SAP1-PORTABLE'
LEGACY_PORTABLE_FORMAT='UCL/2.0-SAP1-PORTABLE'
LONG_DRAFT_FORMAT='UCL/2.2-SAP1-PORTABLE-DRAFT'
ARCHIVE_FORMATS=(PORTABLE_FORMAT, V22_PORTABLE_FORMAT, LONG_DRAFT_FORMAT)
INNER_GRAMMAR_VERSION=_core.RETRACTION_VERSION
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
            'packet':_core.check(packet, archived='archive' in envelope)}

def continue_portable(envelope, contribution):
    """Append an authored draft to a verified Portable envelope."""
    from authoring import author, preflight
    import portable

    parent = decode_portable(envelope)
    archived = 'archive' in envelope
    preflight(parent, contribution, archived=archived)
    packet = author(parent, contribution, archived=archived)
    result = portable.encode(packet, formula_roles=envelope.get('formula_roles'), archived=archived)
    if archived:
        from history_archive import pack
        return pack(result, packet, envelope['archive']['pinned'])
    decode_portable(result)
    return result

def portable_json_bytes(envelope):
    if 'archive' in envelope:
        front = ('format', 'profile', 'archive_guide', 'structural_rules', 'packet')
        order = (*front, *sorted(envelope.keys() - set(front) - {'archive'}), 'archive')
        fields = [_core.canon(key) + b':' + _core.canon(envelope[key]) for key in order]
        data = b'{\n' + b',\n'.join(fields) + b'\n}'
    else:
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


def _read_contribution():
    if sys.stdin.isatty():
        print('Paste the JSON contribution, then press Ctrl-D (Ctrl-Z then Enter on Windows).', file=sys.stderr)
    try:
        return _core.read_json(sys.stdin.buffer)
    except ValueError as exc:
        raise ValueError(f'draft on stdin: {exc}') from exc


def _portable_file(path):
    return _core.read_json_file(path, limit=MAX_PORTABLE_JSON)


def _claim_path(value):
    if value == 'root':
        return []
    if re.fullmatch(r'(?:[0-9]|1[0-5])(?:\.(?:[0-9]|1[0-5])){0,31}', value):
        return [int(index) for index in value.split('.')]
    raise argparse.ArgumentTypeError('use up to 32 dot-separated indices from 0 to 15, or root')


def _continue_cli(args):
    if len(args) != 4:
        raise ValueError('Usage: python src/ucl.py continue incoming.txt next.txt < contribution.json')
    source, output = map(Path, args[2:])
    _write_handoff(source, output, continue_portable(_portable_file(source), _read_contribution()))

def main(args):
    """Dispatch current and archived Portable packets by their version markers."""
    import portable
    if len(args) > 1 and args[1] == 'continue':
        _continue_cli(args)
        return
    if len(args)<3:
        raise ValueError('Usage: python src/ucl.py check | encode | decode | pack | continue | preflight | template | inspect | diff | upgrade | build/canonicalize/draft ...')
    command=args[1]
    if command=='check' and len(args)==3:
        data=_core.read_json_file(args[2], limit=MAX_PORTABLE_JSON)
        if isinstance(data,dict) and isinstance(data.get('format'), str):
            print(json.dumps(check_portable(data),indent=2))
        else:
            print(json.dumps(_core.check(data),indent=2))
    elif command=='preflight' and len(args)==3:
        from authoring import preflight
        envelope = _portable_file(args[2])
        preflight(decode_portable(envelope), _read_contribution(), archived='archive' in envelope)
        print('PREFLIGHT PASSED. Run continue for full validation and handoff.')
    elif command=='template':
        from authoring import reply_template
        parser = argparse.ArgumentParser(prog='python src/ucl.py template')
        parser.add_argument('packet')
        parser.add_argument('--speaker', required=True)
        scope = parser.add_mutually_exclusive_group(required=True)
        scope.add_argument('--claim')
        scope.add_argument('--retract', metavar='ACK_ID', help='retract one of this speaker’s earlier stance ACKs')
        parser.add_argument('--path', type=_claim_path)
        parser.add_argument('--seed-formula', action='store_true',
                            help='copy the selected proposition into explanation and conclusion for editing')
        parser.add_argument('--concept', help='unused alias for a new predicate definition')
        parser.add_argument('--domain', help='existing domain for a unary predicate')
        options = parser.parse_args(args[2:])
        if options.retract is not None and (options.path is not None or options.concept is not None):
            parser.error('--path and --concept require --claim')
        if options.seed_formula and options.claim is None:
            parser.error('--seed-formula requires --claim')
        if options.domain is not None and options.concept is None:
            parser.error('--domain requires --concept')
        draft = reply_template(decode_portable(_portable_file(options.packet)), options.speaker,
                               options.claim, options.path or [], alias=options.concept, domain=options.domain,
                               retract=options.retract, seed_formula=options.seed_formula)
        print(json.dumps(draft, indent=2, ensure_ascii=False))
    elif command=='diff':
        from inspection import compare_packets
        parser = argparse.ArgumentParser(prog='python src/ucl.py diff')
        parser.add_argument('earlier')
        parser.add_argument('later')
        parser.add_argument('--compact', action='store_true', help='summarize changes for a continuation prompt')
        options = parser.parse_args(args[2:])
        delta = compare_packets(decode_portable(_portable_file(options.earlier)),
                                decode_portable(_portable_file(options.later)), compact=options.compact)
        indent = None if options.compact else 2
        print(json.dumps(delta, indent=indent, sort_keys=True))
    elif command=='inspect':
        from inspection import current_state, derive_ledger, describe_packet, focused_context, handoff_briefing

        parser = argparse.ArgumentParser(prog='python src/ucl.py inspect')
        parser.add_argument('packet', help='Portable packet to inspect')
        parser.add_argument('--json', action='store_true', help='emit the derived ledger as JSON')
        parser.add_argument('--since', metavar='EARLIER_PACKET', help='compare against an earlier retained packet')
        scope = parser.add_mutually_exclusive_group()
        scope.add_argument('--act', metavar='ACT_ID', help='read one retained act as a JSON excerpt')
        scope.add_argument('--claim', metavar='CLAIM_ID', help='read one claim and its sources as a JSON excerpt')
        scope.add_argument('--state', action='store_true', help='read a compact state overview as JSON')
        parser.add_argument('--handoff', action='store_true', help='assemble a newcomer briefing as JSON')
        parser.add_argument('--include-act', metavar='ACT_ID', action='append', default=[],
                            help='include an exact act in a newcomer briefing; repeat for more acts')
        parser.add_argument('--path', type=_claim_path, help='exact claim branch, such as 1 or 0.1, or root')
        options = parser.parse_args(args[2:])
        if options.path is not None and options.claim is None:
            parser.error('--path requires --claim')
        if options.include_act and not options.handoff:
            parser.error('--include-act requires --handoff')
        if options.handoff and (options.since or options.act is not None or options.state):
            parser.error('--handoff can be combined with --claim, --path and --include-act')
        if options.since and (options.act is not None or options.claim is not None or options.state):
            parser.error('--since applies to the full ledger. Use diff for a standalone delta.')
        envelope = _portable_file(options.packet)
        if options.handoff:
            selection = dict(claim_id=options.claim, path=options.path, act_ids=options.include_act)
            if 'archive' in envelope:
                from history_archive import inspect_archive_handoff
                briefing = inspect_archive_handoff(envelope, **selection)
            else:
                packet = decode_portable(envelope)
                briefing = handoff_briefing(packet, wire_format=envelope['format'], **selection)
            print(json.dumps(briefing, indent=2))
            return
        if 'archive' in envelope and not options.since:
            from history_archive import inspect_archive
            excerpt = inspect_archive(envelope, act_id=options.act, claim_id=options.claim,
                                      path=options.path, state=options.state)
            print(json.dumps(excerpt, indent=2))
            return
        packet = decode_portable(envelope)
        previous = None
        if options.since:
            previous = decode_portable(_core.read_json_file(options.since, limit=MAX_PORTABLE_JSON))
        if options.act is not None or options.claim is not None:
            print(json.dumps(focused_context(packet, act_id=options.act, claim_id=options.claim, path=options.path), indent=2))
        elif options.state:
            print(json.dumps(current_state(packet), indent=2))
        elif options.json:
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
    elif command=='pack':
        from history_archive import pack
        parser = argparse.ArgumentParser(prog='python src/ucl.py pack')
        parser.add_argument('source', type=Path)
        parser.add_argument('output', type=Path)
        parser.add_argument('--keep-act', action='append', default=[], metavar='ACT_ID')
        options = parser.parse_args(args[2:])
        envelope = _core.read_json_file(options.source, limit=MAX_PORTABLE_JSON)
        packet = decode_portable(envelope)
        pinned = [*envelope.get('archive', {}).get('pinned', []), *options.keep_act]
        expanded = portable.encode(packet, formula_roles=envelope.get('formula_roles'),
                                   archived='archive' in envelope)
        result = pack(expanded, packet, pinned)
        if 'archive' not in result:
            raise ValueError('no eligible unprotected history to archive yet')
        _write_handoff(options.source, options.output, result)
    elif command=='upgrade' and (len(args)==4 or (len(args)==5 and args[4]=='--long-draft')):
        source, output = map(Path, args[2:4])
        envelope = _core.read_json_file(source, limit=MAX_PORTABLE_JSON)
        archived = 'archive' in envelope
        packet = _core.upgrade_packet(decode_portable(envelope), archived=archived)
        result = portable.encode(packet, formula_roles=envelope.get('formula_roles'), archived=archived)
        if archived:
            from history_archive import pack
            result = pack(result, packet, envelope['archive']['pinned'])
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
