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

## Follow-up on the starter's stance

Hal replayed the two continuations where it had left the default `received` action. The evidence, history, and instructions stayed identical within each pair. Only the starter's action differed. Hal used the requested `withhold-judgment` in **1/2** replies with the usual starter and **2/2** replies with the requested action prefilled. All four quoted the exact source and passed both validators. The four calls cost an estimated **$0.141**. This is a two-case result for one model. [Run and prompts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45513921403)

## Follow-up with eight archive entries

Clarke and Hal each joined a synthetic 2,000-act conversation and could request two of eight archived acts. The question asked whether the original Delta-7 trial established the refined matched-control predicate. The index included a Delta-7 sign-off marked PASS under the older criterion and a successful matched comparison from a separate trial. Each reply starter had `withhold-judgment` prefilled on the requested branch.

| Check | Clarke | Hal |
| --- | --- | --- |
| Requested and quoted the primary trial log `t185` | Missed it. Quoted the older-criterion sign-off `t286` instead. | Pass |
| Quoted the chosen archived act exactly | Pass | Pass |
| Reported that the refined criterion was unestablished | Pass | Pass |
| Returned both immutable definition IDs | Pass | Pass |
| Used the requested stance on the intended branch | Pass | Pass |
| Passed Python and Node checks on the first draft | Pass | Pass |

Clarke requested the worksheet and the sign-off. It correctly explained that the sign-off covered the earlier criterion and that “matched” referred to instrument settings. Hal requested the primary run log and the later review checklist. The primary log explicitly states that the original trial had no matched shared-input comparison. The result separates finding the strongest source from correctly interpreting the records actually retrieved.

The four calls cost an estimated **$0.096**. This was one controlled scenario with two models. It does not isolate the effect of index size or stance prefilling.

