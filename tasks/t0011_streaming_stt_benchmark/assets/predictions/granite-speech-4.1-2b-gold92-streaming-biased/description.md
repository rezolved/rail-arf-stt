---
spec_version: "1"
predictions_id: granite-speech-4.1-2b-gold92-streaming-biased
task: t0011_streaming_stt_benchmark
date_created: "2026-06-26"
model: ibm-granite/granite-speech-4.1-2b
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** Granite Speech 4.1 2B — keyword biased, streaming simulation
- **Task:** t0011_streaming_stt_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** Azure H100 NVL, Transformers BF16, 32 kB PCM chunk streaming simulation
- **Date:** 2026-06-26

## Overview

Per-clip predictions from ibm-granite/granite-speech-4.1-2b with keyword prompt injection
(`"transcribe the speech to text. Keywords: Rezolve, Rezolve Ai, ..."`, 31 domain terms) under
production-style streaming: audio delivered as 32 kB PCM int16 chunks (~1 s at 16 kHz),
accumulated in memory, transcribed on None sentinel. Mirrors `STTAdapter.transcribe_stream()`.

## Model

- **HuggingFace ID / Model ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** Granite Speech 4.1 2B (encoder-decoder), ~2B params
- **Framework:** HuggingFace Transformers, BF16
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** Keyword prompt injection — 31 domain vocabulary terms

## Streaming Simulation

- Chunk size: 32,000 bytes = 16,000 samples = ~1 s at 16 kHz int16
- Mean chunks/clip: 6.7 (avg audio duration ~6.7 s)
- Latency clock: starts at first chunk delivery, ends when transcription returns
- Accumulate-then-transcribe: all chunks buffered, single model call at end

## Data

Gold-92 benchmark: 93 WAV clips from Rezolve production investor-relations sessions.
Anomaly clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92-streaming.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Granite transcript
- `latency_seconds`: wall-clock from first chunk to transcript (float)
- `num_chunks`: number of 32 kB chunks delivered
- `audio_duration_seconds`: clip audio duration

## Metrics

| Metric | Streaming | Batch (t0007) | Delta |
| --- | --- | --- | --- |
| WER (gold-92) | 8.8% | 8.8% | 0.00 pp |
| Entity accuracy (gold-92) | 41.1% | 40.2% | +0.87 pp |
| Entity accuracy (domain vocab) | 97.1% | 98.6% | −1.45 pp |
| Action-critical WER | 7.6% | 8.2% | −0.63 pp |
| Intent preservation | 93.6% | 92.5% | +1.08 pp |
| Latency p50 | 0.250 s | 0.248 s | +0.001 s |

## Main Ideas

- Streaming delivery has no measurable effect on accuracy (all deltas within noise)
- Granite streaming outperforms Parakeet streaming on all accuracy metrics
- Latency overhead from streaming is negligible (+1 ms)
- Granite p50 latency 250 ms well within 800 ms SLA
