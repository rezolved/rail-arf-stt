---
spec_version: "2"
predictions_id: "parakeet-unified-biasing-best-hyperparam"
documented_by_task: "t0019_parakeet_biasing_improvement"
date_documented: "2026-07-02"
---

## What produced these predictions

Per the plan's pre-registered rejection rule (`plan/plan.md` Step 3): the hyperparameter sweep's
top-2 screening candidates by 20-clip EA-DV (`alpha=3.0, depth_scaling=3.0` and `alpha=2.0,
depth_scaling=4.0`) were confirmed on all 93 clips, and both breached the +1.0 absolute point WER
regression cap versus baseline by more than 20 points (see `results/hyperparam_top2_full93.json`:
WER 38.4% and 31.0% vs. an 11.0% baseline). A follow-up narrower grid closer to the default
(`alpha` 1.0-1.5, `depth_scaling` 2.0-2.5, 18 configs) was screened with WER tracked and found
**zero EA-DV movement** across every config — all scored EA-DV=0.600 on the fixed 20-clip
subsample, identical to the default point.

Because no candidate config both improves EA-DV and stays within the WER cap, the plan's fallback
rule applies: the "winning" config is the unchanged production default (`alpha=1.0,
depth_scaling=2.0`). This file is therefore byte-identical to
`parakeet-unified-biasing-baseline/files/predictions.jsonl` — it is included as its own predictions
asset (per `task.json` `expected_assets.predictions: 3`) to make the hyperparameter-sweep's null
result an explicit, traceable artifact rather than an implicit assumption.

## Dataset

All 93 clips of gold-92 (`t0001_stt_benchmark`, `assets/dataset/stt-benchmark-gold-92`).

## Evidence for the null result

See `results/hyperparam_sweep.jsonl` (15-config wide grid), `results/hyperparam_sweep_narrow.jsonl`
(18-config narrow grid), and `results/images/hyperparam_sweep_heatmap.png` for the full grid.
