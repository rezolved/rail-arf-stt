---
spec_version: "1"
task_id: "t0008_moonshine_v2_benchmark"
updated_at: "2026-06-25T10:10:00Z"
completed_steps: 13
next_step_number: 8
next_step_id: "suggestions"
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

### Step 5 — implementation

Full Moonshine v2 Medium benchmark completed. All 93 clips transcribed using
`UsefulSensors/moonshine-streaming-medium` (HuggingFace Transformers, CPU). Key finding: Moonshine
ONNX package only supports v1 (tiny/base); used the Transformers streaming-medium model as the v2
equivalent. All 7 metrics computed with BCa bootstrap CIs. 4 charts generated. 2 prediction assets
created and DVC-tracked. Shallow-fusion feasibility assessed (verdict: "needs research").

### Step 6 — results

All required results files written: results_summary.md, results_detailed.md (13-REQ coverage table,
10 examples, analysis), metrics.json (7 keys, all verified), costs.json ($0),
remote_machines_used.json ([]). `verify_task_results` and `verify_task_metrics` both passed.

* * *

## Cross-Step Decisions

- wrong_action_rate_gold92 metric computed as proxy `1 - intent_preservation_gold92` (no gold action
  labels available).
- Two prediction assets: `moonshine-v2-medium-gold92` (primary inference) and
  `moonshine-v2-medium-gold92-biasing-assessment` (feasibility assessment doc, not full inference
  run).
- Legacy flat metrics.json format (single run variant, all 7 registered keys).
- Model: moonshine_onnx only supports v1 tiny/base. Using `UsefulSensors/moonshine-streaming-medium`
  via HuggingFace Transformers (`MoonshineStreamingForConditionalGeneration`) as the v2 Medium
  equivalent. Documented in code/paths.py.

* * *

### Step 7 — compare-literature

`results/compare_literature.md` written and verified (0 errors, 0 warnings). Compared Moonshine v2
Medium against: (1) Kudlur2026 (arXiv 2602.12241): published WER=6.65% on Open ASR Leaderboard vs.
gold-92 WER=16.6% (+9.95pp domain mismatch); latency 258ms (ONNX/M3) vs. 232ms (Transformers/CPU),
directionally consistent. (2) t0004 Whisper large-v3 + initial_prompt: entity_accuracy_domain_vocab
94.5% vs. 9.1% (−85.4pp, biased vs. unbiased cross-model); latency 6.66s vs. 0.232s (Moonshine 29x
faster). (3) t0004 Moonshine base: entity_accuracy identical at 21.7% (0pp delta), confirming entity
failure is vocabulary-driven not capacity-driven. Key finding: v2 Medium adds no entity accuracy
over base despite 7x more parameters; biasing is required before Moonshine can serve as an edge
fallback.

## Next Step Notes

Step 7 (compare-literature) completed. Proceed to step 8 (suggestions).
