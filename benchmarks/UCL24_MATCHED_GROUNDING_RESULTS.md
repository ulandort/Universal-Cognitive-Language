# UCL 2.4 matched evidence-grounding comparison

A fresh call assessed the same evidence once as a UCL briefing excerpt and once as structured English. The experiment used Clarke 1.0 and Hal 1.0, with three synthetic archive cases and one call per model, case, and format. There were six matched pairs and 12 calls. The format submitted first alternated across pairs.

| Case | What the reader had to distinguish |
| --- | --- |
| Retracted qualification | Retrieve the original qualification and report its retracted status. The baseline observation leaves the control unestablished. |
| Unmet requirement | Identify the qualification as current. The log records repetition and leaves the input assignment unspecified. |
| Similar archived observations | Choose the observation where inputs varied independently. Both observations report that the pattern repeated. |

Both arms received identical selected facts, including the original observation and qualification text, exact source IDs, claim branch, and current ACK status. The UCL arm used a JSON projection of an archived handoff. The English arm rendered the same fields as sentences. Both arms received the same question, JSON answer schema, and seeded reply starter.

Before calling either model, the harness fixed four checks per reply. Each check required an exact match for the selected source and quote, the qualification's source and quote, the latest ACK and stance status, or the evidence status. The harness checked UCL-arm continuations separately with Python and Node, including the selected branch and archived citation. The natural-language reasons were retained for a separate review.

## Results

Counts use six submitted calls per format. An unscorable response contributes no passed checks.

| Measure | UCL briefing | Structured English |
| --- | ---: | ---: |
| Scorable JSON replies | 6/6 | 5/6 |
| Exact archived act and quote | 6/6 | 5/6 |
| Exact qualification author act and quote | 2/6 | 5/6 |
| Exact latest ACK and stance status | 6/6 | 4/6 |
| Correct control status | 6/6 | 5/6 |
| Total exact checks passed | 20/24 | 19/24 |
| Replies that passed all four evidence checks | 2/6 | 4/6 |
| First-pass UCL continuations validated | 6/6 | — |
| Input tokens | 4,092 | 3,909 |
| Estimated cost | $0.2287 | $0.2009 |

The 12 calls cost an estimated **$0.430**. The UCL briefs used 183 additional input tokens in total, about **4.7%** more than the matched English briefs.

All six UCL replies copied the qualification wording exactly. Four put the ACK ID `condition37` in the field asking for the author act ID `t37`. In the tested JSON projection, the qualification and latest-stance records expose their IDs as `id` and their author acts as `by`. The English rendering explicitly called out the author act in prose. A clearer label such as `author_act` in the briefing could be tested in a follow-up.

One English response could not be parsed as JSON. Another supplied the correct latest ACK ID with additional prose in its exact-match field. Among scorable replies, both formats selected the correct archived observation and reported the correct control status. In the separate prose review, one UCL reply inferred from “No intervention was recorded” that the control was not applied, even though its structured answer correctly said the control was unestablished. The four exact checks score the structured fields.

These are three variants of one synthetic archive fixture, with two models and one reply per model, case, and format. The counts support a concrete author-ID usability finding. Broader claims about the formats would need more varied conversations and repeated trials.

[Run and scored replies](https://github.com/ulandort/Universal-Cognitive-Language/actions/runs/45506360838) · [Test harness and scoring fixed before the run](https://github.com/ulandort/Universal-Cognitive-Language/blob/f62e6427cdb365d70008c9b2efede36feae3f1f0/benchmarks/matched_grounding_once.py)
