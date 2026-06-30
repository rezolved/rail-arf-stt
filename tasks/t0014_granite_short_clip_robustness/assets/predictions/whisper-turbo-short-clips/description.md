---
spec_version: "2"
predictions_id: "whisper-turbo-short-clips"
documented_by_task: "t0014_granite_short_clip_robustness"
date_documented: "2026-06-30"
---

# Whisper turbo on Short Clips (0.5–3 s)

## Metadata

- **Name**: Whisper turbo on Short Clips (0.5–3 s)
- **Model**: Whisper large-v3-turbo (HuggingFace Transformers, float16, CUDA)
- **Datasets**: 44 synthetic short clips trimmed from gold-92 audio
- **Format**: jsonl
- **Instances**: 44
- **Created by**: t0014_granite_short_clip_robustness

## Overview

These predictions capture the per-clip transcription output of Whisper large-v3-turbo on 44
synthetic short clips (0.5–3.0 s) trimmed from gold-92 production audio. The experiment was
designed to characterize Whisper's short-clip failure modes — specifically empty output and
hallucination rates — that disqualified it from production use in brainpowa-realtime-api.

The inference uses HuggingFace Transformers (not faster-whisper) because faster-whisper has a
confirmed multi-GPU bug on the Azure H100 NVL host (documented in t0012). This means the
VAD filter behavior may differ from the production brainpowa configuration, which uses
faster-whisper. The no_speech_probability field is a proxy (0.0 for non-empty, 1.0 for empty)
because HuggingFace Whisper does not expose per-segment no_speech_prob directly.

All clips were processed through the accumulate-then-transcribe pattern matching
STTAdapter.transcribe_stream() base class default: 32kB PCM-16 chunks accumulated, then
transcribed once on the complete buffer. Domain vocabulary prompt injection (31 Rezolve terms)
was applied identical to t0012.

## Model

Whisper large-v3-turbo (openai/whisper-large-v3-turbo) loaded via HuggingFace Transformers.
Configuration: dtype=float16, CUDA device cuda:0, beam_size=1, max_new_tokens=200. Initial
prompt: comma-separated 31 domain vocabulary terms (Rezolve, brainpowa, NASDAQ, Shopify Plus,
etc.). Forced language=English, task=transcribe.

## Data

44 short clips synthesized from 93 gold-92 WAV files (16 kHz mono PCM-16) by trimming to fixed
durations at 6 bins: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 seconds. Plus 2 edge cases (synthetic 0.5 s
silence and 0.5 s background noise). 7 clips per bin selected for variety (speech-rich, noise-heavy,
neutral). Minimum source clip duration is 3.07 s.

| Duration Bin | Clips |
|---|---|
| 0.5 s | 9 (includes 2 edge cases) |
| 1.0 s | 7 |
| 1.5 s | 7 |
| 2.0 s | 7 |
| 2.5 s | 7 |
| 3.0 s | 7 |
| **Total** | **44** |

## Prediction Format

Each line of `predictions-short-clips.jsonl` is a JSON object:

```json
{
  "clip_id": "error_en_0011_0.5s",
  "duration_s": 0.5,
  "transcript": "hospitality.",
  "is_empty": false,
  "is_hallucination": false,
  "no_speech_probability": 0.0,
  "latency_seconds": 0.138,
  "ttfd_seconds": 0.138,
  "num_chunks": 1
}
```

Fields:

- `clip_id` — unique clip identifier (source_clip_id + duration suffix)
- `duration_s` — clip duration in seconds
- `transcript` — model transcript (empty string if is_empty)
- `is_empty` — true if transcript is empty after stripping
- `is_hallucination` — true if transcript contains no reference words and matches BoH pattern
- `no_speech_probability` — proxy: 0.0 for non-empty transcripts, 1.0 for empty (HuggingFace Whisper
  does not expose this directly; faster-whisper would give exact values)
- `latency_seconds` — wall-clock from first chunk arrival to transcript returned
- `ttfd_seconds` — time to first non-empty delta (equals latency for non-empty; null for empty)
- `num_chunks` — number of 32kB chunks the clip was split into (1 for all short clips ≤ 2s)

## Metrics

| Metric | Value |
|---|---|
| Empty rate (all clips) | 0.0% |
| Hallucination rate | 0.0% |
| Empty rate sub-2 s | 0.0% |
| Latency p50 | 0.146 s |

Notable finding: HuggingFace Whisper produces 0% empty rate on sub-2 s clips. This contrasts
with the production brainpowa configuration using faster-whisper with VAD filter, which would be
expected to produce higher empty rates on very short clips. The HuggingFace generate() path does
not apply faster-whisper's VAD-based segment suppression.

## Main Ideas

- Whisper via HuggingFace Transformers shows **0% empty rate** on clips as short as 0.5 s,
  which is lower than expected from the VAD misfiring hypothesis — this is a backend difference
  (HuggingFace vs faster-whisper) that must be interpreted carefully
- **0% hallucination rate** on all 44 short clips using BoH top-30 pattern matching
- Entity accuracy drops steeply for sub-1 s clips (EA 4.2%) and recovers at 2–3 s (38.3%),
  consistent with insufficient audio context for meaningful transcription at very short durations
- Latency p50 is 0.146 s for all clip lengths — dominated by model fixed overhead,
  well within the 0.800 s production constraint

## Summary

This predictions asset captures Whisper large-v3-turbo output on 44 synthetic short clips
(0.5–3.0 s) designed to stress-test the short-clip failure mode that disqualified Whisper from
brainpowa production. The key finding is that HuggingFace Transformers Whisper produces 0%
empty and 0% hallucination rates on these clips, which differs from the expected behavior of the
faster-whisper production backend (which applies VAD suppression via no_speech_threshold).

The entity accuracy results confirm the expected degradation: 4.2% at sub-1 s bins rising to
38.3% at 2–3 s, consistent with insufficient audio context. These predictions serve as the
Whisper baseline in the stratified analysis comparing all three models across 6 duration strata.
The no_speech_probability field is a proxy (0.0/1.0) due to HuggingFace API limitations.
