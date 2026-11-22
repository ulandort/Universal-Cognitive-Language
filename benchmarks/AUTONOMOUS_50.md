# L50 — 50-turn autonomous UCL continuity and endurance

**Status:** experimental manual workflow, not a completed paid benchmark or release certification. This is **50 NEW turns**, continuing the final genuine L25 result, for an expected **93 fully retained discourse acts** if all new messages validate.

## Original unmodified lineage

L50 retrieves the archive of [paid L25 run 45081092157](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45081092157) (GitHub artifact `14777333599`), selects the **last successfully delivered** handoff from turn 25, checks that it is an independently valid UCL/2.0 Portable packet and pins its exact SHA-256 packet identity:

`KSyyxhhzqja2Kp-K7DGReJfx99l1vcy5wDn-ErwSDm8`.

The seed has **43 retained acts and 39 retained acknowledgements**, because 23 of the scheduled 25 L25 messages were delivered. All six CG-1 model-created definitions retain their original immutable SHA-256 identity. The last speaker in L25 was Clarke, so **Hal begins L50**, followed by alternating Clarke and Hal.

This is not a synthetic reconstruction; every receiver gets the entire independently validated retained history and definition catalog. The original L25 artifact is set to expire December 6, 2026. Archive the authenticated provenance for longer-term reproduction instead of assuming the GitHub-hosted artifact persists.

## Intent and distinctions from L25

1. **Interpretation metadata is advisory, never a message-delivery condition.** A short, absent, null, or non-string interpretation is recorded or skipped, rather than rejecting the independently valid authored UCL contribution. This specifically addresses the 23 L25 rejected attempts due only to an arbitrary minimum 20-character summary requirement.
2. **Actual UCL validation remains strict.** New acts, references, original expression types, exact ACK target paths, immutability, hashes, formal grammar, complete history and self-contained embedded guidance are independently checked before a receiver sees the message. The authoring prompt stresses that target paths use JSON integers: `[0]`, not `["0"]`; the validator never silently converts them.
3. **All history remains fully expanded.** No silent truncation, invented earlier messages or unmarked condensation. Packet growth and original act retention are checked on every delivered message.
4. **Independent dissent is legitimate.** The models are free to challenge, qualify or reject each other's ideas. Conversational disagreement is never a language or protocol failure. Typed formulas are speculative hypotheses unless separately proven; the test does not establish truth.
5. **Every tenth new turn** invites a reference to a substantially earlier message. These are *advisory reasoning/recall probes*, not artificial validation gates; invalid formal references are still disallowed by UCL itself. Responses are preserved for independent semantic review.
6. The initial 43 acts plus 50 additional delivered acts would be **93**, below the current 100-act limit; 39 initial acknowledgements plus 50 would be **89**, below the current 150-ACK limit.

## Boundaries and reporting

- Completion token ceiling: **16,384 per model request**, including any tokens counted as hidden reasoning by the provider.
- Up to two model-owned retries following validation feedback. First-pass and repaired deliveries are separately reported.
- Default estimated spend guard: **$20 USD total**, not a provider-enforced spending guarantee; pre-call reserve prevents initiating new requests once its estimate exceeds remaining cap. API timeouts may still be billable even without usage.
- Maximum serialized packet guard: 900 KB. All generated packets are validated self-contained UCL and checked for original definition and act retention.
- The raw artifact includes all attempts, exact delivered packets, summaries, reference probes, packet sizes and token counts. A complete run does not constitute measured semantic superiority over English or full independent proof of comprehension.
- **Release target remains full public UCL/2.0**; normative JS/Python interoperability and full documentation still require independent verification.

## Manual launch

From the GitHub repository **Actions**, select **UCLBench Autonomous 50-Turn Stress (manual)** on branch `main`; the workflow checks out `develop/2.0`. It **runs free exact-seed tests and a synthetic 50-turn protocol oracle before any paid calls**.

Recommended inputs: `paid_run=yes`, `max_repairs=2`, `cap_usd=20.00`. Use `paid_run=no` for a free validation-only check. The workflow never executes paid API requests on ordinary pushes.
