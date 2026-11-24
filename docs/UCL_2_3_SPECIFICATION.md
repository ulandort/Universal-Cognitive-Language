# UCL 2.3 Portable

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
- Retraction keeps both records and their target claim. `withdraw` still applies to the speaker's own claim.
- Replay in act order, using the ACK array order within an act. If the original ACK is still the latest stance at its speaker and exact target, mark that stance retracted without restoring any older stance. If a newer stance already exists, preserve it. A later stance can supersede the retraction marker.
- Gzip packing keeps the original stance ACK, its source, and the retraction readable. No new archive fields are needed.

## Fingerprints

| Reference | SHA-256, unpadded Base64url |
|---|---|
| Structural rules | `-ZE0iIhznPDfPkf21ncHm3plHzqarquH51NGnkw8McU` |
| Embedded inner guide | `qotxiYswBk-8n5ZpwaSj_42Q5irV-KW9tzMPlgdNbLw` |
