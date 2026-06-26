---
spec_version: "1"
predictions_id: granite-speech-4.1-2b-gold92-biased
task: t0007_ibm_granite_4_1_benchmark
date_created: "2026-06-25"
model: ibm-granite/granite-speech-4.1-2b
dataset: stt-benchmark-gold-92
instance_count: 93
---
## Metadata

- **Model:** IBM Granite Speech 4.1 2B — keyword biased
- **Task:** t0007_ibm_granite_4_1_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU (bfloat16), HuggingFace Transformers 4.57.6, keyword biasing via chat prompt
- **Date:** 2026-06-25

## Overview

Per-clip predictions from IBM Granite Speech 4.1 2B with keyword biasing on the gold-92
benchmark. Keyword biasing is injected via the chat template prompt (`<|audio|>{prompt}`) with
Rezolve domain vocabulary terms. This is the primary production-candidate variant for this task.

## Model

- **HuggingFace ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** GraniteSpeechForConditionalGeneration + AutoProcessor
- **Params:** ~2B
- **Framework:** HuggingFace Transformers 4.57.6
- **Hardware:** GPU, bfloat16, ~4 GB VRAM
- **Biasing:** Keyword injection via chat template prompt

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
| WER (gold-92) | 8.8% |
| Entity accuracy (gold-92) | 40.2% |
| Entity accuracy (domain vocab) | 98.5% |
| Action-critical WER | 8.2% |
| Intent preservation | 92.5% |
| Latency p50 | 0.248s |

## Main Ideas

- Granite biased achieves 98.5% domain-vocabulary entity accuracy, matching Whisper (94.5%)
- 40.2% overall entity accuracy — +17 pp vs. batch, −5.8 pp vs. Whisper
- WER=8.8%, matching Whisper large-v3 (8.5%)
- Latency 248 ms p50 — 27× faster than Whisper (6.66s), within 800ms voice-to-action budget
- +73% better overall entity accuracy vs. Parakeet production (23.2%)
- Credible production replacement for Parakeet on accuracy; fine-tuning could close remaining gap vs. Whisper
