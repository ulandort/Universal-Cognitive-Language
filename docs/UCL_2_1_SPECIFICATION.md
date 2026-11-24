# UCL/2.1 Portable specification

UCL/2.1 is the current development revision of Portable. It uses the single self-contained UTF-8 JSON handoff described in the [2.0 specification](UCL_2_0_SPECIFICATION.md), with the identity and version changes below. The 11 core operators, four body layers, typed expressions, claim paths, and retained conversation model carry forward.

## Version markers

The envelope `format` is `UCL/2.1-SAP1-PORTABLE`, its `profile` is `portable`, and `packet.guide.version` is `UCL/1.1`. The pinned 2.1 authoring rules and inner guide are embedded in every file. A 2.1 validator requires these markers and their corresponding rules and guide to agree. Historical `UCL/2.0-SAP1-PORTABLE` envelopes use the original `UCL/1.0` guide and original definition IDs.

## Definition ID

Compute the ID with SHA-256 over ASCII `UCL-SEM-10`, one LF byte, and the UCL-CJSON-1 bytes of the payload below. Encode the full digest as unpadded base64url.

- For a domain, hash `{"definition": definition, "domain": {"mode": mode, "members": members}}`. For an open domain, members is null. For a finite domain, sort the unique member strings by Unicode scalar value before hashing. A change in mode or membership changes the domain ID.
- For any other definition, hash `{"definition": normalized_definition}`. Replace every `sort` and `returns` alias with its domain ID, and replace each entry of `args` with its domain ID, preserving argument order. Keep all other fields verbatim. Calculate domain IDs first. Domain definitions do not depend on other definitions.
- Keep the definition's original aliases in the wire object and in formulas. Only the hash payload substitutes domain IDs. The alias used as the definition map key does not enter the hash. Glosses enter the hash as authored text. The ID pins that description and the exact referenced types.

The packet hash still uses `UCL-PACKET-7` plus LF over the canonical packet with `integrity` removed. The rules and envelope checksums still use their 2.0 domains. The hashed envelope includes the format marker. A validator checks the marker against the matching embedded guide and rules.

The [quickstart packet](../examples/quickstart.txt) provides a reproducible example. Domain `D` has ID `xkW6osZLx9x59iCwGHZt6OZKTkPyhP8_5yQoZNc1kjw`. Predicate `P` keeps `"args":["D"]` on the wire and substitutes that ID in its hash payload. Its resulting ID is `vNk20qtiNpJ9tnP1T--03t__NCyFVKWQGISzY-ENM5E`.

## Guide and rules fingerprints

| Object | Unpadded base64url SHA-256 |
|---|---|
| Inner guide, canonical bytes | `MPlJIly50bq9GZiueX9SmlNNBvHXNg0ktOZQi08lUAU` |
| Inner guide, Node checker pin with `UCL-GUIDE-PIN-2` and LF | `gwOP2P5TdHQ7ZY92znMm80KFUnN6HJEKxUuyfCWdVKs` |
| SAP-1 rules with `UCL-SAP1-RULES-2.0` and LF | `JJC_P_4nhysFsB-1YOY-m3pWtJR8IBCloH06b4eOsE4` |

## Working with archived files

```bash
python src/ucl.py check archived.txt
python src/ucl.py upgrade archived.txt current.txt
python src/ucl.py check current.txt
```

Ordinary checking, decoding, inspection, and continuation use the packet's declared version. Fresh drafts without archived IDs built with the CLI use 2.1 identities. The explicit upgrade keeps the source file and writes a separate file. It recalculates definition IDs, the exact symbol declaration, structured revision ID fields, and checksums. It preserves alias bindings, authored prose, acts, acknowledgements, claims, domain declarations, and formula roles. An ID quoted in prose remains a quotation of the original archived ID. Keep the archived packet for verifying references to its original hashes.

Portable 2.1 retains single-character aliases and the existing catalog limit. Explicit retirement, multi-character aliases, and formal examples in the hashed definition schema are separate proposed changes.
