# Predictions by Date Added

7 predictions asset(s) grouped by creation date.

[Back to all predictions](../README.md)

---

## 2026-06-25 (2)

<details>
<summary>📊 <strong>Moonshine v2 Medium on Gold-92</strong>
(<code>moonshine-v2-medium-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-v2-medium-gold92` |
| **Model ID** | — |
| **Model** | Moonshine Streaming Medium (UsefulSensors/moonshine-streaming-medium), transformers CPU inference, ~266M params, sliding-window Transformer encoder |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.165496
* **entity_accuracy_gold92**: 0.217029
* **entity_accuracy_domain_vocab**: 0.090909
* **intent_preservation_gold92**: 0.870968
* **latency_p50_seconds**: 0.2321

## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** CPU, transformers 5.12.1, no biasing
- **Date:** 2026-06-25

## Overview

This asset contains per-clip predictions from Moonshine Streaming Medium on the gold-92
benchmark. Moonshine is a streaming Transformer encoder-decoder STT model from UsefulSensors,
optimised for edge and low-latency deployment. The medium variant has approximately 266M
parameters and uses a sliding-window encoder architecture.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder + auto-regressive decoder
- **Params:** ~266M
- **Framework:** HuggingFace Transformers (MoonshineStreamingForConditionalGeneration)
- **Hardware:** CPU inference
- **Biasing:** None (no vocabulary boosting or prompt injection)

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

One anomaly clip (`error_en_0005`) has Cyrillic ground truth due to an annotation error; it is
included in WER computation but excluded from entity accuracy aggregates.

## Prediction Format

Each line in `files/predictions-gold92.jsonl` is a JSON object with:

- `clip_id`: string identifier
- `ground_truth`: reference transcript
- `prediction`: Moonshine v2 Medium hypothesis
- `wer_local`: per-clip word error rate (float)
- `entity_accuracy_local`: per-clip entity accuracy (float or null for anomaly clip)
- `latency_ms`: inference latency in milliseconds (float)
- `latency_stage`: one of `cold_start`, `warmup`, `warmed`

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 0.1655 |
| Entity accuracy (gold-92) | 0.2170 |
| Entity accuracy (domain vocab) | 0.0909 |
| Action-critical WER | 0.3418 |
| Intent preservation | 0.8710 |
| Wrong-action rate | 0.1290 |
| Latency p50 (warmed) | 0.233s |

## Main Ideas

- Moonshine v2 Medium (CPU) achieves WER=16.6% on gold-92, 2x worse than Whisper large-v3
  (8.5%)
- Domain-vocabulary entity accuracy is 9.1% vs 94.5% for Whisper with biasing — 85pp gap
- Excellent warmed latency: 0.233s p50 (29x faster than Whisper 6.66s)
- Entity recognition failures are vocabulary-driven (OOV domain terms), not capacity-driven
- Model is not production-ready for Rezolve's voice commerce use case without vocabulary
  biasing

## Summary

Moonshine v2 Medium achieves reasonable general WER (16.6%) but significantly underperforms
Whisper on domain-specific entity accuracy (9.1% vs 94.5% domain-vocab accuracy). The model
does not support vocabulary biasing or initial prompt injection, which explains the poor
performance on Rezolve-specific entity terms. Warmed-up latency p50 is 0.233s, which is
excellent for the streaming use case. The model is not recommended for production deployment
without vocabulary biasing or fine-tuning.

</details>

<details>
<summary>📊 <strong>Moonshine v2 Medium Shallow-Fusion Feasibility
Assessment</strong>
(<code>moonshine-v2-medium-gold92-biasing-assessment</code>) — — instances
(jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-v2-medium-gold92-biasing-assessment` |
| **Model ID** | — |
| **Model** | Moonshine v2 Medium — shallow fusion feasibility assessment (no inference run) |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | — |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92-biasing-assessment/description.md) |

## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Type:** Feasibility assessment (no per-clip predictions)
- **Date:** 2026-06-25

## Overview

This asset documents a feasibility assessment for adding shallow-fusion vocabulary biasing to
Moonshine v2 Medium. The assessment was motivated by the model's low domain-vocabulary entity
accuracy (9.1%) compared to Whisper with vocabulary biasing (94.5%). No inference was run for
this asset; it is an architectural analysis only.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder-decoder (not CTC)
- **Key constraint:** No `initial_prompt` support; no built-in hotword boosting

## Data

