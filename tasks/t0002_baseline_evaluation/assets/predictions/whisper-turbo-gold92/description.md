---
spec_version: "2"
predictions_id: "whisper-turbo-gold92"
documented_by_task: "t0002_baseline_evaluation"
date_documented: "2026-06-23"
---
# Whisper turbo on Gold-92

## Metadata

* **Name**: Whisper turbo on Gold-92
* **Model**: Whisper turbo (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper turbo, run locally on an Apple
M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU inference) on the
gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in this project, containing
93 annotated WAV clips from Rezolve production investor-relations voice sessions, with accented
English speakers across three source categories: `clean_voices` (speaker-narrated IR Q&A),
`production` (live production session captures), and `error_cases` (known hard cases including
adversarial and multilingual inputs).

Whisper turbo is a distilled variant of Whisper Large v3 developed by OpenAI to achieve near-large
accuracy at substantially reduced inference cost. This evaluation quantifies whether turbo's
compression trades off significantly on entity accuracy for the Rezolve investor-relations domain,
or whether it achieves a better speed-accuracy tradeoff than large-v3 for production deployment.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper turbo
hypothesis, per-clip entity accuracy (all-or-nothing Caubrière et al. 2020 criterion), per-clip
WER, inference latency in seconds, and entity span annotations indicating which action-critical
entities (brand names, product lines, IR terms) were correctly recognised. These results sit
alongside the `whisper-large-v3-gold92` predictions to enable direct comparison between model
variants.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for this
clip is a normal English sentence; this clip is included in WER computation but excluded from the
aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper turbo is a distilled transformer-based encoder-decoder ASR model released by OpenAI as a
faster alternative to Whisper Large v3. The turbo variant has approximately 809 million parameters
— roughly half the size of large-v3 (~1.5B) — achieved through structured distillation that
preserves the decoder architecture while reducing encoder depth. OpenAI reports that turbo achieves
similar transcription quality to large-v3 on standard ASR benchmarks while running approximately
8x faster in real-time factor on CPU.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The model
was loaded once before the inference loop and applied identically to all 93 clips. The inference
configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing `language="en"`
is mandatory to prevent a documented failure mode where accented English speech is misclassified as
a non-English language, producing garbled transcripts. The model was warmed up on 3 throwaway clips
before recording latencies. Total inference wall-clock time was approximately 6.6 minutes on Apple
M5 CPU, compared to 8.8 minutes for large-v3 — a ~25% reduction on this CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn from
three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which has
normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied to audio
files — they were passed directly to faster-whisper as WAV files.

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
* `entity_spans_reference` — list of detected action-critical entity spans with type and position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing, null for
  anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()` (local CPU only,
  not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | 0.2518 | (0.1812, 0.3370) |
| wer_gold92 | 0.1063 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 4.25s | — |

Entity accuracy of 25.2% matches Whisper Large v3 exactly, confirming that the turbo distillation
preserves entity-level behaviour on this domain. WER of 10.6% is marginally higher than large-v3
(10.0%), consistent with the expected slight quality tradeoff from distillation. Latency p50 of
4.25s is approximately 25% faster than large-v3 (5.66s) on Apple M5 CPU.

## Main Ideas

* Whisper turbo achieves **entity_accuracy_gold92 = 25.2%**, identical to Whisper Large v3 (25.2%)
  — the distillation preserves entity-level accuracy on this IR domain
* WER of **10.6%** is marginally higher than large-v3 (10.0%), a small tradeoff consistent with
  expected distillation loss on non-native accented speech
* Latency p50 of **4.25s** is ~25% faster than large-v3 (5.66s) on Apple M5 CPU — both remain
  far above the 800ms voice-to-action production target, confirming that local CPU inference is
  not viable for production regardless of model size
* The identical entity accuracy between turbo and large-v3 suggests that turbo is the preferred
  variant for subsequent fine-tuning experiments: equivalent baseline quality, faster iteration
  cycles, and lower inference cost on GPU infrastructure

## Summary

These predictions capture the performance of Whisper turbo, OpenAI's distilled large-v3 variant,
on the gold-92 investor-relations benchmark using local CPU inference. The model was applied without
fine-tuning or domain-specific prompt injection to establish a comparative open-source baseline
alongside the Whisper Large v3 run in the same task.

The headline finding is that Whisper turbo achieves **identical entity accuracy (25.2%)** and
**comparable WER (10.6% vs 10.0%)** to Whisper Large v3, while being approximately 25% faster on
Apple M5 CPU (latency p50: 4.25s vs 5.66s). Both models share the same entity recognition failure
patterns — "Rezolve AI" transcribed as "Resolve AI" or "Hizol", "brainpowa" as "brain power" — confirming
that the gap between large-v3 and turbo in the IR domain is negligible before fine-tuning.

Given that turbo matches large-v3 entity accuracy at lower cost, it is the preferred model for
subsequent fine-tuning and post-correction experiments. The 10.6% WER baseline and 4.25s CPU
latency define the starting point that domain adaptation must beat. Both WER and latency
improvements require GPU infrastructure or specialised lightweight models rather than model-size
changes within the Whisper family.
