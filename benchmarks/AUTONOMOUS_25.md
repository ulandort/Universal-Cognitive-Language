# L25 — autonomous 25-turn full-history UCL continuity stress

**Status:** manually launched experiment, not run on pushes. No paid L25 result has been asserted. It extends the **real final RR-1 Portable packet** from [RR-1 run 45080241779](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45080241779), preserving original CG-1 concepts C/E/G/K/M/N and their exact immutable SHA-256 definition IDs.

## Why this matters
This is the first proposed **25 independently model-authored conversational turns**, not the earlier scripted 25-event archival challenge. It starts with a verified 20-act history, asks Clarke/Hal for 25 additional native contributions and ends at **45 retained acts** when all turn deliveries succeed, well below the current 100-act limit. It does not silently condense history, rename definitions or repair semantic content.

## Method and guards
- The full self-contained 2.0 Portable envelope is sent on **every single request**, and the packet, hashes, definition IDs, prior acts and ACK count are validated for each delivered turn.
- Models are free to agree, disagree, question, qualify, revise their own reasoning in prose or propose hypothetical counterexamples. No preordained philosophical conclusion or truth grade. The exact six prior concepts remain available in each message.
- Every fifth turn (5/10/15/20/25) asks the next speaker to connect the current reasoning with a retained act at least six acts old, and checks its actual formal reference. This is a **prompted recall task**, not spontaneous recall or proof of interpretive fidelity.
- Model-authored prior-turn interpretations (not visible to their predecessor) are preserved for **human audit**, not automatically given a semantic-correctness score. Understanding and agreement are separate.
- Each completed turn retains raw model attempts, validation error types, first-try vs recovery, model-owned repairs, packet bytes and cost. Only validated model-authored contributions are delivered.
- Maximum **16,384 completion tokens per model request**; up to two explicit model-owned repairs per turn, with a **default $12 USD estimated cap**, not a provider-guaranteed hard limit. Real provider timeouts can be billed outside the estimate.
- Maximum wire growth guard is 900 KB; do not truncate or quietly omit any historical act. An exceeded limit is a reported failure requiring explicit protocol work.

## Reproducibility
GitHub Actions workflow **UCLBench Autonomous 25-Turn Stress (manual)** lives on `main` and checks out `develop/2.0`. It retrieves the RR-1 artifact `14776719080`, validates it, then performs a free authentic-seed 25-turn regression/synthetic run before any paid API call. The original RR-1 GitHub artifact expires December 6, 2026: explicitly preserve any needed reproducibility fixture with provenance before then.

Recommended paid inputs: `paid_run=yes`, `max_repairs=2`, `cap_usd=12.00`. Use `paid_run=no` to verify the free oracle independently.

**Scoring principle:** Structural integrity, transport, authored syntax, meaning attribution, response format and independent intellectual disagreement must be reported as distinct dimensions. An AI disagreement is *not* a language failure. A valid UCL expression alone is not logical entailment, empirical truth, semantic comprehension or proof of UCL superiority to structured English.

The 50-turn stress test is contingent on observed L25 reliability and context/cost growth. Full public UCL/2.0 release remains the selected target, subject to complete cross-language interoperability and final documentation checks.
