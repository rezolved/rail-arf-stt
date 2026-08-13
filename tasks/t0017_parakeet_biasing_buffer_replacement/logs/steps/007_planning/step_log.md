---
spec_version: "3"
task_id: "t0017_parakeet_biasing_buffer_replacement"
step_number: 7
step_name: "planning"
status: "completed"
started_at: "2026-07-01T21:07:00Z"
completed_at: "2026-07-01T21:15:00Z"
---
## Summary

Planned a biased head-to-head sweep of `parakeet-tdt-0.6b-v3` (production) vs
`parakeet-unified-en-0.6b` (candidate) on gold-92, across an extended buffer-interval grid
(200/300/350/500/750/1000ms), reusing t0015's harness.

## Actions Taken

1. Defined scope: both models, all 6 intervals, single GPU session, GPU-PB TurboBias on for all
   runs (unbiased out of scope).
2. Decided to select the winner by WER + EA + EA-DV together, then run the fine buffer sweep on the
   winner only.

## Outputs

- `plan/plan.md`.

## Issues

No issues encountered.
