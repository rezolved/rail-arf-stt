---
spec_version: "1"
task_id: "t0009_parakeet_production_baseline"
date_completed: "2026-06-25"
---
# Results Summary — Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Summary

Parakeet TDT 0.6b-v3 (NVIDIA, current Rezolve production model) was benchmarked on all 93
gold-92 clips in unbiased and production-config (biased) modes. The production config achieves
entity accuracy=23.2%, domain-vocabulary accuracy=33.3%, WER=15.2%, and action-critical
WER=33.5% at p50 latency=38 ms. Keyword biasing in the production config provides negligible
benefit over unbiased: ΔEA=−0.2 pp, ΔEA_DV=+1.4 pp, ΔWER=+0.1 pp.

This baseline establishes the current production floor. All subsequent benchmark tasks
(t0006–t0010) report their metrics relative to this result. The key finding is that the
production model has very low entity accuracy (23.2%) and very high action-critical WER (33.5%),
confirming significant headroom for improvement.

## Metrics

**Parakeet TDT 0.6b-v3 — production config (biased)**

- **entity_accuracy_gold92**: 23.2% vs. Whisper large-v3 46.0% (−22.8 pp)
- **entity_accuracy_domain_vocab**: 33.3% vs. Whisper 94.5% (−61.2 pp)
- **wer_gold92**: 15.2% vs. Whisper 8.5% (+6.7 pp)
- **action_critical_wer_gold92**: 33.5% vs. Whisper 2.5% (+31.0 pp)
- **intent_preservation_gold92**: 87.1% vs. Whisper 98.9% (−11.8 pp)
- **latency_p50_seconds**: 0.038s vs. Whisper 6.66s (175× faster)

**Keyword-biasing gain (biased vs. unbiased):**

- ΔWER: +0.1 pp (no benefit)
- ΔEntity accuracy: −0.2 pp (marginal degradation)
- ΔDomain-vocab accuracy: +1.4 pp (minimal benefit)

## Verification

- All 93 clips transcribed in both unbiased and biased runs (0 failures)
- metrics.json written with both variants
- `ruff check tasks/t0009_parakeet_production_baseline/code/` — PASSED
