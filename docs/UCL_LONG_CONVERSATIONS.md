# Long conversations in one Portable file

A complete handoff remains one self-contained UTF-8 JSON `.txt` with the guide, authoring rules, and retained conversation. A recipient must be able to read retained acts and interpret their references from that file alone. Packet size, model input cost, and the maximum number of retained acts are separate limits.

## Where the bytes go

Measurements used canonical Portable JSON. The synthetic packet contains the published Challenge's eight acts plus 92 generated responses, each with repeated prose and turn-specific hypothetical observation identifiers. Each response refers to an existing act and uses a defined predicate. Python validated both packets. The gzip column measures file bytes only.

| Packet | Portable bytes | Acts array bytes | Guide and rules bytes | gzip bytes |
|---|---:|---:|---:|---:|
| Published 2.1 Challenge, 8 acts | 23,617 | 3,435 | 15,480 | 9,143 |
| Synthetic 2.1 long conversation, 100 acts | 107,523 | 87,339 | 15,480 | 36,487 |

The published [L50 run](../benchmarks/AUTONOMOUS_50_RESULTS.md) finished at 148,841 bytes with 91 retained acts. It used 2.0 and a different conversation. The 100-act synthetic packet reaches today's retained-act ceiling, even though its bytes fit inside the CLI's file limit. That ceiling requires its own review before supporting substantially more retained acts.

At 100 synthetic acts, the acts account for about 81% of the bytes. Rearranging or shortening the one embedded guide would buy little room for that conversation. Compression saves bytes in transit. Whether gzip or Base64 saves bytes says little about how many tokens an AI needs to read the decoded text. A file made of opaque compressed history would require a decoder before a cold reader could inspect those acts.

## First build a focused local view

Keep one complete Portable file as the handoff. Let a local agent read a selected act or claim and its exact source, the recent relevant acts, and the definitions those acts use. Include the dependency closure of the relevant expressions and the scoped stance records. Mark selected excerpts and the source packet digest. Allow lookup of any omitted-from-view act by its ID using the same local file.

A local view is an input to an agent working with the full file. Continue and validate against the complete file. No new wire field or format is needed. This approach reduces model input for agents with local file access. Someone pasting the entire file into chat still pays the model's full input cost.

## Design explicit condensation for smaller handoffs

Use Portable's existing disclosed history concept for a bounded handoff when the sending participants decide that older wording can be left behind. Keep the path opt-in and require a complete, valid packet after every condensation. Before exposing an official command, agree on these rules:

1. Start from an explicit list of candidate acts and verify the whole source packet. Protect the current act, all retained claim origins and acknowledgement sources and targets, and the source acts of retained viewpoints, formula roles, and vocabulary records. Protect exact references and structured dependencies transitively. Preserve existing unresolved issues and references they rely on.
2. Preserve all definitions, domain declarations, immutable IDs, and retained acts verbatim. Preserve prior omission records. When a retained reference is ambiguous or its source would disappear, reject the proposed omission. Dense histories may yield no safe removals.
3. Record the exact omitted act IDs or ranges and the source packet digest, along with a human-reviewed explanation of what was lost. Keep any summary clearly attributed and distinguish it from quoted acts. A digest can verify a source supplied later, but a recipient cannot reconstruct omitted text from it.
4. Both Python and Node must agree on the resulting packet and every surviving exact claim target. Before shipping a command, test that the continued conversation can keep its unresolved disagreement, preserve the provenance of retained examples, and refuse to cite an omitted act as if its wording were present.

UCL already validates disclosed history, and its inner draft helper provides a starting point. An official Portable command needs version-aware validation and explicit handling of envelope annotations and retained vocabulary provenance before it is ready.

## Lossless options and limits

A future revision of the same format could store repeated structures once and refer to them by a readable local ID. Measure this on long, varied conversations first. The embedded guide already appears once per packet, and local references will save little on unique prose. A local model can reuse the same complete file without sending the whole history to its prompt at every turn.

Keeping every original act means the file must still grow as participants add unique information. A readable, smaller handoff comes from avoiding repetition or from explicitly deciding what verbatim material to leave out. Raising the 100-act limit, focused local reading, and disclosed condensation solve different parts of the problem.
