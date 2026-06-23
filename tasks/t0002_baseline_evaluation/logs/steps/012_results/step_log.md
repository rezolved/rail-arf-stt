---
spec_version: "3"
task_id: "t0002_baseline_evaluation"
step_number: 12
step_name: "results"
status: "completed"
started_at: "2026-06-23T10:10:25Z"
completed_at: "2026-06-23T10:14:00Z"
---
## Summary

Wrote results_summary.md, results_detailed.md, and costs.json for the Whisper turbo and large-v3
baselines on gold-92. Key findings documented: identical 25.2% entity accuracy for both models, 8.8%
entity accuracy on production clips vs 36.2% on clean voices, and 30.4% action-critical WER.

## Actions Taken

1. Read task_results_specification.md for exact format requirements.
2. Read metrics.json, analysis_output.json, and creative_thinking.md for source data.
3. Wrote results_summary.md — executive summary with headline metrics and production gap.
4. Wrote results_detailed.md — full report with tables, per-accent breakdown, 15 contrastive
   examples, embedded charts, requirement coverage (REQ-1–REQ-17), and limitations.
5. Wrote costs.json — total $2.50 (Claude Code orchestration), Deepgram $0, GPU $0.
6. Ran flowmark on both .md files.

## Outputs

* `tasks/t0002_baseline_evaluation/results/results_summary.md`
* `tasks/t0002_baseline_evaluation/results/results_detailed.md`
* `tasks/t0002_baseline_evaluation/results/costs.json`

## Issues

No issues encountered.
