# Universal Cognitive Language

**UCL — a self-contained communication protocol for independent intelligences**

*Define concepts. Exchange precisely scoped claims. Disagree without losing context.*

UCL lets AI systems exchange typed symbolic expressions, independently defined concepts, arguments, questions, acknowledgements and changes of position in an ordinary, readable **UTF-8 JSON `.txt` message**. The recipient can inspect the language guide, definitions and retained conversation **inside the same file**—without a central registry, hosted interpreter or remotely fetched schema.

> **Current release:** **UCL/2.0 Portable**. This is the supported, self-contained release profile; UCL/1.0 is retained as the inner typed grammar and historical specification, not the public default transport. The original 11 core glyphs are unchanged.

## Why UCL?

Natural language is expressive, but it can obscure exactly which proposition a reply accepts, rejects or qualifies. UCL adds explicit structure **without deciding which ideas are true**.

| Principle | How it works |
|---|---|
| **Self-contained** | The message includes its full guide, typed definitions, prior delivered acts and local authoring rules. |
| **Precise references** | Claim bindings, immutable definition IDs and scoped acknowledgements identify what is being discussed. |
| **Independent thinking** | A model can propose new concepts, explore hypotheses, object, withhold judgment or revise its own stance. |
| **No central authority** | Validation and checksum calculation are local; no hosted dictionary, third-party judge or external API is needed. |
| **Transparent history** | Full history by default in current long-form tests. Any future optional condensation must disclose what was omitted. |
| **Extensible, not arbitrary** | New typed concept definitions are allowed; unknown core operators are not silently accepted. |
| **Readable transport** | Plain UTF-8 JSON in `.txt` or `.json`. Optional tooling helps validate and construct messages. |

**UCL is not** a replacement for natural language, a mathematical oracle, a proof that an AI understood another AI, or a claim that every hypothetical assertion is true.

## See the protocol

UCL has **11 unchanged core glyphs**, typed user-defined symbols and explicit four-layer message structure. A few symbolic examples:

```text
~[P][A]                 A has property P
![~[P][A]]              It is not the case that A has P
&[~[P][A]][~[B][A]]     A has both P and B
|[~[P][A]][~[B][A]]     A has P or B
```

Here `P`, `B` and `A` are typed, defined symbols in a particular packet, **not globally prescribed meanings**. A named concept's immutable SHA-256 identity is derived from its definition.

A separate, optional **acknowledgement** precisely identifies the earlier claim to which a participant is responding. For example, `{"claim":"theory","path":[0]}` addresses the first subexpression of the bound earlier claim. The array contains a JSON **integer**; `["0"]` is not interchangeable.

### The portable `.txt` envelope

The stable UCL/2.0 Portable profile includes:

```text
UCL/2.0 portable JSON message
├── format + profile
├── structural_rules
│   ├── rules       (full local authoring guidance)
│   └── sha256      (guide fingerprint)
├── packet
│   ├── guide       (complete language grammar and requirements)
│   ├── definitions + domains + claims
│   ├── discourse + acknowledgements + history
│   ├── body + context + other UCL fields
│   └── integrity   (packet SHA-256)
└── checksum        (envelope SHA-256)
```

A receiver can validate the entire packet locally. Hashes detect changes relative to trusted expected identities; a self-contained checksum **is not an authentication signature**. Optional role annotations describe the intended purpose of individual formulas, not whether the formulas are true.

## Getting started

**Requirements:** Python 3.12+ for the reference CLI. The base validator uses the Python standard library; no cloud service or API key is required for offline checks.

Clone the repository and try the existing reference example:

```bash
python src/ucl.py check examples/cross_model_conversation_8_turns.json
python tools/sap_portable.py encode examples/cross_model_conversation_8_turns.json portable-example.txt
python tools/sap_portable.py check portable-example.txt
python tools/sap_portable.py decode portable-example.txt restored-ucl1.txt
```

The versioned, self-contained wire identifier is **`UCL/2.0-SAP1-PORTABLE`**. The exact canonical serialization, embedded authoring rules and offline validation requirements are defined in the [normative UCL/2.0 specification](docs/UCL_2_0_SPECIFICATION.md).

For constructing a new message from a locally verified prior packet and a model-authored contribution:

```bash
python tools/author.py examples/cross_model_conversation_8_turns.json examples/contribution_example.json next-message.txt
```

The authoring helper appends original model-authored content and recalculates deterministic integrity metadata; it **does not decide the speaker's stance or silently correct a formula's meaning**.

## Independently authored AI conversations

UCLBench tests whether two separate AI models can **actually use** the structure, not merely parse canned symbols. In November 2026, Clarke and Hal took an evolving conversation from an earlier shared context through concept creation and multiple follow-on experiments.

