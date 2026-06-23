# Papers: `confidence-routing` (1)

1 papers across 1 year(s).

[Back to all papers](../README.md)

---

## 2026 (1)

<details>
<summary>📝 Towards Human-Like Interactive Speech Recognition With Agentic Correction
and Semantic Evaluation — Jiang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.29430` |
| **Authors** | Zixuan Jiang, Yanqiao Zhu, Peng Wang, Qinyuan Chen, Xipeng Qiu, Kai Yu |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.29430` |
| **URL** | https://arxiv.org/abs/2605.29430 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`confidence-routing`](../../../meta/categories/confidence-routing/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.29430/summary.md) |

Jiang et al. reframe ASR as a closed-loop interactive task and demonstrate that semantic
errors (wrong intent, wrong entity) are far more correctable than surface token errors. The
motivating observation is that WER fails to distinguish high-value errors (brand names,
quantities) from low-value ones (function words), understating how correctable
business-critical mistakes actually are.

The Agentic ASR framework adds semantic correction, intent routing, and reasoning-based
editing on top of a standard ASR front-end. The S2ER metric provides a semantically meaningful
evaluation via LLM judging with 0.83-0.90 human correlation. An Interactive Simulation System
enables automated multi-turn evaluation.

Key results: S2ER collapses from **~20-28% to <2%** across 10 correction loops while WER
decreases only from ~12% to ~10%. Named entity error rates improve from ~2% to <1% on
specialized NER test sets. The dramatic S2ER vs. WER divergence confirms that semantic errors
concentrate in a small set of critical tokens.

For Rezolve, the primary takeaway is the S2ER metric: adopting it for gold-92 evaluation would
more accurately measure wrong-action rate than WER. The multi-turn correction approach is
appealing but requires latency budgeting — at most 1-2 correction turns are feasible within
800ms. The heavy Qwen3-32B backend requires distillation for production.

</details>
