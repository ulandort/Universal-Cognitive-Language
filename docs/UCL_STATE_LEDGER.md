# UCL state ledger

The ledger is a deterministic read view of a validated UCL/2.0 Portable packet. It can be printed by `python src/ucl.py inspect packet.txt` or produced as JSON by `python src/ucl.py inspect packet.txt --json`. Both commands validate the entire Portable packet first. The JSON is inspection output. Continue the conversation using the original Portable packet.

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
| `recent_acknowledgements` | Last ten acknowledgements in acknowledgement chronology, including procedural actions |
| `symbols` | Defined symbols in code point order, including definitions absent from recent expressions |

Each acknowledgement entry contains `speaker`, `by` (author act ID), `acknowledgement` (ACK ID), `action`, and the original `target`. It also contains the resolved `source_act`, `expression_index`, `path`, and `expression`, plus the original `qualification` and `replacement`. For a whole-act acknowledgement, `expression_index` and `expression` are null. The `expression` is the exact resolved subtree rendered in UCL syntax.

Each symbol entry contains `symbol`, `definition_id`, `kind`, `gloss`, `first_retained_expression_act` (an act ID or null), and the boolean `used_in_recent_acts`. Usage counts expressions directly listed in each act's `expressions` field. Recent usage covers the last five retained acts. First retained use does not establish when a symbol was introduced or whether it remains endorsed.

## Stance derivation

1. Read acknowledgements in the order of their author acts. Break ties within an act using their order in the packet's acknowledgement array.
2. Resolve each target to a retained source act, an expression index or null for a whole act, and a zero-based subtree path. A claim binding with an empty path and a direct reference to the same expression name the same target. Whole acts, whole expressions, and subtrees remain distinct.
3. For each pair of speaker label and resolved target, retain the last `accept`, `reject`, `qualify`, `adopt-for-discussion`, `withhold-judgment`, or `withdraw`. Receipt, understanding, clarification, revision proposals, and custom acknowledgement actions stay in the record without replacing such a stance.
4. Record every withdrawal separately. A withdrawal concerns its exact target and author. The ledger does not apply it to other speakers, related branches, or the content of the original act.

This projection records attributed statements without deciding their truth. Portable 2.0 speaker labels are unauthenticated. A response, revision, or reference to a question does not establish that it was resolved. Question acts and author-recorded open issues are shown separately. Omitted acts cannot supply evidence about earlier stances.

The terminal view puts the recorded state first, then shows recent questions, the vocabulary, and recent acts. It may shorten long prose and escapes nonprintable characters. The JSON view preserves the original strings. Both can be regenerated locally from the single Portable file.
