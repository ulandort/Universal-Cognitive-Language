#!/usr/bin/env python3
"""UCL 2.0 development prototype: full portable and pinned compact guide envelopes.

This is NOT UCL/1.0 wire format. Never interpret compact without full pinned local guide.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import ucl

PROFILE = 'UCL-GUIDE-PROFILES/2.0-draft'
GUIDE_DOMAIN = b'UCL-GUIDE-1\n'
WRAPPER_DOMAIN = b'UCL-PROFILE-2\n'

def fingerprint(domain, obj):
    return base64.urlsafe_b64encode(hashlib.sha256(domain + ucl.canon(obj)).digest()).decode().rstrip('=')

def guide_id(guide):
    return fingerprint(GUIDE_DOMAIN, guide)

def checksum(envelope):
    return fingerprint(WRAPPER_DOMAIN, {k:v for k,v in envelope.items() if k != 'checksum'})

def encode(packet, profile='portable', reference_uri=None):
    ucl.check(packet)
    if profile not in ('portable','compact'):
        raise ValueError('Unsupported profile')
    guide = packet['guide']
    payload = copy.deepcopy(packet)
    if profile == 'compact':
        del payload['guide']
    ref = {'version':guide['version'], 'sha256':guide_id(guide)}
    if reference_uri:ref['reference_uri']=reference_uri
    envelope={'format':PROFILE, 'profile':profile, 'guide_ref':ref, 'packet':payload}
    envelope['checksum']=checksum(envelope)
    return envelope

def decode(envelope, local_guide=None):
    if not isinstance(envelope,dict) or set(envelope) != {'format','profile','guide_ref','packet','checksum'}:
        raise ValueError('Invalid guide profile envelope')
    if envelope['format']!=PROFILE or envelope['profile'] not in ('portable','compact'):
        raise ValueError('Unsupported guide profile')
    if envelope['checksum'] != checksum(envelope):
        raise ValueError('Profile checksum mismatch')
    ref=envelope['guide_ref']
    if not isinstance(ref,dict) or set(ref) not in ({'version','sha256'},{'version','sha256','reference_uri'}):
        raise ValueError('Invalid pinned guide reference')
    pkt=copy.deepcopy(envelope['packet'])
    if envelope['profile']=='portable':
        if not isinstance(pkt,dict) or 'guide' not in pkt:
            raise ValueError('Portable profile MUST embed full guide')
        guide=pkt['guide']
    else:
        if not isinstance(pkt,dict) or 'guide' in pkt:
            raise ValueError('Compact profile MUST omit guide')
        if local_guide is None:
            raise ValueError('Matching local guide unavailable; request portable profile')
        guide=local_guide
        pkt['guide']=copy.deepcopy(guide)
    if ref['version'] != guide.get('version') or ref['sha256'] != guide_id(guide):
        raise ValueError('Pinned guide hash/version mismatch')
    ucl.check(pkt)
    return pkt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('encode','decode'))
    p.add_argument('input',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--profile',choices=('portable','compact'),default='portable')
    p.add_argument('--guide',type=Path,help='Local full guide JSON required to decode compact')
    a=p.parse_args()
    source=json.loads(a.input.read_text())
    if a.mode=='encode':
        result=encode(source,a.profile)
    else:
        guide=json.loads(a.guide.read_text()) if a.guide else None
        result=decode(source,guide)
    a.output.write_bytes(ucl.canon(result))
    print(f'{a.mode}: {a.output} ({a.output.stat().st_size} bytes)')
if __name__=='__main__':main()