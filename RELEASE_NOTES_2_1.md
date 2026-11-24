# UCL/2.1 Portable

UCL 2.1 expands the vocabulary that participants can build and use together. Each handoff is one self-contained UTF-8 JSON `.txt` file, with the guide, authoring template, definitions, and retained conversation embedded. The 11 core operators and four-layer body carry forward.

- **Named aliases and a larger catalog.** Use terms like `$background_sync` alongside single-character aliases. A packet can define up to 512 symbols.
- **Dependency-aware definition IDs.** A predicate's ID binds the domain definitions it depends on. Different domains yield different dependent IDs, even when their local alias is the same.
- **Vocabulary history.** Record examples, counterexamples, and speaker-scoped retirement with an optional successor. The original definition and earlier expressions remain available.
- **Local continuation and inspection.** `continue` assembles a validated handoff from an authored JSON contribution. `inspect` shows the recorded stance for each speaker and exact claim branch. Add `--json` to get the derived ledger.

## Try it

Start with the attached `ucl-2.1-quickstart.txt` or `ucl-2.1-challenge.txt`. Paste a complete packet into an AI chat and ask for a contribution using its embedded reply template. From a checkout with Python 3.12 or later, run the Challenge offline:

```bash
python src/ucl.py inspect examples/challenge.txt
python src/ucl.py continue examples/challenge.txt next.txt < examples/challenge_reply.json
python src/ucl.py check next.txt
```

## Compatibility and verification

The current wire identifier is `UCL/2.1-SAP1-PORTABLE`. The CLI validates and continues released 2.0 files using their original IDs. To reissue an archived packet under 2.1, use `python src/ucl.py upgrade archived.txt current.txt`. Keep the archived file for references to its original hashes. Earlier 2.1 development snapshots use the pins from their corresponding checkouts.

Python is the reference validator. The independent Node checker covers a subset. A live Hal continuation used the embedded template and produced a packet that passed both checkers, with all prior acts and definition IDs retained. See the [live smoke test](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45346075965) and [wire specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.1.0/docs/UCL_2_1_SPECIFICATION.md).
