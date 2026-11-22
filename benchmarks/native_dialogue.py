#!/usr/bin/env python3
"""Multi-turn, directly model-authored UCL semantics versus English controls.

Each model interprets the last DELIVERED message and authors the next message.
UCL contributions (glyph expressions, acts, ACKs) are authored by the model;
the deterministic tool only assembles/checks the envelope and integrity.
No model-generated content is semantically repaired or converted from English.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl
import native_author as n
from live_radium import parse_json,reserve_upper_bound,price_estimate,safe_text

TURNS=4
FIELDS=n.FIELDS

def messages(fmt,turn,case,sender,state):
    name='P' if case['path']==0 else 'B'
    task=n.task_text(case)
    expected='receipt=null' if state['prior_case'] is None else (
      'receipt must interpret the LAST SUCCESSFULLY DELIVERED message using exactly '
      'action, path, signal_sense, evidence; use the actual previous sender message '
      'and not a potentially false recap')
    prompt=(task+'\nYou are '+sender+' and are responding in a true, consecutive '
            'cross-model dialogue. Return exactly {"receipt":..., "authored":...}. '
            'When receipt is an object, it MUST have exact enum keys/values: '
            'action one of reject/adopt-for-discussion/withhold-judgment/accept; '
            'path INTEGER 0=P or INTEGER 1=B; '
            'signal_sense exactly conceptual-hint or instrument-reading; '
            'evidence exactly none or hypothetical-example. '
            'Never replace enum values with English sentences. '
            'NEVER guess a prior message if one was not delivered. '
            +expected+'. The recipient will not see your instructions or task key. '
            'Your authored component is YOUR OWN new communication, not a transcription '
            'or conversion of an English message. Keep prior definitions unchanged.')
    if fmt=='english':
        prompt+=('\nauthored MUST be a substantive original English string (40-1200 characters). '
                 'No structured target fields in the transmitted string.')
        history='\n'.join(state['history']) if state['history'] else 'No prior authored turns.'
    elif fmt=='structured_english':
        prompt+=('\nauthored MUST be the structured JSON object with exactly '
                 'action, path, signal_sense, evidence, note; make the note original. '
                 'action MUST be exactly one of reject/adopt-for-discussion/withhold-judgment/accept; '
                 'path MUST be integer 0=P or 1=B; '
                 'signal_sense MUST be conceptual-hint or instrument-reading; '
                 'evidence MUST be none or hypothetical-example. '
                 'Never use path="P" or action="reject P".')
        history='\n'.join(state['history']) if state['history'] else 'No prior authored turns.'
    else:
        prior=state['last_act'] or 't8'
        template=n.contrib_template(sender,act_id='t'+str(9+turn),
                                    ack_id='x'+str(5+turn),prior_act=prior)
        prompt+=('\nauthored MUST be an original NATIVE UCL contribution object '
                 'with precise glyph expressions, act, reference and ACK target/action. '
                 'Do NOT write an English draft and ask a tool to translate it. '
                 'No host semantics correction: the tool only assembles exact definitions, '
                 'history and integrity. Match the syntactic template but choose ALL '
                 'of its semantic fields yourself. '
                 'acknowledgements[0].target MUST be exactly '
                 '{"claim":"theory","path":[0]} for P, or {"claim":"theory","path":[1]} for B; '
                 'the path contains an integer, never a string or act object. '
                 'act.expressions MUST contain exactly the same single typed expression '
                 'as explanation and conclusion: "~[P][A]" for P or "~[B][A]" for B. '
                 'acknowledgements[0].action MUST be one of reject/adopt-for-discussion/'
                 'withhold-judgment/accept. Never invent an ext: action. '
                 'Replace all placeholders and keep act ID and ACK ID from the template:\n'
                 +json.dumps(template,sort_keys=True))
        history=('Full prior valid UCL packet:\n'+json.dumps(state['packet'],sort_keys=True,separators=(',',':')))
    if state['failed']:
        prompt+=('\nIMPORTANT: '+str(state['failed'])+' previous turn(s) did not produce '
                 'a deliverable message. Do not invent those missing acts or stances. '
                 'Interpret the LAST SUCCESSFUL message only, or null if none.')
    return [{'role':'system','content':n.SYSTEM},
            {'role':'user','content':prompt+'\nPRIOR CONVERSATION:\n'+history}]

def parse_turn(raw,fmt,require_receipt):
    obj=parse_json(raw)
    if set(obj)!={'receipt','authored'}:raise ValueError('Turn must contain exactly receipt and authored')
    receipt=obj['receipt']
    if require_receipt:
        if not isinstance(receipt,dict) or set(receipt)!=set(FIELDS) or not n.valid_intent(receipt):
            raise ValueError('Missing or invalid previous-message receipt')
    elif receipt is not None:
        raise ValueError('Unsent prior position must have receipt=null')
    if fmt=='english':
        if not isinstance(obj['authored'],str):raise ValueError('English authored must be string')
    else:
        if not isinstance(obj['authored'],dict):raise ValueError('Structured authored must be object')
    return receipt,obj['authored']

def run(client=None,dry_run=False,directions=2,cap=5.0):
    if directions not in (1,2):raise ValueError('directions must be 1 or 2')
    if not 0<cap<=10:raise ValueError('cap must be <=$10 and >0')
    baseline=ucl.load_json(n.BASELINE.read_text(encoding='utf-8'))
    results=[];spent=0.0
    for direction in range(directions):
      for fmt in n.FORMATS:
        state={'packet':baseline,'history':[],'prior_case':None,'last_act':None,'failed':0}
        for turn in range(TURNS):
            case=n.CASES[turn]
            speaker=n.MODELS[(direction+turn)%2]
            msgs=messages(fmt,turn,case,speaker,state)
            reserve=reserve_upper_bound(speaker,msgs,n.MAX_OUTPUT)
            if not dry_run and spent+reserve>cap:
                return summarize(results,spent,'budget_stop','Pre-call reserve exceeds remaining dialogue allocation')
            row={'direction':direction,'format':fmt,'turn':turn,'model':speaker,
                 'case_id':case['id'],'target':{k:case[k] for k in FIELDS},
                 'resumed_after_failure':state['failed']>0,
                 'last_delivered_act':state['last_act'],
                 'prompt_bytes':sum(len(m['content'].encode()) for m in msgs),
                 'prompt':safe_text(msgs[-1]['content'])}
            if dry_run:
                if fmt=='english':
                    authored=('I '+case['action']+' only '+('P' if case['path']==0 else 'B')+
                              '. Signal means '+case['signal_sense']+
                              '; evidence is '+case['evidence']+
                              '. The claim remains hypothetical, not empirically established.')
                elif fmt=='structured_english':
                    authored={**{k:case[k] for k in FIELDS},
                              'note':'I discuss exactly one hypothetical claim without claiming any proven result.'}
                else:
                    obj=n.contrib_template(speaker,act_id='t'+str(9+turn),
                                           ack_id='x'+str(5+turn),
                                           prior_act=state['last_act'] or 't8')
                    prop='P' if case['path']==0 else 'B'
                    obj['act']['expressions']=[f'~[{prop}][A]']
                    obj['explanation']=obj['conclusion']=f'~[{prop}][A]'
                    obj['acknowledgements'][0]['target']['path']=[case['path']]
                    obj['acknowledgements'][0]['action']=case['action']
                    obj['act']['text']=('I '+case['action']+' '+prop+
                                       '. Signal means '+case['signal_sense']+
                                       '; evidence='+case['evidence']+
                                       '. Never empirical proof.')
                    obj['acknowledgements'][0]['note']=obj['act']['text']
                    authored=obj
                raw=json.dumps({'receipt':({k:state['prior_case'][k] for k in FIELDS}
                                            if state['prior_case'] else None),
                                'authored':authored})
                row['usage']={'input':0,'output':0}
                row['finish_reason']='dry_run'
            else:
                try:
                    response=client.chat.completions.create(model=speaker,messages=msgs,
                                                            max_tokens=n.MAX_OUTPUT)
                except Exception as exc:
                    row.update({'valid':False,'failure_type':'api_'+type(exc).__name__})
                    results.append(row)
                    return summarize(results,spent,'api_error','No automatic retries')
                raw=response.choices[0].message.content or ''
                usage=getattr(response,'usage',None)
                pin=getattr(usage,'prompt_tokens',None)
                pout=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(speaker,pin,pout) if pin is not None and pout is not None else reserve
                row['usage']={'input':pin,'output':pout}
                row['finish_reason']=getattr(response.choices[0],'finish_reason',None)
            row['raw_response']=safe_text(raw)
            try:
                receipt,authored=parse_turn(raw,fmt,state['prior_case'] is not None)
                row['receipt']=receipt
                if state['prior_case'] is not None:
                    row['receipt_facets']={k:receipt[k]==state['prior_case'][k] for k in FIELDS}
                    row['receipt_correct']=all(row['receipt_facets'].values())
                else:
                    row['receipt_correct']=None
                    row['receipt_facets']=None
                source=authored if fmt=='english' else json.dumps(authored)
                wire,packet,meta=n.normalise_sender(fmt,source,state['packet'],speaker,
                    act_id='t'+str(9+turn),ack_id='x'+str(5+turn))
                row.update(meta)
                row['valid']=True
                row['handoff']=safe_text(wire)
                row['wire_bytes']=len(wire.encode())
                if fmt=='ucl_native':
                    ack=packet['acknowledgements'][-1]
                    row['author_task_correct']=(ack['action']==case['action'] and
                        ack['target']=={'claim':'theory','path':[case['path']]})
                    state['packet']=packet
                    state['last_act']='t'+str(9+turn)
                elif fmt=='structured_english':
                    row['author_task_correct']=(meta['author_intent']['action']==case['action']
                        and meta['author_intent']['path']==case['path'])
                else:
                    row['author_task_correct']=None
                state['history'].append('Turn '+str(turn)+' '+speaker+': '+wire)
                state['prior_case']=case
                state['failed']=0
            except (ValueError,TypeError,KeyError) as exc:
                row['valid']=False
                row['failure_type']='invalid_authorship_or_receipt'
                row['validation_error']=str(exc)[:180]
                state['failed']+=1
            results.append(row)
    return summarize(results,spent,'dry_run' if dry_run else 'complete')

def summarize(rows,spent,status,reason=None):
    by_format={}
    for fmt in n.FORMATS:
        subset=[r for r in rows if r['format']==fmt]
        scored=[r for r in subset if r.get('receipt_correct') is not None]
        by_format[fmt]={
            'turns':len(subset),'valid_generated_messages':sum(r.get('valid') is True for r in subset),
            'invalid_generated_messages':sum(r.get('valid') is False for r in subset),
            'receipt_correct':sum(r['receipt_correct'] is True for r in scored),
            'receipt_scored':len(scored),
            'resumed_after_failures':sum(bool(r.get('resumed_after_failure')) for r in subset),
            'input_tokens':sum((r.get('usage') or {}).get('input') or 0 for r in subset),
            'output_tokens':sum((r.get('usage') or {}).get('output') or 0 for r in subset)
        }
    out={'status':status,'completed_turns':len(rows),'estimated_cost_usd':round(spent,6),
         'by_format':by_format,'cases':rows,
         'limitations':'Four-turn scripted-intent dialogue with model-authored messages; not fully autonomous choice of position. No semantic repair. English sender prose not independently annotated. Missing turns are disclosed and not invented.'}
    if reason:out['reason']=reason
    return out

if __name__=='__main__':
    import argparse,os
    p=argparse.ArgumentParser()
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--directions',type=int,choices=(1,2),default=2)
    p.add_argument('--cap-usd',type=float,default=5.0)
    p.add_argument('--output',default='native-dialogue-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=120)
    result=run(client,dry_run=a.dry_run,directions=a.directions,cap=a.cap_usd)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('complete','dry_run'):raise SystemExit(2)
