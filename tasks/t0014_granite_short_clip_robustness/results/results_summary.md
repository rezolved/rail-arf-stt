# Results Summary: Granite Short-Clip Robustness Validation + Production Fit Assessment

## Summary

Granite Speech 4.1 2B achieves **0% empty output rate** on all short clips (0.5–3 s) compared to
Parakeet TDT 0.6b-v3's **27.3% failure rate** on sub-2 s clips (55.6% on sub-1 s), confirming
Granite avoids Parakeet's key short-clip failure mode. On the gold-92 benchmark Granite leads with
**entity accuracy 94.8%** vs Whisper 92.3% and Parakeet 65.0%, with a wrong-action rate of **1.1% vs
Parakeet's 30.1%**. The production recommendation is **CONDITIONAL YES**: replace Parakeet with
Granite in brainpowa, gating production use on a minimum 2.0 s clip duration to avoid the degenerate
single-chunk path that affects all Parakeet clips under 2 s.

## Metrics

- **Granite entity accuracy (gold-92, all strata)**: **94.8%** vs Parakeet **65.0%** vs Whisper
  **92.3%**
- **Granite empty rate (short clips, all bins)**: **0.0%** vs Parakeet **27.3%** (sub-2 s clips) vs
  Whisper **0.0%**
- **Granite wrong-action rate (gold-92)**: **1.1%** vs Parakeet **30.1%** vs Whisper **5.4%**
- **Granite entity accuracy domain vocab (gold-92)**: **96.7%** vs Parakeet **35.2%** vs Whisper
  **88.5%**
- **Granite WER (gold-92)**: **7.4%** vs Parakeet **16.3%** vs Whisper **7.7%**
- **Granite intent preservation (gold-92)**: **98.9%** vs Parakeet **67.7%** vs Whisper **94.6%**
- **Granite latency p50 (5–10 s stratum)**: **251 ms** vs Parakeet **41 ms** vs Whisper **330 ms**
- **Hallucination rate (all models, all clips)**: **0.0%** — no hallucinations detected

## Verification

- `verify_task_results` — PASSED (0 errors, 0 warnings)
- `verify_task_metrics` — PASSED (0 errors, 0 warnings)
- `verify_predictions_asset` (all 3 assets) — PASSED (0 errors)
- `verify_answer_asset` (`granite-vs-parakeet-production-fit`) — PASSED (0 errors)
