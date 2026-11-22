# UCL/2.0 release readiness — working checklist

Status: experimental development checklist, not a claim of UCL/2.0 conformance or release approval. UCL/1.0 on `main` remains stable. Each gate needs reproducible evidence, recorded failure analysis, and an explicit go/no-go decision. Do not equate syntax correctness, self-reported intent matching, or an oracle dry run with independently validated comprehension.

## Public benchmark reporting policy — disagreement is not a protocol failure

UCL is intended to support independent reasoning, including dissent, counterexamples, unresolved questions and revisions. **A receiving model disagreeing with the preceding model's conclusion is not a language error.** Nor is a model changing its own position after discussion.

For every public benchmark summary, distinguish clearly:
1. **Structural/transport failures:** invalid UCL grammar, broken references, lost history, altered immutable definitions, failed integrity validation, empty or truncated outputs, and provider failures (with provider problems reported separately).
2. **Communication fidelity:** whether the recipient accurately attributes the sender's proposition, scope, stance, definitions and epistemic qualifications. A receiver may accurately understand an argument and still reject it. Measured mismatches against privately self-reported intent are *receipt disagreements*, not automatically proven semantic misunderstandings.
3. **Ancillary classification:** differences in detecting an example, the sense of an ambiguous word, or a requested output enum. These must be named rather than collapsed into an undifferentiated “language failure” score.
4. **Productive intellectual disagreement:** independent objections, counterexamples, alternate theories, and coherent revisions are legitimate—even desirable—conversation outcomes, not correctness penalties. Logical disagreement only becomes an interoperation concern when attribution or intended scope is demonstrably distorted.

Report both numerators and denominators, first-attempt versus repaired delivery, model/provider limitations, and representative qualitative transcript examples. Preserve the original raw evidence and disclose ambiguity; never relabel a measured mismatch as a proven defect or hide a genuine error to improve public presentation. Do not claim superiority over English without a controlled comparison.

In particular, [native UCL-only run 45077733957](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45077733957) achieved 16/16 delivered packets with three model-authored repairs. Its 9/14 exact four-field receipts **must not** be described as “five language failures” or a 35.7% inability to converse. The mismatches include ancillary evidence or signal classifications and one stance distinction; they deserve transcript-level review. Neither their existence nor apparent productive conversation proves perfect semantic fidelity.

## Gate 1 — Optional FR-1 communicative roles

- [x] Implement optional, checksum-protected, indexed author-declared annotations in the self-contained Portable envelope; preserve the original UCL/1.0 inner packet, all 11 core glyphs, and backward compatibility.
- [x] Run a preliminary two-model A/B test: [run 45076312803](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45076312803). Ten plain outputs were unscorable; five of ten annotated outputs were scoreable and correct. This is **not** evidence of ten semantic errors in the plain arm.
- [x] Audit the corrected 16,384-output-token paired run: [run 45076907824](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45076907824). All 20 API calls completed without output-token exhaustion, estimated cost $0.513510. Plain: 5/10 scorable JSON, 5/5 correct role pairs, 4/5 correct joint-proposal flags. Annotated: 5/10 scorable JSON, 5/5 correct role pairs, 5/5 correct joint flags. Hal supplied all ten valid JSON responses; Clarke supplied none despite frequently describing correct roles in prose. Total output tokens plain 45,175, annotated 9,261 (~79.5% lower), but this is one small workload and may be model/response-format dependent. The test does not establish statistically reliable semantic superiority.
- [ ] Resolve Clarke JSON-format noncompliance using a controlled response-format test (not covert semantic repair), then independently test model-authored FR-1 roles before normative inclusion.
- [ ] Require an independently authored-label test, rather than only model reading of synthetic oracle labels; consider ambiguous labels, disagreement, and missing annotations.
- [ ] If evidence warrants, freeze a versioned FR-1 extension schema, its full in-packet guide and conformance vectors. Roles describe communicative purpose, not empirical truth. Otherwise retain experimental status or defer to 2.1.

## Gate 2 — Original independent reasoning

- [x] Existing native exploration runners allow models to propose and challenge P/B hypotheses without prescribing exact new conclusions.
- [ ] Run a fresh **two-model, self-authored** multi-turn exploratory dialogue using the candidate 2.0 format: no hidden predetermined conclusion and no semantic English-to-UCL converter.
- [x] Permit model-authored new typed predicates and preserve immutable identifiers in CG-1; **definition revisions, richer types, and robust attribution across more open-ended tasks remain to be tested**.
- [ ] Blindly annotate whether receivers accurately understood the author's communicative intent; report unresolved interpretations and speculative claims without automatic rejection.
- [ ] Report valid first attempts, recovery-assisted successes, novelty review, and provider/model failure modes separately.

