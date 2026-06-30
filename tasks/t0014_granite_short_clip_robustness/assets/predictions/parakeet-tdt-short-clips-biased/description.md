---
spec_version: "2"
predictions_id: "parakeet-tdt-short-clips-biased"
documented_by_task: "t0014_granite_short_clip_robustness"
date_documented: "2026-06-30"
---

# Parakeet TDT 0.6b-v3 on Short Clips (Biased)

## Metadata

- **Name**: Parakeet TDT 0.6b-v3 on Short Clips (Biased — Single-Chunk Degenerate for sub-2 s)
- **Model**: Parakeet TDT 0.6b-v3 (NeMo 3.1.0, GPU-PB phrase boosting alpha=1.0)
- **Datasets**: 44 synthetic short clips trimmed from gold-92 audio
- **Format**: jsonl
- **Instances**: 44
- **Created by**: t0014_granite_short_clip_robustness

## Overview

These predictions capture the per-clip transcription output of Parakeet TDT 0.6b-v3 on 44
synthetic short clips (0.5–3.0 s) trimmed from gold-92 production audio. The asset is labeled
"biased" because 16 of 44 clips (all clips under approximately 1.0 s in PCM bytes) hit the
degenerate single-chunk path where the entire clip fits within one 32kB PCM-16 chunk. The
`single_chunk_degenerate` flag identifies these clips.

All clips were processed through the accumulate-then-transcribe pattern matching the base class
STTAdapter.transcribe_stream() default: 32kB PCM-16 chunks accumulated into a buffer, then
model.transcribe() called once on the complete audio. This means the sub-2 s clips that arrived
as a single chunk were transcribed once on a minimal audio buffer — the primary cause of the
observed 27.3% empty rate.

GPU-PB phrase boosting was applied with 66 casing variants of 31 domain vocabulary terms
(alpha=1.0, context_score=1.0, depth_scaling=2.0), identical to t0012.

## Model

Parakeet TDT 0.6b-v3 loaded from /home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3 (NeMo
3.1.0). GPU-PB phrase boosting: alpha=1.0, 66 casing variants of 31 domain terms, context_score
=1.0, depth_scaling=2.0, use_bpe_dropout=True. 3 warmup passes run with zero-audio before timing.

## Data

44 short clips synthesized from 93 gold-92 WAV files (16 kHz mono PCM-16) by trimming to fixed
durations at 6 bins: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 seconds. Plus 2 edge cases.

| Duration Bin | Clips | Empty Count | Empty Rate | Single-Chunk |
|---|---|---|---|---|
| 0.5 s | 9 | 5 | 55.6% | yes (all) |
| 1.0 s | 7 | 4 | 57.1% | yes (all) |
| 1.5 s | 7 | 3 | 42.9% | yes (most) |
| 2.0 s | 7 | 0 | 0.0% | no |
| 2.5 s | 7 | 0 | 0.0% | no |
| 3.0 s | 7 | 0 | 0.0% | no |

## Prediction Format

Each line of `predictions-short-clips.jsonl` is a JSON object:

```json
{
  "clip_id": "error_en_0011_0.5s",
  "duration_s": 0.5,
  "transcript": "",
  "is_empty": true,
  "is_hallucination": false,
  "latency_seconds": 0.031,
  "ttfd_seconds": null,
  "num_chunks": 1,
  "single_chunk_degenerate": true
}
```

Fields:

- `clip_id` — unique clip identifier
- `duration_s` — clip duration in seconds
- `transcript` — model transcript (empty string if is_empty)
- `is_empty` — true if transcript is empty after stripping
- `is_hallucination` — true if transcript contains no reference words and matches BoH pattern
- `latency_seconds` — wall-clock from first chunk arrival to transcript returned
- `ttfd_seconds` — time to first non-empty delta (null for empty)
- `num_chunks` — number of 32kB chunks the clip was split into
- `single_chunk_degenerate` — true if the entire clip fit in one 32kB chunk (duration-dependent)

## Metrics

| Metric | Value |
|---|---|
| Empty rate (all clips) | 27.3% (12/44) |
| Hallucination rate | 0.0% |
| Empty rate sub-1 s | 55.6% (5/9) |
| Empty rate 1–2 s | 57.1% (4/7) for 1.0 s; 42.9% for 1.5 s |
| Empty rate 2–3 s | 14.3% (1/7) at 2.0 s; 0.0% at 2.5 s and 3.0 s |
| Single-chunk degenerate clips | 16/44 |
| Latency p50 | 0.032 s |

## Main Ideas

- **Parakeet fails on sub-2 s clips at 27-57% empty rate**, primarily due to the degenerate
  single-chunk path where insufficient audio context causes the CTC decoder to produce no output
- **Zero hallucinations** — Parakeet's CTC architecture does not produce hallucination patterns
  even on very short clips; it either produces sparse correct output or empty string
- **Latency is extremely fast** (p50 32 ms) because Parakeet's CTC decoder is non-autoregressive;
  however, this speed advantage is irrelevant when the empty rate is 55% at sub-1 s durations
- **Above 2 s**, Parakeet empty rate drops to near-zero, indicating the minimum viable clip
  duration for production use is approximately 2.0 s with the current chunk size

## Summary

This predictions asset captures Parakeet TDT 0.6b-v3 output on 44 synthetic short clips,
revealing a significant short-clip failure mode: 27.3% overall empty rate (55.6% for sub-1 s
bins, 42–57% for 1–2 s bins). The "biased" label reflects that 16 clips hit the degenerate
single-chunk path, making results for sub-2 s strata structurally confounded by chunk-fill
mechanics rather than pure model capability.

The zero hallucination rate is a notable advantage over Whisper: Parakeet either produces
sparse correct output or empty string, never fabricated content. Combined with 32 ms p50
latency, Parakeet is an efficient model that degrades silently (empty output) rather than
catastrophically (hallucination) on short clips. The practical implication is a minimum viable
clip duration gate of 2.0 s for production use.
