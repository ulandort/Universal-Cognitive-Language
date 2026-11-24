# UCL state ledger

The ledger is a deterministic read view of a validated UCL Portable packet. It can be printed by `python src/ucl.py inspect packet.txt` or produced as JSON by `python src/ucl.py inspect packet.txt --json` for an unpacked packet. Without `--since`, packed files use a readable archive overview. Continue the conversation using the original Portable packet.

## Current State excerpt

`python src/ucl.py inspect packet.txt --state` emits a compact JSON excerpt. It includes up to 12 recently used definitions with their IDs, up to 12 recorded issue previews, five recent question acts, up to 12 latest stance records, and up to five speaker retirements. Preview fields may shorten prose or expressions. Follow a source act ID with `inspect --act` or a claim and path with `inspect --claim --path` for exact text. A recorded question stays visible even when someone has replied. The current file still carries the full definitions and retained records.

Each `latest_stances` entry has a `status`. `current` marks the latest recorded stance at that scope, which can include withholding judgment or adopting a claim for discussion. `withdrawn` marks the speaker's withdrawal of their own claim. `retracted` means the latest stance was cleared by a retraction. In that entry, `acknowledgement` is the retraction ACK ID and `retracts` is the original ACK ID. Retractions of superseded ACKs appear in `recent_retractions` while the newer stance keeps its own status.

For packed files, the excerpt verifies the envelope checksum and archive layout without inflating blocks. It reports visible and total act counts separately, and sets `whole_packet_audited` to false. Question counts cover visible acts. Gzip packing keeps stance authors, acknowledgement targets for substantive stances, and named claim sources visible. Run `check` for a full audit.

## Packet diff

`python src/ucl.py diff earlier.txt later.txt` validates both packets and compares their retained records. It requires the same grammar and preserves earlier acts, definition IDs, domains, claim bindings, acknowledgements, revisions and viewpoints. It reports new definitions, claim bindings, retirements, questions, revision records, and changes in author-recorded issues. Stance changes are based on the action, qualification and replacement at the same speaker and exact claim scope. A subsequent receipt or identical restatement does not count as a stance change. Repacking the same retained conversation leaves the changes empty. A diff checks continuity between the supplied packets, whose speaker labels are unauthenticated.

Add `--compact` for a paste-ready JSON line with both packet digests, full change counts, and up to eight entries each for new acts, stance changes, retractions, and definitions. Acts and stance changes carry their source IDs. The output shows the latest eight in record order and the first eight new definitions in alias order. Gloss and qualification previews use up to 160 characters. Use the full diff if you need complete records.

## Newcomer briefing

```sh
python src/ucl.py inspect packet.txt --handoff --claim theory --path 1 --include-act t185
```

The briefing includes Current State, the exact latest act, the selected claim branch and its source, and the definitions and domain declarations used by the included excerpts. Repeat `--include-act` to retrieve more acts in the requested order. Use `--path root` for the full claim with ACKs targeting that root. Omit `--path` for the full claim and ACKs from all its branches. The briefing includes the source packet digest, match counts for the selected acknowledgement excerpts, and the archive blocks opened. Packed packets open each requested block once. Run `check` to audit the full packed history.

Briefing version 2 uses three distinct reference labels. The labels apply both to focused ACK excerpts and to stance and retraction entries in its Current State.

| Field | Meaning | Example |
| --- | --- | --- |
| `ack_id` | The acknowledgement record | `condition37` |
| `author_act` | The act that authored the acknowledgement | `t37` |
| `source_act` | The origin of the target claim or expression | `t1` |

The raw `inspect --act`, `inspect --claim`, and `inspect --state` commands retain their existing field names. Packet ACKs still use `id` and `by` on the wire.

When an author has recorded issues, `open_issue` quotes the last entry in `packet.history.unresolved` verbatim and gives its JSON Pointer in the original packet. It is conversation-wide speaker data. It can refer to a different branch than the selected claim. When the list is empty, the field is null. Questions remain in Current State.

