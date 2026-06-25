# Benchmark IBM Granite Speech 4.1 2B on Gold-92

## Motivation

Task t0005 (STT model survey) ranked **IBM Granite Speech 4.1 2B** as the **#1 primary benchmark
candidate** from a field of 20+ open-source STT models:

- Ranks **#1 on the Hugging Face Open ASR Leaderboard** (5.33% mean WER, April 2026)
- Native **keyword biasing** with published F1 metrics — shallow-fusion mechanism for domain
  vocabulary injection (brands, product names, SKUs)
- Estimated **100–200 ms TTFT** in batch mode — within the 800 ms voice-to-action budget for
  short-segment inference
- **Apache 2.0** license; self-hostable via HuggingFace Transformers; ~6–8 GB VRAM

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5% domain
entity accuracy** and **2.5% action-critical WER** on gold-92 using prompt-injection biasing alone.
Granite's native keyword biasing and best-in-class WER position it as a credible candidate to exceed
that entity accuracy with lower overall WER.

**Key caveat:** Granite 4.1 is batch-only by default (non-autoregressive decoder, no native
streaming path). A non-autoregressive (NAR) variant exists and may achieve sub-100 ms latency on
short segments. Streaming capability must be assessed during implementation; if Granite requires
full-segment buffering before decoding, it cannot satisfy the brainpowa `transcribe_stream`
interface without a buffering shim and will be disqualified for the primary streaming path (though
still valuable as a batch/fallback transcriber).

This task validates Granite's entity accuracy and latency on gold-92 and determines whether it is
viable as a production STTAdapter brick replacement or a high-accuracy batch-mode fallback.

## Research Question

**Can IBM Granite Speech 4.1 2B, with native keyword biasing, match or exceed Whisper large-v3 +
initial_prompt entity accuracy (94.5% domain vocab) while achieving ≤ 200 ms p50 per-segment latency
in batch mode on the gold-92 investor-relations domain?**

Secondary questions:

- What is Granite's action-critical WER (AC-WER) vs. the Whisper baseline (2.5%)?
- Does Granite's keyword biasing outperform Whisper's initial_prompt biasing on accented English
  clips (production subset, 8 clips)?
- Is Granite viable for `transcribe_stream` — does a streaming or low-latency incremental path
  exist?

## Scope

### Runs

1. **Granite 4.1 2B — Batch Mode, No Biasing**
   - Model: `ibm-granite/granite-speech-4.1-2b` via HuggingFace Transformers
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: default batch inference, no keyword list
   - Metrics: WER, entity accuracy (overall + domain vocab), intent preservation, action-critical
     WER, latency p50

2. **Granite 4.1 2B — Batch Mode with Keyword Biasing**
   - Model: same as above
   - Keyword vocabulary: identical 31 terms from t0004 (Rezolve, brainpowa, Shopify Plus, Adobe
     Commerce, Salesforce Commerce Cloud, AI Foundry, E-commerce, conversational AI, product
     recommendation, voice AI, ASR, NLU, entity recognition, intent detection, product catalog, SKU,
     brand name, model number, price point, inventory, fulfillment, customer service, support,
     shopping assistant, voice assistant, smart speaker, multi-modal, omnichannel, cross-channel,
     real-time, low-latency)
   - Biasing mechanism: native Granite keyword biasing API (shallow fusion at beam-search time)
   - Metrics: same as batch + keyword-biasing gain (Δ entity accuracy, Δ WER vs. no-biasing run)

### Comparator

**t0004 Baseline (Whisper large-v3 + initial_prompt):**

| Metric | Value |
| --- | --- |
| Entity accuracy (domain vocab) | 94.5% |
| Entity accuracy (overall) | 46.0% |
| WER | 8.5% |
| AC-WER | 2.5% |
| Intent preservation | 98.9% |
| Latency p50 | 6.66 s |

### Registered Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:

- Overall (93 clips)
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining 85 clips)

**Per run:**

- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds`
- `wrong_action_rate_gold92`

**Custom metrics:**

- Keyword-biasing gain: Δ entity accuracy (biased vs. unbiased)
- Keyword-biasing gain: Δ WER (biased vs. unbiased)
- Production subset entity accuracy (accented English, 8 clips)
- Latency feasibility: is p50 < 200 ms per segment achievable?

### Streaming Assessment

As part of run 1 setup, document:

- Whether the HuggingFace Granite API exposes a streaming decode path
- Whether a NAR (non-autoregressive) model variant is available and what its latency profile is
- Whether a buffering shim could wrap Granite for `transcribe_stream` compatibility at acceptable
  latency overhead

This assessment is qualitative; it does not require a separate benchmark run.

## Approach

### Setup

1. Install `transformers` + `torch` (HuggingFace Transformers inference path)
2. Load `ibm-granite/granite-speech-4.1-2b` weights (~6–8 GB VRAM; A100 or H100 recommended)
3. Load gold-92 clips and ground-truth transcripts from t0001
4. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison

### Implementation Steps

1. **Baseline inference (no biasing):** iterate over 93 gold-92 clips, run Granite batch
   transcription, collect predictions + per-clip wall-clock latency
2. **Keyword-biased inference:** same 93 clips with 31-term domain vocabulary active via Granite
   keyword biasing API; collect predictions + latency
3. **Metric computation:** WER (normalized Levenshtein), entity accuracy (substring match on
   annotated entity spans), domain vocab accuracy, AC-WER, intent preservation, latency p50/p95/p99;
   BCa bootstrap 95% confidence intervals on all accuracy metrics
4. **Stratification:** report all metrics on full set, production subset (8 accented clips),
   clean-voice subset
5. **Streaming assessment:** document streaming / NAR path availability (see Scope above)

### Compute

**GPU:** A100 or H100 (6–8 GB VRAM; 93 clips ≈ seconds of inference)\
**Budget estimate:** $3–8 USD

| Component | Cost |
| --- | --- |
| A100 GPU time, ~1 hour setup | $1–2 |
| 2 inference runs × ~30 s each | negligible |
| Metric computation + charting | ~5 min |
| **Total** | **$3–8** |

## Output Specification

### Prediction Assets (2 total)

1. `granite-4.1-2b-gold92-batch` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local, latency_ms}`
   - Format: CSV or JSONL

