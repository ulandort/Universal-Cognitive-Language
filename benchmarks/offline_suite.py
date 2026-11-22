#!/usr/bin/env python3
"""Deterministic offline UCLBench: parser, hashes, references, profiles, corruption.

No AI endpoints, API tokens, or semantic understanding are tested. Exit nonzero on failure.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import random
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
import ucl
import guide_profiles as profiles

EXAMPLE=ROOT/'examples/cross_model_conversation_13_turns.json'

def check_rejects(packet):
    try:ucl.check(packet)
    except (ValueError,TypeError,KeyError):return True
    return False

def execute(seed=2026,iterations=100):
    rand=random.Random(seed)
    baseline=ucl.load_json(EXAMPLE.read_text())
    ucl.check(baseline)
    failures=[]
    passed=0
    cases=0
    def test(label,action):
        nonlocal cases,passed
        cases+=1
        try:
            result=action()
            if result is False:raise AssertionError('false result')
            passed+=1
        except Exception as e:failures.append({'case':label,'error':repr(e)})
    def verify_roundtrip(profile):
        wire=profiles.encode(baseline,profile)
        rec=profiles.decode(wire,baseline['guide'] if profile=='compact' else None)
        assert ucl.canon(rec)==ucl.canon(baseline)
        assert rec['integrity']==baseline['integrity']
        assert rec['definitions']==baseline['definitions']
        assert rec['discourse']==baseline['discourse']
        return True
    test('baseline-valid',lambda: ucl.check(baseline)['status']=='VALID UCL/1.0')
    for mode in ('portable','compact'):
        test('exact-profile-roundtrip-'+mode,lambda m=mode:verify_roundtrip(m))
    wire=profiles.encode(baseline,'compact')
    def no_guide():
        try:profiles.decode(wire)
        except ValueError:return True
        return False
    test('compact-missing-guide-rejected',no_guide)
    def wrong_guide():
        fake=copy.deepcopy(baseline['guide']);fake['grammar']='changed'
        try:profiles.decode(wire,fake)
        except ValueError:return True
        return False
    test('compact-wrong-guide-rejected',wrong_guide)
    def altered_ref():
        modified=copy.deepcopy(wire);modified['guide_ref']['sha256']='not-the-correct-hash';modified['checksum']=profiles.checksum(modified)
        try:profiles.decode(modified,baseline['guide'])
        except ValueError:return True
        return False
    test('compact-tampered-guide-id-rejected',altered_ref)
    def corrupt_wire():
        modified=copy.deepcopy(wire);modified['packet']['discourse']['current']='t1'
        try:profiles.decode(modified,baseline['guide'])
        except ValueError:return True
        return False
    test('compact-corrupt-wrapper-rejected',corrupt_wire)
    for i in range(iterations):
        p=copy.deepcopy(baseline)
        kind=i%6
        if kind==0:
            # Tamper a definition and recalculate packet hash; immutable definition ID must reject it.
            sym=rand.choice(sorted(p['definitions']))
            p['definitions'][sym]['definition']['gloss']+=' altered'
            p['integrity']['sha256']=ucl.packet_id(p)
            test(f'definition-hash-mismatch-{i}',lambda p=p:check_rejects(p))
        elif kind==1:
            # Target missing historic act.
            p['discourse']['acts'][-1]['references']=['nonexistent-'+str(i)]
            p['integrity']['sha256']=ucl.packet_id(p)
            test(f'unknown-act-reference-{i}',lambda p=p:check_rejects(p))
        elif kind==2:
            # Random integrity corruption.
            p['integrity']['sha256']=base64.urlsafe_b64encode(hashlib.sha256(str(i).encode()).digest()).decode().rstrip('=')
            test(f'packet-integrity-mismatch-{i}',lambda p=p:check_rejects(p))
        elif kind==3:
            # A valid packet must remain valid after key-order and whitespace transformations.
            text=json.dumps(p,indent=rand.randint(1,4),sort_keys=bool(rand.randrange(2)),ensure_ascii=True)
            test(f'json-formatting-independence-{i}',lambda text=text:ucl.check(ucl.load_json(text))['status']=='VALID UCL/1.0')
        elif kind==4:
            # Exact tracked claim targeting stays unchanged through portable/compact conversion.
            profile=rand.choice(('portable','compact'))
            test(f'ack-and-claim-preservation-{i}',lambda mode=profile: (
                profiles.decode(profiles.encode(baseline,mode),baseline['guide'] if mode=='compact' else None)['acknowledgements']==baseline['acknowledgements']
                and profiles.decode(profiles.encode(baseline,mode),baseline['guide'] if mode=='compact' else None)['claims']==baseline['claims']))
        else:
            # A fake guide reference must never be accepted as authority by itself.
            modified=copy.deepcopy(wire)
            modified['guide_ref']['reference_uri']='https://example.invalid/another-guide'
            modified['checksum']=profiles.checksum(modified)
            test(f'url-is-not-authority-{i}',lambda modified=modified:ucl.canon(profiles.decode(modified,baseline['guide']))==ucl.canon(baseline))
    source_bytes=len(ucl.canon(baseline))
    sizes={m:len(ucl.canon(profiles.encode(baseline,m))) for m in ('portable','compact')}
    return {'suite':'UCLBench offline development','status':'PASS' if not failures else 'FAIL',
            'seed':seed,'iterations':iterations,'tests':cases,'passed':passed,'failed':len(failures),
            'failures':failures,'canonical_bytes':{'ucl1_packet':source_bytes,**sizes},
            'compact_savings_vs_original_pct':round(100*(1-sizes['compact']/source_bytes),2),
            'note':'Offline structural conformance only; NOT an AI-vs-English performance result.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iterations',type=int,default=100)
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if not 1<=args.iterations<=5000:parser.error('iterations must be 1..5000')
    result=execute(args.seed,args.iterations)
    output=json.dumps(result,indent=2)+'\n'
    if args.out:args.out.write_text(output)
    print(output)
    sys.exit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()