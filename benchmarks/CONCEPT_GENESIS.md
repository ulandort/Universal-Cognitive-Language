# CG-1 — independent concept genesis (UCL/2.0 research)

**Status:** exploratory; opt-in paid workflow, never triggered by a GitHub push. The UCL/1.0 core and default plaintext wire remain unchanged.

## Research question
Can Clarke and Hal create new, precisely typed UCL concept definitions in their own model outputs, transmit them in self-contained UCL/2.0 Portable packets, independently identify what the previous new concept refers to, and continue speculative reasoning without rewriting inherited definitions?

## Method
- A six-turn, one-direction alternating dialogue (Clarke, Hal, Clarke, Hal, Clarke, Hal). Four or eight turns are additional manual options.
- Beginning from the existing eight-act hypothetical P/B baseline, both initial speakers **must independently author one new unary predicate** on domain D, in addition to a substantive English semantic gloss. Later speakers may author more.
- Only a fresh, unallocated single-character extension glyph can be used, drawn from a limited experimental candidate set. UCL/1.0's **11 core operators never change**. The models must use their new concepts as **well-typed formulas** in the same contribution.
- The next model sees the full portable packet including immutable definition glosses and canonical IDs; it must identify the most recently invented glyph and exact definition ID and paraphrase its meaning in its own words. A hash match only measures correct reference, **not semantic comprehension**; paraphrases require blinded human review.
- The model writes the entire semantic definition, UCL formulas, act note and ACK. The deterministic host only extends the preserved prior packet, calculates canonical definition IDs/body/checksums, and validates; it **does not generate or modify the invented meaning**.
- Up to two explicitly model-authored corrections per turn; the first-try and repaired deliveries are scored separately. Invalid attempts are never relayed. Full transcripts and raw error details are saved to an artifact.
- Budget cap is estimated, not a hard provider billing guarantee. Per-call maximum completion tokens is **16,384**; provider-hidden reasoning may consume them.

## Limits and interpretation
The initial research question and domain D are stipulated, so conceptual invention is free *within a bounded typed-predicate grammar*, not unrestricted AI discovery. Unsupported operators and novel domain sorts are intentionally excluded from this first test. A new glyph or SHA identity does **not** prove new conceptual content; human review must compare glosses to earlier definitions and evaluate whether later speakers use them coherently. Exact-reference matching and a successful local validator do not establish semantic equivalence, originality, truth, or an advantage over structured English. The baseline references to P/B are provided for communication continuity but do not dictate new concepts.

## Run
From repository **Actions**, choose [UCLBench Concept Genesis CG-1 (manual)](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-concept-genesis.yml), using **main** as the workflow branch. It checks out **develop/2.0** code.

Choose `paid_run=no` first to perform only offline regression tests and a synthetic protocol oracle. For a real bounded pilot, select `paid_run=yes`, `turns=6`, `max_repairs=2`, `cap_usd=4.00`. The workflow **always** runs the free checks before any paid call, and upload artifacts are retained 14 days.

Acceptance for first pilot: valid introduction of two independently authored immutable new definitions, every surviving message validates and preserves earlier packet context, at least one correct reference to each new concept, and human-reviewed paraphrases that distinguish concepts from P/B. Failures must be reported transparently, not silently repaired or counted as proof of impossibility.
