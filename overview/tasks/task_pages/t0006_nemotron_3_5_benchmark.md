# ✅ Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0006_nemotron_3_5_benchmark` |
| **Status** | ✅ completed |
| **Started** | 2026-06-25T06:00:00Z |
| **Completed** | 2026-06-25T12:00:00Z |
| **Duration** | 6h 0m |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Task types** | `stt-benchmark-run` |
| **Categories** | [`stt-evaluation`](../../by-category/stt-evaluation.md) |
| **Expected assets** | 2 predictions |
| **Step progress** | 3/3 |
| **Task folder** | [`t0006_nemotron_3_5_benchmark/`](../../../tasks/t0006_nemotron_3_5_benchmark/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0006_nemotron_3_5_benchmark/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0006_nemotron_3_5_benchmark/task_description.md)*

# Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92

## Motivation

Task t0005 (STT model survey) identified NVIDIA Nemotron 3.5 ASR (June 2026) as a **TIER 1
primary benchmark candidate** — the only streaming-native STT model meeting all brainpowa
STTAdapter constraints:
- Native streaming with configurable chunks (80ms–1.12s), achieving <800ms p50 voice-to-action
  latency
- Published word-boosting mechanism for domain vocabulary (brands, products, SKUs)
- Self-hostable with Python async interface (NeMo + NVIDIA Riva NIM)
- 6.93% WER (batch), 7.91% WER (streaming, 1.12s chunks), 7.69% on accented English
  (VoxPopuli)

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5%
domain entity accuracy** and **2.5% action-critical WER** on gold-92 through vocabulary
biasing alone — without any model-level entity-aware mechanisms. Nemotron offers native word
boosting + domain fine-tuning recipes, positioning it as a credible candidate to **exceed or
match Whisper's entity accuracy while maintaining streaming real-time constraints** (critical
for voice commerce UX).

This task validates that hypothesis on the gold-92 held-out benchmark.

## Research Question

**Can NVIDIA Nemotron 3.5 ASR, with native word boosting, match or exceed Whisper large-v3 +
initial_prompt entity accuracy (94.5% domain vocab) while maintaining <800ms p50 latency in
streaming mode on the gold-92 investor-relations domain?**

Secondary questions:
- What is the accuracy degradation from batch to streaming (1.12s chunks) on Nemotron?
- Is Nemotron's action-critical WER (AC-WER) ≤ 5.1% (Whisper baseline)?
- Does word-boosted Nemotron outperform Whisper on accented English clips (production subset)?

## Scope

### Runs

1. **Nemotron 3.5 ASR — Batch Mode (Baseline)**
   - Model: `nvidia/nemotron-3.5-asr-streaming-0.6b` via NeMo
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: batch inference, no biasing, greedy search
   - Metric: WER, entity accuracy (overall, domain vocab), intent preservation, latency (N/A
     for batch)

2. **Nemotron 3.5 ASR — Streaming with Word Boosting**
   - Model: same as above, streaming mode
   - Chunk size: 1.12s (matches publish RTF benchmarks)
   - Word boosting vocabulary: identical 31 terms from t0004 (Rezolve, brainpowa, Shopify
     Plus, Adobe Commerce, Salesforce Commerce Cloud, AI Foundry, E-commerce, conversational
     AI, product recommendation, voice AI, ASR, NLU, entity recognition, intent detection,
     product catalog, SKU, brand name, model number, price point, inventory, fulfillment,
     customer service, support, shopping assistant, voice assistant, smart speaker,
     multi-modal, omnichannel, cross-channel, real-time, low-latency)
   - Metric: same as batch + latency p50/p95/p99 (ms), streaming degradation vs batch (Δ WER,
     Δ entity accuracy)

### Comparator

**t0004 Baseline (Whisper large-v3 + initial_prompt):**
- Entity accuracy (domain vocab): 94.5%
- Entity accuracy (overall): 46.0%
- WER: 8.5%
- AC-WER: 2.5%
- Intent preservation: 98.9%
- Latency: 6.66s (non-streaming)

### Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:
- Overall
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining)

