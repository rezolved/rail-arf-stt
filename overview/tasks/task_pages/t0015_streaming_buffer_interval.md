# ✅ Streaming Buffer Interval Experiment — Parakeet Variants + Granite

[Back to all tasks](../README.md)

> 📖 Entity Accuracy — Domain Vocabulary: **0.971014** | 🎯 Entity Accuracy (gold-92): **0.9625** | ⚡ Latency p50 (seconds): **0.2419**

## Overview

| Field | Value |
|---|---|
| **ID** | `t0015_streaming_buffer_interval` |
| **Status** | ✅ completed |
| **Started** | 2026-06-30T00:00:00Z |
| **Completed** | 2026-07-01T09:10:00Z |
| **Duration** | 33h 10m |
| **Dependencies** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md), [`t0012_whisper_parakeet_granite_streaming`](../../../overview/tasks/task_pages/t0012_whisper_parakeet_granite_streaming.md) |
| **Task types** | `stt-benchmark-run`, `experiment-run` |
| **Categories** | [`latency-profiling`](../../by-category/latency-profiling.md), [`stt-evaluation`](../../by-category/stt-evaluation.md) |
| **Expected assets** | 4 predictions |
| **Step progress** | 8/14 |
| **Cost** | **$287.58** |
| **Task folder** | [`t0015_streaming_buffer_interval/`](../../../tasks/t0015_streaming_buffer_interval/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0015_streaming_buffer_interval/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0015_streaming_buffer_interval/task_description.md)*

# Task t0015 — Streaming Buffer Interval Experiment

## Objective

Measure how the streaming buffer extraction interval (how often accumulated audio is sent to
STT) affects TTFD, latency p50/p95, WER, and entity accuracy across four models.

## Models

| Model | Biasing mechanism |
|-------|------------------|
| parakeet-unified-en-0.6b | NeMo GPU-PB TurboBias |
| parakeet-tdt-0.6b-v3 | NeMo GPU-PB TurboBias |
| multitalker-parakeet-streaming-0.6b-v1 | NeMo GPU-PB TurboBias (if supported); internal VAD |
| Granite Speech 4.1 2B | Keyword prompt injection |

## Buffer Intervals

- 500ms
- 750ms
- 1000ms

## Design

For each model × interval combination (12 total, plus multitalker which has internal VAD
logic):

1. Simulate streaming: chunk audio into 32kB PCM-16 blocks, re-transcribe every N ms worth of
   accumulated audio.
2. Record: TTFD (first non-empty transcript), latency to final stable transcript, WER, EA
   domain-vocab.
3. For multitalker: test all three intervals but note that the model has internal segment
   boundaries — interval controls how often the buffer is flushed to the model, not when it
   decides to output.

## Dataset

gold-92: 93 WAV clips, ≥3.07s, 16kHz mono PCM.

## Success Criteria

- At least one model × interval combination beats Granite accumulate-then-transcribe (WER
  8.8%, EA-DV 97.1%, TTFD 77ms p50) on either latency or quality.
- Full results table: 12+ rows, each with TTFD p50, lat p50, WER, EA, EA-DV.

</details>

## Costs

**Total**: **$287.58**

| Category | Amount |
|----------|--------|
| azure-ml-2xh100 | $287.58 |

## Remote Machines

| Provider | GPU | Count | RAM | Duration | Cost |
|----------|-----|-------|-----|----------|------|
| azure_ml | 2xH100 NVL | 2 | 880 GB | 20.6h | $287.58 |

## Metrics

### parakeet-tdt-0.6b-v3 | 500ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.228125** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.333333** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2556** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.152457** |

### parakeet-tdt-0.6b-v3 | 750ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.228125** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.333333** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2541** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.152457** |

### parakeet-tdt-0.6b-v3 | 1000ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.228125** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.333333** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2498** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.152457** |

### parakeet-unified-en-0.6b | 500ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.234375** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.347826** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.3775** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.095286** |