References the gold-92 benchmark and Rezolve domain vocabulary (31 terms) from
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py`.

## Prediction Format

Assessment document only. See `files/shallow_fusion_feasibility.md` for the full analysis.

## Metrics

Not applicable (no inference run for this asset).

## Main Ideas

- Moonshine v2 Medium uses an encoder-decoder architecture that blocks the easiest
  shallow-fusion path (CTC hotword boosting via pyctcdecode)
- Log-linear N-best rescoring (KenLM domain LM) is the recommended approach: ~3-5 days effort,
  +50-80ms latency overhead per clip
- Feasibility verdict: "needs research" — the approach is architecturally viable but 85pp
  entity accuracy gap vs Whisper biased is unlikely to close fully from shallow fusion alone
- Hybrid routing (Moonshine for latency-critical queries, Whisper for entity-critical) may
  offer the best production trade-off

## Summary

Three shallow-fusion approaches were assessed:

1. **Log-linear N-best rescoring** (recommended): Rescore top-4 beams with a KenLM domain LM.
   Effort: 3-5 days. Latency overhead: +50-80ms.
2. **pyctcdecode CTC hotword boosting**: Requires CTC-head surgery or an official CTC variant.
   Blocked by encoder-decoder architecture.
3. **Lattice rescoring**: Similar to approach 1 but with full lattice; higher complexity for
   marginal gain.

**Verdict:** Viable for production (with effort), but the entity accuracy gap vs. Whisper is
large. A hybrid routing strategy (Moonshine for latency-critical, Whisper for entity-critical)
may be optimal.

</details>

## 2026-06-23 (5)

<details>
<summary>📊 <strong>Moonshine Base on Gold-92 (no vocabulary biasing)</strong>
(<code>moonshine-base-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-base-gold92` |
| **Model ID** | — |
| **Model** | UsefulSensors/moonshine-base (~60M parameters) run via useful-moonshine-onnx (ONNX, CPU, 16 kHz). No vocabulary biasing supported. Note: UsefulSensors has no 'small' variant; 'base' is the closest equivalent. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.217029
* **wer_gold92**: 0.183551

# Moonshine Base on Gold-92 (no vocabulary biasing)

## Metadata

* **Name**: Moonshine Base on Gold-92 (no vocabulary biasing)
* **Model**: UsefulSensors Moonshine base (~60M parameters, ONNX CPU)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of UsefulSensors Moonshine base (~60M
parameters, ONNX CPU) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

UsefulSensors Moonshine base (~60M parameters, ONNX CPU) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.2170 |
| wer_gold92 | 0.1836 |
| latency_p50_seconds | 0.07s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper Large v3 + Vocabulary Bias on Gold-92</strong>
(<code>whisper-large-v3-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-large-v3-biased` |
| **Model ID** | — |
| **Model** | OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to a 31-term domain vocabulary string covering Rezolve brand names, product lines, and key people. No fine-tuning applied. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.460145
* **wer_gold92**: 0.085256

# Whisper Large v3 + Vocabulary Bias on Gold-92

## Metadata

* **Name**: Whisper Large v3 + Vocabulary Bias on Gold-92
* **Model**: Whisper Large v3 (~1.5B parameters, faster-whisper INT8)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of Whisper Large v3 (~1.5B parameters,
faster-whisper INT8) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 (~1.5B parameters, faster-whisper INT8) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.4601 |
| wer_gold92 | 0.0853 |
| latency_p50_seconds | 6.66s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper Large v3 on Gold-92</strong>
(<code>whisper-large-v3-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-large-v3-gold92` |
| **Model ID** | — |
| **Model** | OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en') on Apple M5 Mac. No fine-tuning or domain adaptation. Production-ready but latency-constrained for local CPU. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Documentation** | [`description.md`](../../../tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.251812
* **wer_gold92**: 0.100301

# Whisper Large v3 on Gold-92

## Metadata

* **Name**: Whisper Large v3 on Gold-92
* **Model**: Whisper Large v3 (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper Large v3, run locally on
an Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU
inference) on the gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in
this project, containing 93 annotated WAV clips from Rezolve production investor-relations
voice sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases including adversarial and multilingual inputs).

