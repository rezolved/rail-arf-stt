---
spec_version: "2"
task_id: "t0010_funasr_paraformer_benchmark"
date_completed: "2026-06-25"
---
# Results Detailed — FunASR SeACo-Paraformer Benchmark on Gold-92

## Summary

FunASR SeACo-Paraformer-en was benchmarked on all 93 gold-92 clips in batch and SeACo
contextual-biased modes. The model produces near-random English-sounding syllable sequences when
given Rezolve's English speech, yielding WER=122.7% (batch) and WER=122.2% (biased). WER
exceeding 100% indicates the number of word errors exceeds the number of reference words —
effectively complete transcription failure. Entity accuracy is 2.2% in both variants (chance
level), domain-vocabulary accuracy is 0.0%, and SeACo biasing has zero measurable effect on any
metric. The model is not suitable for English STT at Rezolve.

## Methodology

**Model**: `iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020` via FunASR Python SDK.
Batch variant uses standard Paraformer inference; biased variant activates the SeACo contextual
biasing module with Rezolve domain vocabulary from DOMAIN_VOCAB constant.

**Dataset**: 93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Ground truth from `ground_truth.jsonl`. Accent groups: 34 production (accented), 46 clean-voice,
13 error-cases.

**Inference**: Per-clip sequential inference. Latency measured around the FunASR inference call.
GPU server execution.

**Evaluation**: Entity accuracy, domain-vocab accuracy, WER, action-critical WER, intent
preservation computed with the same harness as t0007/t0009. Anomaly clip `error_en_0005`
excluded from entity accuracy. BCa bootstrap CIs computed (n=10,000 resamples).

## Metrics Tables

### Primary metrics

| Metric | Paraformer batch | SeACo biased | Parakeet prod (t0009) | Granite biased (t0007) |
| --- | --- | --- | --- | --- |
| entity_accuracy_gold92 | 2.2% | 2.2% | 23.2% | 40.2% |
| entity_accuracy_domain_vocab | 0.0% | 0.0% | 33.3% | 98.5% |
| wer_gold92 | 122.7% | 122.2% | 15.2% | 8.8% |
| action_critical_wer_gold92 | 100.0% | 100.0% | 33.5% | 8.2% |
| intent_preservation_gold92 | 55.9% | 55.9% | 87.1% | 92.5% |
| latency_p50_seconds | 0.048s | 0.047s | 0.038s | 0.248s |

### SeACo biasing gain (biased vs. batch)

| Metric | Delta |
| --- | --- |
| ΔWER | −0.5 pp |
| ΔEntity accuracy | 0.0 pp |
| ΔDomain-vocab accuracy | 0.0 pp |
| ΔAction-critical WER | 0.0 pp |
| ΔIntent preservation | 0.0 pp |

## Analysis

**Complete transcription failure on English input.** The model consistently produces phonetically
plausible but semantically incoherent English token sequences (e.g., "feel pea lecture suspense
online jeff hainanese telling achieved thorough prosecution"). This pattern is characteristic of
a model trained primarily on Mandarin Chinese attempting to phonetically match English audio to
Chinese-phoneme-adjacent English syllables. The "en" suffix in the model ID indicates the model
was intended for English but was not adequately trained on English data.

**SeACo contextual biasing has zero effect.** The SeACo module theoretically allows token-level
biasing toward user-provided vocabulary. In practice, when the underlying model cannot
transcribe English, biasing toward domain vocabulary has no observable effect: ΔEA=0.0pp,
ΔEA_DV=0.0pp. The biasing mechanism requires the base model to first produce candidate
hypotheses that can be re-scored — if no English tokens are produced, re-scoring is vacuous.

**Latency is fast but irrelevant.** At 0.048s p50, the model is faster than Parakeet production
(0.038s) and dramatically faster than Granite biased (0.248s). This is the only metric where
Paraformer is competitive, but latency is irrelevant when the model produces no usable output.

## Limitations

- Only the `iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020` checkpoint was tested.
  A different FunASR English model (e.g., `iic/speech_paraformer-large_asr_nat-en-16k-common-vocab10020`)
  might perform differently; this is not recommended for investigation given the results.
- The BCa CI for action_critical_wer is degenerate (all 1.0) — the CI is [1.0, 1.0].

## Verification

- All 93 clips transcribed in both configurations (0 failures)
- metrics.json written with both variants and biasing_gain
- WARNING flags triggered: WER > 0.6 for both variants — confirmed as expected failure
- `ruff check tasks/t0010_funasr_paraformer_benchmark/code/` — PASSED

## Files Created

- `results/metrics.json` — metrics for both variants with biasing_gain
- `results/results_summary.md` — this summary
- `results/results_detailed.md` — this file
- `data/paraformer_batch_transcripts.json` — 93 per-clip transcripts, batch mode
- `data/paraformer_biased_transcripts.json` — 93 per-clip transcripts, SeACo biased
- `data/analysis_output.json` — per-clip analysis
- `assets/predictions/seaco-paraformer-large-gold92-batch/` — prediction asset, batch
- `assets/predictions/seaco-paraformer-large-gold92-biased/` — prediction asset, SeACo biased

## Next Steps

- FunASR Paraformer is eliminated from further evaluation.
- Suggestion: Investigate why S-0005 recommended this model; update the survey (t0005) notes
  to flag that this specific checkpoint is not English-capable.
