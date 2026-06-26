---
spec_version: "1"
predictions_id: nemotron-3.5-asr-gold92-word-boosted
task: t0006_nemotron_3_5_benchmark
date_created: "2026-06-25"
model: nvidia/nemotron-asr-en-fastconformer-ctc-large
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** NVIDIA Nemotron 3.5 ASR (streaming + word boosting)
- **Task:** t0006_nemotron_3_5_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva NIM, streaming mode with word-boosting API
- **Date:** 2026-06-25

## Overview

Per-clip predictions from NVIDIA Nemotron 3.5 ASR in streaming mode with the word-boosting API
applied using Rezolve domain vocabulary (brands, products, SKUs). This variant was expected to
improve entity accuracy, but instead degraded all accuracy metrics relative to batch.

## Model

- **Architecture:** FastConformer-CTC, streaming-native
- **Framework:** NVIDIA NeMo / Riva NIM, streaming mode
- **Biasing:** Word-boosting API with DOMAIN_VOCAB terms from constants.py

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production investor-relations
sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Anomaly clip `error_en_0005` has Cyrillic ground truth due to an annotation error; it is
included in WER computation but excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Nemotron ASR transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)
- `chunk_seconds`: streaming chunk size used (float)

## Metrics

| Metric | Value | vs. batch |
| --- | --- | --- |
| WER (gold-92) | 19.9% | +2.3 pp |
| Entity accuracy (gold-92) | 18.7% | −6.0 pp |
| Entity accuracy (domain vocab) | 12.7% | −5.5 pp |
| Action-critical WER | 42.4% | +10.8 pp |
| Intent preservation | 84.9% | −5.4 pp |
| Latency p50 | 0.723s | +0.004s |

## Main Ideas

- Word boosting degrades all accuracy metrics vs. batch: ΔEA=−6.0 pp, ΔWER=+2.3 pp
- Domain-vocab accuracy drops from 18.2% to 12.7% — the opposite of the intended effect
- The word-boosting API failure cause is undiagnosed; likely multi-token entity handling issue
- Not recommended for production; batch mode is strictly better on all accuracy metrics
