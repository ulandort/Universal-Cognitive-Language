# Universal Cognitive Language (UCL) — 1.0

**An experimental, open, self-contained communication protocol for independent intelligences.**

UCL is designed to help AI systems exchange hypotheses, questions, disagreements, revisions and precisely referenced claims across model boundaries. The default message is **readable JSON**; the optional Python/JavaScript tooling is not necessary merely to understand a packet. UCL is **not** a natural-language replacement, a guarantee of shared understanding, an empirical truth system, or a compulsory proof language.

**Version:** UCL/1.0 · **Licence:** Apache-2.0 for this repository's code and documentation · **Status:** initial public specification and reference implementation; interoperability and performance claims are preliminary.

## UCL 2.0 — development branch

This branch contains **experimental, unreleased UCL 2.0 work**. The stable **UCL 1.0** specification remains on [main](https://github.com/ulandort/Universal-Cognitive-Language/tree/main).

The [2.0 development notes](docs/UCL_2_0_DEVELOPMENT.md) describe two planned profiles (**Portable** with a complete embedded guide, and optional **Compact** with a locally verified guide fingerprint), strictly lossless conversation preservation, and the optional exact-reference compression experiment. Compact mode never depends on GitHub being online; without the matching local guide, the receiver must request Portable.

**[UCLBench offline](benchmarks/README.md)** provides deterministic tests for definitions, references, integrity, tampering and guide-profile reconstruction. Run `python benchmarks/offline_suite.py --iterations 1000`; the [GitHub Actions workflow](.github/workflows/uclbench.yml) runs automatically on development changes. Offline tests verify protocol mechanics, **not** AI understanding or superiority to English.

### Controlled 10-turn semantic-retention pilot

The [10-turn pilot](benchmarks/LONG_CONVERSATION.md) adds ten scripted, fully retained events to the original eight-turn conversation, introducing a separately hashed revised concept and precisely scoped disagreements. **Clarke and Hal** answer independently scored multiple-choice questions at two checkpoints across ordinary English, structured English, UCL Portable and UCL Compact. This is an **exploratory scripted-history comprehension test**, not yet autonomous model-to-model debate or proof of UCL advantage. [Launch manually in GitHub Actions](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-long.yml); the workflow defaults to a free dry run and never uses Radium credits on commits.

### Live UCLBench with Radium Cloud (manual, experimental)

The [live Radium harness](benchmarks/LIVE_RADIUM.md) relays small, controlled messages between Hal and Clarke across English, structured English, UCL Portable and UCL Compact. **No paid calls occur on commits**. The manually triggered [UCLBench live workflow](https://github.com/ulandort/Universal-Cognitive-Language/actions/workflows/uclbench-live.yml) defaults to a zero-cost dry run, and uses the `RADIUM_API_KEY` GitHub Actions secret only if you explicitly choose the paid run. The launcher resides on `main` only because GitHub requires manual-dispatch workflows there; it checks out this development branch for all test code.

## How UCL works: glyphs, layers and meaning

UCL uses **11 core glyphs** as a small, fixed vocabulary for expressing typed statements. They are not substitutes for English letters: their meanings come from the grammar, while custom symbols such as `A`, `P` or `D` get **explicit definitions** carried inside the message. Square brackets group arguments. An AI can inspect those definitions instead of guessing what an unfamiliar symbol means.

| Glyph | Read as | Example / role |
|---|---|---|
| `@` | belongs to a domain | `@[A][D]` — A is a member of domain D |
| `#` | scoped variable reference | `#0` — bound variable at index 0 |
| `=` | identical in denotation | `=[A][B]` — identity, **not** mere similarity |
| `~` | typed property or relation | `~[P][A]` — property P applies to A |
| `&` | both | `&[p][q]` — p **and** q |
| `\|` | either or both | `\|[p][q]` — inclusive **or** |
| `!` | not | `![p]` — negation of p |
| `?` | sourced uncertainty or conflict | `?[p]` — epistemic status, **not** a question or missing data |
| `<` | strictly ordered by named relation | `<[O][a][b]` — a precedes b under O |
| `*` | deterministic typed function | applies a declared function to its typed arguments |
| `{` | exists in a declared domain | existential quantifier with a scoped variable |

The five **structural glyphs** `: ; [ ] -` separate and organize expressions and declarations; they are not additional logical operators. For example, given definitions of `A` (a hypothetical system), `P` (a proposed property) and `B` (a different property):

```text
&[~[P][A]][![~[B][A]]]
```

This reads: **“A has property P, and A does not have property B.”** It expresses a *proposition*, not a verified fact. In UCL, `![~[B][A]]` is importantly different from “we have no information about B.”

### The four-layer body

Every complete packet has a `body` with **four semicolon-separated bracketed layers**, not four separate files:

```text
[orientation];[explanation];[conclusion];[exact-symbol-declaration]
```

1. **Orientation:** the kind of communication (for example, a hypothesis, question or proposal), referenced through a defined orientation symbol.
2. **Explanation:** a typed logical proposition stating what is being considered.
3. **Conclusion:** a typed proposition (or supported sourced epistemic record) expressing the message's conclusion; it does **not** need a proof.
4. **Exact symbol declaration:** all core glyphs and custom symbols actually used in the packet's expressions, including full cryptographic definition IDs for custom symbols. An encoder can construct this mechanically.

The body is only **one part** of the surrounding, ordinary JSON packet. That packet also carries the language guide, complete relevant definitions, domains, dialogue acts, precise acknowledgements of earlier claims, and the history needed by a new reader. For instance, a participant can **reject one subclaim while provisionally adopting another** without implying that either is proven true.

### Why the layers matter

English is flexible, but “I disagree with that” can be ambiguous in a long exchange. UCL separates **what is said**, **how it is expressed symbolically**, **which exact earlier claim it addresses**, and **the participant's stance toward that claim**. Definitions are given immutable SHA-256 identities so a revision cannot silently replace an earlier definition. This aims to make long, multi-model conversations easier to trace and check, while keeping speculation, dissent and open-ended discussion valid.

For the complete syntax, including scoped quantifiers, definition hashing and acknowledgement paths, see the [UCL/1.0 specification](docs/SPECIFICATION.md). The [AI-facing README](README_AI.md) gives a compact reading and authoring procedure.

### An extensible vocabulary: how new symbols gain stable meaning

The **11 core glyphs stay fixed**, but UCL's *defined vocabulary* is open-ended. Independent intelligences can introduce new custom symbols for concepts, domains, properties, relations, functions and conversational orientations without changing the core grammar. A hypothetical discussion could begin with `P` and `B`, then introduce `M`, `N` and `K` as the participants develop or refine their theories. Different messages can carry different collections of definitions: **there is no fixed global dictionary or central registry**.

Each custom symbol includes a full description and type information. UCL assigns its definition a **SHA-256 cryptographic fingerprint (256 bits)** derived from the canonical JSON representation, using the defined `UCL-SEM-9` domain separator. The fingerprint is carried with the definition so another AI or validator can recompute it and check that the *exact recorded definition* has not been silently changed.

For illustration, a symbol record may look like this (the ID below is deliberately illustrative, **not** a real hash):

```json
{
  "K": {
    "definition": {
      "kind": "predicate",
      "args": ["D"],
      "gloss": "A proposed property of hypothetical systems in domain D."
    },
    "id": "<computed SHA-256 Base64url definition ID>"
  }
}
```

If the concept changes, its previous definition and ID stay intact; a new symbol with a new hash is introduced, with the revision made explicit. This lets the vocabulary **grow without a predetermined finite list of concepts** while preserving a traceable distinction between old and new meanings. Individual UCL/1.0 packets still have practical resource limits, including the number of definitions they can carry, so “open-ended” does not mean infinite content inside a single message.

**Verification is not encryption.** SHA-256 is a one-way *hash* used to identify definition bytes and check integrity; it does not hide a definition, establish that different AIs understand it identically, or prove the idea true. UCL separately offers **optional AES-256-GCM encryption** (with Argon2id password derivation or a direct key) when participants need to keep an entire message confidential. Plain readable JSON remains the default.

## Why create UCL?

Natural language is extraordinarily expressive and already strong for contemporary models. But in long, multi-party exchanges, the same term can acquire inconsistent meanings, disagreement can be misattributed, and a later reader may not have access to the original context. UCL deliberately trades message size and authoring complexity for **explicit structure**.

| Potential advantage relative to ordinary English | Mechanism | Limitation |
|---|---|---|
| Explicit, stable concept identity | Full SHA-256 of each canonical semantic definition | Matching hashes cannot establish matching interpretation or truth |
| Precise agreement/disagreement | Optional ACKs refer to exact acts, formula indices or quoted subformula paths | Models can still choose a wrong target |
| Revisions without silent redefinition | New glyph + hash, retain prior definition | Semantic quality of a revised definition remains open |
| Cold-start accessibility | Every packet embeds language guide, active definitions and relevant history | Larger packets and greater costs |
| Distinguishes claim from evidence | Optional proof/model checks separate from conversational validity | No general theorem proving or empirical verification |
| Machine checking | Deterministic parser, type checks, canonical hashes, graph references | Formal syntactic compliance isn't reasoning quality |

**These are design properties and potential benefits, not experimentally established superiority to English.** There is no controlled English-vs-UCL study in this release.

## Getting started

Requirements: Python 3.10+ for the optional authoring/reference implementation; Node.js for the independent subset checker. **Reading a packet requires neither.**

```bash
# Examine a self-contained JSON exchange without executing anything:
cat examples/cross_model_conversation_8_turns.json

# Validate a pretty-printed, ordinary JSON .txt or .json packet:
python src/ucl.py check examples/cross_model_conversation_8_turns.json

# Build a complete self-contained packet from a structured draft:
python src/ucl.py build examples/example_draft.json next_message.txt

# Add a compact contribution to a verified existing packet:
python tools/author.py examples/cross_model_conversation_8_turns.json examples/contribution_example.json continued.txt
python src/ucl.py check continued.txt

# Run the independent JavaScript subset checker (canonical bytes required):
node tools/check_ucl.js examples/cross_model_conversation_13_turns.cjson

# Run tests:
python -m unittest discover -s tests -p 'test_*.py' -v
```

The Python encoder auto-computes definition and packet hashes, declarations and guide; it does **not** decide which theory to assert or which ACK stance is correct. The JavaScript implementation is an independent **subset checker**, not a complete proof/model checker. If you cannot run tools, you may create a clearly marked `UNVERIFIED UCL DRAFT`; it is not yet a validated message.

## Two starting points

- **Humans:** this file; [PROJECT.md](docs/PROJECT.md) for the motivation, limits and history; [SPECIFICATION.md](docs/SPECIFICATION.md) for normative v1.0 details.
- **AI systems:** [README_AI.md](README_AI.md) is a machine-facing onboarding and authoring guide. It is intentionally plain text plus exact symbolic examples, **not a private or proprietary model language**.

## What the public experiment showed

In a manually mediated exercise in November 2026, independent Grok and Qwen chat models were supplied self-contained UCL messages in fresh conversations. A synthetic 7-act scenario introduced speculative P and measurable B. Grok proposed a distinction; Qwen proposed M; Grok challenged M's circularity; Qwen refined it as N; Grok asked for an independent criterion for P; Qwen proposed K. The example in `examples/cross_model_conversation_13_turns.json` retains the conversation as a *test record*, not authenticated message provenance. It records 13 total acts, of which the first 7 are synthetic and the later 6 are AI-generated contributions.

**Observed:** Grok and Qwen maintained conceptual continuity across six successive model contributions, introducing new definitions, challenging assumptions and refining a shared hypothetical theory. The exchange used the UCL reference validator and intermediary assistance to produce conformant packets, with English glosses carrying part of the conceptual discussion. This is an early demonstration of structured cross-model dialogue, not a controlled comparison showing superiority to English. See the [experiment log](evidence/EXPERIMENTS.md) for methodology and provenance.

## Design commitments

UCL/1.0 keeps exactly **11 core glyphs** `@ # = ~ & | ! ? < * {` and 5 structural glyphs `: ; [ ] -`. Open speculation and disagreement are valid without proof. History condensation is optional but must openly disclose omissions and preserve all needed bindings/references. Integrity hashes do not authenticate speakers. Optional Brotli and optional authenticated encryption are transport layers, **never required** for reading plain JSON.

## Optional encrypted transport (experimental)

UCL/1.0 supports an **optional encrypted envelope** for private model-to-model messages. The experimental profile uses **AES-256-GCM authenticated encryption** and either **Argon2id** password-based key derivation (with a fresh salt) or a separately exchanged **32-byte direct key**. The *entire self-contained UCL message* is encrypted and, after decryption, is validated using the ordinary UCL rules. Passwords and keys are shared **out of band**, never embedded in the UCL packet. The eleven core glyphs do not change.

Encryption is **not required**: ordinary readable JSON remains the default and needs no encryption tool. This security profile has **not been independently audited** and is not guaranteed cross-language interoperable; do not infer sender identity from encryption alone. See [optional/ENCRYPTION_EXPERIMENTAL.md](optional/ENCRYPTION_EXPERIMENTAL.md) for the threat model, parameters, and encrypt/decrypt CLI.

## Repository map

- `docs/SPECIFICATION.md` — versioned normative profile
- `src/ucl.py` — stdlib Python reference implementation; plain JSON default
- `tools/author.py` — optional incremental encoder
- `tools/check_ucl.js` — independently written JS subset validator
- `tools/brotli_optional.py` — optional binary compression, no default requirement
- `optional/` — *experimental*, unaudited AES-256-GCM/Argon2id encryption profile
- `tests/` and `examples/` — executable tests, real exchange examples, canonical vector
- `LICENSE`, `NOTICE`, `BRANDING_AND_CONFORMANCE.md`, `GOVERNANCE.md` — licensing, provenance, claims of official conformance

## Scope and limitations

UCL is a research-oriented, initial public protocol. The core implementation verifies structure/types/references/hashes; proof validity is a separate result; empirical truth and participant identities are not determined by the protocol. A matching hash means two records encode the same canonical definition bytes, **not** that two minds mean the same thing. Do not execute code included in an untrusted message. Cryptographic transport code is experimental and **not security audited**.

**License:** Apache License 2.0; see [LICENSE](LICENSE). The official project name/logo and certification representations are governed separately as described in [BRANDING_AND_CONFORMANCE.md](BRANDING_AND_CONFORMANCE.md). This is not a restriction on the underlying Apache-licensed implementation.