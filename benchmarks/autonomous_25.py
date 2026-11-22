#!/usr/bin/env python3
"""L25: 25 autonomous, model-authored UCL turns continuing genuine RR-1 output.

Only completed, independently validated self-contained Portable packets are relayed.
No English semantic converter; only deterministic act assembly and hashes.
Never treat a disagreement as a failure. First-attempt and repair results separated.
"""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl,sap_portable,structural_authoring as sap,native_author as n
from author import author
from live_radium import parse_json,safe_text,reserve_upper_bound,price_estimate

OUTPUT=16384
GLYPHS=('C','E','G','K','M','N')
CONCEPT_IDS={
 'C':'uIRR6ai47xbTC6J-HbQroGsTPGn-k14T2Mqi3Ih_x0k',
 'E':'sQy4mWl1jkM6XFSuiPuKxv2b55zabMo4yRyteQtHmo4',
 'G':'CMiyVBXlU_sStNR9xTkxF0aMTNSzzE3J5zheO-wDjME',
 'K':'haKjN_nI06BCSWfPOa7bVTrnI5kZrTbfKD-qci2aI5A',
 'M':'LDgpltoM1WebFUyzX5fMOmbsBby5b2wtScW0SpT25Kw',
 'N':'AbFl-OdjrW5JOWH9KGoMdF0Aosf5yjAxEgEslXnWYc4'}
MAX_WIRE=900000

def load_seed(path):
    env=json.loads(Path(path).read_text(encoding='utf8'))
    pkt=sap_portable.decode(env)
    if len(pkt['discourse']['acts'])!=20 or pkt['discourse']['current']!='t20':
        raise ValueError('L25 expects authentic RR-1 final 20-act packet')
    if any(pkt['definitions'].get(g,{}).get('id')!=d for g,d in CONCEPT_IDS.items()):
        raise ValueError('L25 seed definition identities differ from CG-1 originals')
    return pkt

def ids(state):
    current=len(state['packet']['discourse']['acts'])
    return 't'+str(current+1),'x'+str(len(state['packet']['acknowledgements'])+1)

def prompt(state,turn,speaker):
    act,ack=ids(state)
    prior=state['packet']['discourse']['current']
    example=n.contrib_template(speaker,act,ack,prior)
    every_five=(turn+1)%5==0
    txt=('UCL/2.0 FULL-HISTORY 25-TURN AUTONOMOUS CONTINUATION. '
        'You are '+speaker+'. Continue the *actual* preceding Clarke/Hal conversation '
        'as an independent participant, not as a role-played summary or predetermined '
        'answer. Examine the evolving hypotheses involving invented predicates C,E,G,K,M,N, '
        'their original immutable definitions, and the earlier P/B discussion. '
        'You may agree, disagree, ask for clarification, propose a counterexample, '
        'refine a qualification, identify a logical assumption, or change your own '
        'stance. There is no required agreement, correct philosophical conclusion, '
        'or requirement to invent new concepts. Introduce original relevant reasoning. '
        'Use at least one well-typed existing concept expression and, where warranted, '
        'compound formulas; do not imply a conjunction proves truth or a possible '
        'counterexample is observed data. Preserve ALL prior definitions and acts. '
        'Output EXACTLY one JSON object with keys authored and interpretation. '
        'authored must contain EXACTLY the SAP-1 six fields: act,orientation,'
        'explanation,conclusion,acknowledgements,history_summary. '
        'Use new act ID '+act+', ACK ID '+ack+', act.kind=response, '
        'act.speaker='+speaker+', orientation=L, details.responds_to='+prior+
        ', details.stance=accept|reject|mixed|undetermined. '
        'Keep ACK target scoped to historical claim theory with path [0] or [1], '
        'and make ACK action agree with its own stated meaning. '
        'For first NEW stress turn, interpretation=null. Thereafter '
        'interpretation is a concise, independent summary (at least 20 characters) '
        'of the previous delivered NEW turn, recognizing a legitimate disagreement '
        'as distinct from misunderstanding. Only previous delivered turns count. '
        'Do not add new definitions, claims or unsupported fields; do not invent '
        'new core symbols. The host cannot alter authored semantic content, only '
        'append historical context and calculate hashes. '
        +('RECALL CHECK: In act.text, explicitly relate your current reasoning '
          'to ONE real earlier idea from at least six acts earlier and identify '
          'the historical act ID; do not fabricate a reference or claim that '
          'it was proven. ' if every_five else '')+
        '\nAUTHORING SHAPE (replace every sample semantic field): '+
        json.dumps({'authored':example,'interpretation':None},sort_keys=True)+
        '\nFULL COMPLETE PRIOR SELF-CONTAINED UCL PACKET:\n'+state['wire'])
    return [{'role':'system','content':('Compose precisely valid JSON, independently '
            'authored UCL formulas and honest uncertainty. No Markdown.')},
            {'role':'user','content':txt}]