2. `granite-4.1-2b-gold92-keyword-biased` — batch mode with keyword biasing
   - Same schema

### Results Files

- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  keyword-biasing gain, latency feasibility verdict)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification by subset,
  streaming assessment, limitations
- `results/metrics.json` — registered metrics per variant
- `results/images/` — comparison bar charts:
  - Entity accuracy (domain vocab): Granite no-bias vs. Granite biased vs. Whisper baseline
  - WER: same three configurations
  - AC-WER: same three configurations
  - Latency p50: Granite batch vs. Whisper batch (and Nemotron streaming when t0006 completes)

### Key Questions (numbered, falsifiable)

1. **Entity accuracy (domain vocab):** Does Granite keyword-biased ≥ 94.5% (Whisper baseline)?
   - Hypothesis: YES — #1 WER + native keyword biasing should match or exceed initial_prompt biasing

2. **Overall entity accuracy:** Does Granite keyword-biased ≥ 46.0% (Whisper baseline)?
   - Hypothesis: YES — lower WER should generalize to higher overall entity recall

3. **Keyword-biasing gain:** Does keyword biasing improve entity accuracy over no-biasing run?
   - Hypothesis: YES — native shallow fusion mechanism should lift domain vocab precision

4. **Action-critical WER:** Does Granite keyword-biased AC-WER ≤ 2.5% (Whisper baseline)?
   - Hypothesis: YES — best-in-class WER + entity-focused biasing should reduce action errors

5. **Latency feasibility:** Is Granite p50 ≤ 200 ms per segment?
   - Hypothesis: UNCERTAIN — 100–200 ms TTFT reported in t0005 survey; actual wall-clock on gold-92
     segment lengths must be measured; NAR variant may be needed to hit target

6. **Accented English (production subset):** Does Granite keyword-biased entity accuracy > Whisper
   on 8 production clips?
   - Hypothesis: UNCERTAIN — Granite WER advantage may not hold for accented speech without
     accented-English fine-tuning data

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, entity annotations).
  Required before any inference can run.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results (WER, entity accuracy, intent
  preservation, 31-term biasing vocabulary). Provides the comparison baseline and the exact keyword
  list to use for run 2.

## Expected Assets

- `predictions` asset (count: 2) — batch and keyword-biased Granite 4.1 2B predictions on gold-92

## Budget

- **Estimated:** $3–8 USD
- GPU: A100 or H100 (~1 hour including setup); inference itself is negligible
- No paid data or external APIs

## Success Criteria

1. All 93 clips transcribed in both runs (no-biasing and keyword-biased)
2. All registered metrics computed with valid BCa bootstrap confidence intervals
3. Entity accuracy (domain vocab) measured and compared to t0004 baseline (94.5%)
4. Keyword-biasing gain quantified (Δ entity accuracy and Δ WER)
5. Latency p50 measured and feasibility vs. 200 ms target assessed
6. Streaming / NAR path assessed and documented
7. Predictions assets created and verified
8. Results document includes side-by-side comparison vs. Whisper baseline and interpretation:
   - If entity accuracy ≥ 94.5%: confirms Granite as viable production candidate
   - If entity accuracy < 94.5%: identifies gap and recommends fine-tuning direction or fallback
   - If latency > 200 ms: documents batch-only limitation and recommends NAR variant or buffering
     shim

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set, NEVER tune on)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline (WER, entity
  accuracy, 31-term domain vocabulary); defines comparison target
- **t0005_stt_model_survey_brainpowa** — identified Granite 4.1 2B as #1 benchmark candidate;
  documented keyword biasing mechanism, WER, VRAM footprint, and integration path
- **t0006_nemotron_3_5_benchmark** — parallel benchmark of Nemotron 3.5 (streaming native); Granite
  results should be compared with Nemotron results when both complete
- **S-0005-01** — source suggestion: "Benchmark IBM Granite Speech 4.1 2B on gold-92 for entity
  accuracy and latency"
- **brainpowa-realtime-api** integration target — Granite findings will inform STTAdapter brick
  implementation (HuggingFace Transformers backend + async wrapper)
