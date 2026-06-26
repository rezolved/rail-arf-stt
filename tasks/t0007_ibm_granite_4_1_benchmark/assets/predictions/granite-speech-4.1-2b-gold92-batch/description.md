---
spec_version: "1"
predictions_id: granite-speech-4.1-2b-gold92-batch
task: t0007_ibm_granite_4_1_benchmark
date_created: "2026-06-25"
model: ibm-granite/granite-speech-4.1-2b
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** IBM Granite Speech 4.1 2B — batch (no biasing)
- **Task:** t0007_ibm_granite_4_1_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU (bfloat16), HuggingFace Transformers 4.57.6, no vocabulary biasing
- **Date:** 2026-06-25

## Overview

Per-clip predictions from IBM Granite Speech 4.1 2B in batch mode with no keyword biasing on
the gold-92 benchmark. This variant establishes the Granite unbiased baseline to quantify the
contribution of keyword biasing.

## Model

- **HuggingFace ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** GraniteSpeechForConditionalGeneration + AutoProcessor
- **Params:** ~2B
- **Framework:** HuggingFace Transformers 4.57.6
- **Hardware:** GPU, bfloat16, ~4 GB VRAM
- **Biasing:** None

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production investor-relations
sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Stereo clips pre-converted to mono via soundfile channel-averaging. Anomaly clip `error_en_0005`
(Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Granite Speech transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 12.3% |
| Entity accuracy (gold-92) | 19.5% |
| Entity accuracy (domain vocab) | 31.9% |
| Action-critical WER | 43.0% |
| Intent preservation | 84.9% |
| Latency p50 | 0.250s |

## Main Ideas

- Without biasing, Granite achieves only 19.5% entity accuracy and 31.9% domain-vocab accuracy
- Keyword biasing raises EA from 19.5% to 40.2% (+20.7 pp) and EA_DV from 31.9% to 98.5% (+66.6 pp)
- Biasing is the decisive mechanism; unbiased Granite is not production-ready