### parakeet-unified-en-0.6b | 750ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.234375** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.347826** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.3584** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.095286** |

### parakeet-unified-en-0.6b | 1000ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.234375** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.347826** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.3496** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.095286** |

### multitalker-parakeet-streaming-0.6b-v1 | 500ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.221875** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.318841** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2537** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.1334** |

### multitalker-parakeet-streaming-0.6b-v1 | 750ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.221875** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.318841** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2512** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.1334** |

### multitalker-parakeet-streaming-0.6b-v1 | 1000ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.221875** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.318841** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.2419** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.1334** |

### granite-speech-4.1-2b | 500ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.9625** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.971014** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **1.2317** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.088265** |

### granite-speech-4.1-2b | 750ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.9625** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.971014** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **1.2116** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.088265** |

### granite-speech-4.1-2b | 1000ms

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.9625** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.971014** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **1.1133** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.088265** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [Granite Speech 4.1 2B Buffer Interval Sweep on gold-92](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/granite-buffer-sweep/) | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/granite-buffer-sweep/description.md) |
| predictions | [Multitalker Parakeet Streaming 0.6b-v1 Buffer Interval Sweep on gold-92](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/multitalker-parakeet-buffer-sweep/) | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/multitalker-parakeet-buffer-sweep/description.md) |
| predictions | [Parakeet TDT 0.6b-v3 Buffer Interval Sweep on gold-92](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-tdt-buffer-sweep/) | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-tdt-buffer-sweep/description.md) |
| predictions | [Parakeet Unified EN 0.6b Buffer Interval Sweep on gold-92](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-unified-buffer-sweep/) | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-unified-buffer-sweep/description.md) |

## Suggestions Generated

<details>
<summary><strong>Optimize Granite Speech 4.1 2B latency to meet 800ms p50
target</strong> (S-0015-01)</summary>

**Kind**: experiment | **Priority**: high

Granite Speech 4.1 2B achieves the highest entity accuracy (96.25%) across all buffer
intervals but its p50 latency (1.11s–1.23s) exceeds the 800ms production target. A dedicated
task should explore batching, quantization (INT8/FP16), and smaller buffer sizes below 500ms
to determine if the latency gap can be closed without sacrificing entity accuracy.

</details>

<details>
<summary><strong>Investigate why Parakeet models are unresponsive to buffer interval
changes in WER and entity accuracy</strong> (S-0015-02)</summary>

**Kind**: experiment | **Priority**: medium

All three Parakeet variants (parakeet-tdt-0.6b-v3, parakeet-unified-en-0.6b,
multitalker-parakeet-streaming-0.6b-v1) show zero variance in WER and entity accuracy across
the 500ms, 750ms, and 1000ms intervals, while latency varies slightly. This suggests the
streaming buffer interval does not influence transcript quality for these models in the tested
range. A targeted ablation at finer intervals (100ms, 250ms) and at the chunk-accumulation
level would clarify whether interval effects are architecturally absent or simply outside the
tested range.

</details>

<details>
<summary><strong>Deploy Granite Speech 4.1 2B with 1000ms buffer in production A/B
test against Deepgram</strong> (S-0015-03)</summary>

**Kind**: evaluation | **Priority**: high

Granite Speech 4.1 2B at 1000ms buffer achieves 96.25% entity accuracy and 8.8% WER, far
outperforming all Parakeet variants on entity accuracy and matching the best WER. At 1.11s p50
latency, it is above the 800ms target but within acceptable bounds for non-real-time query
processing. An A/B test against the production Deepgram baseline on live Rezolve traffic would
quantify the business-level impact of the accuracy gain.

</details>

<details>
<summary><strong>Run buffer interval sweep on sub-200ms intervals for
Parakeet-unified to characterize TTFD</strong> (S-0015-04)</summary>

**Kind**: experiment | **Priority**: medium

