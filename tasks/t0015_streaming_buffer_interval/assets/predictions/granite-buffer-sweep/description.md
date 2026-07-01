---
spec_version: "2"
predictions_id: granite-buffer-sweep
name: Granite Speech 4.1 2B Buffer Interval Sweep on gold-92
date_created: "2026-07-01"
created_by_task: t0015_streaming_buffer_interval
dataset_ids:
  - stt-benchmark-gold-92
categories:
  - stt-evaluation
  - latency-profiling
---

## Metadata

| Field | Value |
|---|---|
| Predictions ID | granite-buffer-sweep |
| Task | t0015_streaming_buffer_interval |
| Model | ibm-granite/granite-speech-4.1-2b |
| Dataset | stt-benchmark-gold-92 (gold-92), 93 clips |
| Instance count | 279 (93 clips × 3 intervals) |
| Intervals tested | 500ms, 750ms, 1000ms |
| Date created | 2026-07-01 |
| WER | 8.83% |
| Entity Accuracy | 96.25% |
| EA Domain Vocab | 97.10% |

## Overview

This asset contains predictions from IBM Granite Speech 4.1 2B evaluated under a streaming buffer interval sweep on the gold-92 benchmark dataset. The benchmark task (t0015_streaming_buffer_interval) evaluates 4 models across 3 buffer extraction intervals (500ms, 750ms, 1000ms), for a total of 12 model-interval combinations. This asset covers the Granite Speech 4.1 2B model across all three intervals.

The streaming buffer approach accumulates incoming PCM-16 audio chunks and re-transcribes the accumulated buffer at regular intervals. The interval parameter controls how frequently this re-transcription occurs: at 500ms, the model transcribes every half-second of audio accumulation; at 1000ms, it transcribes once per second. The final transcript is taken from the last inference call when the audio clip ends. Because WER and entity accuracy are computed on the final transcript, these quality metrics are identical across intervals for the same clip — the interval only affects latency and TTFD (time to first decode).

Granite Speech 4.1 2B is a seq2seq speech language model from IBM, capable of accepting natural-language prompts alongside the audio input. This property enables keyword prompt injection biasing, where a curated list of 31 domain-specific terms is supplied in the transcription prompt to steer the model toward correct recognition of proper nouns and technical vocabulary.

Granite achieves the best WER (8.83%) of all models benchmarked in this task, and dramatically outperforms the Parakeet CTC and RNNT models on entity recognition. Its main trade-off is higher latency: as a seq2seq architecture, it is slower than CTC/RNNT models, with p50 latency of 1.1–1.2 seconds depending on interval.

## Model

**Model:** ibm-granite/granite-speech-4.1-2b
**Architecture:** Sequence-to-sequence speech language model (2B parameters)
**Biasing method:** Keyword prompt injection (not NeMo GPU-PB)

Granite Speech 4.1 2B is a multimodal model that processes audio together with a text prompt. The prompt used for all clips in this asset is:

> "transcribe the speech to text. Keywords: Rezolve, brainpowa, ..." (31 domain terms total)

The 31 domain terms span Rezolve-specific product names, brand names, and technical vocabulary that appear in the investor-relations audio corpus (e.g., "Rezolve", "brainpowa", and other proprietary terms). Keyword prompt injection is an intrinsic biasing mechanism that does not require a separate biasing model or GPU-accelerated prefix boosting (unlike NeMo GPU-PB used for Parakeet models). This makes Granite's biasing simpler to deploy but also means the biasing is "soft" — the model is guided but not forced to prefer the listed terms.

The seq2seq architecture means Granite generates its transcript autoregressively, token by token, after processing the full audio context. This makes it inherently slower than discriminative (CTC/RNNT) models, which produce all output frames in a single forward pass. However, the generative nature also makes Granite more robust to complex pronunciation patterns and accented speech, which is why it achieves the lowest WER of all four benchmarked models.

A non-streaming baseline for Granite (accumulate-then-transcribe, from task t0014) achieved WER 8.8%, EA-DV 97.1%, and TTFD p50 77ms. The streaming buffer sweep results match this baseline almost exactly, confirming that Granite's final-transcript quality is robust to partial audio buffering — the model transcribes the full clip accurately regardless of how many intermediate inference calls were made during streaming.

## Data

**Dataset:** stt-benchmark-gold-92 (gold-92)
**Clips:** 93 WAV files, 16kHz mono, variable duration
**Domain:** Investor-relations, earnings calls, product presentations
**Speech characteristics:** Accented English (British, non-native speakers), domain-specific proper nouns, mixed technical and financial vocabulary

The gold-92 dataset is a curated benchmark of 93 audio clips drawn from investor-relations content relevant to the Rezolve AI product domain. Clips contain a variety of speakers with accented English pronunciation. The reference transcripts were manually verified. This dataset is particularly challenging for generic STT models due to the high density of brand names, product names, and neologisms (e.g., "brainpowa") that are absent from standard acoustic model training corpora.

Each of the three JSONL files in this asset (500ms, 750ms, 1000ms) contains predictions for all 93 clips at the corresponding buffer extraction interval, giving 279 prediction records in total. Fields recorded per clip include `clip_id`, `duration_s`, `transcript` (final predicted text), `reference_text`, `is_empty`, `is_hallucination`, `ttfd_seconds`, `latency_seconds`, `interval_ms`, `n_chunks`, and `n_inferences`.

Zero clips produced empty transcripts across all intervals, and zero hallucinations were detected. This reflects Granite's strong reliability on the gold-92 domain, even when running in streaming mode with frequent partial-audio inference calls.

