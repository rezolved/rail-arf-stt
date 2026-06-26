---
spec_version: "1"
predictions_id: seaco-paraformer-large-gold92-batch
task: t0010_funasr_paraformer_benchmark
date_created: "2026-06-25"
model: iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** FunASR SeACo-Paraformer-en — batch (no biasing)
- **Task:** t0010_funasr_paraformer_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, FunASR Python SDK, standard Paraformer inference, no SeACo biasing
- **Date:** 2026-06-25

## Overview

Per-clip predictions from FunASR SeACo-Paraformer-en in standard batch mode (no contextual
biasing) on the gold-92 benchmark. The model produces near-random English-sounding tokens on
English input; WER=122.7% indicates complete transcription failure. This variant establishes
the unbiased baseline for the SeACo ablation.

## Model

- **Model ID:** iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020
- **Architecture:** Paraformer (CTC) with SeACo contextual biasing module
- **Framework:** FunASR Python SDK
- **Hardware:** GPU
- **Biasing:** None

## Data

93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Anomaly clip `error_en_0005` excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Paraformer transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 122.7% |
| Entity accuracy (gold-92) | 2.2% |
| Entity accuracy (domain vocab) | 0.0% |
| Action-critical WER | 100.0% |
| Intent preservation | 55.9% |
| Latency p50 | 0.048s |

## Main Ideas

- WER > 100% confirms complete transcription failure on English input
- Model produces Chinese-phoneme-adjacent English syllable sequences, not transcriptions
- Not suitable for any English STT use case at Rezolve
