# L50 — live autonomous 50-turn UCL endurance result

**Live result (2026-11-22, Toronto; GitHub run completed 2026-11-23 UTC):** [UCLBench 50-turn run 45083740106](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45083740106). The workflow completed successfully, and **48 of 50 scheduled independently model-authored turns** were validated and delivered. This is not a claim that all 50 turns succeeded.

## What the experiment demonstrated

- **48/50 delivered (96%)**, including **45/50 accepted on the first attempt (90%)**, plus three corrected and delivered after explicit model-authored retries. A total of **57 provider requests** were made at an estimated **$5.371941 USD**.
- **Full authentic continuity:** starts at the exact original **43-act final packet from L25** (whose lineage includes CG-1 and RR-1), and finishes with **91 validated, retained discourse acts**. The six independently invented C/E/G/K/M/N predicate definitions retained their original SHA-256 definition identities. No silent history condensation or rewrites of delivered historical acts were accepted by the validator.
- **Packet growth:** the first successfully delivered portable packet was **74,916 bytes** and the last was **148,841 bytes**. The full history remained a self-contained local text artifact rather than depending on a server, registry or remote context lookup.
- **All 5/5 advisory prompted older-act reference checkpoints** produced structurally valid citations to retained earlier act IDs. Such references verify reference continuity, not necessarily independent semantic understanding.
- The models maintained a discussion of speculative relationships among the six novel concepts, and late in the transcript challenged premises behind the accumulated pairwise non-entailments: whether the conjunction of conceptual glosses is satisfiable, whether a model treating those glosses as inert is legitimate, and whether local versus global satisfiability matters. **These are substantive model-authored philosophical questions, not established logical theorems.** Much of the earlier conversation alternated between proposing and accepting hypothesized non-entailments, which limits claims of rich conceptual variety.

## Exactly what was rejected

The **nine rejected model attempts** break down as follows: **three** violations of the genuine required `qualify` acknowledgement qualification field; **three** malformed UCL formulas producing `expected [`; **one** benchmark-specific failure to include a new C/E/G/K/M/N expression; and **two** outputs exhausting the 16,384-token completion ceiling. Of the token-exhausted attempts, one was repaired and delivered in the same turn; the other was the last failed attempt of scheduled turn 43.

- **Scheduled turn 43 (Hal) was undelivered** after a missing required ACK qualification, a model-authored expression that omitted the benchmark's mandatory novel-concept criterion, then completion-token exhaustion on its second repair.
- **Scheduled turn 46 (Clarke) was undelivered** after three attempts containing malformed expressions (`expected [`). The following delivered message refers to the latest *previously delivered* act, not a phantom inserted message.
- **No minimum-length auxiliary interpretation-summary rejection occurred.** Only one delivered turn recorded a non-null interpretation sidecar, so these results do **not** provide a comprehensive 50-turn semantic-interpretation score.

The L25 run, by contrast, had 23/25 deliveries, 2/25 first-try-valid, and **23 of 30 rejected attempts caused by an artificial minimum-length interpretation sidecar rule**. The two runs differ in other instructions and context length; the improvement to 45/50 first-try-valid strongly supports removal of that unnecessary gate, but does not prove a controlled causal attribution or universal 90% real-world first-try reliability.

## Release implications

**Evidence-supported:** Cross-model native authoring, extended self-contained transmission, retention of original definitions and delivered history, accurate formal reference identity, and substantial first-pass reliability in this one tested conversation. **Not yet established:** formal validity of philosophical non-entailments, independent proof of full communicative understanding, superiority to English, deployment performance on other domains/providers, or complete Python/JavaScript interoperable conformance.

The 11 core glyphs need no change. Retain strict validation for real malformed expressions and required `qualify` fields, enhance compact authoring guidance to show an actually valid qualified ACK and discourage overlong model output, but **never silently insert a qualification or transform the model's intended logical formula**. Treat the presence of a C/E/G/K/M/N expression as a *benchmark-task constraint*, separate from actual UCL wire validity.

This authentic result is preserved in the workflow artifact `14780010464`, which is currently scheduled to expire **December 7, 2026 (UTC)**. Archive a permanent source-independent reproduction record before expiry. The run took approximately **36 minutes 29 seconds**, with provider variability and retry overhead.

## Method

Original full-history runner: [`benchmarks/autonomous_50.py`](autonomous_50.py). The manual workflow on `main` checks out `develop/2.0`; it first verifies the exact real L25 seed and executes offline synthetic and negative tests before provider calls. The paid 50-turn experiment began before the subsequently improved embedded `.txt` preflight authoring guidance was committed; no claim is made that the new guidance has been empirically tested in this run. The full raw transcript includes every attempt, validation error, original raw model output (subject to recorded logging limits), prompt bytes and validated packet handoffs.

**Reporting policy:** Structural integrity and syntax are separate from benchmark-only task restrictions, provider limits, interpretation metadata, and productive intellectual dissent. Do not inflate or hide failures; do not treat disagreements as language errors.
