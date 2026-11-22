#!/usr/bin/env python3
"""RR-1: model-owned relational reasoning over the SIX actual CG-1 inventions.

The starting packet is the immutable final handoff from paid CG-1 run 45079394296,
not a fabricated concept fixture. This exploratory test does not prove the
arguments, semantic comprehension, or benchmark superiority.
"""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl
import sap_portable
import structural_authoring as sap
import native_author as n
from author import author
from live_radium import parse_json,safe_text,reserve_upper_bound,price_estimate

GLYPHS=('C','E','G','K','M','N')
MAX_OUTPUT=16384

def load_seed(path):
    env=json.loads(Path(path).read_text())
    pkt=sap_portable.decode(env)
    if not set(GLYPHS).issubset(pkt['definitions']):
        raise ValueError('RR-1 seed must contain all six actual CG-1 concepts')
    if len(pkt['discourse']['acts'])!=14:
        raise ValueError('RR-1 expects exact six-turn CG-1 continuation with 14 acts')
    # Reject substituted fixture or modified concepts: verify previous CG-1 hash IDs.
    ids={'C':'uIRR6ai47xbTC6J-HbQroGsTPGn-k14T2Mqi3Ih_x0k',
         'E':'sQy4mWl1jkM6XFSuiPuKxv2b55zabMo4yRyteQtHmo4',
         'G':'CMiyVBXlU_sStNR9xTkxF0aMTNSzzE3J5zheO-wDjME',
         'K':'haKjN_nI06BCSWfPOa7bVTrnI5kZrTbfKD-qci2aI5A',
         'M':'LDgpltoM1WebFUyzX5fMOmbsBby5b2wtScW0SpT25Kw',
         'N':'AbFl-OdjrW5JOWH9KGoMdF0Aosf5yjAxEgEslXnWYc4'}
    if any(pkt['definitions'][g]['id']!=id for g,id in ids.items()):
        raise ValueError('RR-1 seed concept identities do not match genuine CG-1 output')
    return pkt

def prompt(state,turn,speaker):
    aid='t'+str(15+turn);xid='x'+str(11+turn)
    old=state['packet']['discourse']['current']
    t=n.contrib_template(speaker,aid,xid,old)
    t['act']['expressions']=['&[~[C][A]][~[E][A]]']
    t['explanation']='&[~[C][A]][~[E][A]]'
    t['conclusion']='&[~[C][A]][~[E][A]]'
    # This is an example of the grammar, NOT a mandated conclusion.
    last=state['last_act']
    text=('CONTINUATION OF A GENUINE SIX-TURN CLARKE/HAL CONCEPT INVENTION. '
      'You are '+speaker+'. Invent an original relationship, objection, counterexample, '
      'or well-qualified distinction among the six explicitly defined C,E,G,K,M,N concepts. '
      'You must reason over TWO OR MORE DISTINCT invented concepts in a SINGLE '
      'well-typed UCL formula, with & or | (for implication use |[![p]][q] '
      'only if you genuinely intend an implication). '
      'Do NOT merely list unrelated one-symbol atoms, do NOT assume that a '
      'conjunction is automatically true, and do NOT treat a counterexample '
      'as an empirical observation. The relation and its consequences are YOUR choice. '
      'Read the actual definitions and conversation before composing. '
      'Describe the inferential rationale and precise epistemic limits in act.text. '
      'Respond to the preceding model without being pressured to agree. '
      'Preserve all six immutable definitions, core glyphs and historical acts. '
      'Output ONE JSON object with EXACT keys authored, interpretation. '
      'authored must have EXACT SIX keys act,orientation,explanation,conclusion,'
      'acknowledgements,history_summary as in the template; do not add definitions. '
      'orientation must be L; act.kind response; details has responds_to and stance. '
      'ACK target must be an existing claim {"claim":"theory","path":[0]} or [1]; '
      'this ACK concerns the historical theory and is not endorsement of a newly '
      'created argument. Use act.id='+aid+', ACK id='+xid+', by='+aid+'. '
      'interpretation must be null on the FIRST NEW RR-1 relay turn, else a '
      'free 50+ character independent summary of the PREVIOUS RR-1 contribution. '
      'An interpretation can explicitly disagree; it must not falsely attribute. '
      'The model must write all semantic content. The host ONLY appends the '
      'unchanged historical packet and computes exact hashes. '
      'No proof of truth or novelty is implied by a valid packet. '
      '\nCONTRIBUTION SHAPE EXAMPLE (rewrite ALL semantic fields): '+json.dumps(t)+
      '\nLAST NEW RR-1 RELAY MESSAGE: '+(last or 'NONE')+
      '\nFULL VERIFIED PRIOR UCL/2.0 PORTABLE PACKET:\n'+state['wire'])
    return [{'role':'system','content':'Respond with only valid JSON, no Markdown. Reason independently without inventing empirical data.'},
            {'role':'user','content':text}]

