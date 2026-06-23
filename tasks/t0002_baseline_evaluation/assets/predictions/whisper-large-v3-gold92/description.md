---
spec_version: "2"
predictions_id: "whisper-large-v3-gold92"
documented_by_task: "t0002_baseline_evaluation"
date_documented: "2026-06-23"
---
# Whisper Large v3 on Gold-92

## Metadata

* **Name**: Whisper Large v3 on Gold-92
* **Model**: Whisper Large v3 (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper Large v3, run locally on an
Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU inference) on the
gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in this project, containing
93 annotated WAV clips from Rezolve production investor-relations voice sessions, with accented
English speakers across three source categories: `clean_voices` (speaker-narrated IR Q&A),
`production` (live production session captures), and `error_cases` (known hard cases including
adversarial and multilingual inputs).

The predictions serve as the open-source STT baseline for the Rezolve brainpowa voice commerce
project. Whisper Large v3 is the state-of-the-art general-purpose ASR model from OpenAI and
represents the best available open-source ceiling before any domain-specific fine-tuning or
post-correction. These results define the starting point against which entity-aware post-correction,
domain fine-tuning, and confidence-based routing approaches will be judged in subsequent tasks.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
hypothesis, per-clip entity accuracy (using the all-or-nothing Caubrière et al. 2020 criterion),
per-clip WER, inference latency in seconds, and entity span annotations indicating which
action-critical entities (brand names, product lines, IR terms) were correctly recognised.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for this
clip is a normal English sentence; this clip is included in WER computation but excluded from the
aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 is a transformer-based encoder-decoder ASR model trained by OpenAI on 680,000 hours
of multilingual speech data. The Large v3 variant contains approximately 1.5 billion parameters and
achieves 2.7% WER on LibriSpeech test-clean under clean conditions. On non-native spontaneous
English (LearnerVoice benchmark), Whisper Large v3 achieves 19.18% WER, consistent with the expected
range for accented investor-relations speech.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The model was
loaded once before the inference loop and applied identically to all 93 clips. The inference
configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing `language="en"`
is mandatory to prevent a documented failure mode where accented English speech is misclassified as
a non-English language, producing garbled transcripts. The model was warmed up on 3 throwaway clips
before recording latencies to avoid cold-cache measurements. Total inference wall-clock time was
approximately 9 minutes on Apple M5 CPU.

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
| wer_gold92 | 0.1003 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 5.66s | — |

Entity accuracy of 25.2% reflects the challenging nature of the investor-relations domain for a
general-purpose ASR model. Known failure patterns include: "Rezolve AI" transcribed as "resolve AI"
or "Hizol"; "brainpowa" transcribed as "brain power"; IR abbreviations (20-F, 10-K) inconsistently
formatted. WER of 10.0% indicates overall transcription quality is reasonable but entity-level
accuracy (the primary metric) is significantly lower.

## Main Ideas

* Whisper Large v3 achieves **10.0% WER** on gold-92, within the expected range for accented
  investor-relations speech (8-20% from research literature)
* **Entity accuracy of 25.2%** reveals a substantial gap between overall transcription quality and
  entity-level precision — the primary failure mode for voice commerce
* The known failure pattern "Rezolve AI" → "resolve AI" / "Hizol" appears frequently across
  production and clean_voices clips, confirming that entity post-correction is needed
* Intent preservation of **90.3%** (heuristic proxy) suggests most utterances retain their
  high-level intent even when entity accuracy is low
* Inference latency p50 of **5.66s** (local CPU) exceeds the 800ms voice-to-action target —
  dedicated GPU or cloud API is required for production latency requirements

## Summary

These predictions capture the performance of Whisper Large v3, the leading open-source ASR model, on
the gold-92 investor-relations benchmark using local CPU inference. The model was applied without
fine-tuning or domain-specific prompt injection to establish a clean open-source baseline.

The headline finding is that overall transcription quality (WER: 10.0%) is acceptable but
entity-level accuracy (entity_accuracy_gold92: 25.2%) is low. This gap reflects the model's
difficulty with proper nouns and domain-specific terms that are rare in its training data —
particularly "Rezolve AI", "brainpowa", and IR-domain abbreviations. Intent preservation (heuristic
proxy: 90.3%) shows that most utterances retain sufficient semantic content for basic intent
detection even with imperfect entity recognition.

These results establish the Whisper Large v3 baseline that subsequent post-correction, fine-tuning,
and confidence-routing tasks will need to beat. The comparison against Deepgram Nova-2 (production
baseline) will be added once the Deepgram API key is available (see
intervention/deepgram_api_key_missing.md).
