# UCL 2.3.0 Portable

These notes document the 2.3.0 release. See the [2.4.1 release notes](RELEASE_NOTES_2_4_1.md) for the current release.

UCL 2.3 lets a participant retract an exact earlier stance while keeping the original record and the rest of the discussion intact. The guide, definitions, and full retained history still travel in one self-contained `.txt`, including optional lossless gzip blocks.

- **Exact stance retraction.** Name the speaker's original acknowledgement by ID. If it was the current stance on that branch, Current State shows it as retracted. Newer stances survive and superseded stances stay historical.
- **Current State and diffs.** Use `inspect --state` for recent concepts, questions, issues, and precise stances. Use `diff` to see the changes between two validated packets. On packed files the state view reads visible records without inflating the archive.
- **Easier authoring.** Generate reply starters with `template`, including `--retract ACK_ID`. Use `preflight` to catch common errors before `continue` performs full validation.
- **Compatibility.** The CLI continues older Portable files in their original formats. Explicitly run `upgrade` to use 2.3 retraction rules on an earlier packet. The 2.2 definition IDs carry forward.

## Try the release downloads

Start with the two-turn quickstart, join the eight-turn Challenge, or look up act 185 in the packed example. The Challenge includes two alternative replies to its eighth turn. One introduces a new concept. The other retracts only the earlier stance recorded in `x4`.

```sh
python src/ucl.py preflight ucl-2.3-challenge.txt < ucl-2.3-challenge-retraction.json
python src/ucl.py continue ucl-2.3-challenge.txt next.txt < ucl-2.3-challenge-retraction.json
python src/ucl.py diff ucl-2.3-challenge.txt next.txt
python src/ucl.py inspect ucl-2.3-archive.txt --act t185
```

The release includes the completed retraction packet. Run `sha256sum -c SHA256SUMS.txt` in the directory containing the downloads to check their bytes.

In the live release test, Clarke used labeled excerpts from a synthetic packed conversation to produce act 4,097. It retracted the intended qualification on branch `[1]` while preserving acceptance of branch `[0]`. Python and Node validated the result and the earlier records remained intact. [Live test log](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45447764248)

[UCL 2.3 specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.3.0/docs/UCL_2_3_SPECIFICATION.md)