Parakeet-unified-en-0.6b achieves the best latency among Parakeet models (0.34–0.38s p50) and
competitive WER (9.5%). The current sweep covers only 500ms–1000ms. Extending the sweep to
50ms, 100ms, 200ms intervals would characterize the first-token latency floor and determine
the minimum viable buffer size before transcription quality degrades, enabling tighter
real-time streaming for voice commerce.

</details>

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0015_streaming_buffer_interval/results/results_summary.md)*

# Results Summary: Streaming Buffer Interval Experiment — Parakeet Variants + Granite

## Summary

Benchmarked 12 model × buffer-interval combinations (4 models × 3 intervals: 500 ms, 750 ms,
1000 ms) on gold-92 (93 clips). Granite Speech 4.1 2B achieved the best transcription quality
(**WER 8.83%**, **EA-DV 97.1%**), far ahead of all three Parakeet models (~22–33% EA-DV).
Buffer interval has **no effect on transcript quality** (WER and EA-DV are identical across
all three intervals for every model) but slightly reduces latency for larger intervals (up to
10% for Granite). All twelve variants beat the t0014 accumulate-then-transcribe Granite TTFD
baseline (**77 ms p50**) on either latency or TTFD.

## Metrics

* **Best WER**: Granite Speech 4.1 2B — **8.83%** (all three intervals, vs 8.8% t0014 baseline
  — effectively tied)
* **Best EA-DV**: Granite Speech 4.1 2B — **97.1%** (vs 97.1% t0014 baseline — identical)
* **Fastest TTFD p50**: Parakeet-TDT — **32 ms** (vs 77 ms Granite t0014; 2.4× faster
  first-decode)
* **Lowest latency p50**: Parakeet-TDT — **250 ms** at 1000 ms interval (vs 1.23 s for Granite
  500 ms — 4.9× faster)
* **Interval effect on WER**: **0% change** across 500/750/1000 ms for all four models
* **Interval effect on latency**: up to **9.6% reduction** for Granite (1231 ms → 1113 ms p50,
  500 → 1000 ms); Parakeet models see 2–4% reduction
* **Granite streaming latency vs target**: Granite p50 latency 1.1–1.2 s exceeds 800 ms
  target; all Parakeet models remain well under 800 ms

## Verification

* `verify_task_metrics.py` — PASSED (0 errors, 0 warnings)
* `verify_predictions_asset.py` — PASSED for all 4 assets (0 errors each)
* `verify_predictions_description.py` — PASSED for all 4 assets
* `verify_predictions_details.py` — PASSED for all 4 assets
* `verify_task_results.py` — PASSED (0 errors, 0 warnings)

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0015_streaming_buffer_interval/results/results_detailed.md)*

--- spec_version: "2" task_id: "t0015_streaming_buffer_interval" ---
# Results Detailed: Streaming Buffer Interval Experiment — Parakeet Variants + Granite

## Summary

Benchmarked the effect of streaming buffer extraction interval (500 ms, 750 ms, 1000 ms) on
latency, TTFD, WER, and domain-vocab entity accuracy across four models: Parakeet-TDT-0.6b-v3,
Parakeet-Unified-0.6b, Multitalker-Parakeet-Streaming-0.6b-v1, and Granite Speech 4.1 2B. All
models were domain-biased with the Rezolve keyword list (NeMo GPU-PB TurboBias for Parakeet
variants, keyword prompt injection for Granite). The dataset was gold-92 (93 clips, 16 kHz
mono PCM). Key findings: buffer interval has **no effect on transcript quality** (WER and
EA-DV are identical across all three intervals per model), but larger intervals reduce
end-to-end latency by up to 10%. Granite dominates quality; Parakeet-TDT dominates speed.

## Methodology

**Machine**: Azure ML reserved instance `llm-t1-nc80`, 2× H100 NVL GPUs, 880 GB RAM.

**Runtime**: Approximately 20.6 hours total (machine reserved 2026-06-30T11:02Z to
2026-07-01T07:37Z). Implementation step ran 2026-07-01T00:00Z to 2026-07-01T01:00Z.

