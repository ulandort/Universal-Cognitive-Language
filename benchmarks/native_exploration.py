#!/usr/bin/env python3
"""Exploratory model-chosen UCL / English conversations (no fixed semantic oracle).

Every model independently selects a new claim target, stance, hypothetical-evidence
classification and original argument. Never treat novelty as established truth.
All conclusions retained for blinded qualitative review rather than a validity grade.
"""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import native_author as n
import ucl
from live_radium import parse_json,safe_text,reserve_upper_bound,price_estimate

TURNS=4
FORMATS=n.FORMATS
DIRECTIONS=(0,1)
def make_prompt(fmt,turn,speaker,state):
    prompt=(n.DOMAIN+
      '\nYou are '+speaker+' in an open-ended, four-turn conversation with a separate model. '
      'Explore potentially unexpected distinctions, hypotheses, or implications that '
      'follow from the stipulated meanings of P and B. You may introduce a possible '
      'counterexample, ask a new question, qualify an earlier hypothesis, change your '
      'own stance or propose a different inference. No hypothesis has been empirically '
      'verified. Be creative but logically disciplined: NEVER claim empirical proof, '
      'alter immutable definitions, or imply that a semantic association establishes '
      'causation. Report uncertainty explicitly. '
      'Output ONLY a JSON object with exactly three keys: receipt, intent, authored. '
      'intent is your PRIVATE self-declared intended meaning with EXACT keys '
      'action, path, signal_sense, evidence; choose freely among action = '
      'reject/adopt-for-discussion/withhold-judgment/accept, '
      'path integer 0=P or 1=B, signal_sense = conceptual-hint or instrument-reading, '
      'evidence = none or hypothetical-example. '
      'A hypothetical example is NOT observed measurement. '
      'receipt=null when no prior message was successfully delivered; otherwise '
      'interpret the LAST DELIVERED speaker message using the same four fields, '
      'without seeing their private intent. '
      'The authored message MUST convey what your private intent claims, and '
      'may introduce new theoretical consequences or questions using existing terms. '
      'Do not include your intent JSON in authored prose.')
    if fmt=='english':
        prompt+='\nauthored: original English prose between 40 and 1200 characters, no JSON metadata.'
        history='\n'.join(state['history']) if state['history'] else 'No delivered messages.'
    elif fmt=='structured_english':
        prompt+=('\nauthored: JSON object with exactly action, path, signal_sense, '
                 'evidence, note (20-1200 chars); choose these fields yourself '
                 'and keep them consistent with your private intent.')
        history='\n'.join(state['history']) if state['history'] else 'No delivered messages.'
    else:
        act='t'+str(9+turn);ack='x'+str(5+turn)
        template=n.contrib_template(speaker,act_id=act,ack_id=ack,
                                    prior_act=state['last_act'] or 't8')
        prompt+=('\nauthored: your own NATIVE UCL contribution object, with model-chosen '
                 'well-typed UCL expressions, ACK stance, target path and explanatory note. '
                 'Do NOT generate an English draft for conversion. Python only assembles '
                 'the immutable prior packet and hashes; it does not repair your semantics. '
                 'Valid atomic formulas include "~[P][A]" and "~[B][A]"; negation '
                 '"![~[P][A]]", conjunction, disjunction and other VALID UCL formulas '
                 'may be used when relevant. Uncertainty does not imply empirical truth '
                 'and a question-mark conclusion may require sourced epistemic provenance. '
                 'The model must preserve the original definition of P and B. '
                 'Use exact ACK target {"claim":"theory","path":[0]} for P, or path [1] for B. '
                 'The ACK action must match your private intent and remain an allowed action. '
                 'The act, orientation and formal expression must pass UCL validation. '
                 'Replace all placeholders in this template:\n'
                 +json.dumps(template,sort_keys=True))
        history='Full verified prior UCL packet:\n'+json.dumps(
            state['packet'],sort_keys=True,separators=(',',':'))
    if state['failed']:
        prompt+=('\n'+str(state['failed'])+' previously scheduled message(s) failed '
                 'validation, and were NOT delivered. Interpret only the last real '
                 'message, or use null when there is no last message.')
    return [{'role':'system','content':n.SYSTEM},
            {'role':'user','content':prompt+'\nPRIOR DELIVERED CONTENT:\n'+history}]

