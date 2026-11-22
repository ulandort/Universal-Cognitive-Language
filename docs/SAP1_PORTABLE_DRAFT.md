# UCL 2.0 SAP-1 Portable: self-contained wire draft

**Status: experimental, unreleased.** Stable UCL 1.0 on main and its 11 core glyphs are unchanged.

## Single-message independence

An independent AI receiving one ordinary JSON .txt or .json message can read:

- The full original UCL guide, definitions, claims, orientation, history, prior acts, acknowledgements and integrity data under the fully retained `packet` key.
- All SAP-1 structural field names, typing constraints, permitted actions and stances, exact-reference rules, formula examples and a step-by-step authoring procedure under `structural_rules.rules`.
- Cryptographic fingerprints of both the embedded structural rulebook and the entire enclosing message, in addition to the packet's original UCL 1.0 integrity.

No URL, API key, centralized registry, online schema service, GitHub access or hidden external guide is required to read or construct a reply. A local validator is useful to ensure correctness but need not use any network or external packages.

## Envelope shape

The experimental outer JSON object has exactly five keys: `format`, `profile`, `structural_rules`, `packet`, and `checksum`. Its `format` string is `UCL/2.0-SAP1-PORTABLE-DRAFT`; `profile` is `portable`. `structural_rules` has keys `rules` and `sha256`. The `packet` is the entire original validated UCL 1.0 packet including its full `guide`. All fields and rulebook content are physically embedded in every exported message.

## Canonical integrity

Use UCL 1.0 canonical JSON encoding (`ucl.canon`) for every hash. The structural rules hash is Base64url without padding of SHA-256 of UTF-8 prefix `UCL-SAP1-RULES-DRAFT-1\n` concatenated with canonical embedded `rules`. The envelope checksum uses prefix `UCL-SAP1-ENVELOPE-DRAFT-1\n` and canonical envelope *excluding* the `checksum` key. The full inner packet's existing cryptographic integrity is separately checked without changing its format.

These are consistency and compatibility checks, **not proofs of authorship or authority**. A malicious author can recompute untrusted self-hashes; independent validators should compare the embedded rule set to a locally trusted published implementation/version. No central online authority is necessary.

## Offline usage

From the repository root with Python 3.10+, using standard library only:

`python tools/sap_portable.py encode examples/cross_model_conversation_8_turns.json message_2_0.txt`

`python tools/sap_portable.py check message_2_0.txt`

`python tools/sap_portable.py decode message_2_0.txt restored_1_0.json`

Wrapping an existing packet does not translate or modify its semantics. In the AI-to-AI experiment the model authors its own symbolic contribution, the host mechanically appends history and hashes, and the newly transmitted JSON includes all SAP-1 rules; the other model sees the full independently checkable message.

## Novel hypotheses and language evolution

The 11 existing core glyphs remain fixed. Models may independently reason in well-typed UCL and introduce concepts with properly defined custom symbols. Unknown operators are not silently approved. A proposed novel operator can be explicitly described as a **non-normative language extension proposal** in an act note, preserved for research and versioned review. A valid structure does not prove its proposition true.

SAP-1 currently validates a narrow response contribution with one ACK; it is not yet a general replacement for every UCL 1.0 act or arbitrary new definitions. A second independently written validator and cross-language conformance vectors are prerequisites for formal UCL 2.0 release.

## Historical control

The successful November 22 eight-turn UCL-only run (8/8 first-attempt valid UCL messages; 4/7 correct complete prior-intent receipts) used the earlier prompt-provided SAP-1 with UCL 1.0 Portable transport. The embedded-rules envelope is a subsequent change and must be evaluated on its own without retroactively describing the earlier experiment as a 2.0 wire test.