## Prediction Format

Each file is JSONL (one JSON object per line). Fields:

| Field | Type | Description |
|---|---|---|
| clip_id | string | Unique clip identifier matching gold-92 dataset |
| duration_s | float | Audio clip duration in seconds |
| transcript | string | Final predicted transcript text |
| reference_text | string | Ground-truth reference transcript |
| is_empty | bool | True if transcript is empty or whitespace only |
| is_hallucination | bool | True if transcript is flagged as hallucination |
| ttfd_seconds | float | Time to first decode (seconds from stream start) |
| latency_seconds | float | Total transcription latency (seconds) |
| interval_ms | int | Buffer extraction interval in milliseconds |
| n_chunks | int | Number of audio chunks accumulated |
| n_inferences | int | Number of model inference calls made |

The three files differ only in `interval_ms`, `n_chunks`, `n_inferences`, `ttfd_seconds`, and `latency_seconds`. The `transcript` and all quality metrics are computed on the final transcript after the clip ends.

## Metrics

Quality metrics are computed on the final transcript (identical across intervals for the same clip):

| Metric | Value |
|---|---|
| WER (gold-92) | 8.83% |
| Entity Accuracy (gold-92) | 96.25% |
| EA Domain Vocab | 97.10% |
| Empty transcripts | 0 |
| Hallucinations | 0 |

Latency and TTFD metrics vary by interval:

| Interval | Latency p50 | TTFD p50 |
|---|---|---|
| 500ms | 1.232s | 0.077s |
| 750ms | 1.212s | 0.076s |
| 1000ms | 1.113s | 0.075s |

Key observations:
- **WER 8.83%** is the best of all four models benchmarked in t0015, making Granite the highest-quality transcription model in this sweep.
- **Entity Accuracy 96.25%** and **EA Domain Vocab 97.10%** are dramatically higher than the Parakeet models, demonstrating the effectiveness of keyword prompt injection for domain-specific vocabulary.
- **Latency increases at shorter intervals**: at 500ms, Granite makes more inference calls per clip (shorter buffering window means more frequent re-transcription), which adds overhead. Going from 500ms to 1000ms reduces latency p50 by ~10% (1.232s → 1.113s).
- **TTFD is nearly constant** at 75–77ms across intervals. Shorter intervals trigger the first decode sooner in absolute time, but the difference is minimal (2ms between 500ms and 1000ms intervals).
- **Latency is the main trade-off**: Granite's p50 latency of 1.1–1.2s is significantly higher than the Parakeet models due to autoregressive seq2seq decoding.

## Main Ideas

* **Keyword prompt injection outperforms NeMo GPU-PB for entity recall.** Unlike the Parakeet models (which use NeMo GPU prefix boosting), Granite relies on natural-language keyword injection in the transcription prompt. This soft biasing mechanism is easier to deploy and, in this benchmark, produces better entity accuracy (96.25% vs lower scores for Parakeet variants). The 31 domain terms are listed directly in the prompt, guiding but not forcing the model.

* **Buffer interval is a latency knob, not a quality knob.** Because WER and entity accuracy are computed on the final transcript (after the last inference call), they are independent of the buffer interval. The interval only affects how many inference calls occur during streaming and therefore total processing time. A 1000ms interval reduces inference call frequency and lowers latency p50 by ~10% compared to 500ms, with negligible cost to TTFD.

* **Streaming Granite matches non-streaming baseline.** The Granite non-streaming accumulate-and-transcribe baseline (task t0014) achieved WER 8.8% and EA-DV 97.1% — essentially identical to the streaming buffer sweep results. This confirms that introducing intermediate inference calls during streaming does not degrade Granite's final transcript quality. The model is robust to being shown partial audio.

* **Zero failures across all intervals.** No empty transcripts and no hallucinations were observed across 279 prediction records (93 clips × 3 intervals). This stands in contrast to some alternative models that show occasional hallucinations on very short clips. Granite's prompt-conditioned generation appears to constrain output to plausible transcription outputs.

* **Latency vs. quality trade-off favors 1000ms for production.** Given that quality is constant across intervals and latency improves at 1000ms, the 1000ms buffer interval is the recommended operating point for Granite in a production streaming pipeline where latency matters and TTFD requirements are loose (sub-100ms TTFD is met at all intervals).

## Summary

This asset provides per-clip streaming predictions for Granite Speech 4.1 2B (ibm-granite/granite-speech-4.1-2b) on the gold-92 benchmark (93 clips, investor-relations domain, accented English). The model was evaluated at three buffer extraction intervals — 500ms, 750ms, and 1000ms — producing 279 prediction records in total. Granite achieves the best quality of all models in the t0015 benchmark: WER 8.83%, entity accuracy 96.25%, and domain vocab entity accuracy 97.10%. These quality gains are attributable to the model's generative seq2seq architecture and its ability to accept keyword prompt injection biasing with 31 domain-specific terms. Quality is independent of buffer interval, as all three intervals produce identical final transcripts per clip.

The main trade-off is latency: Granite's autoregressive decoding yields p50 latency of 1.1–1.2 seconds, higher than CTC/RNNT alternatives. Within the sweep, increasing the interval from 500ms to 1000ms reduces latency p50 by approximately 10% (1.232s → 1.113s) at negligible cost to TTFD (77ms → 75ms). For production deployments prioritizing transcript quality over raw speed, the 1000ms interval offers the best latency-quality trade-off for Granite. No empty transcripts or hallucinations were observed across all 279 records, confirming Granite's reliability on this domain.
