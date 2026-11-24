# UCLBench — reproducible benchmarks and conformance tests

UCLBench includes deterministic offline validation and experimental live-model research. **The current public transport is UCL/2.2 Portable**; archived comparison scripts may reproduce experimental profiles, and results from different profiles must not be pooled as if they were the same protocol.

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

## Reproduce, inspect and challenge

Repeat the test with published code and exact seed; inspect every raw model attempt and model-authored repair. Score packet syntax, exact definition identity, correct references, attribution, independent disagreement, input tokens and costs separately. No central verification server is needed. The normative 2.0 format is defined in [the specification](../docs/UCL_2_0_SPECIFICATION.md).
