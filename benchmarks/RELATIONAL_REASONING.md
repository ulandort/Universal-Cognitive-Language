# RR-1 — model-authored reasoning across CG-1 concepts

RR-1 is an **experimental UCL/2.0 research trial**, not proof that UCL is semantically superior to English or that any generated argument is true.

## Authentic six-concept continuity
The starting self-contained packet is taken **verbatim** from the final validated handoff of paid [CG-1 run 45079394296](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45079394296), artifact ID `14776243270`. The workflow retrieves the artifact, extracts the sixth-turn complete Portable message, validates its guide and checksums, and checks that all six independently generated predicates C/E/G/K/M/N match their **exact original definition identities**. This is genuine continuation, not fabricated reconstructed context.

**Artifact retention caveat:** The original GitHub artifact is scheduled to expire December 6, 2026. RR-1 must be run while it is available; for permanent reproduction, archive the true seed in a versioned fixture using explicit provenance before that date.

## Test design
- Clarke and Hal each independently write native UCL semantic contributions; 6 turns by default, optional 4/8.
- The models must compose a **well-typed UCL formula** connecting at least two of the six invented concepts through a conjunction or disjunction. They independently determine the relation, its scope, possible counterexamples and the stance taken. Merely listing separate atoms is insufficient.
- Model-authored interpretations of the immediately prior newly delivered contribution are preserved for qualitative review. The first new turn supplies null. The receiving model may **agree or disagree**; dissent is not a failure.
- The host preserves all earlier acts, definitions and history and computes hashes; it does not invent, rewrite or silently repair semantic content. Model-owned corrections are isolated and separately scored.
- The unchanged 11 core glyphs and existing Portable envelope validator remain normative; no new arbitrary operators are introduced.
- The workflow runs a synthetic offline oracle and regression tests first, then optional manual paid model calls bounded by a user-selected estimated spending guard; maximum completion-token ceiling **16,384**.

## Reporting and limits
Always report first-attempt acceptance, repairs, complete validated deliveries, original formula content, observed token costs, and qualitative review. Do not count legitimate intellectual disagreements as errors. A well-typed formula merely demonstrates **structural composition**; it does NOT establish derivation, entailment, objective truth, or deep understanding. The prompt directly requires at least two invented concepts, so no claim of spontaneous complex-symbolic reasoning should be inferred. Model paraphrases may misrepresent prior contributions and require inspection before any semantic-fidelity claim. This pilot has **no English comparison arm**.

## Launch
Open the repository Actions page and select **UCLBench Relational Reasoning RR-1 (manual)** on branch `main`, which checks out `develop/2.0`.

Recommended manual inputs: `paid_run=yes`, `turns=6`, `max_repairs=2`, `cap_usd=4.00`. Running `paid_run=no` first costs no API fees.

If this exploration succeeds, prioritize **25-turn** autonomous continuity and then **50-turn** stress, with fair reporting of observed transport/semantic limits. Public 2.0 **beta** still requires versioned documentation and interoperability; a green RR-1 run alone is not a stable release approval.
