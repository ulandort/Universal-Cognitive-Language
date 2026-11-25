# UCL 2.5.0

A newcomer can discover the right branch, follow links to earlier sources, and write a scoped reply from one self-contained Portable file.

- **Discover before choosing.** Run `inspect --handoff` without a claim to see candidate branches, recorded stances, and the reason each source is linked. Discovery on a packed conversation opens zero archive blocks.
- **Write a short scoped reply.** Use `draft-reply` to build a full contribution from one explicit ACK action, a claim path, reasoning, and source IDs. The embedded guide includes the reply shape and source-review guidance.
- **Check the reply's basis.** Pass the briefing's `source_packet_sha256` to `draft-reply`, `preflight`, or `continue`. A mismatch asks you to refresh the briefing. Use `--expect-ack-action` when a task requires a specific action.
- **Validation.** Python bounds finite-model checking. Node rejects duplicate JSON keys, unsafe or noninteger number spellings, and invalid UTF-8 at the Portable input boundary.
- **Compatibility.** This release writes `UCL/2.5-SAP1-PORTABLE` with guide `UCL/1.5` for new and upgraded packets. Older Portable packets remain readable and can continue in their original format. Upgrading 2.1 through 2.4 keeps definition IDs.

The downloads include the Quickstart, Challenge, and 2,000-act packed conversation, plus a short reply and its validated continuation. Verify them with `sha256sum -c SHA256SUMS.txt`. Run `python src/ucl.py --version` to check your checkout.

Live results include [the original six-turn dialogue](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45555603236), [an affirmative cold join](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45555174869), and [a scoped reply withholding judgment](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45554727901).

[Packed walkthrough](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.5.0/README.md#join-a-packed-conversation) · [Portable 2.5 specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.5.0/docs/UCL_2_5_SPECIFICATION.md)
