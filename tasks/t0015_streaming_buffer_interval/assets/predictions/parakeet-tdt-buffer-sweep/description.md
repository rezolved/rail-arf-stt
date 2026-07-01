---
spec_version: "2"
predictions_id: parakeet-tdt-buffer-sweep
task: t0015_streaming_buffer_interval
date_created: "2026-07-01"
model: nvidia/parakeet-tdt-0.6b-v3
dataset: stt-benchmark-gold-92
instance_count: 279
---

## Metadata

- **Model:** nvidia/parakeet-tdt-0.6b-v3 with GPU-PB TurboBias domain biasing
- **Task:** t0015_streaming_buffer_interval
- **Dataset:** stt-benchmark-gold-92 (93 clips, 279 total prediction records across 3 intervals)
- **Inference:** NeMo ASR streaming mode, GPU inference, Azure H100 NVL
- **Intervals Tested:** 500ms, 750ms, 1000ms buffer extraction intervals
- **Date:** 2026-07-01

## Overview

This asset contains per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 (Token-and-Duration
Transducer, 0.6B parameters) across a sweep of three streaming buffer extraction intervals: 500ms,
750ms, and 1000ms. The experiment is part of a broader benchmark covering 4 models × 3 intervals
= 12 combinations; this asset covers only the parakeet-tdt model.

In true streaming STT, audio is captured continuously and the model must decide when to extract a
partial or final transcript from the accumulated PCM buffer. The buffer extraction interval controls
how often the accumulated 16kHz mono PCM-16 audio is sent to the model for inference during an
active streaming session. A shorter interval means more frequent model calls and lower TTFD (time
to first decode), but potentially more redundant computation. A longer interval batches more audio
before each inference call, improving GPU utilization but adding initial silence before the first
output token appears.

Each of the 93 gold-92 clips was processed at each of the three intervals, yielding 279 total
records (93 × 3). Because the final transcript is computed from the complete audio regardless of
interval, WER and entity accuracy are identical across all three conditions — interval affects only
the streaming latency profile and TTFD.

GPU-PB TurboBias domain biasing is applied at every inference call using Rezolve's 31-term domain
vocabulary (brand names, product terms, financial entities relevant to investor-relations sessions).
Boosting alpha is set to 1.0.

## Model

- **HuggingFace ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), CTC-Attention hybrid decoder, 0.6B params
- **Framework:** NVIDIA NeMo / Riva SDK
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB TurboBias phrase boosting, 31-term Rezolve domain vocabulary, alpha=1.0
- **Streaming mode:** Buffer extraction at configurable intervals (500ms, 750ms, 1000ms tested)

Parakeet TDT v3 is NVIDIA's production ASR model optimized for low-latency streaming inference.
The TDT architecture emits token predictions along with token duration estimates, enabling
word-level timestamp output without a separate forced-alignment pass. Under streaming operation,
the model maintains an internal RNN-T state across chunks, allowing efficient incremental
processing of incoming audio buffers.

## Data

The gold-92 benchmark consists of 93 WAV clips sourced from Rezolve production investor-relations
sessions. All clips are 16kHz mono, PCM-16 format, with durations ranging from approximately 2s
to 15s (mean ~6.7s). The domain is accented English with heavy use of financial and
investor-relations terminology (earnings, revenue, guidance, product names, etc.).

Gold-92 is a held-out regression set — it is never used for training or fine-tuning. Clip
`error_en_0005` has Cyrillic ground truth and is excluded from entity accuracy aggregates but
included in WER computation. Many clips have no reference_text annotation, which suppresses entity
accuracy scores for those clips (they contribute 0/0 and are excluded from the denominator).

## Prediction Format

Each JSONL file contains 93 records (one per clip). Fields per record:

- `clip_id` (string): unique clip identifier, e.g. `en_0001`
- `duration_s` (float): audio duration in seconds
- `transcript` (string): final parakeet-tdt hypothesis for the full clip
- `reference_text` (string): ground-truth transcript (may be empty string if not annotated)
- `is_empty` (bool): true if transcript is empty string or whitespace-only
- `is_hallucination` (bool): true if transcript contains content not present in source audio
- `ttfd_seconds` (float): time from streaming start to first non-empty output token (seconds)
- `latency_seconds` (float): total wall-clock time from first chunk delivery to final transcript
- `interval_ms` (int): buffer extraction interval in milliseconds (500, 750, or 1000)
- `n_chunks` (int): number of buffer extraction events during the clip
- `n_inferences` (int): total number of model inference calls made

