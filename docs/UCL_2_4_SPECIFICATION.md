# UCL 2.4 Portable

The current format identifier is `UCL/2.4-SAP1-PORTABLE`, with the embedded `UCL/1.4` guide. The complete conversation travels in a single UTF-8 JSON `.txt`. The [2.3 specification](UCL_2_3_SPECIFICATION.md) defines the inherited act, retraction, and acknowledgement semantics. Definition IDs, the four-layer body, and the [gzip archive layout](UCL_LONG_CONVERSATIONS.md#optional-gzip-archives-in-the-same-file) carry forward.

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
