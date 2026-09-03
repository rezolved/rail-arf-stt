---
spec_version: "3"
task_id: "t0026_biasing_on_finetune_ablation"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-09-02T14:15:56Z"
completed_at: "2026-09-02T14:45:00Z"
---
## Summary

Executed `plan/plan.md` in full: fixed the `clean_eval_v2` manifest, copied scoring/boosting/audio
helpers from `t0023`/`t0021`, ran all 4 arms (A/B/C/D) on `LLM-T1-NC80` GPU 1 (already-acquired
machine, no re-provisioning), computed McNemar significance tests, generated 3 charts, and produced
4 `predictions` assets plus 1 `answer` asset.

## Actions Taken

1. Wrote `code/paths.py`, `constants.py`, `scoring.py`, `boosting.py`, `audio_io.py` (copied,
   per-plan, from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` and
   `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py`, not imported cross-task), and
   `fix_manifest.py`, which produced the gitignored `data/clean_eval_v2_manifest_fixed.jsonl` (91/91
   rows resolved to existing audio files).
2. Wrote `code/run_ablation.py` and ran validation gate 1 (2-clip smoke test, all 4 arms including
   the previously-unexercised arm D `restore_from()` + `malsd_batch` boosting combination) and gate
   2 (20-clip run) on the already-acquired `LLM-T1-NC80` GPU 1, `CUDA_VISIBLE_DEVICES=1`, `stt`
   conda env. Both gates passed.
3. During the full 91-clip run, discovered and fixed a scoring bug: `brand_in_ref`'s inherited
   `PHONETIC_PATTERNS` fallback produced 11 false-positive brand-containing clips on `clean_eval_v2`
   (54 vs. the dataset's documented 43) due to a collision with the unrelated "Brain Commerce"
   product name. Restricted `brand_in_ref` to `EXACT_PATTERNS` only, re-verified the 43/48
   brand/neutral split matches the documented count, and reran the full 4-arm x 91-clip inference to
   completion (91/91 successful requests per arm).
4. Wrote `code/mcnemar_test.py` (`scipy.stats.binomtest`, no new dependency) producing
   `results/mcnemar_results.json` (b_vs_d p=1.9e-6, c_vs_d p=0.625), `code/make_charts.py` producing
   the 3 required charts in `results/images/`, and `code/clip_level_appendix.py` producing
   `results/clip_level_appendix.json` (18 clips fixed by exactly one lever).
5. Spawned 5 parallel per-asset subagents to create the 4 `predictions` assets (arms A/B/C/D) and
   the 1 `answer` asset, per Critical Rule 7 of the implementation skill. All 5 assets pass their
   respective verificators with 0 errors (predictions: 1-2 expected `PR-W014`/`PR-W015` warnings per
   the plan's documented `model_id`/`dataset_ids` rationale; answer: 0 errors, 0 warnings).
6. Verified `results/metrics.json` is `{}` per the plan's Phase 1 metrics review (all 7 registered
   project metrics are gold-92-scoped or full-pipeline-latency-scoped, neither applicable here).

## Outputs

* `code/paths.py`, `constants.py`, `scoring.py`, `boosting.py`, `audio_io.py`, `fix_manifest.py`,
  `run_ablation.py`, `mcnemar_test.py`, `make_charts.py`, `clip_level_appendix.py`
* `results/ablation_metrics.json`, `results/arm_{a,b,c,d}_predictions.jsonl` (91 rows each),
  `results/mcnemar_results.json`, `results/clip_level_appendix.json`, `results/metrics.json` (`{}`)
* `results/images/chart1_brand_exact_rate.png`, `chart2_pareto_scatter.png`,
  `chart3_bc_confusion_heatmap.png`
* `assets/predictions/parakeet-unified-base-nobias-clean-eval-v2/`,
  `parakeet-unified-base-bias-clean-eval-v2/`, `parakeet-unified-ft-nobias-clean-eval-v2/`,
  `parakeet-unified-ft-bias-clean-eval-v2/` (each with `details.json`, `description.md`,
  `files/predictions-clean-eval-v2.jsonl`)
* `assets/answer/biasing-vs-finetuning-complementary-or-redundant/` (`details.json`,
  `short_answer.md`, `full_answer.md`)
* `data/.gitignore`, `data/clean_eval_v2_manifest_fixed.jsonl` (gitignored, machine-local)

## Issues

Found and fixed a scoring bug mid-run: the copied `brand_in_ref` helper's `PHONETIC_PATTERNS`
fallback (fine on gold-92, its original tuning set) mismatched "Brain Commerce" as a `brainpowa`
phonetic hit on `clean_eval_v2`, inflating brand-clip count from the documented 43 to 54. Fixed by
restricting to `EXACT_PATTERNS` only for ground-truth brand detection and rerunning the full
inference pass; this is now the correct 43/48 split. No other issues encountered. Separately, the
project's mandated `mypy -p tasks.$TASK_ID.code` invocation only type-checks `__init__.py` (1 source
file) under this repo's current `pyproject.toml` `[tool.mypy] exclude` pattern (`"tasks/.*/code/"`,
present since commit `6416a1e`, predating this task) — a pre-existing, repo-wide mypy-configuration
gap unrelated to this task's code, not fixed here per Critical Rule 1 (deferred to a future
`/self-improvement` pass on `main`).
