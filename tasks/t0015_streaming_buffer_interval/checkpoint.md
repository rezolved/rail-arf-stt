---
spec_version: "1"
task_id: "t0015_streaming_buffer_interval"
updated_at: "2026-06-30T10:53:10Z"
completed_steps: 2
next_step_number: 3
next_step_id: "init-folders"
---
# Task Objective

Benchmark the effect of streaming buffer extraction interval (500ms, 750ms, 1000ms) on latency and
transcription quality across four models: parakeet-unified-en-0.6b, parakeet-tdt-0.6b-v3,
multitalker-parakeet-streaming-0.6b-v1, and Granite Speech 4.1 2B. All models biased with Rezolve
domain keyword list. Dataset: gold-92.

* * *

## Step History

### Step 2 — check-deps

Both dependencies verified as completed: t0014_granite_short_clip_robustness and
t0012_whisper_parakeet_granite_streaming. Output: `logs/steps/002_check-deps/deps_report.json`. No
errors or warnings.

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

Proceed to step 3 (init-folders): create the full task folder structure using init_task_folders.py,
then populate the aggregator cache (task_types.json, costs.json, tasks.json, metrics.json,
suggestions.json) in tasks/t0015_streaming_buffer_interval/ctx/. Step 8 (setup-machines) will
provision an H100 NVL GPU machine for inference — same configuration as t0014. Implementation will
run 4 models × 3 intervals = 12 combinations on gold-92.
