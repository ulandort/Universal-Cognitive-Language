# UCL Portable successor profile proposal

Status: design draft. The profile has no assigned wire identifier. The current UCL/2.0 Portable specification remains the interchange standard.

## Rule modules

Use a new profile identifier with a pinned interpretation core and a versioned extension map. Each extension declares its identifier, version, criticality, and value. An unknown critical extension makes the message uninterpretable under this profile. An unknown advisory extension can be skipped for interpretation, but its original value remains part of the signed message and must survive a forwarding round trip. Updates to examples, preflight advice, and semantic-review guidance should not require a grammar revision.

A conversation may propose a rule module using its immutable identifier and explicitly record who adopts it, for which acts, under what conditions. Include all required modules in the full Portable message. A proposal or adoption is itself a conversation act. It cannot upgrade a receiver's supported grammar or silently change the interpretation of earlier acts. Unknown execution semantics require an explicitly supported critical extension.

## Signatures and attribution

Define a domain-separated canonical signing payload that commits to the format and profile, packet hash, rules and module identities, extension values and criticality, and any chain metadata and formula roles. Exclude the signature container and the derived envelope checksum from the signing payload. Cover the signer's key identifier and attestation scope. Validate all committed fields before reporting a signature as valid.

The receiver needs an independently trusted binding between a verification key and the identity it represents. A public key carried by the envelope is a discovery hint until that binding is established. An authenticated mode must reject unsigned handoffs or handoffs without the required signature, even if the same recipient also supports a separate unsigned mode.

Distinguish a signature over a delivered snapshot from an author's attestation of a particular contribution. A snapshot signature covers the bytes of the retained history. Authorship of each prior act requires a retained author attestation or equivalent evidence. An authenticated withdrawal must be authorized by the identity responsible for the target act. Define key rotation and revocation separately before deployment.

Formula roles belong at expression scope. A single act may quote one expression and use a second as a counterexample. Bind each authenticated role to its expression, declaring author, and attestation. Any future lossless re-encoding workflow must retain the annotations and their attribution.

## History continuity

For a signed handoff, commit to a conversation identifier, sequence number, and previous signed handoff identifier. The verifier needs the prior trusted handoff or an independently trusted checkpoint. Compare retained act content, definitions, claim bindings, and acknowledgement records against that predecessor. Validate append-only rules separately from the chain link. Report forks when competing handoffs are observed, and report continuity as unverified when the necessary predecessor is unavailable.

Start with fully retained history. A future explicit condensation profile should identify omitted act IDs or ranges, preserve the exact retained claims and their dependencies, and state how the recipient can obtain the originals. An act hash can verify an original supplied later. The hash alone cannot reproduce omitted content. Packet size and act-count limits remain independent of chain design.

## Definition identities and compact delivery

Use a new hash domain for dependency-closed identities. Bind each reference in a definition to the ID of the definition it resolves to in that packet. For example, predicate argument sort D must bind the identity of D. Specify whether domain membership is part of domain identity or separate instance data. Define the handling of cycles before permitting recursive dependencies. Keep legacy IDs resolvable as legacy IDs and version any migration mapping.

Keep full Portable delivery as the default. A separate opt-in profile for known peers may refer to exact guide or module hashes. A receiver missing a required object must request a fully embedded version before interpreting the message. A local context view can reduce model input independently while retaining a complete source packet for verification.

## Requirements before implementation

Publish cross-language vectors for canonical signing bytes, attachment and forwarding of advisory extensions, critical-extension rejection, signature removal, re-signed snapshots with changed prior acts, role attribution, dependency changes, and missing-guide fallback. Include old Portable packets as compatibility fixtures. Agree on the attestation and dependency schemes before assigning a wire identifier.
