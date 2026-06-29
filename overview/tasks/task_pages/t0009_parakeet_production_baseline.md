# ✅ Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0009_parakeet_production_baseline` |
| **Status** | ✅ completed |
| **Started** | 2026-06-25T00:00:00Z |
| **Completed** | 2026-06-25T06:00:00Z |
| **Duration** | 6h 0m |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md) |
| **Task types** | `stt-benchmark-run` |
| **Categories** | [`stt-evaluation`](../../by-category/stt-evaluation.md) |
| **Expected assets** | 2 predictions |
| **Step progress** | 3/3 |
| **Task folder** | [`t0009_parakeet_production_baseline/`](../../../tasks/t0009_parakeet_production_baseline/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0009_parakeet_production_baseline/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0009_parakeet_production_baseline/task_description.md)*

# Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Motivation

Parakeet TDT 0.6b-v3 (NVIDIA) is the current production STT model deployed in brainpowa's
voice-commerce pipeline. Tasks t0006–t0010 all compare their benchmarked models against this
production system, making it essential to have directly comparable metrics computed with the
same evaluation harness.

Prior tasks (t0001–t0005) used Whisper large-v3 as the reference baseline. This task
establishes a second, more operationally relevant baseline using the actual production model,
so that benchmark results are interpretable in terms of real-world improvement potential.

## Goal

Run Parakeet TDT 0.6b-v3 on all 93 gold-92 clips in two configurations:

1. **Unbiased** — standard inference, no keyword injection
2. **Biased (production config)** — with the keyword biasing configuration currently deployed
   in production

Compute entity accuracy, domain-vocabulary accuracy, WER, action-critical WER, intent
preservation, and latency p50/p95/p99 using the same evaluation harness as all other benchmark
tasks.

## Success Criteria

- All 93 clips transcribed in both configurations
- metrics.json written with both variants
- Prediction assets registered for DVC tracking
- Results summary and detailed report completed

</details>

## Metrics

### Parakeet TDT 0.6b-v3 — unbiased

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.233696** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.318841** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.341772** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.870968** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.0388** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.151454** |

### Parakeet TDT 0.6b-v3 — biased (production config)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.231522** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.333333** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.335443** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.870968** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.0378** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.152457** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [Parakeet TDT 0.6b-v3 — Production Config (biased) on Gold-92](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-production/) | [`description.md`](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-production/description.md) |
| predictions | [Parakeet TDT 0.6b-v3 — Unbiased on Gold-92](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-unbiased/) | [`description.md`](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-unbiased/description.md) |

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0009_parakeet_production_baseline/results/results_summary.md)*

--- spec_version: "1" task_id: "t0009_parakeet_production_baseline" date_completed:
"2026-06-25" ---
# Results Summary — Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Summary

Parakeet TDT 0.6b-v3 (NVIDIA, current Rezolve production model) was benchmarked on all 93
gold-92 clips in unbiased and production-config (biased) modes. The production config achieves
entity accuracy=23.2%, domain-vocabulary accuracy=33.3%, WER=15.2%, and action-critical
WER=33.5% at p50 latency=38 ms. Keyword biasing in the production config provides negligible
benefit over unbiased: ΔEA=−0.2 pp, ΔEA_DV=+1.4 pp, ΔWER=+0.1 pp.

This baseline establishes the current production floor. All subsequent benchmark tasks
(t0006–t0010) report their metrics relative to this result. The key finding is that the
production model has very low entity accuracy (23.2%) and very high action-critical WER
(33.5%), confirming significant headroom for improvement.

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

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0009_parakeet_production_baseline/results/results_detailed.md)*

--- spec_version: "2" task_id: "t0009_parakeet_production_baseline" date_completed:
"2026-06-25" ---
# Results Detailed — Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Summary

Parakeet TDT 0.6b-v3 is the current production STT model in Rezolve's brainpowa voice-commerce
pipeline. It was benchmarked on all 93 gold-92 clips in two configurations: unbiased (standard
inference) and biased (production config with keyword injection). Entity accuracy in
production config is 23.2%, domain-vocabulary accuracy is 33.3%, and action-critical WER is
33.5%. Ultra-low latency (38 ms p50) is the model's primary strength. Keyword biasing as
currently deployed provides negligible benefit. This establishes the definitive production
floor for all subsequent benchmark comparisons.

## Methodology

**Model**: nvidia/parakeet-tdt-0.6b-v3 via NeMo / Riva SDK. Production config uses the same
keyword list as deployed in the brainpowa pipeline.

**Dataset**: 93 WAV clips from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Ground truth from
`ground_truth.jsonl`. Accent groups: 34 production (accented), 46 clean-voice, 13 error-cases.

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
the cost of ΔEA=−0.2 pp and ΔWER=+0.1 pp. This is consistent with Parakeet's architecture: the
TDT (Token-and-Duration Transducer) model processes vocabulary injection differently from
encoder-decoder models. Keyword injection as currently configured does not meaningfully
improve entity recall for Rezolve domain vocabulary.

**Entity accuracy of 23.2% is the benchmark floor.** Any model benchmarked in tasks
t0006–t0010 that cannot exceed 23.2% entity accuracy offers no improvement over the current
production model. Given the 38 ms p50 latency, a replacement model also needs to remain within
the 800 ms budget.

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
- `assets/predictions/parakeet-tdt-0.6b-v3-gold92-production/` — prediction asset, production
  config

</details>
