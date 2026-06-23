# Results Summary: Baseline Evaluation — Deepgram and Whisper on Gold-92

## Summary

Whisper turbo and Whisper large-v3 were benchmarked on the gold-92 STT dataset (93 clips from
Rezolve investor-relations production sessions). Both models produced **identical entity accuracy of
25.2%** with matching BCa 95% CIs, ruling out model size as the bottleneck. The production-session
subset scored only **8.8% entity accuracy**, exposing a severe gap between lab conditions and real
deployment. Deepgram Nova-2 could not be run due to a missing API key; the Whisper results stand as
the open-source baseline. The primary implication is that vocabulary biasing — not a larger model —
is the highest-ROI next step.

## Metrics

- **Entity accuracy (gold-92, both models)**: **25.2%** (95% BCa CI: 18.1%–33.7%)
- **WER — Whisper large-v3**: **10.0%** (95% BCa CI: 8.8%–14.6%)
- **WER — Whisper turbo**: **10.6%** (95% BCa CI: 8.9%–14.4%)
- **Action-critical WER (both models)**: **30.4%** — 3× higher than general WER, confirming domain
  entities are the failure locus
- **Intent preservation (both models)**: **90.3%** (95% BCa CI: 82.8%–95.7%) — likely over-estimated
  by the span-presence proxy
- **Latency p50 — Whisper turbo**: **4.25 s** vs. **5.66 s** for large-v3 (25% faster, same
  accuracy)
- **Entity accuracy — production clips only**: **8.8%** vs. **36.2%** for clean-voice recordings
- **Deepgram Nova-2**: not run — `DEEPGRAM_API_KEY` unavailable; significance test blocked (REQ-5
  partial)

## Verification

- `verify_task_metrics.py` — PASSED (2 variants, 5 metrics each, explicit variant format)
- `verify_plan.py` — PASSED (0 errors, 0 warnings at plan stage)
- Rejection criteria check — PASSED (WER well below 60% threshold; entity accuracy non-zero)
- `error_en_0005` Cyrillic anomaly — flagged and excluded from entity accuracy aggregate per plan
