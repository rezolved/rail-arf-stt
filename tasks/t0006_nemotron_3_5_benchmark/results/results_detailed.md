---
spec_version: "2"
task_id: "t0006_nemotron_3_5_benchmark"
date_completed: "2026-06-25"
---
# Results Detailed — NVIDIA Nemotron 3.5 ASR Benchmark on Gold-92

## Summary

NVIDIA Nemotron 3.5 ASR was benchmarked on all 93 gold-92 clips from Rezolve production
investor-relations sessions in two configurations: batch inference (no biasing) and streaming
with word boosting. Batch achieves WER=17.6% and entity accuracy=24.7%, both significantly
worse than the Whisper large-v3 baseline (8.5% WER, 46.0% EA). Word boosting degrades all
accuracy metrics vs. batch: EA drops from 24.7% to 18.7% (−6.0 pp), WER worsens from 17.6% to
19.9% (+2.3 pp), domain-vocab accuracy drops from 18.2% to 12.7% (−5.5 pp). Latency p50=0.72s
is within budget but not competitive with Granite biased (248 ms). Nemotron 3.5 is not
recommended for Rezolve production.

## Methodology

**Model**: NVIDIA Nemotron 3.5 ASR via NVIDIA NeMo / Riva NIM. Batch variant uses offline
inference; word-boosted variant uses streaming mode with the word-boosting API.

**Dataset**: 93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Ground truth from `ground_truth.jsonl`. Accent-group labelling from `gold_set.jsonl`:
34 production (accented), 46 clean-voice, 13 error-cases.

**Inference**: Per-clip wall-clock latency measured around the inference call. GPU server
execution. Latency p50/p95/p99 computed from all 93 clips (no warmup exclusion — batch mode).

**Evaluation**: Entity accuracy computed against entity spans from `ground_truth.jsonl`.
Domain-vocabulary accuracy evaluated against DOMAIN_VOCAB constant. WER computed with jiwer
after lowercasing and punctuation stripping. Anomaly clip `error_en_0005` (Cyrillic ground
truth) excluded from entity accuracy aggregates.

## Metrics Tables

### Primary metrics

| Metric | Nemotron batch | Nemotron word-boosted | Whisper (t0004) | Parakeet prod (t0009) |
| --- | --- | --- | --- | --- |
| entity_accuracy_gold92 | 24.7% | 18.7% | 46.0% | 23.2% |
| entity_accuracy_domain_vocab | 18.2% | 12.7% | 94.5% | 33.3% |
| wer_gold92 | 17.6% | 19.9% | 8.5% | 15.2% |
| action_critical_wer_gold92 | 31.6% | 42.4% | 2.5% | 33.5% |
| intent_preservation_gold92 | 90.3% | 84.9% | 98.9% | 87.1% |
| latency_p50_seconds | 0.719s | 0.723s | 6.66s | 0.038s |

### Word-boosting degradation

| Metric | Delta (word-boosted vs. batch) |
| --- | --- |
| ΔWER | +2.3 pp |
| ΔEntity accuracy | −6.0 pp |
| ΔDomain-vocab accuracy | −5.5 pp |
| ΔAction-critical WER | +10.8 pp |
| ΔIntent preservation | −5.4 pp |

## Comparison vs. Baselines

**vs. Whisper large-v3 + initial_prompt (t0004 production reference):**

Nemotron 3.5 batch is substantially worse across all accuracy metrics. WER is 2× higher
(17.6% vs. 8.5%). Entity accuracy is 21 pp lower (24.7% vs. 46.0%). Domain-vocab accuracy
is 76 pp lower (18.2% vs. 94.5%). The only advantage is latency: 0.72s vs. 6.66s (9× faster),
though this is irrelevant given the accuracy gap.

**vs. Parakeet TDT 0.6b-v3 production (t0009):**

Nemotron 3.5 batch is marginally better on entity accuracy (+1.5 pp: 24.7% vs. 23.2%) and
intent preservation (+3.2 pp), but worse on domain-vocab accuracy (18.2% vs. 33.3%) and WER
(17.6% vs. 15.2%). Latency is 19× higher (0.72s vs. 0.038s). Nemotron offers no compelling
advantage over Parakeet.

## Analysis

**Word boosting is counter-productive.** Across all metrics, word boosting degrades performance
vs. batch. This is unexpected — the mechanism is documented to improve domain-vocabulary recall.
Likely causes: (1) the word-boosting API inserts hypothesised tokens that disturb the LM's
language model probabilities; (2) the domain vocabulary terms in Rezolve's use case include
multi-token entities that the word-boosting API handles differently from single-token words;
(3) streaming mode itself introduces accuracy penalties relative to offline batch.

**Entity accuracy is low even in batch mode.** 24.7% overall entity accuracy indicates the
model's base vocabulary coverage of Rezolve domain terms (brands, SKUs, products) is poor.
Unlike Granite Speech 4.1 2B, there is no observed improvement path via keyword biasing.

**Latency is acceptable but not decisive.** p50=0.72s is within the 800 ms voice-to-action
budget. However, this advantage is negated by the accuracy deficits relative to Granite biased
(248 ms, 40.2% EA).

## Limitations

- No per-accent-group breakdowns produced (code lacks accent-group split).
- Latency statistics have p50=p95=p99 (all identical), suggesting the measurement captures
  only average per-clip time without distributional variance across clips; this may be a
  measurement artefact in the run script.
- Word-boosting failure cause not diagnosed at code level; further debugging needed to confirm
  if it is an API usage issue or a fundamental limitation.

## Verification

- All 93 clips transcribed in both batch and word-boosted runs (0 failures)
- metrics.json written with both variants plus Whisper baseline reference
- `ruff check tasks/t0006_nemotron_3_5_benchmark/code/` — PASSED

## Files Created

- `results/metrics.json` — metrics for both variants + Whisper reference
- `results/results_summary.md` — this summary
- `results/results_detailed.md` — this file
- `data/nemotron_batch_transcripts.json` — 93 per-clip transcripts, batch mode
- `data/nemotron_word_boosted_transcripts.json` — 93 per-clip transcripts, word-boosted
- `data/analysis_output.json` — per-clip analysis with accent group
- `assets/predictions/nemotron-3.5-asr-gold92-batch/` — prediction asset, batch variant
- `assets/predictions/nemotron-3.5-asr-gold92-word-boosted/` — prediction asset, word-boosted

## Next Steps

- Investigate word-boosting failure: inspect API call parameters vs. NeMo documentation.
- Consider Nemotron fine-tuning on Rezolve domain data if word boosting is confirmed broken.
- Prioritise Granite Speech 4.1 2B biased as the current best candidate; Nemotron 3.5 is
  deprioritised pending investigation of the word-boosting issue.
