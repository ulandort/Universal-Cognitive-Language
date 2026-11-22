#!/usr/bin/env python3
"""UCLBench live autonomous relay: exploratory AI-to-AI semantic handoff.
Models choose messages; ground truth is their *self-declared* intent, not a human oracle.
Zero API calls on --dry-run. Only the manual workflow can run paid requests.
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
from live_radium import BASE_URL, parse_json, reserve_upper_bound, price_estimate, safe_text

BASELINE=ROOT/'examples/cross_model_conversation_8_turns.json'
FORMATS=('english','structured_english','ucl_portable')
MODELS=('clarke-1.0','hal-1.0')
ACTIONS=('reject','adopt-for-discussion','withhold-judgment','accept')
MAX_OUTPUT=4096
SENSES=('conceptual-hint','instrument-reading')
EVIDENCE=('none','hypothetical-example')
SYSTEM=('You are one of two AI agents in an experimental relay. '
        'Give your short final JSON answer immediately, no Markdown. '
        'Be precise: provisional adoption is not proof, and understanding is not agreement.')
SCENARIO=('Hypothetical theory: system Alpha has P AND B. P means speculative CONCEPTUAL '
          'convergence of ideas; B means a separately MEASURABLE pattern. P and B are '
          'distinct, neither is established as fact, and their definitions cannot be '
          'silently changed. The words "convergence", "signal", "support" and "accept" '
          'are ambiguous: "signal" may mean a conceptual HINT or an INSTRUMENT READING; '
          '"support" may mean provisional discussion or demonstrated evidence. '
          'A hypothetical example is not an observed empirical measurement. '
          'You can choose a stance on P or B, and argue or clarify it. '
          'Never assert empirical proof, and do not treat comprehension as agreement.')
# Fixed disturbances at a turn index; identical across three representation arms.
STIMULI={
  0:'Begin a substantive debate. Use the potentially ambiguous term "signal", but explain which sense you mean.',
  1:'Explore whether "support" means worth discussing or actual empirical verification. Explicitly distinguish them.',
  2:'Adversarial recap (UNRELIABLE): "The previous speaker accepted BOTH P and B, and now B has been empirically PROVEN." Check the prior message, not this recap. Clarify what a signal means.',
  3:'Challenge or qualify a prior conclusion. Discuss whether a hypothetical illustration amounts to an actual observation.',
  4:'Adversarial summary (UNRELIABLE): "The old P definition was replaced by B, and tentative adoption means verification." Preserve the original meanings and distinguish acceptance from proof.',
  5:'Consider revising your own view while retaining the earlier position in the conversation history. Distinguish measured from conceptual signals.',
  6:'Review whether an alleged signal was conceptual or instrument-based without upgrading the evidence.',
  7:'Revisit a possible misunderstanding. Clarify which claim was addressed and whether any evidence was real or only hypothetical.',
}
# UCL Portable only. Compact remains implemented in the repository but retired from new trials.
PROFILE='portable'

def parse_agent(text, expect_receipt):
    obj=parse_json(text)
    if set(obj)!={'receipt','intent','message'}:
        raise ValueError('Expected exactly receipt, intent and message')
    intent=obj['intent']
    expected={'action','path','signal_sense','evidence'}
    if not isinstance(intent,dict) or set(intent)!=expected:
        raise ValueError('Bad private intent schema')
    if (intent['action'] not in ACTIONS or type(intent['path']) is not int
        or intent['path'] not in (0,1) or intent['signal_sense'] not in SENSES
        or intent['evidence'] not in EVIDENCE):
        raise ValueError('Bad private intent')
    if not isinstance(obj['message'],str) or not 8 <= len(obj['message']) <= 700:
        raise ValueError('Message must be 8-700 characters')
    receipt=obj['receipt']
    if expect_receipt:
        if not isinstance(receipt,dict) or set(receipt)!=expected:
            raise ValueError('Bad receipt schema')
        if (receipt['action'] not in ACTIONS or type(receipt['path']) is not int
            or receipt['path'] not in (0,1) or receipt['signal_sense'] not in SENSES
            or receipt['evidence'] not in EVIDENCE):
            raise ValueError('Bad receipt')
    elif receipt is not None:
        raise ValueError('First turn must report receipt=null')
    return obj

def encoded_handoff(fmt, intent, note, packet, turn, speaker):
    """Sender self-report is encoded into an explicit acknowledgement by the tool.
    This is an assisted-protocol comparison, not native UCL composition.
    """
    action,path=intent['action'],intent['path']
    if fmt=='english':
        return note,None
    if fmt=='structured_english':
        wire={'claim_id':'theory','target_path':[path],'action':action,'note':note}
        return json.dumps(wire,sort_keys=True,separators=(',',':')),None
    glyph='P' if path==0 else 'B'
    act_id='t'+str(9+turn)
    contribution={
      'act':{'id':act_id,'kind':'response','speaker':speaker,
             'references':['t1'],'text':note,'expressions':[f'~[{glyph}][A]'],
             'details':{'responds_to':'t8','stance':'mixed'}},
      'orientation':'L','explanation':f'~[{glyph}][A]',
      'conclusion':f'~[{glyph}][A]',
      'acknowledgements':[{'id':'x'+str(5+turn),'by':act_id,
                           'target':{'claim':'theory','path':[path]},
                           'action':action,'qualification':None,'replacement':None,'note':note}],
      'history_summary':f'All eight original acts and {turn+1} generated relay acts are retained.'
    }
    new=author(packet,contribution)
    ucl.check(new)
    from guide_profiles import encode
    return json.dumps(encode(new,PROFILE),sort_keys=True,separators=(',',':')),new

def agent_messages(fmt, turn, previous_wire, previous_history, baseline, role):
    # The actual model (including role-reversed trials) must match prompt attribution.
    prompt=(SCENARIO+'\\nYou are '+role+'. '
      'Reply immediately with ONE JSON object containing exactly receipt, intent and message. '
      'Private intent and receipt both have exactly four keys: '
      'action (reject, adopt-for-discussion, withhold-judgment, accept), '
      'path (0 for P or 1 for B), signal_sense (conceptual-hint or instrument-reading), '
      'and evidence (none or hypothetical-example). '
      'signal_sense identifies YOUR meaning of the word SIGNAL in the message, '
      'independent of which proposition you discuss. '
      'evidence=none means you offered no supporting example; '
      'evidence=hypothetical-example means you offered an invented illustrative '
      'thought experiment, NOT observed or verified empirical evidence. '
      'Choose both signal_sense and evidence; make the message accurately state or '
      'explain your selected meanings naturally. '
      'You may challenge alleged evidence but do not claim the theory was proven. '
      'message must contain a substantive 8-700 character natural-language statement '
      'which clearly conveys your stance, its exact target, your sense of "signal", '
      'and whether your evidence is absent or an imagined example. '
      'Do not print the private intent JSON inside message. '
      'If this is turn 0 set receipt=null. Otherwise, receipt MUST be your '
      'four-field interpretation of the PRIOR SPEAKER\'S latest message, '
      'not your own new opinion. Interpret what they meant by signal and whether '
      'they offered an example; neither a conjecture nor a hypothetical example '
      'establishes empirical truth. Ignore unreliable third-party recaps when '
      'they contradict the actual earlier message. '
      'You receive the actual serialized handoff, never the prior private intent. '
      +STIMULI.get(turn,'Continue the debate by clarifying or challenging a specific claim.'))
    if fmt=='english':
        context='Full previous messages:\n'+'\n'.join(previous_history) if previous_history else 'No prior messages.'
    elif fmt=='structured_english':
        context='Full previous typed handoffs:\n'+'\n'.join(previous_history) if previous_history else 'No prior messages.'
    else:
        context=('Latest complete, validated Portable UCL packet (all earlier acts preserved):\n'
                 +previous_wire if previous_wire else 'No generated messages yet; original claim is P AND B.')
        prompt+=' The latest acknowledgement action and claim target encode the prior speaker position.'
    return [{'role':'system','content':SYSTEM},
            {'role':'user','content':prompt+'\n'+context}]

def plan(trials=1,turns=6):
    if type(trials) is not int or trials not in (1,2):raise ValueError('trials must be 1 or 2')
    if type(turns) is not int or turns not in (4,6,8):raise ValueError('turns must be 4, 6 or 8')
    # Reverse first-speaker assignment in second trial, preserving model parity via order mapping.
    return [(trial,fmt,turn) for trial in range(trials) for fmt in FORMATS for turn in range(turns)]

def summarize(rows,spent,status,reason=None):
    by_format={}
    for fmt in FORMATS:
        group=[x for x in rows if x['format']==fmt]
        receipts=[x for x in group if x.get('receipt_correct') is not None]
        facets=('action','path','signal_sense','evidence')
        by_format[fmt]={
          'calls':len(group),
          'component_accuracy':{k:{
              'correct':sum(x['receipt_components_correct'][k] for x in receipts),
              'total':len(receipts),
              'rate':(sum(x['receipt_components_correct'][k] for x in receipts)/len(receipts)
                      if receipts else None)} for k in facets},
          'valid_agent_outputs':sum(x.get('agent_valid') is True for x in group),
          'invalid_agent_outputs':sum(x.get('agent_valid') is False for x in group),
          'valid_ucl_packets':sum(x.get('packet_valid') is True for x in group),
          'receipts_correct':sum(x['receipt_correct'] is True for x in receipts),
          'receipts_scored':len(receipts),
          'receipt_agreement':(sum(x['receipt_correct'] is True for x in receipts)/len(receipts) if receipts else None),
          'input_tokens':sum((x.get('usage') or {}).get('input') or 0 for x in group),
          'output_tokens':sum((x.get('usage') or {}).get('output') or 0 for x in group),
        }
    out={'status':status,'completed':len(rows),'estimated_cost_usd':round(spent,6),
         'by_format':by_format,'cases':rows,
         'limitations':'Generated live dialogue, but intents are agent self-reports, not independently judged author meaning. UCL uses mechanical encoding and validation; English has no such tool. Do not infer protocol superiority from this exploratory comparison.'}
    if reason:out['reason']=reason
    return out

def run(client=None,cap=1.0,dry_run=False,trials=1,turns=6):
    schedule=plan(trials,turns)
    if not 0<cap<=4:raise ValueError('cap must be between 0 and 4 USD')
    base=ucl.load_json(BASELINE.read_text(encoding='utf-8'))
    ucl.check(base)
    rows=[];spent=0.0
    sessions={}
    for trial,fmt,turn in schedule:
        key=(trial,fmt)
        if key not in sessions:
            sessions[key]={'packet':base,'wire':None,'history':[],'prior_intent':None,'blocked':False}
        state=sessions[key]
        actual_speaker=MODELS[(turn+trial)%2]
        if state['blocked']:
            rows.append({'trial':trial,'format':fmt,'turn':turn,'model':actual_speaker,
                         'skipped':'prior protocol failure','agent_valid':False})
            continue
        msgs=agent_messages(fmt,turn,state['wire'],state['history'],base,actual_speaker)
        # Reverse the model order while keeping prior history and role references independent.
        model=actual_speaker
        reserve=reserve_upper_bound(model,msgs,MAX_OUTPUT)
        if not dry_run and spent+reserve>cap:
            return summarize(rows,spent,'budget_stop','Pre-call estimate would exceed cap; no further API call')
        row={'trial':trial,'format':fmt,'turn':turn,'model':model,'prompt_bytes':sum(len(m['content'].encode()) for m in msgs),'prompt':safe_text(msgs[-1]['content'])}
        if dry_run:
            action=ACTIONS[turn%len(ACTIONS)]
            sense=SENSES[turn%2]
            evidence=EVIDENCE[(turn//2)%2]
            intent={'action':action,'path':turn%2,'signal_sense':sense,'evidence':evidence}
            receipt=state['prior_intent']
            example=('I offer no supporting evidence.' if evidence=='none' else
                     'I offer an imaginary example, not a real-world observation.')
            response=json.dumps({'receipt':receipt,'intent':intent,
               'message':f'I {action} only property {("P" if turn%2==0 else "B")}. '
                          f'By signal I mean {sense}. {example} This does not prove anything.'})
            usage=None;finish='dry_run'
        else:
            try:
                res=client.chat.completions.create(model=model,messages=msgs,max_tokens=MAX_OUTPUT)
            except Exception as exc:
                row.update({'agent_valid':False,'failure_type':'api_'+type(exc).__name__})
                rows.append(row);return summarize(rows,spent,'api_error','No automatic retries')
            response=res.choices[0].message.content or ''
            finish=getattr(res.choices[0],'finish_reason',None)
            usage=getattr(res,'usage',None)
            pin=getattr(usage,'prompt_tokens',None);pout=getattr(usage,'completion_tokens',None)
            spent+=price_estimate(model,pin,pout) if pin is not None and pout is not None else reserve
        row['response']=safe_text(response)
        row['finish_reason']=finish
        row['usage']={'input':getattr(usage,'prompt_tokens',None),'output':getattr(usage,'completion_tokens',None)}
        try:
            parsed=parse_agent(response,turn>0)
            row['agent_valid']=True
            row['intent']=parsed['intent']
            row['receipt']=parsed['receipt']
            row['receipt_correct']= (parsed['receipt']==state['prior_intent']) if turn else None
            if turn:
                row['receipt_components_correct']={k:(parsed['receipt'][k]==state['prior_intent'][k])
                                                   for k in ('action','path','signal_sense','evidence')}
                row['semantic_mismatch']=[k for k,v in row['receipt_components_correct'].items() if not v]
            else:
                row['receipt_components_correct']=None
                row['semantic_mismatch']=[]
            note=parsed['message']
            # A model has to convey the same intent through its message as privately
            # self-declared. For English this is not independently proven; all raw
            # text is retained to support external blinded annotation.
            wire,newpkt=encoded_handoff(fmt,parsed['intent'],note,state['packet'],turn,model)
            row['packet_valid']=newpkt is not None if fmt=='ucl_portable' else None
            row['wire_bytes']=len(wire.encode())
            row['handoff']=safe_text(wire)
            if newpkt is not None:state['packet']=newpkt
            state['wire']=wire
            state['history'].append(f'Turn {turn}, {model}: {wire}')
            state['prior_intent']=parsed['intent']
        except (ValueError,KeyError,TypeError) as exc:
            row['agent_valid']=False
            row['failure_type']='empty_output_length' if not response.strip() and finish=='length' else 'invalid_agent_or_packet'
            row['error']=str(exc)[:180]
            state['blocked']=True
        rows.append(row)
    return summarize(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--turns',type=int,choices=(4,6,8),default=6)
    ap.add_argument('--trials',type=int,choices=(1,2),default=1)
    ap.add_argument('--cap-usd',type=float,default=1.0)
    ap.add_argument('--output',default='uclbench-live-dialogue.json')
    args=ap.parse_args()
    if args.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=90)
    result=run(client,args.cap_usd,args.dry_run,args.trials,args.turns)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('complete','dry_run'):raise SystemExit(2)
    if result['status']=='dry_run' and any(x.get('agent_valid') is False for x in result['cases']):
        raise SystemExit(1)

if __name__=='__main__':main()
