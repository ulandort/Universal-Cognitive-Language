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

## Focused reading and the long-history draft

The local CLI can now retrieve an original act or a scoped claim from a validated file. A focused view prints its source packet digest, the exact source act, relevant typed definitions and domain declarations, and a bounded set of matching acknowledgements. Each acknowledgement names the act to look up for its verbatim wording. If more than 12 acknowledgements match, the view reports the total and prioritizes substantive stances over receipts and procedural records. If the selected group still exceeds 12, the view shows its earliest two and latest ten in act order. Direct references are preserved as IDs for further lookups. Continue and validate against the complete file.

```bash
python benchmarks/long_join.py --out long.txt
python src/ucl.py inspect long.txt --act t1000
python src/ucl.py inspect long.txt --claim theory --path 1
python src/ucl.py inspect long.txt --act t37
node tools/check_ucl_portable.js long.txt
```

The unreleased 2.2 draft uses the same single-file Portable envelope and retains the existing definition IDs. Python and Node accept up to 4,096 retained acts and up to 8,192 each of acknowledgements, claim bindings, and viewpoints, subject to the 8 MB CLI input ceiling and the existing per-record limits. Released 2.0 and 2.1 keep their original limits and hashes. To try the draft with a released packet, run `python src/ucl.py upgrade incoming.txt experimental.txt --long-draft` and continue the resulting file with this checkout.

The 1,000-act fixture is 420,889 bytes in canonical JSON. Looking up `theory` at path `[1]` returns a 2,771-byte canonical excerpt, including the typed condition from act `t37`. The test appends a reply as act 1,001 and preserves all previous acts and IDs. A 4,096-act run of the same fixture was 1,671,673 bytes and returned a 2,772-byte excerpt. Python and Node accepted both sizes. These are byte measurements for a synthetic fixture. Agents reading selected excerpts can avoid sending the whole record to the model. A chat user who pastes the whole file still pays the full input cost.

## Design explicit condensation for smaller handoffs

Use Portable's existing disclosed history concept for a bounded handoff when the sending participants decide that older wording can be left behind. Keep the path opt-in and require a complete, valid packet after every condensation. Before exposing an official command, agree on these rules:

1. Start from an explicit list of candidate acts and verify the whole source packet. Protect the current act, all retained claim origins and acknowledgement sources and targets, and the source acts of retained viewpoints, formula roles, and vocabulary records. Protect exact references and structured dependencies transitively. Preserve existing unresolved issues and references they rely on.
2. Preserve all definitions, domain declarations, immutable IDs, and retained acts verbatim. Preserve prior omission records. When a retained reference is ambiguous or its source would disappear, reject the proposed omission. Dense histories may yield no safe removals.
3. Record the exact omitted act IDs or ranges and the source packet digest, along with a human-reviewed explanation of what was lost. Keep any summary clearly attributed and distinguish it from quoted acts. A digest can verify a source supplied later, but a recipient cannot reconstruct omitted text from it.
4. Both Python and Node must agree on the resulting packet and every surviving exact claim target. Before shipping a command, test that the continued conversation can keep its unresolved disagreement, preserve the provenance of retained examples, and refuse to cite an omitted act as if its wording were present.

UCL already validates disclosed history, and its inner draft helper provides a starting point. An official Portable command needs version-aware validation and explicit handling of envelope annotations and retained vocabulary provenance before it is ready.

## Lossless options and limits

A future revision of the same format could store repeated structures once and refer to them by a readable local ID. Measure this on long, varied conversations first. The embedded guide already appears once per packet, and local references will save little on unique prose. A local model can reuse the same complete file without sending the whole history to its prompt at every turn.

Keeping every original act means the file must still grow as participants add unique information. A readable, smaller handoff comes from avoiding repetition or from explicitly deciding what verbatim material to leave out. The larger draft limit, focused local reading, and disclosed condensation solve different parts of the problem.