def validate(raw,state,turn,speaker):
    obj=parse_json(raw)
    if type(obj) is not dict or set(obj)!={'authored','interpretation'}:
        raise ValueError('reply must have exactly authored, interpretation')
    it=obj['interpretation']
    if state['last_act'] is None:
        if it is not None:raise ValueError('first new conversation turn interpretation must be null')
    elif type(it) is not str or len(it.strip())<50:
        raise ValueError('interpretation must be an independent 50+ character summary')
    contribution=obj['authored']
    aid='t'+str(15+turn);xid='x'+str(11+turn)
    sap.check_contribution(contribution,speaker=speaker,act_id=aid,ack_id=xid,
       prior_acts={a['id'] for a in state['packet']['discourse']['acts']},
       claims=state['packet']['claims'])
    expressions=contribution['act']['expressions']+[contribution['explanation'],contribution['conclusion']]
    parser=ucl.Parser(state['packet']['definitions'])
    compound=[]
    for expression in expressions:
        tree=parser.parse(expression)
        used={g for g in GLYPHS if '~['+g+'][A]' in expression}
        if len(used)>=2 and ('&[' in expression or '|[' in expression):
            compound.append(expression)
    if not compound:
        raise ValueError('must construct a compound well-typed formula relating >=2 invented concepts')
    before=state['packet']
    new=author(before,contribution)
    ucl.check(new)
    if new['definitions']!=before['definitions'] or new['discourse']['acts'][:-1]!=before['discourse']['acts']:
        raise ValueError('prior history or immutable definitions altered')
    env=sap_portable.encode(new)
    assert sap_portable.decode(env)==new
    wire=json.dumps(env,sort_keys=True,separators=(',',':'))
    return obj,new,wire,compound

def synthetic(state,turn,speaker):
    aid='t'+str(15+turn);xid='x'+str(11+turn)
    c=n.contrib_template(speaker,aid,xid,state['packet']['discourse']['current'])
    a,b=('C','E') if turn%2==0 else ('G','K')
    formula='&[~['+a+'][A]][~['+b+'][A]]'
    c['act']['expressions']=[formula]
    c['act']['text']='Hypothetically compare both invented properties and their conceptual independence; this formula is only a speculative proposition.'
    c['explanation']=c['conclusion']=formula
    c['acknowledgements'][0]['target']['path']=[0]
    c['acknowledgements'][0]['action']='adopt-for-discussion'
    c['acknowledgements'][0]['note']='Provisional theory acknowledgement; no proof'
    i=None if state['last_act'] is None else ('The previous speaker considered a potentially hypothetical relation among '
      'invented predicates and explicitly did not supply measured evidence for it.')
    return json.dumps({'authored':c,'interpretation':i})

def summarize(rows,spent,status,reason=None):
    out={'status':status,'estimated_cost_usd':round(spent,6),
         'attempted_turns':len(rows),'delivered':sum(r.get('valid') is True for r in rows),
         'first_attempt_valid':sum(r.get('first_try') is True for r in rows),
         'repaired':sum(r.get('repaired') is True for r in rows),
         'compound_relations_delivered':sum(r.get('valid') is True for r in rows),
         'paraphrases_for_human_review':sum(bool(r.get('interpretation')) for r in rows),
         'api_calls':sum(len(r['attempts']) for r in rows),'cases':rows,
         'limitations':'Compound formula validity is NOT logical derivation, truth, or comprehension. '
          'Paraphrases, inferential merit, purported counterexamples, and conceptual novelty '
          'require independent transcript review; disagreements are not failures. '
          'One direction and no English control arm. Provider timeouts may incur unknown charges.'}
    if reason:out['reason']=reason
    return out

