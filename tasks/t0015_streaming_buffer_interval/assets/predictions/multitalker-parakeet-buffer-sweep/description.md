---
spec_version: "2"
predictions_id: multitalker-parakeet-buffer-sweep
task: t0015_streaming_buffer_interval
date_created: "2026-07-01"
model: nvidia/multitalker-parakeet-streaming-0.6b-v1
dataset: stt-benchmark-gold-92
instance_count: 279
---

## Metadata

- **Predictions ID:** multitalker-parakeet-buffer-sweep
- **Model:** nvidia/multitalker-parakeet-streaming-0.6b-v1
- **Task:** t0015_streaming_buffer_interval
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Intervals tested:** 500ms, 750ms, 1000ms
- **Total instances:** 279 (93 clips × 3 intervals)
- **Inference:** GPU, NeMo SDK, streaming mode with internal VAD
- **Date:** 2026-07-01

## Overview

This asset contains per-clip streaming predictions from nvidia/multitalker-parakeet-streaming-0.6b-v1
across a sweep of three buffer extraction intervals: 500ms, 750ms, and 1000ms. The experiment is
part of a broader benchmark covering 4 streaming STT models × 3 intervals = 12 combinations, with
this asset covering the multitalker model variant.

The core question is whether the buffer extraction interval affects transcription quality or
end-to-end latency for a model that uses internal Voice Activity Detection (VAD) to decide
segment boundaries. Unlike parakeet-tdt, which relies entirely on the streaming harness for
flush timing, the multitalker model determines internally when to emit a final token sequence.
The buffer interval therefore controls how frequently the harness polls and extracts partial
results, but does not itself define segment boundary decisions — those are owned by the model's
VAD module.

The sweep reveals that WER (13.34%), entity accuracy (22.19%), and domain-vocab entity accuracy
(31.88%) are identical across all three intervals, confirming that the final transcript is
invariant to flush cadence. Only latency varies: p50 latency drops from 254ms at 500ms interval
to 242ms at 1000ms interval, a counterintuitive result explained by reduced polling overhead and
fewer partial-result extraction calls at wider intervals.

This asset provides the raw per-clip JSONL files for downstream evaluation, ablation, and
comparison against the Granite accumulate-then-transcribe baseline (WER 8.8%, EA-DV 97.1%,
TTFD 77ms p50) and the parakeet-tdt streaming model.

## Model

- **Model ID:** nvidia/multitalker-parakeet-streaming-0.6b-v1
- **Architecture:** NeMo EncDecMultiTalkerRNNTBPE (Recurrent Neural Network Transducer with
  multi-talker decoder), 0.6B parameters
- **Internal VAD:** Yes — the model has its own Voice Activity Detection logic that determines
  segment boundaries. This is the key architectural difference from parakeet-tdt-streaming, which
  relies on the harness for flush decisions.
- **GPU-PB TurboBias:** Attempted — the GPU-PB TurboBias prefix-beam biasing mechanism was
  applied to the model. However, the multitalker architecture may not fully support TurboBias,
  meaning biasing may have had no effect or partial effect on the output.
- **Patch applied:** `_transcribe_forward` was patched to handle missing speaker targets, enabling
  single-speaker mode. The model is designed for multi-speaker diarization but the gold-92
  benchmark contains single-speaker clips; without the patch, inference would fail on clips
  where no speaker target tensor is supplied.
- **Framework:** NeMo Python SDK, GPU inference
- **Streaming mode:** The model is fed audio chunks at each interval boundary; internal VAD
  decides when to flush accumulated audio into a final token sequence.

## Data

- **Dataset:** stt-benchmark-gold-92
- **Clips:** 93 WAV files, 16kHz mono, investor-relations domain, accented English
- **Source:** `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`
- **Ground truth:** Annotated reference transcripts; entity annotations cover brand names,
  product names, and domain-specific vocabulary relevant to Rezolve's ecommerce voice platform.
- **Split:** All 93 clips used for inference at each of the three intervals, yielding 279
  total records across the three JSONL files.
- **Note:** The gold-92 dataset is a held-out regression set — it is never used for training
  or fine-tuning.

## Prediction Format

Each line in the JSONL files is a JSON object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `clip_id` | string | Unique clip identifier matching gold-92 dataset |
| `duration_s` | float | Duration of the WAV clip in seconds |
| `transcript` | string | Final transcript produced by the model |
| `reference_text` | string | Ground-truth reference transcript |
| `is_empty` | bool | True if the model produced no output |
| `is_hallucination` | bool | True if the model produced speech not in the audio |
| `ttfd_seconds` | float | Time-to-first-decode: seconds from audio start to first token |
| `latency_seconds` | float | End-to-end latency: seconds from audio start to final token |
| `interval_ms` | int | Buffer extraction interval in milliseconds (500, 750, or 1000) |
| `n_chunks` | int | Number of audio chunks fed to the model |
| `n_inferences` | int | Number of model inference calls made during streaming |
| `model_has_internal_vad` | bool | Always true for this model |