def validate(raw,state,turn,speaker):
    obj=parse_json(raw)
    if type(obj) is not dict or set(obj)!={'authored','interpretation'}:
        raise ValueError('wrong two-key response schema')
    inter=obj['interpretation']
    if state['delivered_count']==0:
        if inter is not None:raise ValueError('interpretation must be null until first new delivered turn')
    elif type(inter) is not str or len(inter.strip())<20:
        raise ValueError('interpretation must summarize prior delivered turn in >=20 characters')
    c=obj['authored']; act,ack=ids(state)
    sap.check_contribution(c,speaker=speaker,act_id=act,ack_id=ack,
        prior_acts={a['id'] for a in state['packet']['discourse']['acts']},
        claims=state['packet']['claims'])
    if c['act']['details']['responds_to']!=state['packet']['discourse']['current']:
        raise ValueError('must respond to last delivered act')
    if not c['act']['expressions']:
        raise ValueError('must author at least one UCL formula')
    formulas=c['act']['expressions']+[c['explanation'],c['conclusion']]
    if not any('~['+g+'][A]' in f for g in GLYPHS for f in formulas):
        raise ValueError('no invented concept used in formal reasoning')
    if (turn+1)%5==0:
        prior_acts={a['id'] for a in state['packet']['discourse']['acts'][:-6]}
        if not any(ref in prior_acts for ref in c['act']['references']):
            raise ValueError('five-turn checkpoint must reference an act >=6 historical acts earlier')
    pkt=author(state['packet'],c)
    ucl.check(pkt)
    if pkt['definitions']!=state['packet']['definitions']:
        raise ValueError('immutability regression')
    if pkt['discourse']['acts'][:-1]!=state['packet']['discourse']['acts']:
        raise ValueError('history rewriting')
    if len(pkt['acknowledgements'])!=len(state['packet']['acknowledgements'])+1:
        raise ValueError('ACK preservation failure')
    env=sap_portable.encode(pkt)
    assert sap_portable.decode(env)==pkt
    wire=json.dumps(env,sort_keys=True,separators=(',',':'))
    if len(wire.encode())>MAX_WIRE:raise ValueError('packet exceeds predeclared wire growth guard')
    return obj,pkt,wire

def synthetic(state,turn,speaker):
    act,ack=ids(state)
    c=n.contrib_template(speaker,act,ack,state['packet']['discourse']['current'])
    g,h=GLYPHS[turn%6],GLYPHS[(turn+1)%6]
    formula='&[~['+g+'][A]][![~['+h+'][A]]]'
    c['act']['expressions']=[formula]
    c['act']['text']='Hypothetical relationship between distinct, retained concepts; neither the formula nor this illustration constitutes empirical proof.'
    c['explanation']=c['conclusion']=formula
    c['acknowledgements'][0]['target']['path']=[0]
    c['acknowledgements'][0]['action']='adopt-for-discussion'
    c['acknowledgements'][0]['note']='Provisional discussion, not proof'
    if (turn+1)%5==0:c['act']['references']=['t9']
    return json.dumps({'authored':c,'interpretation':None if state['delivered_count']==0 else
        'The preceding speaker considered speculative relationships between original concepts without proof.'})

def summarize(rows,spent,status,reason=None):
    nums=lambda name:sum(r.get(name) is True for r in rows)
    out={'status':status,'scheduled_turns':25,'attempted_turns':len(rows),
         'delivered':nums('valid'),'first_attempt_valid':nums('first_try'),
         'repaired_delivered':nums('repaired'),
         'total_api_attempts':sum(len(r['attempts']) for r in rows),
         'estimated_cost_usd':round(spent,6),
         'first_wire_bytes':rows[0].get('wire_bytes') if rows else None,
         'last_wire_bytes':next((r['wire_bytes'] for r in rows[::-1] if r.get('valid')),None),
         'checkpoint_references_validated':sum(r.get('checkpoint_passed') is True for r in rows),
         'cases':rows,'limitations':('Independent authored reasoning is not proof of truth '
         'or superior comprehension; human review needed. Disagreement is not failure. '
         'Synthetic offline run is not model evidence. Failed repairs, provider errors '
         'and cost overhead reported separately. Provider timeouts may still be billed.')}
    if reason:out['reason']=reason
    return out