The predictions serve as the open-source STT baseline for the Rezolve brainpowa voice commerce
project. Whisper Large v3 is the state-of-the-art general-purpose ASR model from OpenAI and
represents the best available open-source ceiling before any domain-specific fine-tuning or
post-correction. These results define the starting point against which entity-aware
post-correction, domain fine-tuning, and confidence-based routing approaches will be judged in
subsequent tasks.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
hypothesis, per-clip entity accuracy (using the all-or-nothing Caubrière et al. 2020
criterion), per-clip WER, inference latency in seconds, and entity span annotations indicating
which action-critical entities (brand names, product lines, IR terms) were correctly
recognised.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 is a transformer-based encoder-decoder ASR model trained by OpenAI on 680,000
hours of multilingual speech data. The Large v3 variant contains approximately 1.5 billion
parameters and achieves 2.7% WER on LibriSpeech test-clean under clean conditions. On
non-native spontaneous English (LearnerVoice benchmark), Whisper Large v3 achieves 19.18% WER,
consistent with the expected range for accented investor-relations speech.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The
model was loaded once before the inference loop and applied identically to all 93 clips. The
inference configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing
`language="en"` is mandatory to prevent a documented failure mode where accented English
speech is misclassified as a non-English language, producing garbled transcripts. The model
was warmed up on 3 throwaway clips before recording latencies to avoid cold-cache
measurements. Total inference wall-clock time was approximately 9 minutes on Apple M5 CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which
has normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied
to audio files — they were passed directly to faster-whisper as WAV files.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Resolv AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": false}],
  "entity_accuracy": 0.0,
  "wer": 0.083,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper Large v3 output (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans with type and
  position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing, null for
  anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()` (local CPU
  only, not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | 0.2518 | (0.1812, 0.3370) |
| wer_gold92 | 0.1003 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 5.66s | — |

Entity accuracy of 25.2% reflects the challenging nature of the investor-relations domain for
a general-purpose ASR model. Known failure patterns include: "Rezolve AI" transcribed as
"resolve AI" or "Hizol"; "brainpowa" transcribed as "brain power"; IR abbreviations (20-F,
10-K) inconsistently formatted. WER of 10.0% indicates overall transcription quality is
reasonable but entity-level accuracy (the primary metric) is significantly lower.

## Main Ideas

* Whisper Large v3 achieves **10.0% WER** on gold-92, within the expected range for accented
  investor-relations speech (8-20% from research literature)
* **Entity accuracy of 25.2%** reveals a substantial gap between overall transcription quality
  and entity-level precision — the primary failure mode for voice commerce
* The known failure pattern "Rezolve AI" → "resolve AI" / "Hizol" appears frequently across
  production and clean_voices clips, confirming that entity post-correction is needed
* Intent preservation of **90.3%** (heuristic proxy) suggests most utterances retain their
  high-level intent even when entity accuracy is low
* Inference latency p50 of **5.66s** (local CPU) exceeds the 800ms voice-to-action target —
  dedicated GPU or cloud API is required for production latency requirements

## Summary

These predictions capture the performance of Whisper Large v3, the leading open-source ASR
model, on the gold-92 investor-relations benchmark using local CPU inference. The model was
applied without fine-tuning or domain-specific prompt injection to establish a clean
open-source baseline.

The headline finding is that overall transcription quality (WER: 10.0%) is acceptable but
entity-level accuracy (entity_accuracy_gold92: 25.2%) is low. This gap reflects the model's
difficulty with proper nouns and domain-specific terms that are rare in its training data —
particularly "Rezolve AI", "brainpowa", and IR-domain abbreviations. Intent preservation
(heuristic proxy: 90.3%) shows that most utterances retain sufficient semantic content for
basic intent detection even with imperfect entity recognition.

These results establish the Whisper Large v3 baseline that subsequent post-correction,
fine-tuning, and confidence-routing tasks will need to beat. The comparison against Deepgram
Nova-2 (production baseline) will be added once the Deepgram API key is available (see
intervention/deepgram_api_key_missing.md).

</details>

<details>
<summary>📊 <strong>Whisper Turbo + Vocabulary Bias on Gold-92</strong>
(<code>whisper-turbo-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-turbo-biased` |
| **Model ID** | — |
| **Model** | OpenAI Whisper turbo (~809M parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to a 31-term domain vocabulary string covering Rezolve brand names, product lines, and key people. No fine-tuning applied. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.431159
* **wer_gold92**: 0.08325

# Whisper Turbo + Vocabulary Bias on Gold-92

## Metadata

* **Name**: Whisper Turbo + Vocabulary Bias on Gold-92
* **Model**: Whisper turbo (~809M parameters, faster-whisper INT8)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of Whisper turbo (~809M parameters,
faster-whisper INT8) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper turbo (~809M parameters, faster-whisper INT8) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.4312 |
| wer_gold92 | 0.0832 |
| latency_p50_seconds | 5.86s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper turbo on Gold-92</strong>
(<code>whisper-turbo-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-turbo-gold92` |
| **Model ID** | — |
| **Model** | OpenAI Whisper turbo (~809M parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en') on Apple M5 Mac. No fine-tuning or domain adaptation. Whisper turbo is a distilled variant offering comparable accuracy to large-v3 at roughly 8x faster inference. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Documentation** | [`description.md`](../../../tasks/t0002_baseline_evaluation/assets/predictions/whisper-turbo-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.251812
* **wer_gold92**: 0.106319

# Whisper turbo on Gold-92

## Metadata

* **Name**: Whisper turbo on Gold-92
* **Model**: Whisper turbo (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper turbo, run locally on an
Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU inference)
on the gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in this
project, containing 93 annotated WAV clips from Rezolve production investor-relations voice
sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases including adversarial and multilingual inputs).

Whisper turbo is a distilled variant of Whisper Large v3 developed by OpenAI to achieve
near-large accuracy at substantially reduced inference cost. This evaluation quantifies
whether turbo's compression trades off significantly on entity accuracy for the Rezolve
investor-relations domain, or whether it achieves a better speed-accuracy tradeoff than
large-v3 for production deployment.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
turbo hypothesis, per-clip entity accuracy (all-or-nothing Caubrière et al. 2020 criterion),
per-clip WER, inference latency in seconds, and entity span annotations indicating which
action-critical entities (brand names, product lines, IR terms) were correctly recognised.
These results sit alongside the `whisper-large-v3-gold92` predictions to enable direct
comparison between model variants.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper turbo is a distilled transformer-based encoder-decoder ASR model released by OpenAI as
a faster alternative to Whisper Large v3. The turbo variant has approximately 809 million
parameters — roughly half the size of large-v3 (~1.5B) — achieved through structured
distillation that preserves the decoder architecture while reducing encoder depth. OpenAI
reports that turbo achieves similar transcription quality to large-v3 on standard ASR
benchmarks while running approximately 8x faster in real-time factor on CPU.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The
model was loaded once before the inference loop and applied identically to all 93 clips. The
inference configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing
`language="en"` is mandatory to prevent a documented failure mode where accented English
speech is misclassified as a non-English language, producing garbled transcripts. The model
was warmed up on 3 throwaway clips before recording latencies. Total inference wall-clock time
was approximately 6.6 minutes on Apple M5 CPU, compared to 8.8 minutes for large-v3 — a ~25%
reduction on this CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which
has normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied
to audio files — they were passed directly to faster-whisper as WAV files.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Resolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": false}],
  "entity_accuracy": 0.0,
  "wer": 0.083,
  "latency_seconds": 4.25,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper turbo output (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans with type and
  position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing, null for
  anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()` (local CPU
  only, not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | 0.2518 | (0.1812, 0.3370) |
| wer_gold92 | 0.1063 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 4.25s | — |

Entity accuracy of 25.2% matches Whisper Large v3 exactly, confirming that the turbo
distillation preserves entity-level behaviour on this domain. WER of 10.6% is marginally
higher than large-v3 (10.0%), consistent with the expected slight quality tradeoff from
distillation. Latency p50 of 4.25s is approximately 25% faster than large-v3 (5.66s) on Apple
M5 CPU.

## Main Ideas

* Whisper turbo achieves **entity_accuracy_gold92 = 25.2%**, identical to Whisper Large v3
  (25.2%) — the distillation preserves entity-level accuracy on this IR domain
* WER of **10.6%** is marginally higher than large-v3 (10.0%), a small tradeoff consistent
  with expected distillation loss on non-native accented speech
* Latency p50 of **4.25s** is ~25% faster than large-v3 (5.66s) on Apple M5 CPU — both remain
  far above the 800ms voice-to-action production target, confirming that local CPU inference
  is not viable for production regardless of model size
* The identical entity accuracy between turbo and large-v3 suggests that turbo is the
  preferred variant for subsequent fine-tuning experiments: equivalent baseline quality,
  faster iteration cycles, and lower inference cost on GPU infrastructure

## Summary

These predictions capture the performance of Whisper turbo, OpenAI's distilled large-v3
variant, on the gold-92 investor-relations benchmark using local CPU inference. The model was
applied without fine-tuning or domain-specific prompt injection to establish a comparative
open-source baseline alongside the Whisper Large v3 run in the same task.

The headline finding is that Whisper turbo achieves **identical entity accuracy (25.2%)** and
**comparable WER (10.6% vs 10.0%)** to Whisper Large v3, while being approximately 25% faster
on Apple M5 CPU (latency p50: 4.25s vs 5.66s). Both models share the same entity recognition
failure patterns — "Rezolve AI" transcribed as "Resolve AI" or "Hizol", "brainpowa" as "brain
power" — confirming that the gap between large-v3 and turbo in the IR domain is negligible
before fine-tuning.

Given that turbo matches large-v3 entity accuracy at lower cost, it is the preferred model for
subsequent fine-tuning and post-correction experiments. The 10.6% WER baseline and 4.25s CPU
latency define the starting point that domain adaptation must beat. Both WER and latency
improvements require GPU infrastructure or specialised lightweight models rather than
model-size changes within the Whisper family.

</details>
