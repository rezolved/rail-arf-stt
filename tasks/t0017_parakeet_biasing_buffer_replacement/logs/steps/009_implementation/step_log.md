---
spec_version: "3"
task_id: "t0017_parakeet_biasing_buffer_replacement"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-07-01T21:22:00Z"
completed_at: "2026-07-02T11:30:00Z"
---
## Summary

Ran `code/run_parakeet_buffer_sweep.py` for both models across all 6 buffer intervals on gold-92
(93 clips), with GPU-PB TurboBias domain biasing. Mid-task, found and fixed a bug in
`expand_casing_variants()` and reran the full sweep.

## Actions Taken

1. Initial run (2026-07-01T21:22:45Z, `logs/run.log`): both models, all 6 intervals, 93 clips each,
   GPU-PB TurboBias confirmed built on both models.
2. Found bug: `expand_casing_variants()` used
   `phrase[:1].upper() + phrase[1:]` for its "capitalized" variant, which only capitalizes the
   first character of the whole phrase rather than each word — multi-word domain terms
   ("Salesforce Commerce Cloud", "Adobe Commerce", "Shopify Plus") never got a real title-case
   biasing variant.
3. Fixed to `phrase.title()` in `code/run_parakeet_buffer_sweep.py` (this task) and in the shared
   t0015 harness (`t0015_streaming_buffer_interval/code/run_parakeet_buffer_sweep.py` and
   `run_multitalker_buffer_sweep.py`), since both copies had the identical bug.
4. Reran preflight (`--limit 5`) to confirm the fix works, then reran the full sweep (both models,
   all 6 intervals, 93 clips each) on `gpu-azure` in the background
   (`/tmp/t0017_sweep_refix.log` on the remote).
5. Pulled updated `data/parakeet_{tdt,unified}/predictions_*.jsonl` back via rsync.

## Outputs

- `data/parakeet_tdt/predictions_{200,300,350,500,750,1000}ms.jsonl` (post-fix).
- `data/parakeet_unified/predictions_{200,300,350,500,750,1000}ms.jsonl` (post-fix).
- `logs/run.log` (pre-fix run, GPU-PB build proof — boosting tree structure unchanged by the fix).

## Issues

The casing-variant bug affected biasing quality for multi-word domain terms in both the initial
t0017 run and (independently) in t0015's original results, which were not rerun as part of this
task.
