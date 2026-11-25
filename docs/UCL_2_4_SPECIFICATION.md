# UCL 2.4 Portable

See [Portable 2.5](UCL_2_5_SPECIFICATION.md) for the current release.

The archived 2.4 format identifier is `UCL/2.4-SAP1-PORTABLE`, with the embedded `UCL/1.4` guide. The complete conversation travels in a single UTF-8 JSON `.txt`. The [2.3 specification](UCL_2_3_SPECIFICATION.md) defines the inherited act, retraction, and acknowledgement semantics. Definition IDs, the four-layer body, and the [gzip archive layout](UCL_LONG_CONVERSATIONS.md#optional-gzip-archives-in-the-same-file) carry forward.

The final 2.4 CLI release was [2.4.1](../RELEASE_NOTES_2_4_1.md). It uses the 2.4 packet format, with the fingerprints below.

## Version compatibility

The release version identifies the tools and downloads. The outer marker identifies the packet format, and `packet.guide.version` identifies the embedded language guide.

| Tool release series | Portable format | Inner guide |
| --- | --- | --- |
| 2.4.x | `UCL/2.4-SAP1-PORTABLE` | `UCL/1.4` |
| 2.3.x | `UCL/2.3-SAP1-PORTABLE` | `UCL/1.3` |
| 2.2.x | `UCL/2.2-SAP1-PORTABLE` | `UCL/1.2` |
| 2.1.x | `UCL/2.1-SAP1-PORTABLE` | `UCL/1.1` |
| 2.0.x | `UCL/2.0-SAP1-PORTABLE` | `UCL/1.0` |

The 2.4.1 checker reads these formats and the matching legacy 2.2 draft envelope. Continuing a packet keeps its format. In the 2.4.1 checkout, `upgrade` reissues older packets in the 2.4 format.

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

## Joining and upgrading

Use [the packed handoff exercise](UCL_HANDOFF_TRIAL.md) to try `inspect --handoff`, the reply starter, and `diff --compact`. These commands produce local views or drafts. The Portable file carries the full retained conversation.

Run `python src/ucl.py upgrade incoming.txt current.txt` to reissue older packets in the current format. For a 2.3 input, the upgrade preserves definition IDs, acts, ACKs, retractions, and claim bindings. Packet and envelope hashes reflect the new pinned guide and rules.

## Fingerprints

| Reference | SHA-256, unpadded Base64url |
|---|---|
| Structural rules | `D6r9Rkm_kYFdqO4lofNhjLhP1p4GoVayXxsvA3XZrHk` |
| Embedded inner guide | `OgSiDiN3a2TSuQglgVOyXQaXLh246BltSnAhO4meHTI` |
