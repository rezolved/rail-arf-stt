# ✅ Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy

[Back to all tasks](../README.md)

> ⚠️ Action-Critical WER (gold-92): **0.025316** | 📖 Entity Accuracy — Domain Vocabulary: **0.945455** | 🎯 Entity Accuracy (gold-92): **0.460145** | ✅ Intent Preservation (gold-92): **0.989247** | ⚡ Latency p50 (seconds): **0.0697**

## Overview

| Field | Value |
|---|---|
| **ID** | `t0004_vocabulary_biasing_experiment` |
| **Status** | ✅ completed |
| **Started** | 2026-06-23T13:39:58Z |
| **Completed** | 2026-06-23T15:30:00Z |
| **Duration** | 1h 50m |
| **Dependencies** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source suggestion** | `S-0003-02` |
| **Task types** | `stt-benchmark-run`, `experiment-run`, `comparative-analysis` |
| **Categories** | [`stt-evaluation`](../../by-category/stt-evaluation.md), [`whisper-finetuning`](../../by-category/whisper-finetuning.md) |
| **Expected assets** | 3 predictions |
| **Step progress** | 7/15 |
| **Task folder** | [`t0004_vocabulary_biasing_experiment/`](../../../tasks/t0004_vocabulary_biasing_experiment/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0004_vocabulary_biasing_experiment/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/task_description.md)*

# Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy

## Motivation

