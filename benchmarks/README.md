# UCLBench — reproducible benchmarks and conformance tests

UCLBench includes deterministic offline validation and experimental live-model research. **The current public transport is UCL/2.4 Portable**; archived comparison scripts may reproduce experimental profiles, and results from different profiles must not be pooled as if they were the same protocol.

```bash
python -m unittest discover -s tests -p 'test_release.py' -v
python -m unittest discover -s benchmarks -p 'test_*.py' -v
python benchmarks/offline_suite.py --iterations 1000 --seed 2026 --out uclbench-results.json
```

The base Python reference is standard-library-only. Full cross-language Portable tests use Node.js and check current and archived envelopes, embedded rulebooks, inner packets, and optional formula roles; no network or paid service is required. Offline validation shows mechanical conformance, **not** independent semantic comprehension.

## Long-history storage and live retrieval

The [2.2 stress test](../docs/UCL_LONG_CONVERSATIONS.md#100000-act-stress-test) packed 100,000 synthetic acts into 4.02 MB and verified a continuation to act 100,001. The [live archive run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45442609497) used labeled excerpts and validated Clarke’s reply as act 4,097.

## Independently authored results

| Trial | Delivered / attempted | First-try valid | Notes |
|---|---:|---:|---|
| Native AI conversation | 16/16 | 13/16 | Model-authored UCL, permitted repairs |
| Concept Genesis CG-1 | 6/6 | 4/6 | Six new typed immutable concepts |
| Relational Reasoning RR-1 | 6/6 | 3/6 | Multi-concept combinations; original sidecar-length gate |
| Autonomous L25 | 23/25 | 2/25 | 23/30 rejected attempts due to **benchmark-only** short interpretation notes |
| **Autonomous L50** | **48/50** | **45/50** | 91 retained acts; all five prompted reference probes validated |

The [L25 evidence](AUTONOMOUS_25.md) explicitly distinguishes an artificial auxiliary rule from actual UCL failures; the [L50 evidence](AUTONOMOUS_50_RESULTS.md) provides the full failure taxonomy and limitations. Intellectual disagreement is **not** a validation error. These tests do not establish UCL's superiority over English and do not by themselves prove full semantic understanding.

Historical experiments: [native authorship](NATIVE_AUTHORING.md), [FR-1](formula_roles_experiment.py), [25-event scripted benchmark](ADVERSARIAL_25.md) and [comparative English/UCL dialogues](LIVE_DIALOGUE.md). Archived GitHub Actions artifacts have finite retention; the run links and recorded checksums are provenance, not a permanent raw-transcript hosting guarantee.

## Cold-recipient adversarial source-fidelity result (live UCL/2.0)

In a fresh, two-model test using the six **actually model-invented** CG-2 concept definitions, recipients answered eight predeclared source-fidelity questions with and without a false third-party recap. [Full findings](COLD_RECIPIENT_ATTACK_RESULTS.md): UCL/2.0 **32/32**, matched structured English **32/32** (including **16/16 attacked** in each arm); 8/8 valid responses, software-estimated **$0.187411 USD** total. Neither format was misled in this small, explicitly warned scenario. UCL used **34,531 input tokens** compared with **21,813** for structured English. A result in one test does not establish general superiority or prompt-injection security.

## Additional live results

| Experiment | Observed result | What was checked |
|---|---|---|
| **Post-release Concept Genesis CG-2** | **7/8 delivered; 6 novel definitions; 6/6 identity receipts** | Independently authored concepts, precise critique, counterexamples, and evolving disagreement ([full CG-2 results](CG2_POSTRELEASE_RESULTS.md)) |
| **UCL/2.0 vs structured English** | **UCL 56/56; structured English 48/56** strict-schema answers | UCL: 8/8 valid outputs; English: 7/8. The English malformed response nevertheless contained all 8 correct choices; no observed semantic-accuracy difference ([comparison report](UCL2_VS_STRUCTURED_ENGLISH.md)) |
| **UCL/2.3 live stance retraction** | **4,096 → 4,097 acts** | Clarke identified the earlier qualification on branch `[1]` and retracted it while preserving its acceptance of branch `[0]`. Python and Node validated the continuing packet. ([successful run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45447764248)) |
| **2.4 live newcomer briefing** | **2,000 → 2,001 acts** | Both validators accepted a fresh continuation with an exact archived quote. The prose overread the observation. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45503699604) |
| **2.4 evidence-grounding follow-up** | **Exact quotes and correct control status** | A fresh call distinguished a descriptive observation from the independent-input requirement. [Method and result](../docs/UCL_HANDOFF_TRIAL.md#evidence-grounding-follow-up) |

The structured-English comparison measured schema compliance and factual correctness separately. Both formats achieved the same observed factual correctness in that test. The structured-English input used fewer tokens. Productive disagreement is part of the exchange.

[Portable 2.4 matched evidence-grounding comparison](UCL24_MATCHED_GROUNDING_RESULTS.md) reports exact evidence checks, first-pass continuations, and token and cost differences for 12 calls with Clarke and Hal.

[Portable 2.4 missing-source relay](UCL24_MISSING_SOURCE_RELAY.md) documents the two recovery paths and links the replay bundle.

## Reproduce, inspect and challenge

Repeat the test with published code and exact seed; inspect every raw model attempt and model-authored repair. Score packet syntax, exact definition identity, correct references, attribution, independent disagreement, input tokens and costs separately. No central verification server is needed. See the [current 2.4 specification](../docs/UCL_2_4_SPECIFICATION.md) and the [archived 2.0 specification](../docs/UCL_2_0_SPECIFICATION.md).
