---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
updated_at: "2026-08-13T10:55:00Z"
completed_steps: 10
next_step_number: 9
next_step_id: "implementation"
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

### Step 7 — planning

Wrote `plan/plan.md` (verificator PASSED, zero errors/zero warnings, independently re-verified by
this step-executor, not just the planning subagent's claim). Part A: `code/pareto.py` computes the
**true** non-dominated-point Pareto frontier (not a naive sort-and-scan — that construction can
retain a dominated point when two rows share `neutral_wer`, which both sweeps do), giving 5 frontier
cells per model. An explicit numeric stance (`Δneutral_wer / Δbrand_exact_rate ≤ 1.0` against the
last-**accepted** point, scanned ascending by `neutral_wer`) selects TDT production cell
`cs=2.5/ds=0.5/α=2.0` (48.6%@5.7%, a zero-cost strict improvement over the dominated current-prod
point) and unified cell `cs=3.0/ds=0.5/α=1.5` (60.0%@8.7%) — the latter is the exact config Part B's
GPU run uses for its boosting tree, deliberately not defaulting to t0022's old headline cell
(`cs=2.5/ds=0.5/α=2.5`, 68.6%@27.9%). Part B copies t0023's `apply_malsd_boost()` (not t0021's
broken `apply_boosting()`) into a new `code/run_ft_biased_eval.py`, which reads the selected unified
cell from `results/pareto_unified.json` at runtime rather than hardcoding it. Caveat: the plan also
caught and corrected a data-provenance bug — the task-text-quoted fine-tuned-only clean-21 latency
"0.112s" is actually t0021's **gold-92** latency; the correct clean-21 p50 (computed from t0021's
existing raw per-clip data, not new inference) is ≈0.0536s, and the plan requires both numbers be
reported with provenance labels rather than silently substituted.

### Step 8 — setup-machines

Provisioned and verified `FT-MC` (SSH, 2x H100 NVL, CUDA 12.2; repo rsynced). Part B's preconditions
(t0021 checkpoint, `stt` conda env) were not present or locatable anywhere reachable — see
`intervention/checkpoint_not_found.md`. User decided: defer Part B, tear down, Part A only in step
9\. FT-MC auto-stopped via idle-shutdown, ~$14.06 total.

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

* **Plan decisions for implementation (step 7)**: `plan/plan.md` is the authoritative,
  self-contained spec for step 9 (`implementation`) — read it in full rather than relying on this
  summary. Key numbers/choices the implementation step-executor needs up front:
  * **Part A frontier stance**: true non-dominated-point Pareto filter (`code/pareto.py`), not a
    sort-and-scan. TDT selected cell `context_score=2.5, depth_scaling=0.5, alpha=2.0`
    (`brand_exact_rate=48.6%, neutral_wer=5.7%`) — the new recommended production config, replacing
    the dominated current-prod point (`cs=3.0/ds=0.5/α=1.5`, 45.7%@5.7%). Unified selected cell
    `context_score=3.0, depth_scaling=0.5, alpha=1.5` (`brand_exact_rate=60.0%, neutral_wer=8.7%`).
  * **Part B's boosting config = the unified selected cell above** (`cs=3.0/ds=0.5/α=1.5`), read
    programmatically from `results/pareto_unified.json` at runtime by `run_ft_biased_eval.py`, never
    hardcoded — Part A's step (`code/pareto.py`) must run and write that file before Part B's script
    can execute.
  * **GPU machine**: Azure ML H100 pool (`project/azure_vm.json`), `gpu_class: H100`,
    `provider: azure_ml`, priority `FT-NC80-v3` → `FT-NC80-v1` → `FT-NC80-v2` → `FT-MC`, 2xH100
    each, `$13.96/hr`. Estimated run: well under 1hr GPU wall-clock, padded to 1.5hr (~$21), capped
    at $30 for this task.
  * **Planned script files** (all new, in `code/`): `paths.py`, `pareto.py`, `make_charts.py` (Part
    A); `constants.py`, `scoring.py`, `run_ft_biased_eval.py` (Part B, copies `apply_malsd_boost()`
    from `t0023/code/run.py` — NOT `apply_boosting()` from `t0021/code/run_clean_eval.py`, which
    only ever sets the broken `greedy_batch` strategy); `build_comparison.py` (Milestone 3,
    assembles the 3-row comparison table).
  * **Data-provenance fix**: the task-text-quoted fine-tuned-only clean-21 latency "0.112s" is
    actually t0021's gold-92 latency, not clean-21. `build_comparison.py` must recompute the correct
    clean-21 p50 (≈0.0536s) from t0021's existing raw per-clip data (`clean_eval_finetuned.jsonl`)
    and report both numbers with provenance labels.
  * **Validation gate for the GPU run**: 5-clip smoke test before the full 21-clip run, explicit
    failure conditions (script crash, all-empty transcripts, decoding strategy not showing
    `malsd_batch`), individual-output inspection of all 5 records before proceeding.
  * **Expected assets**: 1 `predictions` asset
    (`assets/predictions/parakeet-finetuned-malsd-biased-clean21/`) and 1 shared `answer` asset
    (`assets/answer/production-decoding-and-biasing-ft-verdict/`) covering both parts' verdicts.

