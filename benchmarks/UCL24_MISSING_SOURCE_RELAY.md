# Portable 2.4 missing-source relay

This test asked whether a newcomer would request an omitted archived act, use it when provided, and hand off a reply that a second newcomer could read. It used two synthetic 2,000-act conversations, each carried in one packed Portable 2.4 file.

| Conversation | Initial reader | Fresh recipient | Evidence status expected from act `t185` |
| --- | --- | --- | --- |
| Research claim | Clarke 1.0 | Hal 1.0 | Establishes independent variation and recurrence in the synthetic record |
| Offline-sync design | Hal 1.0 | Clarke 1.0 | Records a completed upload while leaving explicit consent unestablished |

Each initial reader got two fresh sessions with the same prompt and seeded reply starter. The complete briefing included the exact act. The missing-source briefing withheld it and identified the required act in the task. The task explicitly allowed a source request. Scenario order alternated which briefing was tested first.

When the reader requested the correct act, the harness supplied that single excerpt and asked the reader to complete the original reply. The checks required the exact quote, the correct evidence status, a citation to the archived act, a change only on the selected branch, and first-pass Python and Node validation. The fresh recipient then received a briefing of the resulting file. It had to identify the newest act, its archived citation, the surviving sibling stance, the retraction, and the ACK that was retracted.

## Results

| Conversation | Complete briefing | Missing-source briefing | After source recovery | Fresh recipient |
| --- | --- | --- | --- | --- |
| Research claim | First draft passed | Clarke requested `t185` | First draft quoted the source, correctly identified the recorded control, and passed both validators | Hal identified every requested act and ACK |
| Offline-sync design | First draft passed | Hal requested `t185` | First draft quoted the source, correctly left consent unestablished, and passed both validators | Clarke identified every requested act and ACK |

All four continuations reached act 2,001 and passed Python and Node on the first draft. Both readers requested the omitted act. Both fresh recipients identified the exact archived citation, the current sibling ACK, and the retraction and its target. The relevant claims and prior packet records remained intact. All eight calls completed for an estimated **$0.1331**.

The prompt identified the act to assess and explicitly permitted requesting it. The result covers whether a reader recognizes that a specified source is missing and can use it after retrieval. Open-ended discovery of which source matters remains untested here.

## Replay bundle

Download the [starting packets, briefings, replies, prompts, and scorecard](../evidence/ucl24-missing-source-relays.zip). Each scenario folder has a `starting.txt` and a `recovered-reply.txt`. To verify the recovered handoff, substitute the extracted path for `research/`.

```sh
python src/ucl.py check research/starting.txt
python src/ucl.py check research/recovered-reply.txt
node tools/check_ucl_portable.js research/recovered-reply.txt
python src/ucl.py diff research/starting.txt research/recovered-reply.txt --compact
```

Bundle SHA-256 is `83518a614d90d56d5baa4ae876b4879de7be06b72452ce8e088fa946df37ce25`.

[Live workflow and artifacts](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45510335618) · [Fixture and scoring code](https://github.com/ulandort/Universal-Cognitive-Language/blob/cfc9eb507f37fd9762f2c7bc4ff9ad6cfcb94180/benchmarks/missing_source_once.py)