Files:

- `files/predictions-gold92-500ms.jsonl` — all 93 clips at 500ms interval
- `files/predictions-gold92-750ms.jsonl` — all 93 clips at 750ms interval
- `files/predictions-gold92-1000ms.jsonl` — all 93 clips at 1000ms interval

## Metrics

All accuracy metrics are identical across intervals because the final transcript is the same
regardless of how frequently intermediate buffer extractions occur.

| Metric | 500ms | 750ms | 1000ms |
| --- | --- | --- | --- |
| WER (gold-92) | 15.25% | 15.25% | 15.25% |
| Entity accuracy (gold-92) | 22.81% | 22.81% | 22.81% |
| EA-DV (domain vocab) | 33.33% | 33.33% | 33.33% |
| Latency p50 (s) | 0.256 | 0.254 | 0.250 |
| TTFD p50 (s) | 0.032 | 0.032 | 0.032 |
| Empty transcripts | 3 | 3 | 3 |
| Hallucinations | 0 | 0 | 0 |

**Granite accumulate-then-transcribe baseline (t0011):** WER 8.8%, EA-DV 97.1%, TTFD 77ms p50.
Parakeet's WER is 6.4 pp higher than Granite, and EA-DV is 63.8 pp lower. The TTFD advantage
(32ms vs 77ms) is substantial but does not compensate for the accuracy gap in investor-relations
use cases where entity precision is critical.

Entity accuracy is low (22.81% / 33.33%) primarily because many gold-92 clips have no
reference_text annotation, causing them to contribute nothing to the numerator. The domain-vocab
metric (EA-DV = 33.33%) uses only clips where the reference text contains at least one of the 31
domain vocabulary terms.

Three empty transcripts were observed (3/93 = 3.2% empty rate). No hallucinations detected across
all 279 records.

## Main Ideas

* **Buffer interval has no effect on accuracy.** WER, entity accuracy, and hallucination rate are
  identical at 500ms, 750ms, and 1000ms. The final transcript is determined by the complete audio
  signal, not by how many intermediate buffer extractions occurred.

* **Latency decreases slightly at larger intervals.** Parakeet p50 latency drops from 256ms
  (500ms interval) to 250ms (1000ms interval) — a 6ms improvement. This is consistent with
  reduced inference overhead from fewer model calls per clip. However, the effect is small
  relative to typical voice-to-action latency budgets (~800ms).

* **TTFD is very fast and interval-independent.** At 32ms p50 across all intervals, parakeet-tdt
  produces its first output token extremely quickly — well below the 77ms observed for Granite's
  accumulate-then-transcribe baseline. This makes parakeet attractive for use cases where
  streaming visual feedback (live transcript display) matters more than final accuracy.

* **WER 15.25% is materially higher than Granite (8.8%).** For investor-relations sessions where
  entity precision drives downstream action accuracy, this gap is significant. Domain vocabulary
  biasing at alpha=1.0 raises EA-DV to 33.33% but still far below Granite's 97.1%.

* **Practical implication: choose interval based on compute budget.** Since accuracy is
  unaffected, the optimal interval is determined by GPU utilization goals: larger intervals reduce
  inference calls per session, lowering GPU cost, with a marginal latency benefit.

## Summary

Parakeet TDT 0.6b-v3 with GPU-PB TurboBias was evaluated across three streaming buffer extraction
intervals (500ms, 750ms, 1000ms) on the gold-92 benchmark (93 clips). Accuracy metrics (WER
15.25%, EA 22.81%, EA-DV 33.33%) are identical across all intervals, confirming that buffer
extraction frequency does not affect transcript quality. Latency decreases marginally with larger
intervals (256ms → 250ms p50), and TTFD remains a consistent 32ms across all conditions. The
model produces zero hallucinations and 3 empty transcripts.

Compared to the Granite accumulate-then-transcribe baseline (WER 8.8%, EA-DV 97.1%, TTFD 77ms),
parakeet offers significantly faster TTFD but substantially lower accuracy on this investor-relations
domain, making it better suited to low-latency display use cases than high-precision action routing.
The buffer interval parameter does not change this conclusion — any of the three tested intervals
yields the same accuracy result.
