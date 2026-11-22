# UCLBench: native UCL authorship research suite (experimental 2.0)

**This is the first intentionally native-authoring comparison; no paid experiments have been run automatically.** The stable UCL/1.0 specification on main is unchanged. UCL Compact is retired and is not part of this benchmark.

## Why the preceding results are not a proof of UCL superiority

The November 22, 2026, 6-turn × 2-trial assisted live dialogue completed **36 scheduled messages** for an estimated **$0.998079 USD**. English delivered **12/12** valid turns and **10/10** correct scored receipts; structured English delivered **12/12** and **10/10**; tool-assisted Portable UCL delivered **11/12** and **9/9**, with **two paid recovery requests**, one successful. Input usage was English **11,794**, structured English **12,525**, and UCL Portable **60,674** tokens; output usage was **33,343**, **32,604**, and **51,843**. All scored receipts were correct; there was **no UCL semantic advantage** demonstrated. Crucially, in that run the AI authored English prose and a separate tool created the formal UCL packet from a private intent. This tested assisted encoding rather than native symbolic authorship.

See [paid workflow 45064778784](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45064778784). Historical raw model responses remain in its GitHub Actions artifact.

## What the new suite actually tests

The new workflow performs **three separable protocols**, within ONE total manually chosen estimated cost guard ($5/$7.50/$10).

### A. Independent one-hop native-authoring versus controls (24 author/receiver pairs)

Four independent seeded stress challenges, with **two directions**, each using three arms:
- **Ordinary English:** model writes its original free English message without an intent metadata channel; receiver infers four facets.
- **Structured English:** model directly authors structured JSON with explicit action, target, sense of signal, and evidence label; no converter.
- **Native UCL semantic contribution:** model directly writes its OWN formal UCL expressions, discourse act, precise ACK action and target, and explanatory note. Python **does not convert English into UCL and does not change authored semantic fields**. Python only appends the contribution to the fully retained validated UCL history and computes canonical guide/packet hashes and the symbol declaration. Syntactically or semantically inconsistent native contributions are **rejected, not repaired**.

The four challenge families are (1) conceptual versus instrument *signal*; (2) simulated evidence versus empirical proof; (3) misleading claim-renaming without changing immutable definitions; (4) third-party false summaries that infer acceptance or proof from a narrower claim. Each recipient must answer the same four externally fixed fields: claim stance, exact claim target, sense of signal, and evidence classification. Both Clarke→Hal and Hal→Clarke run every case and format.

**Important validity caveat:** a sender can write an English message that doesn't convey the assigned task. We do not pretend a fixed answer key alone can identify whether the sender or receiver caused the mismatch. Every sender output is preserved for subsequent blind annotation. Structured English and UCL have explicit action/target values that are separately scored for *sender task compliance*. Scores include author-valid, author-task-compliant, receiver-correct, all-fields-correct and end-to-end, plus token counts and estimated cost. Structured English explicitly carries the signal/evidence fields, but UCL encodes only action and target structurally, leaving the nuanced concepts in its act notes. This is a **protocol-stack comparison, not equal-information identical prompts**.

### B. Strict, completely unassisted, complete UCL/1.0 packet authorship (2 requests)

Each model separately receives a verified historical baseline and is instructed to emit an **entire valid checksum-bearing UCL packet** including complete guide, original definitions, old acts, latest act, ACK, body used-symbol declarations and integrity hash. This arm calls \`ucl.check()\` directly on the model's RAW response. There is **no hashing tool, formatting repair, converter, or postprocessed answer**. A strict failure may reflect the difficulty of independently calculating SHA-256 and full canonicalization, not an inability to communicate or reason in UCL. Its score is shown separately; it is not used to penalize the main native semantic-contribution arm.

### C. Four-turn, bidirectional, directly UCL-authored dialogues (24 model turns)

In each of the same three formats, Clarke and Hal alternate four newly **model-authored** messages in both directions, with the second model independently interpreting the most recent message before authoring its reply. The native UCL model writes a new act with unique ID, typed glyph expression and ACK against an immutable claim. The tool only assembles/validates and hashes that *model-authored semantic contribution*. Receipts are compared with the immediately preceding task's four independently stipulated facets. Both the raw author response and raw handoff are retained. If a turn fails to produce a valid message, the next turn explicitly receives only the **last successfully delivered** message; missing turns are never fabricated or secretly rewritten.

The positions to communicate are **seeded** rather than freely selected: these are actual multi-turn cross-model authored messages, but **not completely autonomous theory negotiation**. This choice supplies pre-specified ground truth and makes cross-format error attribution more interpretable. The experiment is exploratory; a small sample of four scenarios, even in two directions, cannot establish general UCL superiority.

## Model and cost controls

- **Main model outputs:** up to **8,192 tokens per sender or recipient call**.
- **Strict full-packet outputs:** up to **16,384 tokens per model**.
- At defaults: **24 one-hop pairs = up to 48 API calls**, plus **2 strict native packet calls**, plus **24 multiturm dialogue author calls** = **up to 74 API calls**.
- One workflow has a single estimated guard, user-set at **USD $5, $7.50, or $10**. A first-stage budget reservation (~55% of selected cap) is allocated to one-hop/strict testing and the remaining unspent budget is available to multi-turn dialogue. No automatic retries; a failed case remains a failure. If a stage hits a cap, the results are retained and the run reports \`budget_stop\`.
- **Actual provider billing can differ**; retain the independent Radium provider-side account limit. If that provider limit is $10 total, it may need separate review before manually initiating a $10 *estimated* test. No key is ever stored in the benchmark artifact; GitHub Actions supplies \`RADIUM_API_KEY\` only to the paid job.
- The workflow never spends credits on pushes, tests or dry runs, and cannot turn itself on. Free dry-run oracles are deterministic **not measured model performance**.

## Running

[Manually launch UCLBench native authoring research](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-native-author.yml) on **main** (which checks out development code \`develop/2.0\`).

Recommended first **free run**: \`paid_run=no\`, \`cases=4\`, \`directions=2\`, \`strict_full_packet=yes\`, \`multi_turn=yes\`, \`cap_usd=10.00\`. After the free workflow passes, repeat with **paid_run=yes** and the same settings. The $10 estimate is a ceiling, **not the target amount the provider must charge**. Results are uploaded to \`uclbench-native-authoring-results\` with both complete \`native-live-results.json\` and summary \`native-live-summary.json\`; free \`native-dry-* \` artifacts are separate. Do not submit secrets or private content in generated prompts; transcripts are stored in GitHub artifacts.

Offline:
\`\`\`bash
python -m unittest discover -s benchmarks -p 'test_native_*.py' -v
python benchmarks/native_suite.py --dry-run --cases 4 --directions 2 --strict yes --multi-turn yes --output-prefix native-dry
\`\`\`

**Interpretation rule:** Compare native-formal author's raw compliance, format validity, correct cross-model interpretation, uninterrupted dialogue depth, and total input/output tokens/cost. Do not use the strict hash-computation task to assert that UCL as a semantic language fails. Likewise, a UCL acknowledgement that preserves action/target cannot establish a semantic advantage unless nuanced meaning that isn't explicitly encoded is also preserved better than English.
