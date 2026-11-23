#!/usr/bin/env python3
"""CG-2: Eight-turn novel-concept synthesis and adversarial cross-framework exchange using stable UCL/2.0.

This tests model-authored concept definitions, not merely novel prose labels.
The host computes hashes/retains immutable history but NEVER invents or repairs
a definition or interprets novelty as truth. Models receive complete UCL/2.0
Portable packets; no ordinary-English relay and no central registry.
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
import native_author as n
import structural_authoring as sap
import sap_portable
from author import author
from live_radium import parse_json,safe_text,reserve_upper_bound,price_estimate

OUTPUT_LIMIT=16384
GLYPHS='CEFGIKMNOSTUVWY'
SYSTEM=('You are an independent cognitive-language researcher. Return ONLY a valid '
        'JSON object and no Markdown. Your goal is original, precise speculative '
        'concept development, not empirical truth or agreement.')
PURPOSE=('Investigate how independently reasoning intelligences can preserve '
         'understanding when conceptual frameworks, interpretations, and observed '
         'patterns differ. You may reason beyond P and B. Make no empirical claims. '
         'An invented concept should have a distinct, operationally informative '
         'meaning rather than merely rename an existing predicate.')

def template(speaker,turn,prior_act):
    c=n.contrib_template(speaker,'t'+str(9+turn),'x'+str(5+turn),prior_act)
    c['new_definitions']={}
    return c

def make_messages(state,turn,speaker):
    required=turn in (0,1,2,3)
    t=template(speaker,turn,state['last_act'] or 't8')
    instructions=(
      PURPOSE+'\nUCL/2.0 CONCEPT GENESIS CHALLENGE (CG-2). '
      'Author your OWN contribution directly as UCL semantic JSON, not English '
      'for a converter. JSON response must contain EXACTLY receipt and authored. '
      'authored is the exact contribution template below INCLUDING new_definitions. '
      'All other authored fields follow SAP-1 rules; this experiment permits '
      'the additional new_definitions object. '      'new_definitions maps a SINGLE UNUSED ASCII glyph to a complete NEW definition '
      'with exactly {"kind":"predicate","args":["D"],"gloss":"meaning"}. '
      'D is the existing domain, A is its example entity, P and B are earlier predicates. '
      'The new predicate must describe an original hypothetical property of D entities. '
      'Invent its substantive meaning yourself; give a nonempty, clear gloss '
      'and state how it differs from existing predicates. '
      'Choose a free glyph among '+GLYPHS+'; any already used glyph is prohibited. '
      'Never rewrite an existing definition, core operator or earlier act. '
      +('During the first four turns, introduce exactly ONE new predicate and use it '
        'in act.expressions and explanation or conclusion, as ~[glyph][A]. '
        if required else
        'This is the second phase. You MAY introduce zero or one new predicates. '
        'Challenge a prior claim, offer a counterexample, or carefully qualify '
        'a previously proposed relationship between at least two independently '
        'defined new concepts. Do not uncritically accept every prior claim. '
        'Try to make a genuine reasoning advance, with precise references '
        'to previous delivered acts. Distinguish conceptual assumptions '
        'from theorems and claim truth from mere syntax. ')+
      'Every act MUST discuss at least one newly invented non-baseline concept '
      'using an actual well-typed formula with its glyph (not just an English name). '
      'Keep hypotheses unproven, and do not confuse a quoted or counterexample '
      'formula with an assertion. '
      'Use a valid ACK target {"claim":"theory","path":[0]} or [1], '
      'and exact actor IDs, matching valid UCL expression syntax. '
      'Your output is a contribution: host ONLY appends history and computes '
      'canonical definition IDs and packet checksums; it does not choose semantic content. '
      'Do not supply hashes for new definitions; their integrity identifiers are computed deterministically. '
      'For receipt: if no previous newly invented concept was DELIVERED, use JSON null. '
      'Otherwise use exactly {"glyph":"G","definition_id":"actual-id",'
      '"paraphrase":"your independent concise interpretation of what it means"}. '
      'The glyph and definition_id MUST refer to the MOST RECENTLY introduced '
      'custom concept in the delivered packet, not an invented or earlier ID. '
      'Paraphrase the meaning in your own words instead of copying the gloss. '
      '\nTEMPLATE: '+json.dumps({'receipt':None,'authored':t},sort_keys=True)+
      '\nCOMPLETE VALIDATED PRIOR PORTABLE PACKET:\n'+state['wire']
    )
    if state['last_concept'] is None:
        instructions+='\nThis is the first delivered concept: receipt MUST be null.'
    if state['failed']:
        instructions+='\n'+str(state['failed'])+' prior undelivered turns must not be inferred as messages.'
    return [{'role':'system','content':SYSTEM},{'role':'user','content':instructions}]

def validate_response(raw,state,turn,speaker):
    obj=parse_json(raw)
    if set(obj)!={'receipt','authored'}:
        raise ValueError('CG-2 response must have exactly receipt and authored')
    rec=obj['receipt']
    if state['last_concept'] is None:
        if rec is not None:raise ValueError('receipt must be null before a delivered new definition')
    else:
        if type(rec) is not dict or set(rec)!={'glyph','definition_id','paraphrase'}:
            raise ValueError('receipt schema incorrect')
        if rec['glyph']!=state['last_concept']['glyph'] or rec['definition_id']!=state['last_concept']['id']:
            raise ValueError('receipt failed exact definition identity')
        if type(rec['paraphrase']) is not str:
            raise ValueError('receipt paraphrase metadata must be a string')
    c=obj['authored']
    if type(c) is not dict or set(c)!=sap.CONTRIBUTION_FIELDS|{'new_definitions'}:
        raise ValueError('CG-1 contribution fields incorrect')
    defs=c['new_definitions']
    if type(defs) is not dict or len(defs)>1 or (turn in (0,1,2,3) and len(defs)!=1):
        raise ValueError('CG-2 requires one novel definition for first four turns; at most one later')
    prior_acts={x['id'] for x in state['packet']['discourse']['acts']}
    sap.check_contribution({k:v for k,v in c.items() if k!='new_definitions'},
        speaker=speaker,act_id='t'+str(9+turn),ack_id='x'+str(5+turn),
        prior_acts=prior_acts,claims=state['packet']['claims'])
    new=[]
    for g,d in defs.items():
        if type(g) is not str or g not in GLYPHS or g in state['packet']['definitions']:
            raise ValueError('CG-2 glyph must be a previously unused reserved-candidate symbol')
        if (type(d) is not dict or set(d)!={'kind','args','gloss'} or
            d['kind']!='predicate' or d['args']!=['D'] or
            type(d['gloss']) is not str or not d['gloss'].strip()):
            raise ValueError('CG-2 new definition must be typed, complete and substantial')
        new.append(g)
    created={g:ucl.definition_id(d) for g,d in defs.items()}
    # The model must actually USE invented concepts as formal expressions.
    concepts=set(state['invented'])|set(new)
    if not concepts:raise ValueError('CG-2 cannot proceed without a created concept')
    formulas=c['act']['expressions']+[c['explanation'],c['conclusion']]
    if not any('~['+g+'][A]' in x for x in formulas for g in concepts):
        raise ValueError('CG-2 new concept not used in formal UCL expression')
    for g in new:
        if not any('~['+g+'][A]' in x for x in formulas):
            raise ValueError('CG-2 authored new definition but did not use it')
    packet=author(state['packet'],c)
    ucl.check(packet)
    for g,r in state['packet']['definitions'].items():
        if packet['definitions'].get(g)!=r:
            raise ValueError('CG-2 attempted mutation of immutable prior definition')
    if packet['discourse']['acts'][:-1]!=state['packet']['discourse']['acts']:
        raise ValueError('CG-2 prior acts modified')
    for g in new:
        if packet['definitions'][g]['id']!=created[g]:
            raise ValueError('CG-2 new definition identity mismatch')
    env=sap_portable.encode(packet)
    assert sap_portable.decode(env)==packet
    return obj,packet,json.dumps(env,sort_keys=True,separators=(',',':')),new

def synthetic(turn,speaker,state):
    c=template(speaker,turn,state['last_act'] or 't8')
    if turn in (0,1,2,3):
        g=('C','E','G','K')[turn]
        c['new_definitions']={g:{'kind':'predicate','args':['D'],
            'gloss':('A speculative conceptual property of a cognitive system describing '
                    'the explicit tracking of interpretive changes across successive '
                    'dialogue states without claiming objective measurement or causation. '
                    'This is distinct from P and B because it concerns dialogue continuity, '+
                    'with independently invented perspective '+str(turn)+'.')}}
    g=next(iter(c['new_definitions']),state['last_concept']['glyph'] if state['last_concept'] else 'C')
    form='~['+g+'][A]'
    c['act']['expressions']=[form]
    c['act']['text']='Hypothetically this distinct invented property could affect interpretive dialogue; it is not empirically verified.'
    c['explanation']=c['conclusion']=form
    c['acknowledgements'][0]['target']['path']=[0]
    c['acknowledgements'][0]['action']='adopt-for-discussion'
    c['acknowledgements'][0]['note']='Discussion only, not established proof'
    rec=(None if state['last_concept'] is None else
         {'glyph':state['last_concept']['glyph'],
          'definition_id':state['last_concept']['id'],
          'paraphrase':'An invented hypothetical property concerned with how interpretations are tracked across dialogue.'})
    return json.dumps({'receipt':rec,'authored':c})

def summarize(rows,spent,status,reason=None):
    out={'status':status,'estimated_cost_usd':round(spent,6),'max_output_tokens':OUTPUT_LIMIT,
         'attempted_turns':len(rows),'delivered':sum(r.get('valid') is True for r in rows),
         'first_attempt_valid':sum(r.get('first_attempt_valid') is True for r in rows),
         'repaired':sum(r.get('repaired') is True for r in rows),
         'new_definitions_created':sum(len(r.get('new_definitions',[])) for r in rows),
         'receipts_verified':sum(r.get('receipt_verified') is True for r in rows),
         'api_attempts':sum(len(r['attempts']) for r in rows),'cases':rows,
         'limitations':('Synthetic dry-run is a protocol oracle, not model success. Live '
          'definition novelty and paraphrase correctness require independent human review. '
          'Identity matching checks exact hashes, NOT meaning; generated hypotheses remain '
          'unverified. Host computes hashes and assembles retained history. No English arm. '
          'Provider timeouts can incur unreported charges.')}
    if reason:out['reason']=reason
    return out

def run(client=None,dry_run=False,turns=8,cap=5.0,max_repairs=2):
    if turns!=8:raise ValueError('CG-2 is exactly 8 turns')
    if max_repairs not in (0,1,2):raise ValueError('max repairs must be 0,1,2')
    if not 0<cap<=5:raise ValueError('cap USD must be >0 <=5')
    packet=ucl.load_json(n.BASELINE.read_text())
    state={'packet':packet,'wire':json.dumps(sap_portable.encode(packet),sort_keys=True,separators=(',',':')),
           'last_act':None,'last_concept':None,'invented':set(),'failed':0}
    rows=[];spent=0.
    for turn in range(turns):
        speaker=n.MODELS[turn%2]
        base=make_messages(state,turn,speaker)
        row={'turn':turn,'speaker':speaker,'attempts':[],'previous_concept':state['last_concept']}
        old='';err=''
        for retry in range(max_repairs+1):
            messages=base if retry==0 else base+[
                {'role':'assistant','content':old or '{}'},
                {'role':'user','content':('VALIDATION FAILED, no message was delivered. '
                  'Correct YOUR OWN original complete response. Exact error: '+err[:350]+
                  '. Do not alter old definitions. No semantic repair will be done by host.') }]
            reserve=reserve_upper_bound(speaker,messages,OUTPUT_LIMIT)
            if not dry_run and spent+reserve>cap:
                row['failure_type']='budget_stop';rows.append(row)
                return summarize(rows,spent,'budget_stop','pre-call reservation exceeded cap')
            attempt={'index':retry,'prompt_bytes':sum(len(m['content'].encode('utf8')) for m in messages)}
            if dry_run:
                raw=synthetic(turn,speaker,state)
                attempt['usage']={'input':0,'output':0}
                attempt['finish_reason']='dry_run'
            else:
                try:
                    response=client.chat.completions.create(
                        model=speaker,messages=messages,max_tokens=OUTPUT_LIMIT)
                except Exception as exc:
                    attempt.update(failure_type='api_'+type(exc).__name__,
                                   provider_charge_unknown=True,error=str(exc)[:200])
                    row['attempts'].append(attempt)
                    break
                raw=response.choices[0].message.content or ''
                usage=response.usage
                pi=getattr(usage,'prompt_tokens',None)
                po=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(speaker,pi,po) if pi is not None and po is not None else reserve
                attempt['usage']={'input':pi,'output':po}
                attempt['finish_reason']=response.choices[0].finish_reason
            attempt['raw_response']=safe_text(raw)
            try:
                obj,new_packet,wire,new=validate_response(raw,state,turn,speaker)
                attempt['valid']=True;row['attempts'].append(attempt)
                row.update({'valid':True,'first_attempt_valid':retry==0,'repaired':retry>0,
                            'receipt_verified':state['last_concept'] is not None,
                            'receipt_paraphrase':obj['receipt']['paraphrase'] if obj['receipt'] else None,
                            'new_definitions':[{ 'glyph':g,'id':new_packet['definitions'][g]['id'],
                              'gloss':new_packet['definitions'][g]['definition']['gloss']} for g in new],
                            'act_text':obj['authored']['act']['text'],
                            'expressions':obj['authored']['act']['expressions'],
                            'envelope_bytes':len(wire.encode('utf8')),
                            'handoff':safe_text(wire)})
                state['packet']=new_packet;state['wire']=wire
                state['last_act']='t'+str(9+turn);state['invented'].update(new)
                if new:
                    g=new[-1]
                    state['last_concept']={'glyph':g,'id':new_packet['definitions'][g]['id']}
                state['failed']=0
                break
            except (ValueError,TypeError,KeyError) as exc:
                old=raw;err=str(exc)
                attempt.update({'valid':False,
                    'failure_type':'output_token_exhaustion' if attempt.get('finish_reason')=='length'
                         else 'invalid_or_rejected_contribution',
                    'validation_error':err[:400]})
                row['attempts'].append(attempt)
        if not row.get('valid'):
            row['valid']=False
            row['failure_type']=row['attempts'][-1].get('failure_type','invalid')
            state['failed']+=1
        rows.append(row)
    return summarize(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--turns',type=int,choices=(8,),default=8)
    ap.add_argument('--max-repairs',type=int,choices=(0,1,2),default=2)
    ap.add_argument('--cap-usd',type=float,default=5.0)
    ap.add_argument('--output',default='cg2-results.json')
    a=ap.parse_args()
    if a.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    out=run(client,dry_run=a.dry_run,turns=a.turns,cap=a.cap_usd,max_repairs=a.max_repairs)
    Path(a.output).write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    if out['status'] not in ('complete','dry_run'):raise SystemExit(2)
    if a.dry_run and out['delivered']!=a.turns:raise SystemExit('CG-2 free oracle failed')

if __name__=='__main__':main()