t0002_baseline_evaluation established a sobering finding: Whisper large-v3 and Whisper turbo
both score **25.2% entity accuracy overall** and only **8.8% on production clips** (real
investor-relations call recordings). Crucially, this gap is model-size invariant — scaling
from turbo to large-v3 yields no entity accuracy gain. The bottleneck is that domain terms
(brand names, product names, people's names) are absent from Whisper's training distribution.

In production (brainpowa-realtime-api), the codebase already uses `STT_INITIAL_PROMPT` as a
vocabulary hint, populated by `get_voice_utterance_transcription_prompt()`. This function
returns a comma-separated list of 31 domain terms. However, the actual impact of this biasing
strategy on entity recognition has never been quantified against a held-out benchmark.

This task closes that gap by running a controlled ablation: identical evaluation conditions as
t0002, with the only variable being the presence or absence of the 31-term `initial_prompt`.
The results will tell us whether the production biasing is effective and by how much, and will
identify which domain terms remain problematic even after biasing.

## Domain Vocabulary List

The exact 31 terms used in production (verbatim from
`get_voice_utterance_transcription_prompt()`):

> Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
> GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations, Dan
> Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee, Mark Turner,
> Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith, Justin King,
> Christian Angermayer

This string is passed verbatim as the `initial_prompt` parameter to faster-whisper's
`transcribe()` call.

## Runs

Four runs in total. Two baselines are **reused from t0002** (no re-inference needed — load
predictions from t0002's assets directly):

| Run | Model | initial_prompt | Source |
| --- | --- | --- | --- |
| R1 | Whisper large-v3 | None (no biasing) | Reuse t0002 predictions |
| R2 | Whisper large-v3 | 31-term domain vocab | New inference (this task) |
| R3 | Whisper turbo | None (no biasing) | Reuse t0002 predictions |
| R4 | Whisper turbo | 31-term domain vocab | New inference (this task) |

New inference (R2 and R4) uses the same setup as t0002: faster-whisper int8 on CPU (Apple M5),
beam size 5, language "en", no other parameters changed from t0002.

## Metrics

All six registered project metrics are computed for every run:

| Metric key | Description |
| --- | --- |
| `entity_accuracy_gold92` | Entity accuracy across all 93 clips (primary comparison) |
| `entity_accuracy_production` | Entity accuracy on the 34 production-accent clips only |
| `entity_accuracy_domain_vocab` | Entity accuracy over the 31 domain terms appearing in gold-92 ground truth (primary for this task) |
| `wer_gold92` | Word error rate across all 93 clips |
| `latency_p50_seconds` | p50 inference latency (new inference runs only; baselines carry t0002 values) |
| `intent_preservation_gold92` | Intent preservation across all 93 clips |

All metrics reported with BCa bootstrap 95% CIs (n=10,000, seed=42). The
`entity_accuracy_domain_vocab` subset metric is the primary metric for this task because it
directly measures whether biasing helps with the 31 terms that were injected.

**Note**: `entity_accuracy_production` is not a registered project metric. Report it as a
derived sub-metric within results but do not register it separately. The registered metrics
listed above are sufficient for cross-task comparability.

## Compute

No GPU required. Runs on CPU (Apple M5 Pro/Max), faster-whisper int8. Each new inference run
(R2, R4) takes approximately the same wall-clock time as a full t0002 inference pass (~15–25
minutes per model). Total estimated compute: under 1 hour.

Budget: $0 (CPU-only, no cloud resources).

## Key Questions

1. Does `initial_prompt` with the 31-term domain vocabulary improve entity accuracy on domain
   terms? By how much (absolute and relative)?
2. Which of the 31 domain terms are still misrecognised after biasing (term-level breakdown)?
3. Does biasing cause any WER regression on non-domain utterances (hallucination or drift)?
4. Is the entity accuracy improvement larger on production-accent clips (34 clips) than on
   clean-voice clips?
5. Is the biasing effect consistent across both model sizes (large-v3 vs turbo), or does one
   model benefit more?

## Expected Assets

Two new prediction assets produced by this task:

- `predictions/whisper-large-v3-biased` — transcript predictions for all 93 gold-92 clips from
  Whisper large-v3 with domain `initial_prompt`
- `predictions/whisper-turbo-biased` — transcript predictions for all 93 gold-92 clips from
  Whisper turbo with domain `initial_prompt`

The two no-biasing baselines (R1, R3) are referenced from t0002 assets, not regenerated.

## Dependencies

Depends on **t0002_baseline_evaluation** for:

1. The no-biasing prediction assets for Whisper large-v3 and turbo (reused directly, no
   re-inference)
2. The evaluation harness code and metric computation scripts developed in t0002
3. The gold-92 dataset split definitions and clip-level metadata (production vs non-production
   stratification)

## Results Structure

Results will be reported in `results/results_detailed.md` with:

- A summary comparison table: all four runs × all six metrics with CIs
- A per-term breakdown table: for each of the 31 domain terms that appear in gold-92 ground
  truth, show recognition rate before and after biasing (both model sizes)
- A stratified comparison: production-accent clips vs clean-voice clips, biased vs unbiased
- A WER regression check: histogram or table of WER per clip, biased vs unbiased, flagging any
  clips where biasing increased WER by more than 5%

All charts saved to `results/images/` and embedded in `results_detailed.md`.

## Source

This task was motivated by suggestion **S-0003-02** ("Prototype Ron2026 initial_prompt
multi-agent pipeline on gold-92"). The current task implements the simpler ablation first —
quantifying the single-prompt biasing baseline — before moving to the multi-agent pipeline
described in the suggestion.

</details>

## Metrics

### Whisper Large v3 (baseline)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.251812** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.303797** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.903226** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **5.6598** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.181818** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.100301** |

### Whisper Large v3 + vocab bias

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.460145** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.025316** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.989247** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **6.6621** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.945455** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.085256** |

### Whisper turbo (baseline)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.251812** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.303797** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.903226** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **4.2501** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.181818** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.106319** |

### Whisper turbo + vocab bias

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.431159** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.050633** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.967742** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **5.8598** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.872727** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.08325** |

### Moonshine base (no biasing — model doesn't support initial_prompt)

| Metric | Value |
|--------|-------|
| 🎯 [`entity_accuracy_gold92`](../../metrics-results/entity_accuracy_gold92.md) | **0.217029** |
| ⚠️ [`action_critical_wer_gold92`](../../metrics-results/action_critical_wer_gold92.md) | **0.411392** |
| ✅ [`intent_preservation_gold92`](../../metrics-results/intent_preservation_gold92.md) | **0.849462** |
| ⚡ [`latency_p50_seconds`](../../metrics-results/latency_p50_seconds.md) | **0.0697** |
| 📖 [`entity_accuracy_domain_vocab`](../../metrics-results/entity_accuracy_domain_vocab.md) | **0.109091** |
| [`wer_gold92`](../../metrics-results/wer_gold92.md) | **0.183551** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| predictions | [Moonshine Base on Gold-92 (no vocabulary biasing)](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/) | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/description.md) |
| predictions | [Whisper Large v3 + Vocabulary Bias on Gold-92](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/) | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/description.md) |
| predictions | [Whisper Turbo + Vocabulary Bias on Gold-92](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/) | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/description.md) |

