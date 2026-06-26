---
spec_version: "1"
predictions_id: parakeet-tdt-0.6b-v3-gold92-unbiased
task: t0009_parakeet_production_baseline
date_created: "2026-06-25"
model: nvidia/parakeet-tdt-0.6b-v3
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — unbiased
- **Task:** t0009_parakeet_production_baseline
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva SDK, standard inference, no keyword injection
- **Date:** 2026-06-25

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 in standard inference mode (no keyword
biasing) on the gold-92 benchmark. This variant establishes the unbiased baseline for Rezolve's
current production STT model.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** GPU
- **Biasing:** None

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production investor-relations
sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Anomaly clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Parakeet transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 15.1% |
| Entity accuracy (gold-92) | 23.4% |
| Entity accuracy (domain vocab) | 31.9% |
| Action-critical WER | 34.2% |
| Intent preservation | 87.1% |
| Latency p50 | 0.039s |
