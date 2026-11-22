#!/usr/bin/env python3
"""Native UCL-only dialogue with optional feedback-driven, model-owned repairs.

The receiver sees ONLY independently validated portable UCL packets. The relay
never changes model-written meaning, expressions or acknowledgements; the model
must write a complete replacement contribution after specific validation
feedback. Every API attempt (including unsuccessful repairs) is recorded and
counts against the shared estimated budget guard. No paid call on code pushes.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from types import SimpleNamespace

import native_author as n
import native_exploration as e
import structural_authoring as sap
import ucl
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[1]/'tools'))
import sap_portable
from live_radium import parse_json, safe_text, reserve_upper_bound, price_estimate

SYNTAX_GUIDE = """UCL/2.0 EXPERIMENTAL NATIVE AUTHORING CHECKLIST
The transport remains UCL/1.0 Portable. These are authoring rules, not new glyphs.
1. Response JSON has ONLY receipt, intent, authored. On the FIRST delivered turn
   or after all prior failed attempts, receipt must be JSON null. Prior historical
   acts in the immutable packet are not last-delivered *generated* messages.
2. Choose your own original claim target/stance. ACK target must have shape
   {"claim":"theory","path":[0]} (P) or path [1] (B). Indices are integers.
   The ACK id and act id must match the supplied turn template, exactly.
3. UCL grammar: ~[P][A], ~[B][A], ![~[P][A]], &[p][q], |[p][q].
   Parentheses, ASCII words (e.g. T, AND, OR), juxtaposed formulas and a
   bare top-level ? are not substitutes for these operators. Every argument
   must be enclosed in its own [brackets] and every expression must be typed.
4. The orientation is the exact UCL orientation symbol "L", NOT an English
   word or an epistemic formula. explanation MUST be a proposition.
   conclusion MUST be a proposition or a properly sourced epistemic report.
5. To avoid UNSOURCED uncertainty, do not place ?[p] in conclusion unless
   you also author a complete, validator-accepted context_updates.epistemic
   record. A stance of withhold-judgment is an ACK action, NOT necessarily
   an epistemic conclusion. Negation ![p] asserts a proposition, not simply
   absence of evidence or a provisional stance.
6. Use only known glyphs and existing defined symbols. The 11 core glyphs
   are @ # = ~ & | ! ? < * {. Do NOT invent T, -> or prose identifiers.
7. Each response act must have exactly the fields of its supplied template.
   Its details must be {"responds_to":"<existing earlier act>","stance":
   "accept|reject|mixed|undetermined"}. The references array must name only
   existing prior acts. Each ACK references a prior claim, not a new act.
8. The independently checked parent UCL packet is immutable. Do not rewrite
   its definitions, history or earlier acts. The relay adds the new act
   and hashes without altering any model-authored semantic field.
