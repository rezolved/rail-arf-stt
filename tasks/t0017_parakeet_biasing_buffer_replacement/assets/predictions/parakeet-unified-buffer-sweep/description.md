---
spec_version: "2"
predictions_id: parakeet-unified-buffer-sweep
task: t0017_parakeet_biasing_buffer_replacement
date_created: "2026-07-02"
model: nvidia/parakeet-unified-en-0.6b
dataset: stt-benchmark-gold-92
instance_count: 558
---
## Metadata

- **Model:** nvidia/parakeet-unified-en-0.6b with GPU-PB TurboBias domain biasing
- **Task:** t0017_parakeet_biasing_buffer_replacement
- **Dataset:** stt-benchmark-gold-92 (93 clips, 558 total prediction records across 6 intervals)
- **Inference:** NeMo ASR streaming mode, GPU inference, Azure H100 NVL
- **Intervals tested:** 200, 300, 350, 500, 750, 1000ms buffer extraction intervals
- **Date:** 2026-07-02

## Overview

Per-clip predictions from `parakeet-unified-en-0.6b` (unified streaming decoder, 0.6B parameters)
across a fine streaming buffer extraction sweep (200–1000ms), head-to-head against the brainpowa
production model `parakeet-tdt-0.6b-v3` (see sibling asset `parakeet-tdt-buffer-sweep`). Mirrors the
t0015 harness with an extended interval grid.

GPU-PB TurboBias domain biasing is applied at every inference call using Rezolve's 31-term domain
vocabulary expanded to 72 casing variants (original, lowercase, per-word title-case), alpha=1.0.
This run supersedes an earlier pass that used a buggy casing-variant expansion
(`phrase[:1].upper() + phrase[1:]`, which only capitalized the first character of the whole phrase
instead of each word) — fixed to `phrase.title()` before this data was generated, so multi-word
domain terms ("Salesforce Commerce Cloud", "Adobe Commerce", etc.) now get a real title-case biasing
variant.

## Model

- **HuggingFace ID:** nvidia/parakeet-unified-en-0.6b
- **Architecture:** Unified streaming decoder, 0.6B params
- **Framework:** NVIDIA NeMo
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB TurboBias phrase boosting, 31-term Rezolve domain vocabulary expanded to
  72 casing variants, alpha=1.0
- **Streaming mode:** Buffer extraction at configurable intervals (200/300/350/500/750/1000ms
  tested)

Candidate replacement for the brainpowa production Parakeet checkpoint (`parakeet-tdt-0.6b-v3`).

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
| WER (gold-92) | 10.73% |
| Entity accuracy (gold-92) | 23.44% |
| EA-DV (domain vocab) | 34.78% |
| Latency p50 @1000ms | 0.353s |
| TTFD p50 | 0.037s |
| Empty transcripts | 0 / 93 |
| Hallucinations | 0 |

Winner vs `parakeet-tdt-0.6b-v3` on every metric (WER −4.42pp, EA-DV +1.45pp, 3→0 empty). See
`results/results_detailed.md` in the task folder for the full comparison and production
recommendation.

## Main Ideas

* **Best accuracy of the two Parakeet candidates.** Lower WER, higher EA-DV, and zero empty
  transcripts versus `parakeet-tdt-0.6b-v3` on identical clips and biasing config.
* **Buffer interval has no effect on accuracy.** Final transcript is identical at every tested
  interval; only compute latency and TTFD vary.
* **Still bounded by the Parakeet family's biasing ceiling.** EA-DV of 34.78% is the best of the two
  Parakeet models but far below Granite Speech 4.1 2B's 97.1% on the same vocabulary.

## Summary

`parakeet-unified-en-0.6b` was evaluated on gold-92 (93 clips) with GPU-PB TurboBias domain biasing
across six streaming buffer extraction intervals (200–1000ms). Accuracy (WER 10.73%, EA 23.44%,
EA-DV 34.78%) is identical across all intervals, with zero empty transcripts and no hallucinations.
Compared against the current brainpowa production model `parakeet-tdt-0.6b-v3` (sibling asset
`parakeet-tdt-buffer-sweep`), unified wins on every biased accuracy metric at a modest latency cost.
See `results/results_detailed.md` for the full comparison and production recommendation.
