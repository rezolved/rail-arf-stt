# Suggestions: `confidence-routing`

1 suggestion(s) in category
[`confidence-routing`](../../../meta/categories/confidence-routing/) **1 open** (1 medium).

[Back to all suggestions](../README.md)

---

## Medium Priority

<details>
<summary>📊 <strong>Implement intent classification metric to replace span-presence
proxy</strong> (S-0002-07)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-07` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`confidence-routing`](../../../meta/categories/confidence-routing/) |

The current intent_preservation_gold92 metric uses a span-presence heuristic that is
over-estimated: 'Resolve' satisfies 'Rezolve' after normalisation, inflating the 90.3% figure.
A proper intent classifier should distinguish entity substitution that changes action target
(e.g., wrong company name) from substitution that preserves action type (e.g., generic query
intent). This is needed to make intent_preservation_gold92 meaningful for the
confidence-routing policy (wrong_action_rate_gold92 goal: <2%). Implement as a lightweight
rule-based or LLM-based classifier and re-evaluate on gold-92. Recommended task types:
write-library, experiment-run.

</details>
