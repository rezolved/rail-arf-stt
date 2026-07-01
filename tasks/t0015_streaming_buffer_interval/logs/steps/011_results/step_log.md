---
spec_version: "3"
task_id: "t0015_streaming_buffer_interval"
step_number: 11
step_name: "results"
status: "completed"
started_at: "2026-07-01T07:52:40Z"
completed_at: "2026-07-01T08:05:00Z"
---
## Summary

Wrote all results files for the streaming buffer interval experiment: results_summary.md,
results_detailed.md, and fixed metrics.json to comply with the registered-metrics schema (removed
unregistered keys latency_p95_seconds, ttfd_p50_seconds, ttfd_p95_seconds, and extra variant-level
fields). Generated four PNG charts and wrote a comprehensive results_detailed.md with metrics
tables, analysis, examples, and task requirement coverage.

## Actions Taken

1. Ran `uv run python -m arf.scripts.utils.prestep t0015_streaming_buffer_interval results`.
2. Read existing `results/metrics.json` (12 variants from implementation step).
3. Ran verify_task_metrics — found 48 errors (unregistered keys, extra variant fields); fixed
   metrics.json to remove non-registered keys (latency_p95_seconds, ttfd_p50_seconds,
   ttfd_p95_seconds) and strip extra top-level variant fields (model, interval_ms, diagnostics).
4. Generated four charts via matplotlib: WER by model×interval, EA-DV by model×interval, latency p50
   by model×interval, TTFD p50 by model×interval; saved to results/images/.
5. Wrote results/results_summary.md with Summary, Metrics (7 bullets), and Verification sections.
6. Wrote results/results_detailed.md (spec_version: "2") with all mandatory and recommended sections
   including 13 concrete examples from actual prediction JSONL files.
7. Added missing ## Verification section to results_detailed.md after first verificator run.
8. Re-ran verify_task_metrics and verify_task_results — both PASSED (0 errors, 0 warnings).
9. Ran flowmark on both results markdown files.
10. Updated checkpoint.md and committed all work.

## Outputs

* `results/results_summary.md`
* `results/results_detailed.md`
* `results/metrics.json` (corrected — only registered metric keys, clean variant format)
* `results/images/wer_by_model_interval.png`
* `results/images/ea_dv_by_model_interval.png`
* `results/images/latency_p50_by_model_interval.png`
* `results/images/ttfd_p50_by_model_interval.png`
* `logs/steps/011_results/step_log.md`

## Issues

The implementation-step metrics.json included three unregistered metric keys (latency_p95_seconds,
ttfd_p50_seconds, ttfd_p95_seconds) and extra variant-level fields (model, interval_ms, diagnostics)
not allowed by the explicit variant format. These were removed from metrics.json. The p95 latency
and TTFD values are documented in results_detailed.md tables instead.
