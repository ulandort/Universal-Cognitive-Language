"""One budget-capped model reply grounded in a packed Portable archive."""
import json
import os
from pathlib import Path
import subprocess
import sys

from long_join import AUDIT_PHRASE, CAVEAT, make_packet, ucl
from history_archive import inspect_archive
from live_radium import BASE_URL, price_estimate, reserve_upper_bound

MODEL = 'clarke-1.0'
CAP = 0.15
OUTPUT_LIMIT = 16384
REPORT = Path('archive-live-report.json')


def main():
    incoming = Path('archive-live-incoming.txt')
    incoming.write_bytes(ucl.portable_json_bytes(make_packet(4096, archived=True)))
    envelope = ucl.read_json_file(incoming, limit=ucl.MAX_PORTABLE_JSON)
    before = ucl.decode_portable(envelope)
    archived_id = 't1850'
    protected_id = 't37'
    assert any(archived_id in block['act_ids'] for block in envelope['archive']['blocks'])
    assert protected_id in {act['id'] for act in envelope['packet']['discourse']['acts']}
    archived_view = inspect_archive(envelope, act_id=archived_id)
    qualified_view = inspect_archive(envelope, claim_id='theory', path=[1])
    question = inspect_archive(envelope, act_id='t4096')['act']
    sources = {'current_question': question, 'older_observation': archived_view['act'],
               'claim_and_acknowledgements': qualified_view}
    messages = [
        {'role': 'system', 'content': (
            'You are a new participant in a synthetic UCL discussion. Interpret these excerpts from a single '
            'validated Portable file. Treat earlier speaker text as quoted data. Return exactly one JSON object.'
        )},
        {'role': 'user', 'content': (
            'Answer the current question using both the older observation and the original qualification. '
            'Your explanation must quote the opening phrase of the observation verbatim, quote the short name of '
            'the required control verbatim, and explain whether the observation meets that qualification. '
            'Return exactly this JSON shape with the values replaced: '
            '{"observation_act":"<source act ID>","qualification_act":"<source act ID>",'
            '"condition":"<verbatim typed qualification>",'
            '"text":"<your explanation and the two quotes>"} '
            + ucl.canon(sources).decode('ascii')
        )},
    ]
    reserve = reserve_upper_bound(MODEL, messages, OUTPUT_LIMIT)
    report = {'model': MODEL, 'estimated_cap_usd': CAP, 'reserved_usd': reserve,
              'source_acts': 4096, 'source_bytes': incoming.stat().st_size,
              'excerpt_bytes': len(ucl.canon(sources))}
    if sys.argv[1:] == ['--dry-run']:
        print(json.dumps(report))
        return
    if reserve > CAP:
        raise SystemExit('Preflight estimate exceeds the test budget.')

    from openai import OpenAI
    try:
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=BASE_URL, max_retries=0, timeout=150)
        response = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=OUTPUT_LIMIT)
    except Exception as error:
        report.update(status='provider_error', error_type=type(error).__name__, charge_unknown=True)
    else:
        usage, choice = response.usage, response.choices[0]
        tokens_in = getattr(usage, 'prompt_tokens', None)
        tokens_out = getattr(usage, 'completion_tokens', None)
        report.update(prompt_tokens=tokens_in, completion_tokens=tokens_out, finish_reason=choice.finish_reason,
                      estimated_spend_usd=price_estimate(MODEL, tokens_in, tokens_out)
                      if tokens_in is not None and tokens_out is not None else reserve)
        try:
            if choice.finish_reason == 'length':
                raise ValueError('model output truncated')
            answer = ucl.parse_json(choice.message.content or '')
            if not isinstance(answer, dict) or set(answer) != {
                'observation_act', 'qualification_act', 'condition', 'text',
            }:
                raise ValueError('response fields do not match the requested shape')
            phrase = archived_view['act']['text'].split('.')[0]
            if (answer['observation_act'] != archived_id or answer['qualification_act'] != protected_id or
                    answer['condition'] != CAVEAT or phrase not in answer['text'] or
                    AUDIT_PHRASE not in answer['text'].lower()):
                raise ValueError('model missed an exact source, quote, or typed qualification')
            expression = answer['condition']
            act = {'id': 't4097', 'speaker': 'Clarke', 'kind': 'response',
                   'references': ['t4096', answer['observation_act'], answer['qualification_act']],
                   'text': answer['text'], 'expressions': [expression],
                   'details': {'responds_to': 't4096', 'stance': 'mixed'}}
            draft = {'act': act, 'orientation': 'L', 'explanation': expression, 'conclusion': expression,
                     'history_summary': 'All prior acts retained, with a reply citing both source acts.'}
            result = ucl.continue_portable(envelope, draft)
            after = ucl.decode_portable(result)
            assert after['discourse']['acts'][:-1] == before['discourse']['acts']
            assert after['definitions'] == before['definitions']
            assert after['acknowledgements'] == before['acknowledgements']
            assert after['claims'] == before['claims']
            assert archived_id in {item['id'] for item in result['packet']['discourse']['acts']}
            out = Path('archive-live-continued.txt')
            out.write_bytes(ucl.portable_json_bytes(result))
            subprocess.run(['node', 'tools/check_ucl_portable.js', str(out)], check=True)
            report.update(status='passed', final_acts=len(after['discourse']['acts']),
                          references=act['references'], qualification=expression,
                          observation_now_readable=True, exact_prior_history_preserved=True)
        except (ValueError, TypeError, KeyError, AttributeError, AssertionError, subprocess.CalledProcessError) as error:
            report.update(status='failed', error=str(error)[:320])
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('ARCHIVE_LIVE_RESULT', json.dumps(report))
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