def parse_response(raw,fmt,has_previous):
    obj=parse_json(raw)
    if set(obj)!={'receipt','intent','authored'}:raise ValueError('Wrong exploratory reply schema')
    intent=obj['intent']
    if not isinstance(intent,dict) or set(intent)!=set(n.FIELDS) or not n.valid_intent(intent):
        raise ValueError('Invalid private intent')
    receipt=obj['receipt']
    if has_previous:
        if not isinstance(receipt,dict) or set(receipt)!=set(n.FIELDS) or not n.valid_intent(receipt):
            raise ValueError('Invalid prior receipt')
    elif receipt is not None:raise ValueError('No prior delivered message: receipt must be null')
    authored=obj['authored']
    if fmt=='english':
        if not isinstance(authored,str):raise ValueError('English authored must be text')
    else:
        if not isinstance(authored,dict):raise ValueError('Formal authored message must be object')
    return obj

def run(client=None,dry_run=False,cap=4.0,turns=TURNS,directions=2):
    if turns not in (2,4):raise ValueError('turns must be 2 or 4')
    if directions not in (1,2):raise ValueError('directions must be 1 or 2')
    if not 0<cap<=10:raise ValueError('cap must be USD 0-10')
    base=ucl.load_json(n.BASELINE.read_text())
    rows=[];spent=0.
    for direction in range(directions):
      for fmt in FORMATS:
        state={'packet':base,'history':[],'last_intent':None,'last_act':None,'failed':0}
        for turn in range(turns):
            sender=n.MODELS[(turn+direction)%2]
            messages=make_prompt(fmt,turn,sender,state)
            reserve=reserve_upper_bound(sender,messages,n.MAX_OUTPUT)
            if not dry_run and spent+reserve>cap:
                return summary(rows,spent,'budget_stop','Pre-call estimate would exceed cap')
            row={'direction':direction,'turn':turn,'format':fmt,'model':sender,
                 'resumed_after_failure':bool(state['failed']),
                 'prompt_bytes':sum(len(x['content'].encode()) for x in messages),
                 'prompt':safe_text(messages[-1]['content'])}
            if dry_run:
                case=n.CASES[turn]
                intent={k:case[k] for k in n.FIELDS}
                receipt=state['last_intent']
                atom='~[P][A]' if intent['path']==0 else '~[B][A]'
                note=('I '+intent['action']+' '+('P' if intent['path']==0 else 'B')+
                      '. Signal means '+intent['signal_sense']+
                      '. Evidence: '+intent['evidence']+
                      '. One novel possibility is that correlation alone cannot '
                      'distinguish conceptual from measured convergence.')
                if fmt=='english':authored=note
                elif fmt=='structured_english':authored={**intent,'note':note}
                else:
                    authored=n.contrib_template(sender,'t'+str(9+turn),'x'+str(5+turn),
                                                   state['last_act'] or 't8')
                    authored['act']['text']=note
                    authored['act']['expressions']=[atom]
                    authored['explanation']=authored['conclusion']=atom
                    authored['acknowledgements'][0]['target']['path']=[intent['path']]
                    authored['acknowledgements'][0]['action']=intent['action']
                    authored['acknowledgements'][0]['note']=note
                raw=json.dumps({'receipt':receipt,'intent':intent,'authored':authored})
                row['usage']={'input':0,'output':0}
                row['finish_reason']='dry_run'
            else:
                try:
                    result=client.chat.completions.create(model=sender,messages=messages,
                                                          max_tokens=n.MAX_OUTPUT)
                except Exception as exc:
                    row.update({'valid':False,'failure_type':'api_'+type(exc).__name__})
                    rows.append(row)
                    return summary(rows,spent,'api_error','No retries')
                raw=result.choices[0].message.content or ''
                usage=result.usage
                pi=getattr(usage,'prompt_tokens',None);po=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(sender,pi,po) if pi is not None and po is not None else reserve
                row['usage']={'input':pi,'output':po}
                row['finish_reason']=result.choices[0].finish_reason
            row['raw_response']=safe_text(raw)
            try:
                parsed=parse_response(raw,fmt,state['last_intent'] is not None)
                row['intent']=parsed['intent']
                row['receipt']=parsed['receipt']
                if state['last_intent'] is not None:
                    row['receipt_facets']={k:parsed['receipt'][k]==state['last_intent'][k]
                                           for k in n.FIELDS}
                    row['receipt_correct']=all(row['receipt_facets'].values())
                else:
                    row['receipt_correct']=None
                authored=parsed['authored']
                source=authored if fmt=='english' else json.dumps(authored)
                wire,packet,meta=n.normalise_sender(fmt,source,state['packet'],sender,
                    act_id='t'+str(9+turn),ack_id='x'+str(5+turn))
                if fmt=='structured_english':
                    row['self_report_matches_explicit_structure']=all(
                        meta['author_intent'][k]==parsed['intent'][k] for k in n.FIELDS)
                elif fmt=='ucl_native':
                    row['self_report_matches_explicit_structure']=all(
                        meta['author_intent'][k]==parsed['intent'][k] for k in ('action','path'))
                    state['packet']=packet
                    state['last_act']='t'+str(9+turn)
                else:row['self_report_matches_explicit_structure']=None
                row.update(meta)
                row['valid']=True
                row['wire_bytes']=len(wire.encode())
                row['handoff']=safe_text(wire)
                state['history'].append('Turn '+str(turn)+' '+sender+': '+wire)
                state['last_intent']=parsed['intent']
                state['failed']=0
            except (ValueError,TypeError,KeyError) as exc:
                row['valid']=False
                row['failure_type']=n.classify_failure(raw,row.get('finish_reason'),exc)
                row['validation_error']=str(exc)[:180]
                state['failed']+=1
            rows.append(row)
    return summary(rows,spent,'dry_run' if dry_run else 'complete')

