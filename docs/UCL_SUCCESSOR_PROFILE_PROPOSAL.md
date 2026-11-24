# UCL Portable successor profile proposal

Status: design draft for a possible future Portable revision. Portable is the single interchange format. This document defines no alternate format.

## State-first export

Start with the [local state ledger](UCL_STATE_LEDGER.md). A future Portable revision could export a short reader header, the derived ledger, the pinned guide and rules, then the complete sequence of contribution records. Keep it in one UTF-8 JSON document. The header identifies the format, head, declared history coverage, and trust boundaries. Conversation prose remains speaker data. A verifier must recompute an embedded ledger from the retained records and reject a mismatch. Its concise terminal rendering can guide navigation, while the original records remain available for interpretation and quotation.

Append-only applies to the contribution records. Export regenerates the changing header and ledger, and may rewrite the file. Validate that the prior records form an unchanged prefix before exporting a continuation. If a writer uses a cached ledger, verify it against a complete replay before delivery. An exporter operating on a shared destination should check the expected head before replacing the file.

## Conversation commitments and concept relationships

- A temporary commitment should name its speaker, an exact claim and path, and the act that starts its discussion scope. A conditional commitment should carry a typed antecedent and take effect only after that speaker records its activation. The validator checks the references and types. Participants still decide whether the condition holds.
- [Portable 2.3](UCL_2_3_SPECIFICATION.md) implements exact ACK retraction. A future join receipt could bind to the exact packet digest and record the participant's stated readiness.
- A proposed refinement should link two immutable definition IDs and name its proposing act. Both definitions remain resolvable. A participant can explicitly adopt a refinement without changing how earlier expressions are interpreted.
- Parallel replies can name a common parent and exact target paths. A comparison can show divergent replies. A reconciliation act should cite both heads and make choices about conflicting bindings or commitments explicit.

The existing gzip index, exact lookup and `--keep-act` support a working set inside one file. Measure how often newcomers need older blocks before defining another recency tier. Plaintext audience annotations can guide reading and are visible to every recipient. Actual access control would require encryption and key management.

## Rule modules

Use a new profile identifier with a pinned interpretation core and a versioned extension map. Each extension declares its identifier, version, criticality, and value. An unknown critical extension makes the message uninterpretable under this profile. An unknown advisory extension can be skipped for interpretation, but its original value remains part of the signed message and must survive a forwarding round trip. Updates to examples, preflight advice, and semantic-review guidance should not require a grammar revision.

A conversation may propose a rule module using its immutable identifier and explicitly record who adopts it, for which acts, under what conditions. Include all required modules in the full Portable message. A proposal or adoption is itself a conversation act. It cannot upgrade a receiver's supported grammar or silently change the interpretation of earlier acts. Unknown execution semantics require an explicitly supported critical extension.

## Signatures and attribution

Define a domain-separated canonical signing payload that commits to the format and profile, packet hash, rules and module identities, extension values and criticality, and any chain metadata and formula roles. Exclude the signature container and the derived envelope checksum from the signing payload. Cover the signer's key identifier and attestation scope. Validate all committed fields before reporting a signature as valid.

The receiver needs an independently trusted binding between a verification key and the identity it represents. A public key carried by the envelope is a discovery hint until that binding is established. An authenticated mode must reject unsigned handoffs or handoffs without the required signature, even if the same recipient also supports a separate unsigned mode.

Distinguish a signature over a delivered snapshot from an author's attestation of a particular contribution. A snapshot signature covers the bytes of the retained history. A contribution signature commits to that record's act, acknowledgements, definition additions, definition retirements, claim bindings, and any other changes supplied by that author. Cover the previous record hash and sequence as part of the signed record. A later snapshot signer does not inherit authorship of older records.

The genesis record declares the conversation's key roster and signature policy. For an authenticated conversation, verify each required contribution signature against the key authorized for that author at that point in the chain. An authenticated withdrawal must be authorized by the identity responsible for the target act. Report integrity, signature verification, and external identity binding separately. Agree on key registration, rotation, and revocation before enabling authenticated authoring. Unsigned conversations can use the same file structure with an explicit unauthenticated policy.

Formula roles belong at expression scope. A single act may quote one expression and use a second as a counterexample. Bind each authenticated role to its expression, declaring author, and attestation. Any future lossless re-encoding workflow must retain the annotations and their attribution.

## History continuity

Give every contribution a domain-separated hash over its canonical payload, which includes its conversation identifier, sequence number, previous record hash, and complete contribution. Genesis starts the sequence and establishes the conversation identifier and initial policy. The head is the final record hash. A full replay can verify internal linkage, sequencing, and replayed state from the included genesis. Compare a trusted earlier head against the corresponding retained record to establish continuity with a previously seen conversation. Report forks when competing successors to the same record are observed. An unanchored chain does not establish that its genesis is the recipient's expected starting point.

Start with fully retained history and leave hash-only stubs out of the first revision. Any future change to history retention needs explicit omission records and a dependency rule protecting exact targets and the context required to interpret them. A content hash can verify an original supplied later. Packet size and act-count limits remain independent of chain design.

## Definition identities and local inspection

[Portable 2.1](UCL_2_1_SPECIFICATION.md) binds every typed domain dependency into the definition ID. Domain mode and membership are part of domain identity. The current dependency graph has domains as leaves. Define the handling of cycles before permitting recursive dependencies.

Portable 2.1 supports named aliases and vocabulary records in retained acts. Speakers can retire a definition for their own use and suggest a successor without removing its binding. They can attach typed examples and counterexamples to existing definitions. A future authenticated revision should attest to these vocabulary records with their parent acts.

Keep the guide and required rule modules embedded in every delivered packet. Local tools may derive a concept index or a shorter view for a particular reply from the complete packet. These views are for inspection within the recipient's workflow. The canonical handoff remains the complete Portable packet.

## Requirements before implementation

Publish cross-language vectors for canonical signing bytes, attachment and forwarding of advisory extensions, critical-extension rejection, signature removal, changed prior contributions, forks, ledger mismatches, withdrawal authorization, role attribution, dependency changes, and required embedded guides. Include existing Portable packets as compatibility fixtures. Agree on the attestation and dependency schemes before assigning a wire identifier.
