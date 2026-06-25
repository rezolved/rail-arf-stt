---
spec_version: "1"
task_id: "t0007_ibm_granite_4_1_benchmark"
updated_at: "2026-06-25T07:47:00Z"
completed_steps: 8
next_step_number: 8
next_step_id: "setup-machines"
---
# Task Objective

Benchmark IBM Granite Speech 4.1 2B with keyword biasing on gold-92 to validate entity accuracy and
latency vs. Whisper large-v3 + initial_prompt baseline.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0007_ibm_granite_4_1_benchmark` created. Step plan written to `step_tracker.json` (15
steps: research-papers, research-internet, creative-thinking skipped; research-code, planning,
setup-machines, teardown, compare-literature included per stt-benchmark-run task type). Step 1 is a
mechanical setup step with no research output.

### Step 2 — check-deps

Both dependencies verified as completed: t0001_stt_benchmark (gold-92 dataset ingestion) and
t0004_vocabulary_biasing_experiment (Whisper initial_prompt biasing baseline). Result written to
`logs/steps/002_check-deps/deps_report.json` with 0 errors and 0 warnings.

### Step 4 — research-papers

Skipped: stt-benchmark-run task type does not list research-papers as an optional step.

### Step 5 — research-internet

Skipped: stt-benchmark-run task type does not list research-internet as an optional step.

### Step 11 — creative-thinking

Skipped: stt-benchmark-run task type does not list creative-thinking as an optional step.

### Step 3 — init-folders

Mandatory task folder structure created (12 directories with .gitkeep files) via `init_task_folders`
script; key output is `logs/steps/003_init-folders/folders_created.txt`. Aggregator cache populated
in `tasks/t0007_ibm_granite_4_1_benchmark/ctx/` (task_types.json, costs.json, tasks.json,
metrics.json, suggestions.json) for subagent reuse throughout the task.

### Step 6 — research-code

Reviewed all completed task code (t0001, t0002, t0004, t0005) — no registered libraries exist in
this project; all harness code must be copied from t0004 into `code/`. Primary reuse target is t0004
with five files identified: `load_dataset.py`, `compute_metrics_biased.py`, `constants.py`,
`write_predictions.py`, and `run_whisper_biased.py`. Baseline to beat: 94.5% domain-vocab entity
accuracy, 8.5% WER, 6.66s p50 latency (Whisper large-v3 + initial_prompt). Research summary
compressed to `research/research_summary.md` (6.5 KB) for downstream agent use.

### Step 7 — planning

Plan written to `plan/plan.md` covering two Granite Speech 4.1 2B inference runs (no-biasing and
31-term keyword-biased) on gold-92. Key decision: copy 4 scripts verbatim from t0004 and write 2 new
Granite-specific inference scripts; Granite keyword biasing API parameter is unconfirmed and flagged
as top risk requiring explicit verification in Step 3 of the plan. Verificator passed with zero
errors and zero warnings.

* * *

## Cross-Step Decisions

GPU tier: A100 80 GB required for Granite Speech 4.1 2B inference; estimated $3-8 compute cost
authorized against $1997.50 remaining budget.

* * *

## Next Step Notes

Step 7 (planning) completed with `plan/plan.md` verified clean. Proceed to step 8 (setup-machines):
provision an A100 80 GB GPU instance (or H100 with 6-8 GB VRAM minimum) per `## Remote Machines` in
`plan/plan.md`. The implementation agent will need to confirm the Granite keyword biasing API
parameter before writing `run_granite_biased.py` — this is flagged as the top implementation risk.
Load `plan/plan.md` for full GPU and environment setup requirements including the HuggingFace model
ID `ibm-granite/granite-speech-4.1-2b` and required Python dependencies.
