---
spec_version: "1"
task_id: "t0015_streaming_buffer_interval"
updated_at: "2026-07-01T09:10:00Z"
completed_steps: 14
next_step_number: null
next_step_id: null
---
# Task Objective

Benchmark the effect of streaming buffer extraction interval (500ms, 750ms, 1000ms) on latency and
transcription quality across four models: parakeet-unified-en-0.6b, parakeet-tdt-0.6b-v3,
multitalker-parakeet-streaming-0.6b-v1, and Granite Speech 4.1 2B. All models biased with Rezolve
domain keyword list. Dataset: gold-92.

* * *

## Step History

### Step 11 — results

Wrote results_summary.md, results_detailed.md (spec_version: "2") with 4 charts, metrics tables, 13
concrete examples, and ## Task Requirement Coverage. Fixed metrics.json to remove unregistered keys
and extra variant fields; both verify_task_metrics and verify_task_results pass with 0 errors.

### Step 10 — teardown

Logged machine usage for llm-t1-nc80 (Azure H100 NVL reserved instance). Machine kept alive per
project policy — not deallocated. Updated `machine_log.json` with `total_duration_hours: 20.6` and
`total_cost_usd: 287.58`; created `results/costs.json` and `results/remote_machines_used.json`.
RM-E001 from `verify_machines_destroyed` is expected and documented in
`intervention/reserved_machine_not_destroyed.md`.

### Step 9 — implementation

Ran all 12 model × interval combinations (4 models × 3 intervals) on gold-92 (93 clips). All
prediction JSONL files were already present from remote execution on llm-t1-nc80 (Azure H100 NVL).
Computed WER, entity accuracy (heuristic + domain-vocab), latency p50/p95, and TTFD p50/p95 via
`compute_and_write_metrics.py`. Wrote `results/metrics.json` with 12 variants in explicit-variant
format. Created 4 predictions assets (parakeet-tdt-buffer-sweep, parakeet-unified-buffer-sweep,
multitalker-parakeet-buffer-sweep, granite-buffer-sweep), each with 3 interval JSONL files (93 clips
each). All 4 assets passed verificator (0 errors, 1 expected PR-W014 warning each).

Key results:
- Best WER: Granite 8.83% (all intervals), Parakeet-unified 9.53%
- Best EA-DV: Granite 97.10%, far ahead of Parakeet models (~33%)
- Fastest TTFD p50: Parakeet-TDT 32ms, Parakeet-unified 37ms, Multitalker 64ms, Granite 75-77ms
- Lowest latency: Parakeet-TDT / Multitalker ~250ms, Parakeet-unified ~350ms, Granite 1.1-1.2s
- Interval effect on latency: larger intervals slightly reduce latency (up to 10% for Granite)
- Quality invariant to interval: WER/EA identical across intervals (same final transcript)

### Step 8 — setup-machines

Reserved Azure H100 NVL machine (llm-t1-nc80, 2×H100 NVL, 880 GB RAM) verified live via SSH. All
four models confirmed ready: parakeet-tdt-0.6b-v3 (pre-cached), parakeet-unified-en-0.6b
(downloaded), multitalker-parakeet-streaming-0.6b-v1 (downloaded), Granite Speech 4.1 2B
(pre-existing). GPU smoke gate: PASS. Machine log: `logs/steps/008_setup-machines/machine_log.json`.

### Step 3 — init-folders

Task folder structure created via init_task_folders: 12 directories with .gitkeep files and
`assets/predictions/` subdirectory matching expected_assets. Aggregator cache populated in
`tasks/t0015_streaming_buffer_interval/ctx/` (task_types.json, costs.json, tasks.json, metrics.json,
suggestions.json).

### Step 2 — check-deps

Both dependencies verified as completed: t0014_granite_short_clip_robustness and
t0012_whisper_parakeet_granite_streaming. Output: `logs/steps/002_check-deps/deps_report.json`. No
errors or warnings.

### Step 13 — suggestions

Skipped — per step_tracker.json: no suggestions step for this experiment task.

### Step 12 — compare-literature

Skipped — per step_tracker.json: no literature comparison needed for this interval experiment.

### Step 7 — planning

Skipped — experiment design provided directly by user; no planning step required.

### Step 6 — research-code

Skipped — codebase patterns established in t0012/t0014; no code research needed.

### Step 5 — research-internet

Skipped — models are known; no internet research needed.

### Step 4 — research-papers

Skipped — experiment design is fully specified; no paper research needed.

### Step 1 — create-branch

Branch `task/t0015_streaming_buffer_interval` created. Worktree initialized at
`rail-arf-stt-worktrees/t0015_streaming_buffer_interval`. Steps 4-7 (research-papers,
research-internet, research-code, planning) pre-marked as skipped per user instruction.

* * *

## Cross-Step Decisions

- Steps 4-7 skipped: experiment design fully specified by user, no research needed.
- Models: parakeet-unified-en-0.6b, parakeet-tdt-0.6b-v3, multitalker-parakeet-streaming-0.6b-v1,
  Granite Speech 4.1 2B.
- Intervals: 500ms, 750ms, 1000ms.
- Biasing: all models biased with Rezolve domain keyword list (Granite via keyword prompt, Parakeet
  variants via NeMo GPU-PB TurboBias).
- Dataset: gold-92 (93 clips).

* * *

### Step 14 — reporting

Ran all verificators: verify_task_file (pass, TF-W001 warning on long description),
verify_task_dependencies (pass), verify_suggestions (pass, created suggestions.json with 4
suggestions), verify_task_metrics (pass), verify_task_results (pass), verify_task_folder (pass),
verify_logs (pass after creating skipped step logs for steps 4-7, 12-13), verify_machines_destroyed
(expected RM-E001 documented in intervention/). Captured 10 session transcripts. Set task.json
status="completed", end_time="2026-07-01T09:10:00Z". Fixed source_suggestion from "user-direct" to
null.

## Next Step Notes

Task complete. All steps finished. Next action for coordinator: push branch, create PR, merge.
