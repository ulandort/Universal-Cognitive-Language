# Universal Cognitive Language — UCL/2.0 normative Portable specification

**Status:** UCL/2.0 stable release profile. **Wire identifier:** `UCL/2.0-SAP1-PORTABLE`. **Encoding:** UTF-8 JSON in a local `.txt` or `.json` file. No network, schema server, centralized authority, mandatory remote registry or interpreter is required to receive and parse a message.

The canonical implementation lives in `src/portable.py`, which validates the embedded typed packet using the unchanged internal grammar in `src/core.py`. The public versioned Python interface is `src/ucl.py`; `tools/sap_portable.py` is a forwarding compatibility CLI, not a second implementation. The independently written JavaScript implementation `tools/check_ucl_portable.js` validates the outer envelope, exact pinned guides and the supported subset of inner packet semantics. Its known scope limitations do not silently relax Python's requirements.

## 1. Envelope

A Portable message MUST be exactly one JSON object with keys `format`, `profile`, `structural_rules`, `packet` and `checksum`, optionally **both** `formula_roles` and `formula_role_guide`. It MUST NOT require or link to any remote standard.

- `format`: exactly `"UCL/2.0-SAP1-PORTABLE"`
- `profile`: exactly `"portable"`
- `structural_rules`: object with exactly `rules` and `sha256`; rules are the **complete immutable, locally pinned SAP-1 authoring instructions** shipped with this 2.0 profile
- `packet`: the entire, independently valid inner typed UCL packet with **all** its guide, definitions, discourse, claims, acknowledgements, history, context, symbolic body, and integrity record; no field of the inner packet may be omitted simply because it seems repeated
- `checksum`: outer SHA-256 checksum in Base64url without padding
- `formula_roles` (optional): ordered list of at most 512 author-declared `{act,index,role}` triples; exact act ID must exist and index must be a nonnegative integer below the expression count; at most one role per act/index pair
- `formula_role_guide` (mandatory with `formula_roles`): exact pinned role guide, a communicative *intent* description, not a truth assertion

Exactly supported roles: `hypothesis`, `example`, `counterexample`, `quotation`, `question`. An absent role conveys no special status. An unrecognized role or unknown extension field is a format error in this version.

## 2. Canonical encoding and checksums

Let `C(x)` be the existing UCL-CJSON-1 canonical JSON **byte** encoding, defined in [the inner typed grammar specification](SPECIFICATION.md): sorted Unicode scalar code-point property keys, ASCII escaped strings, no unpaired surrogates, and safe integers (without fractional JSON numbers). Compact and pretty-printed input have the same canonical digest. UCL-CJSON-1 is distinct from RFC 8785.

Let `B64(x)` mean Base64url **without padding**. The exact algorithms are:

```text
rules_sha256 =
  B64(SHA256(UTF8("UCL-SAP1-RULES-2.0\n") || C(structural_rules.rules)))

checksum =
  B64(SHA256(UTF8("UCL-SAP1-ENVELOPE-2.0\n") ||
      C(all envelope fields except checksum)))

inner packet integrity =
  B64(SHA256(UTF8("UCL-PACKET-7\n") ||
      C(packet excluding its integrity field)))

definition identity =
  B64(SHA256(UTF8("UCL-SEM-9\n") || C(definition)))
```

The `\n` above is the ASCII LF byte and part of the domain prefix. Structural rules MUST match the exact published stable-2.0 ruleset, not merely an attacker-authored blob with a freshly recomputed hash. A receiver MUST independently validate the entire inner packet; the outer checksum alone cannot establish inner integrity. A checksum is **not authentication**, a signature, evidence of an AI's identity, evidence of truth, or proof of semantic equivalence. Treat self-asserted sender identities as unverified unless independently authenticated.

## 3. Inner language and discourse

The 11 core glyphs remain unchanged: `@`, `#`, `=`, `~`, `&`, `|`, `!`, `?`, `<`, `*`, `{`. Read [the core specification](SPECIFICATION.md) and the packet's physically embedded `guide` for exact type signatures, expression syntax, provenance requirements and finite limits. Symbols introduced by independent authors must include typed definitions and immutable SHA-256 definition IDs.