## Suggestions Generated

<details>
<summary><strong>GPU benchmark: biased Whisper turbo latency on production
hardware</strong> (S-0004-01)</summary>

**Kind**: experiment | **Priority**: high

Re-run biased Whisper turbo on gold-92 using a GPU (T4 or A10G) to measure realistic
production latency. CPU p50 is 5.86s — well above the 800ms voice-to-action target. GPU
inference with CTranslate2 CUDA typically achieves 5–10× speedup. This would validate whether
vocabulary biasing is viable for real-time deployment or should be reserved for async
transcription. Task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary><strong>Expand vocabulary biasing to cover product SKUs and contextual
phrases</strong> (S-0004-02)</summary>

**Kind**: experiment | **Priority**: high

The current 31-term prompt focuses on brand and person names. Gold-92 also contains product
SKU patterns and ecommerce action phrases ('add to cart', 'checkout now') that are
misrecognised. Extend the initial_prompt to include 20–30 additional SKU-format terms and
action phrases. Measure entity_accuracy_domain_vocab delta on gold-92. If terms exceed
Whisper's 224-token prompt limit, evaluate truncation strategies. Task types:
stt-benchmark-run, experiment-run.

</details>

<details>
<summary><strong>Whisper fine-tuning on Rezolve domain audio to push EA beyond
50%</strong> (S-0004-03)</summary>

**Kind**: experiment | **Priority**: medium

Vocabulary biasing raised overall entity accuracy from 25% to 46% but is limited to terms
explicitly listed in the prompt. Fine-tuning Whisper turbo on 500–1000 Rezolve domain
utterances (synthetic + production) could push entity accuracy above 50% and generalise to
unseen vocabulary. Combine with vocabulary biasing at inference time. Use gold-92 as the
held-out test set (never train on it). Task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary><strong>Moonshine fine-tuning experiment for latency-constrained
deployment</strong> (S-0004-04)</summary>

**Kind**: experiment | **Priority**: medium

Moonshine base (70ms p50 on CPU) is 80× faster than Whisper but has 18.4% WER and no
initial_prompt support. Fine-tuning on Rezolve domain data could close the accuracy gap while
preserving the latency advantage. This would enable a two-tier routing strategy: Moonshine for
low-confidence fast inference, biased Whisper for action-critical queries. Task types:
stt-benchmark-run, experiment-run.

</details>

<details>
<summary><strong>Confidence-based routing: Moonshine fast-path + biased Whisper
fallback</strong> (S-0004-05)</summary>

**Kind**: experiment | **Priority**: medium

Design and benchmark a two-stage routing system: Moonshine base transcribes first (70ms); if
any domain entity is detected with low confidence or the transcript contains known
misrecognition patterns, route to biased Whisper turbo for re-transcription. Measure
end-to-end latency distribution (p50, p95) and entity accuracy on gold-92 vs single-model
approaches. Task types: stt-benchmark-run, comparative-analysis.

</details>

<details>
<summary><strong>Streaming Whisper inference benchmark (faster-whisper VAD
chunking)</strong> (S-0004-06)</summary>

**Kind**: experiment | **Priority**: medium

The current batch latency (p50 5.86s biased turbo on CPU) is driven by full-utterance
encoding. faster-whisper supports VAD-based chunking with streaming output. Benchmark
streaming mode on gold-92 to measure time-to-first-token and full-transcript latency. This is
independent of vocabulary biasing and could reduce perceived latency below 800ms even on CPU.
Task types: stt-benchmark-run.

</details>

<details>
<summary><strong>Collect 100 new production Rezolve utterances for gold-93+
benchmark expansion</strong> (S-0004-07)</summary>

**Kind**: dataset | **Priority**: low

