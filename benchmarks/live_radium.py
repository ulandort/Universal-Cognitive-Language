#!/usr/bin/env python3
"""UCLBench live Radium API smoke runner. Experimental, not a scientific benchmark.

Manual use only. Never logs or stores credentials. No API calls on --dry-run.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tools')]
import ucl
import guide_profiles
from author import author

BASELINE = ROOT / 'examples/cross_model_conversation_8_turns.json'
PRICES = {'hal-1.0': (2.00, 10.00), 'clarke-1.0': (0.75, 4.50), 'tycho-1.0': (0.10, 1.50)}
FORMATS = ('english', 'structured_english', 'ucl_portable', 'ucl_compact')
MODEL_CHOICES = ('hal-1.0', 'clarke-1.0')
MAX_OUTPUT = 1024
BASE_URL = 'https://api.radium.cloud/v1'
SYSTEM = 'You are participating in a controlled message-relay benchmark. Give the requested short final response immediately. Follow the requested response format precisely. Do not discuss the test.'


def parse_json(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text, flags=re.I).strip()
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError('Response must be a JSON object')
    return obj


def case_for(index):
    # Balanced across two propositions and two possible stances; public, deterministic seed.
    path = (index // 2) % 2
    action = ('reject', 'adopt-for-discussion')[index % 2]
    return {'claim_id': 'theory', 'path': path, 'action': action}


def sender_prompt(fmt, case):
    prop = 'P' if case['path'] == 0 else 'B'
    header = ('Original speaker A proposes that hypothetical system Alpha has P AND B. '
              'P means speculative convergence; B means a separate measurable convergence pattern. '
              'You are speaker H. Your intention is to '+('reject' if case['action']=='reject' else 'provisionally adopt for discussion')+
              ' ONLY the '+prop+' component, WITHOUT taking a stance on the other component. '
              'Send a short message to a different AI; no conclusions about real-world truth.')
    if fmt == 'english':
        return header + '\nWrite your handoff in natural English, maximum 90 words, and do not include instructions to the recipient.'
    if fmt == 'structured_english':
        return header + '\nWrite one JSON object with keys claim_id ("theory"), target_path (an array containing the 0-based index of the component you address), action ("reject" or "adopt-for-discussion"), and note (short plain English). Nothing else.'
    return header + '\nWrite one JSON object containing exactly action ("reject" or "adopt-for-discussion"), path (0 or 1), and note (a short explanation). These are the data for a mechanical UCL authoring tool. Do not generate SHA hashes, full packets, Markdown fences or other keys.'


def build_handoff(fmt, case, sender_text, baseline):
    if fmt == 'english':
        return sender_text.strip(), {'syntax_ok': True}
    data = parse_json(sender_text)
    if fmt == 'structured_english':
        if set(data) != {'claim_id', 'target_path', 'action', 'note'} or data['claim_id'] != 'theory' or not isinstance(data['target_path'], list) or len(data['target_path']) != 1 or type(data['target_path'][0]) is not int or data['target_path'][0] not in (0, 1) or data['action'] not in ('reject','adopt-for-discussion') or not isinstance(data['note'],str):
            raise ValueError('Malformed structured-English handoff')
        return json.dumps(data, ensure_ascii=True, sort_keys=True), {'syntax_ok': True}
    if set(data) != {'action','path','note'} or type(data['path']) is not int or data['path'] not in (0,1) or data['action'] not in ('reject','adopt-for-discussion') or not isinstance(data['note'],str) or len(data['note']) > 1000:
        raise ValueError('Malformed UCL author input')
    prop='P' if data['path'] == 0 else 'B'
    contrib = {
        'act': {'id':'t9','kind':'response','speaker':'H','references':['t1','t8'],
                'text':'Speaker H states a position on exactly one component of the earlier theory. '+data['note'],
                'expressions':[f'~[{prop}][A]'],
                'details':{'responds_to':'t8','stance':'mixed'}},
        'orientation':'L','explanation':f'~[{prop}][A]','conclusion':f'~[{prop}][A]',
        'acknowledgements':[{'id':'x5','by':'t9','target':{'claim':'theory','path':[data['path']]},
                             'action':data['action'],'qualification':None,'replacement':None,'note':data['note']}],
        'history_summary':'All previous acts retained; t9 adds a single precisely scoped stance.'
    }
    packet=author(baseline,contrib)
    ucl.check(packet)
    wire=guide_profiles.encode(packet,'portable' if fmt=='ucl_portable' else 'compact')
    # Readability vs measurement: compact's rule set is supplied to the receiver
    # as a separate system message. Count it as context; it isn't free.
    return json.dumps(wire, separators=(',', ':'), sort_keys=True,ensure_ascii=True), {'syntax_ok': True, 'packet_hash':packet['integrity']['sha256']}


def receiver_messages(fmt, handoff, baseline):
    messages=[{'role':'system','content':SYSTEM}]
    if fmt=='ucl_compact':
        messages.append({'role':'system','content':'The following is a locally available, trusted exact UCL language guide for this session. Apply it to the compact-guide packet: '+json.dumps(baseline['guide'],sort_keys=True,separators=(',',':'))})
    instruct='A different AI has sent a message about a prior two-part claim. Original claim ID theory: Alpha has property P AND property B; P is the first part (index 0), B the second (index 1). What single claim component did that AI take a stance on, and what was its stance? Reply with ONLY a JSON object containing action (reject or adopt-for-discussion) and path (0 or 1). Do not infer any other stance. '
    if fmt.startswith('ucl_'):
        instruct+='Read the latest acknowledgement by t9; it targets a claim subtree path. Compact guide is supplied separately in system instructions if necessary. '
    messages.append({'role':'user','content':instruct+'\nMESSAGE:\n'+handoff})
    return messages


def price_estimate(model, prompt_tokens, completion_tokens):
    ip,op=PRICES[model]
    return (prompt_tokens*ip+completion_tokens*op)/1_000_000


def reserve_upper_bound(model, messages, max_output=MAX_OUTPUT):
    # Deliberately conservative: at most one billable input token per UTF-8 byte
    # for ordinary text; API-specific tokenization and hidden fees still possible.
    utf8_bytes=sum(len(m['content'].encode('utf-8')) for m in messages)
    return price_estimate(model, utf8_bytes+1024, max_output)


def safe_text(text):
    # Avoid accidentally copying API-like secrets into artifacts.
    return re.sub(r'sk[_-][a-zA-Z0-9_-]{12,}', '[REDACTED]', text)[:120000]


def run(client, trials=1, cap=0.50, dry_run=False):
    if not 1 <= trials <= 8:raise ValueError('Trials must be 1–8')
    if not 0 < cap <= 2:raise ValueError('Per-run budget cap must be >0 and <= $2')
    baseline=ucl.load_json(BASELINE.read_text());ucl.check(baseline)
    records=[];cost=0.;failures=0
    for trial in range(trials):
        case=case_for(trial)
        for fmt in FORMATS:
            sender=MODEL_CHOICES[trial % 2]
            receiver=MODEL_CHOICES[(trial+1) % 2]
            sender_msg=[{'role':'system','content':SYSTEM},{'role':'user','content':sender_prompt(fmt,case)}]
            reservation=reserve_upper_bound(sender,sender_msg)
            if cost+reservation>cap:
                return {'status':'budget_stop','spent_usd_estimate':round(cost,6),'completed':len(records),'cases':records,'reason':'Pre-call cost reserve exceeds cap'}
            if dry_run:
                # Exercise mechanical UCL construction without API usage.
                if fmt=='english': example='I reject only the P component; I take no position on B.'
                elif fmt=='structured_english':example=json.dumps({'claim_id':'theory','target_path':[case['path']],'action':case['action'],'note':'Stance only on one subclaim.'})
                else:example=json.dumps({'path':case['path'],'action':case['action'],'note':'One component only.'})
                try:
                    handoff,meta=build_handoff(fmt,case,example,baseline)
                    msgs=receiver_messages(fmt,handoff,baseline)
                    ok=True
                except Exception as exc:
                    ok=False;failures+=1;meta={'error':repr(exc)};msgs=[]
                records.append({'trial':trial,'format':fmt,'sender':sender,'receiver':receiver,'dry_run':True,'author_valid':ok,'bytes':sum(len(x['content'].encode()) for x in msgs),'details':meta})
                continue
            sender_resp=client.chat.completions.create(model=sender,messages=sender_msg,max_tokens=MAX_OUTPUT)
            sender_text=sender_resp.choices[0].message.content or ''
            usage=getattr(sender_resp,'usage',None)
            actual_in=getattr(usage,'prompt_tokens',None)
            actual_out=getattr(usage,'completion_tokens',None)
            cost += price_estimate(sender, actual_in, actual_out) if actual_in is not None and actual_out is not None else reservation
            row={'trial':trial,'format':fmt,'sender':sender,'receiver':receiver,'intended':case,'sender_response':safe_text(sender_text), 'sender_usage':{'input':actual_in,'output':actual_out},'sender_finish_reason':getattr(sender_resp.choices[0],'finish_reason',None)}
            try:
                handoff,meta=build_handoff(fmt,case,sender_text,baseline)
                row['author_valid']=True
                row.update(meta)
            except Exception as exc:
                row['author_valid']=False;row['error']=str(exc);row['correct']=False;failures+=1;records.append(row);continue
            msgs=receiver_messages(fmt,handoff,baseline)
            reserve=reserve_upper_bound(receiver,msgs)
            if cost+reserve>cap:
                row['receiver_skipped']='budget reserve exceeded';records.append(row)
                return {'status':'budget_stop','spent_usd_estimate':round(cost,6),'completed':len(records),'cases':records,'reason':'Receiver request reserve exceeds cap'}
            rec_resp=client.chat.completions.create(model=receiver,messages=msgs,max_tokens=MAX_OUTPUT)
            rec_text=rec_resp.choices[0].message.content or ''
            usage=getattr(rec_resp,'usage',None)
            pi=getattr(usage,'prompt_tokens',None);co=getattr(usage,'completion_tokens',None)
            cost+=price_estimate(receiver,pi,co) if pi is not None and co is not None else reserve
            row['receiver_response']=safe_text(rec_text)
            row['receiver_usage']={'input':pi,'output':co}
            row['receiver_finish_reason']=getattr(rec_resp.choices[0],'finish_reason',None)
            row['wire_bytes']=len(handoff.encode())
            row['receiver_prompt_bytes']=sum(len(m['content'].encode()) for m in msgs)
            try:
                ans=parse_json(rec_text)
                row['correct']=set(ans)=={'action','path'} and ans['action']==case['action'] and type(ans['path']) is int and ans['path']==case['path']
            except (ValueError,TypeError,KeyError):row['correct']=False
            if not row['correct']:failures+=1
            records.append(row)
    return {'status':'dry_run' if dry_run else 'complete','completed':len(records),'spent_usd_estimate':round(cost,6),'failures':failures,'cases':records,'warning':'Exploratory small-sample smoke test; no statistically significant claims. API charges may differ from estimate. Empty visible model responses are protocol/output failures, not demonstrated UCL semantic failures.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--trials',type=int,default=1)
    ap.add_argument('--cap-usd',type=float,default=0.50)
    ap.add_argument('--output',default='uclbench-live-results.json')
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    if args.dry_run:client=None
    else:
        key=os.environ.get('RADIUM_API_KEY')
        if not key:raise SystemExit('RADIUM_API_KEY is not set. Add it as a GitHub Actions repository secret.')
        from openai import OpenAI
        client=OpenAI(api_key=key,base_url=BASE_URL,max_retries=0,timeout=90.0)
    result=run(client,args.trials,args.cap_usd,args.dry_run)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n')
    brief={k:v for k,v in result.items() if k!='cases'}
    print(json.dumps(brief,indent=2))
    if result['status']=='budget_stop': raise SystemExit(2)
    if result['status']=='dry_run' and result.get('failures'):raise SystemExit(1)

if __name__=='__main__':main()