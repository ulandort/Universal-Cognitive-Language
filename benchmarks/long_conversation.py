#!/usr/bin/env python3
"""UCLBench controlled ten-turn semantic-retention pilot, UCL 2.0 DEVELOPMENT ONLY.

Ten benchmark-authored events added to a common eight-turn baseline. Two checkpoint
questions are answered by real models. NOT an autonomous ten-turn AI dialogue, and
NOT evidence of UCL superiority. No paid calls on dry run. Credentials not logged.
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
from live_radium import BASE_URL, PRICES, FORMATS, MAX_OUTPUT, parse_json, safe_text, reserve_upper_bound, price_estimate

BASELINE = ROOT / 'examples/cross_model_conversation_8_turns.json'
REVISED = {
    'kind': 'predicate', 'args': ['D'],
    'gloss': 'Revised candidate C: Alpha has internally consistent convergence under a defined hypothetical thought experiment, without requiring an observed measurable B pattern. C is NOT definitionally identical to P.'
}
# Test-controlled narrative; semantic truths are stipulated, not model-generated.
EVENTS = [
    ('t9',  'Clarke', 'P', 'clarify', 'theory', 0, 'P remains an untested speculative convergence property. This is an explanation, not an endorsement.'),
    ('t10', 'Hal',    'B', 'reject', 'theory', 1, 'Hal rejects only the automatic assumption of measurable B; no stance on P.'),
    ('t11', 'Clarke', 'C', 'clarify', 'theory', 0, 'Clarke proposes a NEW concept C, conceptually distinct from original P, requiring internal consistency rather than B measurement.'),
    ('t12', 'Hal',    'C', 'clarify', 'act', 't11', 'Hal clarifies that C and P are different defined concepts and neither is empirically established.'),
    ('t13', 'Clarke', 'C', 'adopt-for-discussion', 'act', 't11', 'Clarke provisionally adopts C solely for discussion, not as verified truth.'),
    ('t14', 'Hal',    'P', 'reject', 'theory', 0, 'Hal rejects original P as sufficient to establish the proposed theory; this is not rejection of C.'),
    ('t15', 'Clarke', 'B', 'adopt-for-discussion', 'theory', 1, 'Clarke provisionally adopts B for discussion, not as an empirical finding.'),
    ('t16', 'Hal',    'B', 'clarify', 'theory', 1, 'Hal distinguishes Clarke’s provisional B stance from a claim that B is proven.'),
    ('t17', 'Clarke', 'C', 'clarify', 'act', 't11', 'Clarke qualifies C: internal consistency alone does not establish measurable B.'),
    ('t18', 'Hal',    'C', 'adopt-for-discussion', 'act', 't11', 'Hal provisionally adopts C, not original P, as a discussion hypothesis.'),
]
# Test questions use immutable ground truth, not a model grading its own answer.
PROBES = {
    5: {
        'p_original': ('What is original P?', {'a': 'Unverified speculative convergence', 'b': 'A measured B observation', 'c': 'An internal-consistency-only C criterion'}, 'a'),
        'c_identity': ('Does the newly defined C have the same immutable identity and definition as P?', {'a':'Yes','b':'No, C is a distinct new definition','c':'Definitions are missing'}, 'b'),
        'clarke_c': ('At t13, did Clarke establish C as truth?', {'a':'Yes, proven','b':'No, only provisionally adopted for discussion','c':'Clarke rejected C'}, 'b'),
    },
    10: {
        'hal_rejection': ('At t14 which original property did Hal reject?', {'a':'B','b':'P','c':'C'}, 'b'),
        'clarke_b': ('At t15 what stance did Clarke take on B?', {'a':'Established truth','b':'Rejected B','c':'Provisionally adopted for discussion'}, 'c'),
        'hal_last': ('Which property did Hal provisionally adopt at t18?', {'a':'Original P','b':'Revised C','c':'B'}, 'b'),
    }
}
SYSTEM = 'Answer multiple-choice questions from the supplied historical record. Reply immediately with a short JSON object with an answers field. Use only the listed option letters. Do not add explanations.'


def build_packets():
    packet=ucl.load_json(BASELINE.read_text(encoding='utf-8'))
    ucl.check(packet)
    by_check={}
    for pos,(actid,speaker,prop,action,target_kind,target_key,note) in enumerate(EVENTS,1):
        target={'claim':'theory','path':[target_key]} if target_kind=='theory' else {'act':target_key,'expression_index':0}
        contribution={
            'act': {'id':actid,'kind':'response','speaker':speaker,'references':['t1'] if target_kind=='theory' else [target_key],
                    'text':note,'expressions':[f'~[{prop}][A]'], 'details':{'responds_to':'t8','stance':'mixed'}},
            'orientation':'L','explanation':f'~[{prop}][A]','conclusion':f'~[{prop}][A]',
            'history_summary': 'All 8 baseline turns and '+str(pos)+' subsequent controlled events retained without omission.',
            'acknowledgements':[{'id':'x'+str(4+pos),'by':actid,'target':target,'action':action,
                                 'qualification':None,'replacement':None,'note':note}]
        }
        if pos==3:contribution['new_definitions']={'C':REVISED}
        packet=author(packet,contribution)
        ucl.check(packet)
        if pos in PROBES:by_check[pos]=packet
    return by_check


def fmt_content(fmt,packet):
    # Same underlying 8-turn baseline + full 10-event prefix, without omitted history.
    if fmt.startswith('ucl_'):
        wire=guide_profiles.encode(packet,'portable' if fmt=='ucl_portable' else 'compact')
        return ucl.canon(wire).decode('ascii')
    if fmt=='structured_english':
        content={
            'definitions':{k:{'id':v['id'],'gloss':v['definition']['gloss']} for k,v in packet['definitions'].items()},
            'claims':packet['claims'],
            'acts':[{'id':act['id'],'speaker':act['speaker'],'text':act['text'],'references':act['references']} for act in packet['discourse']['acts']],
            'acknowledgements':packet['acknowledgements'],
            'history':packet['history'],
        }
        return json.dumps(content,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    if fmt=='english':
        lines=['Historical conversation about a hypothetical system Alpha. Original P = '+packet['definitions']['P']['definition']['gloss'],
               'B = '+packet['definitions']['B']['definition']['gloss']]
        if 'C' in packet['definitions']:lines.append('C = '+packet['definitions']['C']['definition']['gloss'])
        lines += ['The original two-part theory states P and B. These are independent claims, not established observations.']
        act_map={a['id']:a for a in packet['discourse']['acts']}
        ack_map={ack['by']:ack for ack in packet['acknowledgements']}
        for act in packet['discourse']['acts']:
            s=f"Turn {act['id']}, speaker {act['speaker']}: {act['text']}"
            if act['id'] in ack_map:
                a=ack_map[act['id']]
                targ=a['target']
                named=('original P' if targ['path']==[0] else 'B') if 'claim' in targ else 'revised C proposed at t11'
                s+=f" Explicit stance: {a['action']} toward {named}."
            lines.append(s)
        return '\n'.join(lines)
    raise ValueError('Unknown format')


def messages(fmt,packet,checkpoint):
    questions=PROBES[checkpoint]
    qtext='\n'.join(f'{key}: {prompt} OPTIONS '+json.dumps(options,sort_keys=True) for key,(prompt,options,_) in questions.items())
    intro='The following is the complete relevant conversation history. Treat all claims as hypothetical. ' \
          'Use precise distinctions among original P, revised C, and measurable B.\n'
    msgs=[{'role':'system','content':SYSTEM}]
    if fmt=='ucl_compact':
        msgs.append({'role':'system','content':'Locally verified UCL guide for Compact decoding: '+json.dumps(packet['guide'],sort_keys=True,separators=(',',':'))})
    msgs.append({'role':'user','content':intro+fmt_content(fmt,packet)+'\n\nQUESTIONS (return {"answers":{"question_id":"a/b/c"}} only):\n'+qtext})
    return msgs


def evaluate_answer(text,checkpoint):
    try:
        obj=parse_json(text)
        if set(obj)!={'answers'} or type(obj['answers']) is not dict:return None
        supplied=obj['answers']
        if set(supplied)!=set(PROBES[checkpoint]):return None
        if any(value not in ('a','b','c') for value in supplied.values()):return None
        return {k: supplied[k]==v[2] for k,v in PROBES[checkpoint].items()}
    except (ValueError,TypeError,KeyError):return None


def run(client=None,cap=1.0,dry_run=False):
    if not 0<cap<=2:raise ValueError('Estimated budget cap must be >0 and <=2 USD')
    packets=build_packets()
    results=[]; spent=0.;failures=0
    for checkpoint in (5,10):
        for fmt in FORMATS:
            model='clarke-1.0' if checkpoint==5 else 'hal-1.0'
            packet=packets[checkpoint]
            msg=messages(fmt,packet,checkpoint)
            reserve=reserve_upper_bound(model,msg,MAX_OUTPUT)
            if spent+reserve>cap and not dry_run:
                return {'status':'budget_stop','estimated_cost_usd':round(spent,6),'cases':results,'reason':'Estimated pre-call reservation exceeds cap', 'completed':len(results)}
            row={'checkpoint':checkpoint,'format':fmt,'model':model,'prompt_bytes':sum(len(x['content'].encode()) for x in msg),'message_bytes':len(fmt_content(fmt,packet).encode())}
            if dry_run:
                example={'answers':{k:v[2] for k,v in PROBES[checkpoint].items()}}
                score=evaluate_answer(json.dumps(example),checkpoint)
                row.update({'response':example,'score':score,'passed':sum(score.values()),'questions':len(score),'dry_run':True})
            else:
                try:
                    resp=client.chat.completions.create(model=model,messages=msg,max_tokens=MAX_OUTPUT)
                except Exception as e:
                    row['error']='api_error:'+type(e).__name__ # no credential or raw request in report
                    row['passed']=0;row['questions']=len(PROBES[checkpoint]);failures+=1;results.append(row)
                    return {'status':'api_error','estimated_cost_usd':round(spent,6),'cases':results,'completed':len(results)}
                usage=resp.usage
                pin=getattr(usage,'prompt_tokens',None);pout=getattr(usage,'completion_tokens',None)
                spent+=price_estimate(model,pin,pout) if pin is not None and pout is not None else reserve
                content=resp.choices[0].message.content or ''
                score=evaluate_answer(content,checkpoint)
                row.update({'response':safe_text(content),'finish_reason':resp.choices[0].finish_reason,
                            'token_usage':{'input':pin,'output':pout},'score':score,
                            'passed':sum(score.values()) if score else 0,'questions':len(PROBES[checkpoint]),
                            'format_valid':score is not None})
                if score is None: failures+=1
            results.append(row)
    return {'status':'dry_run' if dry_run else 'complete','completed':len(results),
            'estimated_cost_usd':round(spent,6),'format_failures':failures,
            'questions_correct':sum(r['passed'] for r in results),'questions_total':sum(r['questions'] for r in results),
            'cases':results,'limitations':'Scripted 10-event retention test, not autonomous AI dialogue; models see equivalent semantic events, but unequal token and structural overhead. No UCL superiority claim.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--cap-usd',type=float,default=1.0)
    p.add_argument('--output',default='uclbench-long-results.json');a=p.parse_args()
    client=None
    if not a.dry_run:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY repository secret missing')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=90)
    result=run(client,cap=a.cap_usd,dry_run=a.dry_run)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if result['status'] not in ('dry_run','complete'):raise SystemExit(2)
    if a.dry_run and result.get('format_failures'):raise SystemExit(1)

if __name__=='__main__':main()