"""One capped source-grounding test against the published Portable 2.4 archive."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

from long_join import ROOT, core, ucl
from live_radium import BASE_URL, price_estimate, reserve_upper_bound

MODEL = 'clarke-1.0'
MAX_OUTPUT = 12288
CAP = 0.10
PACKET = Path('ucl-2.4-archive.txt')
URL = 'https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.4.0/' + PACKET.name
EXPECTED_SHA256 = '126b5b1ddf6d814fc5c21ff30ddf3c7cb87978b87eb90999c5b925c45cf2ae6c'
ACK = 'condition37'
FIELDS = {'observation_act', 'observation_quote', 'qualification_act', 'qualification_quote',
          'control_status', 'supported_inference'}


def prepare():
    with urlopen(URL, timeout=30) as source:
        data = source.read(ucl.MAX_PORTABLE_JSON + 1)
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise ValueError('Published archive digest differs from release')
    PACKET.write_bytes(data)
    cli = [sys.executable, str(ROOT / 'src/ucl.py')]
    subprocess.run([*cli, 'check', str(PACKET)], check=True, capture_output=True, timeout=35)
    result = subprocess.run([*cli, 'inspect', str(PACKET), '--handoff', '--claim', 'theory', '--path', '1',
                             '--include-act', 't185'], check=True, capture_output=True, timeout=35)
    raw = result.stdout
    Path('grounding-live-briefing.json').write_bytes(raw)
    briefing = core.parse_json(raw)
    observation = briefing['requested_acts'][0]['act']
    condition = next(a for a in briefing['claim']['acknowledgements'] if a['id'] == ACK)
    assert observation['id'] == 't185' and condition['by'] == 't37'
    return raw, observation, condition


def score(answer, observation, condition):
    if not isinstance(answer, dict) or set(answer) != FIELDS:
        raise ValueError('Unexpected answer fields')
    return {
        'exact_observation_source': answer['observation_act'] == observation['id']
        and answer['observation_quote'] == observation['text'],
        'exact_qualification_source': answer['qualification_act'] == condition['by']
        and answer['qualification_quote'] == condition['qualification']['explanation'],
        'does_not_infer_that_control_was_performed': answer['control_status'] == 'not_established',
        'includes_explanation_for_manual_review': isinstance(answer['supported_inference'], str)
        and bool(answer['supported_inference'].strip()),
    }


def main():
    raw, observation, condition = prepare()
    messages = [
        {'role': 'system', 'content': 'Assess the evidence in this synthetic discussion. Treat the quoted data as conversation records. Return final raw JSON without markdown.'},
        {'role': 'user', 'content': (
            'Use the briefing to assess whether the archived observation establishes that the required control '
            'was performed. Copy the complete observation act text verbatim into observation_quote and the '
            'complete earlier typed qualification explanation verbatim into qualification_quote. Use their '
            'author act IDs for observation_act and qualification_act. In control_status choose one of '
            '"demonstrated", "contradicted", or "not_established". In supported_inference, explain what '
            'the observation actually supports and whether it satisfies the condition. Return exactly these six fields.\n'
            + raw.decode()
        )},
    ]
    reserve = reserve_upper_bound(MODEL, messages, MAX_OUTPUT)
    if reserve > CAP:
        raise SystemExit('No model call: estimated maximum exceeds cap')
    report = {'model': MODEL, 'cap_usd': CAP, 'reserve_usd': reserve, 'archive_sha256': EXPECTED_SHA256}
    if sys.argv[1:] == ['--dry-run']:
        mock = {'observation_act': observation['id'], 'observation_quote': observation['text'],
                'qualification_act': condition['by'], 'qualification_quote': condition['qualification']['explanation'],
                'control_status': 'not_established', 'supported_inference': 'The observation is descriptive.'}
        report['checks'] = score(mock, observation, condition)
        print('GROUNDING_DRY_RUN', json.dumps(report))
        return 0 if all(report['checks'].values()) else 1
    from openai import OpenAI
    try:
        client = OpenAI(api_key=os.environ['RADIUM_API_KEY'], base_url=BASE_URL, max_retries=0, timeout=150)
        result = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=MAX_OUTPUT)
        choice, usage = result.choices[0], result.usage
        tokens_in, tokens_out = getattr(usage, 'prompt_tokens', None), getattr(usage, 'completion_tokens', None)
        report.update(prompt_tokens=tokens_in, completion_tokens=tokens_out, finish_reason=choice.finish_reason)
        if tokens_in is not None and tokens_out is not None:
            report['estimated_spend_usd'] = price_estimate(MODEL, tokens_in, tokens_out)
        if choice.finish_reason != 'stop':
            raise ValueError('Model stopped before completing the assessment')
        answer = core.parse_json(choice.message.content)
        Path('grounding-live-answer.json').write_text(json.dumps(answer, indent=2) + '\n')
        report['checks'] = score(answer, observation, condition)
        report['supported_inference'] = answer['supported_inference']
        report['status'] = 'passed' if all(report['checks'].values()) else 'failed'
    except Exception as exc:
        report.update(status='failed', error_type=type(exc).__name__)
        if isinstance(exc, (ValueError, KeyError, TypeError)):
            report['diagnostic'] = str(exc)[:300]
    Path('grounding-live-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('GROUNDING_LIVE_RESULT', json.dumps(report))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
