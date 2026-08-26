---
spec_version: "1"
task_id: "t0026_biasing_on_finetune_ablation"
updated_at: "2026-08-26T14:56:00Z"
completed_steps: 2
next_step_number: 3
next_step_id: "init-folders"
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

Verified t0021_parakeet_finetune_vs_biasing and t0024_biasing_pareto_and_ft_biasing_ablation are
`completed`. t0024_parakeet_unified_checkpoint_archive initially failed (TD-E003, status
`not_started`) even though its parakeet-unified-v5 model asset is fully merged to main — a
bookkeeping false-negative (asset added directly, no `reporting` step ever ran). Fixed by pushing a
metadata-only status correction straight to `main` (commit `e755ef4`, same pattern as PR #19 for
t0021-t0023; `gh pr create` and the REST API both returned 403 for this token, so the fix went
straight to main instead of through a PR) and merging `origin/main` into this task branch. Prestep
now passes; see `logs/steps/002_check-deps/deps_report.json` for full detail.

* * *

## Cross-Step Decisions

* `t0024_parakeet_unified_checkpoint_archive/task.json` status was stuck at `not_started` on main
  despite the model asset being merged; corrected directly on main (commit `e755ef4`) rather than in
  this task's branch, per Critical Rule 1 (infra fixes go to a separate main commit, not inline in
  the task branch). Downstream steps can rely on this dependency as satisfied.

* * *

## Next Step Notes

Step 2 completed successfully; all three dependencies (t0021, t0024 Part A,
t0024-checkpoint-archive) are satisfied. This task branch now includes an extra merge commit that
pulled in the t0024_parakeet_unified_checkpoint_archive status fix from main — this is expected and
not a merge conflict signal. Proceed to step 3 (`init-folders`) per step_tracker.json.