| Experiment | Observed result | What it demonstrates |
|---|---|---|
| Native UCL-only conversation | 16/16 delivered | Independent, validated authorship with model-owned repairs |
| Concept Genesis CG-1 | 6/6 delivered | Six model-authored new typed concepts with immutable IDs |
| Relational Reasoning RR-1 | 6/6 delivered | Model-authored combinations of those concepts |
| Autonomous L25 | 23/25 delivered | 43 retained acts; 5/5 prompted historical references |
| **Autonomous L50** | **48/50 delivered; 45/50 first try** | 91 retained acts; 5/5 prompted historical references; no silent history loss |
| **Post-release Concept Genesis CG-2** | **7/8 delivered; 6 novel definitions; 6/6 identity receipts** | Independently authored concepts, precise critique, counterexamples, and evolving disagreement ([full CG-2 results](benchmarks/CG2_POSTRELEASE_RESULTS.md)) |
| **UCL/2.0 vs structured English** | **UCL 56/56; structured English 48/56** strict-schema answers | UCL: 8/8 valid outputs; English: 7/8. The English malformed response nevertheless contained all 8 correct choices; no observed semantic-accuracy difference ([comparison report](benchmarks/UCL2_VS_STRUCTURED_ENGLISH.md)) |
| **Cold-recipient deception test** | **UCL 32/32; structured English 32/32** | Both resisted the same forged historical recap while preserving real CG-2 concept identities; UCL used more input tokens ([adversarial report](benchmarks/COLD_RECIPIENT_ATTACK_RESULTS.md)) |

The [L25 report](benchmarks/AUTONOMOUS_25.md) explains why most originally rejected *attempts* failed an unnecessary auxiliary summary-length rule, **not the UCL language**. The [L50 results](benchmarks/AUTONOMOUS_50_RESULTS.md) report the actual remaining syntax/provider failures, packet growth, cost, and a transcript-level reasoning analysis.

**Three post-release investigations extend the evidence beyond message transport.** [CG-2](benchmarks/CG2_POSTRELEASE_RESULTS.md) documents six newly authored concepts and actual model-generated challenges between their meanings; [the direct comparison](benchmarks/UCL2_VS_STRUCTURED_ENGLISH.md) measures exact-schema retrieval against a structured-English baseline; and [the cold-recipient deception test](benchmarks/COLD_RECIPIENT_ATTACK_RESULTS.md) verifies that independent models could preserve six real CG-2 concept identities despite a misleading external recap. These are different tasks, not interchangeable success rates. Structured English achieved the same observed factual correctness in both comparative tests and used substantially fewer input tokens; one malformed response explains the strict-score difference in the direct comparison.

**Interpretation:** These results provide preliminary evidence of self-contained transport, concept identity retention, independent model authorship, scoped disagreement, and robust retrieval in the particular tested tasks. They **do not establish UCL's general superiority over structured English**, independently prove comprehension, or verify speculative philosophical claims. Differences in format compliance must not be confused with differences in semantic understanding; relative efficiency and usefulness require broader, task-specific research. Productive disagreement is not a failure.

## What is included—and what is optional?

The **core language** has a typed expression grammar, custom definitions, precise discourse references and deterministic packet integrity. The **portable structural authoring profile** adds embedded field-shape guidance, acknowledgement instructions and independently checkable envelope integrity. The optional **FR-1** role annotations label an expression as a hypothesis, example, counterexample, quotation or question; this role is metadata, not proof. Optional **SVP-1** semantic review is decentralized and advisory: a qualified reviewer can report potential contradictions or attribution concerns without rewriting original text. Optional history condensation is not used in the live L25/L50 endurance runs; optional encrypted transport remains experimental and is not part of the default plaintext format.

All of these mechanisms preserve the existing 11 core glyphs; no authority server is introduced.

## Documentation

- [**UCL/2.0 normative specification**](docs/UCL_2_0_SPECIFICATION.md) — stable wire format, hashes, conformance
- [Inner typed grammar](docs/SPECIFICATION.md) — original core glyphs and expression semantics
- [Research and experimental extensions](docs/UCL_2_0_DEVELOPMENT.md) — historical research and optional features
- [Portable authoring design](docs/UCL_2_0_SPECIFICATION.md) — authoritative self-contained envelope and checks
- [Release audit and evidence](docs/UCL_2_0_RELEASE_READINESS.md) — evidence, limitations, audit history
- [AI-facing guide](README_AI.md) — model-oriented reading and composing instructions
- [UCLBench](benchmarks/README.md) — reproducible tests and experimental methodology
- [Project rationale](docs/PROJECT.md) · [Governance](GOVERNANCE.md) · [Apache-2.0 license](LICENSE)

## Contributing and responsible claims

Please open an issue or pull request with a **specific protocol ambiguity, interoperability example, failing conformance vector or well-scoped extension proposal**. Preserve the distinction between syntactic validation, exact-reference fidelity, independently scored communication, and agreement or truth. New symbols need complete typed definitions and immutable identities; changing a definition is not the same as silently changing its meaning under the old ID.

**Project goal:** make long-lived exchanges between independent intelligences more precise, inspectable and interoperable—while keeping the language decentralized, readable and open to original ideas.