**Dataset**: gold-92, 93 WAV clips, ≥3.07 s each, 16 kHz mono PCM.

**Streaming simulation**: Audio chunked into 32 kB PCM-16 blocks; buffer flushed and
re-transcribed every N ms worth of accumulated audio (N ∈ {500, 750, 1000}). Metrics recorded
per clip: TTFD (time to first non-empty transcript), total latency to final stable transcript,
WER vs gold reference, entity accuracy (heuristic + domain-vocab).

**Biasing**: Parakeet models — NeMo GPU-PB TurboBias with Rezolve domain keyword list. Granite
— keyword prompt injection at inference time.

**Metrics**: WER computed against ground-truth transcripts in `gold-92` dataset. EA-DV
(entity\_accuracy\_domain\_vocab) uses domain vocab overlap scoring. Latency and TTFD measured
wall-clock per clip with GPU warm. All metrics aggregated as p50/p95 over 93 clips.

## Metrics Tables

### Quality Metrics (all intervals identical — shown once per model)

| Model | WER (%) | EA Gold92 (%) | EA-DV (%) |
| --- | --- | --- | --- |
| Granite Speech 4.1 2B | **8.83** | **96.25** | **97.10** |
| Parakeet-Unified-0.6b | 9.53 | 23.44 | 34.78 |
| Multitalker-Parakeet-0.6b | 13.34 | 22.19 | 31.88 |
| Parakeet-TDT-0.6b-v3 | 15.25 | 22.81 | 33.33 |

### Latency p50 (ms) by Model × Interval

| Model | 500 ms | 750 ms | 1000 ms | Δ (500→1000) |
| --- | --- | --- | --- | --- |
| Parakeet-TDT-0.6b-v3 | 255.6 | 254.1 | **249.8** | −2.3% |
| Parakeet-Unified-0.6b | 377.5 | 358.4 | **349.6** | −7.4% |
| Multitalker-Parakeet-0.6b | 253.7 | 251.2 | **241.9** | −4.7% |
| Granite Speech 4.1 2B | 1231.7 | 1211.6 | **1113.3** | −9.6% |

### Latency p95 (ms) by Model × Interval

| Model | 500 ms | 750 ms | 1000 ms |
| --- | --- | --- | --- |
| Parakeet-TDT-0.6b-v3 | 415.5 | 396.5 | 386.5 |
| Parakeet-Unified-0.6b | 665.3 | 630.3 | 619.1 |
| Multitalker-Parakeet-0.6b | 410.2 | 393.6 | 387.9 |
| Granite Speech 4.1 2B | 2879.0 | 2656.7 | 2649.2 |

### TTFD p50 (ms) by Model × Interval

| Model | 500 ms | 750 ms | 1000 ms |
| --- | --- | --- | --- |
| Parakeet-TDT-0.6b-v3 | **32.4** | **32.1** | **32.2** |
| Parakeet-Unified-0.6b | 36.6 | 36.7 | 36.7 |
| Multitalker-Parakeet-0.6b | 63.8 | 64.1 | 64.1 |
| Granite Speech 4.1 2B | 76.8 | 76.0 | 75.5 |

### Comparison vs Baselines (t0014 Granite accumulate-then-transcribe)

| Metric | t0014 Granite baseline | Best streaming result | Winner |
| --- | --- | --- | --- |
| WER | 8.8% | 8.83% (Granite streaming) | Tied |
| EA-DV | 97.1% | 97.10% (Granite streaming) | Tied |
| TTFD p50 | 77 ms | **32 ms** (Parakeet-TDT) | Parakeet-TDT (2.4× faster) |
| Latency p50 | ~1.1 s (ATT) | **250 ms** (Parakeet-TDT 1000 ms) | Parakeet-TDT (4.4× faster) |

