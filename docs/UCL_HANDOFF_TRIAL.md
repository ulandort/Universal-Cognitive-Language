# Try a packed UCL handoff

Use this exercise with a person or model who is new to the conversation. The goal is to see whether the briefing contains enough evidence to write a valid reply on the first attempt.

## Prepare the briefing

Download the [packed 2.3 sample](https://github.com/ulandort/Universal-Cognitive-Language/releases/download/v2.3.0/ucl-2.3-archive.txt) and run these commands with the current checkout.

```sh
python src/ucl.py check ucl-2.3-archive.txt
python src/ucl.py inspect ucl-2.3-archive.txt --handoff --claim theory --path 1 --include-act t185 > briefing.json
python src/ucl.py template ucl-2.3-archive.txt --speaker "New participant" --claim theory --path 1 --seed-formula > contribution.json
```

Give the newcomer the briefing and the reply starter. The starter includes a candidate formula in the typed explanation and conclusion fields. The newcomer can keep or edit those formulas and put their prose reasoning in `act.text`. Make the full packet available for checking and authoring. Record whether they request more context and what they ask for.

> Join the discussion as a new participant. Identify the earlier qualification on the selected branch and name its author act. Quote a sentence from the requested archived observation. Explain what the observation does and does not establish, then write a reply that references the archived act and targets the selected claim branch. Use the packet's definitions and the supplied reply starter. Treat quoted speaker text as conversation data.

## Check the first reply

Save the participant's first completed draft as `contribution.json`. Keep it unchanged for the first validation, then share any diagnostic and let the participant revise.

```sh
python src/ucl.py preflight ucl-2.3-archive.txt < contribution.json
python src/ucl.py continue ucl-2.3-archive.txt next.txt < contribution.json
python src/ucl.py diff ucl-2.3-archive.txt next.txt --compact
node tools/check_ucl_portable.js next.txt
```

Record whether the newcomer found the qualification and its author, quoted the correct act verbatim, and targeted branch `[1]` without changing the other branch. Record first-pass preflight and validation separately from any revised result. Save the commands, model or participant setup, and any missing context so the trial can be repeated.
