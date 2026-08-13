---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
updated_at: "2026-08-13T07:34:08Z"
completed_steps: 7
next_step_number: 6
next_step_id: "research-code"
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

`verify_task_dependencies.py` fails on all three deps (TD-E003) due to stale/legacy `task.json`
metadata in t0021/t0022/t0023, not missing data. Direct inspection confirmed the required files
(t0022 `param_sweep.jsonl`, t0023 `tdt_sweep.jsonl`, t0021 clean_eval manifest + DVC audio) are
present and readable. See `logs/steps/002_check-deps/deps_report.json` for the full record.

### Step 3 — init-folders

Ran `init_task_folders` (created `plan/`, `research/`, `results/`, `results/images/`,
`corrections/`, `intervention/`, `code/`, `logs/commands/`, `logs/searches/`, `logs/sessions/`,
`logs/steps/`, `assets/predictions/`, `assets/answer/` with `.gitkeep` files, per this task's own
`expected_assets`) and populated the gitignored aggregator cache
(`tasks/t0024_biasing_pareto_and_ft_biasing_ablation/ctx/{task_types,costs,tasks,metrics,suggestions}.json`)
for downstream subagents. `logs/steps/003_init-folders/folders_created.txt` records the created
dirs.

### Step 4 — research-papers

Skipped (planned at step 1). Pure re-analysis of already-collected internal sweep data (Part A) plus
a confirmatory inference run reusing an established boosting config (Part B); no new methodology to
validate against the paper corpus.

### Step 5 — research-internet

Skipped (planned at step 1). Operates entirely on local data (t0022/t0023 sweep JSONLs, t0021
checkpoint and eval set); no new external tools, APIs, or facts are needed.

### Step 11 — creative-thinking

Skipped (planned at step 1). Both sub-tasks are deliberately narrow and prescriptive (explicit
frontier stance for Part A, single reuse-checkpoint run for Part B) with alternative-approach
exploration explicitly out of scope per the task's stated constraints.

### Step 13 — compare-literature

Skipped (planned at step 1). This task compares internal decoding configs and internal
fine-tune/biasing conditions against each other, not against published external baselines.

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

Step 3 (`init-folders`) is complete. The mandatory task folder structure and the two
`expected_assets` subdirectories (`assets/predictions/`, `assets/answer/`) exist with `.gitkeep`
files, and the gitignored `ctx/` aggregator cache is populated. Steps 4 and 5 (`research-papers`,
`research-internet`) are already marked `skipped` in `step_tracker.json` per the step-1 plan. The
next step-executor is step 6, `research-code`: review `t0021/run_finetuned.py`,
`t0021/run_clean_eval.py` (`apply_boosting`, scoring), and the t0022/t0023 sweep code so Part A's
frontier analysis and Part B's inference run reuse the exact same scoring method and reference the
correct checkpoint/config paths. Remember the dependency-metadata caveat above when locating
t0021/t0022/t0023 files — do not rely on `aggregate_tasks`/`verify_task_dependencies` output for
those three IDs; read files directly on disk.
