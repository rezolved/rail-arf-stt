# Results Summary: Streaming Buffer Interval Experiment — Parakeet Variants + Granite

## Summary

Benchmarked 12 model × buffer-interval combinations (4 models × 3 intervals: 500 ms, 750 ms, 1000
ms) on gold-92 (93 clips). Granite Speech 4.1 2B achieved the best transcription quality (**WER
8.83%**, **EA-DV 97.1%**), far ahead of all three Parakeet models (~22–33% EA-DV). Buffer interval
has **no effect on transcript quality** (WER and EA-DV are identical across all three intervals for
every model) but slightly reduces latency for larger intervals (up to 10% for Granite). All twelve
variants beat the t0014 accumulate-then-transcribe Granite TTFD baseline (**77 ms p50**) on either
latency or TTFD.

## Metrics

* **Best WER**: Granite Speech 4.1 2B — **8.83%** (all three intervals, vs 8.8% t0014 baseline —
  effectively tied)
* **Best EA-DV**: Granite Speech 4.1 2B — **97.1%** (vs 97.1% t0014 baseline — identical)
* **Fastest TTFD p50**: Parakeet-TDT — **32 ms** (vs 77 ms Granite t0014; 2.4× faster first-decode)
* **Lowest latency p50**: Parakeet-TDT — **250 ms** at 1000 ms interval (vs 1.23 s for Granite 500
  ms — 4.9× faster)
* **Interval effect on WER**: **0% change** across 500/750/1000 ms for all four models
* **Interval effect on latency**: up to **9.6% reduction** for Granite (1231 ms → 1113 ms p50, 500 →
  1000 ms); Parakeet models see 2–4% reduction
* **Granite streaming latency vs target**: Granite p50 latency 1.1–1.2 s exceeds 800 ms target; all
  Parakeet models remain well under 800 ms

## Verification

* `verify_task_metrics.py` — PASSED (0 errors, 0 warnings)
* `verify_predictions_asset.py` — PASSED for all 4 assets (0 errors each)
* `verify_predictions_description.py` — PASSED for all 4 assets
* `verify_predictions_details.py` — PASSED for all 4 assets
* `verify_task_results.py` — PASSED (0 errors, 0 warnings)
