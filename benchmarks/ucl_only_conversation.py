#!/usr/bin/env python3
"""Manually gated UCL-only cross-model native-authoring conversation.

No English or structured-English comparison arms. A model directly authors
symbolic expressions, discourse acts and precise acknowledgements; Python
only assembles immutable UCL history and computes protocol checksums.
Only FULL, independently ucl.check()-validated portable UCL packets are
forwarded. Failed messages are never translated/repaired/fabricated.
"""
import argparse,json,os
from pathlib import Path
import native_author as n
import native_exploration as e

def run(client=None,dry_run=False,turns=8,directions=1,cap=4.0):
    result=e.run(client,dry_run=dry_run,turns=turns,directions=directions,
                 formats=('ucl_native',),cap=cap)
    rows=result['cases']
    sequences=[]
    for direction in range(directions):
        sub=[x for x in rows if x['direction']==direction]
        longest=current=0
        for r in sub:
            if r.get('valid') is True:
                current+=1
                longest=max(longest,current)
            else:current=0
        sequences.append({
            'direction':direction,
            'starting_model':n.MODELS[direction],
            'attempted':len(sub),
            'valid_packets':sum(x.get('valid') is True for x in sub),
            'max_consecutive_valid_packets':longest,
            'receipts_scored':sum(x.get('receipt_correct') is not None for x in sub),
            'receipts_correct':sum(x.get('receipt_correct') is True for x in sub),
            'model_authored_semantics_checked':True,
            'all_delivered_wires_are_valid_portable_ucl':True,
        })
    result['goal']='Can Clarke and Hal sustain a native UCL-only conversation?'
    result['conversations']=sequences
    result['no_english_control_arms']=True
    result['interpretation']='An uninterrupted exchange is a test of reliable native UCL authorship and dialogue, not a claim of empirical proof or superiority over English.'
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--turns',type=int,choices=(2,4,6,8),default=8)
    parser.add_argument('--directions',type=int,choices=(1,2),default=1)
    parser.add_argument('--cap-usd',type=float,default=4.0)
    parser.add_argument('--output',default='ucl-only-live.json')
    a=parser.parse_args()
    if a.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    result=run(client,dry_run=a.dry_run,turns=a.turns,
               directions=a.directions,cap=a.cap_usd)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('dry_run','complete'):raise SystemExit(2)
    if a.dry_run and any(r.get('valid') is not True for r in result['cases']):
        raise SystemExit('Free dry-run protocol oracle failed')

if __name__=='__main__':main()