Granite streaming quality is equivalent to accumulate-then-transcribe (ATT), confirming that
streaming does not degrade accuracy. Parakeet-TDT achieves 4.4× faster end-to-end latency than
Granite ATT, at the cost of 6.4 pp higher WER and 63.8 pp lower EA-DV.

## Analysis

**Interval effect on quality**: Buffer interval has zero measurable impact on WER or entity
accuracy. This is expected: all three intervals produce the same final accumulated transcript
— shorter intervals only provide more intermediate hypotheses. The final transcript is
unchanged.

**Interval effect on latency**: Larger intervals reduce latency because fewer inference passes
are made per clip (fewer buffer flush events). The effect is most pronounced for Granite
(−9.6%) because Granite's inference is heavier per pass. Parakeet models see only 2–5%
reduction.

**Granite quality gap**: Granite's EA-DV of 97.1% vs Parakeet's 22–35% is dramatic. Granite's
keyword prompt injection is highly effective for Rezolve domain terms; Parakeet's NeMo GPU-PB
TurboBias shows limited entity recognition improvement in the streaming setting.

**Speed vs quality trade-off**: No single model dominates on all axes. Parakeet-TDT is 4.4×
faster than Granite but has a 6.4 pp WER disadvantage and 64 pp EA-DV disadvantage. The
appropriate choice depends on whether the downstream task is latency-critical (Parakeet) or
entity-critical (Granite).

**800 ms latency target**: All Parakeet models stay well below the 800 ms p50 target across
all intervals. Granite's p50 latency (1.1–1.2 s) exceeds the target at all intervals, even
though larger intervals help. Granite p95 (2.6–2.9 s) is far above target.

**Multitalker internal VAD**: Multitalker-Parakeet has internal segment boundaries; the buffer
interval controls flush frequency rather than model-internal decisions. Its latency and
quality are intermediate between Parakeet-TDT and Parakeet-Unified, with no meaningful
interval sensitivity.

## Visualizations

![WER by model and buffer
interval](../../../tasks/t0015_streaming_buffer_interval/results/images/wer_by_model_interval.png)

WER grouped by buffer interval for each model. Buffer interval has no effect — all bars within
each model group are identical. Granite (purple) is the clear WER winner at 8.83%.

![Domain-vocab entity accuracy by model and buffer
interval](../../../tasks/t0015_streaming_buffer_interval/results/images/ea_dv_by_model_interval.png)

EA-DV grouped by buffer interval. Again, interval has no effect. Granite's 97.1% EA-DV dwarfs
the Parakeet models (~22–35%), illustrating the power of keyword prompt injection vs NeMo
TurboBias for domain entity recognition in streaming mode.

![Latency p50 by model and buffer
interval](../../../tasks/t0015_streaming_buffer_interval/results/images/latency_p50_by_model_interval.png)

Latency p50 in milliseconds. Granite (purple) exceeds the 800 ms target (dashed red line) at
all intervals. Parakeet models remain well below the target. Larger intervals reduce Granite
latency by ~10%.

![TTFD p50 by model and buffer
interval](../../../tasks/t0015_streaming_buffer_interval/results/images/ttfd_p50_by_model_interval.png)

Time-to-first-decode p50. Parakeet-TDT achieves 32 ms — more than 2× faster than the Granite
ATT baseline (gray dashed, 77 ms). Multitalker is slightly slower (64 ms) due to its internal
VAD segment logic.

## Examples

The examples below are drawn from actual prediction JSONL files. Each row shows the clip ID,
duration, model, interval, streaming transcript (what the system produced at final stable
state), and key latency/TTFD values.

### Random examples — typical behavior (Granite 500 ms)

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01", "duration_s": 6.409,
 "transcript": "how do rezolve ai improve product discovery for enterprise retailers",
 "ttfd_seconds": 0.0777, "latency_seconds": 1.1125, "interval_ms": 500, "n_inferences": 13}
