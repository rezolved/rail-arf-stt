---
spec_version: "1"
task_id: "t0026_biasing_on_finetune_ablation"
updated_at: "2026-08-26T15:20:00Z"
completed_steps: 9
next_step_number: 8
next_step_id: "setup-machines"
---
# Task Objective

2x2 ablation of GPU-PB biasing x parakeet-unified fine-tuning on the 91-clip clean_eval_v2 holdout.
Completes t0024's deferred Part B.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0026_biasing_on_finetune_ablation` created. Initial folder structure initialized in
`tasks/t0026_biasing_on_finetune_ablation/`. Step 1 is a mechanical setup step with no research
output.

### Step 2 — check-deps

t0021 and t0024-Part-A are `completed`. t0024_parakeet_unified_checkpoint_archive initially failed
(TD-E003, status `not_started`) despite its model asset being fully merged to main — a bookkeeping
false-negative (asset added directly, no `reporting` step ever ran). Fixed with a metadata-only
status correction pushed straight to `main` (commit `e755ef4`, same pattern as PR #19), merged into
this branch. See `logs/steps/002_check-deps/deps_report.json` for full detail.

### Step 3 — init-folders

Mandatory task folder structure created via `init_task_folders` (13 dirs + `.gitkeep`,
`__init__.py`, `code/__init__.py`), matching `expected_assets` (`predictions: 4`, `answer: 1`).
Aggregator cache populated at `tasks/t0026_biasing_on_finetune_ablation/ctx/` (task_types, costs,
tasks, metrics, suggestions) — gitignored, local-only for this session. Step log:
`logs/steps/003_init-folders/folders_created.txt`.

### Step 4 — research-papers

Skipped (planned at step 1). Predetermined 2x2 ablation using an already-selected biasing cell and
existing fine-tuned checkpoint; no new literature validation required.

### Step 5 — research-internet

Skipped (planned at step 1). No new external tools, APIs, or facts are needed beyond what
t0021-t0024 already established.

### Step 11 — creative-thinking

Skipped (planned at step 1). Mechanical, predetermined 2x2 ablation with no open design space for
alternative approaches.

### Step 13 — compare-literature

Skipped (planned at step 1). Metrics are project-internal (clean_eval_v2, non-registered) with no
published baseline to compare against, matching t0024's precedent.

### Step 6 — research-code

Produced `research/research_code.md` (13 tasks reviewed, 9 cited, 0 libraries registered — no
import-via-library path exists) and `research/research_summary.md`. Verificator passed with 0
errors/0 warnings. Key finding for planning: the `apply_malsd_boost`/brand-scoring/`wer` helpers
this task needs live at `tasks/t0023_tdt_vs_unified_biasing/code/run.py:76-299` and must be
**copied**, not imported; `t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json`
already has the selected biasing cell/frontier and should be read directly rather than re-derived;
t0021's `domain_vocab_accuracy` metric is incompatible with this task's required `brand_exact_rate`
and must not be reused.

### Step 7 — planning

`plan/plan.md` written and verified (`verify_plan`, 0 errors, 0 warnings). Defines the 4 arms
(A=base/no-bias, B=base+bias, C=fine-tuned/no-bias, D=fine-tuned+bias) run on `clean_eval_v2` using
the fixed t0024 Pareto cell (`context_score=3.0, depth_scaling=0.5, alpha=1.5`) for biased arms, a
gitignored corrected copy of the `clean_eval_v2` manifest under this task's own `data/`, code copied
(not imported) from `tasks/t0023_tdt_vs_unified_biasing/code/run.py`, a `scipy.stats.binomtest`
McNemar analysis, and GPU pinning to `LLM-T1-NC80` GPU 1 with explicit sequencing ahead of `t0025`.
Caveat for `setup-machines`: the plan assumes `t0025` has not started GPU work yet (true as of this
step) but that must be re-checked before acquiring the machine.

* * *

## Cross-Step Decisions

* `t0024_parakeet_unified_checkpoint_archive/task.json` status was stuck at `not_started` on main
  despite the model asset being merged; corrected directly on main (commit `e755ef4`) rather than in
  this task's branch, per Critical Rule 1 (infra fixes go to a separate main commit, not inline in
  the task branch). Downstream steps can rely on this dependency as satisfied.

* No library asset exists for the STT scoring/boosting helpers (`apply_malsd_boost`, brand scoring,
  `wer`). Planning/implementation must **copy** these functions from
  `tasks/t0023_tdt_vs_unified_biasing/code/run.py:76-299` into this task's `code/` directory per the
  cross-task import rule — do not import from t0023's `code/` directly.

* No prior task implements a McNemar test; `research_code.md` recommends `scipy.stats.binomtest` on
  discordant pairs (scipy is already a project dependency) rather than adding `statsmodels`.

* * *

## Next Step Notes

Step 7 (planning) completed successfully; `plan/plan.md` is ready and verified. Proceed to step 8
(`setup-machines`) per `step_tracker.json`: acquire `LLM-T1-NC80` GPU 1 (`CUDA_VISIBLE_DEVICES=1`),
verify the `stt` conda env and GPU visibility, and re-confirm `t0025` has not started GPU work on
the same machine before proceeding (the two tasks cannot run GPU work concurrently on `LLM-T1-NC80`
today). See `plan/plan.md`'s `## Remote Machines` and `## Step by Step` sections for exact
provisioning and sequencing steps.
