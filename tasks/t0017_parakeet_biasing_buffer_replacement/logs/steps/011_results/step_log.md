---
spec_version: "3"
task_id: "t0017_parakeet_biasing_buffer_replacement"
step_number: 11
step_name: "results"
status: "completed"
started_at: "2026-07-02T11:30:00Z"
completed_at: "2026-07-02T11:50:00Z"
---
## Summary

Computed metrics from the post-fix predictions, regenerated charts, and updated
`results/results_detailed.md` and `results/results_summary.md` with the corrected numbers.

## Actions Taken

1. Ran `code/compute_and_write_metrics.py` against the post-fix prediction files, producing
   `results/metrics.json` (12 variants).
2. Ran `code/make_charts.py` to regenerate `results/images/*.png`.
3. Updated `results/results_detailed.md` and `results/results_summary.md` numbers (WER, EA, EA-DV,
   phrase-variant counts) to reflect the fix; conclusion (unified wins) unchanged.

## Outputs

- `results/metrics.json`.
- `results/images/{accuracy_comparison,reliability_comparison,winner_latency_by_interval,latency_comparison}.png`.
- `results/results_detailed.md`, `results/results_summary.md`.

## Issues

No issues encountered.
