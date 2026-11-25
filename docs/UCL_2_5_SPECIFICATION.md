# UCL 2.5 Portable

The current format identifier is `UCL/2.5-SAP1-PORTABLE`, with the embedded `UCL/1.5` guide. The complete conversation travels in a single UTF-8 JSON `.txt`. The [2.3 specification](UCL_2_3_SPECIFICATION.md) defines the inherited act, retraction, and acknowledgement semantics. Definition IDs, the four-layer body, and the [gzip archive layout](UCL_LONG_CONVERSATIONS.md#optional-gzip-archives-in-the-same-file) carry forward.

The current CLI release is [2.5.0](../RELEASE_NOTES_2_5.md). It uses the 2.5 packet format, with the fingerprints below.

## Version compatibility

The release version identifies the tools and downloads. The outer marker identifies the packet format, and `packet.guide.version` identifies the embedded language guide.

| Tool release series | Portable format | Inner guide |
| --- | --- | --- |
| 2.5.x | `UCL/2.5-SAP1-PORTABLE` | `UCL/1.5` |
| 2.4.x | `UCL/2.4-SAP1-PORTABLE` | `UCL/1.4` |
| 2.3.x | `UCL/2.3-SAP1-PORTABLE` | `UCL/1.3` |
| 2.2.x | `UCL/2.2-SAP1-PORTABLE` | `UCL/1.2` |
| 2.1.x | `UCL/2.1-SAP1-PORTABLE` | `UCL/1.1` |
| 2.0.x | `UCL/2.0-SAP1-PORTABLE` | `UCL/1.0` |

The 2.5.0 checker reads these formats and the matching legacy 2.2 draft envelope. Continuing a packet keeps its format. Use `upgrade` to reissue it in the current format.

## Embedded authoring example

The guide's `reply_authoring` example assumes that `A` is a defined value, `B` is a predicate accepting its sort, and `t1` is a retained act. It uses these fields within a contribution.

```json
{
  "explanation": "~[B][A]",
  "conclusion": "~[B][A]",
  "act": {
    "text": "The earlier observation is relevant to whether A has B.",
    "references": ["t1"]
  }
}
```

Use the actual packet's definitions when writing typed formulas. Write prose in `act.text` and cite turn IDs in `act.references`. The optional `template --seed-formula` copies the selected proposition into the two typed fields for editing. Use `preflight` and then `continue` to validate and assemble the complete packet.

The 2.5 guide also embeds a short example for `draft-reply`. Use it for a single acknowledgement on an existing proposition. The optional assembler accepts the exact claim and path, one chosen ACK action, reasoning, and retained act references. It emits a full contribution under the same act and ACK schema.

## Joining and upgrading

Use [the packed handoff exercise](UCL_HANDOFF_TRIAL.md) to try `inspect --handoff`, the reply starter, and `diff --compact`. These commands produce local views or drafts. The Portable file carries the full retained conversation.

Run `python src/ucl.py upgrade incoming.txt current.txt` to reissue older packets in the current format. For 2.3 and 2.4 inputs, the upgrade preserves definition IDs, acts, ACKs, retractions, and claim bindings. Packet and envelope hashes reflect the new pinned guide and rules.

## Reference validator behavior

- The Portable CLI accepts up to 8,000,000 bytes of stored JSON. The lower-level Python JSON reader defaults to 1,000,000 bytes unless its caller passes an explicit limit. Gzip archive blocks have their own expansion limits.
- The finite-model checker in the reference source uses one budget of 1,000,000 work units per validation across model table checks and both formulas. Work includes evaluated expression nodes and table lookups. Exhausting the budget rejects the check without reaching a model verdict. Decimal confidence strings in [0,1] are supported alongside the existing `null` and integer values 0 and 1.
- Quoted viewpoints support `denies` alongside `asserts`, `believes`, `reports`, and `questions`. The implemented proof rules produce `not-requested`, `verified`, `invalid-proof`, or `unsupported`. The guide also lists `inconsistent-premises` and `undetermined`, which the current proof rules do not derive.

## Fingerprints

| Reference | SHA-256, unpadded Base64url |
|---|---|
| Structural rules | `qxViiEonrg5zB4K3w_w03_tdBEbN3hegJuIBmBBWwZU` |
| Embedded inner guide | `gzHdeowljmb9MM2cyz4vEcG0QaqjydvNQDCcyhrH-vc` |
