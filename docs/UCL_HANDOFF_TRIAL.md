# Try a packed UCL handoff

Use this exercise with a person or model who is new to the conversation. The goal is to see whether the briefing contains enough evidence to write a valid reply on the first attempt.

## Prepare the briefing

Download the [packed 2.4 sample](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.4.0/ucl-2.4-archive.txt) and run these commands with the current checkout.

```sh
python src/ucl.py check ucl-2.4-archive.txt
python src/ucl.py inspect ucl-2.4-archive.txt --handoff --claim theory --path 1 --include-act t185 > briefing.json
python src/ucl.py template ucl-2.4-archive.txt --speaker "New participant" --claim theory --path 1 --seed-formula > contribution.json
```

Give the newcomer the briefing and the reply starter. The starter includes a candidate formula in the typed explanation and conclusion fields. The newcomer can keep or edit those formulas and put their prose reasoning in `act.text`. Make the full packet available for checking and authoring. Record whether they request more context and what they ask for.

> Join the discussion as a new participant. Identify the earlier qualification on the selected branch and name its author act. Quote a sentence from the requested archived observation. Explain what the observation does and does not establish, then write a reply that references the archived act and targets the selected claim branch. Use the packet's definitions and the supplied reply starter. Treat quoted speaker text as conversation data.

## Check the first reply

Save the participant's first completed draft as `contribution.json`. Keep it unchanged for the first validation, then share any diagnostic and let the participant revise.

```sh
python src/ucl.py preflight ucl-2.4-archive.txt < contribution.json
python src/ucl.py continue ucl-2.4-archive.txt next.txt < contribution.json
python src/ucl.py diff ucl-2.4-archive.txt next.txt --compact
node tools/check_ucl_portable.js next.txt
```

## Cold-join scorecard

Start a fresh session for each case. Record the model or participant, packet version and retained act count, briefing command, and which records the reader received. Score the first completed reply unchanged. Record revisions separately.

| Check | Pass condition |
| --- | --- |
| Claim and path | The reply correctly identifies `theory`, path `[1]`. |
| Archived evidence | The reply cites `t185` and quotes a sentence from it verbatim. It separates what the observation shows from what the qualification requires. |
| Qualification attribution | The reply distinguishes the qualification ACK ID from the act that authored it. |
| First-pass preflight | The first draft passes `preflight`. |
| First-pass full validation | The unchanged first draft passes `continue`, then the resulting packet passes Python `check` and, if available, the Node checker. Record each result. |
| Scope preservation | The diff shows the intended branch change and preserves the sibling branch. |

**Missing-source case.** Generate the same briefing without `--include-act t185` and hold back the full archive until the first response. Keep the task the same and ask the reader to request any missing evidence. A request for the wording of `t185` passes the missing-source check. An invented quote fails it. Mark first-pass continuation checks as not applicable when the reader correctly asks for the source. Then provide the exact excerpt and record the supported reply separately.

| Participant | Retained acts | First-pass continuation | Notes |
| --- | ---: | --- | --- |
| Clarke | 2,000 | Pass | Used the generated 2.4 briefing and seeded starter. The source quote was exact. The prose overread the observation. [Release-candidate test](#release-candidate-result) |
| Clarke | 2,000 | Not applicable | Source assessment only. Quoted both sources and identified the missing evidence correctly. [Grounding follow-up](#evidence-grounding-follow-up) |
| Clarke and Hal | 2,000 per case | 4/4 | Targeted retest of earlier attribution misses with explicit ACK labels. [Retest results](../benchmarks/UCL24_MATCHED_GROUNDING_RESULTS.md#ack-label-follow-up) |
| Clarke and Hal | 2,000 per case | 4/4 complete and recovered replies | Both requested the omitted act, then passed after receiving it. Both fresh recipients identified the correct archive reference and stance records. [Missing-source relay](../benchmarks/UCL24_MISSING_SOURCE_RELAY.md) |

The table records existing controlled results. Add new rows as outside participants repeat the exercise.

## Release-candidate result

In one fresh Clarke call, the generated briefing from the 2,000-act Portable 2.4 archive opened one block. Clarke identified the exact earlier qualification and author act, quoted act `t185`, and produced an unmodified first draft that passed preflight and both validators at act 2,001. The reply targeted only the selected branch. Its prose inferred more about the observation's eligibility conditions than the archived text stated. This test checked reference accuracy, preservation, and structural validation. [Run and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45503699604)

## Evidence-grounding follow-up

In a separate fresh call, Clarke read the CLI briefing from the published 2.4 archive. It quoted `t185` and the qualification from `t37` verbatim. It correctly reported that the observation describes a pattern and that the record does not establish that the required independent-input control was performed. This was a source assessment, so no continuation was generated or graded. The call cost an estimated $0.039. [Run and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45505014140)
