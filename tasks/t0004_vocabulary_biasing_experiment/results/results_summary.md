# t0004 Results Summary — Vocabulary Biasing Experiment

## Summary

Injecting a 31-term domain vocabulary via Whisper's `initial_prompt` parameter produces a **4–5×
improvement in domain-entity accuracy** (18% → 87–95%) with no WER degradation. Action-Critical WER
dropped from 30% to 2.5% (large-v3 biased), approaching the project success criterion of <2%
wrong-action rate. Moonshine base is 80× faster (p50 70ms) but significantly weaker on this domain.

## Metrics

- **entity_accuracy_domain_vocab**: 18.2% → 94.5% (large-v3 biased), 87.3% (turbo biased) — 4–5×
  improvement; 10.9% for Moonshine base (weaker)
- **entity_accuracy_gold92**: 25.2% → 46.0% (large-v3 biased), 43.1% (turbo biased); 21.7% Moonshine
  base
- **wer_gold92**: 10.0% → 8.5% (large-v3 biased), 10.6% → 8.3% (turbo biased); 18.4% Moonshine base
  — biasing does not hurt WER
- **action_critical_wer_gold92**: 30.4% → 2.5% (large-v3 biased), 5.1% (turbo biased); 41.1%
  Moonshine base
- **intent_preservation_gold92**: 90.3% → 98.9% (large-v3 biased), 96.8% (turbo biased); 84.9%
  Moonshine base
- **latency_p50_seconds**: 5.66s (large-v3) / 4.25s (turbo) baseline; 6.66s / 5.86s biased; 0.07s
  Moonshine base

| Variant | EA gold-92 | EA DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Whisper large-v3 (baseline) | 25.2% | 18.2% | 10.0% | 30.4% | 90.3% | 5.66s |
| **Whisper large-v3 + bias** | **46.0%** | **94.5%** | 8.5% | **2.5%** | **98.9%** | 6.66s |
| Whisper turbo (baseline) | 25.2% | 18.2% | 10.6% | 30.4% | 90.3% | 4.25s |
| **Whisper turbo + bias** | **43.1%** | **87.3%** | 8.3% | **5.1%** | **96.8%** | 5.86s |
| Moonshine base (no bias) | 21.7% | 10.9% | 18.4% | 41.1% | 84.9% | 0.07s |

## Verification

All verificators passed:

- `verify_predictions`: 0 errors for all 3 prediction assets (whisper-large-v3-biased,
  whisper-turbo-biased, moonshine-base-gold92); 1 warning PR-W014 (no linked model asset —
  acceptable for this task)
- `verify_task_metrics`: 0 errors, 0 warnings (after registering `entity_accuracy_domain_vocab`
  metric)
- `mypy`: 0 issues found in task code package
- `ruff`: 0 errors after auto-fix
