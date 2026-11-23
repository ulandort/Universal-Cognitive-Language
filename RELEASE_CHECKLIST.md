# Release checklist — UCL/2.0 Portable

**Target:** full public stable UCL/2.0, not beta. The stable Portable envelope replaces the standalone 1.0 packet as the recommended interchange format. The inner core glyphs, grammar and definition hashing are preserved. The historical research record is retained, but draft formats are not accepted as the 2.0 standard.

## Protocol and implementation

- [x] Freeze exact wire identifier `UCL/2.0-SAP1-PORTABLE` and independent 2.0 checksum domains.
- [x] Include fully self-contained language guide, typed definitions, claims, acts, acknowledgements, provenance and local authoring instructions in ordinary `.txt` JSON.
- [x] Retain all 11 core glyphs and immutable definition identities; do not silently alter meaning, history, or scoped ACKs.
- [x] Verify exact pinned embedded rules, original inner guide, inner packet checksum and envelope checksum offline; unknown or modified profiles fail closed.
- [x] Provide standard-library Python reference checker and zero-dependency independent JavaScript Portable verifier (documented subset of full inner semantics).
- [x] Include negative vectors for altered guide, rehashed unknown rules, tampering, duplicate FR-1 references, and malformed fields; use tests and CI for further regressions.
- [x] Keep FR-1 roles, SVP-1 opinions and encryption separate and optional; do not imply any is proof, authentication or required central authority.
- [x] Preserve concrete validation failures and model-authored retry provenance without equating philosophical disagreement with communication failure.

## Public documentation

- [x] Human-facing README with first-use walkthrough, capabilities, live research evidence and limitations.
- [x] AI-facing reading/authoring README with exact ACK and UCL syntax.
- [x] Frozen [UCL/2.0 normative specification](docs/UCL_2_0_SPECIFICATION.md).
- [x] Public [release notes](RELEASE_NOTES_2_0.md) and [changelog](CHANGELOG.md).
- [x] UCLBench methodology and L25/L50 actual results with exact errors, costs and authentic lineage.
- [x] Archive prior experimental draft documentation without presenting it as the supported release.
- [x] Include Apache-2.0 licence, conformance/branding notices, governance and attribution.

## Release validation and publication

- [x] Final exact release-candidate core and full offline CI runs green at the selected commit (verified by [publication workflow](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45088402215)).
- [x] Independent Python/JavaScript parity checks for stable Portable envelope pass on the published release build.
- [x] Merge the inspected release candidate into `main` ([PR #1](https://github.com/ulandort/Universal-Cognitive-Language/pull/1)) and verify public README and stable wire on `main`.
- [x] Publish the [full stable GitHub release v2.0.0](https://github.com/ulandort/Universal-Cognitive-Language/releases/tag/v2.0.0), not a prerelease, with a downloadable validated `.txt` packet.
- [x] Run the **four-turn offline** post-release Concept Genesis smoke check against `main` ([successful automatic run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45088332367)); live four-turn paid verification is tracked separately from release correctness.

**Not certified:** no third-party security audit, comprehensive semantic-proof guarantee, superiority over English, or complete JS proof/model engine parity. These are not claimed to be complete stable-release conditions for the core Portable interchange profile; unsupported capability claims must be explicit.
