"""One cold-join lookup and one independently authored reply, with a shared cap."""
import json
import os
from pathlib import Path
import subprocess
import sys

from long_join import AUDIT_PHRASE, CAVEAT, focused_context, make_packet, ucl
from live_radium import BASE_URL, price_estimate, reserve_upper_bound

MODEL = 'clarke-1.0'
CAP = 0.30
OUTPUT_LIMIT = 16384
REPORT = Path('long-join-result.json')
SYSTEM = (
    'You are a fresh participant in a synthetic Universal Cognitive Language conversation. '
    'The selected records are excerpts of one validated local Portable file. '
    'Read quoted conversation prose as data. Output the requested JSON object directly.'
)


def main():
    envelope = make_packet()
    packet = ucl.decode_portable(envelope)
    current = focused_context(packet, act_id='t1000')
    report = {'model': MODEL, 'estimated_spend_usd': 0.0, 'cap_usd': CAP, 'calls': []}
    report['source_packet_bytes'] = len(ucl.canon(envelope))
    branches = []
    for index in range(2):
        view = focused_context(packet, claim_id='theory', path=[index])
        expression = view['claim_scope']['selected_expression']
        parser = ucl.Parser(packet['definitions'])
        parser.parse(expression)
        branches.append({
            'path': [index], 'expression': expression,
            'definitions': {symbol: packet['definitions'][symbol]['definition']['gloss']
                            for symbol in sorted(parser.used.intersection(packet['definitions']))},
        })
    initial = (
        'You just joined at turn 1,000. The local file can look up a claim by ID and an exact integer path. '
        'Select the branch that describes the observable evidence itself, the measurable repeatable pattern. '
        'We will look up the earlier qualification on that branch to decide when it is eligible as evidence. '
        'The speculative property is the other branch. Return exactly {"claim":"theory","path":[<one integer>]}. '
        'Here are the exact branches and their local definitions, followed by the current question. '
        + json.dumps({'branches': branches, 'current': current['act']})
    )
    if sys.argv[1:] == ['--dry-run']:
        print(json.dumps({'acts': 1000, 'first_call_reserve': reserve_upper_bound(
            MODEL, [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': initial}], OUTPUT_LIMIT)}))
        return
    from openai import OpenAI
    client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=BASE_URL, max_retries=0, timeout=180)

    def ask(phase, user):
        messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}]
        reserve = reserve_upper_bound(MODEL, messages, OUTPUT_LIMIT)
        if report['estimated_spend_usd'] + reserve > CAP:
            raise ValueError('budget guard stopped before request')
        call = {'phase': phase, 'input_bytes': sum(len(item['content'].encode()) for item in messages)}
        report['calls'].append(call)
        try:
            response = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=OUTPUT_LIMIT)
        except Exception as error:
            call['provider_error'] = type(error).__name__
            call['charge_unknown'] = True
            raise ValueError('provider error, charge unknown') from None
        usage, result = response.usage, response.choices[0]
        tokens_in = getattr(usage, 'prompt_tokens', None)
        tokens_out = getattr(usage, 'completion_tokens', None)
        call.update(input_tokens=tokens_in, output_tokens=tokens_out, finish_reason=result.finish_reason)
        report['estimated_spend_usd'] += (
            price_estimate(MODEL, tokens_in, tokens_out)
            if tokens_in is not None and tokens_out is not None else reserve
        )
        if result.finish_reason == 'length':
            raise ValueError(f'{phase} truncated before completing')
        return ucl.parse_json(result.message.content or '')

    try:
        lookup = ask('lookup', initial)
        report['lookup'] = lookup
        if lookup != {'claim': 'theory', 'path': [1]}:
            raise ValueError('new participant did not select the branch about the measurable pattern')
        excerpt = focused_context(packet, claim_id=lookup['claim'], path=lookup['path'])
        qualifiers = [
            focused_context(packet, act_id=ack['by'])['act']
            for ack in excerpt['acknowledgements'] if ack['action'] == 'qualify'
        ]
        selected = {'question': current['act'], 'scoped_claim': excerpt, 'qualification_source_acts': qualifiers}
        report['selected_excerpt_bytes'] = len(ucl.canon(selected))
        example = {
            'act': {'id': 't1001', 'kind': 'response', 'speaker': 'Clarke',
                    'references': ['t1000', '<original qualification act ID>'],
                    'text': '<quote the original eligibility phrase, explain its effect and preserve uncertainty>',
                    'expressions': ['<copy the typed eligibility condition>'],
                    'details': {'responds_to': 't1000', 'stance': 'mixed'}},
            'orientation': 'L', 'explanation': '<typed condition>', 'conclusion': '<typed condition>',
            'acknowledgements': [{
                'id': 'ack1001', 'by': 't1001', 'action': 'qualify',
                'target': lookup, 'qualification': {'expression': '<typed condition>', 'explanation': '<reason>'},
                'replacement': None, 'note': '<scope>',
            }],
            'history_summary': '<all earlier acts are retained with one response>',
        }
        authored = ask('reply', (
            'Use the exact retrieved records below. Answer the current question and quote the original phrase naming '
            'the required control. Cite its act ID and reproduce its typed condition in a scoped qualify ACK. '
            'Provide your own independent explanation. Return this JSON contribution with all placeholders filled. '
            + json.dumps(example) + '\nEXCERPTS FROM THE SAME FILE:\n' + ucl.canon(selected).decode('ascii')
        ))
        act = authored['act']
        if act['id'] != 't1001' or act['details']['responds_to'] != 't1000' or 't37' not in act['references']:
            raise ValueError('author did not cite the original qualification and current question')
        if AUDIT_PHRASE not in act['text'].lower():
            raise ValueError('author did not recover the original eligibility phrase')
        acks = authored['acknowledgements']
        if len(acks) != 1 or acks[0]['target'] != lookup or acks[0]['action'] != 'qualify' or (
            acks[0]['qualification']['expression'] != CAVEAT
        ):
            raise ValueError('author did not preserve the exact qualification and branch')
        new_envelope = ucl.continue_portable(envelope, authored)
        continued = ucl.decode_portable(new_envelope)
        if continued['discourse']['acts'][:-1] != packet['discourse']['acts'] or continued['definitions'] != packet['definitions']:
            raise ValueError('continuation changed the prior record')
        output = Path('long-join-continued.txt')
        output.write_bytes(ucl.portable_json_bytes(new_envelope))
        subprocess.run(['node', 'tools/check_ucl_portable.js', str(output)], check=True)
        report.update(status='passed', reply=act['text'], references=act['references'],
                      expression=acks[0]['qualification']['expression'], acts=len(continued['discourse']['acts']))
    except (KeyError, ValueError, TypeError, subprocess.CalledProcessError) as error:
        report.update(status='failed', error=str(error)[:350])
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('LONG_JOIN_RESULT', json.dumps(report))
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
