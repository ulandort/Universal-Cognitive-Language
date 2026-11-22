# UCLBench 10-turn semantic-retention pilot (experimental)

**The 10-turn sequence is a fixed, pre-specified, synthetic scenario, not a freely generated 10-turn conversation between independent AIs.** The benchmark adds events `t9`–`t18` to the existing synthetic eight-turn corpus. It uses the same underlying historical information for ordinary English, structured English, UCL Portable and UCL Compact. The two AI models answer multiple-choice historical-meaning questions at checkpoints 5 and 10. This isolates **semantic retention/comprehension** from generative dialogue behavior and supplies an objective answer key. We should build autonomous dialogue as a separate future arm.

## Scenario and scoring

- The initial theory contains a **speculative P** and **separate measurable B**.
- At `t11`, Clarke introduces **C** as a distinct immutable definition; its criterion is conceptual internal consistency, not observed B.
- Later speakers target *specific* old claims or acts, sometimes rejecting them and sometimes adopting them **only for discussion**. The source transcript preserves all 18 acts and every active definition.
- Two checkpoints (after five and ten newly scripted events) each present three questions about original meaning, new-vs-old definition identity, precise rejection scope, and provisional-versus-factual stance. Answers are scored against hard-coded ground truth, not by an LLM judge.
- Four format arms × two checkpoints = **eight paid calls** by default: **Clarke** at the five-event checkpoint and **Hal** at the ten-event checkpoint. There are six questions per format (24 total) but the six answers come in two API calls. Inputs include full relevant conversation history in every arm, though wire-format and guide overhead differ substantially.
- The UCL arms use the reference `author()` tool to construct complete valid packets; this is **tool-assisted UCL**, not native AI authorship. Compact receives an exact local guide in the system context, and its tokens are counted. Ordinary English omits machine formalism but retains all conversation text and states.
- Capture completion status, model, input/output tokens, visible response, scored answers, and estimated USD cost. No automatic retry. A pre-call estimated-reservation guard stops starting new calls when a given budget would be exceeded. **This guard cannot guarantee provider-side billing limits.**

This is an **exploratory controlled pilot**, not a randomized blinded comparison or proof UCL outperforms English. In particular, Hal and Clarke are tested at different checkpoint difficulties, and base transcript/context representation differs between arms. Do not interpret single-run percentage differences as meaningful evidence; conduct role-balanced, independently repeated runs later.

## Running

On the GitHub Actions page, open **UCLBench 10-turn (manual)**, choose `main` branch, start with `paid_run=no`, then use `paid_run=yes` and a conservative estimated budget such as **USD $1.00** after verifying the dry-run.

Local dry run, no API key required:

```bash
python -m unittest discover -s benchmarks -p 'test_long_conversation.py' -v
python benchmarks/long_conversation.py --dry-run --output long-dry-run.json
```

Paid call with the `RADIUM_API_KEY` environment variable (requires `openai` SDK):

```bash
python benchmarks/long_conversation.py --cap-usd 1.00 --output long-results.json
```

All examples and prompts contain **synthetic information**. Never send secrets or private data through the benchmark runner or its downloadable, potentially public GitHub Actions artifacts.