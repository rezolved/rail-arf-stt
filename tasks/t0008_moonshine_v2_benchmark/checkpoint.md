---
spec_version: "1"
task_id: "t0008_moonshine_v2_benchmark"
updated_at: "2026-06-25T09:01:00Z"
completed_steps: 10
next_step_number: 5
next_step_id: "implementation"
---
# Task Objective

Benchmark Moonshine v2 (CPU-only) on gold-92 to validate entity accuracy and latency without GPU
requirements, comparing entity recall and biasing feasibility vs. Whisper baseline.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0008_moonshine_v2_benchmark` created from main. Step plan written to
`step_tracker.json` (9 active steps: planning, implementation, results, compare-literature,
suggestions, reporting; 6 skipped: research-papers, research-internet, research-code,
setup-machines, teardown, creative-thinking). CPU-only task with no remote compute.

### Step 2 — check-deps

Both dependencies verified as completed: `t0001_stt_benchmark` and
`t0004_vocabulary_biasing_experiment`. Result written to
`logs/steps/002_check-deps/deps_report.json` with 0 errors and 0 warnings.

### Step 3 — init-folders

Task folder structure created (12 directories with `.gitkeep`); `__init__.py` and `code/__init__.py`
written. Aggregator cache populated in `ctx/` (5 files: task_types, costs, tasks, metrics,
suggestions). Key output: `logs/steps/003_init-folders/folders_created.txt`.

### Step 10 — research-papers

Skipped — no relevant papers in corpus for STT shallow-fusion benchmarking beyond t0004 and t0005.

### Step 11 — research-internet

Skipped — task scope is limited to benchmarking and feasibility assessment; sufficient domain
knowledge from t0004 and t0005.

### Step 12 — research-code

Skipped — task does not require research into prior task code; uses t0004 predictions and t0001
benchmark data directly.

### Step 13 — setup-machines

Skipped — all computation runs on local CPU; no remote machines required.

### Step 14 — teardown

Skipped — no remote machines to tear down.

### Step 15 — creative-thinking

Skipped — task scope is well-defined; creative alternatives addressed in planning phase.

### Step 4 — planning

Plan produced at `plan/plan.md` with 13 REQ items, 7 milestones, and 4 rejection criteria. Key
decision: wrong_action_rate_gold92 computed as `1 - intent_preservation` (proxy, documented). Two
prediction assets specified: batch-inference predictions and shallow-fusion feasibility doc.

* * *

## Cross-Step Decisions

- wrong_action_rate_gold92 metric will be computed as proxy `1 - intent_preservation_gold92` (no
  gold action labels available).
- Two prediction assets: `moonshine_v2_batch_predictions` (primary inference) and
  `moonshine_v2_shallow_fusion_feasibility` (feasibility assessment doc, not full inference run).
- Legacy flat metrics.json format (single run variant, all 7 registered keys).

* * *

## Next Step Notes

Step 4 (planning) completed — plan/plan.md verified with 0 errors. Proceed to step 5
(implementation): spawn a subagent to execute the `/implementation` skill. The implementation must
run Moonshine v2 Medium via OnnxRuntime CPU on all 93 gold-92 clips, compute all 7 registered
metrics, produce 2 prediction assets, and generate at least 2 charts in results/images/. Read
plan/plan.md for the full step-by-step, REQ checklist, and code design. Audio clips are in
tasks/t0001_stt_benchmark/. The 31-term biasing vocabulary is in t0004. Budget: $0 (CPU-only).