Use the original Portable file with the recipient's validator and authoring tools. The briefing is an excerpt for reading and prompting. Try the [outside-reader exercise](UCL_HANDOFF_TRIAL.md) to see whether a new participant can continue from it.

## JSON fields

| Field | Meaning |
|---|---|
| `ledger_version` | Integer `1`, the version of this inspection output |
| `packet_sha256` | The validated inner packet digest, in the packet's original base64url representation |
| `history_status`, `retained_act_count`, `omissions` | Recorded history coverage, observed retained act count, and ordered omission records |
| `recorded_summary`, `recorded_open_issues` | The exact summary and unresolved strings in `packet.history`, supplied by the packet author |
| `questions` | All retained question acts in act order, with `act`, `speaker`, and verbatim `targets` |
| `stances` | Latest recorded stance per speaker and exact target, ordered by the selected acknowledgements' chronology |
| `withdrawals` | Every retained withdrawal, in acknowledgement chronology |
| `retractions` | Every retained 2.3 stance retraction, including the original ACK ID and author act and whether it cleared the stance at that point |
| `recent_acknowledgements` | Last ten acknowledgements in acknowledgement chronology, including procedural actions |
| `symbols` | Defined symbols in code point order, including definitions absent from recent expressions |
| `comparison` | Present with `--since earlier.txt`. Includes `previous_packet_sha256` and the code-point-sorted `added_symbols` |
| `vocabulary` | Retained retirements, examples, and counterexamples in act and record order, with speaker, act, and resolved definition ID |

Each acknowledgement entry contains `speaker`, `by` (author act ID), `acknowledgement` (ACK ID), `action`, and the original `target`. It also contains the resolved `source_act`, `expression_index`, `path`, and `expression`, plus the original `qualification` and `replacement`. For a whole-act acknowledgement, `expression_index` and `expression` are null. The `expression` is the exact resolved subtree rendered in UCL syntax.

An example or counterexample also includes the referenced expression. A retirement includes the suggested successor and its resolved ID, both null when no successor was given.

Each symbol entry contains `symbol`, `definition_id`, `kind`, `gloss`, `first_retained_expression_act` (an act ID or null), the boolean `used_in_recent_acts`, and the ordered `recent_expression_acts` list of exact act IDs. Usage counts expressions directly listed in each act's `expressions` field. Recent usage covers the last five retained acts. First retained use does not establish when a symbol was introduced or whether it remains endorsed.

## Stance derivation

1. Read acknowledgements in the order of their author acts. Break ties within an act using their order in the packet's acknowledgement array.
2. Resolve each target to a retained source act, an expression index or null for a whole act, and a zero-based subtree path. A claim binding with an empty path and a direct reference to the same expression name the same target. Whole acts, whole expressions, and subtrees remain distinct.
3. For each pair of speaker label and resolved target, retain the last `accept`, `reject`, `qualify`, `adopt-for-discussion`, `withhold-judgment`, or `withdraw`. Receipt, understanding, clarification, revision proposals, and custom acknowledgement actions stay in the record without replacing such a stance.
4. Record every withdrawal separately. A withdrawal concerns its exact target and author.
5. Record every retraction separately. If it names the latest stance at that speaker and exact target, replace the current entry with the retraction marker. Earlier stances stay in history and do not resume. A retraction of a superseded ACK leaves the newer stance in effect. The diff lists new retractions even when the current stance stays the same.

This projection records attributed statements without deciding their truth. Portable speaker labels are unauthenticated. A response, revision, or reference to a question does not establish that it was resolved. Question acts and author-recorded open issues are shown separately. Omitted acts cannot supply evidence about earlier stances.

The terminal view starts with a Concept Index, then shows recorded state, recent questions, the full symbol catalog, and recent acts. A comparison requires the same grammar version, matching earlier definitions, domains, and claims, and an unchanged retained act prefix. It compares two validated records and does not authenticate their provenance. Retirement is attributed to a speaker and never removes a symbol from the catalog. It may shorten long prose and escapes nonprintable characters. The JSON view preserves the original strings. Both can be regenerated locally from the single Portable file.
