---
spec_version: "1"
task_id: "t0015_streaming_buffer_interval"
updated_at: "2026-06-30T10:59:00Z"
completed_steps: 9
next_step_number: 8
next_step_id: "setup-machines"
---
# Task Objective

Benchmark the effect of streaming buffer extraction interval (500ms, 750ms, 1000ms) on latency and
transcription quality across four models: parakeet-unified-en-0.6b, parakeet-tdt-0.6b-v3,
multitalker-parakeet-streaming-0.6b-v1, and Granite Speech 4.1 2B. All models biased with Rezolve
domain keyword list. Dataset: gold-92.

* * *

## Step History

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

## Next Step Notes

Proceed to step 8 (setup-machines): provision an H100 NVL GPU machine for inference, same
configuration as t0014_granite_short_clip_robustness. The ctx/ aggregator cache is pre-populated and
available for downstream subagents (do not re-run aggregators; read ctx/ files instead).
Implementation will run 4 models × 3 intervals = 12 experiment combinations on gold-92 (93 clips).
