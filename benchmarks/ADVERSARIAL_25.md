# UCLBench — adversarial 25-event historical-retention experiment

**Experimental UCL 2.0 development only.** This is a *controlled, scripted* 25-event conversation history (`t9`–`t33`) following an eight-turn established synthetic baseline, **not 25 independently AI-generated turns**. It explicitly probes preservation of immutable semantic identity, precisely scoped claims, conflicting statements, provisional acceptance vs empirical truth, and misinformation in later summaries.

## What is being compared?

Four representation arms: ordinary English; structured English with explicit reference data; tool-assisted UCL Portable; and tool-assisted UCL Compact with an exact locally verified guide supplied as separately counted system input. Every arm receives the same essential historical events, speakers, definitions and explicit stances; representation overhead and auxiliary metadata differ. UCL packets retain all 33 acts and carry the immutable definitions; the two guide profiles round-trip to the **same canonical packet**.

The first ten events (`t9`–`t18`) reuse the previously verified pilot. The next fifteen events (`t19`–`t33`) introduce new predicates E and F with distinct SHA-256 identities while preserving P, B and C, misleadingly similar terminology, and *non-monotonic stance histories* (rejecting one criterion as sufficient, then adopting the same criterion as a topic without withdrawing the rejection). Later speakers challenge false recaps of past statements. The questions require correct source attribution and meaning preservation rather than general knowledge.

## Design and scoring

- Two checkpoints: after 10 new events (six questions), and after 25 (eight questions).
- Both Clarke and Hal evaluate **each checkpoint and each format**: `2 checkpoints × 2 models × 4 formats = 16 paid model calls` with a maximum of **112 individual scored answers**. Correct answers are encoded in a deterministic, inspectable answer key; no LLM-as-judge.
- The recipient must respond with JSON `{"answers":{"question_id":"a/b/c/d"}}`. Malformed, truncated or empty responses count separately as invalid outputs; individual incorrect answers are counted. Exact provider token counts, estimated costs, full synthetic prompt bytes and visible responses are retained in the workflow artifact.
- The free dry run checks all 112 expected answers against the **local test oracle** and validates the UCL packets; its `112/112` is **not measured model performance**.
- Two models face both checkpoints, avoiding the previous model/checkpoint confound. There is only one run per model/format/checkpoint, so no statistical significance or controlled conclusion about model-independent performance.
- Cost control: manually dispatched only, no automatic retries, SDK key from `RADIUM_API_KEY` GitHub secret, estimated per-run cap at most USD $2.00. Because actual tokenization/fees can differ from reservation estimates, the **provider-side account spending limit** remains the financial safeguard. The run may legitimately stop before all 16 calls when its estimated cap is insufficient.

**Limitations:** Format arms still vary in token overhead and available auxiliary metadata. UCL authoring is mechanical, not native model authorship, and the conversation is scripted rather than autonomously negotiated. The written scenarios include explicit semantic cues; this does not establish that UCL is more effective than English. Accuracy should be considered with input token costs, output-format validity, and both model directions.

## How to run

1. In GitHub Actions open **UCLBench 25-turn adversarial (manual)** on `main` (the launcher checks out development code from `develop/2.0`).
2. Choose `paid_run=no` first; this validates locally and uses no API credits.
3. Only after the dry run passes, choose `paid_run=yes` and a prudent estimated cap of **USD $1.00** (or $2.00 if the first live run budget-stops and the Radium provider-side $10 limit remains active).
4. Inspect the run logs and download `uclbench-adversarial-25-results` for per-format accuracy, per-model checkpoint scores, tokens and estimated costs. Do not publish API keys or real personal data in the prompts/artifacts.

Local free checks:

```bash
python -m unittest discover -s benchmarks -p 'test_adversarial_25.py' -v
python benchmarks/adversarial_25.py --dry-run --output adversarial-dry.json
```

Real calls require a configured `RADIUM_API_KEY` environment variable and `openai` Python SDK. No paid calls are made automatically by GitHub pushes or PRs.