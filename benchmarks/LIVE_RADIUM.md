# UCLBench live — Radium Cloud (2.0 development only)

A manually triggered, low-cost **exploratory smoke benchmark**, not yet a statistically controlled claim of UCL superiority. No API calls run on pushes or pull requests. The offline dry-run exercises authoring and exact reconstruction without spending money.

## Setup

1. Revoke any API key previously pasted in chat or copied into code. Use a fresh key.
2. Add a GitHub Actions repository secret named `RADIUM_API_KEY` in Settings → Secrets and variables → Actions. This secret is never embedded in a source file.
3. In **Actions → UCLBench live (manual) → Run workflow**, keep `paid_run` set to `no` for the initial dry run. When ready, select `yes`, start with `trials=1`, `cap_usd=0.50`. Choose the main branch to dispatch; the launcher checks out `develop/2.0` to run actual code. A provider-side USD $10 spending limit is separate and recommended.
4. Open the workflow summary and download the `uclbench-live-report` artifact to inspect scores, API-reported token counts and per-format transcripts.

The runner's **per-run cap is a conservative estimate**, not a financial guarantee. Provider charges, tokenization, and hidden reasoning tokens can differ from estimates. `openai` SDK retries are disabled; no automatic workflow trigger spends tokens. The workflow has `permissions: contents: read` and a concurrency group.

## Test procedure

Each trial: a deterministic hypothetical two-part claim P & B and a specified stance on exactly one part. Sender Hal or Clarke produces a handoff. Receiver (the other model) must identify the exact claim path and stance. Four arms: ordinary English, structured English/JSON, UCL Portable, UCL Compact. For UCL, the optional encoder constructs and validates a full self-contained packet from the sender's small structured contribution. Compact's exact guide is supplied in the receiver system prompt: **those prompt tokens are measured and are not free**. Sender outputs requiring a malformed encoding are recorded as authoring failures.

**Important design caveats:** The four conditions do not yet perfectly match informational overhead, sender interface, or the amount of history. Because the UCL arms carry a baseline synthetic conversation, raw token counts must not be interpreted as efficiency measures of the glyph language alone. This run is for authentication, compatibility, mechanics, and preliminary reference-accuracy signals only. Future UCLBench should match task content and add pre-registered, randomized and blinded evaluation.

## Live-test improvements after the first two paid runs

The first Hal-first test produced no visible answer within 192 output tokens. A later 1,024-token trial yielded successful structured English and UCL Portable handoffs, while Hal still produced empty length-limited messages in English and UCL Compact. Those are **model generation/output-budget failures**, not demonstrated semantic failures of those communication formats.

The live harness now sends **Clarke first** for trial 1 and reverses the model roles in trial 2. It reports `author_valid` (mechanically well-formed message), `sender_intent_correct` (whether structured contributions target the intended claim and stance), `correct` (end-to-end receiver answer), `failure_type`, and finish reasons/token usage separately. English sender-intent correctness is left **unscored**, rather than being guessed with naive pattern matching; future independent blind grading is needed. If a sender produces no valid message, the recipient is not tested, and the result must not be described as a comprehension failure.

Use **1 trial and USD $0.25 estimated cap** first, followed by 2 or 4 trials for role reversal and case balance only after checking transcripts. The software cap remains an estimate; the provider-side limit is authoritative. The four arms do not establish UCL superiority: sender interfaces differ, UCL employs a mechanical authoring tool, and the UCL packets include substantial historical context.

## Local commands

```bash
python benchmarks/live_radium.py --dry-run --trials 4 --output dry-run.json
python -m unittest discover -s benchmarks -p 'test_live_radium.py' -v
# Real calls (requires environment variable and pip install openai):
python benchmarks/live_radium.py --trials 1 --cap-usd 0.50 --output result.json
```

**Privacy:** Benchmark results include public synthetic prompts and AI responses; do not feed private data into a public Actions artifact. API keys are never intentionally logged or exported.