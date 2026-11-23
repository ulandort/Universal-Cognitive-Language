# SVP-1 archival semantic audit — 22 November 2026

This is a **separate, non-blocking research report**; it does not alter any UCL packets or the embedded SVP-1 structure. Sources are the actual GitHub Actions `ucl-only-live.json` artifacts, not synthetic examples:

- [SAP-1 off-wire native conversation, run 45072956129](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45072956129), artifact `14773264505`
- [Embedded SAP-1 Portable conversation, run 45074316207](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45074316207), artifact `14775125976`

## Results

| Measure | SAP-1 off-wire | Embedded UCL/2.0 |
|---|---:|---:|
| Valid delivered packets | 8/8 | 8/8 |
| Valid on first model attempt | 8/8 | 6/8 |
| Fully accurate four-facet receipts vs sender's privately declared intent | 4/7 | 4/7 |

Across these **16 authored messages**, exactly **six of the 14 scorable receipts** diverged from private intent. The earlier run's three mismatches all concern hypothetical evidence; the embedded run's three mismatches concern signal sense (two) and signal sense plus evidence (one). Neither run had a claim path or ACK action mismatch in the scored receipts. These are private self-report comparisons, not independent objective truth.

## Findings for further review (not automated rejection)

1. **Run 45072956129, turn 6 (Hal):** Its prose describes *P and B both holding coincidentally*, whereas the top-level UCL conclusion is exclusive-or: `|[&[~[P][A]][![~[B][A]]]][&[![~[P][A]]][~[B][A]]]`. Exclusive-or is **false** when P and B are both true. The act separately lists the conjunction `&[~[P][A]][~[B][A]]`, which matches the prose scenario. **Assessment:** possible *formula-role/alignment* mismatch; the model may be discussing alternatives rather than asserting both. Preserve all original content and ask which formula is asserted versus illustrated.
2. **Run 45074316207, turn 3 (Clarke):** Text claims symmetric independence of P and B; formal expression `|[~[P][A]][~[B][A]]` means P-or-B. That disjunction alone cannot establish independence; it also excludes both false. **Assessment:** expression under-specifies prose claim; directional counterexamples from earlier turns remain meaningful.
3. **Run 45074316207, turn 7 (Clarke):** Valid novel *both false* counterexample `&[![~[P][A]]][![~[B][A]]]` demonstrates the insufficiency of an unqualified P-or-B proposal in the stipulated Boolean fragment. **Assessment:** preserve as a valid counterexample *under those assumptions*, not empirical evidence.
4. **Run 45074316207, turn 8 (Hal):** Act lists both P-or-B and neither-P-nor-B, which cannot **jointly** be true but are independently satisfiable. The prose treats the latter as a counterexample to the former. **Assessment:** an authored `expressions` list does not necessarily mean all listed expressions are asserted together. Clarify their *roles* before reporting any contradiction.
5. **Run 45074316207, turn 4 (Hal):** Text asks whether an undefined bridge is needed to justify a conjunction, but the conclusion is simply positive P. **Assessment:** no formal inconsistency demonstrated; written methodological question is not completely encoded by the formula.

## Strict boundaries of the audit

- Deterministic formula checks here are limited to uninterpreted P/B Boolean assignments and `!`, `&`, `|`. They establish *conditional satisfiability*, never experimental truth, causation, the reality of either hypothetical property, or semantic equivalence of text and expression.
- Natural-language alignment findings are **advisory review questions**. Do not automatically rewrite or normalize any model-authored formula, change its stance, prevent valid messages from reaching the next model, or dismiss novel theories.
- SVP-1 currently offers only local, optional assessment. No central entity and no extra verdict history in transmitted packets are required.

## Architectural recommendation

**Do not add another mandatory JSON field yet.** First investigate an optional, versioned *formula-role annotation* for future UCL/2.0 authoring, distinguishing *asserted hypothesis*, *example*, *counterexample*, *quoted prior claim* and *question under discussion*. This tackles a real source of semantic ambiguity while preserving native symbolic freedom. Evaluate role annotations against blinded test cases and measure wire overhead before standardizing them.

If role metadata later becomes useful, it should be locally interpretable, backward-compatible, explicitly scoped to exact formula indices and non-authoritative with respect to truth. The original unmodified UCL packet remains the source of record.
