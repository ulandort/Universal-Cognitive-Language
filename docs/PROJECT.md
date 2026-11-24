# UCL — purpose, promise, and history

UCL (Universal Cognitive Language) began as an exploration of whether independent AI systems can communicate theories and disputes through a deliberately structured, open language. Rather than enforcing proof, it supports claims that can be tentative, wrong, metaphorical or contradictory, while making their reference targets machine-checkable.

## Why not just English?

English communicates nuance exceptionally well. UCL seeks to reduce *certain* ambiguities: immutable meaning records, explicit scoping, exact claim references, declared uncertainty and disclosed missing history. Long dialogues can become easier to audit. UCL could be useful for multi-agent research debates, preserving definitions across independent systems, and checking who challenged which premise. It is not known to improve reasoning accuracy, token efficiency, or understanding compared with English or structured English/JSON. The current default uses English glosses alongside symbols; it is deliberately hybrid.

## Development outline

During iterative 2026 previews through v0.21 the protocol gained open symbolic domains, optional formal proofs, typed function/predicate signatures, proof/message separation, standalone context, immutable definition identities, revisions, explicit ACKs targeting subclaims, exact quotation and nested viewpoints, safe-history disclosures, and cross-language canonicalization tests. Early preview transport used Brotli/Base64; external model testing showed that plain JSON is substantially more accessible to text interfaces and became the v1.0 default. UCL/2.1 builds on that choice with a self-contained Portable envelope, named aliases, and an embedded authoring template. UCL/2.2 adds scoped retrieval and optional lossless gzip archives within the same file. UCL/2.3 adds exact stance retraction, current-state inspection, and packet diffs. Optional AES-256-GCM/Argon2id encryption remains an experimental outer transport feature.

## External experiment (not controlled)

A synthetic seven-act debate introduced hypothetical P and B. Fresh sessions with Grok and Qwen interpreted the packet and advanced ideas: proposed M, questioned whether M's separation was circular, revised M as N, questioned whether N decided P, and proposed K as a potential fixed-point criterion. Six contributed acts t8–t13 are kept in a single self-contained example. In each exchange an intermediary repaired machine-readable details. All conversational outcomes therefore qualify as *validator-assisted*, not independent end-to-end protocol conformance. Neither models' claimed authorship nor hypotheses were cryptographically authenticated. The debate does not establish scientific facts about cognition.

## Cautious claims

Potential benefits must be compared in rigorous matched trials against English and structured English, including error rates, lost references, repairs, output tokens, new conceptual insights and verifier interventions. Proof-certificate presence does not guarantee that premises are true. This initial v1.0 fixes a baseline for independent reimplementation; it is not a declaration that all security, reasoning, or interoperation questions have been solved.