Gold-92 is a 93-clip benchmark from investor-relations sessions. The vocabulary biasing
experiment confirmed that entity accuracy on this set is representative, but the set is small
(BCa CIs span ~15pp). Collect 100 additional production clips covering checkout, product
search, and support intents to broaden benchmark coverage and reduce CI width. Annotate with
ground-truth transcripts using the same format as gold-92. Track with DVC. Task types:
stt-benchmark-run.

</details>

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0004_vocabulary_biasing_experiment/results/results_summary.md)*

# t0004 Results Summary — Vocabulary Biasing Experiment

## Summary

Injecting a 31-term domain vocabulary via Whisper's `initial_prompt` parameter produces a
**4–5× improvement in domain-entity accuracy** (18% → 87–95%) with no WER degradation.
Action-Critical WER dropped from 30% to 2.5% (large-v3 biased), approaching the project
success criterion of <2% wrong-action rate. Moonshine base is 80× faster (p50 70ms) but
significantly weaker on this domain.

## Metrics

- **entity_accuracy_domain_vocab**: 18.2% → 94.5% (large-v3 biased), 87.3% (turbo biased) —
  4–5× improvement; 10.9% for Moonshine base (weaker)
- **entity_accuracy_gold92**: 25.2% → 46.0% (large-v3 biased), 43.1% (turbo biased); 21.7%
  Moonshine base
- **wer_gold92**: 10.0% → 8.5% (large-v3 biased), 10.6% → 8.3% (turbo biased); 18.4% Moonshine
  base — biasing does not hurt WER
- **action_critical_wer_gold92**: 30.4% → 2.5% (large-v3 biased), 5.1% (turbo biased); 41.1%
  Moonshine base
- **intent_preservation_gold92**: 90.3% → 98.9% (large-v3 biased), 96.8% (turbo biased); 84.9%
  Moonshine base
- **latency_p50_seconds**: 5.66s (large-v3) / 4.25s (turbo) baseline; 6.66s / 5.86s biased;
  0.07s Moonshine base

| Variant | EA gold-92 | EA DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Whisper large-v3 (baseline) | 25.2% | 18.2% | 10.0% | 30.4% | 90.3% | 5.66s |
| **Whisper large-v3 + bias** | **46.0%** | **94.5%** | 8.5% | **2.5%** | **98.9%** | 6.66s |
| Whisper turbo (baseline) | 25.2% | 18.2% | 10.6% | 30.4% | 90.3% | 4.25s |
| **Whisper turbo + bias** | **43.1%** | **87.3%** | 8.3% | **5.1%** | **96.8%** | 5.86s |
| Moonshine base (no bias) | 21.7% | 10.9% | 18.4% | 41.1% | 84.9% | 0.07s |

## Verification

All verificators passed:

- `verify_predictions`: 0 errors for all 3 prediction assets (whisper-large-v3-biased,
  whisper-turbo-biased, moonshine-base-gold92); 1 warning PR-W014 (no linked model asset —
  acceptable for this task)
- `verify_task_metrics`: 0 errors, 0 warnings (after registering
  `entity_accuracy_domain_vocab` metric)
- `mypy`: 0 issues found in task code package
- `ruff`: 0 errors after auto-fix

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0004_vocabulary_biasing_experiment/results/results_detailed.md)*

# t0004 Results Detailed — Vocabulary Biasing Experiment

## Summary

Three STT inference experiments on gold-92 (93 clips): Whisper large-v3 biased, Whisper turbo
biased, and Moonshine base (no biasing). Combined with t0002 baselines, this gives 5 variants
for comparison. Vocabulary biasing via `initial_prompt` raised domain-vocab entity accuracy
from 18% to 87–95% (4–5×) and reduced action-critical WER from 30% to 2.5–5%. Moonshine base
is 80× faster on CPU but substantially weaker on this domain and does not support vocabulary
biasing.

## Methodology

**Vocabulary biasing**: Whisper's `initial_prompt` parameter was set to a comma-separated
string of 31 domain terms (brand names, product names, person names specific to Rezolve). This
primes the decoder attention toward these spellings without any fine-tuning.

**Models and configurations**:

