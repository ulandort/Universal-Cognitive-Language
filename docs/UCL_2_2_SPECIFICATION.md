# UCL/2.2 Portable specification

This document specifies Portable 2.2. See [Portable 2.3](UCL_2_3_SPECIFICATION.md) for the current release. The interchange is one self-contained UTF-8 JSON `.txt` file. The envelope identifies `UCL/2.2-SAP1-PORTABLE` and profile `portable`. The inner guide identifies `UCL/1.2`. The [2.1 specification](UCL_2_1_SPECIFICATION.md) supplies the unchanged definition ID algorithm, named aliases, vocabulary records, expression syntax, and authoring fields. The 11 core glyphs and the packet, rules, and envelope hash domains carry forward.

## Long histories and archives

An unpacked 2.2 packet supports up to 4,096 acts and up to 8,192 each of acknowledgements, claim bindings, and viewpoints. The optional `archive_guide` and `archive` fields appear together when older acts are packed. Their content is covered by the envelope checksum. The archive layout, protected-source policy, block framing, and lossless reconstruction are described in [Long conversations in one Portable file](UCL_LONG_CONVERSATIONS.md#optional-gzip-archives-in-the-same-file). The inner packet digest covers the exact expanded conversation. An archive may retain more than 4,096 acts when it fits the stored and expanded byte limits.

Read the embedded guide and current discussion first. An exact old act is recoverable from its indexed gzip block. The optional Python CLI is sufficient for local retrieval and continuation. The Node verifier independently checks canonical encoding and the reconstructed packet within its documented subset.

## Fingerprints

All values below are unpadded Base64url SHA-256.

| Object | Digest |
|---|---|
| Inner guide, canonical bytes | `SgHVVjXpgzfVdWLQPV-ku5DT2wzhZzK6seQcPBrjgHA` |
| Inner guide with `UCL-GUIDE-PIN-2` and LF | `OJq6wvk1iM4amrEhQsxzi-xBNt3tkRRL8NJEHnNTaIY` |
| Authoring rules with `UCL-SAP1-RULES-2.0` and LF | `LQQIye-mjF8wKYpLdvEwzRLHBfVxnzyBPzBnkqi5LZc` |
| Archive guide, raw UTF-8 string | `I5ii4bIUzldhadQm8YkY3MkPrn49NtCU5Lpw27O5HCc` |

## Compatibility and migration

The v2.2.0 checkout reads and continues earlier 2.0, 2.1, and the final 2.2 draft packets using their original format. Its `upgrade earlier.txt current.txt` command writes a separate stable 2.2 packet. The 2.3 checkout upgrades to Portable 2.3. Definition IDs from 2.1 and the final 2.2 draft carry forward. A 2.0 upgrade recalculates the original definition IDs and structured revision references. Use the original file to resolve references to its original hashes.
