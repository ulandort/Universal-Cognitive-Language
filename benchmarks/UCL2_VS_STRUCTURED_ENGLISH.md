# Stable UCL/2.0 vs structured English — matched 25-event history comparison

**Live run:** [GitHub Actions #45090283766](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45090283766), November 22, 2026 (Toronto) / November 23 UTC. **Published research:** real API calls to Clarke 1.0 and Hal 1.0. Full raw artifact: `ucl2-structured-english-matched-study`, ID `14781440884` (expires December 7, 2026 UTC). **Study code:** [`ucl2_vs_structured.py`](ucl2_vs_structured.py), with [offline matched tests](test_ucl2_vs_structured.py).

## Outcome: UCL led on STRICT protocol compliance; no demonstrated semantic accuracy advantage

| Measure | UCL/2.0 Portable stable | Structured English JSON |
|---|---:|---:|
| Requests | 8/8 | 8/8 |
| **Valid JSON responses in the required exact schema** | **8/8 (100%)** | **7/8 (87.5%)** |
| Strictly accepted and correct question answers | **56/56 (100%)** | **48/56 (85.7%)** |
| Incorrect choices in properly formatted responses | **0** | **0** |
| Correct responses among strictly valid responses | **56/56 (100%)** | **48/48 (100%)** |
| Input tokens (provider-reported) | **62,928** | **30,374** |
| Output tokens (provider-reported) | 11,614 | 11,006 |
| Completion-length failures | 0 | 0 |

**Critical raw-output finding:** The one rejected structured-English response (repetition 2, turn/checkpoint 25, Clarke) was **not a failure to understand the questions** and did **not omit the answers**. It included **all eight correct answer IDs and choices**, but lacked the required outer `"answers"` property (returned `{"t19_alias":"b",...}` rather than `{"answers":{"t19_alias":"b",...}}`). The strict benchmark correctly counted it as invalid because its output schema was wrong. If a permissive human reader accepted the otherwise clear choices, **all 56/56 semantic item responses from each format were correct**. Do not describe the strict-score gap as eight factual misunderstandings, eight unanswered items, or evidence that UCL understood history better.

**Combined:** 16 requests, 112 scored items under exact-schema rules, 104/112 strict end-to-end correct, 15/16 perfectly valid outputs, estimated combined provider cost **$0.283266 USD**. This is one small exploratory case set, not a precise estimate of general reliability. All observed correct choices were on the fixed publicly encoded questions. The original 25 historical events were scripted and **not an independently generated 25-turn conversation** in this comparison.

## Study design and what it isolates

Both model families received the **same stipulated concepts, historical events, answer options and exact answer keys**, with two checkpoints (10 and 25 events) and two repetitions. Each model/checkpoint/repetition encountered both formats, and the order of the two formats rotated. The UCL arm transported its full history and language rules in the **actual stable `UCL/2.0-SAP1-PORTABLE` envelope**. The structured-English arm carried the same definitions, hashes, acts, ACKs, original claims and history in more compact JSON. Both records were generated mechanically from a single validated underlying state.

Both arms used the same final response instruction: produce exactly `{"answers":{"id":"a/b/c/d",...}}`. The strict scorer rejected missing or extra keys rather than silently repairing output. There were no schema-retry calls in either arm.

**What was observed:** UCL yielded more exact-schema compliant output in this tiny sample (8/8 vs 7/8), while structured English used **about half as many input tokens** (30,374 vs 62,928). Both achieved perfect answer-choice accuracy conditional on an accepted reply; even the one malformed structured-English reply listed the correct answers. The additional UCL overhead is a genuine implementation/resource cost and may affect scaling.

This was **not** a randomized blinded study, independent semantic evaluation, proof of language superiority, a native language-generation comparison, or an AI-to-AI novelty test. It tests *reading* a mechanically encoded historical record, not autonomous invention and transmission of novel concepts. Individual response outcomes are not independent draws; questions are repeated across formats/models/repetitions. No strong statistical claim should be made from a single malformed JSON response.

## Symmetric generalization policy — neither format is universally better

If this or a future study finds structured English ahead, the only defensible conclusion is that it performed better on **the particular tested tasks, settings, models and metrics**. Further extensive research is essential before suggesting structured English is generally superior to UCL. Conversely, the same restriction applies to this study's measured UCL advantage in strict JSON compliance: **UCL has not been demonstrated generally superior to structured English**.

UCL's design creates plausible advantages for **exact immutable concept IDs, fully self-contained machine-readable packets, independently extensible typed definitions, targeted subclaim acknowledgements, auditable disagreement and revisions, local offline validation and long-lived multi-agent context**. These advantages remain use-case-specific hypotheses requiring separate controlled evidence. Structured English can offer very significant benefits in **compactness, familiar semantics, accessible prose and lower token overhead**, all worth reporting rather than downplaying.

## Needed future research to establish task-dependent advantages

- Native model-authored novel concept generation and **cold-recipient interpretation**, with independent blinded semantic-scoring controls
- Adversarial cross-agent correction of false recaps, ambiguous aliases, identity substitutions and explicit provenance at long histories
- Scoped disagreement and qualified acknowledgements targeting *subexpressions* rather than broad document summaries
- Multi-model, multi-domain, longer-horizon validation with confidence intervals and task-level randomization (not merely repeated identical questions)
- Equalized input/output budget, context-window and guide-size ablations, latency/token/resource costs, timeout and recovery analyses
- Comparisons to plain English, **equally detailed** structured English and task-custom schemas, not artificially weak baseline prompts
- Full response validity, semantic understanding, operational cost and formal correctness scored as **separate** axes

**Bottom line:** This result is *positive evidence of UCL/2.0's correct strict-formatted historical-reference retrieval in 8/8 responses*. It does not prove that a structured-English model misunderstood even one of the 56 questions, nor that either protocol dominates across all use cases. The distinctively important UCL capabilities (new concept invention, exact reference identity and multi-agent argument) require task-specific evidence such as the separately published CG-1/CG-2 tests.