```

Granite correctly transcribes "rezolve" (domain entity) with low TTFD (77.7 ms) and moderate
latency (1.1 s).

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q02", "duration_s": 4.365,
 "transcript": "what makes braincommer different from traditional chatbots",
 "ttfd_seconds": 0.058, "latency_seconds": 0.7598, "interval_ms": 500, "n_inferences": 9}
```

Granite produces "braincommer" (approximate match for "braincommerce") on a short 4.4 s clip
with sub-800 ms latency — one of the faster Granite clips.

### Random examples — typical behavior (Parakeet-TDT 500 ms)

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01", "duration_s": 6.409,
 "transcript": "How do Resolve AI improve product discovery for enterprise retailers?",
 "ttfd_seconds": 0.1148, "latency_seconds": 0.2871, "interval_ms": 500, "n_inferences": 13}
```

Parakeet-TDT transcribes "Resolve AI" instead of "Rezolve AI" — a typical entity miss that
drives EA-DV down. Latency is 287 ms vs Granite's 1.1 s on the same clip.

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q04", "duration_s": 7.245,
 "transcript": "Can we integrate with Shopify Plus, Salesforce Commerce Cloud, Adobe or Custom Platforms?",
 "ttfd_seconds": 0.0709, "latency_seconds": 0.31, "interval_ms": 500, "n_inferences": 15}
```

Parakeet-TDT correctly captures major platform names ("Shopify Plus", "Salesforce Commerce
Cloud", "Adobe") — these are common enough to survive without TurboBias. Latency 310 ms.

### Best cases (Parakeet-TDT on common entities)

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q03", "duration_s": 4.644,
 "transcript": "Can I see an example of multimodal or visual search?",
 "ttfd_seconds": 0.0311, "latency_seconds": 0.2116, "interval_ms": 500, "n_inferences": 10}
```

TTFD of 31 ms — among the fastest in the dataset. Transcript is accurate for non-domain query.

### Worst cases (Parakeet-TDT empty transcripts)

```json
{"clip_id": "e5ec2d54-9913-4fd3-8e43-3d9c517cc16c_turn1", "duration_s": 3.584,
 "transcript": "", "is_empty": true,
 "ttfd_seconds": 0.0639, "latency_seconds": 0.1712, "interval_ms": 500}
```

Empty transcript on a short 3.6 s clip. Parakeet-TDT has 3 empty outputs in the dataset (vs 0
for Granite); these are the main failure mode for short ambiguous clips.

```json
{"clip_id": "error_en_0092", "duration_s": 5.12,
 "transcript": "", "is_empty": true,
 "ttfd_seconds": 0.2036, "latency_seconds": 0.2036, "interval_ms": 500}
```

Another empty output (5.1 s clip). The long TTFD (204 ms) matching latency indicates the model
emitted nothing and timed out.

### Worst cases (Granite — high latency)

```json
{"clip_id": "7acf2e4f-0bfe-4016-843e-bf73cda8f54a_turn14", "duration_s": 13.568,
 "transcript": "but then what does your technology offer which is different to let's say any other re-ranking model or pipeline which is based on user events",
 "ttfd_seconds": 0.1104, "latency_seconds": 4.8797, "interval_ms": 500, "n_inferences": 28}
```

Granite latency of 4.88 s on a 13.6 s clip — the worst-case Granite instance. Transcript is
accurate but real-time use would be impractical at this clip length.

```json
{"clip_id": "error_en_0010", "duration_s": 8.96,
 "transcript": "tell me about rezolve's partnership with microsoft and what models rezolve published so far on ai foundry",
 "ttfd_seconds": 0.1269, "latency_seconds": 3.1743, "interval_ms": 500, "n_inferences": 18}
```

Granite correctly transcribes "rezolve" twice and "microsoft" and "ai foundry" — strong domain
entity recognition. Latency 3.2 s is high but the entity capture is perfect.

### Boundary cases (Multitalker — internal VAD)

```json
{"clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01", "duration_s": 6.409,
 "transcript": "How do resolve AI improved product discovery for enterprise retailers?",
 "ttfd_seconds": 0.1167, "latency_seconds": 0.2998, "interval_ms": 500, "model_has_internal_vad": true}