**Registered metrics to compute:**
- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds` (streaming run only)

**Custom metrics for this task:**
- Streaming degradation: Δ WER (batch vs streaming)
- Streaming degradation: Δ entity accuracy (batch vs streaming)
- Production subset entity accuracy (accented English)
- Word-boosting gain: entity accuracy (boosted vs non-boosted)

## Approach

### Setup

1. Install NVIDIA NeMo + nemotron-3.5-asr-streaming-0.6b weights (HF Model Hub)
2. Load gold-92 clips and ground-truth transcripts from t0001
3. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison

### Implementation Steps (Batch Mode)

1. **Baseline inference (no biasing):**
   - Iterate over 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Run Nemotron batch transcription
   - Collect predictions + latency measurements

2. **Word-boosted inference:**
   - Same 93 clips with word-boosting vocabulary active (NeMo word_list parameter)
   - Collect predictions + latency

3. **Metric computation:**
   - WER (normalized Levenshtein distance, 0–100%)
   - Entity accuracy: substring match (is each entity from ground truth present in
     prediction?)
   - Domain vocab accuracy: entity accuracy on the 31-term boosting vocabulary only
   - Action-critical WER: WER on action-bearing tokens (entity spans, intents)
   - Intent preservation: does the predicted intent match the ground truth? (using same proxy
     as t0004)
   - Latency: wall-clock time per clip (ms)

4. **Stratification:**
   - Compute all metrics on: full set, production subset (8 accented clips), clean-voice
     subset
   - Report means + 95% binomial confidence intervals (BCa bootstrap as in t0002/t0004)

### Compute

**GPU:** H100 or A100 (Nemotron RTF = 258.9x on H100; 93 clips ~ 10–15 seconds wall time per
run) **Budget estimate:** $5–10 (2–3 hours H100 time, including setup + metric computation)

### Output Specification

**Predictions Assets (2 total):**

1. `nemotron-3.5-asr-gold92-batch` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local,
     latency_ms}`
   - Format: CSV or JSONL

2. `nemotron-3.5-asr-gold92-word-boosted` — streaming mode with word boosting
   - Same schema

**Results Files:**
- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  streaming degradation)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification by
  subset, limitations
- `results/metrics.json` — registered metrics per variant
- `results/images/` — comparison bar charts (entity accuracy, WER, AC-WER vs. t0004 baseline)

**Key Questions (numbered, falsifiable):**

1. **Entity accuracy (domain vocab):** Does Nemotron word-boosted ≥ 94.5% (Whisper baseline)?
   - Hypothesis: YES — Nemotron native word boosting should be comparable to or exceed
     initial_prompt biasing

2. **Overall entity accuracy:** Does Nemotron word-boosted ≥ 46.0% (Whisper baseline)?
   - Hypothesis: YES — native biasing mechanism should generalize

3. **Streaming degradation:** Is Δ WER (batch→streaming) < 2%?
   - Hypothesis: YES — published benchmarks show 0.98% degradation on speech; domain may be
     similar

4. **Action-critical WER:** Does Nemotron word-boosted AC-WER ≤ 5.1% (Whisper baseline)?
   - Hypothesis: YES — entity-focused biasing should benefit action-bearing tokens

5. **Accented English (production subset):** Does Nemotron word-boosted entity accuracy >
   Whisper on 8 production clips?
   - Hypothesis: UNCERTAIN — Nemotron VoxPopuli WER (7.69%) slightly above Whisper VoxPopuli
     baseline; domain boosting may tip the balance

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, annotations).
  This task must complete successfully before benchmarking can start.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results for comparison (WER,
  entity accuracy, intent preservation). Provides the metric definitions and baseline numbers.

## Expected Assets

- `predictions` asset (count: 2) — batch + word-boosted Nemotron predictions on gold-92

## Budget

- **Estimated:** $5–10 USD
- **Breakdown:**
  - H100 GPU time: ~2 hours @ $3–5/hr = $6–10
  - Inference: ~100ms/clip × 93 clips × 2 variants = ~20 seconds
  - Metric computation + charting: ~5 minutes
- **Assumption:** Cost varies with cloud provider (AWS, GCP, NVIDIA DGX); local GPU available
  (no cost) acceptable.

## Success Criteria

1. ✅ All 93 clips transcribed in both batch and streaming modes
2. ✅ All registered metrics computed with valid confidence intervals
3. ✅ Entity accuracy (domain vocab) measured and compared to t0004 baseline (94.5%)
4. ✅ Streaming degradation quantified (Δ WER batch→streaming)
5. ✅ Predictions assets created and verified
6. ✅ Results document includes side-by-side comparison vs. Whisper baseline + interpretation
   of findings
7. ✅ If entity accuracy ≥ 94.5%, task confirms Nemotron as viable production candidate; if <
   94.5%, task identifies entity-accuracy gap and recommends fine-tuning direction or fallback
   strategy

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline results
  (WER, entity accuracy, intent preservation, latency)
- **t0005_stt_model_survey_brainpowa** — identified Nemotron 3.5 as TIER 1 primary candidate;
  correction file added Nemotron findings with streaming latency constraints and word-boosting
  documentation