### Independent-reasoning pilot evidence (2026-11-22)

- Paid [UCL-only native workflow run 45077733957](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45077733957): two eight-turn Clarke/Hal dialogues, 16/16 validated self-contained Portable UCL messages delivered; 13/16 first-attempt valid and three model-authored repairs (19 provider requests); estimated $1.508582.
- Exact four-facet receiver-to-sender-private-intent agreements: 9/14 (Clarke-start 4/7, Hal-start 5/7). Of five mismatched receipts, four included evidence classification, one included signal sense without evidence, and one included stance alongside evidence; these are not necessarily evidence of formally wrong expressions. Full transcript and failed attempt details are in the workflow artifact.
- Qualitative evolution: independence counterexamples led to conceptual dependence of measurement on P; another dialogue advanced a possible ambiguity in how Alpha is individuated under P versus B. These were **model-chosen hypotheses**, not empirical findings or independently certified novel ideas. Multi-expression role ambiguity remains, notably quotations/hypothetical illustrations versus co-assertions.
- **Next experiment CG-1:** enable models to author genuinely *new fully defined UCL concepts*, immutable identities, new references, and revisions within otherwise fully self-contained messages. Do not allow unexplained new operators or silent changes to the 11 core glyphs. Compare actual semantic definition understanding, not merely new names; ensure structural checks alone cannot declare novelty.
- [CG-1 live concept genesis run 45079394296](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45079394296) succeeded: **six of six** self-contained, new-definition UCL messages delivered; **four of six first-attempt valid**, two delivered after model-authored repairs (three failed attempts; nine total provider calls); **six distinct model-authored predicate definitions** preserved as immutable hashed identities; **five of five** definition receipts referenced the previous new concept's exact glyph and definition ID. Estimated API cost **$0.423467**.
- Qualitative human-read transcript inspection found the model-generated concept progression C interpretative coherence, E meaning resonance, G inferential invariance, K functional surrogacy, M adaptive mapping, N ontological indifference. Subsequent models independently paraphrased their predecessor's definition with substantively consistent meanings. This is strong preliminary evidence for the **ability to extend and reference a self-contained vocabulary**, but it does not establish philosophical novelty, correct inference, or superiority to English; the prompt constrained the research subject and predicates to domain D.
- The CG-1 identity receipt tests only exact hashes, not equivalence of the paraphrase. The research interpretation is a qualitative judgment and should not be inflated into a fully verified semantic-comprehension score. Both first-try model failures and repairs should be publicly reported.
- Gate 2 remains **partially open**: sustained validated native dialogue and new-concept creation are now demonstrated. Independent blind annotation, stronger cross-model reasoning tests with concepts, and semantic fidelity remain outstanding.

### Final short-form reasoning pilot before long stress

- **RR-1 is prepared but has not yet had a paid run:** [runner](../benchmarks/relational_reasoning.py), [protocol](../benchmarks/RELATIONAL_REASONING.md), and manual GitHub Actions workflow on `main`. It uses the **actual full CG-1 final Portable packet** from [CG-1 paid run 45079394296](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45079394296), validates the six original concept identity hashes and asks Clarke/Hal to independently compose formal multi-concept relations. It preserves dissent as a valid outcome; interpretations and philosophical inferences require qualitative assessment, not merely structural parsing.
- **Release sequence:** RR-1 transcript audit, 25-turn autonomous stress, 50-turn stress if justified, complete Python/JS normative interop and documentation review, then a targeted public **UCL/2.0 stable/full release** if all mandatory readiness checks are satisfactory. Do not imply a green workflow constitutes semantic superiority or stable release certification.

### RR-1 completed — genuine CG-1 relational reasoning (2026-11-22)

