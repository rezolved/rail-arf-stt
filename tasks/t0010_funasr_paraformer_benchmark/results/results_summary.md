---
spec_version: "1"
task_id: "t0010_funasr_paraformer_benchmark"
date_completed: "2026-06-25"
---
# Results Summary — FunASR SeACo-Paraformer Benchmark on Gold-92

## Summary

FunASR SeACo-Paraformer-en (iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020) was
benchmarked on all 93 gold-92 clips in batch and contextual-biased modes. The model produces
near-random English-sounding tokens when given Rezolve's investor-relations English speech:
WER=122.7% (batch), WER=122.2% (biased). WER exceeding 100% indicates the model's hypotheses
contain more word errors than reference words — effectively complete transcription failure.
Entity accuracy is 2.2% in both variants, and domain-vocabulary accuracy is 0.0%. SeACo
contextual biasing has zero effect on any accuracy metric.

The root cause is that Paraformer was trained primarily on Mandarin Chinese speech data.
The "en" variant's English capability is severely limited and cannot handle Rezolve's
English voice-commerce speech. This model is not suitable for any English STT application
at Rezolve.

## Metrics

**SeACo-Paraformer-large — batch (no biasing)**

- **entity_accuracy_gold92**: 2.2% vs. Parakeet prod 23.2% (−21.0 pp), vs. Granite biased 40.2% (−38.0 pp)
- **entity_accuracy_domain_vocab**: 0.0% vs. Parakeet 33.3% (−33.3 pp), vs. Granite biased 98.5% (−98.5 pp)
- **wer_gold92**: 122.7% — WER > 100% indicates more errors than reference words
- **action_critical_wer_gold92**: 100.0% — all entity-containing clips fail
- **intent_preservation_gold92**: 55.9% — by chance token overlap only
- **latency_p50_seconds**: 0.048s — fast but irrelevant given transcription failure

**SeACo contextual biasing gain (biased vs. batch):**

- ΔWER: −0.5 pp (noise-level)
- ΔEntity accuracy: 0.0 pp (zero effect)
- ΔDomain-vocab accuracy: 0.0 pp (zero effect)

## Verdict

FunASR SeACo-Paraformer is completely unsuitable for English speech recognition at Rezolve.
WER > 100% and entity accuracy ≈ 2% confirm total transcription failure on English input.
This model should not be evaluated further for Rezolve's voice-commerce pipeline.
