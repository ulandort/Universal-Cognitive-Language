# UCL/1.0 normative specification (plain JSON profile)

This document specifies the archived 1.0 inner format. See [Portable 2.3](UCL_2_3_SPECIFICATION.md) for the current release.

**Version identifier:** exactly `UCL/1.0`. This document describes the normative data profile checked by the Python reference implementation. The source implementation is the operational reference for expression parsing, act-detail schemas and exact validation rules. Other conforming implementations MUST match the declared canonical serialization, definition identities, packet integrity, and language semantics. A private model's interpretation is not a conformance proof.

## Envelope and self containment

The **default wire form** is a UTF-8 text file whose contents are one JSON object, optionally pretty printed; no fences, prompt preface, compression, Base64, interpreter or external URL is necessary. The object contains exactly: `guide`, `definitions`, `domains`, `model`, `proof`, `context`, `body`, `links`, `revisions`, `discourse`, `acknowledgements`, `history`, `claims`, `viewpoints`, `integrity`. The `guide` includes the grammar, symbol table and version. All required active semantic definitions, discourse references and targetable claims MUST be included in the message. Nothing refers to a remote registry for correctness.

### Four-layer body

`[orientation];[explanation];[conclusion];[exact-symbol-declaration]`.

The first layer is a declared orientation symbol of kind `orientation`; explanation is a typed proposition; conclusion is a typed proposition or (when provenance requirements are satisfied) an epistemic record. The fourth layer lists exactly the core and custom glyphs used throughout all parsed expressions and declaration-bearing content, sorted by code point; custom glyphs use `<glyph>:<full-definition-id>`. A parser must not silently infer or append unlisted glyphs. The authoring tool may calculate this layer automatically.

### Eleven core glyphs

| Glyph | Meaning | Formal shape |
|---|---|---|
| `@` | membership | `@[term][domain]` |
| `#` | scoped bound variable reference | `#0`, `#1`, ... |
| `=` | denotational identity | `=[term][term]` |
| `~` | typed predicate/relation application | `~[P][x]` |
| `&` | conjunction | `&[p][q]` |
| `&#124;` | inclusive disjunction | `&#124;[p][q]` |
| `!` | negation | `![p]` |
| `?` | sourced epistemic uncertainty/conflict (not lack of data) | `?[p]` |
| `<` | named strict ordering | `<[O][a][b]` |
| `*` | total deterministic typed function | `*[F][arg...]` |
| `{` | existential quantification over explicit domain | `{[#0][D][p]` |

Five structural glyphs `: ; [ ] -` are reserved. Universals are expressible through negated existential quantification. Types, binder scope, ordering and optional finite model interpretations are checked by the reference parser. Ordinary conversations require **no proof** and may be speculative.

## Definitions and hashing

Each noncore glyph carries a complete definition object and `id`. Define `C(x)` as UCL-CJSON-1: JSON with ASCII escaped strings, Unicode scalar-value code-point ordering of object keys, no unpaired surrogates, no fractional JSON numbers, and integers confined to the IEEE-754 safe integer range; decimal fractions are exact strings. No undefined/NaN/Infinity. Python reference implementation (`canon`) and JS checker produce matching canonical bytes for tested vectors. This profile is not RFC 8785.

`definition_id(d) = BASE64URL_NOPAD(SHA256(UTF8("UCL-SEM-9\n") || C(d)))`

`packet_id(p) = BASE64URL_NOPAD(SHA256(UTF8("UCL-PACKET-7\n") || C(p without the integrity field)))`

A complete valid packet contains `"integrity":{"sha256":"..."}`. Hashes detect altered canonical content; **they are not sender authentication or proofs of semantic equivalence**. To change a semantic definition, introduce a fresh glyph/ID, retain previous identity and a transparent revision record. Do not reuse the old identifier for new meaning.

## Discourse, quotations and acknowledgements

`discourse.acts` is ordered, contains unique IDs, has explicit `speaker`, `kind`, textual description, typed `expressions`, `references`, and act-specific `details`; `discourse.current` names the latest act. References resolve to retained prior acts. Act edges are **not evidence** of truth or sender identity. `claims` bind an exact prior act expression to a claim ID. `viewpoints` can report a holder's belief/assertion/question about an existing claim or viewpoint without committing the reporting intelligence to its content; cycles and invalid ownership are rejected.

Acknowledgements are **optional**, not a mandatory third ruleset. Each record contains `id`, `by` (a retained act), `target` (`{act,expression_index}` or `{claim,path}`), `action`, `qualification`, `replacement`, `note`. Actions include `received`, `understood`, `accept`, `reject`, `qualify`, `clarify`, `propose-revision`, `adopt-for-discussion`, `withhold-judgment`, `withdraw`; documented extension kinds may be declared separately. Targets may specify proposition subexpressions by a zero-based tree path. `withdraw` is limited to one's own claims; adopting for discussion is **not endorsing truth**. A rejected conjunction subclaim does not automatically reject its siblings.

## History and optional derivations

`history.status` is `fully-expanded` or `condensed`. A condensed message MUST disclose omitted scope, nature and implications, preserve all definitions and referenced acts/claims, and must not imply omitted content is reconstructable. The provided condenser is conservative and never a guarantee of summary adequacy. `proof` is optional. A proof is evaluated relative to stated premises with supported rules; invalid or unsupported optional proof is **separate** from packet structural validity. Finite model checking is distinct from factual verification and only possible with a supplied finite stipulated interpretation. Open or infinite domains do not become empty by default.

## Optional transport and security

Brotli is an **optional** lossless transport optimization; plain JSON is normative default and fully valid standalone. The `optional/` folder documents an experimental AES-256-GCM envelope with Argon2id (password mode) or direct 32-byte keys. Encryption covers complete packet bytes, not underlying truth or author authenticity. Out-of-band secret required. This experimental envelope is NOT claimed interoperable/audited as a frozen v1.0 security standard.

## Resource bounds and safety

The reference profile limits expanded bytes, nesting depth, definition count, discourse length, ACK count, proof steps and finite model tuple sizes. See `guide.limits` and `src/ucl.py` for exact validation. Never execute untrusted embedded scripts. Malformed input is rejected rather than silently amended by a validator. An optional separate authoring tool may construct a compliant packet from a draft; the resulting file must still validate. A flagged semantic inconsistency should generally be a warning, not invalidation of an otherwise open speculative conversation.

## Conformance and limitations

Conformance means a tool correctly handles the frozen 1.0 profile and canonical vectors for the claims it makes; the included JS checker is a **subset verifier**. The present release has not undergone a complete third-party review, formal threat modeling, independent security audit, or English comparison study. Branding and claims of *official certification* require separate approval as explained in `BRANDING_AND_CONFORMANCE.md`; this does not restrict compatible independent implementations or use of Apache-licensed materials.
