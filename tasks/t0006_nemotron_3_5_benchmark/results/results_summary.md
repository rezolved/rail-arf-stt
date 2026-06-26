---
spec_version: "1"
task_id: "t0006_nemotron_3_5_benchmark"
date_completed: "2026-06-25"
---
# Results Summary — NVIDIA Nemotron 3.5 ASR Benchmark on Gold-92

## Summary

NVIDIA Nemotron 3.5 ASR was benchmarked on all 93 gold-92 clips in two configurations: batch
(no biasing) and streaming with word boosting. Batch WER=17.6% is 2× worse than the Whisper
large-v3 baseline (8.5%), and batch entity accuracy=24.7% is 21 pp below Whisper (46.0%). Word
boosting actively degrades performance relative to batch: ΔEA=−6.0 pp, ΔWER=+2.3 pp,
ΔEA_DV=−5.5 pp. Latency p50=0.72s is within the 800 ms voice-to-action budget but does not
offer a meaningful advantage over Granite biased (248 ms).

Nemotron 3.5 is not recommended for Rezolve production. Word boosting is the primary failure
mode — the mechanism degrades rather than improves domain-vocabulary accuracy, suggesting the
word-boosting API does not behave as documented for this domain. Without an effective biasing
mechanism, the model cannot meet Rezolve's entity accuracy requirements.

## Metrics

**Nemotron 3.5 ASR — batch (no biasing)**

- **entity_accuracy_gold92**: 24.7% vs. Whisper 46.0% (−21.3 pp), vs. Parakeet prod 23.2% (+1.5 pp)
- **entity_accuracy_domain_vocab**: 18.2% vs. Whisper 94.5% (−76.3 pp), vs. Parakeet 33.3% (−15.1 pp)
- **wer_gold92**: 17.6% vs. Whisper 8.5% (+9.1 pp), vs. Parakeet 15.1% (+2.5 pp)
- **action_critical_wer_gold92**: 31.6% vs. Whisper 2.5% (+29.1 pp), vs. Parakeet 33.5% (−1.9 pp)
- **intent_preservation_gold92**: 90.3% vs. Whisper 98.9% (−8.6 pp), vs. Parakeet 87.1% (+3.2 pp)
- **latency_p50_seconds**: 0.719s vs. Parakeet 0.038s (19× slower), vs. Whisper 6.66s (9× faster)

**Nemotron 3.5 ASR — streaming + word boosting**

- **entity_accuracy_gold92**: 18.7% vs. batch 24.7% (−6.0 pp) — word boosting degrades accuracy
- **entity_accuracy_domain_vocab**: 12.7% vs. batch 18.2% (−5.5 pp)
- **wer_gold92**: 19.9% vs. batch 17.6% (+2.3 pp) — word boosting worsens WER
- **action_critical_wer_gold92**: 42.4% vs. batch 31.6% (+10.8 pp)
- **intent_preservation_gold92**: 84.9% vs. batch 90.3% (−5.4 pp)
- **latency_p50_seconds**: 0.723s (≈ batch, no meaningful latency benefit from streaming mode)

**Word-boosting degradation (word-boosted vs. batch):**

- ΔWER: +2.3 pp
- ΔEntity accuracy: −6.0 pp
- ΔDomain-vocab accuracy: −5.5 pp

## Verdict

Nemotron 3.5 ASR is not suitable for Rezolve production: WER is 2× worse than Whisper, entity
accuracy is 21 pp below Whisper, and word boosting actively degrades all accuracy metrics.