def run(seed,client=None,dry_run=False,turns=25,cap=12.,max_repairs=2):
    if turns!=25:raise ValueError('L25 requires exactly 25 turns')
    if max_repairs not in (0,1,2):raise ValueError('repair option invalid')
    if not 0<cap<=25:raise ValueError('cap out of range')
    pkt=load_seed(seed)
    state={'packet':pkt,'wire':json.dumps(sap_portable.encode(pkt),sort_keys=True,separators=(',',':')),
           'delivered_count':0}
    rows=[];spent=0.
    for turn in range(turns):
        speaker=n.MODELS[turn%2]
        base=prompt(state,turn,speaker)
        row={'turn':turn,'speaker':speaker,'attempts':[],
             'prior_packet_bytes':len(state['wire'].encode()),
             'prior_act_count':len(state['packet']['discourse']['acts'])}
        old='';error=''
        for retry in range(max_repairs+1):
            messages=base if retry==0 else base+[
              {'role':'assistant','content':old or '{}'},
              {'role':'user','content':'Your prior candidate was NOT delivered. Exact validation error: '+
               error[:300]+'. Rewrite the entire JSON yourself, retaining your own meaning where possible.'}]
            reserve=reserve_upper_bound(speaker,messages,OUTPUT)
            if not dry_run and spent+reserve>cap:
                row['failure_type']='budget_stop';rows.append(row)
                return summarize(rows,spent,'budget_stop','pre-call estimated reservation exceeds cap')
            a={'retry':retry,'prompt_bytes':sum(len(m['content'].encode()) for m in messages)}
            if dry_run:
                raw=synthetic(state,turn,speaker)
                a['finish_reason']='dry_run';a['usage']={'input':0,'output':0}
            else:
                try:
                    rsp=client.chat.completions.create(model=speaker,messages=messages,max_tokens=OUTPUT)
                except Exception as ex:
                    a.update(failure_type='api_'+type(ex).__name__,provider_charge_unknown=True,
                             error=str(ex)[:200])
                    row['attempts'].append(a);break
                raw=rsp.choices[0].message.content or ''
                pi=getattr(rsp.usage,'prompt_tokens',None)
                po=getattr(rsp.usage,'completion_tokens',None)
                spent+=price_estimate(speaker,pi,po) if pi is not None and po is not None else reserve
                a.update(finish_reason=rsp.choices[0].finish_reason,
                         usage={'input':pi,'output':po})
            a['raw_response']=safe_text(raw)
            try:
                obj,new,wire=validate(raw,state,turn,speaker)
                a['valid']=True;row['attempts'].append(a)
                row.update(valid=True,first_try=retry==0,repaired=retry>0,
                    checkpoint_passed=(turn+1)%5==0,wire_bytes=len(wire.encode()),
                    act_id=new['discourse']['current'],
                    act_text=obj['authored']['act']['text'],
                    interpretation=obj['interpretation'],
                    formulas=obj['authored']['act']['expressions'],
                    handoff=wire)
                state['packet']=new;state['wire']=wire;state['delivered_count']+=1
                break
            except (ValueError,TypeError,KeyError) as ex:
                error=str(ex);old=raw
                a.update(valid=False,failure_type='output_token_exhaustion'
                         if a.get('finish_reason')=='length' else 'validation_or_schema',
                         validation_error=error[:350])
                row['attempts'].append(a)
        if not row.get('valid'):
            row.update(valid=False,failure_type=row['attempts'][-1].get('failure_type','invalid'))
        rows.append(row)
    return summarize(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seed',required=True)
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--turns',type=int,default=25)
    p.add_argument('--max-repairs',type=int,choices=(0,1,2),default=2)
    p.add_argument('--cap-usd',type=float,default=12.)
    p.add_argument('--output',default='l25-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        from openai import OpenAI
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    r=run(a.seed,client,dry_run=a.dry_run,turns=a.turns,cap=a.cap_usd,max_repairs=a.max_repairs)
    Path(a.output).write_text(json.dumps(r,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='cases'},indent=2))
    if r['status'] not in ('dry_run','complete'):raise SystemExit(2)
    if a.dry_run and r['delivered']!=25:raise SystemExit('25-turn offline oracle failed')

if __name__=='__main__':main()
