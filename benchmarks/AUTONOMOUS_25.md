# L25 — autonomous 25-turn full-history UCL continuity stress

**Status:** paid L25 experiment completed and independently archived; manual workflow, not run on pushes. It extends the **real final RR-1 Portable packet** from [RR-1 run 45080241779](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45080241779), preserving original CG-1 concepts C/E/G/K/M/N and their exact immutable SHA-256 definition IDs.

## Live result — sustained self-contained communication

**The real 25-turn trial successfully delivered 23 independently model-authored UCL messages**, continuing an already-established 20-act conversation to **43 fully retained acts**. Both Clarke and Hal preserved all six genuinely model-created concepts and their immutable identities throughout the delivered history. The validated packets grew from **41,106 to 73,120 bytes** without silent condensation or modification of prior delivered acts. **All five prompted older-history reference checkpoints passed structural validation.**

The strongest result is that the models continued a real, evolving cross-model discourse with a growing, fully self-contained UCL packet—not a fresh synthetic dialogue or a scripted sequence. The discussion explored relationships among previously invented concepts, including competing hypothetical non-entailments. This supports long-form transport, concept identity retention and formal-reference continuity; it does **not** establish objective truth of those arguments or perfect semantic understanding.

**Run:** [GitHub Actions #45081092157](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45081092157) · November 22, 2026 · about 22m38s · estimated **$2.955910 USD** · 53 API requests. The workflow finished successfully; two of the 25 scheduled contributions were not delivered, so **23/25** is the correct delivery count. Of the 23 delivered messages, **2 were accepted initially and 21 after explicit model-authored corrections**.

### What the failed attempts mean

The benchmark used an **overly strict, non-UCL auxiliary rule** requiring interpretation notes of at least 20 characters. This caused **23 of 30 rejected attempts (76.7%)**. Those 23 rejections are **not UCL grammar failures, broken concept identities, lost history, or evidence of failed cross-model reasoning**. This was a problem in the experimental scoring/delivery gate, and the rule was removed from the subsequent 50-turn test.

The other seven rejected attempts are genuine model-authoring/validation issues that should not be hidden: **five malformed acknowledgement paths** (JSON string indices rather than integers), **one incorrect expression field type**, and **one unknown operator**. A rejected attempt does not automatically equal a lost turn, because the model could independently repair its contribution and retry. The two undelivered turns were scheduled turns **7 and 24**.

**Interpretation matters:** The high repair count is not an appropriate standalone measure of UCL's structural robustness because an artificial sidecar requirement was used as a delivery criterion. Equally, it would be inaccurate to report this as 25/25 success or to claim that no genuine authoring errors occurred. We report what worked prominently, and retain exact failures for independent reproducibility.

### What we changed for the next experiment

For L50, short, null or absent private interpretation metadata no longer blocks delivery. The prompt explicitly distinguishes valid ACK paths `[0]` from invalid `["0"]`; strict checks for actual UCL grammar, integrity, prior acts and hashes remain in place. Older-act recall probes are evaluated as separate evidence rather than artificial delivery gates. This lets the next stress test focus more directly on UCL while preserving honest auditability.

## Why this matters
This was a scheduled **25-turn independently model-authored conversational trial**, not the earlier scripted 25-event archival challenge. It starts with a verified 20-act history, asked Clarke/Hal for 25 additional native contributions and reached **43 retained acts** after 23 valid deliveries, well below the current 100-act limit. It does not silently condense history, rename definitions or repair semantic content.

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

The 50-turn stress test is prepared with safeguards informed by observed L25 behavior. Full public UCL/2.0 release remains the selected target, subject to complete cross-language interoperability and final documentation checks.
