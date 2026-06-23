---
spec_version: "3"
task_id: "t0004_vocabulary_biasing_experiment"
step_number: 12
step_name: "results"
status: "completed"
started_at: "2026-06-23T14:43:53Z"
completed_at: "2026-06-23T15:20:00Z"
---
## Summary

Wrote results_summary.md (headline metrics table, key findings, verification status),
results_detailed.md (full methodology, metrics table, confidence intervals, analysis by metric, 10
transcript examples with code blocks, limitations), costs.json ($0.00 CPU-only), and
remote_machines_used.json (empty). All registered metrics for all 5 variants are reported.
`verify_task_results` passed with 0 errors and 0 warnings.

## Actions Taken

1. Wrote `results/results_summary.md` with mandatory sections: Summary, Metrics (6 bullet metrics
   + full comparison table), Verification.
2. Wrote `results/results_detailed.md` with mandatory sections: Summary, Methodology, Full Metrics
   Table, Confidence Intervals, Analysis, Examples (10 examples with fenced code blocks),
   Limitations, Verification, Files Created.
3. Wrote `results/costs.json` — total cost $0.00, empty breakdown, note explaining CPU-only run.
4. Wrote `results/remote_machines_used.json` — empty array (no remote machines used).
5. Ran `uv run flowmark` on both markdown files.
6. Ran `verify_task_results` — passed with 0 errors, 0 warnings.

## Outputs

- `tasks/t0004_vocabulary_biasing_experiment/results/results_summary.md`
- `tasks/t0004_vocabulary_biasing_experiment/results/results_detailed.md`
- `tasks/t0004_vocabulary_biasing_experiment/results/costs.json`
- `tasks/t0004_vocabulary_biasing_experiment/results/remote_machines_used.json`

## Issues

No issues encountered.
