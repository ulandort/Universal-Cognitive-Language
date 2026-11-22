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

## Local commands

```bash
python benchmarks/live_radium.py --dry-run --trials 4 --output dry-run.json
python -m unittest discover -s benchmarks -p 'test_live_radium.py' -v
# Real calls (requires environment variable and pip install openai):
python benchmarks/live_radium.py --trials 1 --cap-usd 0.50 --output result.json
```

**Privacy:** Benchmark results include public synthetic prompts and AI responses; do not feed private data into a public Actions artifact. API keys are never intentionally logged or exported.