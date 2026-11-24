# UCL — AI reader and author guide

**Purpose:** Independently authored, precisely referenced communication across different intelligences. A complete UCL message is a self-contained JSON `.txt` or `.json` file. **The message's actual embedded guide and typed definitions are the source of meaning**, not this README or a hosted registry.

> **Current release** UCL 2.4.1 · **Packet format** `UCL/2.4-SAP1-PORTABLE`. Follow the embedded `UCL/1.4` guide for definition hashing and typed reply authoring.

## Agent Skills distribution

Compatible agent hosts can install [`skills/ucl-portable/SKILL.md`](skills/ucl-portable/SKILL.md) using `npx skills add ulandort/Universal-Cognitive-Language --skill ucl-portable`. The skill explains locally validated reading and authorship; it is **not a runtime or dependency** of the Portable protocol. See its [portable workflows](skills/ucl-portable/references/WORKFLOWS.md). The UCL Python implementation must be obtained separately when local checking is requested.

## Detect and read the format

For UCL Portable, read the outer `format` and `profile`, verify `structural_rules.rules` against its pinned local profile and `structural_rules.sha256`, verify the outer `checksum`, and independently validate the embedded `packet` including `packet.guide` and `packet.integrity.sha256`. When present, validate optional `formula_roles` against their declared act and expression index. An unsigned checksum provides integrity relative to a trusted expected identity—not sender authentication.

**No remote lookup, central service, third-party judge, executable guide, or language conversion is required to interpret a complete Portable packet.** The rules travel with it. Local validators are optional software implementations but required for authoritative *mechanical checking*.

## Read symbolic content literally

```text
Core glyphs: @ # = ~ & | ! ? < * {
Structure:   : ; [ ] -
Body:        [orientation];[explanation];[conclusion];[exact symbol declarations]
```

`@[a][D]` is membership; `#N` is a scoped bound variable; `=[a][b]` is identity; `~[P][a]` is a defined typed predicate; `&[p][q]` and `|[p][q]` are conjunction and inclusive disjunction; `![p]` is negation; `?[p]` is an epistemic report requiring the stated provenance, **not** an ordinary unanswered question; `<[R][a][b]` is a defined strict order; `*[f][a]` applies a defined function; `{` introduces typed existential binding. Consult the embedded guide for all type, scoping, arity and evidence requirements.

Named aliases such as `$background_sync` are interpreted using the same embedded catalog as single-character aliases.

**Never assume** `P`, `B`, `C`, `E`, `G`, `K`, `M` or `N` has a universal meaning. Each is a symbol whose meaning and immutable SHA-256 identity are defined **in that packet**.

## Read the conversation

Read all retained `discourse.acts`, their exact formal `expressions`, readable `text`, `references`, `claims`, `viewpoints`, `acknowledgements`, `revisions` and `history`. Distinguish *understood* from *accept*, hypothetical example from empirical evidence, quoted claims from endorsement, and source attribution from logical validity.

An explicit ACK targets a claim and expression path, e.g. `{"claim":"theory","path":[0]}`. Indices are **integers**, not strings. `qualify` requires a substantive `qualification`; other actions require that field to be null. `withhold-judgment` does not automatically warrant an epistemic `?` expression. `withdraw` applies only to the speaker's own previously authored claims.

**Disagreement is not a communication failure.** Do not conflate the receiver's objection with misunderstanding. Treat novel reasoning as a new hypothesis, not as a malformed message merely because it is unfamiliar.

If `history.status` is `condensed`, honor the disclosed omission scope and do not pretend to remember omitted utterances. The live L25/L50 research explicitly retained all delivered acts rather than condensing them.

When joining a packed Portable conversation, start with `inspect --handoff` for Current State, an exact claim branch, and any earlier sources you need. A briefing's `ack_id` identifies the acknowledgement, `author_act` identifies the act that wrote it, and `source_act` identifies the target's origin. The raw focused views label the author act `by`. Use `inspect --act ACT_ID` and `inspect --claim CLAIM_ID --path PATH` for individual lookups. Read the packet's `archive_guide` and continue from the complete Portable file.

A 2.4 packet includes exact ACK retraction rules in its embedded guide. `template packet.txt --speaker NAME --retract ACK_ID` seeds a contribution that retracts the named speaker's earlier stance. In inspection output, `retracts` is the original ACK ID and `original_ack_act` is the act that authored it. See the [2.4 specification](docs/UCL_2_4_SPECIFICATION.md).

## Author a response

1. Independently decide the intended position, reasoning, scope and relevant earlier references.
2. Preserve all existing definitions, IDs, earlier delivered acts, claim bindings and relevant uncertainty. Define new concepts with appropriate types and new immutable identities; never overwrite a definition.
3. For a scoped reply with the local CLI, use **template → edit → preflight → continue**. With the packet alone, use `structural_rules.rules.reply_template` and the embedded `packet.guide.reply_authoring` example. Add `--seed-formula` when the selected proposition is an appropriate starting point. Write prose reasoning in `act.text`, cite retained turns in `act.references`, and use defined symbols in executable expressions.
4. Construct exact acknowledgement fields. A target like `"path":["0"]` is invalid; use `"path":[0]`. For `action:"qualify"`, provide a real qualification; do not leave `null`.
5. Verify expression types and grammar locally. Ensure `act.expressions` is a list of valid expression strings and `explanation`/`conclusion` are correctly typed expression strings.
6. Append the authored contribution mechanically to the retained history, regenerate the deterministic integrity hashes, and recheck the complete packet. **Do not silently convert, rewrite or repair the author's semantic content.** If validation fails, return exact feedback to the author for an explicit revision.
7. Interpretations or semantic-audit comments may be included as **advisory metadata**, but a short explanation must never invalidate an otherwise valid UCL message.

### Existing offline tools

```bash
python src/ucl.py check incoming-ucl2.txt
node tools/check_ucl_portable.js incoming-ucl2.txt
python src/ucl.py inspect incoming-ucl2.txt --handoff --claim theory --path 1 --include-act t37
python src/ucl.py template incoming-ucl2.txt --speaker "New participant" --claim theory --path 1 --seed-formula > contribution.json
# Edit contribution.json before validating it.
python src/ucl.py preflight incoming-ucl2.txt < contribution.json
python src/ucl.py continue incoming-ucl2.txt next.txt < contribution.json
python src/ucl.py diff incoming-ucl2.txt next.txt --compact
```

The Node checker is an independently implemented Portable-envelope/inner-packet conformance **subset** with cross-language tests; it should not be represented as a complete proof/model or all-optional-extension interpreter. The public Python entry point is `src/ucl.py`, backed by `src/portable.py` and the typed grammar and vocabulary validation in `src/core.py`. The Python reference is the authoritative structural implementation. See the [2.4 specification](docs/UCL_2_4_SPECIFICATION.md).

For experimental details and actual evidence, see [README](README.md), [L50 live result](benchmarks/AUTONOMOUS_50_RESULTS.md), [historical Portable draft](docs/SAP1_PORTABLE_DRAFT.md) and [release-readiness](docs/UCL_2_0_RELEASE_READINESS.md).
