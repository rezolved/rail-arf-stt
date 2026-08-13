---
spec_version: "2"
predictions_id: parakeet-tdt-buffer-sweep
task: t0017_parakeet_biasing_buffer_replacement
date_created: "2026-07-02"
model: nvidia/parakeet-tdt-0.6b-v3
dataset: stt-benchmark-gold-92
instance_count: 558
---
## Metadata

- **Model:** nvidia/parakeet-tdt-0.6b-v3 (brainpowa production model) with GPU-PB TurboBias domain
  biasing
- **Task:** t0017_parakeet_biasing_buffer_replacement
- **Dataset:** stt-benchmark-gold-92 (93 clips, 558 total prediction records across 6 intervals)
- **Inference:** NeMo ASR streaming mode, GPU inference, Azure H100 NVL
- **Intervals tested:** 200, 300, 350, 500, 750, 1000ms buffer extraction intervals
- **Date:** 2026-07-02

## Overview

Per-clip predictions from `parakeet-tdt-0.6b-v3` (Token-and-Duration Transducer, 0.6B parameters)
across a fine streaming buffer extraction sweep (200–1000ms), head-to-head against
`parakeet-unified-en-0.6b` (see sibling asset `parakeet-unified-buffer-sweep`). Mirrors the t0015
harness with an extended interval grid.

GPU-PB TurboBias domain biasing is applied at every inference call using Rezolve's 31-term domain
vocabulary expanded to 72 casing variants (original, lowercase, per-word title-case), alpha=1.0.
This run supersedes an earlier pass that used a buggy casing-variant expansion
(`phrase[:1].upper() + phrase[1:]`, which only capitalized the first character of the whole phrase
instead of each word) — fixed to `phrase.title()` before this data was generated, so multi-word
domain terms ("Salesforce Commerce Cloud", "Adobe Commerce", etc.) now get a real title-case biasing
variant.

## Model

- **HuggingFace ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NVIDIA NeMo
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB TurboBias phrase boosting, 31-term Rezolve domain vocabulary expanded to
  72 casing variants, alpha=1.0
- **Streaming mode:** Buffer extraction at configurable intervals (200/300/350/500/750/1000ms
  tested)

This is the current brainpowa production Parakeet checkpoint. TDT emits token predictions with
duration estimates, enabling incremental streaming decoding without a separate alignment pass.

## Data

The gold-92 benchmark consists of 93 WAV clips sourced from Rezolve production investor-relations
sessions, 16kHz mono PCM-16, durations ~2–15s. Domain is accented English with financial and
investor-relations terminology. Gold-92 is a held-out regression set — never used for training or
tuning.

## Prediction Format

Each JSONL file contains 93 records (one per clip). Fields: `clip_id`, `duration_s`, `transcript`,
`reference_text`, `is_empty`, `is_hallucination`, `ttfd_seconds`, `latency_seconds`, `interval_ms`,
`n_chunks`, `n_inferences`.

Files: `files/predictions-gold92-{200,300,350,500,750,1000}ms.jsonl`.

## Metrics

Accuracy is invariant to interval (final transcript is identical regardless of buffer size).

| Metric | Value (all intervals) |
| --- | --- |
| WER (gold-92) | 15.15% |
| Entity accuracy (gold-92) | 23.44% |
| EA-DV (domain vocab) | 33.33% |
| Latency p50 @1000ms | 0.253s |
| TTFD p50 | 0.033s |
| Empty transcripts | 3 / 93 |
| Hallucinations | 0 |

See `results/results_detailed.md` in the task folder for the full head-to-head against
`parakeet-unified-en-0.6b` and the production recommendation.

## Main Ideas

* **Buffer interval has no effect on accuracy.** WER, entity accuracy, and hallucination rate are
  identical at every tested interval — the final transcript depends on the complete audio signal,
  not on how many intermediate buffer extractions occurred.
* **Reliability gap vs unified.** 3 of 93 clips return an empty transcript, versus 0 for
  `parakeet-unified-en-0.6b` on the same clips — this is the same failure mode that disqualified
  Whisper from production.
* **Biasing ceiling is low.** Even with GPU-PB TurboBias correctly configured (72 phrase variants,
  confirmed built on this model), EA-DV tops out at 33.33% — the flagship term "Rezolve" is
  consistently mis-transcribed.

## Summary

`parakeet-tdt-0.6b-v3`, the current brainpowa production model, was evaluated on gold-92 (93 clips)
with GPU-PB TurboBias domain biasing across six streaming buffer extraction intervals (200–1000ms).
Accuracy (WER 15.15%, EA 23.44%, EA-DV 33.33%) is identical across all intervals; 3 of 93 clips
produce empty transcripts. Compared against `parakeet-unified-en-0.6b` (sibling asset
`parakeet-unified-buffer-sweep`), tdt is strictly worse on every biased accuracy metric while being
slightly faster on compute latency. See `results/results_detailed.md` for the full comparison and
production recommendation.
