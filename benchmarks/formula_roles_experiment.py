#!/usr/bin/env python3
"""Paired optional formula-role UCL/2.0 reading experiment.

Identical validated UCL inner packet in both arms; the ONLY wire difference
is the optional, author-declared role array and its outer checksum. Models
see the whole self-contained JSON packet, not an extracted hint. No API calls
unless a GitHub Actions manual paid_run=yes dispatch selects them.
This tests whether role labels aid role identification, NOT semantic truth,
scientific discovery, or independent correctness of labels.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl
import native_author as n
import sap_portable as portable
from author import author
from live_radium import parse_json, reserve_upper_bound, price_estimate, safe_text

ROLES=tuple(sorted(portable.ROLES))
FIXTURES=(
    ('counterexample',
     'I propose P as one hypothetical possibility; the opposite not-P is a counterexample to taking P for granted, not a second assertion.',
     ['~[P][A]','![~[P][A]]'],['hypothesis','counterexample'],False),
    ('example',
     'As an invented illustration only, suppose P and B happen together; separately I propose P-or-B as another hypothesis, not an observed measurement.',
     ['&[~[P][A]][~[B][A]]','|[~[P][A]][~[B][A]]'],
     ['example','hypothesis'],False),
    ('quotation',
     'A critic is quoted as saying P-or-B; I offer neither-P-nor-B as a counterexample to that proposed requirement, not as an empirical discovery.',
     ['|[~[P][A]][~[B][A]]','&[![~[P][A]]][![~[B][A]]]'],
     ['quotation','counterexample'],False),
    ('two-hypotheses',
     'Two independent hypotheses for joint discussion are P and B. Both are proposals, neither verified as fact; they can be entertained together.',
     ['~[P][A]','~[B][A]'],['hypothesis','hypothesis'],True),
    ('question',
     'The question under discussion is whether B could hold; a separate hypothetical example imagines P without B, solely to test the argument.',
     ['~[B][A]','&[~[P][A]][![~[B][A]]]'],
     ['question','example'],False)
)
SYSTEM=('You are an independent receiver of a self-contained UCL packet. '
        'Read the latest generated act and its formula roles when present; '
        'do not change its original formulas or substitute empirical truth. '
        'Respond with ONLY a JSON object: '
        '{"roles":["hypothesis|example|counterexample|quotation|question",'
        '"hypothesis|example|counterexample|quotation|question"],'
        '"jointly_proposed":true|false}. '
        'Jointly proposed means both expressions are introduced together as '
        'the current speaker\\'s own hypotheses, NOT that either is empirically true. '
        'If role annotations are missing, infer cautiously from the act note. '
        'No commentary.')

def fixture(index):
    label,note,forms,roles,joint=FIXTURES[index]
    base=ucl.load_json(n.BASELINE.read_text(encoding='utf-8'))
    c=n.contrib_template('clarke-1.0','t9','x5','t8')
    c['act']['text']=note
    c['act']['expressions']=forms[:]
    c['explanation']=c['conclusion']=forms[0]
    c['acknowledgements'][0]['target']['path']=[0]
    c['acknowledgements'][0]['action']='adopt-for-discussion'
    c['acknowledgements'][0]['note']='Hypothetical discussion, not empirical evidence'
    c['history_summary']='All original history preserved; t9 added as hypothetical research discussion.'
    packet=author(base,c)
    ucl.check(packet)
    without=portable.encode(packet)
    with_roles=portable.encode(packet,formula_roles=[
        {'act':'t9','index':i,'role':role} for i,role in enumerate(roles)])
    assert portable.decode(without)==portable.decode(with_roles)==packet
    return {'label':label,'gold_roles':roles,'gold_jointly_proposed':joint,
            'without':without,'with':with_roles}

def build_prompt(wire):
    return [{'role':'system','content':SYSTEM},
            {'role':'user','content':('Read the exact UCL Portable message. '
                 'Identify roles for the TWO expressions of final act t9, '
                 'in listed index order. No assumption that listed expressions '
                 'are jointly asserted.\\n'+json.dumps(wire,sort_keys=True,separators=(',',':')))}]

def score(raw,gold):
    x=parse_json(raw)
    if type(x) is not dict or set(x)!={'roles','jointly_proposed'}:
        raise ValueError('Receiver output schema incorrect')
    if (type(x['roles']) is not list or len(x['roles'])!=2 or
        any(type(y) is not str or y not in ROLES for y in x['roles']) or
        type(x['jointly_proposed']) is not bool):
        raise ValueError('Receiver output values incorrect')
    return {'roles':x['roles'],'jointly_proposed':x['jointly_proposed'],
            'exact_roles':x['roles']==gold['gold_roles'],
            'correct_roles':sum(a==b for a,b in zip(x['roles'],gold['gold_roles'])),
            'joint_correct':x['jointly_proposed']==gold['gold_jointly_proposed']}

def summary(rows,spent,status,reason=None):
    by_arm={}
    for arm in ('plain','annotated'):
        selected=[r for r in rows if r['arm']==arm]
        valid=[r for r in selected if 'score' in r]
        by_arm[arm]={'attempted':len(selected),'scored':len(valid),
                     'exact_roles':sum(x['score']['exact_roles'] for x in valid),
                     'role_fields_correct':sum(x['score']['correct_roles'] for x in valid),
                     'joint_correct':sum(x['score']['joint_correct'] for x in valid)}
    out={'status':status,'estimated_cost_usd':round(spent,6),
         'by_arm':by_arm,'rows':rows,
         'limitations':'Synthetic authored role-label oracle, not independent novel thought or verified semantic truth. Models see role annotations and may copy them. All roles are provisional author declarations; report conditioned on successfully scored output. Same underlying UCL packet; different auxiliary role bytes and checksum. Provider timeouts may incur unknown charges.'}
    if reason:out['reason']=reason
    return out

def run(client=None,dry_run=False,cap=4.0,models=('clarke-1.0','hal-1.0')):
    if not 0<cap<=10:raise ValueError('cap must be 0-10')
    if not models or any(m not in n.MODELS for m in models):raise ValueError('models unsupported')
    rows=[];spent=0.
    for index in range(len(FIXTURES)):
      f=fixture(index)
      pbytes=len(ucl.canon(f['without']))
      abytes=len(ucl.canon(f['with']))
      for model in models:
        # Alternate arm order, reducing order/systematic time confounding.
        arms=('plain','annotated') if index%2==0 else ('annotated','plain')
        for arm in arms:
          envelope=f['without' if arm=='plain' else 'with']
          messages=build_prompt(envelope)
          limit=1500
          reserve=reserve_upper_bound(model,messages,limit)
          if not dry_run and spent+reserve>cap:
              return summary(rows,spent,'budget_stop','Pre-request cost estimate exceeded cap')
          row={'case':f['label'],'model':model,'arm':arm,
               'base_bytes':pbytes,'annotated_bytes':abytes,
               'added_bytes':abytes-pbytes,
               'added_percent':round(100*(abytes-pbytes)/pbytes,2),
               'packet_checksum':envelope['packet']['integrity']['sha256'],
               'envelope_checksum':envelope['checksum']}
          if dry_run:
              raw=json.dumps({'roles':f['gold_roles'],
                  'jointly_proposed':f['gold_jointly_proposed']})
              row['usage']={'input':0,'output':0}
          else:
              try:
                  resp=client.chat.completions.create(model=model,messages=messages,
                                                     max_tokens=limit)
                  raw=resp.choices[0].message.content or ''
                  pi=getattr(resp.usage,'prompt_tokens',None)
                  po=getattr(resp.usage,'completion_tokens',None)
                  spent+=price_estimate(model,pi,po) if pi is not None and po is not None else reserve
                  row['usage']={'input':pi,'output':po}
                  row['finish_reason']=getattr(resp.choices[0],'finish_reason',None)
              except Exception as exc:
                  row['error']='provider_'+type(exc).__name__
                  row['provider_charge_unknown']=True
                  rows.append(row)
                  continue
          row['raw_response']=safe_text(raw)
          try:row['score']=score(raw,f)
          except (ValueError,TypeError,KeyError) as exc:row['error']=str(exc)[:180]
          rows.append(row)
    return summary(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--cap-usd',type=float,default=4.0)
    p.add_argument('--output',default='formula-roles-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    out=run(client=client,dry_run=a.dry_run,cap=a.cap_usd)
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
    if out['status'] not in ('complete','dry_run'):raise SystemExit(2)

if __name__=='__main__':main()
