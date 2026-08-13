# Results Summary: Biasing Pareto Re-Analysis + Biasing-on-Fine-Tune Ablation

## Summary

Part A re-analyzed t0022's and t0023's existing 100-cell hyperparameter sweeps and computed the true
Pareto frontier (`brand_exact_rate` vs `neutral_wer`) for both `parakeet-tdt-0.6b-v3` and
`parakeet-unified-en-0.6b`, proving the current live-production TDT decoding config is dominated and
selecting a concrete replacement. Part B (fine-tuning + `malsd_batch` biasing ablation) was
deliberately deferred mid-task after the t0021 fine-tuned checkpoint and its `stt` conda environment
could not be located on any reachable machine, a user-approved scope reduction, not a silent gap.

## Metrics

* **TDT frontier**: 5 non-dominated cells out of 100 swept; selected production cell
  `context_score=2.5, depth_scaling=0.5, alpha=2.0` reaches **48.6%** `brand_exact_rate` at **5.7%**
  `neutral_wer` — a +2.9pp gain over the current live-prod cell (`45.7%` @ `5.7%`) at **zero** extra
  `neutral_wer` cost.
* **Unified frontier**: 5 non-dominated cells out of 100 swept; selected cell
  `context_score=3.0, depth_scaling=0.5, alpha=1.5` reaches **60.0%** `brand_exact_rate` at **8.7%**
  `neutral_wer`.
* **Headline-cell cost comparison**: the prior tasks' headline cells cost **64.9%** (TDT) and
  **27.9%** (unified) `neutral_wer` — roughly 11x and 3x this task's selected cells' `neutral_wer`,
  for only +11.4pp / +8.6pp more `brand_exact_rate`.
* **Part B**: **0 of 9** planned Part-B requirements (`REQ-12`–`REQ-21`) completed — deferred, not
  attempted, after $14.06 of GPU provisioning found neither the checkpoint nor its runtime
  environment reachable (see `intervention/checkpoint_not_found.md`).
* **registered project metrics measured**: none — `results/metrics.json` is `{}` (Part A is pure
  re-analysis of already-collected sweep data, not a new gold-92 evaluation run, so none of the
  registered `*_gold92` metrics apply).

## Verification

* `meta.asset_types.answer.verificator` on
  `assets/answer/production-decoding-and-biasing-ft-verdict/` — PASSED (0 errors, 0 warnings),
  confirmed in step 9.
* `verify_task_metrics.py` on `results/metrics.json` (`{}`) — PASSED (0 errors, 0 warnings),
  confirmed in step 9.
* `ruff check`, `ruff format`, `mypy` on `code/paths.py`, `code/pareto.py`, `code/make_charts.py` —
  all clean, confirmed independently in step 9 (not just the implementation subagent's self-report).
* `verify_machines_destroyed.py` — PASSED (0 errors, 0 warnings), confirmed in step 10.
