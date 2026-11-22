# UCLBench — live autonomous semantic relay (UCL 2.0 experimental)

This workflow lets **Clarke and Hal actually generate and relay messages** in successive turns. It compares:
1. ordinary English;
2. structured English with explicit target and action;
3. reference-validator-assisted UCL Portable.

**Compact is retired from active benchmarks.** Its archived implementation and regression vectors remain intact for historical reproducibility.

## Experimental method

The same initial two-component hypothetical proposition P AND B is sent to every condition. A model authors a response with a **private, self-reported intent** `{action,path}`, along with message prose. The next model sees only the serialized handoff, **not the private intent**, and must report its understanding of the preceding speaker before authoring its own response. Six turns (or an initial four-turn pilot) allow misunderstandings to propagate and later messages to challenge or reopen earlier claims. After turn three, an identical deliberately unreliable recap is presented in every arm.

- **English:** only the author's message prose is transmitted, together with the accumulated transcript.
- **Structured English:** identical prose plus the explicit declared target/action in a JSON envelope. This is a machine-assisted structured format, not simply prose.
- **UCL Portable:** a local, validated author tool constructs the fully self-contained UCL packet including immutable definitions and precise acknowledgements. Sender does **not** independently generate the entire UCL syntax or cryptographic hashes. Prior packet always remains fully expanded. Validator checks the wire after each generated turn.

The receiver's receipt is compared with the **sender's privately declared intent** for an exact pair match (action and P/B target). The resulting score is **cross-model agreement with author self-report**, not automatically proof that the author truly expressed the same intent in English. We preserve the raw message and self-report separately for eventual *blinded human annotation* and leakage checks. Author intentions are **not shared with recipients**. No LLM judge is used to grade the receipt; the expected exact reference/stance comes directly from the hidden declaration.

**Important comparability limits:** UCL and structured English use an encoder which guarantees the author's declared target/action in the wire, whereas English's prose is unaudited. Thus a higher score for either structured format might come from that supplied structure/tool assistance. Input sizes, retained metadata and model starting roles can also differ. This is a *protocol-stack feasibility experiment*, not controlled proof of UCL glyph superiority. Larger replicated samples and independently annotated English intent/message alignment are needed for a rigorous superiority claim.

## Running

GitHub Actions: [UCLBench autonomous dialogue (manual)](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-dialogue.yml). Trigger on **main**; it checks out **develop/2.0** for all code. The default is `paid_run=no`, which runs all local regression tests and simulated messages **without paid API calls**. Then try `paid_run=yes`, `turns=4`, `trials=1`, and `cap_usd=2.00`. Six turns and two trials can be selected later. Trial two swaps starting speaker. All real API requests are manually triggered; no automatic retries, SDK retries disabled. A pre-call cost reservation stops requests estimated to exceed the selected budget. This is **not a billing guarantee**, so retain an independent Radium provider-side spending limit.

The JSON artifact stores every synthetic prompt/visible response, intended meaning, interpreted meaning, full token usage, form validity, and estimated cost. Full UCL packet bytes are not stored verbatim in each row to keep artifacts manageable; each recipient prompt can be reconstructed from the retained protocol, model decisions, and baseline. Please do not add private data or credentials to these public GitHub artifacts.

Local free test:

```sh
python -m unittest discover -s benchmarks -p 'test_live_dialogue.py' -v
python benchmarks/live_dialogue.py --dry-run --trials 2 --turns 6 --output dialogue-dry-run.json
```

To preserve the prior benchmark comparison, **do not overwrite** the earlier experiment files or change the immutable 1.0 specification. Existing Compact tests remain in the offline conformance suite.
