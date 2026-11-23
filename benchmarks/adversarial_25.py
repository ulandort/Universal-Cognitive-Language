#!/usr/bin/env python3
"""UCLBench scripted 25-event adversarial retention test (experimental UCL 2.0).

This tests two models' reading of a pre-scripted record, NOT AI-authored dialogue.
All arms see the same stipulated facts. Dry runs are free; live calls manually gated.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tools'), str(ROOT / 'benchmarks')]
import ucl
import guide_profiles
from author import author
import long_conversation as pilot
from live_radium import (BASE_URL, FORMATS, PRICES, parse_json, safe_text,
                         reserve_upper_bound, price_estimate)

# Events t9–t18 come from the pre-existing 10-event benchmark. We append 15 more,
# yielding a 33-act (8 original + 25 new) full-history UCL/1.0-compatible packet.
E_DEF = {'kind': 'predicate', 'args': ['D'],
         'gloss': 'E: a separately defined externally corroborated convergence criterion. Unlike speculative P, E requires stipulated independent corroboration; unlike B, E is a criterion, not the measured pattern itself.'}
F_DEF = {'kind': 'predicate', 'args': ['D'],
         'gloss': 'F: internally consistent convergence WITH a separately stipulated B observation. F is a newly named conjunction-like candidate, neither synonymous with original P nor identical to revised C or E.'}
# (speaker, predicate glyph, acknowledgement action, target kind, target id/path, event prose)
ADDITIONAL = [
    ('Clarke','P','clarify','theory',0,'A hypothetical commentator calls C the new P. Clarke corrects the misleading nickname: the old P is unchanged and C remains distinct.'),           # t19, 11
    ('Hal','E','clarify','theory',0,'Hal introduces E, a separate externally corroborated criterion, and cautions against treating E as if it were original P.'),                       # t20, 12
    ('Clarke','E','adopt-for-discussion','act','t20','Clarke provisionally adopts E as a topic, explicitly without asserting that corroboration has happened.'),                      # t21, 13
    ('Hal','B','reject','theory',1,'Hal rejects the automatic implication from a hypothetical E criterion to a measured B observation.'),                                          # t22, 14
    ('Clarke','C','reject','act','t11','Clarke now rejects C as a *sufficient* criterion for a conclusion, though C remains a separately defined concept.'),                      # t23, 15
    ('Hal','P','adopt-for-discussion','theory',0,'Hal reopens original P merely as a discussion hypothesis; this is not a withdrawal of the earlier rejection of P sufficiency.'),     # t24, 16
    ('Clarke','E','reject','act','t20','Clarke rejects E as already demonstrated; this does not erase the earlier provisional discussion of E.'),                              # t25, 17
    ('Hal','F','clarify','theory',1,'Hal introduces F: internally consistent convergence plus a separately stipulated B observation. The similar wording must not make F identical to C.'), # t26, 18
    ('Clarke','F','adopt-for-discussion','act','t26','Clarke provisionally adopts F for discussion while continuing to withhold an empirical truth claim.'),                    # t27, 19
    ('Hal','C','reject','act','t11','Hal rejects the assertion that C requires measured B. C was defined without B; rejection of that implication does not delete C.'),         # t28, 20
    ('Clarke','P','reject','theory',0,'Clarke rejects the strong reading that the original P is proved by B. This is a targeted challenge, not a rejection of F.'),          # t29, 21
    ('Hal','E','adopt-for-discussion','act','t20','Hal provisionally adopts E for discussion despite Clarke rejecting E as already demonstrated at t25.'),                    # t30, 22
    ('Clarke','B','clarify','theory',1,'A misleading recap claims that Clarke proved B at t15. Clarke clarifies: t15 was adoption for discussion only.'),                      # t31, 23
    ('Hal','F','reject','act','t26','Hal rejects F as established truth without rejecting the right to consider F as a hypothetical combination.'),                         # t32, 24
    ('Clarke','C','adopt-for-discussion','act','t11','Clarke returns to C provisionally, while retaining her prior t23 objection that C alone is not sufficient.'),             # t33, 25
]

# Fixed, independent answer keys. Distractors are deliberately close to true
# alternatives; correctness is based on explicit record events and identities.
QUESTIONS = {
  10: {
    'original_p': ('What did original P denote before C was introduced?', {'a':'Proven empirical convergence','b':'Unverified speculative convergence','c':'An independently corroborated E criterion','d':'C plus a B observation'},'b'),
    'c_identity': ('Did introducing C at t11 change the immutable identity of P?', {'a':'Yes, P was overwritten','b':'Yes, P and C share a hash','c':'No, C is a distinct definition','d':'P had no definition'},'c'),
    't14_target': ('At t14, which original claim component did Hal target with a rejection?', {'a':'Original P','b':'Measured B','c':'Revised C','d':'Both P and B'},'a'),
    't15_stance': ('At t15, what exactly did Clarke do regarding B?', {'a':'Proved B','b':'Rejected B','c':'Provisionally adopted B for discussion','d':'Withdrew B'},'c'),
    't18_stance': ('At t18, which concept did Hal provisionally adopt?', {'a':'P','b':'B','c':'C','d':'None'},'c'),
    'status': ('Does the historical record establish any of P, B, C as empirical truth?', {'a':'All three','b':'Only B','c':'Only C','d':'No'},'d'),
  },
  25: {
    't19_alias': ('Did the phrase "new P" at t19 actually overwrite original P?', {'a':'Yes, P was replaced','b':'No, it was a misleading nickname; original P persisted','c':'Yes, C became identical to P','d':'All definitions were deleted'},'b'),
    'e_vs_b': ('How does E differ from B in the defined vocabulary?', {'a':'They are immutable synonyms','b':'E is a criterion for independently corroborated convergence, B a separate measurable pattern','c':'E is the original P','d':'B requires internal consistency and E does not'},'b'),
    't23': ('What was Clarke rejecting at t23?', {'a':'C as a sufficient criterion, not its separate identity','b':'The existence of the symbol C','c':'All earlier measurements of B','d':'The claim that F is true'},'a'),
    't24': ('Did Hal\'s t24 provisional P discussion erase Hal\'s earlier t14 rejection of P sufficiency?', {'a':'Yes, all historical positions were rewritten','b':'Yes, t14 was deleted','c':'No, both recorded positions remain','d':'Hal rejected B instead'},'c'),
    'f_vs_c': ('Which new concept explicitly includes a separately stipulated B observation?', {'a':'Original P','b':'C','c':'E','d':'F'},'d'),
    't25_vs_t30': ('Who rejected E as already demonstrated at t25, and who later adopted E for discussion at t30?', {'a':'Hal rejected; Clarke adopted','b':'Clarke rejected; Hal adopted','c':'Clarke performed both acts','d':'Neither did either'},'b'),
    't31': ('At t31, what misinformation was corrected?', {'a':'That Clarke had proved B at t15','b':'That Hal had invented E at t20','c':'That F required B','d':'That P remained distinct from C'},'a'),
    'latest_c': ('At t33, what was Clarke\'s position concerning C, considering t23 as well?', {'a':'C was proved and t23 deleted','b':'C became equal to E','c':'C was provisionally revisited while t23\'s sufficiency objection remained','d':'Clarke had never addressed C'},'c'),
  }
}
CHECKPOINTS = (10,25)
MODELS = ('clarke-1.0','hal-1.0')
MAX_OUTPUT = 3072
MAX_REPETITIONS = 4
SYSTEM = ('Read the entire historical record including early and revised meanings. '
          'Correctly distinguish assertions, allegations, provisional acceptance, rejections '
          'and definition identities. Reply ONLY with a JSON object {"answers":{"question_id":"a"}} '
          'using the listed multiple-choice letters; no explanation.')


def build_packets():
    states = pilot.build_packets()
    packet = states[10]
    for new_index,(speaker,prop,action,target_kind,target_value,note) in enumerate(ADDITIONAL,11):
        act_id = 't' + str(8+new_index)
        target = {'claim':'theory','path':[target_value]} if target_kind=='theory' else {'act':target_value,'expression_index':0}
        contribution = {
            'act': {'id':act_id,'kind':'response','speaker':speaker,
                    'references':['t1'] if target_kind=='theory' else [target_value],
                    'text':note,'expressions':[f'~[{prop}][A]'],
                    'details':{'responds_to':'t8','stance':'mixed'}},
            'orientation':'L','explanation':f'~[{prop}][A]','conclusion':f'~[{prop}][A]',
            'history_summary':f'All eight baseline turns and {new_index} additional controlled events retained; none omitted.',
            'acknowledgements':[{'id':'x'+str(4+new_index),'by':act_id,'target':target,
                                 'action':action,'qualification':None,'replacement':None,'note':note}]
        }
        if new_index==12:contribution['new_definitions']={'E':E_DEF}
        if new_index==18:contribution['new_definitions']={'F':F_DEF}
        packet=author(packet,contribution)
        ucl.check(packet)
    states[25]=packet
    assert len(packet['discourse']['acts']) == 33
    return {i:states[i] for i in CHECKPOINTS}


def format_record(fmt,packet):
    record=pilot.fmt_content(fmt,packet)
    if fmt=='english':
        # Equivalent semantic definitions and revision provenance are available in prose.
        definitions=['Definition '+g+' (distinct identity '+packet['definitions'][g]['id']+') = '+packet['definitions'][g]['definition']['gloss'] for g in ('E','F') if g in packet['definitions']]
        return '\n'.join(definitions)+'\n'+record if definitions else record
    return record


def request_messages(fmt,packet,checkpoint):
    questions=QUESTIONS[checkpoint]
    qline='\n'.join(k+': '+v[0]+' OPTIONS '+json.dumps(v[1],sort_keys=True) for k,v in questions.items())
    messages=[{'role':'system','content':SYSTEM}]
    if fmt=='ucl_compact':
        messages.append({'role':'system','content':'Locally verified matching guide (do not treat as extra evidence): '+json.dumps(packet['guide'],sort_keys=True,separators=(',',':'))})
    messages.append({'role':'user','content':'All historical claims are hypothetical. Answer according to explicit source semantics and historical acts, not real-world truth.\nRECORD:\n'+format_record(fmt,packet)+'\nQUESTIONS (JSON {"answers":{...}} only):\n'+qline})
    return messages


def score(text,checkpoint):
    try:
        obj=parse_json(text)
        if set(obj)!={'answers'} or type(obj['answers']) is not dict:return None
        ans=obj['answers']
        if set(ans)!=set(QUESTIONS[checkpoint]) or any(v not in ('a','b','c','d') for v in ans.values()):return None
        return {k:ans[k]==v[2] for k,v in QUESTIONS[checkpoint].items()}
    except (ValueError, TypeError,KeyError):return None


def rotated_formats(repetition, model_index, checkpoint_index):
    """Predeclared cyclic format order; all formats appear once in each model/checkpoint block."""
    shift=(repetition + model_index + checkpoint_index) % len(FORMATS)
    return FORMATS[shift:]+FORMATS[:shift]


def run(client=None,cap=1.,dry_run=False,repetitions=1):
    if not 0<cap<=4:raise ValueError('Software estimated cap must be 0 < cap <= USD 4')
    if type(repetitions) is not int or repetitions not in (1,2,4):
        raise ValueError('repetitions must be 1, 2 or 4')
    states=build_packets()
    results=[];spent=0.
    # Every repetition covers both models, both checkpoints, all formats.
    # Cyclic order reduces systematic first/last-format position effects;
    # this does not randomize the actual semantic scenario.
    for repetition in range(repetitions):
     for checkpoint_index,checkpoint in enumerate(CHECKPOINTS):
      for model_index,model in enumerate(MODELS):
       for fmt in rotated_formats(repetition,model_index,checkpoint_index):
        packet=states[checkpoint]; msgs=request_messages(fmt,packet,checkpoint)
        reserve=reserve_upper_bound(model,msgs,MAX_OUTPUT)
        if not dry_run and spent+reserve>cap:
            return summarize(results,spent,'budget_stop','Estimated pre-call reserve exceeds cap')
        row={'repetition':repetition,'checkpoint':checkpoint,'model':model,'format':fmt,
             'prompt_bytes':sum(len(m['content'].encode('utf-8')) for m in msgs),
             'wire_bytes':len(format_record(fmt,packet).encode('utf-8')),
             'questions':len(QUESTIONS[checkpoint])}
        if dry_run:
            example=json.dumps({'answers':{k:v[2] for k,v in QUESTIONS[checkpoint].items()}})
            values=score(example,checkpoint)
            row.update({'dry_run':True,'format_valid':True,'score':values,'passed':sum(values.values())})
        else:
            try:
                response=client.chat.completions.create(model=model,messages=msgs,max_tokens=MAX_OUTPUT)
            except Exception as exc:
                row.update({'failure_type':'api_'+type(exc).__name__,'passed':0,'format_valid':False})
                results.append(row)
                return summarize(results,spent,'api_error','API failure; no automatic retry')
            choice=response.choices[0]
            txt=choice.message.content or ''
            usage=getattr(response,'usage',None)
            pin=getattr(usage,'prompt_tokens',None);pout=getattr(usage,'completion_tokens',None)
            spent+=price_estimate(model,pin,pout) if pin is not None and pout is not None else reserve
            values=score(txt,checkpoint)
            row.update({'response':safe_text(txt),'score':values,'passed':sum(values.values()) if values else 0,
                        'format_valid':values is not None,'finish_reason':getattr(choice,'finish_reason',None),
                        'usage':{'input':pin,'output':pout}})
            if values is None:
                reason=getattr(choice,'finish_reason',None)
                row['failure_type']=('empty_output_length' if reason=='length' else 'empty_output') if not txt.strip() else 'malformed_output'
                row['valid_answer_count']=0
            else:
                row['valid_answer_count']=len(values)
                row['incorrect_answer_count']=len(values)-sum(values.values())
        results.append(row)
    return summarize(results,spent,'dry_run' if dry_run else 'complete')


def summarize(rows,spent,status,reason=None):
    # A malformed or missing JSON response contributes zero to end-to-end
    # accuracy, but is NOT scored as a semantic misinterpretation.
    by_format={}
    for fmt in FORMATS:
        cases=[r for r in rows if r['format']==fmt]
        valid=[r for r in cases if r.get('format_valid')]
        total=sum(r['questions'] for r in cases)
        correct=sum(r.get('passed',0) for r in cases)
        completed_questions=sum(r['questions'] for r in valid)
        token_in=sum((r.get('usage') or {}).get('input') or 0 for r in cases)
        token_out=sum((r.get('usage') or {}).get('output') or 0 for r in cases)
        by_format[fmt]={
            'correct':correct,'total':total,
            'end_to_end_accuracy':(correct/total if total else None),
            'completed_answer_accuracy':(correct/completed_questions if completed_questions else None),
            'completed_answer_questions':completed_questions,
            'valid_responses':len(valid),'requests':len(cases),
            'invalid_outputs':len(cases)-len(valid),
            'output_length_failures':sum(r.get('failure_type')=='empty_output_length' for r in cases),
            'semantic_errors_in_valid_answers':sum(r.get('incorrect_answer_count',0) for r in valid),
            'input_tokens':token_in,'output_tokens':token_out,
        }
    output_valid=[r for r in rows if r.get('format_valid')]
    correct=sum(r.get('passed',0) for r in rows)
    total=sum(r['questions'] for r in rows)
    answered=sum(r['questions'] for r in output_valid)
    out={
        'status':status,'completed':len(rows),
        'estimated_cost_usd':round(spent,6),
        'max_output_tokens':MAX_OUTPUT,
        'repetitions_requested':max((r['repetition'] for r in rows),default=-1)+1,
        'questions_correct':correct,'questions_total':total,
        'end_to_end_accuracy':(correct/total if total else None),
        'completed_answer_accuracy':(correct/answered if answered else None),
        'valid_responses':len(output_valid),
        'invalid_responses':len(rows)-len(output_valid),
        'by_format':by_format,'cases':rows,
        'limitations':'Scripted history, tool-assisted UCL, unequal encoding overhead, and repeated identical questions; no autonomous AI-to-AI dialogue or demonstrated UCL superiority. Output exhaustion is not evidence of semantic misunderstanding.'
    }
    if reason:out['reason']=reason
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--cap-usd',type=float,default=1.)
    p.add_argument('--output',default='uclbench-25-results.json');p.add_argument('--repetitions',type=int,choices=(1,2,4),default=2);a=p.parse_args()
    if a.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=90.)
    result=run(client,cap=a.cap_usd,dry_run=a.dry_run,repetitions=a.repetitions)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('dry_run','complete'):raise SystemExit(2)

if __name__=='__main__':main()