#!/usr/bin/env python3
"""Optional compressed TRANSPORT. Never required to read ordinary UCL/1.0 JSON."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import ucl
try:import brotli
except ImportError:raise SystemExit('Optional dependency: pip install brotli')
a=argparse.ArgumentParser();a.add_argument('mode',choices=['compress','decompress']);a.add_argument('source');a.add_argument('destination');x=a.parse_args()
if x.mode=='compress':
    raw=Path(x.source).read_bytes();ucl.load_json(raw.decode('utf-8'));Path(x.destination).write_bytes(brotli.compress(raw))
else:
    raw=Path(x.source).read_bytes()
    if len(raw)>ucl.MAX_COMPRESSED:raise SystemExit('compressed size cap')
    d=brotli.Decompressor();out=bytearray()
    for i in range(0,len(raw),256):
        out.extend(d.process(raw[i:i+256]))
        if len(out)>ucl.MAX_EXPANDED:raise SystemExit('expanded size cap')
    if not d.is_finished():raise SystemExit('truncated compressed data')
    ucl.load_json(out.decode('utf-8'));Path(x.destination).write_bytes(out)
