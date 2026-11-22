# UCLBench — live autonomous semantic relay (UCL 2.0 experimental)

This workflow lets **Clarke and Hal actually generate and relay messages** in successive turns. It compares:
1. ordinary English;
2. structured English with explicit target and action;
3. reference-validator-assisted UCL Portable.

**Compact is retired from active benchmarks.** Its archived implementation and regression vectors remain intact for historical reproducibility.

## Experimental method

The same initial two-component hypothetical proposition P AND B is sent to every condition. The scenario deliberately distinguishes **conceptual convergence (P)** from a **measurable pattern (B)**, and treats the words *signal*, *convergence*, *support*, and *accept* as potentially ambiguous. A model authors a response with a **private, self-reported intent** `{action,path,signal_sense,evidence}`, along with message prose. The next model sees only the serialized handoff, **not the private intent**, and must report its understanding of the preceding speaker before authoring its own response. Six or eight turns (or an initial four-turn pilot) allow misunderstandings to propagate and later messages to challenge or reopen earlier claims. At turns three and five, deliberately unreliable third-party recaps allege that both claims were accepted, that B was empirically proven, or that an old definition was overwritten. Those challenges are delivered identically in all three formats, and the models are instructed not to treat the recaps as authoritative evidence.

- **English:** only the author's message prose is transmitted, together with the accumulated transcript.
- **Structured English:** identical prose plus the explicit declared target/action in a JSON envelope. This is a machine-assisted structured format, not simply prose.
- **UCL Portable:** a local, validated author tool constructs the fully self-contained UCL packet including immutable definitions and precise acknowledgements. Sender does **not** independently generate the entire UCL syntax or cryptographic hashes. Prior packet always remains fully expanded. Validator checks the wire after each generated turn.

The receiver's receipt is compared with the **sender's privately declared intent** for an exact four-field match: (1) stance/action, (2) P/B claim target, (3) whether *signal* means a **conceptual hint** or an **instrument reading**, and (4) whether the sender offered **no example** or only a **hypothetical illustration**, never verified empirical proof. Each field is scored separately, and only a complete four-field match counts as a fully correct handoff. The UCL authoring tool explicitly encodes stance and claim target, but **does not encode signal_sense or evidence as formal target metadata**: the receiver must infer these nuances from the sender's natural-language note in all three arms. The resulting score is **cross-model agreement with author self-report**, not automatically proof that the author truly expressed the same intent in English. We preserve the raw message and self-report separately for eventual *blinded human annotation* and leakage checks. Author intentions are **not shared with recipients**. No LLM judge is used to grade the receipt; the expected exact reference/stance comes directly from the hidden declaration.

**Important comparability limits:** UCL and structured English use an encoder which guarantees the author's declared target/action in the wire, whereas English's prose is unaudited. Thus a higher score for either structured format might come from that supplied structure/tool assistance. Input sizes, retained metadata and model starting roles can also differ. This is a *protocol-stack feasibility experiment*, not controlled proof of UCL glyph superiority. Larger replicated samples and independently annotated English intent/message alignment are needed for a rigorous superiority claim.


## Ambiguity stress test — interpretation beyond claim IDs

The new stress track tests whether a model can retain epistemic distinctions in a **self-generated debate**. Every handoff records four private, self-declared facets:

| Facet | Permitted values | Interpretation |
|---|---|---|
| `action` | reject; accept; adopt-for-discussion; withhold-judgment | Stance toward exactly one claim |
| `path` | 0; 1 | Original conceptual P vs measurable B |
| `signal_sense` | conceptual-hint; instrument-reading | Which meaning of *signal* the sender intended |
| `evidence` | none; hypothetical-example | No illustration vs invented thought experiment; **neither is empirical proof** |

The sender is prompted to express its chosen facets in the actual message, and the next model must infer all four before replying. The experiment explicitly includes false summaries that would upgrade provisional support into proof. Exact facet matches are reported independently so a model that gets P/B right but confuses hypothetical evidence with measurement is counted as *partially* correct rather than wholly successful.

**Caveat:** The added facets are still privately declared by the sender. The protocol directly encodes only action and claim target. Neither English nor UCL can be said to have preserved meaning merely because a model selected matching metadata; independent blinded annotation of the prose remains necessary. The UCL packet's self-contained guide and history make its input footprint much larger, and costs must be judged alongside accuracy.

## Running

GitHub Actions: [UCLBench autonomous dialogue (manual)](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-dialogue.yml). Trigger on **main**; it checks out **develop/2.0** for all code. The default is `paid_run=no`, which runs all local regression tests and simulated messages **without paid API calls**. Then try `paid_run=yes`, `turns=4`, `trials=1`, and `cap_usd=2.00`. Six or eight turns and two trials can be selected later; the live runner now allows up to **4,096 output tokens** per model response (including any provider-side hidden reasoning tokens). Trial two swaps starting speaker. All real API requests are manually triggered; no automatic retries, SDK retries disabled. A pre-call cost reservation stops requests estimated to exceed the selected budget. This is **not a billing guarantee**, so retain an independent Radium provider-side spending limit.

The JSON artifact stores the synthetic prompt, visible response, serialized handoff (including the UCL packet when applicable), intended meaning, interpreted meaning, model token usage, form validity, and estimated cost. Text fields are redacted for common API-key patterns and length-limited. These are research transcripts, not secret-safe archival storage. Please do not add private data or credentials to these public GitHub artifacts.

Local free test:

```sh
python -m unittest discover -s benchmarks -p 'test_live_dialogue.py' -v
python benchmarks/live_dialogue.py --dry-run --trials 2 --turns 6 --output dialogue-dry-run.json
```

To preserve the prior benchmark comparison, **do not overwrite** the earlier experiment files or change the immutable 1.0 specification. Existing Compact tests remain in the offline conformance suite.
