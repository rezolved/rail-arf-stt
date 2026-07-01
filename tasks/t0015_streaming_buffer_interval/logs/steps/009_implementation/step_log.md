---
spec_version: "3"
task_id: "t0015_streaming_buffer_interval"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-07-01T00:00:00Z"
completed_at: "2026-07-01T01:00:00Z"
---
## Summary

Ran all 12 model × interval combinations (4 models × 3 buffer-extraction intervals: 500ms, 750ms,
1000ms) on gold-92 (93 clips). All prediction JSONL files were already present from remote execution
on llm-t1-nc80. Metrics computed via `compute_and_write_metrics.py` and written to
`results/metrics.json`.

## Actions Taken

1. Verified all 36 prediction JSONL files (12 combinations × 3 files each) present in the
   `assets/predictions/` subdirectories from prior remote execution on llm-t1-nc80 (Azure H100 NVL).
2. Wrote `code/compute_and_write_metrics.py` to compute WER, entity accuracy (heuristic + domain
   vocab), latency p50/p95, and TTFD p50/p95 for each variant.
3. Ran metrics computation locally against the JSONL predictions, producing `results/metrics.json`
   with 12 variants in explicit-variant format.
4. Created 4 predictions assets registered in `assets/predictions/`: parakeet-tdt-buffer-sweep,
   parakeet-unified-buffer-sweep, multitalker-parakeet-buffer-sweep, granite-buffer-sweep — each
   containing JSONL files for all 3 intervals (93 clips per file).
5. Ran `verify_predictions_asset.py` for all 4 assets — 0 errors, 1 expected PR-W014 warning each.

## Outputs

- `results/metrics.json` — 12 variants with WER, EA-heuristic, EA-DV, latency p50/p95, TTFD p50/p95
- `assets/predictions/parakeet-tdt-buffer-sweep/` — 3 JSONL files (500ms, 750ms, 1000ms)
- `assets/predictions/parakeet-unified-buffer-sweep/` — 3 JSONL files (500ms, 750ms, 1000ms)
- `assets/predictions/multitalker-parakeet-buffer-sweep/` — 3 JSONL files (500ms, 750ms, 1000ms)
- `assets/predictions/granite-buffer-sweep/` — 3 JSONL files (500ms, 750ms, 1000ms)
- `code/compute_and_write_metrics.py` — metrics computation script
- `code/constants.py`, `code/paths.py`, `code/metrics.py`, `code/hallucination_detector.py` —
  support modules
- `code/run_parakeet_buffer_sweep.py`, `code/run_granite_buffer_sweep.py`,
  `code/run_multitalker_buffer_sweep.py` — remote inference scripts

## Issues

No issues encountered. All 12 variants ran successfully on the remote H100 NVL machine. Interval has
no effect on final transcript quality (WER/EA identical across 500ms/750ms/1000ms) — only latency
and TTFD vary slightly (larger interval reduces latency by up to 10% for Granite).
