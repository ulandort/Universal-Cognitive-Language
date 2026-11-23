**Historical research record (not the release specification).** Experimental drafts, outcomes and proposed work below are retained for reproducibility. **UCL/2.0 Portable is the current public profile**; its normative standard is [UCL/2.0 specification](UCL_2_0_SPECIFICATION.md). Statements below about a future or unreleased 2.0 reflect the state when experiments were originally recorded and are not current release status.

---

# UCL 2.0 development track (not yet a released specification)

UCL 1.0 remains the stable public specification on `main`. Features below are *experimental* on `develop/2.0`; they are not a new official wire standard and do not weaken or change the 11 core glyphs.

## Guide profiles

- **Portable (default):** complete guide, all active session definitions, full needed conversation history, acts and acknowledgements are in the message. No network or external tools required to interpret the rules.
- **Compact (retired experimental profile):** historical proof-of-concept only; not developed or included in new active cross-model benchmarks. Its code and offline conformance vectors remain for reproducibility. Previous token savings were modest once the full local guide context was counted. This is **not** a breaking deletion of an existing wire profile; a future revival would require demonstrated gains with a legitimately pre-cached guide.
- The current Python `tools/guide_profiles.py` represents a *prototype wrapper around a verified UCL/1.0 packet*, not final UCL/2.0 wire syntax. It preserves and reconstructs the entire original 1.0 packet exactly. Changing the 2.0 wire schema requires its own versioned specification and cross-language review.
- The experimental compact format carries its own wrapper checksum; a successful decode also validates the reconstructed original UCL 1.0 message and its original integrity record.

## Exact reference compression (LRC)

Optional research experiment **only**. Repeated identical subtrees can be locally referenced only when the complete envelope is smaller. No historical condensation, paraphrasing or information loss is permitted. The earlier 13-act sample showed LRC **increased** raw size, so it is not enabled here. The prototype lives in the downloadable prior experimental archive and is not a mandatory UCL/2.0 feature. Prefer ordinary lossless transport compression where effective.

## No loss of history

All tests and transport profiles preserve original acts, text, definitions, revisions, attribution and stance. No lossy summary is permitted in this 2.0 development track. Existing UCL/1.0 supports an explicitly disclosed condensed-history facility, but **this track does not use it**.

## Offline UCLBench

