# UCLBench: native UCL authorship research suite (experimental 2.0)

**The first native-authorship paid experiment completed on November 22, 2026. The revised benchmark below is a follow-up; no further paid run has been launched automatically.** The stable UCL/1.0 specification on main is unchanged. UCL Compact is retired and is not part of this benchmark.

## Why the preceding results are not a proof of UCL superiority

The November 22, 2026, 6-turn × 2-trial assisted live dialogue completed **36 scheduled messages** for an estimated **$0.998079 USD**. English delivered **12/12** valid turns and **10/10** correct scored receipts; structured English delivered **12/12** and **10/10**; tool-assisted Portable UCL delivered **11/12** and **9/9**, with **two paid recovery requests**, one successful. Input usage was English **11,794**, structured English **12,525**, and UCL Portable **60,674** tokens; output usage was **33,343**, **32,604**, and **51,843**. All scored receipts were correct; there was **no UCL semantic advantage** demonstrated. Crucially, in that run the AI authored English prose and a separate tool created the formal UCL packet from a private intent. This tested assisted encoding rather than native symbolic authorship.

See [paid workflow 45064778784](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45064778784). Historical raw model responses remain in its GitHub Actions artifact.

## First native-authorship paid baseline: November 22, 2026

The first paid [native workflow run 45066654527](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45066654527) completed **26 one-hop/strict challenges and 24 dialogue turns**, with **$1.990501 USD** estimated total cost. This is the empirical baseline for the syntax-and-output revision.

| Format | One-hop author-valid | One-hop receivers correct | Multi-turn valid messages | Multi-turn receipts scored |
|---|---:|---:|---:|---:|
| English | 8/8 | 4/8 | 2/8 | 0 |
| Structured English | 0/8 | 0 tested | 0/8 | 0 |
| Native UCL symbolic contributions | 0/8 | 0 tested | 0/8 | 0 |
| Strict full UCL packet | 0/2 | Not applicable | — | — |

**Failure analysis:** English receiver answers failed mostly on the claim target, with no demonstrated errors in the other scored facets. Structured English and UCL often produced invalid shape/value combinations rather than valid messages delivered to a receiving model. Several failed outputs hit the previous 8,192-token ceiling; strict full-packet tasks hit 16,384 tokens. **Neither semantic superiority nor semantic inferiority can be inferred from a receiver evaluation that never occurred.**

**Predeclared follow-up changes:** The revised primary native sender/receiver call budget is 16,384 tokens, while strict full-packet generation remains limited to 16,384 (the shared limit supported by both selected models). Prompts now give unambiguous *exact enum fields*, **integer** P/B claim paths, required ACK target object, matching UCL expression syntax, and original complete immutable UCL baseline in the native one-hop sender prompt. No model output is semantically fixed by the host. Repeat tests are exploratory and do not become independent task samples just because the prompting improved.

## Follow-up: formal expressivity without an artificial exact-formula rule

The earlier native-authoring benchmark required **every** act expression, explanation and conclusion to equal the bare positive proposition `~[P][A]` or `~[B][A]`. This was **an extra experimental restriction, not a UCL/1.0 rule**. It could incorrectly reject a model that wrote `![~[P][A]]` while rejecting P. The revised benchmark removes this check. **The unchanged real UCL validator remains mandatory**, including typing, orientation, epistemic provenance, immutable definitions, references, preserved history and integrity. We never repair invalid authored semantics after receipt.

Results now explicitly distinguish `output_token_exhaustion`, `invalid_json`, `author_schema_rejection` and `ucl_validator_rejection`, plus count validator-accepted model-generated expressions differing from the canonical positive atom. This enables a substantive audit of whether an authored expression is a justified inference or simply a valid but irrelevant formula. Grammar validity, stance compliance, recipient understanding and truth are not equivalent.

The native UCL main sender/receiver allowance remains **16,384** completion tokens per call; strict full-packet challenge remains 16,384. The prior paid results are frozen as the baseline. This follow-up still uses seeded targets and is an accuracy experiment, **not** a free-discovery benchmark.

## Exploratory paid-run failure and transport fix (November 22, 2026)

[Paid exploratory workflow 45069942179](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45069942179) stopped after **21/24 scheduled turns**, at an estimated **$0.722309 USD**, on `api_APITimeoutError` from the Hal 1.0 provider request. The timeout is **transport failure, not a token-exhaustion or UCL semantic verdict**. GitHub preserved all completed transcripts. English authorship was 8/8 valid with 0/6 receipts matching each prior speaker's private intent; structured English was 8/8 valid with 6/6 matching; native UCL was 0/4 delivered before the timeout (four schema rejections on the first direction because the model populated `receipt` even when no immediately prior relay message had successfully been delivered).

Revised follow-up: UCL's prompt now explicitly says the original reference packet's historical acts do **not** count as a prior *generated relay* message; `receipt=null` is required until the first native UCL handoff is successfully delivered. Provider timeout per-request is 240 seconds (previously 120), and a timeout is logged as an undelivered turn **without aborting the remaining experiments** or inventing any recipient message. Timed-out requests may still be billable by Radium, so the report records that provider charges are unknown. No auto-retry is introduced. This change corrects test infrastructure; it does not silently fix a model's failed UCL authoring or guarantee future validity.

