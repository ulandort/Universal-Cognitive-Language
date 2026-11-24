#!/usr/bin/env python3
"""Optional incremental authoring for UCL/2.0 inner typed packets.
Usage: python tools/author.py existing_packet.txt contribution.json next_packet.txt
Inputs never need to include the previous full discourse. This helper does NOT
silently rewrite earlier definitions, choose a stance, or infer truth.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import ucl

from authoring import author

def main():
    if len(sys.argv)!=4:raise SystemExit('Usage: python tools/author.py prior_packet.txt contribution.json out.txt')
    prior=ucl.load_json(Path(sys.argv[1]).read_text())
    contribution=json.loads(Path(sys.argv[2]).read_text())
    pkt=author(prior,contribution)
    Path(sys.argv[3]).write_text(ucl.dump_json(pkt,pretty=True))
    print('VALID',pkt['integrity']['sha256'])
if __name__=='__main__':main()
