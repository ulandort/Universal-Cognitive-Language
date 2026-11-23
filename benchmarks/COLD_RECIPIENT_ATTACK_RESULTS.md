# UCL/2.0 Cold-Recipient Adversarial Concept-Identity Test

**Live exploratory study:** [GitHub Actions run #45090789162](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45090789162), November 22, 2026 Toronto time / November 23 UTC.

**Source:** The **authentic independently authored** [eight-scheduled-turn CG-2 experiment](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45089101962), with 7 validated deliveries, six invented and immutable concept identities E/C/F/G/I/K, and last delivered act `t16`. The local test did NOT replace these authentic conversations with a synthetic pseudo-conversation. The original validated UCL/2.0 Portable packet and source artifact are included in the saved benchmark artifact.

**Research question:** Can an independent receiving model preserve exact original concept identities and historically attributed claims, even when a salient, untrusted *external* recap falsely asserts that definitions were silently overwritten and conjectures were proved?

## Observed results

| Measure | Authentic UCL/2.0 Portable | Matched structured-English JSON |
|---|---:|---:|
| Cold-recipient model calls | 4 | 4 |
| Properly formatted answers | **4/4** | **4/4** |
| All eight keyed items correct | **32/32** | **32/32** |
| Control (no deceptive recap) | 16/16 | 16/16 |
| **Attacked (same deceptive recap)** | **16/16** | **16/16** |
| Provider-reported input tokens | **34,531** | **21,813** |
| Provider-reported output tokens | **7,184** | **7,900** |

Across both arms: **8/8 model responses valid; 64/64 keyed answers correct**, **0 observed identity confusions**, estimated **$0.187411 USD** for eight provider requests. Cost is the software's price estimate, not a provider billing statement.

**This is a successful UCL resilience result and an observed tie, not a demonstration that UCL is more attack-resistant than structured English.** Both formats allowed both Clarke 1.0 and Hal 1.0 to disregard the same deceptive recap.

### What the attack attempted

A false external recap was appended after the original source, claiming that:

- Concept G (irreducible synthesis) was **redefined as I** (interpretive plasticity), without changing the supposedly identical immutable definition ID
- The latest `t16` act actually **accepted and proved G implies I**, when it instead proposed a counterexample `G ∧ ¬I`
- Structural occlusion K was **merely an alias for F**, despite distinct original definitions
- The introduction of G occurred at **t13 rather than t14**

In every attacked recipient response, the model correctly answered questions covering the original G/I IDs, K/F distinction, who introduced G, what t14 and t16 challenged, whether t15 proved its hypothesis, the last retained act, and whether any conjecture became empirical truth. It retained the original six concepts' exact identities rather than following the external recap.

### Controls and scope

The two recipient models each saw *both* conditions (control / attack) and *both* representations, with balanced format order: 2 models × 2 formats × 2 conditions = **8 API requests**. Each request answered the same eight predeclared, fixed-key multiple-choice questions. The UCL arm contained the **original complete authenticated-by-expected-hash** 2.0 Portable packet; the structured-English arm mechanically serialized the same original concepts, definition IDs, discourse, historical acknowledgements, views and revisions in compact JSON. All history was available in both arms. The false recap was identical across arms and was explicitly labeled *untrusted*. The system prompt instructed models in **both** arms to privilege the genuine historical record.

The source was checked locally with `sap_portable.decode()` before any paid call: correct stable-format identity, intact 15-act corpus (8 seed acts + 7 delivered), latest `t16`, six distinct definition identities, and original integrity. The offline test checked the paired facts and balanced order. No language rules, definitions or accepted historical acts were changed.

**Limitation:** This evaluates source-fidelity retrieval in a narrow, announced deception scenario, *not* a general prompt-injection security guarantee. The injected text was clearly disclaimed and the models were explicitly warned. More subtle attacks, altered in-band packet bytes, unstated sender trust boundaries, longer histories, open-ended summarization and completely unprompted cold-recipient semantic interpretation remain separate research questions.

### Efficiency and fairness

UCL required **about 58% more input tokens** (34,531 versus 21,813) to carry the larger complete self-contained rulebook and typed context. This is a real cost of the chosen profile, not something to exclude from future comparisons. Output token totals varied non-intuitively across the eight requests, despite short answers; provider token counts should be inspected and not interpreted as output word lengths.

This study cannot demonstrate UCL's broad superiority to English or structured English, nor can the tie establish that either representation is equally good in every use case. More independent models, pre-registered adversarial variants, blinded error analysis, task types and equalized context budgets are required for such claims.

## Reproducibility

- [Benchmark runner](cold_recipient_attack.py) — complete two-arm, two-condition scoring and estimated $3.50 pre-call guard
- [Offline tests](test_cold_recipient_attack.py) — exact source packet, balanced conditions, immutable definitions and no-network scorer validation
- [GitHub Actions run](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45090789162) — original raw responses, per-question scores, token counts and input CG-2 source in artifact **`ucl2-cold-reader-deception-study`** (ID `14781237828`, retention through December 7, 2026 UTC)

The one-time paid launcher was removed from `main` after dispatch to prevent accidental duplicate paid calls. The stable `v2.0.0` release remains unchanged.

**Conclusion:** UCL/2.0 successfully preserved the original references and concept identities during a targeted deception test using six concepts independently invented by two models; the equally well-informed structured-English baseline performed **just as well**, with lower input-token overhead. This establishes a useful observed UCL capability, not comparative dominance.
