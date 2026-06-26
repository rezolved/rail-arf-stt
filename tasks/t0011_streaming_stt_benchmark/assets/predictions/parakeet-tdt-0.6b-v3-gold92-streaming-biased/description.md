---
spec_version: "1"
predictions_id: parakeet-tdt-0.6b-v3-gold92-streaming-biased
task: t0011_streaming_stt_benchmark
date_created: "2026-06-26"
model: nvidia/parakeet-tdt-0.6b-v3
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — biased (production config), streaming simulation
- **Task:** t0011_streaming_stt_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** Azure H100 NVL, NeMo / Riva SDK, 32 kB PCM chunk streaming simulation
- **Date:** 2026-06-26

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 with production keyword biasing (NeMo
GPU-PB phrase boosting, alpha=1.0) under production-style streaming: audio delivered as
32 kB PCM int16 chunks (~1 s at 16 kHz), accumulated in memory, transcribed on None sentinel.
Mirrors the `STTAdapter.transcribe_stream()` default accumulate-then-transcribe pattern.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB phrase boosting, 66 casing variants, alpha=1.0

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
- `hypothesis`: Parakeet transcript
- `latency_seconds`: wall-clock from first chunk to transcript (float)
- `num_chunks`: number of 32 kB chunks delivered
- `audio_duration_seconds`: clip audio duration

## Metrics

| Metric | Streaming | Batch (t0009) | Delta |
| --- | --- | --- | --- |
| WER (gold-92) | 15.2% | 15.2% | +0.05 pp |
| Entity accuracy (gold-92) | 23.1% | 23.2% | −0.05 pp |
| Entity accuracy (domain vocab) | 33.3% | 33.3% | +0.03 pp |
| Action-critical WER | 33.5% | 33.5% | +0.04 pp |
| Intent preservation | 87.1% | 87.1% | 0.00 pp |
| Latency p50 | 0.041 s | 0.038 s | +0.003 s |

## Main Ideas

- Streaming delivery has no measurable effect on accuracy (all deltas < 0.1 pp)
- Accumulate-then-transcribe is functionally equivalent to batch at segment level
- Latency overhead from streaming is negligible (+3 ms) — chunk iteration is near-instant
- Parakeet remains the fastest model at 41 ms p50, 6× faster than Granite under streaming
