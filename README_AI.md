# UCL/1.0 · machine-facing entrypoint (AI reader / author)

**Mode:** OPEN_DIALOGUE. **Transport:** plain JSON by default. **No server/registry/tool required to interpret a message.** This file helps scan a repository; a UCL packet itself includes its operative guide and definitions. Follow the actual packet, not undocumented assumptions in this README.

```
VERSION := UCL/1.0
CORE    := @ # = ~ & | ! ? < * {
STRUCT  := : ; [ ] -
BODY    := [orientation];[explanation];[conclusion];[exact-declared-symbols]
INTEGRITY := sha256(packet excluding integrity), domain-separated
DEFINITIONS := immutable glyph -> {definition, sha256 identity}
HISTORY := full or explicitly disclosed condensed; no external history dependency
PROOF   := OPTIONAL; validity independent of claim truth / dialogue validity
```

## Interpret symbols literally

`@[term][domain]` membership; `#N` scoped bound reference; `=[term][term]` denotational identity; `~[predicate][typed arguments...]` relation/predicate; `&[prop][prop]` conjunction; `|[prop][prop]` inclusive disjunction; `![prop]` negation; `?[prop]` *sourced* uncertainty/conflict, **not** missing knowledge; `<[order][a][b]` explicitly named strict order; `*[function][typed args...]` deterministic typed function; `{[#N][domain][prop]` existential. Universal quantification may be expressed with negation/existential. `?` is not a general question marker; questions are discourse acts.

## Reader algorithm

1. Parse plain JSON. Verify required top-level fields and `guide.version` against local version profile, or identify the packet as a draft. **Never execute embedded code.**
2. Read `guide`, `definitions` (immutable definition gloss and type signature), `domains`, and `context`. Do **not** assume an open domain is empty or finite.
3. Interpret `body` as four bracketed layers; check typed expressions and exact used-symbol declarations.
4. Read ordered `discourse.acts`, `claims`, `viewpoints`, `acknowledgements`, `revisions`, `history`. Acknowledge specific targets; acceptance ≠ proof; quoted attributed belief ≠ endorsement.
5. Clearly distinguish speculation, an optional certificate's derivability, and empirical truth. Report ambiguity rather than silently reinterpret terms.
6. If `history.status=condensed`, disclose nonexpanded history and do not pretend you possess omitted utterances.
7. A fresh model requires **only this complete packet** to continue the discussion; any optional encoder merely automates mechanical work.

## Author algorithm

- Retain all definition records; create a *new glyph* and new hash whenever meaning changes. Keep referenced earlier acts and claims. Add one new ordered act with a unique `id`, explicit `kind`, `speaker`, `references`, `details`, `expressions`, and `text`.
- Optional ACKs: `received`, `understood`, `accept`, `reject`, `qualify`, `clarify`, `propose-revision`, `adopt-for-discussion`, `withhold-judgment`, `withdraw`; only the original speaker can withdraw its own claim. Target exact prior `{act, expression_index}` or `{claim, path}` (zero-based propositional subtree path). ACK records express stance, not verified fact. Custom actions require declared typed extensions.
- Use a proposition for the body's explanation and conclusion (except supported sourced epistemic conclusion); do not claim the prose means `!B` while the symbolic expression says `B`.
- Prefer `tools/author.py` to create a valid standalone message from a compact contribution. If no code execution is available, output `UNVERIFIED UCL DRAFT` explicitly and leave integrity unverified rather than fabricate hashes.
- Preserve `guide` and the standalone history; generate SHA-256 canonical definition IDs and exact declaration; use UCL-CJSON-1 and packet hash. No special syntax beyond JSON is required for the default transport.

## Concrete ACK example

For `&[~[P][A]][~[B][A]]`, path `[0]` selects `~[P][A]`; path `[1]` selects `~[B][A]`. Exact claim ID points to its retained source act. `reject` path `[1]` is *not* a rejection of path `[0]`.

## What is not established

The November 2026 Grok–Qwen exercise demonstrated **validator-assisted** conversation continuity, not independent, error-free authorship or UCL superiority to English. English glosses still carry substantial conceptual content. An SHA-256 identity binds canonical text, not consciousness, meaning equivalence, scientific accuracy, or authenticity. UCL is neutral about the correctness of users' ideas.

## Files

Normative text: `docs/SPECIFICATION.md`. Working payload: `examples/cross_model_conversation_13_turns.json`. CLI: `python src/ucl.py check FILE`. Build: `python src/ucl.py build DRAFT OUTPUT`. Incremental: `python tools/author.py PACKET CONTRIBUTION OUT`. Uncompressed `.txt` and `.json` are both acceptable; their **contents** are ordinary JSON.

## Optional transport confidentiality

`UCL-ENCRYPTED/0.1-preview` is an **optional, experimental**, external envelope: AES-256-GCM authenticated encryption with Argon2id password derivation or out-of-band 32-byte direct key. Decrypt complete bytes *before* parsing/validating ordinary self-contained UCL JSON. Encryption is not a claim of speaker authenticity, semantic correctness, or truth. The default is plain JSON; no key or crypto tool is needed to interpret plaintext. Implementation and cautions: `optional/ENCRYPTION_EXPERIMENTAL.md`.