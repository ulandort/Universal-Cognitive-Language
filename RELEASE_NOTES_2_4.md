# UCL 2.4.0 Portable

See the [2.4.1 release notes](RELEASE_NOTES_2_4_1.md) for the current tooling release.

Portable 2.4 makes it easier to join a long-running conversation. Every packet carries the `UCL/1.4` guide with a worked example that distinguishes typed formulas, prose reasoning, and retained turn references. The full conversation still travels in one `.txt`.

- `inspect --handoff` produces a briefing with Current State, the exact latest act, a selected claim branch, and any archived acts you request. Packed briefings open only the requested archive blocks.
- `template --seed-formula` supplies a valid typed starting point for a scoped reply. The author still decides the reasoning and the stance.
- `diff --compact` shows a bounded summary of new acts, concepts, stance changes, and retractions with their source IDs.
- `upgrade` reissues older packets in 2.4. A 2.3 upgrade preserves the definition IDs and conversation records, including retractions.

## Try the packed example

Download `ucl-2.4-archive.txt` and use the 2.4 checkout.

```sh
python src/ucl.py inspect ucl-2.4-archive.txt --handoff --claim theory --path 1 --include-act t185
python src/ucl.py template ucl-2.4-archive.txt --speaker "New participant" --claim theory --path 1 --seed-formula
```

In the release-candidate test, Clarke used the generated briefing and seeded template to continue the packed archive to act 2,001. It cited the exact earlier records and passed both validators on its first draft. [Live test](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45503699604)

The release also includes the two-turn Quickstart, the Challenge, and a worked retraction. Validate the downloaded bytes with `sha256sum -c SHA256SUMS.txt`.

[Portable 2.4 specification](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.4.0/docs/UCL_2_4_SPECIFICATION.md) · [Full handoff walkthrough](https://github.com/ulandort/Universal-Cognitive-Language/blob/v2.4.0/docs/UCL_HANDOFF_TRIAL.md)
