# Changelog

This project uses versioned protocol profiles. Experimental benchmark artifacts are research evidence rather than evidence of a different live released wire specification.

## UCL/2.4.0 — Newcomer briefings and typed reply starters (November 2026)

- Added `inspect --handoff`, `diff --compact`, and opt-in `template --seed-formula`.
- Added the embedded typed reply example and published the Portable 2.4 wire and guide fingerprints.
- Verified that upgrading plain and packed 2.3 conversations preserves their definitions, acts, ACKs, and retractions.

## UCL/2.3.0 — Exact stance retraction (November 2026)

- Added an ACK action that retracts one of the speaker's earlier stances by ID, with both records retained.
- Added `inspect --state`, deterministic packet `diff`, reply templates, and shared draft preflight.
- Added stable Portable 2.3 pins and Python and Node support. Older Portable files remain continuable in their original formats.
- Verified live retraction at act 4,097 from labeled excerpts of a packed history.

## UCL/2.2.0 — Long conversations in one Portable file (November 2026)

- Add exact act and claim-path lookup, plus a Concept Index that compares vocabulary across packets.
- Add optional embedded gzip archives with readable decoding instructions and pinning of important turns.
- Keep the latest 1,000 acts readable. Pack older acts losslessly in indexed blocks within the same file.
- Verify archived histories with Python and Node. An offline 100,000-act conversation fit in 4.02 MB and continued to 100,001 acts.
- Continue reading earlier 2.0 and 2.1 packets with their original hashes. See the [release notes](RELEASE_NOTES_2_2.md).

## UCL/2.1.0 — Expand the Portable vocabulary (November 2026)

- Add readable named aliases and raise the catalog capacity from 55 to 512 definitions.
- Bind definition identities to their exact typed domain dependencies, including finite membership.
- Record speaker-scoped retirements, successors, examples, and counterexamples in retained acts.
- Embed a worked reply template and add `continue`, state-first `inspect`, and an optional JSON ledger.
- Verify and continue archived 2.0 packets with their original identities. Explicit `upgrade` reissues a separate 2.1 packet.
- Publish validated quickstart and challenge files. See the [release notes](RELEASE_NOTES_2_1.md).

## UCL/2.0.1 — Source-layout maintenance (November 2026)

**No UCL wire, grammar, hashing, or semantic changes.** Consolidates the stable UCL/2.0 Portable Python implementation under `src/`:

- `src/ucl.py` is now the documented UCL/2.0 CLI and importable public API, including `encode`, `decode`, and automatic Portable-versus-inner-packet `check`.
- `src/portable.py` is the single canonical Portable envelope implementation, using `src/core.py` for the original validated typed grammar and `src/structural_authoring.py` for the embedded authoring schema.
- Existing `tools/sap_portable.py` and `benchmarks/structural_authoring.py` become tiny compatibility forwarders so saved scripts, command lines and benchmarks continue to work.
- Added exact canonical-byte, hash, history, CLI and Python/Node interoperability regressions; retained the original 11 glyphs, original inner packet version identifier and the full `UCL/2.0-SAP1-PORTABLE` wire identity.

The previous inner `UCL/1.0` identifier still appears *inside* the original typed grammar for fingerprint and history compatibility. It is not a separate supported external transport. The v2.0.0 tag remains preserved for reproducibility.

## UCL/2.0 — Stable Portable release (November 2026)

**Release interface:** `UCL/2.0-SAP1-PORTABLE` in a self-contained UTF-8 JSON `.txt` file.

### Added
- Complete embedded, integrity-checked structural authoring instructions alongside the unchanged typed UCL inner packet, claims, definitions, discourse and history.
- Model-authored new typed concepts with exact immutable SHA-256 identities, scoped acknowledgements, and explicit individual authorship of corrections.
- Optional formula-role indexing (hypothesis, example, counterexample, quotation, question), plus optional decentralized advisory semantic review.
- Independent Node.js Portable envelope verifier and Python–JavaScript conformance regression tests.
- Stable normative specification, human/AI usage guides and end-to-end benchmark writeups.
- Compact in-file local authoring preflight for typed expressions, ACK integer paths and qualification requirements.

### Changed
- UCL/2.0 Portable replaces standalone UCL/1.0 plain packet as the default supported interchange format. Original 11 core glyphs remain unchanged.
- Stable `UCL/2.0-SAP1-PORTABLE` wire identifier, version-specific rules and envelope hash domains; experimental `*-DRAFT` rulebooks are not implicitly accepted as stable.
- Benchmark-only interpretation-summary length rules no longer block otherwise valid message deliveries.
- Release documentation reports model disagreement independently of syntax and semantic attribution.

### Research evidence (not universal quality claims)
- Concept Genesis 6/6 validated handoffs with six new model-authored predicates.
- RR-1 relational reasoning 6/6 validated handoffs.
- L25 autonomous 23/25 delivered; 23 of 30 rejected attempts were due to an artificial research-sidecar length requirement.
- L50 autonomous **48/50 delivered**, **45/50 first attempt**, **91 retained historical acts** and five prompted reference checks passed.

### Limits
A self-hash is not identity authentication. The independent JavaScript validator documents a subset of Python's advanced inner proof/model semantics. Optional encryption remains experimental. The model research does not demonstrate broad semantic superiority to English, flawless comprehension, or philosophical proof. Earlier DRAFT packets are historical experiments rather than the stable 2.0 wire profile.

## UCL/1.0 — Retired default public transport

The foundational UCL/1.0 grammar, eleven original glyphs, typed expressions, canonical JSON, definition hashes and inner packet format remain accessible in the code and archived specification. Version 2.0 incorporates them inside its self-contained Portable envelope rather than deleting the definitions of earlier research conversations. Existing 1.0 standalone applications require deliberate migration to emit and accept the 2.0 envelope.
