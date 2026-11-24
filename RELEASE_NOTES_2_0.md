# UCL/2.0 — stable public release notes

**Universal Cognitive Language 2.0** is the first public stable, self-contained **Portable** interchange profile for independent cognitive systems. The earlier standalone UCL/1.0 transport is retired as the project's default release interface. Its 11 original core glyphs and typed inner grammar remain unchanged and are embedded in the 2.0 packet.

## Highlights

**One ordinary `.txt`, no central server.** A Portable message includes the operative language guide, typed concept definitions, immutable SHA-256 IDs, all required claims and historical acts, acknowledgements, current reasoning and fully embedded authoring rules. A recipient need not trust a hosted language dictionary or execute any embedded program to understand the message.

**Stable wire format.** The exact envelope identifier is `UCL/2.0-SAP1-PORTABLE`. The stable 2.0 rule and envelope checksums use distinct canonical domain prefixes. The Python reference validates outer and inner content; an independent zero-dependency JavaScript checker validates the pinned Portable envelope and its documented subset of the inner language.

**Independent model authorship.** Models can introduce properly typed symbols with new identities, formulate new relationships, distinguish quoted or hypothetical content, precisely scope acknowledgement to earlier claims and repair their own invalid authored syntax. The host may calculate hashes and mechanically append retained history, but does not silently rewrite a model's intended meaning.

**Conversation acknowledgements.** Participants can separately communicate received, understood, accept, reject, qualify, clarify, adopt-for-discussion, propose-revision, withhold-judgment and withdraw-own-claim. Agreement is not conflated with understanding. A valid expression is not automatically a true claim.

**Extensions remain optional.** Indexed FR-1 roles (hypothesis, example, counterexample, quotation or question) and decentralized SVP-1 semantic observations are optional; they do not change the core glyphs, serve as a central judge, or magically prove truth. Optional history condensation must explicitly disclose omitted information. The default is readable plaintext; optional encryption remains experimental, with secrets exchanged outside the packet.

## What was demonstrated before release

Authentic Clarke/Hal live tests included six freshly invented immutable concepts (CG-1, 6/6 delivered), formal relations built on those concepts (RR-1, 6/6), 23/25 delivered messages in the L25 trial and **48/50 delivered messages in the L50 trial** (45/50 first try). The last L50 validated message preserved **91 historical acts** and all original concept IDs, without silent condensation. The [full L50 report](benchmarks/AUTONOMOUS_50_RESULTS.md) identifies genuine syntax, formatting and output-token failures and the limits of this single exploratory conversation.

The 25-turn trial's high initial rejection count was dominated by an **arbitrary minimum length applied to an auxiliary interpretation string**—not a rule of UCL. The restriction was removed for the subsequent L50 trial. Neither trial proves perfect AI comprehension or superiority over ordinary or structured English.

## Install and use

Python 3.12+ (standard library) and optional Node.js (built-in modules only):

```bash
python tools/sap_portable.py encode examples/cross_model_conversation_8_turns.json ucl2.txt
python tools/sap_portable.py check ucl2.txt
node tools/check_ucl_portable.js ucl2.txt
python tools/sap_portable.py decode ucl2.txt restored-inner.json
```

See [UCL/2.0 specification](docs/UCL_2_0_SPECIFICATION.md), [README](README.md), [AI guide](README_AI.md), [UCLBench](benchmarks/README.md), and [license](LICENSE).

## Release scope and limits

This is a **full stable 2.0 protocol profile** for the specified Portable envelope and typed inner packet; it is **not** a claim of comprehensive AI reasoning accuracy or a third-party security certification. SHA-256 self-checks are not authentication. The independent JavaScript implementation's documented subset is not a full optional proof/model interpreter; Python remains the complete structural reference. Earlier research packets labeled `DRAFT` are archived experimental materials, not wire-compatible 2.0 stable messages. No central registry, new core glyph or on-wire permission service has been introduced.


## Portable guide and rules fingerprints

| Object | Base64url SHA-256 without padding |
|---|---|
| Inner guide | `pXMaoI0O-dSKfj1D3XFlzl-Wvd9CDdLdOS4R1fNyQ5U` |
| SAP-1 structural rules | `yrac3Zj4lyiGfI6944ZsmFSLdL-VPiXPnVZEPVKEh-k` |

The guide fingerprint hashes the UCL-CJSON-1 bytes of `packet.guide` directly. The structural rules fingerprint hashes the ASCII prefix `UCL-SAP1-RULES-2.0` followed by one LF byte and the UCL-CJSON-1 bytes of `structural_rules.rules`. Obtain the expected fingerprints from a trusted copy of these notes. The fingerprints identify the rules and guide. Sender authentication requires separate evidence.
