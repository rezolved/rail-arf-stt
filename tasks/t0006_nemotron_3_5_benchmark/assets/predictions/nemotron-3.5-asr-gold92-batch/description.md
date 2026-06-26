---
spec_version: "1"
predictions_id: nemotron-3.5-asr-gold92-batch
task: t0006_nemotron_3_5_benchmark
date_created: "2026-06-25"
model: nvidia/nemotron-asr-en-fastconformer-ctc-large
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** NVIDIA Nemotron 3.5 ASR (batch, no biasing)
- **Task:** t0006_nemotron_3_5_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva NIM, batch mode, no word boosting
- **Date:** 2026-06-25

## Overview

Per-clip predictions from NVIDIA Nemotron 3.5 ASR in batch (offline) mode on the gold-92
benchmark. No word boosting or domain biasing applied. This variant establishes the Nemotron
baseline without any vocabulary injection.

## Model

- **Architecture:** FastConformer-CTC, streaming-native
- **Framework:** NVIDIA NeMo / Riva NIM
- **Biasing:** None

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

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 17.6% |
| Entity accuracy (gold-92) | 24.7% |
| Entity accuracy (domain vocab) | 18.2% |
| Action-critical WER | 31.6% |
| Intent preservation | 90.3% |
| Latency p50 | 0.719s |

## Main Ideas

- Nemotron 3.5 batch WER=17.6%, 2× worse than Whisper large-v3 (8.5%)
- Entity accuracy 24.7%, 21 pp below Whisper (46.0%)
- Domain-vocab accuracy 18.2%, 76 pp below Whisper (94.5%)
- Latency 0.72s within 800 ms budget but not competitive with Granite biased (248 ms)
- Word boosting (see word-boosted variant) degrades all accuracy metrics vs. this baseline
