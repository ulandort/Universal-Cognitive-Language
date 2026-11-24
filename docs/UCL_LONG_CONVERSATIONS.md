# Long conversations in one Portable file

A complete handoff remains one self-contained UTF-8 JSON `.txt` with the guide, authoring rules, and retained conversation. A recipient must be able to read retained acts and interpret their references from that file alone. Packet size, model input cost, and the maximum number of retained acts are separate limits.

## Where the bytes go

Measurements used canonical Portable JSON. The synthetic packet contains the published Challenge's eight acts plus 92 generated responses, each with repeated prose and turn-specific hypothetical observation identifiers. Each response refers to an existing act and uses a defined predicate. Python validated both packets. The gzip column measures file bytes only.

| Packet | Portable bytes | Acts array bytes | Guide and rules bytes | gzip bytes |
|---|---:|---:|---:|---:|
| Published 2.1 Challenge, 8 acts | 23,617 | 3,435 | 15,480 | 9,143 |
| Synthetic 2.1 long conversation, 100 acts | 107,523 | 87,339 | 15,480 | 36,487 |

The published [L50 run](../benchmarks/AUTONOMOUS_50_RESULTS.md) finished at 148,841 bytes with 91 retained acts. It used 2.0 and a different conversation. The 100-act fixture reached the 2.1 retained-act ceiling. Portable 2.2 supports up to 4,096 unpacked acts and larger packed histories within its byte limits.

At 100 synthetic acts, the acts account for about 81% of the bytes. Rearranging or shortening the one embedded guide would buy little room for that conversation. Compression saves bytes in transit. Whether gzip or Base64 saves bytes says little about how many tokens an AI needs to read the decoded text. A file made of opaque compressed history would require a decoder before a cold reader could inspect those acts.

## Focused reading and long histories

The local CLI can now retrieve an original act or a scoped claim from a validated file. A focused view prints its source packet digest, the exact source act, relevant typed definitions and domain declarations, and a bounded set of matching acknowledgements. Each acknowledgement names the act to look up for its verbatim wording. If more than 12 acknowledgements match, the view reports the total and prioritizes substantive stances over receipts and procedural records. If the selected group still exceeds 12, the view shows its earliest two and latest ten in act order. Direct references are preserved as IDs for further lookups. Continue and validate against the complete file.

```bash
python benchmarks/long_join.py --out long.txt
python src/ucl.py inspect long.txt --act t1000
python src/ucl.py inspect long.txt --claim theory --path 1
python src/ucl.py inspect long.txt --act t37
node tools/check_ucl_portable.js long.txt
```

The 2.2 release uses the same single-file Portable envelope and retains the existing definition IDs. Python and Node accept up to 4,096 retained acts and up to 8,192 each of acknowledgements, claim bindings, and viewpoints, subject to the 8 MB CLI input ceiling and the existing per-record limits. Released 2.0 and 2.1 keep their original limits and hashes. To migrate a released packet, run `python src/ucl.py upgrade incoming.txt current.txt` and continue the resulting file with this checkout.

The 1,000-act fixture is 420,889 bytes in canonical JSON. Looking up `theory` at path `[1]` returns a 2,771-byte canonical excerpt, including the typed condition from act `t37`. The test appends a reply as act 1,001 and preserves all previous acts and IDs. A 4,096-act run of the same fixture was 1,671,673 bytes and returned a 2,772-byte excerpt. Python and Node accepted both sizes. These are byte measurements for a synthetic fixture. Agents reading selected excerpts can avoid sending the whole record to the model. A chat user who pastes the whole file still pays the full input cost.

## Optional gzip archives in the same file

```bash
python src/ucl.py pack long.txt packed.txt --keep-act t500
python src/ucl.py inspect packed.txt --act t1850
python src/ucl.py inspect packed.txt --claim theory --path 1
python src/ucl.py check packed.txt
node tools/check_ucl_portable.js packed.txt
python src/ucl.py continue packed.txt next.txt < contribution.json
```

Packing is opt-in for Portable 2.2. At 2,000 turns the first 1,000 become eligible, then each older batch of 1,000 becomes eligible as the conversation grows. The newest 1,000 stay readable. A packet whose stored representation approaches 7 MB can also archive a smaller eligible batch. Batches split further when their expanded data would exceed 4 MB.

The tool leaves important turns verbatim in the readable portion. It protects the sources of bound claims and viewpoints, formula annotations, vocabulary records, substantive acknowledgements and their exact act targets, and direct references from the readable tail. Use repeatable `--keep-act` options to preserve additional turns that carry important prose or evidence. The CLI carries those pins into subsequent handoffs. A packed conversation continues to apply the archive policy as it grows.

### Read and decompress

