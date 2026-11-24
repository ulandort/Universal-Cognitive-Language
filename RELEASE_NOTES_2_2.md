# UCL 2.2.0 Portable

These notes document the historical 2.2.0 release. See the [2.4.1 release notes](RELEASE_NOTES_2_4_1.md) for the current release.

Long conversations can now retain older turns losslessly inside the same self-contained `.txt`. The guide, active records, and newest 1,000 acts stay readable, while optional gzip blocks carry older acts. Each packed file explains how to locate, decode, and verify a block without a server.

- **Exact lookup.** `inspect --act t37` retrieves an original act. `inspect --claim theory --path 1` retrieves a claim branch and its typed dependencies.
- **Concept Index.** See current vocabulary and attributed retirements. Compare packets with `inspect --since earlier.txt` to identify newly added definitions.
- **Protected history.** Packing keeps important sources readable. Use `pack --keep-act ACT_ID` to pin an additional turn.
- **Compatibility.** Released 2.0 and 2.1 packets remain readable and continuable. Explicit `upgrade` reissues them as 2.2.

## Try the attached files

Use the quickstart to practice a short continuation, the Challenge to introduce a concept, or the packed 2,000-act example to retrieve an archived turn.

```bash
python src/ucl.py inspect ucl-2.2-archive.txt --act t185
python src/ucl.py check ucl-2.2-archive.txt
node tools/check_ucl_portable.js ucl-2.2-archive.txt
```

An offline 100,000-act synthetic conversation fit inside a 4.02 MB packet. Python and Node accepted it and the continuation to act 100,001. The test used short, repetitive messages. Actual file size depends on the conversation.

The CLI caps stored Portable files at 8 MB and uses separate expansion limits. Targeted lookups open a single indexed block. Full checks and continuation reconstruct the complete transcript in memory. See the [2.2 specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.2.0/docs/UCL_2_2_SPECIFICATION.md).
