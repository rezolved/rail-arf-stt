---
spec_version: "1"
task_id: "t0026_biasing_on_finetune_ablation"
updated_at: "2026-09-02T14:45:00Z"
completed_steps: 9
next_step_number: 10
next_step_id: "teardown"
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

### Step 8 — setup-machines

Resumed from `blocked_intervention` after PR #26 (commit `8b7f5ec`, merged into this branch as
`bc074b7`) fixed the shared-deadline bug in `azure_ml_vm.py`'s `acquire()`. Acquired `LLM-T1-NC80`
on the first attempt (0 `failed_attempts`, 499.4s to SSH-ready), verified GPU 1 isolation
(`CUDA_VISIBLE_DEVICES=1`, `stt` env, NeMo 3.1.0), and `dvc pull`ed the checkpoint and
`clean_eval_v2` audio. Machine is `ready` and locked for `t0026`; `t0025` remains `not_started`, so
no co-tenancy conflict exists yet. See
`logs/steps/008_setup-machines/{machine_log.json,step_log.md}`.

### Step 9 — implementation

Executed `plan/plan.md` in full on the already-acquired `LLM-T1-NC80` GPU 1: fixed the manifest,
copied scoring/boosting/audio code from `t0021`/`t0023`, ran all 4 arms (91/91 successful requests
each), computed McNemar tests, generated 3 charts, and produced 4 `predictions` assets + 1 `answer`
asset, all passing their verificators with 0 errors. Mid-run, found and fixed a scoring bug (see
Cross-Step Decisions) that required a full rerun. Key finding: biasing is redundant once fine-tuning
is applied (arm D vs. arm C McNemar p=0.625, not significant) and costs 4.7x more `neutral_wer`
degradation than on the base model. See `logs/steps/009_implementation/step_log.md`.

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

* `azure_ml_vm.to_machine_log_entry()` has a pre-existing gap (traced to commit `c06c5b5`, unrelated
  to PR #25/#26): it omits `spec_version`, `hourly_cost_usd`, `started_vm`, and emits
  `provider: "azure-ml"` instead of the spec's `"azure_ml"` enum value. Worked around by
  hand-enriching `machine_log.json` with the real `acquire()` output, matching the precedent set by
  `t0014`/`t0015`/`t0024`. Not fixed inline here per Critical Rule 1 — worth a `/self-improvement`
  fix on `main` and a note in this task's `suggestions` step.

* `.dvc/config.local`'s vault-sourced connection string is stale/`AuthenticationFailed` in this
  worktree; worked around locally (gitignored, uncommitted) by falling back to
  `az login`/`AzureCliCredential` per `docs/dvc-data-workflow.md`. This is a team-wide vault issue
  (shared key with `rail-arf-finetuning`/`rail-benchmarks`), not a task-branch fix.

* The copied `brand_in_ref` helper's `PHONETIC_PATTERNS` fallback (correct on gold-92, its original
  tuning set) produced 11 false-positive brand-containing clips on `clean_eval_v2` — "Brain
  Commerce" phonetically collided with `brainpowa`. Fixed in this task's own `code/scoring.py` by
  restricting ground-truth brand detection to `EXACT_PATTERNS` only; verified this reproduces the
  documented 43 brand / 48 neutral split before the full run. This divergence from the literal
  `t0023` copy is local to this task's `code/`, not upstreamed.

* This repo's `pyproject.toml` `[tool.mypy] exclude = ["tasks/.*/code/", "tasks/.*/assets/"]`
  (present since commit `6416a1e`, unrelated to this task) makes the mandated
  `mypy -p tasks.$TASK_ID.code` invocation only type-check `__init__.py` (1 source file) — the
  exclude pattern suppresses follow-import checking into the rest of `code/`.
  `ruff check`/`ruff format` still fully lint every file. This is a pre-existing, repo-wide gap
  affecting every task that follows the documented mypy invocation, not specific to t0026; worth a
  `/self-improvement` fix on `main` and a note in this task's `suggestions` step.

* * *

## Next Step Notes

Step 9 (`implementation`) completed: all 4 `predictions` assets and the 1 `answer` asset exist and
pass verification; `results/ablation_metrics.json`, `mcnemar_results.json`,
`clip_level_appendix.json`, and 3 charts in `results/images/` are all in place;
`results/metrics.json` is `{}` per the plan's deliberate-omission rationale. All GPU-dependent work
for this task is finished. Proceed to step 10 (`teardown`): destroy/release `LLM-T1-NC80` (or
confirm it is left in a safe, deallocated state) before `t0025_parakeet_tdt_brand_finetune` attempts
its own `setup-machines`. No further GPU work is needed for this task.