If validation fails, you may receive the exact error and your previous
candidate. Return an ENTIRE corrected original JSON object, not a patch.
Reconsider the semantics if necessary; never assume a valid formula is true.
"""

def attempt_prompt(base_messages, old_raw, error, repair_index):
    if repair_index==0:
        return base_messages
    # Full raw candidate is included to support exact self-correction.
    # The other model never sees it. This is feedback, not auto-repair.
    return base_messages + [{
        'role':'assistant','content':old_raw if old_raw.strip() else '{}'
    },{
        'role':'user','content':(
            'UCL AUTHORING VALIDATION FAILED. This is your private correction '
            'chance '+str(repair_index)+'; no message was delivered to the other '
            'model. Exact error: '+str(error)[:400]+
            '\nThe old contribution was NOT automatically changed. '
            'Return a complete corrected JSON object with receipt, intent, '
            'authored, preserving your chosen idea where possible. '
            'Use the exact supplied act/ACK IDs and the syntax checklist. '
            'No commentary, no patches, no English handoff.'
        )
    }]

def validate_candidate(raw,speaker,state,turn):
    obj=e.parse_response(raw,'ucl_native',state['last_intent'] is not None)
    authored=obj['authored']
    sap.check_contribution(authored,speaker=speaker,act_id='t'+str(9+turn),
                           ack_id='x'+str(5+turn),
                           prior_acts={x['id'] for x in state['packet']['discourse']['acts']},
                           claims=state['packet']['claims'])
    wire,packet,meta=n.normalise_sender('ucl_native',json.dumps(authored),
        state['packet'],speaker,act_id='t'+str(9+turn),
        ack_id='x'+str(5+turn))
    # A parser or host-derived string is never sent without a final protocol check.
    ucl.check(packet)
    # Wire carries the COMPLETE structural standard, original UCL guide,
    # definitions and conversation history. The receiver needs no registry.
    portable=sap_portable.encode(packet)
    sap_portable.decode(portable)
    wire=json.dumps(portable,ensure_ascii=True,sort_keys=True,separators=(',',':'))
    meta['self_contained_profile_hash']=portable['structural_rules']['sha256']
    return obj,wire,packet,meta

def synthetic_response(turn,speaker,state):
    case=n.CASES[turn%len(n.CASES)]
    intent={k:case[k] for k in n.FIELDS}
    atom='~[P][A]' if intent['path']==0 else '~[B][A]'
    note=('I '+intent['action']+' '+('P' if intent['path']==0 else 'B')+
          '. Signal: '+intent['signal_sense']+'; evidence: '+intent['evidence']+
          '. The old hypotheses remain unproved; test their logical independence.')
    authored=n.contrib_template(speaker,'t'+str(9+turn),'x'+str(5+turn),
                                   state['last_act'] or 't8')
    authored['act']['text']=note
    authored['act']['expressions']=[atom]
    authored['explanation']=authored['conclusion']=atom
    authored['acknowledgements'][0]['target']['path']=[intent['path']]
    authored['acknowledgements'][0]['action']=intent['action']
    authored['acknowledgements'][0]['note']=note
    return json.dumps({'receipt':state['last_intent'],'intent':intent,'authored':authored})

def summary(rows,spent,status,turns,directions,max_repairs,reason=None):
    conversations=[]
    for direction in range(directions):
        sub=[r for r in rows if r['direction']==direction]
        longest=streak=0
        for r in sub:
            streak=streak+1 if r.get('valid') is True else 0
            longest=max(longest,streak)
        conversations.append({
            'direction':direction,'starting_model':n.MODELS[direction],
            'attempted':len(sub),'valid_packets':sum(r.get('valid') is True for r in sub),
            'max_consecutive_valid_packets':longest,
            'first_attempt_valid':sum(r.get('first_attempt_valid') is True for r in sub),
            'repaired_and_delivered':sum(r.get('repaired_and_delivered') is True for r in sub),
            'receipts_scored':sum(r.get('receipt_correct') is not None for r in sub),
            'receipts_correct':sum(r.get('receipt_correct') is True for r in sub)
        })
    out={
        'status':status,'goal':'Sustain an original, model-authored UCL-only conversation',
        'formats_requested':['ucl_native'],'no_english_control_arms':True,
        'turns_requested':turns,'directions_requested':directions,
        'max_repairs_per_turn':max_repairs,'total_estimated_cost_usd':round(spent,6),
        'api_calls_attempted':sum(len(r['attempts']) for r in rows),
        'conversations':conversations,'cases':rows,
        'structural_profile':sap.PROFILE,
        'transport_format':sap_portable.FORMAT,
        'structural_rules_embedded':True,
        'limitations':('Only validated complete UCL packets are delivered; no '
         'English comparison arm or automatic semantic converter. Correcting models '
         'receive explicit error feedback; success after correction is NOT '
         'first-attempt native authorship. Private self-reported intent is not '
         'objective truth or independently verified novelty. Provider timeouts '
         'might be billable even when no usage was returned.')
    }
    if any(a.get('provider_charge_unknown') for r in rows for a in r['attempts']):
        out['estimated_cost_caveat']='Timed-out provider requests may have unknown charges'
    if reason:out['reason']=reason
    return out

def run(client=None,dry_run=False,turns=8,directions=1,cap=4.0,max_repairs=2):
    if turns not in (2,4,6,8):raise ValueError('turns must be 2,4,6,8')
    if directions not in (1,2):raise ValueError('directions must be 1,2')
    if max_repairs not in (0,1,2):raise ValueError('max_repairs must be 0,1,2')
    if not 0<cap<=10:raise ValueError('estimated cap must be 0-10 USD')
    original=ucl.load_json(n.BASELINE.read_text())
    rows=[];spent=0.0
    for direction in range(directions):
      initial_envelope=sap_portable.encode(original)
      state={'packet':original,'history':[],'last_intent':None,
             'last_act':None,'failed':0,
             'latest_wire':json.dumps(initial_envelope,sort_keys=True,separators=(',',':'))}
      for turn in range(turns):
        speaker=n.MODELS[(turn+direction)%2]
        base=e.make_prompt('ucl_native',turn,speaker,state)
        # Replace the plain 1.0 baseline with the fully self-contained 2.0
        # envelope. The standalone embedded structural rules are included in
        # the ACTUAL message, not only a host prompt or online documentation.
        old_packet=json.dumps(state['packet'],sort_keys=True,separators=(',',':'))
        if old_packet not in base[-1]['content']:
            raise ValueError('Internal error: prior packet missing from authored prompt')
        base[-1]['content']=base[-1]['content'].replace(old_packet,state['latest_wire'])
        base[-1]['content']+='\n'+SYNTAX_GUIDE+'\n'+sap.authoring_rules(
            act_id='t'+str(9+turn),ack_id='x'+str(5+turn),speaker=speaker,
            prior_act=state['last_act'] or 't8')
        row={'direction':direction,'turn':turn,'model':speaker,'format':'ucl_native',
             'resumed_after_failure':state['failed']>0,
             'last_delivered_act':state['last_act'],
             'structural_profile':sap.PROFILE,
            'transport_format':sap_portable.FORMAT,
            'attempts':[]}
        prior_raw='';prior_error=''
        for retry in range(max_repairs+1):
            msgs=attempt_prompt(base,prior_raw,prior_error,retry)
            reserve=reserve_upper_bound(speaker,msgs,n.MAX_OUTPUT)
            if not dry_run and spent+reserve>cap:
                row.update({'valid':False,'failure_type':'budget_stop'})
                rows.append(row)
                return summary(rows,spent,'budget_stop',turns,directions,max_repairs,
                               'Pre-call cost reservation exceeded remaining cap')
            attempt={'index':retry,'prompt_bytes':sum(len(m['content'].encode()) for m in msgs)}
            if dry_run:
                raw=synthetic_response(turn,speaker,state)
                attempt['usage']={'input':0,'output':0}
                attempt['finish_reason']='dry_run'
            else:
                try:
                    resp=client.chat.completions.create(
                        model=speaker,messages=msgs,max_tokens=n.MAX_OUTPUT)
                except Exception as exc:
                    attempt.update({'failure_type':'api_'+type(exc).__name__,
                                    'provider_charge_unknown':True,'error':str(exc)[:160]})
                    row['attempts'].append(attempt)
                    # A timeout is a transport event, not a semantic validation
                    # error. Do not resend automatically: it could be billed.
                    break
                raw=resp.choices[0].message.content or ''
                usage=resp.usage
                inp=getattr(usage,'prompt_tokens',None)
                out=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(speaker,inp,out) if inp is not None and out is not None else reserve
                attempt['usage']={'input':inp,'output':out}
                attempt['finish_reason']=getattr(resp.choices[0],'finish_reason',None)
            attempt['raw_response']=safe_text(raw)
            try:
                parsed,wire,packet,meta=validate_candidate(raw,speaker,state,turn)
                attempt['valid']=True
                row['attempts'].append(attempt)
                row.update(meta)
                row['valid']=True
                row['first_attempt_valid']=retry==0
                row['repaired_and_delivered']=retry>0
                row['receipt']=parsed['receipt']
                row['intent']=parsed['intent']
                row['receipt_correct']=(None if state['last_intent'] is None else
                    all(parsed['receipt'][k]==state['last_intent'][k] for k in n.FIELDS))
                row['receipt_facets']=(None if state['last_intent'] is None else
                    {k:parsed['receipt'][k]==state['last_intent'][k] for k in n.FIELDS})
                row['self_report_matches_explicit_structure']=all(
                    meta['author_intent'][k]==parsed['intent'][k] for k in ('action','path'))
                row['handoff']=safe_text(wire)
                row['wire_bytes']=len(wire.encode())
                # Only here is a validated packet made the next turn's state.
                state['packet']=packet
                state['latest_wire']=wire
                state['last_act']='t'+str(9+turn)
                state['last_intent']=parsed['intent']
                state['history'].append(wire)
                state['failed']=0
                break
            except (ValueError,TypeError,KeyError) as exc:
                prior_error=str(exc)
                prior_raw=raw
                attempt.update({'valid':False,'failure_type':(
                    'structural_profile_rejection' if isinstance(exc,sap.StructuralProfileError)
                    else n.classify_failure(raw,attempt.get('finish_reason'),exc)),
                    'validation_error':str(exc)[:400],
                    'possible_language_extension':'manual_review_required'
                        if any(t in raw for t in ('new operator','extend the language',
                                                   'proposed glyph','novel syntax')) else None})
                row['attempts'].append(attempt)
                if attempt['failure_type']=='output_token_exhaustion':
                    # The model may use another attempt if budget remains.
                    pass
        if not row.get('valid'):
            row['valid']=False
            row['failure_type']=row['attempts'][-1].get('failure_type','invalid')
            state['failed']+=1
        rows.append(row)
    return summary(rows,spent,'dry_run' if dry_run else 'complete',
                   turns,directions,max_repairs)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--turns',type=int,choices=(2,4,6,8),default=8)
    parser.add_argument('--directions',type=int,choices=(1,2),default=1)
    parser.add_argument('--max-repairs',type=int,choices=(0,1,2),default=2)
    parser.add_argument('--cap-usd',type=float,default=4.0)
    parser.add_argument('--output',default='ucl-only-live.json')
    a=parser.parse_args()
    if a.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    result=run(client,dry_run=a.dry_run,turns=a.turns,directions=a.directions,
               cap=a.cap_usd,max_repairs=a.max_repairs)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('dry_run','complete'):raise SystemExit(2)
    if a.dry_run and any(r.get('valid') is not True for r in result['cases']):
        raise SystemExit('Free dry-run protocol oracle failed')

if __name__=='__main__':main()