def summary(rows,spent,status,reason=None):
    stats={}
    for fmt in FORMATS:
        r=[x for x in rows if x['format']==fmt]
        sc=[x for x in r if x.get('receipt_correct') is not None]
        stats[fmt]={'turns':len(r),'valid_authored':sum(x.get('valid') is True for x in r),
                    'receipts_correct':sum(x['receipt_correct'] is True for x in sc),
                    'receipts_scored':len(sc),
                    'self_report_explicit_structure_matches':sum(
                        x.get('self_report_matches_explicit_structure') is True for x in r),
                    'token_exhaustions':sum(x.get('failure_type')=='output_token_exhaustion' for x in r),
                    'input_tokens':sum((x.get('usage') or {}).get('input') or 0 for x in r),
                    'output_tokens':sum((x.get('usage') or {}).get('output') or 0 for x in r)}
    out={'status':status,'total_estimated_cost_usd':round(spent,6),
         'by_format':stats,'cases':rows,
         'limitations':'Exploratory, not proof of truth or novelty. Models choose hypotheses and positions; no predetermined semantic answer. Private intent is self-reported, not independent truth. Novel inference requires blinded human review, and absence of false empirical claims must be audited. UCL formal structures contain host-calculated checksums only.'}
    if reason:out['reason']=reason
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--turns',type=int,choices=(2,4),default=4)
    p.add_argument('--directions',type=int,choices=(1,2),default=2)
    p.add_argument('--cap-usd',type=float,default=4.)
    p.add_argument('--output',default='exploratory-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=120)
    out=run(client,dry_run=a.dry_run,cap=a.cap_usd,turns=a.turns,
            directions=a.directions)
    Path(a.output).write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    if out['status'] not in ('complete','dry_run'):raise SystemExit(2)
    if a.dry_run and any(not x.get('valid') for x in out['cases']):
        raise SystemExit('Exploratory free deterministic oracle failed')
