---
spec_version: "2"
task_id: "t0009_parakeet_production_baseline"
date_completed: "2026-06-25"
---
# Results Detailed — Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Summary

Parakeet TDT 0.6b-v3 is the current production STT model in Rezolve's brainpowa voice-commerce
pipeline. It was benchmarked on all 93 gold-92 clips in two configurations: unbiased (standard
inference) and biased (production config with keyword injection). Entity accuracy in production
config is 23.2%, domain-vocabulary accuracy is 33.3%, and action-critical WER is 33.5%.
Ultra-low latency (38 ms p50) is the model's primary strength. Keyword biasing as currently
deployed provides negligible benefit. This establishes the definitive production floor for all
subsequent benchmark comparisons.

## Methodology

**Model**: nvidia/parakeet-tdt-0.6b-v3 via NeMo / Riva SDK. Production config uses the same
keyword list as deployed in the brainpowa pipeline.

**Dataset**: 93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Ground truth from `ground_truth.jsonl`. Accent groups: 34 production (accented), 46 clean-voice,
13 error-cases.

**Inference**: Sequential per-clip. Per-clip wall-clock latency measured around the inference
call. GPU server execution.

**Evaluation**: Entity accuracy, domain-vocab accuracy, WER, action-critical WER, intent
preservation computed with the same harness as t0004 and t0006–t0010. Anomaly clip
`error_en_0005` excluded from entity accuracy.

## Metrics Tables

### Primary metrics

| Metric | Parakeet unbiased | Parakeet prod (biased) | Whisper (t0004) |
| --- | --- | --- | --- |
| entity_accuracy_gold92 | 23.4% | 23.2% | 46.0% |
| entity_accuracy_domain_vocab | 31.9% | 33.3% | 94.5% |
| wer_gold92 | 15.1% | 15.2% | 8.5% |
| action_critical_wer_gold92 | 34.2% | 33.5% | 2.5% |
| intent_preservation_gold92 | 87.1% | 87.1% | 98.9% |
| latency_p50_seconds | 0.039s | 0.038s | 6.66s |

### Biasing gain (biased vs. unbiased)

| Metric | Delta |
| --- | --- |
| ΔWER | +0.1 pp |
| ΔEntity accuracy | −0.2 pp |
| ΔDomain-vocab accuracy | +1.4 pp |

## Comparison vs. Baselines

**vs. Whisper large-v3 + initial_prompt (t0004):**

Parakeet is substantially worse on all accuracy metrics. Entity accuracy is 22.8 pp below
Whisper (23.2% vs. 46.0%). Domain-vocab accuracy is 61 pp below Whisper (33.3% vs. 94.5%).
Action-critical WER is 31 pp higher (33.5% vs. 2.5%). The only advantage is latency: 0.038s
vs. 6.66s (175× faster), which is the primary reason it is deployed in production.

## Analysis

**Keyword biasing is ineffective.** The production biasing config provides ΔEA_DV=+1.4 pp at
the cost of ΔEA=−0.2 pp and ΔWER=+0.1 pp. This is consistent with Parakeet's architecture:
the TDT (Token-and-Duration Transducer) model processes vocabulary injection differently from
encoder-decoder models. Keyword injection as currently configured does not meaningfully improve
entity recall for Rezolve domain vocabulary.

**Entity accuracy of 23.2% is the benchmark floor.** Any model benchmarked in tasks t0006–t0010
that cannot exceed 23.2% entity accuracy offers no improvement over the current production model.
Given the 38 ms p50 latency, a replacement model also needs to remain within the 800 ms budget.

**Latency is the model's strongest feature.** 38 ms p50 is dramatically faster than any other
benchmarked model. If entity accuracy can be improved via fine-tuning, Parakeet TDT remains a
compelling production option.

## Limitations

- No latency p95/p99 available in metrics.json (single latency value per clip).
- No per-accent-group breakdown produced; full accent-group analysis deferred.
- Biasing configuration matches current production deployment but has not been independently
  optimised for gold-92 vocabulary.

## Verification

- All 93 clips transcribed in both configurations (0 failures)
- metrics.json written with both variants
- `ruff check tasks/t0009_parakeet_production_baseline/code/` — PASSED

## Files Created

- `results/metrics.json` — metrics for both variants
- `results/results_summary.md` — this summary
- `results/results_detailed.md` — this file
- `data/parakeet_batch_transcripts.json` — 93 per-clip transcripts, unbiased mode
- `data/parakeet_biased_transcripts.json` — 93 per-clip transcripts, production config
- `data/analysis_output.json` — per-clip analysis
- `assets/predictions/parakeet-tdt-0.6b-v3-gold92-unbiased/` — prediction asset, unbiased
- `assets/predictions/parakeet-tdt-0.6b-v3-gold92-production/` — prediction asset, production config
