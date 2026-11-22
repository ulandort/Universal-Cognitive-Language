# UCL/2.0 release readiness — working checklist

Status: experimental development checklist, not a claim of UCL/2.0 conformance or release approval. UCL/1.0 on `main` remains stable. Each gate needs reproducible evidence, recorded failure analysis, and an explicit go/no-go decision. Do not equate syntax correctness, self-reported intent matching, or an oracle dry run with independently validated comprehension.

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
- [ ] Permit legitimately defined new predicates and distinguish definition evolution from accidental reuse; retain all revisions, attribution, alternatives, and explicit acknowledgment targets.
- [ ] Blindly annotate whether receivers accurately understood the author's communicative intent; report unresolved interpretations and speculative claims without automatic rejection.
- [ ] Report valid first attempts, recovery-assisted successes, novelty review, and provider/model failure modes separately.

### Independent-reasoning pilot evidence (2026-11-22)

- Paid [UCL-only native workflow run 45077733957](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45077733957): two eight-turn Clarke/Hal dialogues, 16/16 validated self-contained Portable UCL messages delivered; 13/16 first-attempt valid and three model-authored repairs (19 provider requests); estimated $1.508582.
- Exact four-facet receiver-to-sender-private-intent agreements: 9/14 (Clarke-start 4/7, Hal-start 5/7). Of five mismatched receipts, four included evidence classification, one included signal sense without evidence, and one included stance alongside evidence; these are not necessarily evidence of formally wrong expressions. Full transcript and failed attempt details are in the workflow artifact.
- Qualitative evolution: independence counterexamples led to conceptual dependence of measurement on P; another dialogue advanced a possible ambiguity in how Alpha is individuated under P versus B. These were **model-chosen hypotheses**, not empirical findings or independently certified novel ideas. Multi-expression role ambiguity remains, notably quotations/hypothetical illustrations versus co-assertions.
- **Next experiment CG-1:** enable models to author genuinely *new fully defined UCL concepts*, immutable identities, new references, and revisions within otherwise fully self-contained messages. Do not allow unexplained new operators or silent changes to the 11 core glyphs. Compare actual semantic definition understanding, not merely new names; ensure structural checks alone cannot declare novelty.
- Gate 2 remains **partially open**: valid exchanges are demonstrated, but first-attempt success and interpretation fidelity need improvement, and newly authored definitions have not been tested.

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

## Release rule

An optional FR-1 success alone is insufficient. Consider **Beta** after a versioned 2.0 envelope/specification and meaningful native self-authorship checks; **Release Candidate** only after complete cross-language conformance and long-dialogue reliability trials; **Stable** only after the five gates have documented acceptable outcomes. Record failures transparently, retain UCL/1.0 unchanged, and do not silently promote experimental features. API-paid trials require separate manual authorization and a guarded cap.
