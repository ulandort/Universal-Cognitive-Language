# UCL 2.4.1

This tooling patch packages the packed-conversation walkthrough, briefing improvements, and live replay files. The Portable format remains `UCL/2.4-SAP1-PORTABLE` with the `UCL/1.4` guide. Existing 2.4 packets retain their IDs and checksums.

- **Briefing v2.** `ack_id` names the acknowledgement, `author_act` names the turn that authored it, and `source_act` names the target’s origin. These labels apply to `inspect --handoff`.
- **Recorded open issue.** The briefing quotes the last recorded open issue and points to its location in the packet. It returns null when none was recorded.
- **Packed join walkthrough.** The README leads with a 2,000-act sample and a seeded reply starter. The scorecard includes an exercise in which a newcomer must request a missing source.
- **Replay files.** Download `ucl24-missing-source-relays.zip` to inspect the two conversations, exact model prompts, first drafts, and validation scorecards.

Run `python src/ucl.py --version` to see the tooling release, packet format, and guide version. Use `sha256sum -c SHA256SUMS.txt` to verify the release downloads.

[Packed walkthrough](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.4.1/README.md#join-a-packed-conversation) · [Portable 2.4 specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.4.1/docs/UCL_2_4_SPECIFICATION.md)