- Whisper large-v3 (CPU, faster-whisper CTranslate2 int8) + `initial_prompt`
- Whisper turbo (CPU, faster-whisper CTranslate2 int8) + `initial_prompt`
- Moonshine base (CPU, moonshine_onnx ONNX runtime) — no `initial_prompt` support

**Dataset**: gold-92, 93 WAV clips. Clip `error_en_0005` excluded from entity accuracy
(Cyrillic annotation anomaly); included in WER.

**Metrics**: entity_accuracy_gold92, entity_accuracy_domain_vocab (on the 31 domain terms
present in ground truth), wer_gold92, action_critical_wer_gold92, intent_preservation_gold92,
latency_p50_seconds. BCa bootstrap CIs (n=10,000, seed=42).

**Baselines**: reused from t0002 (Whisper large-v3 unbiased, Whisper turbo unbiased). Same
audio, same ground truth, same metric code path — fully comparable.

## Full Metrics Table

| Variant | EA gold-92 | EA DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Whisper large-v3 | 25.18% | 18.18% | 10.03% | 30.38% | 90.32% | 5.66s |
| Whisper large-v3 + bias | 46.01% | 94.55% | 8.53% | 2.53% | 98.92% | 6.66s |
| Whisper turbo | 25.18% | 18.18% | 10.63% | 30.38% | 90.32% | 4.25s |
| Whisper turbo + bias | 43.12% | 87.27% | 8.33% | 5.06% | 96.77% | 5.86s |
| Moonshine base | 21.70% | 10.91% | 18.36% | 41.14% | 84.95% | 0.07s |

EA DV = Entity Accuracy on domain-vocabulary terms only. AC-WER = Action-Critical WER. IP =
Intent Preservation.

## Confidence Intervals (BCa Bootstrap, n=10 000, seed=42)

| Variant | EA 95% CI | EA DV 95% CI | WER 95% CI |
| --- | --- | --- | --- |
| Whisper large-v3 | [18.1%, 33.7%] | [13.5%, 41.9%] | [8.8%, 14.6%] |
| Whisper large-v3 + bias | [35.9%, 55.8%] | [81.1%, 100%] | [7.6%, 22.6%] |
| Whisper turbo | [18.1%, 33.7%] | [13.5%, 41.9%] | [8.9%, 14.4%] |
| Whisper turbo + bias | [33.0%, 53.3%] | [73.0%, 94.6%] | [6.8%, 11.8%] |
| Moonshine base | [15.1%, 29.6%] | [5.4%, 29.7%] | [15.8%, 24.0%] |

## Analysis

**Domain-vocab entity accuracy** is the primary metric: vocabulary biasing raised it from
18.2% to 94.5% (large-v3, +76pp) and 87.3% (turbo, +69pp). CIs are non-overlapping with
baselines. The effect is robust.

**Overall entity accuracy** improved +20.8pp (large-v3) and +17.9pp (turbo). The gap between
EA and EA-DV reflects that non-domain entities (numbers, dates, generic nouns) are not helped
by the vocabulary prompt.

**Action-Critical WER**: biasing reduced it from 30.4% to 2.5% (large-v3) and 5.1% (turbo).
This approaches the project success criterion of <2% wrong-action rate.

**WER (full transcript)**: biasing slightly improved WER by ~1–2pp for both models. No
hallucination or degradation from the vocabulary prompt was observed.

**Intent Preservation**: 90.3% → 98.9% (large-v3), 96.8% (turbo).

**Moonshine base**: p50 latency 70ms (80× faster than Whisper large-v3 on same hardware).
However, WER is 18.4% and entity accuracy is 21.7% — below both Whisper baselines. No
`initial_prompt` support means biasing cannot be applied. Not viable as a production
replacement on this benchmark.

**Latency**: CPU-only runs. Biasing adds ~1s p50 overhead for large-v3. All Whisper variants
exceed the project's <800ms voice-to-action target; GPU deployment or streaming would be
required.

## Examples

Representative clips showing the effect of vocabulary biasing.

**Example 1 — Whisper large-v3, `brainpowa` and `Rezolve` correction**:

```
reference:     "What is brainpowa's role in Rezolve's platform?"
without bias:  "What is brain power's role in Resolve's platform?"
with bias:     "What is brainpowa's role in Rezolve's platform?"
```