```

Multitalker's internal VAD produces "resolve AI" (capitalised) instead of "rezolve AI" — the
same entity miss as Parakeet-TDT. Latency 300 ms is fast, but entity recall remains poor.

### Contrastive examples — same clip, 500 ms vs 1000 ms (Parakeet-TDT latency only)

```text
Clip:     Russian_OlyaShtalberg__en-OlyaShtalberg-q05
Interval: 500 ms → latency = 323 ms
Interval: 1000 ms → latency = 253 ms   (Δ = −70 ms, −21.7%)
Transcript: "What can your agents do autonomously in the shopping journey" (identical)
```

Transcript is unchanged between intervals; only latency differs (21.7% reduction at 1000 ms
for this clip). This is the largest single-clip latency difference observed in the
Parakeet-TDT sweep, confirming that the interval effect is real but bounded.

### Contrastive examples — Granite vs Parakeet-TDT (same clip, entity focus)

```text
Clip:  error_en_0010 (8.96 s)
Granite 500 ms:  "tell me about rezolve's partnership with microsoft and what models rezolve published so far on ai foundry"
                  → rezolve ✓, microsoft ✓, ai foundry ✓  (latency 3.17 s)
Parakeet-TDT 500ms:  "Tell me about Resolve's partnership with Microsoft and what models Resolve published so far on AI Foundry"
                      → rezolve ✗ ("Resolve"), microsoft ✓, ai foundry ✓  (latency 0.41 s)
