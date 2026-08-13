---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
updated_at: "2026-08-13T07:42:12Z"
completed_steps: 8
next_step_number: 7
next_step_id: "planning"
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

### Step 6 — research-code

Wrote `research/research_code.md` (verificator PASSED, zero errors/warnings) and
`research/research_summary.md`. Confirmed by direct file read (not just the subagent's claim):
`t0022`'s `param_sweep.jsonl` and `t0023`'s `tdt_sweep.jsonl` are each 100-row JSONL with schema
`{context_score, depth_scaling, alpha, brand_exact_rate, neutral_wer}`; the live-prod TDT cell
(`cs=3.0/ds=0.5/α=1.5`) reads `brand_exact_rate=0.457, neutral_wer=0.057` in `tdt_sweep.jsonl`,
exactly matching `task_description.md`; `t0021/code/paths.py`
`FINETUNED_NEMO = /mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`. Found the exact
Part B bug: `t0021/code/run_clean_eval.py`'s `apply_boosting()` (lines 126-135) only ever sets
`strategy = "greedy_batch"` + `greedy.boosting_tree.*` — never `malsd_batch` — so the fine-tuned
checkpoint has never actually had a boosting tree applied; `t0023/code/run.py`'s
`apply_malsd_boost()` (lines 281-299, `strategy = "malsd_batch"` + `beam.boosting_tree.*` +
`beam.boosting_tree_alpha`) is the function to copy in for Part B instead. Could not independently
verify the `brainpowa-realtime-api/config.py` production-default values cited in
`task_description.md` — that repo is not present in this sandbox; treat those specific numbers as
unverified-here (not load-bearing for either part, since Part A/B use the sweep JSONLs and the
frontier point, not the literal config file).

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

* **Part B boosting-code fix identified (step 6)**: `t0021/code/run_clean_eval.py`'s
  `apply_boosting()` only ever configures `strategy = "greedy_batch"` (writes to
  `greedy.boosting_tree.*`) — NeMo silently ignores boosting under `greedy_batch` (proven in
  `t0022`'s decoding matrix), so the fine-tuned checkpoint has never actually been evaluated with a
  working boosting tree. Planning/implementation for Part B must copy `t0023/code/run.py`'s
  `apply_malsd_boost()` (sets `strategy = "malsd_batch"`, writes `beam.boosting_tree.*` +
  `beam.boosting_tree_alpha`) in place of it, not reuse `apply_boosting()` as-is.

* **Verification gap (step 6)**: the live production `brainpowa-realtime-api/config.py` decoding
  defaults cited in `task_description.md` could not be independently re-read — that repo is not
  cloned into this rail-arf-stt sandbox/worktree. Not load-bearing for either part (Part A/B work
  entirely from the sweep JSONLs and the frontier point, not the literal config file), but any step
  that needs to actually edit or cite that config file verbatim will need access to the
  `brainpowa-realtime-api` repo separately.

* * *

## Next Step Notes

Step 6 (`research-code`) is complete. `research/research_code.md` (verificator PASSED, zero
errors/warnings) and the compact `research/research_summary.md` are written and committed. Verified
directly on disk (not just via the subagent): both sweep JSONLs are 100-row grids with schema
`{context_score, depth_scaling, alpha, brand_exact_rate, neutral_wer}`; the live-prod TDT cell
matches `task_description.md` exactly (`brand_exact_rate=0.457`, `neutral_wer=0.057`); the
checkpoint path `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` is confirmed in
`t0021/code/paths.py`. The next step-executor is step 7, `planning`: synthesize
`research/research_summary.md` into `plan/plan.md`, covering the Pareto-frontier computation/charts
for Part A and the single fine-tuned+`malsd_batch`-biased inference run for Part B (must select and
justify the specific frontier cell for Part B's boosting config — do not default to `t0022`'s old
headline cell without checking Part A's own frontier answer first, per `task_description.md`).
Remember both Cross-Step Decisions above: the dependency-metadata caveat (steps 2/6) and the
`apply_boosting()` → `apply_malsd_boost()` swap needed for Part B's implementation code.
