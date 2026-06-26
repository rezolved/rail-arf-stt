---
spec_version: "1"
predictions_id: parakeet-tdt-0.6b-v3-gold92-production
task: t0009_parakeet_production_baseline
date_created: "2026-06-25"
model: nvidia/parakeet-tdt-0.6b-v3
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — biased (production config)
- **Task:** t0009_parakeet_production_baseline
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva SDK, keyword injection matching current production deployment
- **Date:** 2026-06-25

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 with the keyword biasing configuration
currently deployed in Rezolve's brainpowa production pipeline. This is the canonical production
baseline used for comparison across all t0006–t0010 benchmark tasks.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** GPU
- **Biasing:** Keyword injection matching current production deployment

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
| WER (gold-92) | 15.2% |
| Entity accuracy (gold-92) | 23.2% |
| Entity accuracy (domain vocab) | 33.3% |
| Action-critical WER | 33.5% |
| Intent preservation | 87.1% |
| Latency p50 | 0.038s |

## Main Ideas

- This is the production baseline used for all t0006–t0010 comparisons
- Keyword biasing provides negligible benefit vs. unbiased: ΔEA=−0.2 pp, ΔEA_DV=+1.4 pp
- Ultra-low latency (38 ms) is the model's decisive strength for production deployment
- Entity accuracy 23.2% and AC-WER 33.5% set the floor all benchmark models must exceed