[Run, prompts, and first drafts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45515108524) · [Fixture and scoring code](https://github.com/ulandort/Universal-Cognitive-Language/blob/db8a9e4bfcfef46ca6d7db049d5a8fa0b6788eec/benchmarks/archived_distractor_once.py)

## 2.5 candidate discovery from the unfocused briefing

Clarke and Hal joined the same synthetic, 2,000-act packed conversation. Each received the generated unfocused handoff and a plain-English objective. The objective supplied no claim ID, path, or act IDs. The briefing listed candidate branches and linked acts from the packet, opened zero archive blocks, and withheld the archived observation text. This tested discovery using those links.

| Check | Clarke | Hal |
| --- | --- | --- |
| Identified the intended branch, `theory` path `[1]` | Pass | Pass after removing the Markdown fence |
| Requested the primary archived observation `t18` | Missed it. Requested the claim origin and the eligibility rule. | Pass after removing the Markdown fence |
| Assessed the retrieved evidence | Reported the observation was missing. | Quoted `t18` exactly and correctly identified the missing independent-input comparison. |
| First continuation passed Python and Node | Validation rejected `act.details.stance: "withhold"`. The separate ACK remained `received`. | The raw-JSON harness rejected the Markdown fence. The original contribution inside it passed both validators and recorded `withhold-judgment` on the intended branch. |

Hal's first reply contained the correct branch and requested IDs inside a Markdown code fence. The follow-up replayed those choices after unwrapping the fence and then made its first continuation call. Both fences were counted as output-format failures. The continuation payload passed the packet-digest guard and cited `t18`. The follow-up used the model's original JSON fields.

The four calls cost an estimated **$0.0994**. This was one scenario with two models and a bounded set of suggested links. [Initial run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45551154654) · [Hal follow-up](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45551392974) · [Fixture and scoring code](https://github.com/ulandort/Universal-Cognitive-Language/blob/5aba20e1c13f35c7d4e596f0dfc89234c86f3674/benchmarks/cold_discovery_once.py)

### Retest with explicit stance field guidance

The retest used the same fixture and distinguished `act.details.stance` from the scoped `acknowledgements[0].action` in the continuation prompt. It also asked for a single unwrapped JSON object. Both models selected the intended branch and produced validating continuations with `withhold-judgment` on that branch. Neither model requested the primary observation `t18` in this rerun.

- Clarke requested `t37` and `t7`. Its draft used the correct stance fields and passed both validators, but treated a claim-analysis act as an observation.
- Hal's initial discovery call reached its output limit. A retry with a larger allowance returned raw JSON and requested `t37` and `t760`. The test harness initially omitted current-act references from its list of permitted requests, even though the briefing showed `t760`. The continuation used Hal's recorded selection after correcting the harness. Hal returned raw JSON, explicitly reported the observation missing, and passed both validators.

Five calls cost an estimated **$0.1973**, including the incomplete Hal discovery call. The results cover stance authoring on this case and leave source selection as a separate outcome. [Retest](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45551863222) · [Hal discovery retry](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45552116935) · [Hal continuation](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45552307815)

### Source map and missing-observation trial

The unfocused briefing identified the claim origin, the author of the scoped qualification, and the archived act referenced by that author. It opened zero archive blocks. Two versions of the same 2,000-act fixture used identical source links. In the present case, `t18` recorded completed runs. In the absent case, it described an outline without a completed run or result. The aim was to distinguish a retrieved observation that falls short from a missing observation.

| Case | Clarke | Hal |
| --- | --- | --- |
| Observation present | Requested `t18` on the first lookup, quoted it exactly, reported `not_established`, and produced a valid scoped reply. | Requested `t18` on the first lookup. Its answer reached the output limit. The replay quoted `t18` exactly and reported `not_established`, but the contribution failed because it put the stance in the wrong field. |
| Observation absent | Requested another lookup after the allowed follow-up. The final-response replay reported `source_missing` and produced a valid scoped reply. | Reported `source_missing` after one additional lookup. The initial contribution left `act.text` empty. The final-response replay reported the same status with a valid scoped reply. |

The replays used the original retrieved records and explicitly ended the lookup window. They required nonempty reasoning even when the observation was missing. Hal's observation-present replay also had a larger output allowance. Both models retrieved the primary observation on their first lookup when it existed. Both recognized the absent observation in the final-response replay. The trial uses one graph with two matching source layouts. It changes the briefing and author instructions together.

Thirteen calls cost an estimated **$0.4740**. [Initial run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45552985805) · [Final-response replay](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45553342362)

### Prefilled ACK replay

A single Hal call replayed the observation-present continuation. The evidence, instructions and output allowance matched the prior run. The only change was the starter's ACK action, from `received` to `withhold-judgment` using the new template option. Hal again quoted `t18` exactly and reported `not_established`. It changed the ACK to `reject` and used the invalid `act.details.stance` value `negative`. The prior reply also used `reject` and had the invalid response detail `against`. Preflight rejected both drafts. This replay shows that prefilling does not guarantee that a model preserves the chosen stance. It cost an estimated **$0.0628**. [Replay and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45554000164)

### Short scoped-decision replay

Hal received the same already-retrieved observation and qualification and returned one explicit ACK action, its reasoning and source references. The CLI assembled the response with `draft-reply --expect-ack-action withhold-judgment` and continued from the briefing's packet digest. On its first attempt Hal quoted `t18` exactly, reported `not_established`, and chose `withhold-judgment`. Python and Node validated the resulting packet and the diff showed exactly one new stance on `theory` path `[1]`. The test covered one scoped continuation with the sources already selected. The single call cost an estimated **$0.0249**. [Live replay and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45554727901)

### Cold join with qualifying evidence

Clarke joined a synthetic 2,000-act conversation from an unfocused briefing and a plain-English objective. The task supplied no claim ID, path, source ID, or expected ACK action. Clarke selected `orion-evidence` path `[1]`, requested the eligibility rule `t37` and archived run log `t18` on its first lookup, and quoted the run log exactly. It concluded that Orion met the independent-input criterion and chose `accept` on that branch. The result left the broader speculative claim untouched.

The first short decision passed `draft-reply`. Python and Node validated the continued packet, and the diff showed exactly one changed stance at the intended branch. The test covered one model and one controlled affirmative scenario. The two calls cost an estimated **$0.0171**. [Live run and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45555174869)
