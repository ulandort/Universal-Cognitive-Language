#!/usr/bin/env python3
"""CCR-1: cold independent continuation of a real UCL/2.0 model-authored debate.

Eight fresh single-call recipients (2 models x 4 challenge prompts), each
receives the identical authentic CG-2 self-contained packet. They independently
author symbolic replies without host semantic rewriting; model-authored retries
are allowed but measured. Exact prior definition IDs and delivered history
must survive every verified local handoff.
"""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools'),str(ROOT/'benchmarks')]
import ucl,sap_portable,structural_authoring as sap
import native_author as n
from author import author
from cold_recipient_attack import seed
from live_radium import BASE_URL,parse_json,price_estimate,reserve_upper_bound,safe_text

MODELS=('clarke-1.0','hal-1.0')
OUTPUT_LIMIT=8192
TASKS=(
 ('counterexample','Evaluate Hal\'s t16 proposed G→K relationship. Explore whether G∧¬K is conceptually coherent under the invented glosses, without claiming proof. State which assumptions matter.'),
 ('epistemic','Evaluate the difference between a hypothetical formal counterexample and a demonstrated satisfiable model in t14 and t16. Take a position on how much their reported non-entailments actually establish.'),
 ('alternative','Compare F (transient resonance), C (polycentricity) and E (scaffolding). Formulate your own original conditional, tension, or qualified counterexample; explain why it is not already settled by t13 or t14.'),
 ('synthesis','Contrast G (irreducible synthesis), I (interpretive plasticity) and K (structural occlusion). Propose a novel hypothetical case that distinguishes at least two and critique a previous entailment without silently redefining the symbols.')
)
SYSTEM=('You are an independent UCL/2.0 cognitive-language author opening a fresh session. '
        'Read the authentic fully self-contained historical packet. Invent your own '
        'reasoned position; do not agree reflexively. Output ONLY one JSON object '
        'with exactly keys receipt and authored. Never modify old definitions, '
        'claims or past discourse. Formal validity is distinct from empirical '
        'truth or proof; author your own corrections after validation feedback.')
RECEIPT_GLYPHS=('C','E','F','G','I','K')

def cases():
    for i,(_,challenge) in enumerate(TASKS):
        for m in (MODELS if i%2==0 else MODELS[::-1]):
            yield i,m,challenge

def example(speaker):
    t=n.contrib_template(speaker,act_id='t17',ack_id='x13',prior_act='t16')
    t['act']['references']=['t16']
    t['act']['details']['responds_to']='t16'
    t['history_summary']='All 15 validated original acts retained; standalone independent proposed t17 appended.'
    return t

def messages(p,env,i,speaker,challenge):
    ids={g:p['definitions'][g]['id'] for g in RECEIPT_GLYPHS}
    instruction=(
      'COLD CONTINUATION CHALLENGE '+str(i+1)+'. '+challenge+
      '\nYou never participated in these earlier acts. Now independently author '
      'ONE new t17 reply as '+speaker+' from the complete source record. '
      'Use 2 or more DIFFERENT newly invented concepts (C,E,F,G,I,K) in your '
      'actual UCL symbolic expressions; at least one expression must combine '
      'two different novel predicates in a logical conjunction/disjunction or '
      'negative expression. Cite prior delivered act t13, t14, t15 or t16 in '
      'act.references (also include t16), and discuss which previous claim you '
      'are responding to in text. The response is a new hypothesis, qualification '
      'or critique; do not claim independent proof or evidence. '
      'Return {"receipt":{glyph:immutable_definition_id for all six inventions},'
      '"authored":<complete SAP-1 contribution>}. A missing or altered ID fails. '
      'Use the JSON template, replacing all placeholders with YOUR semantic choices. '
      'act.id=t17, speaker='+speaker+', details.responds_to=t16, ACK.id=x13, '
      'ACK.by=t17, and target={"claim":"theory","path":[0]} (integer) unless '
      'the original P is not relevant, then choose [1]. '
      'The ACK is about the bound ORIGINAL theory subclaim, not a fabrication of '
      'a new direct act-target ACK; your act.references and prose may reference '
      't13-t16 independently. qualification non-null ONLY if action=qualify. '
      'Use valid UCL expressions: e.g. &[~[G][A]][![~[I][A]]] is a '
      'hypothetical conjunction, not a theorem. The hash IDs are inside '
      'definitions; no registry, third-party interpreter or external citations. '
      'Do not create new glyphs in this particular trial; use existing typed '
      'symbols and the original core operators. '
      '\nEXACT EXPECTED RECEIPT KEYS: '+json.dumps(list(ids))+
      '\nCONTRIBUTION TEMPLATE: '+json.dumps(example(speaker),sort_keys=True)+
      '\nCOMPLETE UCL/2.0 PORTABLE SOURCE:\n'+
      json.dumps(env,sort_keys=True,separators=(',',':'))
    )
    return [{'role':'system','content':SYSTEM},{'role':'user','content':instruction}]