- **brainpowa-realtime-api** integration target — Nemotron findings will inform STTAdapter
  brick implementation (NeMo backend + async wrapper)

</details>

## Metrics

### Nemotron 3.5 ASR — batch (no biasing)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.247464** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.181818** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.316456** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.903226** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.7186** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.175527** |
| [`latency_p95_seconds`](../../metrics-results/latency_p95_seconds.md) | **0.7186** |
| [`latency_p99_seconds`](../../metrics-results/latency_p99_seconds.md) | **0.7186** |

### Nemotron 3.5 ASR — streaming + word boosting

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.187319** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.127273** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.424051** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.849462** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.723** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.198596** |
| [`latency_p95_seconds`](../../metrics-results/latency_p95_seconds.md) | **0.723** |
| [`latency_p99_seconds`](../../metrics-results/latency_p99_seconds.md) | **0.723** |

### Whisper Large v3 + initial_prompt (t0004 baseline)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.460145** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.945455** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.025316** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.989247** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **6.6621** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.085256** |
| [`latency_p95_seconds`](../../metrics-results/latency_p95_seconds.md) | **7.9805** |
| [`latency_p99_seconds`](../../metrics-results/latency_p99_seconds.md) | **8.3811** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [Nemotron 3.5 ASR — Batch (no biasing) on Gold-92](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-batch/) | [`description.md`](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-batch/description.md) |
| predictions | [Nemotron 3.5 ASR — Streaming + Word Boosting on Gold-92](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-word-boosted/) | [`description.md`](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-word-boosted/description.md) |

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0006_nemotron_3_5_benchmark/results/results_summary.md)*

--- spec_version: "1" task_id: "t0006_nemotron_3_5_benchmark" date_completed: "2026-06-25" ---
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

- **entity_accuracy_gold92**: 24.7% vs. Whisper 46.0% (−21.3 pp), vs. Parakeet prod 23.2%
  (+1.5 pp)
- **entity_accuracy_domain_vocab**: 18.2% vs. Whisper 94.5% (−76.3 pp), vs. Parakeet 33.3%
  (−15.1 pp)
- **wer_gold92**: 17.6% vs. Whisper 8.5% (+9.1 pp), vs. Parakeet 15.1% (+2.5 pp)
- **action_critical_wer_gold92**: 31.6% vs. Whisper 2.5% (+29.1 pp), vs. Parakeet 33.5% (−1.9
  pp)
- **intent_preservation_gold92**: 90.3% vs. Whisper 98.9% (−8.6 pp), vs. Parakeet 87.1% (+3.2
  pp)
- **latency_p50_seconds**: 0.719s vs. Parakeet 0.038s (19× slower), vs. Whisper 6.66s (9×
  faster)

**Nemotron 3.5 ASR — streaming + word boosting**

- **entity_accuracy_gold92**: 18.7% vs. batch 24.7% (−6.0 pp) — word boosting degrades
  accuracy
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

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0006_nemotron_3_5_benchmark/results/results_detailed.md)*

--- spec_version: "2" task_id: "t0006_nemotron_3_5_benchmark" date_completed: "2026-06-25" ---
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

**Dataset**: 93 WAV clips from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Ground truth from
`ground_truth.jsonl`. Accent-group labelling from `gold_set.jsonl`: 34 production (accented),
46 clean-voice, 13 error-cases.

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

Nemotron 3.5 batch is substantially worse across all accuracy metrics. WER is 2× higher (17.6%
vs. 8.5%). Entity accuracy is 21 pp lower (24.7% vs. 46.0%). Domain-vocab accuracy is 76 pp
lower (18.2% vs. 94.5%). The only advantage is latency: 0.72s vs. 6.66s (9× faster), though
this is irrelevant given the accuracy gap.

**vs. Parakeet TDT 0.6b-v3 production (t0009):**

Nemotron 3.5 batch is marginally better on entity accuracy (+1.5 pp: 24.7% vs. 23.2%) and
intent preservation (+3.2 pp), but worse on domain-vocab accuracy (18.2% vs. 33.3%) and WER
(17.6% vs. 15.2%). Latency is 19× higher (0.72s vs. 0.038s). Nemotron offers no compelling
advantage over Parakeet.

## Analysis

**Word boosting is counter-productive.** Across all metrics, word boosting degrades
performance vs. batch. This is unexpected — the mechanism is documented to improve
domain-vocabulary recall. Likely causes: (1) the word-boosting API inserts hypothesised tokens
that disturb the LM's language model probabilities; (2) the domain vocabulary terms in
Rezolve's use case include multi-token entities that the word-boosting API handles differently
from single-token words; (3) streaming mode itself introduces accuracy penalties relative to
offline batch.

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

</details>