* **Part B deferred, user-approved (step 8)**: `FT-MC` (the only reachable pool entry — the other 3
  `project/azure_vm.json` entries no longer exist in Azure) was provisioned and fully verified
  (SSH/GPU/CUDA), but neither the t0021 fine-tuned checkpoint
  (`/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`) nor the `stt` conda env exist
  on it, and neither could be located on any reachable machine (see
  `intervention/checkpoint_not_found.md`). This is a data-provenance gap, not a machine-selection
  problem — the VM that actually ran t0021 no longer exists in the pool. **User decision: defer Part
  B, tear down FT-MC, proceed with Part A only this round.** Step 9 (`implementation`) MUST run
  **Part A only**: pure local analysis of `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl`
  and `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` (no GPU, no remote machine). Do
  **not** attempt Part B and do **not** re-search for the checkpoint — that search is exhausted and
  documented. Whatever step 9 produces for the `answer`/`predictions` assets and `results/` must
  reflect Part-A-only scope (or explicitly mark Part B fields as not-run/deferred) rather than
  fabricating Part B output.

* * *

## Next Step Notes

Step 8 (`setup-machines`) is complete. `FT-MC` was provisioned, SSH/GPU (2x H100 NVL)/CUDA verified,
repo synced — but Part B's required checkpoint and conda env do not exist on it or anywhere
reachable (see `intervention/checkpoint_not_found.md` for the full search and the stale-pool-config
/ DVC-auth findings, which are infra issues for `main`, not this branch). The user was consulted and
explicitly decided: tear down now (already done — FT-MC auto-stopped via its own idle-shutdown, no
runaway cost, ~$14.06 total, see `machine_log.json`), defer Part B, and proceed with **Part A only**
this round. Step 9 (`implementation`) must NOT provision a machine, must NOT search for the
checkpoint again, and must NOT run Part B. Do the Part A work exactly as scoped in `plan/plan.md`
(Pareto frontier computation + charts from `t0022`/`t0023`'s existing sweep JSONLs, TDT selected
cell `cs=2.5/ds=0.5/α=2.0`, unified selected cell `cs=3.0/ds=0.5/α=1.5`), and make sure the `answer`
asset and `results/` output clearly state that Part B is deferred pending human resolution of the
checkpoint location, rather than silently omitting it. Step 10 (`teardown`) still runs next after
`implementation` per the normal step order — it should find FT-MC already destroyed and just
reconcile `results/costs.json` / `results/remote_machines_used.json` against `machine_log.json`.
Remember the Cross-Step Decisions above (this step's entry has the exact frontier cells, script
names, and GPU pool/cost numbers step 9 `implementation` will need) plus the dependency-metadata
caveat (steps 2/6) and the `apply_boosting()` → `apply_malsd_boost()` swap.