## Separate free-choice hypothesis exploration

A distinct [exploratory native conversation workflow](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-native-exploration.yml) and [runner](native_exploration.py) let models choose their own P/B target, position, hypothetical example, UCL composition and theoretical inference across four turns in both directions. The comparison arms remain original English, structured English and **directly authored UCL**; no semantic English-to-UCL converter is used. Models can explore negations, conjectures, counterexamples, distinctions between conceptual and measured convergence, and other implications consistent with the existing UCL definitions. They cannot rewrite P or B or claim empirical proof. A receiver reconstructs the prior sender's *privately self-declared* intent without having seen that intent.

This mode is deliberately **not judged by a predetermined answer key**. The summary measures delivered-message validity, structured self-report agreement, cross-model interpretation accuracy against private self-report, output cost and completion problems. Novel, unexpected or apparently efficient inferences are preserved as full transcripts for blinded qualitative review, **not promoted to facts or proofs**. Whether UCL yielded more surprising insights than English cannot be automatically determined from the metadata alone. Strict formal syntax validity still does not establish the truth or originality of a hypothesis. All real API calls require separate manual paid authorization and a separately selected estimated $2/$4/$5 cap; start with the free dry-run.

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

- **Main model outputs:** up to **16,384 tokens per sender or recipient call**, increased from 8,192 to test whether models exhausted their reasoning/completion budget.
- **Strict full-packet outputs:** up to **16,384 tokens per model**.
- At defaults: **24 one-hop pairs = up to 48 API calls**, plus **2 strict native packet calls**, plus **24 multiturm dialogue author calls** = **up to 74 API calls**.
- One workflow has a single estimated guard, user-set at **USD $5, $7.50, or $10**. A first-stage budget reservation (~55% of selected cap) is allocated to one-hop/strict testing and the remaining unspent budget is available to multi-turn dialogue. No automatic retries; a failed case remains a failure. If a stage hits a cap, the results are retained and the run reports \`budget_stop\`.
- **Actual provider billing can differ**; retain the independent Radium provider-side account limit. If that provider limit is $10 total, it may need separate review before manually initiating a $10 *estimated* test. No key is ever stored in the benchmark artifact; GitHub Actions supplies \`RADIUM_API_KEY\` only to the paid job.
- The workflow never spends credits on pushes, tests or dry runs, and cannot turn itself on. Free dry-run oracles are deterministic **not measured model performance**.

## UCL-only native conversation feasibility workflow

The separate [UCL-only native AI conversation](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-ucl-only.yml) deliberately removes **every English/structured-English comparison arm**. The only delivered messages between Clarke 1.0 and Hal 1.0 are complete, portable **UCL/1.0 packets** validated against the unchanged `ucl.check()` implementation. Each model authors its OWN UCL semantic contribution, glyph expression, discourse act and precise ACK reference; the host mechanically appends the original self-contained history and calculates hashes, never translates an English answer or repairs an invalid act. Natural-language instructions and optional explanatory act notes are still used; this is a native-UCL exchange feasibility test, not a claim that the models' hidden reasoning is in UCL.

Defaults: **eight UCL-only turns**, Clarke starting, optionally reverse starting order too; estimated $4 software spending guard (user may select $2/$5/$10); output ceiling **16,384 tokens per request**. Results include attempted and validated packets, the longest uninterrupted sequence of valid packets, precise sender/receiver intent alignment, partial/undelivered turns, transport failures, and raw input/output transcript. Failures are preserved rather than invented away. Existing initial history records do NOT count as delivered generated turns. A provider timeout may still be billed even when output is not returned. The free dry-run validates relay mechanics but is NOT real communication evidence.

For testing whether two models **can sustain an actual UCL dialogue at all**, run this UCL-only workflow before comparing it statistically against English.

## Running

[Manually launch UCLBench native authoring research](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-native-author.yml) on **main** (which checks out development code \`develop/2.0\`).

Recommended first **free run**: \`paid_run=no\`, \`cases=4\`, \`directions=2\`, \`strict_full_packet=yes\`, \`multi_turn=yes\`, \`cap_usd=10.00\`. After the free workflow passes, repeat with **paid_run=yes** and the same settings. The $10 estimate is a ceiling, **not the target amount the provider must charge**. Results are uploaded to \`uclbench-native-authoring-results\` with both complete \`native-live-results.json\` and summary \`native-live-summary.json\`; free \`native-dry-* \` artifacts are separate. Do not submit secrets or private content in generated prompts; transcripts are stored in GitHub artifacts.

Offline:
\`\`\`bash
python -m unittest discover -s benchmarks -p 'test_native_*.py' -v
python benchmarks/native_suite.py --dry-run --cases 4 --directions 2 --strict yes --multi-turn yes --output-prefix native-dry
\`\`\`

**Interpretation rule:** Compare native-formal author's raw compliance, format validity, correct cross-model interpretation, uninterrupted dialogue depth, and total input/output tokens/cost. Do not use the strict hash-computation task to assert that UCL as a semantic language fails. Likewise, a UCL acknowledgement that preserves action/target cannot establish a semantic advantage unless nuanced meaning that isn't explicitly encoded is also preserved better than English.
