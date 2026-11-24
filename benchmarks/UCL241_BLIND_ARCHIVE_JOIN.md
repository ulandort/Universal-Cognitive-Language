# UCL 2.4.1 blind archive joins

Clarke 1.0 and Hal 1.0 each joined three synthetic, 2,000-act packed conversations in fresh sessions. The initial briefing included Current State, the selected claim branch, and a four-entry archive index with act IDs and headings. It withheld all four candidate texts and did not identify which act to choose. Each reader could request up to two acts before answering.

| Case | Evidence in the archive |
| --- | --- |
| Decisive evidence | One completed trial records independent input variation and a persistent pattern. The baseline repeats the pattern under shared inputs. |
| Insufficient evidence | The execution log records repetition and leaves how inputs were assigned unspecified. A plan describes the intended control. |
| Refined meaning | The original experiment supports the earlier independent-input concept. The refined definition also requires a matched comparison absent from that experiment. Both definitions have separate immutable IDs. |

The second call supplied the unedited acts selected by the model and an opt-in seeded reply starter. The scorecard separately checks selection of the relevant act, exact source quotation, the reported evidence status, both definition IDs for the refinement, the scope and citation of the reply, and Python and Node validation of the first draft. The test uses brief headings to narrow discovery to four archived acts. It does not measure open-ended search through all 2,000 acts.

## Results

| Case | Model | Requested acts | Exact source and evidence status | Required scoped ACK action | First draft validated |
| --- | --- | --- | --- | --- | --- |
| Decisive evidence | Clarke | `t185`, `t286` | Pass | Pass | Pass |
| Decisive evidence | Hal | `t149`, `t185` | Pass | Pass | Pass |
| Insufficient evidence | Clarke | `t286`, `t149` | Pass | Pass | Pass |
| Insufficient evidence | Hal | `t286` | Pass | Left `received` | Pass |
| Refined meaning | Clarke | `t185`, `t690` | Pass | Pass | Pass |
| Refined meaning | Hal | `t185` | Pass | Left `received` | Pass |

All six readers selected the relevant act, quoted it exactly, cited it on the requested branch, and reported the expected evidence status. Both readers of the refined-meaning case returned both immutable IDs and explained which comparison the original evidence lacked. All six first drafts passed Python and Node validation. Four used the required `withhold-judgment` action. In the other two, Hal used `received`, so the packet recorded receipt without the requested stance. Those replies addressed the requested branch and preserved the earlier record.

The 12 calls cost an estimated **$0.238**. The controlled task measured source choice within a four-entry index, evidence assessment, and first-pass authoring. Structural validity and following the requested dialogue action were scored separately.

## Replay

The [replay bundle](../evidence/ucl241-blind-archive-replay.zip) contains Clarke's refinement run and the full six-session scorecard. It includes the starting packet, briefing, source index, exact selected acts, prompts, raw replies, and validated continuation. Extract it and use the 2.4.1 checkout to verify the handoff.

```sh
python src/ucl.py check starting.txt
python src/ucl.py check continued.txt
node tools/check_ucl_portable.js continued.txt
python src/ucl.py diff starting.txt continued.txt --compact
```

Bundle SHA-256 is `56382f7f3e85b44f1bd2602bd6b79ff780e847f76dbec9bffb06d44684367b08`.

[Live workflow and full artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45512747636) · [Fixture and scoring code](https://github.com/ulandort/Universal-Cognitive-Language/blob/4cfbff72befa245af9a88cd3008139af2df64c02/benchmarks/blind_archive_once.py)