The file starts with its usual format identifier, an `archive_guide`, the embedded authoring rules, and the readable packet. The archive index and compressed blocks follow. A cold reader can read the current discussion and learn how to retrieve an exact older turn without an external lookup service.

Find the requested act in `archive.blocks[].act_ids`. Its block's `data` is unpadded Base64url for a single gzip member with no optional gzip header fields. Decode Base64url (add padding if the decoder needs it), then decompress up to the declared `expanded_bytes`. Verify the exact byte count and the Base64url SHA-256 of the expanded bytes. The block is canonical UTF-8 JSON containing the ordered acts and acknowledgement records.

The `act_slots` array maps the archived acts to zero-based positions in the complete transcript. Insert the readable acts, in their stored order, into the remaining positions. Archived acknowledgements are pairs of their original zero-based index and the acknowledgement object. The readable acknowledgements use the corresponding positions in `archive.readable_ack_slots`. The inner digest remains the digest of the full reconstructed packet. Both validators verify it and the complete transcript on `check`. Selective `inspect --act` opens at most one compressed block and reports that a full audit was not performed.

The CLI still limits the stored file to 8 MB. The reader separately caps each expanded block at 4 MB and total expanded archive bytes at 96 MB per audit. Archived packets are not limited to 4,096 acts. Full `check` and `continue` currently reconstruct the complete transcript in memory. Use the packed file as the handoff. The expanded inner JSON from `decode` remains available for reading and auditing.

## 100,000-act stress test

The published 2.2 implementation packed 100,000 synthetic acts and 99,995 acknowledgements into 99 archive blocks. Python reconstructed and validated the packet. The offline continuation to act 100,001 preserved the original archive blocks, readable acts, and definition records. Node independently checked the continued packet.

```bash
python benchmarks/long_join.py --turns 100000 --pack --out long.txt
python src/ucl.py check long.txt
node tools/check_ucl_portable.js long.txt
python src/ucl.py inspect long.txt --act t1850
```

| Representation | Bytes |
|---|---:|
| Equivalent uncompressed Portable JSON | 40,776,915 |
| Single packed Portable `.txt`, including the guide, readable acts, and index | 4,018,702 |
| Storage reduction | 90.1% |

The uncompressed figure measures the reconstructed JSON before applying unpacked file limits. The fixture uses generated, short and repetitive acts. This measures storage and continuation on that record. File size on a live research conversation depends on the length and variety of its acts.

## Live archive continuation

Clarke received 1,012 bytes of labeled excerpts from a 575,525-byte packed 2.2 file. It quoted the observation from archived act 1,850 and used the typed qualification recorded in act 37. The local tool supplied the excerpts and assembled the contribution fields. Python and Node accepted act 4,097 and verified the prior acts, definitions, claims, and acknowledgements were preserved. Act 1,850 became readable in the new packet because the reply cited it. [Successful run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45442609497)

## Design explicit condensation for smaller handoffs

Use Portable's existing disclosed history concept for a bounded handoff when the sending participants decide that older wording can be left behind. Keep the path opt-in and require a complete, valid packet after every condensation. Before exposing an official command, agree on these rules:

1. Start from an explicit list of candidate acts and verify the whole source packet. Protect the current act, all retained claim origins and acknowledgement sources and targets, and the source acts of retained viewpoints, formula roles, and vocabulary records. Protect exact references and structured dependencies transitively. Preserve existing unresolved issues and references they rely on.
2. Preserve all definitions, domain declarations, immutable IDs, and retained acts verbatim. Preserve prior omission records. When a retained reference is ambiguous or its source would disappear, reject the proposed omission. Dense histories may yield no safe removals.
3. Record the exact omitted act IDs or ranges and the source packet digest, along with a human-reviewed explanation of what was lost. Keep any summary clearly attributed and distinguish it from quoted acts. A digest can verify a source supplied later, but a recipient cannot reconstruct omitted text from it.
4. Both Python and Node must agree on the resulting packet and every surviving exact claim target. Before shipping a command, test that the continued conversation can keep its unresolved disagreement, preserve the provenance of retained examples, and refuse to cite an omitted act as if its wording were present.

UCL already validates disclosed history, and its inner draft helper provides a starting point. An official Portable command needs version-aware validation and explicit handling of envelope annotations and retained vocabulary provenance before it is ready.

## Lossless options and limits

A future revision of the same format could store repeated structures once and refer to them by a readable local ID. Measure this on long, varied conversations first. The embedded guide already appears once per packet, and local references will save little on unique prose. A local model can reuse the same complete file without sending the whole history to its prompt at every turn.

Keeping every original act means the file must still grow as participants add unique information. A readable, smaller handoff comes from avoiding repetition or from explicitly deciding what verbatim material to leave out. Block archiving reduces stored bytes without losing old wording. Focused reading reduces what the model needs in its context. Disclosed condensation is a separate research design for when participants are willing to leave material behind.