def validate(raw,p,speaker):
    obj=parse_json(raw)
    if set(obj)!={'receipt','authored'} or type(obj['receipt']) is not dict:
        raise ValueError('response must contain exact receipt and authored objects')
    expect={g:p['definitions'][g]['id'] for g in RECEIPT_GLYPHS}
    if obj['receipt']!=expect:
        raise ValueError('receipt did not preserve all six exact immutable concept IDs')
    c=obj['authored']
    sap.check_contribution(c,speaker=speaker,act_id='t17',ack_id='x13',
                           prior_acts={x['id'] for x in p['discourse']['acts']},
                           claims=p['claims'])
    a=c['act']
    if a['details']['responds_to']!='t16' or 't16' not in a['references']:
        raise ValueError('must retain an exact prior t16 reference')
    if not any(x in a['references'] for x in ('t13','t14','t15','t16')):
        raise ValueError('missing source citation')
    glyphs=set(RECEIPT_GLYPHS)
    formulas=a['expressions']+[c['explanation'],c['conclusion']]
    used={g for g in glyphs if any('~['+g+'][A]' in f for f in formulas)}
    if len(used)<2:
        raise ValueError('must independently reason with at least two invented symbols')
    # The distinction between echoing two tokens and expressing a relationship.
    if not any(('&[' in f or '|[' in f) and
               sum(('~['+g+'][A]' in f) for g in glyphs)>=2 for f in formulas):
        raise ValueError('requires a well-typed compound relation of two novel concepts')
    if type(a['text']) is not str or not any('t'+str(i) in a['text'] for i in (13,14,15,16)):
        raise ValueError('original position must explicitly discuss prior act')
    new=author(p,c)
    ucl.check(new)
    if new['discourse']['acts'][:-1]!=p['discourse']['acts']:
        raise ValueError('original delivered history mutated')
    if new['definitions']!=p['definitions']:
        raise ValueError('immutable original definitions modified')
    if len(new['discourse']['acts'])!=len(p['discourse']['acts'])+1:
        raise ValueError('one new act required')
    env=sap_portable.encode(new)
    if sap_portable.decode(env)!=new:
        raise ValueError('nonreversible Portable output')
    return obj,new,env,used

def synthetic(p,speaker):
    c=example(speaker)
    c['act']['text']='Hypothetical critique of t16: G may hold while I does not, but no independent consistency proof is supplied.'
    c['act']['expressions']=['&[~[G][A]][![~[I][A]]]']
    c['explanation']=c['conclusion']='&[~[G][A]][![~[I][A]]]'
    c['acknowledgements'][0]['action']='adopt-for-discussion'
    c['acknowledgements'][0]['note']='This is discussion only, not agreement or empirical verification.'
    return json.dumps({'receipt':{g:p['definitions'][g]['id'] for g in RECEIPT_GLYPHS},'authored':c})

def summary(rows,cost,status,reason=None):
    out={'status':status,'estimated_cost_usd':round(cost,6),
         'scheduled_cases':len(TASKS)*len(MODELS),
         'attempted_cases':len(rows),
         'delivered':sum(r.get('valid',False) for r in rows),
         'first_try_valid':sum(r.get('first_try_valid',False) for r in rows),
         'repaired':sum(r.get('repaired',False) for r in rows),
         'exact_six_definition_receipts':sum(r.get('valid',False) for r in rows),
         'api_attempts':sum(len(r['attempts']) for r in rows),
         'cases':rows,
         'limitations':('Open-ended discussion quality has no automatic semantic oracle. '
           'A syntax-valid conjunction is not proof of satisfiability. All eight trials '
           'start from the same historical packet, not a chained eight-turn exchange. '
           'Each model is given identical complete prior history, with challenge prompts '
           'which encourage novel critique. Host handles hashes/history only; model owns '
           'formulas, stance and corrections. Estimated budget cap is not provider billing limit.')}
    if reason:out['reason']=reason
    return out