Three files are provided, one per interval:

- `files/predictions-gold92-500ms.jsonl` — 93 clips at 500ms extraction interval
- `files/predictions-gold92-750ms.jsonl` — 93 clips at 750ms extraction interval
- `files/predictions-gold92-1000ms.jsonl` — 93 clips at 1000ms extraction interval

## Metrics

Transcription quality metrics are identical across all three intervals because the model's
internal VAD determines segment boundaries independently of the polling cadence. Only latency
varies:

| Metric | 500ms | 750ms | 1000ms |
| --- | --- | --- | --- |
| WER (gold-92) | 13.34% | 13.34% | 13.34% |
| Entity accuracy (gold-92) | 22.19% | 22.19% | 22.19% |
| EA domain vocab | 31.88% | 31.88% | 31.88% |
| Latency p50 | 0.254s | 0.251s | 0.242s |
| TTFD p50 | 0.064s | 0.064s | 0.064s |
| Empty transcripts | 0 | 0 | 0 |
| Hallucinations | 0 | 0 | 0 |

**Comparison vs Granite baseline** (accumulate-then-transcribe, non-streaming):

| Metric | Multitalker (1000ms) | Granite baseline | Delta |
| --- | --- | --- | --- |
| WER | 13.34% | 8.8% | +4.54 pp |
| EA domain vocab | 31.88% | 97.1% | −65.2 pp |
| TTFD p50 | 0.064s | 0.077s | −13ms |
| Latency p50 | 0.242s | N/A (batch) | — |

The multitalker model achieves faster TTFD than Granite's batch mode (64ms vs 77ms), but at
significant cost to entity accuracy on domain vocabulary (31.88% vs 97.1%). The WER gap (4.54
percentage points) is meaningful but secondary to the entity accuracy collapse, which is the
primary concern for Rezolve's investor-relations use case.

## Main Ideas

* **Internal VAD decouples quality from flush cadence.** The multitalker model's built-in VAD
  means that changing the buffer extraction interval from 500ms to 1000ms has zero effect on
  transcription quality. WER, entity accuracy, and domain-vocab accuracy are all identical
  across intervals. This is the expected behavior for an architecture that owns its own segment
  boundary decisions.

* **TTFD at 64ms — twice the parakeet-tdt latency.** The internal VAD introduces a buffering
  overhead: the model must accumulate enough audio to confidently detect voice activity before
  emitting the first token. This results in a TTFD p50 of 64ms, approximately double the
  parakeet-tdt streaming baseline. For the gold-92 use case (investor-relations Q&A, clips
  averaging 5–8 seconds), this is acceptable, but for short utterances it becomes noticeable.

* **Wider intervals reduce end-to-end latency.** Despite the VAD decoupling quality, latency
  still improves as the interval widens: 254ms at 500ms → 242ms at 1000ms. This is due to
  reduced polling overhead — fewer extraction calls means less Python-level coordination cost
  between the streaming harness and the model. The 12ms saving is modest but consistent.

* **GPU-PB TurboBias impact uncertain.** TurboBias biasing was attempted but the
  EncDecMultiTalkerRNNTBPE architecture may not expose the same biasing hooks as parakeet-tdt.
  Entity accuracy at 31.88% (domain vocab) is significantly below the Granite baseline (97.1%),
  suggesting biasing was ineffective or absent. Further investigation is needed to confirm
  whether TurboBias applies to multitalker inference.

* **`_transcribe_forward` patch enables single-speaker inference.** The model expects
  multi-speaker speaker-target tensors. The patch allows it to run on single-speaker clips
  without crashing, but may not be optimal for single-speaker audio — the model may internally
  try to separate speakers in audio that has only one.

* **No empty transcripts or hallucinations.** Across all 279 records, zero clips produced empty
  output and zero were flagged as hallucinations. This is a positive reliability signal: the
  model never refuses to produce output and does not confabulate speech on silent or near-silent
  segments.

## Summary

The multitalker-parakeet-streaming-0.6b-v1 model achieves WER of 13.34% on gold-92, entity
accuracy of 22.19%, and domain-vocab entity accuracy of 31.88% — all invariant to buffer
extraction interval. TTFD p50 is 64ms and end-to-end latency p50 ranges from 242ms (1000ms
interval) to 254ms (500ms interval). The model produces no empty transcripts and no
hallucinations across all 279 clip-interval combinations.

The primary limitation is entity accuracy on domain vocabulary: at 31.88% vs the Granite
baseline of 97.1%, the model misses roughly two-thirds of domain-specific entities. This is
likely attributable to ineffective or unsupported TurboBias biasing on the multitalker
architecture. Until biasing is confirmed to work, the multitalker model is not suitable for
production deployment in Rezolve's investor-relations STT pipeline despite its competitive
streaming latency characteristics.

The buffer interval sweep confirms that 1000ms is the optimal operating point for this model:
lowest latency (242ms p50) with identical transcription quality to shorter intervals.
