---
spec_version: "1"
task_id: "t0008_moonshine_v2_benchmark"
date_completed: "2026-06-25"
---
# Results Summary — Moonshine v2 Benchmark on Gold-92

## Summary

Moonshine v2 Medium (UsefulSensors/moonshine-streaming-medium, 266M params, CPU) was benchmarked on
all 93 gold-92 clips. It achieves WER=16.6% and entity accuracy (domain vocab) of 9.1%, both
significantly worse than the Whisper large-v3 baseline (8.5% WER, 94.5% domain-vocab entity
accuracy). Warmed latency p50 of 233ms is close to the 200ms target but does not meet it; cold-start
latency is 1.33s. Moonshine is not production-ready for Rezolve's voice commerce use case without
vocabulary biasing, but shallow-fusion is feasible (~15–25 hours effort, verdict: "needs research").

## Metrics

- **wer_gold92**: 16.6% (BCa 95% CI: 14.8%–22.6%) vs. Whisper baseline 8.5% — 2x worse
- **entity_accuracy_gold92**: 21.7% (BCa 95% CI: 15.0%–29.5%) vs. Whisper 46.0% — 24pp below
- **entity_accuracy_domain_vocab**: 9.1% (BCa 95% CI: 5.4%–27.0%) vs. Whisper 94.5% — 85pp below
- **action_critical_wer_gold92**: 34.2% (BCa 95% CI: 16.3%–30.6%) vs. Whisper 2.5% — 13x worse
- **intent_preservation_gold92**: 87.1% (BCa 95% CI: 78.5%–92.5%) vs. Whisper 98.9%
- **wrong_action_rate_gold92**: 12.9% (proxy: 1 − intent_preservation) vs. project threshold 2%
- **latency_p50_seconds**: 0.232s (full 93-clip median); warmed p50: 0.233s; cold-start: 1.33s

## Verification

- `verify_plan t0008_moonshine_v2_benchmark` — PASSED, 0 errors
- `verify_predictions_asset moonshine-v2-medium-gold92` — PASSED, 0 errors
- `verify_predictions_asset moonshine-v2-medium-gold92-biasing-assessment` — PASSED, 0 errors
- `verify_task_metrics t0008_moonshine_v2_benchmark` — PASSED, 0 errors
- `ruff check code/` — PASSED, 0 errors
- `mypy -p tasks.t0008_moonshine_v2_benchmark.code` — PASSED, 0 errors