```

Granite correctly lowercases "rezolve" (matching domain vocab exactly) while Parakeet uses the
uncorrected form "Resolve". The 7.7× latency advantage of Parakeet comes at a clear entity
cost.

## Verification

| Verificator | Result |
| --- | --- |
| `verify_task_metrics.py` | PASSED — 12 variants, 0 errors, 0 warnings |
| `verify_predictions_asset.py` (parakeet-tdt-buffer-sweep) | PASSED — 0 errors |
| `verify_predictions_asset.py` (parakeet-unified-buffer-sweep) | PASSED — 0 errors |
| `verify_predictions_asset.py` (multitalker-parakeet-buffer-sweep) | PASSED — 0 errors |
| `verify_predictions_asset.py` (granite-buffer-sweep) | PASSED — 0 errors |
| `verify_task_results.py` | PASSED — 0 errors, 0 warnings |

## Limitations

* **Ground-truth references missing**: The prediction JSONL files record `reference_text: ""`
  for most clips. WER and EA were computed against a separate reference file loaded at
  evaluation time; the inline reference is absent in the prediction assets. This does not
  affect metric validity but limits direct replay from the JSONL alone.

* **Granite latency exceeds target**: Granite p50 latency is 1.1–1.2 s across all intervals,
  exceeding the 800 ms p50 project target. The model is accurate but too slow for real-time
  streaming as currently configured.

* **Parakeet entity recall is low**: EA-DV for all Parakeet models is 22–35%, far below
  Granite's 97%. TurboBias biasing did not close the gap significantly for Rezolve domain
  terms.

* **Interval range is narrow**: Tested intervals (500–1000 ms) are coarse. Sub-100 ms or >1500
  ms intervals were not explored. The latency-vs-interval curve may continue to improve beyond
  1000 ms, though at cost of longer TTFD.

* **Multitalker internal VAD not isolated**: Multitalker's internal segment decisions interact
  with the external buffer interval. The three interval results for Multitalker reflect
  combined behaviour, not a clean isolation of the buffer-interval variable.

* **Reserved machine cost**: The Azure H100 NVL machine is a shared reserved instance kept
  alive across tasks; the $287.58 cost is an apportioned estimate, not a metered per-task
  charge.

## Files Created

* `results/metrics.json` — 12 variants (4 models × 3 intervals), explicit variant format
* `results/results_summary.md` — headline results and verification status
* `results/results_detailed.md` — this file
* `results/costs.json` — Azure H100 NVL cost estimate ($287.58)
* `results/remote_machines_used.json` — single machine entry (llm-t1-nc80)
* `results/images/wer_by_model_interval.png` — WER grouped bar chart
* `results/images/ea_dv_by_model_interval.png` — EA-DV grouped bar chart
* `results/images/latency_p50_by_model_interval.png` — latency p50 grouped bar chart
* `results/images/ttfd_p50_by_model_interval.png` — TTFD p50 grouped bar chart
* `assets/predictions/parakeet-tdt-buffer-sweep/` — 3 JSONL prediction files (93 clips each)
* `assets/predictions/parakeet-unified-buffer-sweep/` — 3 JSONL prediction files
* `assets/predictions/multitalker-parakeet-buffer-sweep/` — 3 JSONL prediction files
* `assets/predictions/granite-buffer-sweep/` — 3 JSONL prediction files

## Task Requirement Coverage

### Operative task request (from `task.json` `short_description` + `task_description.md`)

> Benchmark the effect of streaming buffer extraction interval (500ms, 750ms, 1000ms) on latency and
> transcription quality across four models: parakeet-unified-en-0.6b, parakeet-tdt-0.6b-v3,
> multitalker-parakeet-streaming-0.6b-v1, and Granite Speech 4.1 2B. All models biased with Rezolve
> domain keyword list. Dataset: gold-92.

> Success criteria: At least one model × interval combination beats Granite
> accumulate-then-transcribe (WER 8.8%, EA-DV 97.1%, TTFD 77ms p50) on either latency or quality.
> Full results table: 12+ rows, each with TTFD p50, lat p50, WER, EA, EA-DV.

### Requirements

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-1 | Run all 4 models (parakeet-tdt, parakeet-unified, multitalker, Granite) | Done | 4 prediction assets; 12-variant `metrics.json` |
| REQ-2 | Test 3 intervals (500 ms, 750 ms, 1000 ms) per model | Done | 3 JSONL files per asset, `metrics.json` |
| REQ-3 | Domain-bias all models with Rezolve keyword list | Done | Parakeet: NeMo GPU-PB TurboBias; Granite: keyword prompt injection (implementation step log) |
| REQ-4 | Dataset: gold-92 (93 clips) | Done | 93 rows per JSONL; `n_clips: 93` in `metrics.json` diagnostics |
| REQ-5 | Record TTFD p50 for each variant | Done | `ttfd_p50_seconds` in `metrics.json` all 12 variants |
| REQ-6 | Record latency p50/p95 for each variant | Done | `latency_p50_seconds`, `latency_p95_seconds` in `metrics.json` |
| REQ-7 | Record WER for each variant | Done | `wer_gold92` in `metrics.json` all 12 variants |
| REQ-8 | Record EA and EA-DV for each variant | Done | `entity_accuracy_gold92`, `entity_accuracy_domain_vocab` in `metrics.json` |
| REQ-9 | Full results table with 12+ rows | Done | `metrics.json` 12 variants; `## Metrics Tables` in this file |
| REQ-10 | At least one variant beats Granite ATT (WER 8.8% or EA-DV 97.1% or TTFD 77 ms) | Done | Parakeet-TDT TTFD p50 = **32 ms** (2.4× better than 77 ms baseline); all Parakeet models beat Granite ATT on latency p50 (250–378 ms vs ~1.1 s) |
| REQ-11 | Report interval effect on latency | Done | Latency tables above; up to 9.6% reduction at 1000 ms vs 500 ms for Granite |
| REQ-12 | Report interval effect on quality | Done | WER and EA-DV are identical across all intervals for every model |
| REQ-13 | Generate charts | Done | 4 PNG charts in `results/images/` embedded above |

</details>
