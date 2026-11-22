#!/usr/bin/env python3
"""One manually authorized budget across native UCL one-hop, strict and dialogue tests."""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'benchmarks')]
import native_author as author
import native_dialogue as dialogue

def suite(client=None,dry_run=False,cases=4,directions=2,strict=True,
          multi_turn=True,cap=10.0):
    if not 0<cap<=10:raise ValueError('Total estimated budget must be >0 and <=$10')
    # Reserve ~55% of experiment budget for 1-hop author/receiver + strict
    # full-packet evaluations; remaining allocation goes to longer dialogue.
    # Actual unused first-stage allowance is available to the second stage.
    first_cap=cap*.55 if multi_turn else cap
    first=author.run(client,dry_run=dry_run,cases=cases,directions=directions,
                     strict=strict,cap=first_cap)
    spent=first['estimated_cost_usd']
    second=None
    if multi_turn and first['status']!='api_error':
        available=cap-spent
        if available>0:
            second=dialogue.run(client,dry_run=dry_run,directions=directions,
                                cap=available)
    total=spent+(second['estimated_cost_usd'] if second else 0.0)
    statuses=[first['status']]+([second['status']] if second else [])
    status=('dry_run' if dry_run and all(s=='dry_run' for s in statuses) else
            'complete' if all(s=='complete' for s in statuses) else
            'api_error' if 'api_error' in statuses else 'budget_stop')
    return {'status':status,'total_estimated_cost_usd':round(total,6),
            'per_stage':{'one_hop_and_strict':first,'multi_turn_native_dialogue':second},
            'stage_statuses':statuses,'spending_guard_usd':cap,
            'limitations':'Both stages share the same estimated software cap, not an external billing guarantee. Main native UCL is model-authored semantic structure with deterministic checksum assembly; strict mode tests unassisted complete packet authorship. English sender intent cannot be fairly auto-validated without blinded semantic assessment.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--cases',type=int,choices=(2,4),default=4)
    p.add_argument('--directions',type=int,choices=(1,2),default=2)
    p.add_argument('--strict',choices=('yes','no'),default='yes')
    p.add_argument('--multi-turn',choices=('yes','no'),default='yes')
    p.add_argument('--cap-usd',type=float,default=10.)
    p.add_argument('--output-prefix',default='native-suite')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=author.BASE_URL,
                      max_retries=0,timeout=120)
    result=suite(client,dry_run=a.dry_run,cases=a.cases,directions=a.directions,
                 strict=a.strict=='yes',multi_turn=a.multi_turn=='yes',cap=a.cap_usd)
    prefix=Path(a.output_prefix)
    prefix.parent.mkdir(parents=True,exist_ok=True)
    (prefix.parent/(prefix.name+'-results.json')).write_text(
        json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    summary={k:v for k,v in result.items() if k!='per_stage'}
    summary['stage_summaries']={
        label:({k:v for k,v in stage.items() if k!='cases'} if stage else None)
        for label,stage in result['per_stage'].items()}
    (prefix.parent/(prefix.name+'-summary.json')).write_text(
        json.dumps(summary,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if result['status'] not in ('complete','dry_run'):
        raise SystemExit(2)
    if a.dry_run:
        for stage in result['per_stage'].values():
            if stage and any(x.get('end_to_end_success') is False for x in stage['cases']
                             if 'end_to_end_success' in x):
                raise SystemExit('Dry run deterministic oracle failed')

if __name__=='__main__':main()
