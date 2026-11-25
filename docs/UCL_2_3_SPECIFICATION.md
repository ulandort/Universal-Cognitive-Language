# UCL 2.3 Portable

See [Portable 2.4](UCL_2_4_SPECIFICATION.md) for the current release. This page documents the 2.3 wire and inherited retraction semantics.

The format identifier is `UCL/2.3-SAP1-PORTABLE` and the embedded grammar version is `UCL/1.3`. The [2.2 specification](UCL_2_2_SPECIFICATION.md) defines the inherited structure, gzip archive layout, and definition identities. Every packet carries its matching guide and authoring rules. Continuing an older packet keeps its original version. An explicit `upgrade` to 2.3 preserves 2.2 definition IDs, claims, acts, acknowledgements, and optional formula roles and recomputes the guide and packet hashes.

## Exact ACK retraction

Use the standard seven-field ACK shape.

```json
{
  "id": "x6",
  "by": "t10",
  "target": {"ack": "x5"},
  "action": "retract",
  "qualification": null,
  "replacement": null,
  "note": "I retract this stance."
}
```

- The target ACK must be retained and authored by an earlier act with the same speaker label. Speaker labels remain unauthenticated.
- The original action must be `accept`, `reject`, `qualify`, `adopt-for-discussion`, or `withhold-judgment`. Each such ACK can be retracted once. Retractions themselves are permanent records. A participant can take a new stance with a new ACK.
- Retraction keeps both records and their target claim. For `withdraw`, the new act’s speaker label must match the target’s origin act.
- Replay in act order, using the ACK array order within an act. If the original ACK is still the latest stance at its speaker and exact target, mark that stance retracted without restoring any older stance. If a newer stance already exists, preserve it. A later stance can supersede the retraction marker.
- Gzip packing keeps the original stance ACK, its source, and the retraction readable. No new archive fields are needed.

### Retract and take a new stance in one reply

Give each ACK a fresh ID. Use the same new act ID in both `by` fields. Put the retraction first, then use the exact claim ID and path for the new stance. For example, speaker D can retract the Challenge's `x4` and explicitly withhold judgment on that branch.

```json
[
  {"id":"x5","by":"t9","target":{"ack":"x4"},"action":"retract","qualification":null,"replacement":null,"note":""},
  {"id":"x6","by":"t9","target":{"claim":"theory","path":[1]},"action":"withhold-judgment","qualification":null,"replacement":null,"note":""}
]
```

Current State shows `x6` as the current stance. The recent retraction still links `x5` to `x4`. To leave the branch without a new stance, use just the first ACK.

## Fingerprints

| Reference | SHA-256, unpadded Base64url |
|---|---|
| Structural rules | `-ZE0iIhznPDfPkf21ncHm3plHzqarquH51NGnkw8McU` |
| Embedded inner guide | `qotxiYswBk-8n5ZpwaSj_42Q5irV-KW9tzMPlgdNbLw` |
