#!/usr/bin/env python3
"""UCLBench native-authored semantics: controlled sender/recipient handoffs.
Main UCL arm: model authors symbolic UCL contribution, act and ACK natively;
deterministic author() only assembles historical envelope and hashes (no repair).
Separate strict arm requires entire UCL packet including integrity by the model.
No API calls unless explicitly manually dispatched in paid workflow.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl
from author import author
from live_radium import BASE_URL,parse_json,safe_text,reserve_upper_bound,price_estimate

BASELINE=ROOT/'examples/cross_model_conversation_8_turns.json'
FORMATS=('english','structured_english','ucl_native')
MODELS=('clarke-1.0','hal-1.0')
FIELDS=('action','path','signal_sense','evidence')
ACTIONS=('reject','adopt-for-discussion','withhold-judgment','accept')
SENSES=('conceptual-hint','instrument-reading')
EVIDENCE=('none','hypothetical-example')
MAX_OUTPUT=8192
FULL_OUTPUT=16384
CASES=(
    {'id':'ambiguous_signal','action':'reject','path':0,'signal_sense':'conceptual-hint','evidence':'none',
     'challenge':'An unreliable observer has called your conceptual hint an instrument reading. Correct that ambiguity explicitly.'},
    {'id':'false_empirical_proof','action':'adopt-for-discussion','path':1,'signal_sense':'instrument-reading','evidence':'hypothetical-example',
     'challenge':'An observer claims your imagined measurement proves B. Distinguish an invented illustration from observed evidence.'},
    {'id':'old_definition_identity','action':'withhold-judgment','path':0,'signal_sense':'conceptual-hint','evidence':'hypothetical-example',
     'challenge':'A misleading critic calls B the "new P". Reject any silent replacement of original P and preserve the old definition.'},
    {'id':'contradictory_attribution','action':'reject','path':1,'signal_sense':'instrument-reading','evidence':'none',
     'challenge':'A third-party recap says the speaker accepted both P and B, and B was proven. Make your narrowly scoped disagreement unambiguous.'},
)
DOMAIN=('The original theory is the conjunction P AND B about Alpha. '
        'P is a speculative conceptual convergence property. '
        'B is a separate measurable convergence pattern. Neither is empirically established. '
        'An invented example never establishes observed proof. '
        'Keep definition identity fixed; provisional discussion is not verification.')
SYSTEM='Controlled test. Respond in the requested single format, with no Markdown or commentary. Give the final answer immediately.'

def fixture(case_index, direction):
    if type(case_index) is not int or case_index not in range(len(CASES)):raise ValueError('bad case index')
    if direction not in (0,1):raise ValueError('bad direction')
    return CASES[case_index],MODELS[direction],MODELS[1-direction]

def task_text(case):
    label='P' if case['path']==0 else 'B'
    evidence='an imaginary illustrative thought experiment, not a real observation' if case['evidence']=='hypothetical-example' else 'no supporting example'
    sense='a conceptual hint rather than a measurement' if case['signal_sense']=='conceptual-hint' else 'an instrument reading (but not proof that a reading exists)'
    return (DOMAIN+' Your task: communicate ONLY your stance '+case['action']+
            ' on claim '+label+'; do not take a new stance on the other claim. '
            'Use the word "signal" meaning '+sense+'. Offer '+evidence+'. '
            'Make clear that neither claim is proven. '+case['challenge'])

def contrib_template(sender,act_id='t9',ack_id='x5',prior_act='t8'):
    # The writer must fill every semantic field itself; no target/stance
    # is prepopulated with the correct expected answer.
    return {
      'act':{'id':act_id,'kind':'response','speaker':sender,'references':['t1'],
             'text':'WRITE YOUR OWN SUBSTANTIVE UCL ACT NOTE',
             'expressions':['WRITE TYPED UCL PREDICATE e.g. ~[P][A]'],
             'details':{'responds_to':prior_act,'stance':'mixed'}},
      'orientation':'L','explanation':'WRITE UCL EXPRESSION','conclusion':'WRITE UCL EXPRESSION',
      'acknowledgements':[{'id':ack_id,'by':act_id,'target':{'claim':'theory','path':['CHOOSE 0 OR 1']},
                           'action':'CHOOSE VALID ACK ACTION','qualification':None,
                           'replacement':None,'note':'WRITE A PRECISE EXPLANATION'}],
      'history_summary':'All eight original acts retained; native UCL contribution t9 appended.'
    }

def sender_messages(fmt,case,sender,baseline):
    prompt=task_text(case)
    if fmt=='english':
        prompt+='\nWrite ONLY your original natural-language handoff to another AI (80-200 words). No JSON, intent declaration, or key-value labels.'
    elif fmt=='structured_english':
        prompt+='\nWrite a single JSON object with exactly action, path, signal_sense, evidence, note. Use standard values and a substantive original English note (<=1200 characters). No other keys.'
    else:
        prompt+=('\nYou are an independent UCL author, NOT an English-to-UCL converter. '
                 'Produce the next formal contribution as raw JSON matching the template. '
                 'Author your OWN UCL expression(s), precise target claim path and ACK action. '
                 'The host will assemble the immutable original history and compute SHA-256 '
                 'mechanically, but WILL NOT fix or rewrite your semantic fields. '
                 'Treat your note as explanation of your formal act, not the semantic source. '
                 'Do not output a complete checksum-bearing packet in this arm. '
                 'The earlier immutable reference packet is valid; it has claim ID theory with '
                 'path 0=P and path 1=B. Your act ID must be t9 and ACK x5 by t9. '
                 'Only existing glyphs and actions are supported. Exact JSON template:\n'
                 +json.dumps(contrib_template(sender),ensure_ascii=True))
    return [{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]

def normalise_sender(fmt,text,baseline,sender,act_id='t9',ack_id='x5'):
    """Never infer intent from prose or repair a generated semantic object."""
    if fmt=='english':
        if not isinstance(text,str) or not 40<=len(text.strip())<=2200:
            raise ValueError('English length out of range')
        return text.strip(),None,{'author_valid':True,'authoring_mode':'native_english'}
    obj=parse_json(text)
    if fmt=='structured_english':
        if not isinstance(obj,dict) or set(obj)!=set(FIELDS)|{'note'}:
            raise ValueError('Structured fields invalid')
        if not valid_intent(obj):raise ValueError('Structured values invalid')
        if not isinstance(obj['note'],str) or not 20<=len(obj['note'])<=1200:
            raise ValueError('Bad note')
        return json.dumps(obj,sort_keys=True,separators=(',',':')),None,{
            'author_valid':True,'authoring_mode':'native_structured',
            'author_intent':{k:obj[k] for k in FIELDS}}
    # The model writes ALL symbolic/semantic fields. The authoring tool merely
    # adds deterministic inherited history, guide, symbol declarations and hashes.
    if not isinstance(obj,dict) or set(obj)!={
        'act','orientation','explanation','conclusion','acknowledgements','history_summary'
    }:raise ValueError('Native contribution fields invalid')
    act=obj['act']
    if not isinstance(act,dict) or set(act)!={'id','kind','speaker','references','text','expressions','details'}:
        raise ValueError('Native act fields invalid')
    if act['id']!=act_id or act['speaker']!=sender or act['kind']!='response':
        raise ValueError('Wrong identity or act kind')
    if not isinstance(act['text'],str) or not 20<=len(act['text'])<=1200:
        raise ValueError('Bad native act text')
    if not isinstance(act['expressions'],list) or not act['expressions']:
        raise ValueError('No native symbolic expression')
    acks=obj['acknowledgements']
    if not isinstance(acks,list) or len(acks)!=1:raise ValueError('One scoped ACK required')
    ack=acks[0]
    if not isinstance(ack,dict) or ack.get('by')!=act_id or ack.get('id')!=ack_id:
        raise ValueError('Missing native ACK')
    target=ack.get('target')
    if not isinstance(target,dict) or target.get('claim')!='theory' or type(target.get('path')) is not list or len(target['path'])!=1 or type(target['path'][0]) is not int or target['path'][0] not in (0,1):
        raise ValueError('Incorrect ACK target shape')
    path=target['path'][0]
    expression=f'~[{"P" if path==0 else "B"}][A]'
    if (act['expressions']!=[expression] or obj['explanation']!=expression or
        obj['conclusion']!=expression or obj['orientation']!='L'):
        raise ValueError('Symbolic expression does not align with the ACK target')
    # No invented claim equality or proof: the receiver must infer meaning from
    # model-authored ACK and prose. The host does not rewrite semantic content.
    packet=author(baseline,obj)
    ucl.check(packet)
    from guide_profiles import encode
    wire=json.dumps(encode(packet,'portable'),ensure_ascii=True,separators=(',',':'),sort_keys=True)
    return wire,packet,{'author_valid':True,'authoring_mode':'native_ucl_delta',
                        'author_intent':{'action':ack['action'],'path':path},
                        'packet_sha256':packet['integrity']['sha256']}

def valid_intent(obj):
    return (obj.get('action') in ACTIONS and type(obj.get('path')) is int
            and obj['path'] in (0,1) and obj.get('signal_sense') in SENSES
            and obj.get('evidence') in EVIDENCE)

def recipient_messages(fmt,wire):
    prompt=(DOMAIN+'\nA different AI authored the following message. '
            'Without relying on third-party claims, determine the SENDER\'S latest intended '
            'stance and exact referenced claim. Also infer the meaning of their word "signal" '
            'and whether they offered only an invented illustration or no supporting example. '
            'Reply with exactly one JSON object with four fields: '
            '{"action":"reject|adopt-for-discussion|withhold-judgment|accept",'
            '"path":0,"signal_sense":"conceptual-hint|instrument-reading",'
            '"evidence":"none|hypothetical-example"}. '
            'Do not infer empirical proof from a hypothetical example. '
            'Use the latest t9 ACK and act for UCL, not earlier historical stances. '
            'No explanation.\nMESSAGE:\n'+wire)
    return [{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]

def judge_receiver(text,case):
    try:
        obj=parse_json(text)
        if set(obj)!=set(FIELDS) or not valid_intent(obj):return {'valid':False,'correct':False,'facets':{}}
        facets={k:obj[k]==case[k] for k in FIELDS}
        return {'valid':True,'correct':all(facets.values()),'facets':facets,'interpreted':obj}
    except (ValueError,KeyError,TypeError):
        return {'valid':False,'correct':False,'facets':{}}

def strict_messages(case,sender,baseline):
    return [{'role':'system','content':SYSTEM},
            {'role':'user','content':task_text(case)+
            '\nSTRICT INDEPENDENT UCL AUTHORING CHALLENGE: output ONLY a complete, fully valid '
            'UCL/1.0 JSON packet, directly authored by you. Preserve all eight original acts, '
            'immutable definitions, guide, claims, and history; add one original t9 response by '
            +sender+' with a correctly scoped ACK x5 to the stipulated claim component. '
            'Compute every required packet integrity field and exact symbol declaration yourself. '
            'No repair, rewriting or checksum assistance is provided. This strict challenge '
            'is scored independently of the three main comparison arms.\nREFERENCE:\n'
            +json.dumps(baseline,sort_keys=True,separators=(',',':'))}]

def strict_grade(text,case,baseline,sender):
    try:
        obj=parse_json(text)
        ucl.check(obj)
        old=baseline['discourse']['acts']
        acts=obj['discourse']['acts']
        if len(acts)!=len(old)+1 or acts[:len(old)]!=old:raise ValueError('History altered')
        if obj['definitions']!=baseline['definitions']:raise ValueError('Definition altered')
        if obj['guide']!=baseline['guide']:raise ValueError('Guide altered')
        if obj['claims']!=baseline['claims']:raise ValueError('Original claim altered')
        a=acts[-1]
        if a['id']!='t9' or a['speaker']!=sender:raise ValueError('Wrong native author identity')
        matches=[x for x in obj['acknowledgements'] if x.get('by')=='t9']
        if len(matches)!=1:raise ValueError('Missing/extra t9 ACK')
        ack=matches[0]
        if (ack['action']!=case['action'] or
            ack['target']!={'claim':'theory','path':[case['path']]}):
            raise ValueError('Wrong author stance/target')
        return {'valid':True,'task_correct':True,'reason':'validated'}
    except (ValueError,TypeError,KeyError) as exc:
        return {'valid':False,'task_correct':False,'reason':str(exc)[:160]}

def layout(cases=4,directions=2,strict=True):
    if type(cases) is not int or cases not in (2,4):raise ValueError('cases must be 2 or 4')
    if type(directions) is not int or directions not in (1,2):raise ValueError('directions must be 1 or 2')
    tasks=[(i,d,f) for i in range(cases) for d in range(directions) for f in FORMATS]
    if strict:
        tasks +=[(0,d,'ucl_strict_full') for d in range(directions)]
    return tasks

def summarize(rows,cost,status,reason=None):
    by_format={}
    for fmt in (*FORMATS,'ucl_strict_full'):
        group=[r for r in rows if r['format']==fmt]
        by_format[fmt]={
            'tasks':len(group),
            'authors_valid':sum(r.get('author_valid') is True for r in group),
            'author_task_correct':sum(r.get('author_task_correct') is True for r in group),
            'receivers_correct':sum(r.get('receiver_correct') is True for r in group),
            'receivers_scored':sum(r.get('receiver_scored') is True for r in group),
            'end_to_end_success':sum(r.get('end_to_end_success') is True for r in group),
            'input_tokens':sum((r.get(k) or {}).get('input') or 0 for r in group for k in ('sender_usage','receiver_usage')),
            'output_tokens':sum((r.get(k) or {}).get('output') or 0 for r in group for k in ('sender_usage','receiver_usage')),
        }
    obj={'status':status,'completed_tasks':len(rows),'estimated_cost_usd':round(cost,6),
         'by_format':by_format,'cases':rows,
         'limitations':'No blinding of the format; fixed seeded tasks and small sample. English sender intent is not automatically independently annotated, so receiver disagreement may reflect author omission. Native UCL delta is model-authored semantic structure but tool-assembled checksums; strict full UCL tests no-tools complete packet generation separately. Compare end-to-end validity and token cost, not just conditional receiver accuracy.'}
    if reason:obj['reason']=reason
    return obj

def run(client=None,dry_run=False,cases=4,directions=2,strict=True,cap=10.0):
    tasks=layout(cases,directions,strict)
    if not 0<cap<=10:raise ValueError('cap must be 0 < cap <= $10')
    baseline=ucl.load_json(BASELINE.read_text(encoding='utf-8'))
    rows=[];cost=0.0
    for ci,d,fmt in tasks:
        case,sender,receiver=fixture(ci,d)
        row={'case_id':case['id'],'case_index':ci,'direction':d,'format':fmt,
             'sender':sender,'receiver':receiver,'target':{k:case[k] for k in FIELDS}}
        full=(fmt=='ucl_strict_full')
        messages=strict_messages(case,sender,baseline) if full else sender_messages(fmt,case,sender,baseline)
        outlim=FULL_OUTPUT if full else MAX_OUTPUT
        reserve=reserve_upper_bound(sender,messages,outlim)
        if not dry_run and cost+reserve>cap:
            return summarize(rows,cost,'budget_stop','sender pre-call reservation would exceed cap')
        if dry_run:
            if full:
                draft=ucl.draft_from_packet(baseline)
                packet=author(baseline,{
                    'act':{'id':'t9','kind':'response','speaker':sender,'references':['t1'],
                           'text':'I discuss only one hypothesized component, never proven.',
                           'expressions':[f'~[{"P" if case["path"]==0 else "B"}][A]'],
                           'details':{'responds_to':'t8','stance':'mixed'}},
                    'orientation':'L','explanation':f'~[{"P" if case["path"]==0 else "B"}][A]',
                    'conclusion':f'~[{"P" if case["path"]==0 else "B"}][A]',
                    'acknowledgements':[{'id':'x5','by':'t9','target':{'claim':'theory','path':[case['path']]},
                                         'action':case['action'],'qualification':None,'replacement':None,
                                         'note':'The claim is only hypothetical.'}],
                    'history_summary':'All original acts retained.'})
                reply=json.dumps(packet)
            elif fmt=='english':
                reply=('I '+case['action']+' only '+('P' if case['path']==0 else 'B')+
                       '. By signal I mean '+case['signal_sense']+
                       '. Evidence is '+case['evidence']+'. This is not empirical proof.')
            elif fmt=='structured_english':
                reply=json.dumps({**{k:case[k] for k in FIELDS},
                                  'note':'This is explicitly hypothetical and never confirmed by measurement.'})
            else:
                prop='P' if case['path']==0 else 'B'
                obj=contrib_template(sender)
                obj['act']['text']='I '+case['action']+' only '+prop+'. Signal means '+case['signal_sense']+'. Evidence is '+case['evidence']+'.'
                obj['act']['expressions']=[f'~[{prop}][A]']
                obj['explanation']=f'~[{prop}][A]'
                obj['conclusion']=f'~[{prop}][A]'
                obj['acknowledgements'][0]['target']['path']=[case['path']]
                obj['acknowledgements'][0]['action']=case['action']
                obj['acknowledgements'][0]['note']=obj['act']['text']
                reply=json.dumps(obj)
            row['sender_usage']={'input':0,'output':0}
            row['sender_finish_reason']='dry_run'
        else:
            try:
                resp=client.chat.completions.create(model=sender,messages=messages,max_tokens=outlim)
            except Exception as exc:
                row.update({'author_valid':False,'failure_type':'sender_api_'+type(exc).__name__})
                rows.append(row)
                return summarize(rows,cost,'api_error','No automatic retries')
            reply=resp.choices[0].message.content or ''
            usage=resp.usage
            pin=getattr(usage,'prompt_tokens',None);pout=getattr(usage,'completion_tokens',None)
            cost+=price_estimate(sender,pin,pout) if pin is not None and pout is not None else reserve
            row['sender_usage']={'input':pin,'output':pout}
            row['sender_finish_reason']=getattr(resp.choices[0],'finish_reason',None)
        row['sender_response']=safe_text(reply)
        if full:
            grade=strict_grade(reply,case,baseline,sender)
            row['author_valid']=grade['valid']
            row['author_task_correct']=grade['task_correct']
            row['failure_type']=None if grade['valid'] else grade['reason']
            row['end_to_end_success']=grade['task_correct']
            rows.append(row)
            continue
        try:
            wire,packet,meta=normalise_sender(fmt,reply,baseline,sender)
            row.update(meta)
            if fmt=='ucl_native':
                ack=packet['acknowledgements'][-1]
                row['author_task_correct']=(ack['action']==case['action'] and
                    ack['target']=={'claim':'theory','path':[case['path']]})
            elif fmt=='structured_english':
                row['author_task_correct']=(meta['author_intent']['action']==case['action'] and
                                            meta['author_intent']['path']==case['path'])
            else:
                row['author_task_correct']=None
        except (ValueError,TypeError,KeyError) as exc:
            row['author_valid']=False
            row['author_task_correct']=False if fmt!='english' else None
            row['failure_type']='author_'+type(exc).__name__
            row['validation_error']=str(exc)[:180]
            row['end_to_end_success']=False
            rows.append(row)
            continue
        row['wire_bytes']=len(wire.encode())
        row['handoff']=safe_text(wire)
        messages=recipient_messages(fmt,wire)
        reserve=reserve_upper_bound(receiver,messages,MAX_OUTPUT)
        if not dry_run and cost+reserve>cap:
            row['receiver_skipped']='budget_stop'
            rows.append(row)
            return summarize(rows,cost,'budget_stop','receiver pre-call reservation would exceed cap')
        if dry_run:
            rtext=json.dumps({k:case[k] for k in FIELDS})
            row['receiver_usage']={'input':0,'output':0}
        else:
            try:
                resp=client.chat.completions.create(model=receiver,messages=messages,max_tokens=MAX_OUTPUT)
            except Exception as exc:
                row['failure_type']='receiver_api_'+type(exc).__name__
                rows.append(row)
                return summarize(rows,cost,'api_error','No automatic retries')
            rtext=resp.choices[0].message.content or ''
            usage=resp.usage
            pin=getattr(usage,'prompt_tokens',None);pout=getattr(usage,'completion_tokens',None)
            cost+=price_estimate(receiver,pin,pout) if pin is not None and pout is not None else reserve
            row['receiver_usage']={'input':pin,'output':pout}
            row['receiver_finish_reason']=getattr(resp.choices[0],'finish_reason',None)
        row['receiver_response']=safe_text(rtext)
        grade=judge_receiver(rtext,case)
        row['receiver_scored']=grade['valid']
        row['receiver_correct']=grade['correct']
        row['receiver_facets']=grade['facets']
        row['receiver_interpreted']=grade.get('interpreted')
        row['end_to_end_success']=(row['author_valid'] and grade['correct'] and
                                 row.get('author_task_correct') is not False)
        rows.append(row)
    return summarize(rows,cost,'dry_run' if dry_run else 'complete')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--cases',type=int,choices=(2,4),default=4)
    p.add_argument('--directions',type=int,choices=(1,2),default=2)
    p.add_argument('--strict',choices=('yes','no'),default='yes')
    p.add_argument('--cap-usd',type=float,default=10.0)
    p.add_argument('--output',default='native-author-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=120)
    result=run(client,dry_run=a.dry_run,cases=a.cases,directions=a.directions,
               strict=a.strict=='yes',cap=a.cap_usd)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('complete','dry_run'):raise SystemExit(2)
    if a.dry_run and any(x.get('end_to_end_success') is not True for x in result['cases']):
        raise SystemExit('Dry-run oracle failed')

if __name__=='__main__':main()