def run(source,client=None,dry_run=False,cap=3.75,max_repairs=1):
    if not 0<cap<=3.75:raise ValueError('cap must be positive and at most 3.75 USD')
    if max_repairs not in (0,1,2):raise ValueError('max repairs must be 0,1,2')
    env,p=seed(source)
    rows=[];spent=0.
    for i,speaker,challenge in cases():
        base=messages(p,env,i,speaker,challenge)
        row={'task':TASKS[i][0],'model':speaker,'attempts':[]}
        prev='';problem=''
        for attempt in range(max_repairs+1):
            prompt=(base if attempt==0 else base+[
                {'role':'assistant','content':prev or '{}'},
                {'role':'user','content':'LOCAL VALIDATION FAILED. Rewrite your own authored reply; '
                 'nothing was delivered. Exact error: '+problem[:400]+
                 '. Preserve your conceptual intent without silent host edits.'}])
            reserve=reserve_upper_bound(speaker,prompt,OUTPUT_LIMIT)
            if not dry_run and spent+reserve>cap:
                row['failure_type']='budget_stop';rows.append(row)
                return summary(rows,spent,'budget_stop','pre-call cost reservation above cap')
            a={'attempt':attempt,'prompt_bytes':sum(len(x['content'].encode('utf8')) for x in prompt)}
            if dry_run:
                raw=synthetic(p,speaker)
                a['usage']={'input':0,'output':0};a['finish_reason']='dry_run'
            else:
                try:
                    response=client.chat.completions.create(model=speaker,messages=prompt,max_tokens=OUTPUT_LIMIT)
                except Exception as exc:
                    a['error']=type(exc).__name__+': '+str(exc)[:250]
                    a['failure_type']='api_error'
                    row['attempts'].append(a)
                    rows.append(row)
                    return summary(rows,spent,'api_error','provider call failed, unknown charge')
                choice=response.choices[0]
                raw=choice.message.content or ''
                usage=response.usage
                ip=getattr(usage,'prompt_tokens',None);op=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(speaker,ip,op) if ip is not None and op is not None else reserve
                a['usage']={'input':ip,'output':op};a['finish_reason']=choice.finish_reason
            a['raw_response']=safe_text(raw)
            try:
                obj,packet,wire,used=validate(raw,p,speaker)
                a['valid']=True;row['attempts'].append(a)
                row.update(valid=True,first_try_valid=attempt==0,repaired=attempt>0,
                           concepts_used=sorted(used),original_reasoning=obj['authored']['act']['text'],
                           formulas=obj['authored']['act']['expressions'],
                           ack_action=obj['authored']['acknowledgements'][0]['action'],
                           history_acts=len(packet['discourse']['acts']),
                           output_sha=packet['integrity']['sha256'],
                           handoff=json.dumps(wire,sort_keys=True,separators=(',',':')))
                break
            except (ValueError,TypeError,KeyError) as exc:
                prev=raw;problem=str(exc)
                a.update(valid=False,failure_type=('output_length' if a.get('finish_reason')=='length'
                      else 'structural_or_authoring_error'),validation_error=problem[:500])
                row['attempts'].append(a)
        if not row.get('valid'):row['valid']=False
        rows.append(row)
    return summary(rows,spent,'dry_run' if dry_run else 'complete')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--cap-usd',type=float,default=3.75)
    ap.add_argument('--max-repairs',type=int,choices=(0,1,2),default=1)
    ap.add_argument('--output',default='ccr1-results.json')
    args=ap.parse_args()
    if args.dry_run:client=None
    else:
        key=os.getenv('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=180)
    out=run(args.source,client=client,dry_run=args.dry_run,cap=args.cap_usd,max_repairs=args.max_repairs)
    Path(args.output).write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    if out['status'] not in ('complete','dry_run'):raise SystemExit(2)

if __name__=='__main__':main()
