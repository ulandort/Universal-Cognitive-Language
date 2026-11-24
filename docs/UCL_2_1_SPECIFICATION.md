# UCL/2.1 Portable specification

This is the archived UCL/2.1 specification. See [UCL/2.4](UCL_2_4_SPECIFICATION.md) for the current release. It uses the single self-contained UTF-8 JSON handoff described in the [2.0 specification](UCL_2_0_SPECIFICATION.md), with the vocabulary, identity, and version changes below. The 11 core operators, four body layers, typed expressions, claim paths, and retained conversation model carry forward.

## Version markers

The envelope `format` is `UCL/2.1-SAP1-PORTABLE`, its `profile` is `portable`, and `packet.guide.version` is `UCL/1.1`. The pinned 2.1 authoring rules and inner guide are embedded in every file. A 2.1 validator requires these markers and their corresponding rules and guide to agree. Historical `UCL/2.0-SAP1-PORTABLE` envelopes use the original `UCL/1.0` guide and original definition IDs.

## Named aliases

The catalog accepts up to 512 definitions. In addition to the existing single-character aliases, a named alias starts with `$`, followed by an ASCII letter and up to 63 ASCII letters, digits, or underscores. In an expression such as `~[$background_sync][A]`, consume the whole alias as one symbol. A lone `$` can still be a single-character alias. Alias names are case-sensitive and local to the packet. Read their types and meanings from the embedded definitions.

The exact declaration layer uses the same space-separated `alias:id` entries, sorted as complete entries. A continuation may introduce a new alias and definition while preserving all earlier alias bindings.

## Vocabulary records

An act may add a `vocabulary` array of 1 to 16 records. The parent act supplies the recorded attribution and carries any explanatory text.

- `{"action":"retire","definition":"$background_sync","successor":"$opt_in_sync"}` records the speaker's retirement of the definition for their own use. Both aliases must exist and differ. Set `successor` to null if none is suggested. The original definition, ID, and all earlier expressions remain available. Other speakers can still use it.
- `{"action":"counterexample","definition":"$background_sync","expression_index":0}` labels that act's indexed expression as a counterexample. Use `example` for an example. The index is a zero-based integer, and the chosen expression must use the named definition. The label communicates the speaker's interpretation.
- A single act may retire a given alias at most once and may label a given expression at most once per definition. Include the definition alias and any successor alias in the exact declaration layer. The records participate in the packet checksum and preserve the definition IDs.

See the [worked contribution](../examples/challenge_reply.json) for an attributed counterexample. `inspect` shows the recent vocabulary records, and the [JSON ledger](UCL_STATE_LEDGER.md) includes all retained records with their definition IDs.

## Definition ID

Compute the ID with SHA-256 over ASCII `UCL-SEM-10`, one LF byte, and the UCL-CJSON-1 bytes of the payload below. Encode the full digest as unpadded base64url.

- For a domain, hash `{"definition": definition, "domain": {"mode": mode, "members": members}}`. For an open domain, members is null. For a finite domain, sort the unique member strings by Unicode scalar value before hashing. A change in mode or membership changes the domain ID.
- For any other definition, hash `{"definition": normalized_definition}`. Replace every `sort` and `returns` alias with its domain ID, and replace each entry of `args` with its domain ID, preserving argument order. Keep all other fields verbatim. Calculate domain IDs first. Domain definitions do not depend on other definitions.
- Keep the definition's original aliases in the wire object and in formulas. Only the hash payload substitutes domain IDs. The alias used as the definition map key does not enter the hash. Glosses enter the hash as authored text. The ID pins that description and the exact referenced types.

The packet hash still uses `UCL-PACKET-7` plus LF over the canonical packet with `integrity` removed. The rules and envelope checksums still use their 2.0 domains. The hashed envelope includes the format marker. A validator checks the marker against the matching embedded guide and rules.

The [quickstart packet](../examples/quickstart.txt) provides a reproducible example. Domain `D` has ID `xkW6osZLx9x59iCwGHZt6OZKTkPyhP8_5yQoZNc1kjw`. Predicate `P` keeps `"args":["D"]` on the wire and substitutes that ID in its hash payload. Its resulting ID is `vNk20qtiNpJ9tnP1T--03t__NCyFVKWQGISzY-ENM5E`.

## Embedded reply template

Every 2.1 packet carries `structural_rules.rules.reply_template`. Its example contribution shows a named predicate, an attributed example, an optional retirement with successor, and a scoped qualification. Sample IDs, aliases, expressions, references, and prose are placeholders to replace using the active conversation. Authors can omit vocabulary records and new definitions when their reply does not need them. The author returns the contribution object and the local `continue` command assembles the next complete packet.

## Guide and rules fingerprints

| Object | Unpadded base64url SHA-256 |
|---|---|
| Inner guide, canonical bytes | `yT1x1BpqfS9bbv55O7hrG6VVpNYA3YCxX4Cxmn7-R3A` |
| Inner guide, Node checker pin with `UCL-GUIDE-PIN-2` and LF | `y9nzzEGsMLesvWT5qAyaugxXnlMCXHtuj3PweHvYFkc` |
| SAP-1 rules with `UCL-SAP1-RULES-2.0` and LF | `IwfCnyR6owRSz6XBEGi1er4u_4Zksy1DrlgyiB7XvmI` |

## Working with archived files

```bash
python src/ucl.py check archived.txt
python src/ucl.py upgrade archived.txt current.txt
python src/ucl.py check current.txt
```

Ordinary checking, decoding, inspection, and continuation use the packet's declared version. Fresh drafts without archived IDs built with the CLI use 2.1 identities. The explicit upgrade keeps the source file and writes a separate file. It recalculates definition IDs, the exact symbol declaration, structured revision ID fields, and checksums. It preserves alias bindings, authored prose, acts, acknowledgements, claims, domain declarations, and formula roles. An ID quoted in prose remains a quotation of the original archived ID. Keep the archived packet for verifying references to its original hashes.

Earlier development snapshots of 2.1 used different pinned guide and rules text. Use the matching development checkout to verify those snapshots. Archived 2.0 files retain their original pins.
