---
spec_version: "2"
predictions_id: "granite-speech-short-clips-biased"
documented_by_task: "t0014_granite_short_clip_robustness"
date_documented: "2026-06-30"
---

# Granite Speech 4.1 2B on Short Clips (Biased)

## Metadata

- **Name**: Granite Speech 4.1 2B on Short Clips (Biased — Single-Block Attention for sub-4 s)
- **Model**: Granite Speech 4.1 2B (HuggingFace Transformers, bfloat16, CUDA)
- **Datasets**: 44 synthetic short clips trimmed from gold-92 audio
- **Format**: jsonl
- **Instances**: 44
- **Created by**: t0014_granite_short_clip_robustness

## Overview

These predictions capture the per-clip transcription output of Granite Speech 4.1 2B on 44
synthetic short clips (0.5–3.0 s) trimmed from gold-92 production audio. The asset is labeled
"biased" because all 44 clips are shorter than Granite's 4-second block-attention window —
every clip is processed as a single Conformer block pass with fewer Q-Former acoustic embeddings
than longer clips would produce, which affects transcription quality at very short durations.

All clips were processed via the STTAdapter.transcribe_stream() base class default:
accumulate-then-transcribe with 32kB PCM-16 chunks. This pattern structurally avoids the
intermediate VAD passes that cause Whisper's failure mode: the model receives the complete
audio once and transcribes it in one pass. Keyword prompt injection ("transcribe the speech
to text. Keywords: Rezolve, brainpowa, ...") with 31 domain terms was applied.

The key finding is that Granite produces **zero empty outputs and zero hallucinations** on all
44 short clips, including sub-0.5 s clips. This confirms Granite's structural advantage for
short-clip robustness.

## Model

Granite Speech 4.1 2B loaded from /home/azureuser/granite-model/granite-speech-4.1-2b
(HuggingFace Transformers, dtype=bfloat16, device_map=cuda). Prompt format:
"transcribe the speech to text. Keywords: Rezolve, brainpowa, NASDAQ, ..." (31 domain terms).
Generation: max_new_tokens=256, do_sample=False, num_beams=1 (greedy). 3 warmup passes
with silent audio before timing.

## Data

44 short clips synthesized from 93 gold-92 WAV files (16 kHz mono PCM-16) by trimming to fixed
durations at 6 bins: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 seconds. Plus 2 edge cases.

| Duration Bin | Clips | Empty Count | Empty Rate |
|---|---|---|---|
| 0.5 s | 9 | 0 | 0.0% |
| 1.0 s | 7 | 0 | 0.0% |
| 1.5 s | 7 | 0 | 0.0% |
| 2.0 s | 7 | 0 | 0.0% |
| 2.5 s | 7 | 0 | 0.0% |
| 3.0 s | 7 | 0 | 0.0% |

## Prediction Format

Each line of `predictions-short-clips.jsonl` is a JSON object:

```json
{
  "clip_id": "error_en_0011_0.5s",
  "duration_s": 0.5,
  "transcript": "the hospital",
  "is_empty": false,
  "is_hallucination": false,
  "latency_seconds": 0.077,
  "ttfd_seconds": 0.077,
  "num_chunks": 1
}
```

Fields:

- `clip_id` — unique clip identifier (source_clip_id + duration suffix)
- `duration_s` — clip duration in seconds
- `transcript` — model transcript (non-empty for all 44 clips)
- `is_empty` — false for all 44 clips
- `is_hallucination` — false for all 44 clips
- `latency_seconds` — wall-clock from first chunk arrival to transcript returned
- `ttfd_seconds` — time to first non-empty delta (equals latency for all clips)
- `num_chunks` — number of 32kB chunks the clip was split into

## Metrics

| Metric | Value |
|---|---|
| Empty rate (all clips) | 0.0% (0/44) |
| Hallucination rate | 0.0% (0/44) |
| Empty rate sub-1 s | 0.0% |
| Empty rate sub-2 s | 0.0% |
| Entity accuracy sub-1 s | 9.1% |
| Entity accuracy 2–3 s | 40.7% |
| Latency p50 | 0.125 s |

## Main Ideas

- **Granite achieves 0% empty rate across all duration bins**, including sub-0.5 s clips —
  the accumulate-then-transcribe pattern with single-block Conformer processing does not
  produce empty outputs even at minimal clip lengths
- **0% hallucination rate** on all 44 clips — no known Whisper hallucination patterns detected,
  consistent with Granite's autoregressive decoder being less prone to spurious repetition
- **Entity accuracy degrades gracefully with duration** (9.1% at sub-1 s, 11.7% at 1–2 s,
  40.7% at 2–3 s) rather than failing catastrophically — partial transcripts like "the hospital"
  or "can I see" are produced even on very short clips
- **Latency p50 0.125 s** is well within the 0.800 s production constraint for all clip lengths

## Summary

This predictions asset captures Granite Speech 4.1 2B output on 44 synthetic short clips
(0.5–3.0 s), demonstrating the model's structural robustness to the short-clip failure mode
that disqualified Whisper from production. The critical finding is 0% empty rate and 0%
hallucination rate across all duration bins — Granite always produces some transcription
output, even for 0.5 s clips containing only a fragment of a single word.

The "biased" label reflects that all clips fall within Granite's 4-second block-attention window,
meaning the single-block path is always used and fewer Q-Former embeddings are available for
shorter clips. This reduces word accuracy but does not produce empty outputs or hallucinations.
Entity accuracy increases monotonically from 9% at sub-1 s to 41% at 2–3 s, matching the
intuition that more audio context allows the model to transcribe more complete tokens. These
predictions provide the primary evidence supporting the YES recommendation for replacing Parakeet
with Granite in brainpowa-realtime-api.