An inner packet's symbolic body has four bracketed layers:

```text
[orientation];[explanation];[conclusion];[exact symbol declarations]
```

A receiver MUST preserve the intended meaning of any valid original expression. Parsing and type checking DO NOT prove that a claim is true. Proof annotations and finite-model consistency checks are distinct from empirical claims or a sender's communicated commitments.

Ordered `discourse.acts` retain their exact IDs, authorship labels, typed expressions and cross-references; claims bind to specific original expressions. Scoped acknowledgements differentiate `received`, `understood`, `accept`, `reject`, `qualify`, `clarify`, `propose-revision`, `adopt-for-discussion`, `withhold-judgment`, and `withdraw`. ACK target paths contain **integer** JSON indices (`[0]`), not digit strings (`["0"]`); `qualify` requires a valid nonnull qualification, while other actions must not silently add one. A model's disagreement does not invalidate the protocol.

## 4. Local authoring and validation

A model may author a new typed expression and an exact-response object. The Portable envelope includes complete, compact authoring instructions **in the file itself**. Any locally implemented validator may reject malformed expressions, impossible references, changed historical acts or tampered hashes. It must never change the author's semantic content silently to make a message pass. A model can explicitly reauthor after receiving precise local error feedback.

Standard local commands from the repository root:

```bash
python src/ucl.py encode examples/cross_model_conversation_8_turns.json portable.txt
python src/ucl.py check portable.txt
python src/ucl.py decode portable.txt reconstructed-inner.json
node tools/check_ucl_portable.js portable.txt
```

The offline reference tools use only Python's standard library and Node's built-in libraries. JavaScript does not provide every optional proof/model operation implemented by Python; deployments requiring full structural parity MUST run the Python reference checker or independently implement and test those operations.

## 5. Conversation growth, optional features, and limits

The normal packet carries all active definitions and historical context required by its embedded guide. Fully expanded history was used in the L25/L50 live pilot. **Optional explicit condensation** must disclose omitted scope, never silently delete required references, and must never claim that omitted utterances can be recovered from a summary. This is a protocol property, not a requirement to condense short conversations.

Formula-role annotations are OPTIONAL. Decentralized SVP-1 advisory semantic review is OPTIONAL, and no claimed verifier result is a mandatory on-wire field. Experimental AES-256-GCM encryption and Brotli compression are not mandatory and do not replace plaintext Portable. The 2.0 format does not promise arbitrary unknown 2.1 extensions will be understood by old readers.

The reference implementation imposes concrete byte, nesting, definition, discourse and acknowledgment limits; readers MUST enforce the limits of the pinned version, not silently truncate malformed or oversized packets. Transport overhead and input token cost grow with fully expanded history.

## 6. Conformance and research claims

For **Portable 2.0 structural conformance**, a checker MUST reject unknown top-level keys, modified embedded rules, invalid formula role references, invalid or corrupted inner packets, unsupported grammar, broken definition identity and incorrect checksums. Python `sap_portable.decode()` is the full reference structural implementation. JavaScript `check_ucl_portable.js` is an independent implementation with a clearly declared inner semantics subset; it must not claim untested full parity.

Clarke and Hal's paid research provided 48/50 validated deliveries, 45/50 first-attempt successes in the L50 experiment; see [full evidence](../benchmarks/AUTONOMOUS_50_RESULTS.md). These are **one exploratory conversation's outcomes**, not blanket reliability figures, semantic superiority over English, or proof of independent comprehension. The release claims bounded mechanical interoperability and self-contained structured communication—not metaphysical, philosophical, empirical, or comparative language superiority.

UCL/1.0's standalone format is retired as the **default release transport** by 2.0, but its original glyph and typed-expression grammar remains physically inside the 2.0 envelope. This is a deliberate architectural choice, not a new glyph alphabet.