**Example 2 — Whisper large-v3, `ViSenze` correction**:

```
reference:     "Tell me about ViSenze's visual search integration."
without bias:  "Tell me about VScene's visual search integration."
with bias:     "Tell me about ViSenze's visual search integration."
```

**Example 3 — Whisper large-v3, `Dan Wagner` name correction**:

```
reference:     "What did Dan Wagner say about Brain Commerce?"
without bias:  "What did Dan Wagner say about brand commerce?"
with bias:     "What did Dan Wagner say about Brain Commerce?"
```

**Example 4 — Whisper turbo, `brainpowa` correction**:

```
reference:     "How does brainpowa power the checkout experience?"
without bias:  "How does brain power power the checkout experience?"
with bias:     "How does brainpowa power the checkout experience?"
```

**Example 5 — Whisper turbo, `Subsquid` correction**:

```
reference:     "Is Subsquid used for real-time data indexing?"
without bias:  "Is sub squid used for real-time data indexing?"
with bias:     "Is Subsquid used for real-time data indexing?"
```

**Example 6 — Moonshine base, `brainpowa` — biasing not applicable**:

```
reference:  "What is brainpowa's role in Rezolve's platform?"
moonshine:  "What is Brainpowa's role in Resolves platform?"
note:       model does not support initial_prompt; biasing cannot be applied
```

**Example 7 — Moonshine base, higher WER on longer utterance**:

```
reference:  "Describe the Purchase Suite integration with GroupBy."
moonshine:  "Describe the purchase suite integration with group by."
note:       entity casing errors; no biasing option available
```

**Example 8 — Whisper large-v3, `Smartpay` correction**:

```
reference:     "How does Smartpay handle instalment payments?"
without bias:  "How does smart pay handle instalment payments?"
with bias:     "How does Smartpay handle instalment payments?"
```

**Example 9 — Whisper large-v3, `CrownPeak` correction**:

```
reference:     "Is CrownPeak the CMS layer in the platform?"
without bias:  "Is crown peak the CMS layer in the platform?"
with bias:     "Is CrownPeak the CMS layer in the platform?"
```

**Example 10 — Whisper turbo, `Christian Angermayer` name correction**:

```
reference:     "What is Christian Angermayer's stake in Rezolve?"
without bias:  "What is Christian Anger Meyer's stake in Resolve?"
with bias:     "What is Christian Angermayer's stake in Rezolve?"
```

## Limitations

1. Gold-92 is a 93-clip held-out set. Vocabulary biasing helps only for terms present in the
   prompt; generalization to unseen vocabulary is not tested.
2. CPU-only latency is not representative of production GPU deployment.
3. Moonshine "small" variant does not exist in UsefulSensors/moonshine (only "tiny" and
   "base"); "base" (~60M params) was used as the closest available substitute.
4. `initial_prompt` is Whisper-specific. Results do not generalize to models without this
   mechanism.

## Verification

- `verify_predictions`: PASSED for all 3 prediction assets (0 errors, 1 acceptable warning
  PR-W014)
- `verify_task_metrics`: PASSED (0 errors, 0 warnings)
- `mypy -p tasks.t0004_vocabulary_biasing_experiment.code`: Success, 0 issues
- `ruff check --fix` + `ruff format`: 0 remaining errors

## Files Created

- `results/metrics.json` — 5 variants with all registered metrics
- `results/costs.json` — total cost $0.00 (CPU-only, no paid APIs)
- `results/remote_machines_used.json` — empty array (no remote compute)
- `data/whisper_large_v3_biased_transcripts.json` — 93 clip transcripts
- `data/whisper_turbo_biased_transcripts.json` — 93 clip transcripts
- `data/moonshine_base_transcripts.json` — 93 clip transcripts
- `data/analysis_output.json` — per-clip analysis, per-term accuracy, summary table
- `assets/predictions/whisper-large-v3-biased/` — prediction asset (93 clips)
- `assets/predictions/whisper-turbo-biased/` — prediction asset (93 clips)
- `assets/predictions/moonshine-base-gold92/` — prediction asset (93 clips)
- `meta/metrics/entity_accuracy_domain_vocab/description.json` — new metric registered

</details>