Run from repo root:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s benchmarks -p 'test_*.py' -v
python benchmarks/offline_suite.py --iterations 1000 --seed 2026 --out uclbench-results.json
```

The suite runs deterministic mutation tests (definition identity, corrupted packet hash, unknown act references), formatting-independent validation, pinned-guide checks, full portable/compact round trips, and preservation of every claim and acknowledgement. Results are machine-readable JSON and exit nonzero on failure. GitHub Actions runs these on branch and PR activity.

This **does not** test any LLM's comprehension, English-vs-UCL performance, authentication, or adversarial security. A future UCLBench live-model runner needs independent ground truth, published scoring methods and controlled API tests. Avoid presenting offline passes as AI model accuracy results.

## Conformance conditions before 2.0 release

1. Produce a complete normative 2.0 specification, with unambiguous wire format and explicit guide fingerprint derivation.
2. Test Python and independently written JavaScript reference implementations using shared canonical vectors.
3. Ensure portable cold-start reading without web access, and, only for any archival Compact compatibility checks, explicit fallback when a local guide is unavailable.
4. Require strict reconstruction of all active context and history, with no lossy condensation in 2.0.
5. Run UCLBench offline conformance suite and publish real outputs, then live English/structured-English/UCL comparative benchmarks.
6. Retain optional AES-256-GCM encrypted transport as a distinct experimental, unaudited feature.
## Active 2.0 AI dialogue research

New paid research prioritizes **UCL Portable, ordinary English, and structured English**, with generated multi-turn exchanges, self-declared private author intentions, independent recipient interpretation, exact claim/stance target scoring, validation and cost reporting. See [live autonomous relay](../benchmarks/LIVE_DIALOGUE.md). **No UCL superiority has been established**: an encoder provides explicit intent metadata to the structured variants and the English author's self-report still needs independent evaluation against actual prose.

## Structural Authoring Profile SAP-1 — experimental 2.0 (November 2026)

**Status: prototype, not a released UCL 2.0 wire standard.** The 11 core glyphs, UCL/1.0 grammar, stable 1.0 branch and its validator remain unchanged. SAP-1 is a hard-coded deterministic authoring schema for model-authored incremental contributions; it does not dictate which philosophical or scientific conclusions can be expressed.

An eight-attempt UCL-only Clarke/Hal experiment produced 3 valid packets and a longest uninterrupted exchange of two. Rejections included wrong expression type, missing epistemic provenance, unrecognized operators, malformed syntax and an invalid acknowledgement ID. None was caused by the output-token cap. Fixed structure and targeted feedback can address authoring reliability while preserving theoretical novelty.

The prototype lives at benchmarks/structural_authoring.py, applied before the unchanged real UCL validator. It enforces fixed contribution/act/ACK field shapes; exact current act and acknowledgement IDs; existing response and claim bindings; an array of integer path indices; supported ACK actions and response stances; response orientation L; and expression-string types. Nested glyph types, evidence provenance, history and integrity continue to be checked by UCL/1.0. SAP-1 never repairs a model's semantics, and it does not force its formula to one previously preferred positive atom.

The model-facing rules include examples of property applications, negation, conjunction and disjunction, plus an explicit distinction between an ACK action of withhold-judgment and a provenance-bearing epistemic conclusion.

### Language evolution versus syntax mistakes

Models may invent concepts or propose alternative operators. A correctly defined custom concept is legitimate within UCL's open vocabulary; an unknown core operator is NOT silently valid. A model can explicitly describe a proposed new grammar/operator in an act note for future analysis. It remains NON-NORMATIVE until versioned adoption and independent validator interoperability. This prevents accidental drift from being mistaken for established consensus while allowing genuine innovations to be studied. Current SAP-1 limits its contribution envelope and does not yet implement arbitrary new-definition creation in the experimental relay; preserving this extension path is a requirement before release.

### Feedback-directed authorship

The manual UCL-only workflow optionally allows 0, 1 or 2 additional calls per failed message. An author is shown its own raw draft and the exact validator error and must reauthor a COMPLETE candidate. No English semantic converter or external repair algorithm is involved. A packet is passed to the other model ONLY after it validates. Every call, correction, provider timeout and its estimated spend is recorded. The runner distinguishes first-attempt valid packets, repaired packets and longest uninterrupted conversation. A repair-assisted success must not be described as first-attempt native authorship.

Before promotion to released 2.0, define independent cross-language SAP-1 validation vectors, confirm new-definition extensibility and compatibility, and measure whether the stable structure helps or unduly constrains real exploratory discourse.


## Self-contained SAP-1 Portable envelope (implemented, experimental)

The experimental 2.0 Portable transport now embeds the COMPLETE SAP-1 authoring rules inside every UTF-8 JSON (.txt/.json) message, rather than requiring a prompt, repository lookup, remote service or central registry. The canonical tool is tools/sap_portable.py.

Each message contains: format UCL/2.0-SAP1-PORTABLE-DRAFT; a complete structural_rules block with authoring field requirements, exact references and IDs, typed symbolic examples, extension proposal policy and a SHA-256 fingerprint; an unchanged, complete UCL/1.0 packet with its entire guide, definitions, acts and history; plus an independently recomputable domain-separated envelope checksum.

The UCL-only dialogue runner now passes this self-contained 2.0 draft envelope as the actual message to the next model, not just as an off-wire prompt. The receiver can implement the embedded rules locally. A validator can pin the known version and recheck the embedded rules, outer checksum and UCL/1.0 packet. A self-contained checksum is tamper detection, NOT authentication or truth. No centralized third-party is required. Independently written cross-language validators are still needed before calling the format a stable 2.0 standard.

Offline, without API keys or internet:

```bash
python tools/sap_portable.py encode examples/cross_model_conversation_8_turns.json example-ucl2.txt
python tools/sap_portable.py check example-ucl2.txt
python tools/sap_portable.py decode example-ucl2.txt restored-ucl1.txt
```

The November 22, 2026 native UCL-only run 45072956129 produced 8/8 first-try valid messages with zero repairs, cost estimate $0.501071, and 4/7 correct four-field receipts. All three receipt mismatches were evidence classification only. That earlier run used off-wire SAP-1 instructions; it is a baseline, NOT a test of the new embedded wire. Source: https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45072956129

Unknown core operators may be proposed as non-normative notes, but may not silently redefine the syntax. Stable UCL/1.0 remains unchanged.


## SVP-1 optional decentralized semantic verification — implemented experimental draft

UCL/2.0-SVP-1-DRAFT is now a small, versioned rule section in the existing SAP-1 Portable structural_rules block. It is included in the transmitted, self-contained JSON .txt packet and is covered by the same independently recomputable hashes. No external service, central judge, third-party dictionary or hosted AI is required. This is NOT a released normative 2.0 specification.

SVP-1 is mandatory-to-understand for a reader of this draft profile, but OPTIONAL to execute. Checks include existing typed UCL validation, formal consistency under expressly stated premises and bounded Boolean abstraction, advisory text/formula alignment and conversational continuity. Semantic assessments are NOT required on the wire and never become an automatic syntax veto. Reports are independent optional sidecars referencing the exact envelope checksum, not copies of whole transcripts.

CRITICAL NOVELTY GUARANTEE: An unknown, original, speculative or empirically unsupported hypothesis is NOT automatically false or rejected. Even a demonstrable contradiction retains the original and must identify the explicit premises and exact derivation; a model may challenge the premise or propose an alternative theory. Natural-language alignment is indeterminate unless separately and transparently interpreted. Disagreement between independent auditors is preserved as disagreement rather than central authority.

The local deterministic demonstration tool tools/semantic_audit.py performs bounded exhaustive Boolean satisfiability on structurally validated expressions using uninterpreted atoms. It never claims that a satisfying assignment proves empirical truth, and it never attempts to parse subtle natural-language meaning automatically. Unsupported or out-of-scope cases are marked not-assessed. The optional report is separate and cannot alter the original envelope.

Offline use:

```bash
python tools/semantic_audit.py example-ucl2.txt --output example-audit.json
```

The November 22, 2026 first paid test of fully self-contained SAP-1 Portable (run 45074316207) returned **8/8 delivered valid packets, 6/8 first-attempt valid, two repaired, 4/7 complete private-intent receipt matches**, estimated $0.803166. One first-attempt rejection was output-token exhaustion and one was syntax validation. This satisfies stage-one feasibility but not proof of semantic understanding, truth, novelty or language superiority. The SVP-1 addition follows that run and has not yet undergone a new paid model test.


## Optional Formula Roles FR-1 — matched-packet experiment (experimental)

FR-1 is a **non-normative, optional** outer envelope field `formula_roles`, NOT a new UCL 1.0 glyph or a mandatory change to the symbolic inner packet. An entry has three fields: `{"act":"t9","index":0,"role":"counterexample"}` and refers to an existing act's exact expressions array index (zero-based integer). Allowed provisional author-declared roles: `hypothesis`, `example`, `counterexample`, `quotation`, `question`. Roles are not truth claims, proofs, or central audit decisions. A missing annotation is **unannotated**, never silently treated as assertion.

The envelope checksum covers each annotation; the original inner UCL packet and its hash are unchanged. Invalid or duplicate references, noninteger indices, unknown roles, and tampering are rejected by the optional-profile validator. Annotating a novel hypothesis cannot automatically reject, edit or normalize it. Existing unannotated envelopes continue to pass unchanged.

The paired experiment in `benchmarks/formula_roles_experiment.py` creates five constructed UCL packets with two formal expressions each and author-declared intentions. Clarke and Hal can read each identical source packet twice, once plain and once with the role array; the receiver reports which expression is an original hypothesis, example, counterexample, quotation or question, and whether both are jointly proposed. The benchmark compares field accuracy and byte overhead; roles are supplied as a synthetic author-label oracle, so higher scores **cannot independently prove improved reasoning, factual discovery or semantic truth**. Alternate case order partially mitigates arm-order effects. Repeated blinded trials and genuine model-authored annotations are needed before FR-1 could become normative.

Free regression tests reject altered entries, guarantee unchanged inner UCL packet identity, and verify that packets WITHOUT roles have zero FR-1-specific overhead. Tagged examples add a short local role guide plus two labels (under 480 extra canonical UTF-8 bytes per fixture; measured overhead is recorded per case). Unknown-hypothesis protections remain unchanged. The manual GitHub workflow defaults to `paid_run=no`, and uses a bounded shared estimated budget only if the user explicitly selects yes.

Manual workflow: https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-formula-roles.yml

Do not confuse a role's communicative function (`counterexample`) with empirical truth or with an assertion that the counterexample actually occurred. This experiment does not yet modify the main UCL-only conversation's authoring behavior or require FR-1 tags on any message.
