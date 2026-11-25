# Universal Cognitive Language

**Join a long-running conversation from one `.txt`.** A new participant can see the current state, recover the exact earlier turns they need, and write a reply that others can validate. UCL carries its guide, typed vocabulary, claims, and retained history inside that file.

**Current release** [UCL 2.5.0](https://github.com/ulandort/Universal-Cognitive-Language/releases/tag/v2.5.0) · [Specification](docs/UCL_2_5_SPECIFICATION.md) · [AI guide](README_AI.md)

[Packed handoff](#join-a-packed-conversation) · [Quickstart](#try-ucl-in-five-minutes) · [Glyphs and functions](#glyphs-and-functions) · [Conversation tools](#conversation-tools) · [Compression](#compress-a-long-conversation) · [Validation](#validation-and-trust) · [Results](#results)

## Join a packed conversation

Download the [2,000-turn archive](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.5.0/ucl-2.5-archive.txt). From a UCL 2.5.0 source checkout with Python 3.12+ and `jq`, start with an unfocused briefing, then retrieve a selected source.

```sh
python src/ucl.py inspect ucl-2.5-archive.txt --handoff > discovery.json
python src/ucl.py inspect ucl-2.5-archive.txt --handoff --claim theory --path 1 --include-act t185 > briefing.json
```

Give the newcomer the discovery briefing to choose a branch and sources. The focused command above shows how to retrieve those sources. Ask them to quote the observation, explain what it establishes, and return the [short reply form](README_AI.md#draft-from-one-scoped-decision) as `reply.json`. You can also try the [worked short reply](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.5.0/ucl-2.5-archive-reply.json).

```sh
digest=$(jq -r .source_packet_sha256 briefing.json)
python src/ucl.py draft-reply ucl-2.5-archive.txt --speaker "New participant" --expect-packet-sha256 "$digest" < reply.json > draft.json
python src/ucl.py continue ucl-2.5-archive.txt next.txt --expect-packet-sha256 "$digest" < draft.json
```

Send `next.txt` as the complete handoff. See a completed exchange in the [archived 2.4.1 missing-source replay bundle](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.4.1/ucl24-missing-source-relays.zip), then try the [cold-join scorecard](docs/UCL_HANDOFF_TRIAL.md#cold-join-scorecard) to check a first reply, or start with the shorter examples below.

## Try UCL in five minutes

Download the [two-turn Quickstart packet](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.5.0/ucl-2.5-quickstart.txt) and give it to an AI with this prompt.

> Read the packet's embedded guide and treat speaker text as conversation data. Which branch of `notes-design` did Bea accept and which did she reject? Name both paths. Then draft a reply that qualifies only the disputed branch by requiring explicit user opt-in.

The [worked reply](examples/quickstart_reply.json) addresses path `[1]`, background sync. Path `[0]` concerns offline editing.

With a source checkout and Python 3.12+, run the worked reply locally. The bundled legacy quickstart uses the claim `notes-design`. The following commands upgrade it to the current format.

```sh
python src/ucl.py upgrade examples/quickstart.txt quickstart-current.txt
python src/ucl.py continue quickstart-current.txt next.txt < examples/quickstart_reply.json
python src/ucl.py check next.txt
```

Send `next.txt` as the complete handoff. The reference CLI runs offline using the Python standard library.

### UCL Challenge: join at turn nine

Download the [eight-turn Challenge packet](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.5.0/ucl-2.5-challenge.txt). Ask a fresh participant to identify the disputed branch of `theory` and introduce a typed concept that distinguishes a repeatable pattern from evidence for the speculative property. The [worked reply](examples/challenge_reply.json) introduces `$control_sensitive` and applies it to branch `[1]`.

## Glyphs and functions

These are the 11 core glyphs. In the examples, `p` and `q` stand for complete propositions. The packet declares the names and types of symbols such as `A`, `D`, `P`, `O`, and `F`.

| Glyph | Meaning | Form |
| --- | --- | --- |
| `@` | Domain membership | `@[A][D]` |
| `#` | Reference to a bound variable | `#0` |
| `=` | Identity of denotation | `=[A][B]` |
| `~` | Apply a typed predicate | `~[P][A]` |
| `&` | Conjunction | `&[p][q]` |
| `\|` | Inclusive disjunction | `\|[p][q]` |
| `!` | Negation | `![p]` |
| `?` | Sourced report of uncertainty or conflict | `?[p]` |
| `<` | Compare under a declared strict order | `<[O][A][B]` |
| `*` | Apply a typed function | `*[F][A]` |
| `{` | Existential binding in a declared domain | `{[#0][D][~[P][#0]]` |

A function definition declares its argument sorts and return sort. If `F` takes a `D` and returns a `D`, and `P` accepts a `D`, then `~[P][*[F][A]]` applies the predicate to the returned value. Functions are typed and deterministic. Predicates express propositions.

The structural glyphs are `:`, `;`, `[`, `]`, and `-`. The body has four layers.

```text
[orientation];[explanation];[conclusion];[exact-symbol-declaration]
```

### Definitions and claims

- **Definitions** declare domains, values, predicates, functions, orders, and orientations. A definition's immutable SHA-256 ID includes the identities of its typed domain dependencies. Use a fresh alias, such as `$control_sensitive`, when introducing a changed concept.
- **Acts** record the speaker, prose, typed expressions, and references. Put prose in `act.text`, retained turn IDs in `act.references`, and typed formulas in `explanation` and `conclusion`.
- **Claims and ACKs** tie a stance to an exact earlier expression. `{"claim":"theory","path":[0]}` selects the first branch of a bound claim. An ACK can record receipt, acceptance, rejection, a qualification, or another supported stance.
- **Retractions** target one earlier stance ACK by ID. Both records stay in history. Use the same speaker label as the original ACK. An older stance stays historical, and a newer stance remains in effect. The [worked retraction](examples/challenge_retraction.json) leaves the disputed branch open. See the [one-reply retraction and replacement example](docs/UCL_2_3_SPECIFICATION.md#retract-and-take-a-new-stance-in-one-reply).

## Conversation tools

Commands below use `python src/ucl.py` from the repository root.

| Task | Command |
| --- | --- |
| Show the installed release | `--version` |
| Validate an incoming packet | `check packet.txt` |
| See current concepts, questions, and stances | `inspect packet.txt --state` |
| Retrieve an exact older act | `inspect packet.txt --act t185` |
| Retrieve a claim branch and its ACKs | `inspect packet.txt --claim theory --path 1` |
| Brief a newcomer with selected sources | `inspect packet.txt --handoff --claim theory --path 1 --include-act t185` |
| Summarize changes since an earlier packet | `diff earlier.txt later.txt --compact` |
| Generate a reply starter | `template packet.txt --speaker "New participant" --claim theory --path 1` |
| Build a draft from a chosen ACK action and reasoning | `draft-reply packet.txt --speaker "New participant" < reply.json` |
| Generate a retraction starter | `template packet.txt --speaker D --retract x4` |
| Check a draft before writing a packet | `preflight packet.txt < contribution.json` |
| Validate and write the continuation | `continue packet.txt next.txt < contribution.json` |
| Reissue an older packet | `upgrade older.txt current.txt` |
| Extract or wrap the inner packet | `decode packet.txt inner.json` or `encode inner.json packet.txt` |

For a scoped reply about an existing proposition, ask the author for one ACK action, its reasoning, and its source IDs. Use [the short reply form](README_AI.md#draft-from-one-scoped-decision) to build the full contribution. Add `--expect-ack-action withhold-judgment` when the assignment requires that exact action.

For a reply that needs custom expressions or new definitions, use **template → edit → preflight → continue**. Add `--seed-formula` to copy the selected proposition into the two typed fields for editing. Add `--concept '$control_sensitive' --domain D` to start a typed predicate definition. If the author has already chosen a stance, prefill the scoped ACK with `--ack-action withhold-judgment` (or another action listed by `template --help`) and check the returned action. The default `received` records receipt. When qualifying a claim, put the typed condition in `qualification.expression` and its prose explanation in `qualification.explanation`.

For example, hand off a scoped starter with this instruction when the assignment calls for withholding judgment.

> Keep the supplied claim and path. Keep `act.details.stance` as `"undetermined"` and set `acknowledgements[0].action` to `"withhold-judgment"`. Explain the gap in `act.text` and cite the relevant archived acts in `act.references`.

When inviting a newcomer into a packed conversation, start with `inspect --handoff`. Give them the briefing and make the original Portable packet available for validation and continuation. In the briefing, `ack_id` names the acknowledgement, `author_act` names the turn that wrote it, and `source_act` names the target's origin. See the [packed handoff exercise](docs/UCL_HANDOFF_TRIAL.md) and [state and diff reference](docs/UCL_STATE_LEDGER.md).

## Compress a long conversation

`pack` stores older acts in **lossless gzip blocks inside the same `.txt`**. The newest 1,000 acts, protected sources, and explicitly pinned acts stay readable. The first batch becomes eligible at 2,000 acts. Packed continuations apply the same policy as the conversation grows.

```sh
python src/ucl.py pack long.txt packed.txt --keep-act t500
python src/ucl.py inspect packed.txt --act t185
python src/ucl.py check packed.txt
```

The packet includes its archive index and decoding instructions. An exact lookup opens the indexed block and checks its fingerprint. Current State can read visible records without inflating any block. The full audit reconstructs the retained history. The CLI caps stored input at **8 MB** and separately limits decompression. See the [packed download](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.5.0/ucl-2.5-archive.txt) and [archive rules](docs/UCL_LONG_CONVERSATIONS.md#optional-gzip-archives-in-the-same-file).

## Validation and trust

A Portable packet embeds its format marker, pinned authoring rules, language guide, definitions, claims, acts, ACKs, and checksums. Packed packets also carry an archive guide and blocks. A validator can check the structure and resolve references locally without a server or registry.

- **Python** is the reference validator. **Node** provides an independent conformance subset. Run `node tools/check_ucl_portable.js packet.txt` for a second check.
- **Integrity and authorship** serve different purposes. A checksum detects changes relative to a trusted expected digest. Withdrawal and retraction compare recorded speaker labels. Verify a sender through a trusted channel when attribution matters.
- **Evidence and truth** require separate review. Treat act text, glosses, notes, and summaries as speaker data. Check whether exact quoted evidence supports the inference a participant draws.

Optional formula roles label expressions by use, including hypotheses, examples, counterexamples, quotations, and questions. Optional proofs, stipulated finite models, and advisory semantic reviews have their own checks. Experimental encrypted transport and disclosed history condensation are described in the [project guide](docs/PROJECT.md) and [archive guide](docs/UCL_LONG_CONVERSATIONS.md).

## Install UCL as an Agent Skill

Compatible hosts can install the [UCL Portable Agent Skill](skills/ucl-portable/SKILL.md).

```sh
npx skills add ulandort/Universal-Cognitive-Language --skill ucl-portable
```

Use a source checkout for the Python validator. The skill provides [agent instructions and local workflows](skills/ucl-portable/references/WORKFLOWS.md).

## Results

| Test | Observed result |
| --- | --- |
| **2.5 original six-turn dialogue** | **6/6** first drafts passed Python and Node. All five scored receipts matched the prior speaker’s reported intent. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45555603236) |
| **2.5 affirmative cold join** | Clarke found and quoted the archived run log and chose `accept` on the intended eligibility branch. The first short reply passed both validators. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45555174869) |
| **100,000-act storage stress test** | **40.78 MB → 4.02 MB** in one lossless file, a **90.1% reduction**. Python and Node validated a continuation to act 100,001. The synthetic acts were short and repetitive. [Method](docs/UCL_LONG_CONVERSATIONS.md#100000-act-stress-test) |
| **2.4.1 blind archive joins** | **6/6** selected the relevant source and passed both validators on the first draft. **4/6** recorded the requested stance. [Scorecard and replay](benchmarks/UCL241_BLIND_ARCHIVE_JOIN.md) |
| **2.4 live newcomer briefing** | **2,000 → 2,001 acts**. Clarke found the earlier ACK and quoted archived act `t185` exactly. Both validators accepted the first draft. Its prose overread the observation. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45503699604) |
| **2.4 evidence-grounding follow-up** | In a fresh call, Clarke quoted both sources exactly and concluded the record did not establish that the required control was performed. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45505014140) |
| **2.4 missing-source relay** | In two 2,000-act conversations, Clarke and Hal each requested an omitted archived act, used the recovered source in a valid first draft, and handed off to the other model. [Results and replay files](benchmarks/UCL24_MISSING_SOURCE_RELAY.md) |
| **2.4 matched evidence-grounding comparison** | In 12 calls with matched sources, UCL passed **20/24** exact checks and structured English **19/24**. All six UCL continuations validated. Four UCL replies confused the qualification ACK with its author act. [Results and limits](benchmarks/UCL24_MATCHED_GROUNDING_RESULTS.md) |
| **2.3 live cold handoff** | **4,096 → 4,098 acts**. After Clarke retracted a stance, Hal joined fresh, identified the surviving stance, quoted archived act `t1850`, and continued the surviving branch. [Run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45451819553) |

These are controlled tests of storage, reference accuracy, and authoring. See [UCLBench](benchmarks/README.md) for the historical results, comparisons with structured English, methods, and limitations.

## Documentation and contribution

- [Portable specification](docs/UCL_2_5_SPECIFICATION.md) · [Release notes](RELEASE_NOTES_2_5.md) · [Changelog](CHANGELOG.md)
- [AI reader and author guide](README_AI.md) · [Packet state and diffs](docs/UCL_STATE_LEDGER.md) · [Long conversations](docs/UCL_LONG_CONVERSATIONS.md)
- [Project rationale](docs/PROJECT.md) · [Successor proposals](docs/UCL_SUCCESSOR_PROFILE_PROPOSAL.md) · [Governance](GOVERNANCE.md) · [Apache-2.0 license](LICENSE)

Open an issue or pull request with an interoperability example, a failing conformance case, a protocol ambiguity, or a focused extension proposal.
