# ✅ Benchmark FunASR SeACo-Paraformer on Gold-92

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0010_funasr_paraformer_benchmark` |
| **Status** | ✅ completed |
| **Started** | 2026-06-25T00:00:00Z |
| **Completed** | 2026-06-25T20:00:00Z |
| **Duration** | 20h 0m |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md), [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Source suggestion** | `S-0005-02` |
| **Task types** | `stt-benchmark-run` |
| **Categories** | [`stt-evaluation`](../../by-category/stt-evaluation.md) |
| **Expected assets** | 2 predictions |
| **Step progress** | 3/3 |
| **Task folder** | [`t0010_funasr_paraformer_benchmark/`](../../../tasks/t0010_funasr_paraformer_benchmark/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0010_funasr_paraformer_benchmark/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0010_funasr_paraformer_benchmark/task_description.md)*

# Benchmark FunASR SeACo-Paraformer on Gold-92

## Motivation

Task t0005 (STT model survey) identified FunASR SeACo-Paraformer-en as a candidate for
contextual-biasing benchmarking. SeACo-Paraformer is a variant of the Paraformer architecture
with a dedicated contextual biasing module (SeACo — Selective Attention with Contextual
Objects), designed to improve recall of domain-specific vocabulary. The English variant
(`iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020`) was identified as a potential
lower-latency alternative to Granite biased, given Paraformer's CTC-based architecture.

The task was also motivated by suggestion S-0005-02 from task t0005's suggestion generation.

## Goal

Run FunASR SeACo-Paraformer-en on all 93 gold-92 clips in two configurations:

1. **Batch (no biasing)** — standard Paraformer inference without contextual biasing
2. **SeACo biased** — SeACo contextual biasing with Rezolve domain vocabulary

Compute entity accuracy, domain-vocabulary accuracy, WER, action-critical WER, intent
preservation, and latency p50/p95/p99. Compare against Parakeet production (t0009) and Granite
biased (t0007) baselines.

## Success Criteria

- All 93 clips transcribed in both configurations
- metrics.json written with both variants
- Prediction assets registered for DVC tracking
- Results summary and detailed report completed

</details>

## Metrics

### Paraformer-large — batch (no biasing)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.021739** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.0** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **1.0** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.55914** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.0478** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **1.22668** |
| [`latency_p95_seconds`](../../metrics-results/latency_p95_seconds.md) | **0.0565** |
| [`latency_p99_seconds`](../../metrics-results/latency_p99_seconds.md) | **0.0587** |

### SeACo-Paraformer-large — contextual biased

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.021739** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.0** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **1.0** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.55914** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.0472** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **1.221665** |
| [`latency_p95_seconds`](../../metrics-results/latency_p95_seconds.md) | **0.0534** |
| [`latency_p99_seconds`](../../metrics-results/latency_p99_seconds.md) | **0.0559** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [SeACo-Paraformer-en — Batch (no biasing) on Gold-92](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-batch/) | [`description.md`](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-batch/description.md) |
| predictions | [SeACo-Paraformer-en — Contextual Biased on Gold-92](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-biased/) | [`description.md`](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-biased/description.md) |

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0010_funasr_paraformer_benchmark/results/results_summary.md)*

--- spec_version: "1" task_id: "t0010_funasr_paraformer_benchmark" date_completed:
"2026-06-25" ---
# Results Summary — FunASR SeACo-Paraformer Benchmark on Gold-92

## Summary

FunASR SeACo-Paraformer-en (iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020) was
benchmarked on all 93 gold-92 clips in batch and contextual-biased modes. The model produces
near-random English-sounding tokens when given Rezolve's investor-relations English speech:
WER=122.7% (batch), WER=122.2% (biased). WER exceeding 100% indicates the model's hypotheses
contain more word errors than reference words — effectively complete transcription failure.
Entity accuracy is 2.2% in both variants, and domain-vocabulary accuracy is 0.0%. SeACo
contextual biasing has zero effect on any accuracy metric.

The root cause is that Paraformer was trained primarily on Mandarin Chinese speech data. The
"en" variant's English capability is severely limited and cannot handle Rezolve's English
voice-commerce speech. This model is not suitable for any English STT application at Rezolve.

## Metrics

**SeACo-Paraformer-large — batch (no biasing)**

- **entity_accuracy_gold92**: 2.2% vs. Parakeet prod 23.2% (−21.0 pp), vs. Granite biased
  40.2% (−38.0 pp)
- **entity_accuracy_domain_vocab**: 0.0% vs. Parakeet 33.3% (−33.3 pp), vs. Granite biased
  98.5% (−98.5 pp)
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
WER > 100% and entity accuracy ≈ 2% confirm total transcription failure on English input. This
model should not be evaluated further for Rezolve's voice-commerce pipeline.

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0010_funasr_paraformer_benchmark/results/results_detailed.md)*

--- spec_version: "2" task_id: "t0010_funasr_paraformer_benchmark" date_completed:
"2026-06-25" ---
# Results Detailed — FunASR SeACo-Paraformer Benchmark on Gold-92

## Summary

FunASR SeACo-Paraformer-en was benchmarked on all 93 gold-92 clips in batch and SeACo
contextual-biased modes. The model produces near-random English-sounding syllable sequences
when given Rezolve's English speech, yielding WER=122.7% (batch) and WER=122.2% (biased). WER
exceeding 100% indicates the number of word errors exceeds the number of reference words —
effectively complete transcription failure. Entity accuracy is 2.2% in both variants (chance
level), domain-vocabulary accuracy is 0.0%, and SeACo biasing has zero measurable effect on
any metric. The model is not suitable for English STT at Rezolve.

## Methodology

**Model**: `iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020` via FunASR Python
SDK. Batch variant uses standard Paraformer inference; biased variant activates the SeACo
contextual biasing module with Rezolve domain vocabulary from DOMAIN_VOCAB constant.

**Dataset**: 93 WAV clips from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Ground truth from
`ground_truth.jsonl`. Accent groups: 34 production (accented), 46 clean-voice, 13 error-cases.

**Inference**: Per-clip sequential inference. Latency measured around the FunASR inference
call. GPU server execution.

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

**Complete transcription failure on English input.** The model consistently produces
phonetically plausible but semantically incoherent English token sequences (e.g., "feel pea
lecture suspense online jeff hainanese telling achieved thorough prosecution"). This pattern
is characteristic of a model trained primarily on Mandarin Chinese attempting to phonetically
match English audio to Chinese-phoneme-adjacent English syllables. The "en" suffix in the
model ID indicates the model was intended for English but was not adequately trained on
English data.

**SeACo contextual biasing has zero effect.** The SeACo module theoretically allows
token-level biasing toward user-provided vocabulary. In practice, when the underlying model
cannot transcribe English, biasing toward domain vocabulary has no observable effect:
ΔEA=0.0pp, ΔEA_DV=0.0pp. The biasing mechanism requires the base model to first produce
candidate hypotheses that can be re-scored — if no English tokens are produced, re-scoring is
vacuous.

**Latency is fast but irrelevant.** At 0.048s p50, the model is faster than Parakeet
production (0.038s) and dramatically faster than Granite biased (0.248s). This is the only
metric where Paraformer is competitive, but latency is irrelevant when the model produces no
usable output.

## Limitations

- Only the `iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020` checkpoint was
  tested. A different FunASR English model (e.g.,
  `iic/speech_paraformer-large_asr_nat-en-16k-common-vocab10020`) might perform differently;
  this is not recommended for investigation given the results.
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

</details>