def run(seed,client=None,dry_run=False,turns=6,cap=4.0,max_repairs=2):
    if turns not in (4,6,8):raise ValueError('turns must be 4,6,8')
    if max_repairs not in (0,1,2):raise ValueError('repairs must be 0,1,2')
    if not 0<cap<=10:raise ValueError('cap must be USD 0-10')
    pkt=load_seed(seed)
    state={'packet':pkt,'wire':json.dumps(sap_portable.encode(pkt),sort_keys=True,separators=(',',':')),
           'last_act':None}
    rows=[];spent=0.
    for turn in range(turns):
        speaker=n.MODELS[turn%2]
        base=prompt(state,turn,speaker)
        row={'turn':turn,'speaker':speaker,'attempts':[]}
        old='';error=''
        for retry in range(max_repairs+1):
            messages=base if retry==0 else base+[
              {'role':'assistant','content':old or '{}'},
              {'role':'user','content':'Last undelivered candidate failed validation: '+error[:350]+
               '. Author your OWN corrected full JSON; no semantic repair or silent changes.'}]
            reserve=reserve_upper_bound(speaker,messages,MAX_OUTPUT)
            if not dry_run and spent+reserve>cap:
                row['failure_type']='budget_stop';rows.append(row)
                return summarize(rows,spent,'budget_stop','pre-call reservation exceeded cap')
            attempt={'retry':retry}
            if dry_run:
                raw=synthetic(state,turn,speaker)
                attempt['finish_reason']='dry_run';attempt['usage']={'input':0,'output':0}
            else:
                try:
                    rsp=client.chat.completions.create(model=speaker,messages=messages,max_tokens=MAX_OUTPUT)
                except Exception as ex:
                    attempt.update({'failure_type':'api_'+type(ex).__name__,
                                    'provider_charge_unknown':True,'error':str(ex)[:200]})
                    row['attempts'].append(attempt);break
                raw=rsp.choices[0].message.content or ''
                pi=getattr(rsp.usage,'prompt_tokens',None)
                po=getattr(rsp.usage,'completion_tokens',None)
                spent+=price_estimate(speaker,pi,po) if pi is not None and po is not None else reserve
                attempt.update({'finish_reason':rsp.choices[0].finish_reason,
                                'usage':{'input':pi,'output':po}})
            attempt['raw_response']=safe_text(raw)
            try:
                obj,new,wire,compound=validate(raw,state,turn,speaker)
                attempt['valid']=True;row['attempts'].append(attempt)
                row.update({'valid':True,'first_try':retry==0,'repaired':retry>0,
                            'interpretation':obj['interpretation'],
                            'compound_formulas':compound,
                            'act_text':obj['authored']['act']['text'],
                            'handoff':safe_text(wire),'wire_bytes':len(wire.encode())})
                state['packet']=new;state['wire']=wire
                state['last_act']=obj['authored']['act']['text']
                break
            except (ValueError,TypeError,KeyError) as ex:
                error=str(ex);old=raw
                attempt.update({'valid':False,
                    'failure_type':'output_token_exhaustion' if attempt.get('finish_reason')=='length'
                        else 'schema_or_semantic_validation',
                    'validation_error':error[:400]})
                row['attempts'].append(attempt)
        if not row.get('valid'):
            row['valid']=False
            row['failure_type']=row['attempts'][-1].get('failure_type','invalid')
        rows.append(row)
    return summarize(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seed',required=True)
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--turns',type=int,choices=(4,6,8),default=6)
    p.add_argument('--max-repairs',type=int,choices=(0,1,2),default=2)
    p.add_argument('--cap-usd',type=float,default=4.)
    p.add_argument('--output',default='rr1-results.json')
    a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=n.BASE_URL,max_retries=0,timeout=240)
    out=run(a.seed,client,dry_run=a.dry_run,turns=a.turns,cap=a.cap_usd,max_repairs=a.max_repairs)
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    if out['status'] not in ('dry_run','complete'):raise SystemExit(2)
    if a.dry_run and out['delivered']!=a.turns:raise SystemExit('offline oracle failed')

if __name__=='__main__':main()
