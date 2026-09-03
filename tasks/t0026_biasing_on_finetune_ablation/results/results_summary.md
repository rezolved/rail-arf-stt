# Results Summary: Biasing on Top of Fine-Tuning — Complementary or Redundant?

## Summary

Ran a 2x2 ablation of GPU-PB context biasing x `parakeet-unified` fine-tuning (arms A/B/C/D) on the
91-clip `clean_eval_v2` holdout, completing `t0024`'s deferred Part B. Fine-tuning alone (arm C)
recovers almost all of the achievable brand accuracy; stacking biasing on top (arm D) adds no
statistically significant gain over fine-tuning alone and costs substantially more WER on neutral
speech once fine-tuning is already applied. `t0025_parakeet_tdt_brand_finetune` should proceed as
scoped; it should not budget extra work to stack biasing on its resulting checkpoint by default.

## Metrics

* **brand_exact_rate (overall)**: A **0.0%**, B **37.2%**, C **79.1%**, D **83.7%** — fine-tuning
  (A→C) is the dominant lever; biasing on top of fine-tuning (C→D) adds only **+4.65** points.
* **neutral_wer**: A **8.1%**, B **12.7%** (+4.6 pts over A), C **27.1%**, D **48.8%** (+21.7 pts
  over C) — biasing costs **~4.7x** more neutral WER once the model is fine-tuned than on the base
  model.
* **McNemar c_vs_d (fine-tuned, bias vs. no-bias)**: 1 clip favors C, 3 favor D, **p = 0.625** — not
  significant; D's nominal edge over C is statistically indistinguishable from noise.
* **McNemar b_vs_d (biased, fine-tuned vs. not)**: 0 clips favor B, 20 favor D, **p = 1.9e-6** —
  fine-tuning clears the biasing-only arm decisively.
* **Clip-level mechanism**: of the 18 clips fixed by exactly one lever relative to baseline A, **18
  are fixed by fine-tuning (arm C) and 0 by biasing alone (arm B)** — the levers are not attacking
  disjoint error classes.
* **Request success rate**: **91/91 (100%)** for all four arms — no arm falls below the plan's 0.8
  rejection threshold, so all numbers above are reportable without caveat.

## Verification

* `uv run python -m arf.scripts.verificators.verify_task_metrics t0026_biasing_on_finetune_ablation`
  — **PASSED** (0 errors), `results/metrics.json` confirmed `{}` per the plan's Phase 1 review (no
  registered project metric applies — all are gold-92-scoped or full-pipeline-latency-scoped).
* `uv run python -m arf.scripts.verificators.verify_task_results t0026_biasing_on_finetune_ablation`
  — **PASSED** (0 errors) on this step's `results_summary.md`, `results_detailed.md`,
  `metrics.json`, `costs.json`, `remote_machines_used.json`.
* `meta.asset_types.predictions.verificator` (all 4 arms) and
  `meta.asset_types.answer.verificator biasing-vs-finetuning-complementary-or-redundant` — both
  **PASSED** with 0 errors in step 9 (implementation), independently re-confirmed this step by
  direct read of `assets/`.
* Metrics cross-check: every number quoted above was read directly from
  `results/ablation_metrics.json` and `results/mcnemar_results.json` and matches exactly (no
  rounding beyond the JSON's own precision).
