# Evidence log — November 22, 2026 independent-model manual exchanges

## Setup

Initial scenario: synthetic prior acts `t1` through `t7`, open hypothetical domain D, speculative P(A) and separate measurable B(A). An intermediary supplied a self-contained plain JSON UCL packet to an external model in a fresh conversation; the model returned an unverified draft; an assistant repaired formatting, hashing or semantic inconsistencies, validated the repaired packet and forwarded it to the other model.

## Observed contributions

| Act | Model | Contribution | Limitation |
|---|---|---|---|
| t8 | Grok | Questioned how P and B could diverge in a thought experiment | Required JSON/ACK/body/hash repairs |
| t9 | Qwen | Introduced M as a proposed mediating property | Placeholder definition hash, malformed expression and omitted guide content |
| t10 | Grok | Challenged M's circularity and proposed an independent-coherence criterion | Unrecognized ACK action, incorrect ACK targets and syntax repairs |
| t11 | Qwen | Proposed refining M to internal coherence (encoded as N to preserve M) | Changed immutable definition without new identity; symbolic expression contradicted prose |
| t12 | Grok | Observed stipulated N does not decide P or prove independence | Required orientation and metadata fixes |
| t13 | Qwen | Proposed K as asymptotic fixed-point condition for P | Unverified new hash and missing formal definition for the designated structure S |

The later six acts were generated as model contributions but their transmitted validated forms were **mediator-edited**, not raw independent output. The example file is an illustrative *reconstructed experiment artifact*; its speaker fields are unauthenticated and some earlier text/metadata reflect repair annotations. Test A previously established qualitative English comprehension in Grok and Qwen, but did not require correct UCL authorship. No blinded scoring, randomized control, English baseline, or repeated trials were run. No external AI computed its own verified SHA-256 in this workflow. The exercise supports feasibility of **validator-assisted continuity**, not superior reasoning, a new machine-only language, or autonomously valid two-way transfers.

## Proposed evaluation next

Compare three arms with fresh model sessions: (a) unstructured English, (b) structured English/JSON with explicit references, (c) UCL. Match theoretical tasks and dialogue lengths; pre-register metrics for citation/ACK errors, meaning drift, preserved definitions, syntactic validity, editor interventions, token/byte cost, reasoning novelty, and contradiction recovery. Publish raw outputs plus interventions separately from repaired packets, without claiming signed model provenance.

## November 22, 2026 — UCLBench scripted 25-event baseline, Radium

**Runs:** [free verification](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45061494580) and [paid benchmark](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45061533668). Historical event sequence contains 25 scripted new acts plus eight baseline acts (33 retained), not 25 independent AI-authored turns. Each of Hal 1.0 and Clarke 1.0 read checkpoints 10 and 25 across four representation formats; 16 API calls, 112 objectively keyed multiple-choice answers.

| Format | Correct / total | Invalid or empty model responses |
|---|---:|---:|
| Ordinary English | 20/28 | 1 |
| Structured English | 22/28 | 1 |
| UCL Portable (mechanically authored) | 28/28 | 0 |
| UCL Compact (mechanically authored) | 14/28 | 2 |
| **Total** | **84/112** | **4** |

Provider-reported usage yielded **$0.252649 USD estimated** by the harness; the user's provider account may report a different aggregate cost. The 28 missed answers correspond to **four responses with no visible answer**, reported as output-length exhaustion at a 1,536-token completion cap. **All 12 responses that produced valid answers scored 100%** (84/84); there were no demonstrated wrong semantic interpretations among valid responses. Thus **75% end-to-end accuracy is not 75% semantic comprehension accuracy**. This small, one-repetition run gives *no evidence of UCL superiority over English*: observed format differences could arise from model-specific completion behavior, prompt size, output token limits, or chance.

**Follow-up protocol (pre-run plan):** Raise max output to 3,072 tokens; repeat all model/checkpoint/format blocks (1, 2, or 4 passes) with cyclically rotated format order; publish **end-to-end accuracy** separately from **accuracy conditional on a valid complete model answer**, output validity, reason for failure, and input/output token counts. Retain all raw synthetic visible responses, model identifiers and estimated API cost. Repeated evaluations of the same scripted questions are exploratory and *not independent task samples*. Manual paid workflow only, with a pre-call estimated cap and separate provider-side account limit.



## November 22, 2026 — assisted autonomous 6-turn × 2-trial dialogue baseline

**Live run:** [GitHub Actions 45064778784](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45064778784), completed successfully; estimated **$0.998079 USD**, all **36** scheduled turns attempted, with **two UCL recovery calls**. The free workflow before it is [45064702356](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45064702356) and is an oracle only.

| Arm | Valid messages / scheduled | Exact receipts correct / scored | Recovery requests | Input tokens | Output tokens |
|---|---:|---:|---:|---:|---:|
| English | 12/12 | 10/10 | 0 | 11,794 | 33,343 |
| Structured English | 12/12 | 10/10 | 0 | 12,525 | 32,604 |
| Tool-assisted UCL Portable | 11/12 | 9/9 | 2 | 60,674 | 51,843 |

UCL's two recovery attempts produced one successfully delivered turn and one permanently failed turn, after which the next sender resumed from the last successfully transmitted message; hence only nine UCL receipts were scorable. No format produced a wrong **scored** receipt. No benefit over English was established on semantic fidelity. UCL consumed about **5.1×** as many input tokens as ordinary English and about **1.55×** as many output tokens, driven by carrying complete historical packets, reasoning and retries.

**Interpretation and next methodology:** UCL was mechanically assembled by a tool from the model's separately declared semantic intent and English note. This is fair evidence about *the tool-assisted stack*, not direct UCL authorship. The following separately documented [native authorship research suite](../benchmarks/NATIVE_AUTHORING.md) pre-registers four independent semantic traps, native formal act/ACK authoring, no-tools complete-packet authorship, bidirectional sender/receiver scoring and four-turn directly-authored conversations; it preserves raw transcripts and separates strict checksum/serialization from meaning. Neither its offline tests nor its existence is live empirical evidence. **All paid tests remain manually triggered**.

