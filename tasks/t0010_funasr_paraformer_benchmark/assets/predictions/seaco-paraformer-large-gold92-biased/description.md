---
spec_version: "1"
predictions_id: seaco-paraformer-large-gold92-biased
task: t0010_funasr_paraformer_benchmark
date_created: "2026-06-25"
model: iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** FunASR SeACo-Paraformer-en — contextual biased
- **Task:** t0010_funasr_paraformer_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, FunASR Python SDK, SeACo contextual biasing with DOMAIN_VOCAB
- **Date:** 2026-06-25

## Overview

Per-clip predictions from FunASR SeACo-Paraformer-en with SeACo contextual biasing activated
using Rezolve domain vocabulary terms. The model produces near-random English-sounding tokens
on English input; WER=122.2% indicates complete transcription failure. SeACo biasing has zero
measurable effect vs. batch (ΔEA=0.0pp, ΔEA_DV=0.0pp, ΔWER=−0.5pp).

## Model

- **Model ID:** iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020
- **Architecture:** Paraformer (CTC) with SeACo contextual biasing module
- **Framework:** FunASR Python SDK
- **Hardware:** GPU
- **Biasing:** SeACo module with DOMAIN_VOCAB terms from constants.py

## Data

93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Anomaly clip `error_en_0005` excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Paraformer transcript (SeACo biased)
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 122.2% |
| Entity accuracy (gold-92) | 2.2% |
| Entity accuracy (domain vocab) | 0.0% |
| Action-critical WER | 100.0% |
| Intent preservation | 55.9% |
| Latency p50 | 0.047s |

## Main Ideas

- SeACo biasing has zero effect: ΔEA=0.0pp, ΔEA_DV=0.0pp vs. batch
- WER > 100% confirms complete transcription failure; biasing cannot rescue a broken base model
- Not suitable for any English STT use case at Rezolve
