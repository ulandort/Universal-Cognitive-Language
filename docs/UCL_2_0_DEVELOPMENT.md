# UCL 2.0 development track (not yet a released specification)

UCL 1.0 remains the stable public specification on `main`. Features below are *experimental* on `develop/2.0`; they are not a new official wire standard and do not weaken or change the 11 core glyphs.

## Guide profiles

- **Portable (default):** complete guide, all active session definitions, full needed conversation history, acts and acknowledgements are in the message. No network or external tools required to interpret the rules.
- **Compact (retired experimental profile):** historical proof-of-concept only; not developed or included in new active cross-model benchmarks. Its code and offline conformance vectors remain for reproducibility. Previous token savings were modest once the full local guide context was counted. This is **not** a breaking deletion of an existing wire profile; a future revival would require demonstrated gains with a legitimately pre-cached guide.
- The current Python `tools/guide_profiles.py` represents a *prototype wrapper around a verified UCL/1.0 packet*, not final UCL/2.0 wire syntax. It preserves and reconstructs the entire original 1.0 packet exactly. Changing the 2.0 wire schema requires its own versioned specification and cross-language review.
- The experimental compact format carries its own wrapper checksum; a successful decode also validates the reconstructed original UCL 1.0 message and its original integrity record.

## Exact reference compression (LRC)

Optional research experiment **only**. Repeated identical subtrees can be locally referenced only when the complete envelope is smaller. No historical condensation, paraphrasing or information loss is permitted. The earlier 13-act sample showed LRC **increased** raw size, so it is not enabled here. The prototype lives in the downloadable prior experimental archive and is not a mandatory UCL/2.0 feature. Prefer ordinary lossless transport compression where effective.

## No loss of history

All tests and transport profiles preserve original acts, text, definitions, revisions, attribution and stance. No lossy summary is permitted in this 2.0 development track. Existing UCL/1.0 supports an explicitly disclosed condensed-history facility, but **this track does not use it**.

## Offline UCLBench

Run from repo root:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s benchmarks -p 'test_*.py' -v
python benchmarks/offline_suite.py --iterations 1000 --seed 2026 --out uclbench-results.json
```

The suite runs deterministic mutation tests (definition identity, corrupted packet hash, unknown act references), formatting-independent validation, pinned-guide checks, full portable/compact round trips, and preservation of every claim and acknowledgement. Results are machine-readable JSON and exit nonzero on failure. GitHub Actions runs these on branch and PR activity.

This **does not** test any LLM's comprehension, English-vs-UCL performance, authentication, or adversarial security. A future UCLBench live-model runner needs independent ground truth, published scoring methods and controlled API tests. Avoid presenting offline passes as AI model accuracy results.

## Conformance conditions before 2.0 release

1. Produce a complete normative 2.0 specification, with unambiguous wire format and explicit guide fingerprint derivation.
2. Test Python and independently written JavaScript reference implementations using shared canonical vectors.
3. Ensure portable cold-start reading without web access, and, only for any archival Compact compatibility checks, explicit fallback when a local guide is unavailable.
4. Require strict reconstruction of all active context and history, with no lossy condensation in 2.0.
5. Run UCLBench offline conformance suite and publish real outputs, then live English/structured-English/UCL comparative benchmarks.
6. Retain optional AES-256-GCM encrypted transport as a distinct experimental, unaudited feature.
## Active 2.0 AI dialogue research

New paid research prioritizes **UCL Portable, ordinary English, and structured English**, with generated multi-turn exchanges, self-declared private author intentions, independent recipient interpretation, exact claim/stance target scoring, validation and cost reporting. See [live autonomous relay](../benchmarks/LIVE_DIALOGUE.md). **No UCL superiority has been established**: an encoder provides explicit intent metadata to the structured variants and the English author's self-report still needs independent evaluation against actual prose.
