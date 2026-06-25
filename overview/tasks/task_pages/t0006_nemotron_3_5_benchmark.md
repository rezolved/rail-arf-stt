# ⏹ Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0006_nemotron_3_5_benchmark` |
| **Status** | ⏹ not_started |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Task types** | `stt-benchmark-run` |
| **Expected assets** | 2 predictions |
| **Task folder** | [`t0006_nemotron_3_5_benchmark/`](../../../tasks/t0006_nemotron_3_5_benchmark/) |

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

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [nemotron-3.5-asr-gold92-batch](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-batch/) | — |
| predictions | [nemotron-3.5-asr-gold92-word-boosted](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-word-boosted/) | — |
