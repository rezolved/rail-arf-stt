---
predictions_id: moonshine-v2-medium-gold92
task: t0008_moonshine_v2_benchmark
date_created: "2026-06-25"
model: UsefulSensors/moonshine-streaming-medium
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** CPU, transformers 5.12.1, no biasing
- **Date:** 2026-06-25

## Overview

This asset contains per-clip predictions from Moonshine Streaming Medium on the gold-92 benchmark.
Moonshine is a streaming Transformer encoder-decoder STT model from UsefulSensors, optimised for
edge and low-latency deployment. The medium variant has approximately 266M parameters and uses a
sliding-window encoder architecture.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder + auto-regressive decoder
- **Params:** ~266M
- **Framework:** HuggingFace Transformers (MoonshineStreamingForConditionalGeneration)
- **Hardware:** CPU inference
- **Biasing:** None (no vocabulary boosting or prompt injection)

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production investor-relations
sessions with accented English speech. Ground truth transcripts are from
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

## Summary

Moonshine v2 Medium achieves reasonable general WER (16.6%) but significantly underperforms Whisper
on domain-specific entity accuracy (9.1% vs 94.5% domain-vocab accuracy). The model does not support
vocabulary biasing or initial prompt injection, which explains the poor performance on
Rezolve-specific entity terms. Warmed-up latency p50 is 0.233s, which is excellent for the streaming
use case. The model is not recommended for production deployment without vocabulary biasing or
fine-tuning.