- [Paid RR-1 workflow run 45080241779](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45080241779) completed successfully using the actual final six-concept CG-1 Portable packet as an independently validated starting point.
- **6/6** new fully validated model-authored Portable messages delivered; **3/6 first-attempt valid**; three later succeeded with model-authored repairs (**9 provider requests**, estimated **$0.482015 USD**). All six delivered messages contained typed multi-concept expressions; **five interpretations** of a preceding newly generated message were recorded for review.
- All three rejected first attempts failed the experiment's **minimum 50-character interpretation-field requirement**, not UCL expression grammar, structural integrity, concept identity, or an observed intellectual disagreement. Thus reporting them as "three language failures" would be false. The additional requests are still important evidence of format compliance and cost overhead.
- Direct transcript review: both models communicated speculative non-entailment relationships involving C/E/G/K/M/N, including N and not M, C and E and not G, K and not M, N and not C, C and K and not M, and G and K and not E. Five interpretation summaries were substantively aligned with the immediately preceding model-authored prose. This is **qualitative evidence**, not a blinded comprehension score.
- **Do not equate valid conjunctions with demonstrated logical independence**: hypothetical combinations such as `&[~[N][A]][![~[M][A]]]` are model-authored speculative counterexample *descriptions*, not verified satisfiable models or formal proofs. Models did not demonstrate new empirical discoveries, entailment theorems, or superiority over structured English.
- **Next stress gate:** autonomous 25-turn conversation and then 50-turn if viable. Track cumulative input length, maximum body/act limits, no silent history loss, valid identity hashes, first-try versus recovery, attributable context retention and total cost. Long turns may require explicit continuation ID budgeting and accommodation of increasing full-packet sizes without silently condensing history.

## Gate 3 — Long conversational stability

- [x] Preserve the scripted 10-turn and 25-event semantic-retention benchmarks (see `benchmarks/LONG_CONVERSATION.md` and `benchmarks/ADVERSARIAL_25.md`). These are scripted histories, **not autonomous AI discussions**.
- [ ] Execute a 25-turn independently generated dialogue pilot and, if stable, a 50-turn stress run with a predefined cost guard.
- [ ] Check literal full-history preservation, immutable definition hashes, act/ACK/reference resolution, non-monotonic stances, quotation scopes, and extension handling.
- [ ] Track token cost and envelope byte growth by turn, validation and provider failures, first-try and repaired delivery, and semantic receipt agreement. Do not silently condense UCL/2.0 active history.

## Gate 4 — Cross-language interoperability and adversarial conformance

- [x] Existing Python reference validation and JavaScript subset checker establish a starting point.
- [ ] Write a complete normative UCL/2.0 specification distinguishing the outer envelope and its stable 1.0 inner packet.
- [ ] Verify an independently written **full** JS/TypeScript implementation against Python using shared canonical vectors (hashes, Unicode, numeric bounds, complete guide, nested expressions, role indices, ACKs, full history).
- [ ] Test malformed packets, tampered checksums, duplicate roles, missing guides, unknown extensions, contradictory annotations, oversized messages, and adversarial content; ensure fail-closed validation without covert semantic rewriting.
- [ ] State precisely which validations are mandatory and which semantic audits are advisory; preserve novelty and disagreements.

## Gate 5 — Fair comparison and release evidence

- [x] Preserve earlier English / structured English / UCL comparison results and their methodology caveats (`benchmarks/NATIVE_AUTHORING.md`, `benchmarks/LIVE_DIALOGUE.md`).
- [ ] Predeclare matched semantic tasks, both model directions, controlled prompt budgets, independent annotations and consistent output limits across English, structured English, and UCL Portable.
- [ ] Score authored-task compliance separately from valid transmission, receiver comprehension, recovery, and end-to-end correct intent; report confidence and sample sizes.
- [ ] Report all token and byte overhead, pricing, false proof attributions, and format failures; compare against structured English, not just unstructured prose.
- [ ] Publish raw reproducible artifacts and a limitations statement before any performance or superiority claim.

## Release rule — full 2.0 launch target

**User-approved launch designation: UCL/2.0 full public release, not a beta.** RR-1 is running as of November 22, 2026; no outcome is assumed. Following transcript review, conduct the proposed 25-turn and 50-turn stress tests, finalize versioned documentation and the portable `.txt` format, complete Python/JavaScript interoperability checks and negative conformance tests, and disclose reproducible benchmark strengths and limitations. Record explicit go/no-go decisions for unresolved issues before tagging `2.0`.

This is a **target designation, not a declaration that the necessary checks have already passed**. If a release-blocking issue remains, fix it or transparently scope the feature; do not disguise it to meet the full-release label. Functional disagreement among AIs is not a language failure. No claim of semantic superiority or flawless comprehension without evidence.

Keep stable UCL/1.0 intact until intentional release steps; maintain the unchanged 11 core glyphs, self-contained messages, immutable definition identities and optional extensions. Paid trials require separate manual authorization and a guarded estimated cap.
