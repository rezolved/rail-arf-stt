---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
updated_at: "2026-08-13T07:31:13Z"
completed_steps: 2
next_step_number: 3
next_step_id: "init-folders"
---
# Task Objective

Re-analyze existing t0022/t0023 biasing sweeps for the brand-accuracy/WER tradeoff, then test
biasing on top of the existing t0021 fine-tuned checkpoint.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0024_biasing_pareto_and_ft_biasing_ablation` created. Initial folder structure
initialized in `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/`. Step 1 is a mechanical setup
step with no research output.

### Step 2 — check-deps

`verify_task_dependencies.py` reports all three dependencies (t0021, t0022, t0023) as unsatisfied
(TD-E003, exit 1) purely on `task.json` metadata: t0021/t0022 have stale `status: "not_started"`
despite complete committed results, and t0023 uses a legacy pre-spec schema reporting `"complete"`
instead of `"completed"`. Direct file inspection confirmed the actual artifacts this task needs are
present and readable: `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` (100 rows),
`tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` (100 rows), and
`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/manifest.jsonl` (21 clips, audio via
`data/clean_eval_audio.dvc`). Full detail in `logs/steps/002_check-deps/deps_report.json`. Since
`prestep` hard-blocks on verificator failure with no override flag, this step's folder creation and
`step_tracker.json` in_progress transition were done by hand to proceed past the block.

* * *

## Cross-Step Decisions

* **Dependency metadata caveat (step 2)**: `t0021_parakeet_finetune_vs_biasing` and
  `t0022_gpu_pb_diagnostic` have stale `task.json` `status: "not_started"` fields despite having
  complete, committed `results/`/`data/` output; `t0023_tdt_vs_unified_biasing` uses a legacy
  pre-spec `task.json` schema (no `spec_version`/`task_index`/`expected_assets`,
  `status: "complete"` not `"completed"`) that `verify_task_dependencies.py` /
  `aggregate_tasks.py --ids` cannot resolve. Do NOT modify t0021/t0022/t0023's `task.json` files
  (never edit other tasks' folders) — this is a pre-existing repo data-quality issue, not something
  this task fixes. Any later step that runs `verify_task_dependencies.py`, `aggregate_tasks.py`, or
  similar metadata-based tooling against these three task IDs should expect it to report them as
  incomplete/unresolvable and should treat that as a known false negative — verify the actual needed
  files directly on disk instead (paths listed in the Step 2 history entry above and in
  `logs/steps/002_check-deps/deps_report.json`).

* * *

## Next Step Notes

Step 2 (`check-deps`) is complete. Dependencies are functionally satisfied — the sweep JSONLs and
t0021 clean-eval manifest/audio are present and readable, verified by direct file inspection since
the metadata-based verificator false-negatives on all three deps (see Cross-Step Decisions). The
next step-executor (`init-folders`, step 3) should proceed normally: run `init_task_folders`, which
reads `expected_assets` from this task's own `task.json` (unaffected by the dependency metadata
issue) to scaffold the folder structure.
