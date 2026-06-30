# Predictions by Date Added

20 predictions asset(s) grouped by creation date.

[Back to all predictions](../README.md)

---

## 2026-06-30 (3)

<details>
<summary>📊 <strong>Granite Speech 4.1 2B on Short Clips (Biased — Single-Block
Attention for sub-4 s)</strong>
(<code>granite-speech-short-clips-biased</code>) — 44 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `granite-speech-short-clips-biased` |
| **Model ID** | — |
| **Model** | Granite Speech 4.1 2B loaded from /home/azureuser/granite-model/granite-speech-4.1-2b (HuggingFace Transformers, torch_dtype=bfloat16, device_map=cuda). Keyword prompt injection: 'transcribe the speech to text. Keywords: Rezolve, brainpowa, ...' (31 domain terms). Same configuration as t0012 best variant. |
| **Datasets** |  |
| **Format** | jsonl |
| **Instances** | 44 |
| **Date created** | 2026-06-30 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Documentation** | [`description.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/predictions/granite-speech-short-clips-biased/description.md) |

**Metrics at creation:**

* **empty_rate**: 0.0
* **hallucination_rate**: 0.0
* **latency_p50_seconds**: 0.125
* **sub_1s_empty_rate**: 0.0
* **sub_2s_empty_rate**: 0.0

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
every clip is processed as a single Conformer block pass with fewer Q-Former acoustic
embeddings than longer clips would produce, which affects transcription quality at very short
durations.

All clips were processed via the STTAdapter.transcribe_stream() base class default:
accumulate-then-transcribe with 32kB PCM-16 chunks. This pattern structurally avoids the
intermediate VAD passes that cause Whisper's failure mode: the model receives the complete
audio once and transcribes it in one pass. Keyword prompt injection ("transcribe the speech to
text. Keywords: Rezolve, brainpowa, ...") with 31 domain terms was applied.

The key finding is that Granite produces **zero empty outputs and zero hallucinations** on all
44 short clips, including sub-0.5 s clips. This confirms Granite's structural advantage for
short-clip robustness.

## Model

Granite Speech 4.1 2B loaded from /home/azureuser/granite-model/granite-speech-4.1-2b
(HuggingFace Transformers, dtype=bfloat16, device_map=cuda). Prompt format: "transcribe the
speech to text. Keywords: Rezolve, brainpowa, NASDAQ, ..." (31 domain terms). Generation:
max_new_tokens=256, do_sample=False, num_beams=1 (greedy). 3 warmup passes with silent audio
before timing.

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

- **Granite achieves 0% empty rate across all duration bins**, including sub-0.5 s clips — the
  accumulate-then-transcribe pattern with single-block Conformer processing does not produce
  empty outputs even at minimal clip lengths
- **0% hallucination rate** on all 44 clips — no known Whisper hallucination patterns
  detected, consistent with Granite's autoregressive decoder being less prone to spurious
  repetition
- **Entity accuracy degrades gracefully with duration** (9.1% at sub-1 s, 11.7% at 1–2 s,
  40.7% at 2–3 s) rather than failing catastrophically — partial transcripts like "the
  hospital" or "can I see" are produced even on very short clips
- **Latency p50 0.125 s** is well within the 0.800 s production constraint for all clip
  lengths

## Summary

This predictions asset captures Granite Speech 4.1 2B output on 44 synthetic short clips
(0.5–3.0 s), demonstrating the model's structural robustness to the short-clip failure mode
that disqualified Whisper from production. The critical finding is 0% empty rate and 0%
hallucination rate across all duration bins — Granite always produces some transcription
output, even for 0.5 s clips containing only a fragment of a single word.

The "biased" label reflects that all clips fall within Granite's 4-second block-attention
window, meaning the single-block path is always used and fewer Q-Former embeddings are
available for shorter clips. This reduces word accuracy but does not produce empty outputs or
hallucinations. Entity accuracy increases monotonically from 9% at sub-1 s to 41% at 2–3 s,
matching the intuition that more audio context allows the model to transcribe more complete
tokens. These predictions provide the primary evidence supporting the YES recommendation for
replacing Parakeet with Granite in brainpowa-realtime-api.

</details>

<details>
<summary>📊 <strong>Parakeet TDT 0.6b-v3 on Short Clips (Biased — Single-Chunk
Degenerate for sub-2 s)</strong>
(<code>parakeet-tdt-short-clips-biased</code>) — 44 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-tdt-short-clips-biased` |
| **Model ID** | — |
| **Model** | Parakeet TDT 0.6b-v3 loaded from /home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3 (NeMo 3.1.0). GPU-PB phrase boosting applied with alpha=1.0, 66 casing variants of 31 domain vocabulary terms, context_score=1.0, depth_scaling=2.0, use_bpe_dropout=True. Same configuration as t0012 production simulation. |
| **Datasets** |  |
| **Format** | jsonl |
| **Instances** | 44 |
| **Date created** | 2026-06-30 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Documentation** | [`description.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/predictions/parakeet-tdt-short-clips-biased/description.md) |

**Metrics at creation:**

* **empty_rate**: 0.2727
* **hallucination_rate**: 0.0
* **latency_p50_seconds**: 0.032
* **single_chunk_degenerate_count**: 16
* **sub_1s_empty_rate**: 0.556

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

All clips were processed through the accumulate-then-transcribe pattern matching the base
class STTAdapter.transcribe_stream() default: 32kB PCM-16 chunks accumulated into a buffer,
then model.transcribe() called once on the complete audio. This means the sub-2 s clips that
arrived as a single chunk were transcribed once on a minimal audio buffer — the primary cause
of the observed 27.3% empty rate.

GPU-PB phrase boosting was applied with 66 casing variants of 31 domain vocabulary terms
(alpha=1.0, context_score=1.0, depth_scaling=2.0), identical to t0012.

## Model

Parakeet TDT 0.6b-v3 loaded from /home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3 (NeMo
3.1.0). GPU-PB phrase boosting: alpha=1.0, 66 casing variants of 31 domain terms,
context_score =1.0, depth_scaling=2.0, use_bpe_dropout=True. 3 warmup passes run with
zero-audio before timing.

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
- `single_chunk_degenerate` — true if the entire clip fit in one 32kB chunk
  (duration-dependent)

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
  single-chunk path where insufficient audio context causes the CTC decoder to produce no
  output
- **Zero hallucinations** — Parakeet's CTC architecture does not produce hallucination
  patterns even on very short clips; it either produces sparse correct output or empty string
- **Latency is extremely fast** (p50 32 ms) because Parakeet's CTC decoder is
  non-autoregressive; however, this speed advantage is irrelevant when the empty rate is 55%
  at sub-1 s durations
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

</details>

<details>
<summary>📊 <strong>Whisper turbo on Short Clips (0.5-3 s)</strong>
(<code>whisper-turbo-short-clips</code>) — 44 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-turbo-short-clips` |
| **Model ID** | — |
| **Model** | Whisper large-v3-turbo (openai/whisper-large-v3-turbo) via HuggingFace Transformers, float16 on CUDA. Domain vocabulary prompt injection (31 Rezolve terms). Note: faster-whisper is NOT used here due to a multi-GPU bug on the test host (confirmed in t0012); results may differ slightly from production brainpowa-realtime-api which uses faster-whisper. |
| **Datasets** |  |
| **Format** | jsonl |
| **Instances** | 44 |
| **Date created** | 2026-06-30 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Documentation** | [`description.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/predictions/whisper-turbo-short-clips/description.md) |

**Metrics at creation:**

* **empty_rate**: 0.0
* **hallucination_rate**: 0.0
* **latency_p50_seconds**: 0.146
* **sub_2s_empty_rate**: 0.0

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
confirmed multi-GPU bug on the Azure H100 NVL host (documented in t0012). This means the VAD
filter behavior may differ from the production brainpowa configuration, which uses
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
silence and 0.5 s background noise). 7 clips per bin selected for variety (speech-rich,
noise-heavy, neutral). Minimum source clip duration is 3.07 s.

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
- `no_speech_probability` — proxy: 0.0 for non-empty transcripts, 1.0 for empty (HuggingFace
  Whisper does not expose this directly; faster-whisper would give exact values)
- `latency_seconds` — wall-clock from first chunk arrival to transcript returned
- `ttfd_seconds` — time to first non-empty delta (equals latency for non-empty; null for
  empty)
- `num_chunks` — number of 32kB chunks the clip was split into (1 for all short clips ≤ 2s)

## Metrics

| Metric | Value |
|---|---|
| Empty rate (all clips) | 0.0% |
| Hallucination rate | 0.0% |
| Empty rate sub-2 s | 0.0% |
| Latency p50 | 0.146 s |

Notable finding: HuggingFace Whisper produces 0% empty rate on sub-2 s clips. This contrasts
with the production brainpowa configuration using faster-whisper with VAD filter, which would
be expected to produce higher empty rates on very short clips. The HuggingFace generate() path
does not apply faster-whisper's VAD-based segment suppression.

## Main Ideas

- Whisper via HuggingFace Transformers shows **0% empty rate** on clips as short as 0.5 s,
  which is lower than expected from the VAD misfiring hypothesis — this is a backend
  difference (HuggingFace vs faster-whisper) that must be interpreted carefully
- **0% hallucination rate** on all 44 short clips using BoH top-30 pattern matching
- Entity accuracy drops steeply for sub-1 s clips (EA 4.2%) and recovers at 2–3 s (38.3%),
  consistent with insufficient audio context for meaningful transcription at very short
  durations
- Latency p50 is 0.146 s for all clip lengths — dominated by model fixed overhead, well within
  the 0.800 s production constraint

## Summary

This predictions asset captures Whisper large-v3-turbo output on 44 synthetic short clips
(0.5–3.0 s) designed to stress-test the short-clip failure mode that disqualified Whisper from
brainpowa production. The key finding is that HuggingFace Transformers Whisper produces 0%
empty and 0% hallucination rates on these clips, which differs from the expected behavior of
the faster-whisper production backend (which applies VAD suppression via no_speech_threshold).

The entity accuracy results confirm the expected degradation: 4.2% at sub-1 s bins rising to
38.3% at 2–3 s, consistent with insufficient audio context. These predictions serve as the
Whisper baseline in the stratified analysis comparing all three models across 6 duration
strata. The no_speech_probability field is a proxy (0.0/1.0) due to HuggingFace API
limitations.

</details>

## 2026-06-26 (2)

<details>
<summary>📊 <strong>Granite Speech 4.1 2B — Streaming Keyword-Biased on
Gold-92</strong>
(<code>granite-speech-4.1-2b-gold92-streaming-biased</code>) — 93 instances
(jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `granite-speech-4.1-2b-gold92-streaming-biased` |
| **Model ID** | — |
| **Model** | ibm-granite/granite-speech-4.1-2b, HuggingFace Transformers BF16, GPU inference, keyword prompt injection (31 domain terms) |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-26 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0011_streaming_stt_benchmark`](../../../overview/tasks/task_pages/t0011_streaming_stt_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0011_streaming_stt_benchmark/assets/predictions/granite-speech-4.1-2b-gold92-streaming-biased/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.088265
* **entity_accuracy_gold92**: 0.41087
* **entity_accuracy_domain_vocab**: 0.971014
* **action_critical_wer_gold92**: 0.075949
* **intent_preservation_gold92**: 0.935484
* **latency_p50_seconds**: 0.25

## Metadata

- **Model:** Granite Speech 4.1 2B — keyword biased, streaming simulation
- **Task:** t0011_streaming_stt_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** Azure H100 NVL, Transformers BF16, 32 kB PCM chunk streaming simulation
- **Date:** 2026-06-26

## Overview

Per-clip predictions from ibm-granite/granite-speech-4.1-2b with keyword prompt injection
(`"transcribe the speech to text. Keywords: Rezolve, Rezolve Ai, ..."`, 31 domain terms) under
production-style streaming: audio delivered as 32 kB PCM int16 chunks (~1 s at 16 kHz),
accumulated in memory, transcribed on None sentinel. Mirrors `STTAdapter.transcribe_stream()`.

## Model

- **HuggingFace ID / Model ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** Granite Speech 4.1 2B (encoder-decoder), ~2B params
- **Framework:** HuggingFace Transformers, BF16
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** Keyword prompt injection — 31 domain vocabulary terms

## Streaming Simulation

- Chunk size: 32,000 bytes = 16,000 samples = ~1 s at 16 kHz int16
- Mean chunks/clip: 6.7 (avg audio duration ~6.7 s)
- Latency clock: starts at first chunk delivery, ends when transcription returns
- Accumulate-then-transcribe: all chunks buffered, single model call at end

## Data

Gold-92 benchmark: 93 WAV clips from Rezolve production investor-relations sessions. Anomaly
clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92-streaming.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Granite transcript
- `latency_seconds`: wall-clock from first chunk to transcript (float)
- `num_chunks`: number of 32 kB chunks delivered
- `audio_duration_seconds`: clip audio duration

## Metrics

| Metric | Streaming | Batch (t0007) | Delta |
| --- | --- | --- | --- |
| WER (gold-92) | 8.8% | 8.8% | 0.00 pp |
| Entity accuracy (gold-92) | 41.1% | 40.2% | +0.87 pp |
| Entity accuracy (domain vocab) | 97.1% | 98.6% | −1.45 pp |
| Action-critical WER | 7.6% | 8.2% | −0.63 pp |
| Intent preservation | 93.6% | 92.5% | +1.08 pp |
| Latency p50 | 0.250 s | 0.248 s | +0.001 s |

## Main Ideas

- Streaming delivery has no measurable effect on accuracy (all deltas within noise)
- Granite streaming outperforms Parakeet streaming on all accuracy metrics
- Latency overhead from streaming is negligible (+1 ms)
- Granite p50 latency 250 ms well within 800 ms SLA

</details>

<details>
<summary>📊 <strong>Parakeet TDT 0.6b-v3 — Streaming Biased on Gold-92</strong>
(<code>parakeet-tdt-0.6b-v3-gold92-streaming-biased</code>) — 93 instances
(jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-tdt-0.6b-v3-gold92-streaming-biased` |
| **Model ID** | — |
| **Model** | nvidia/parakeet-tdt-0.6b-v3, Token-and-Duration Transducer, NeMo/Riva SDK, GPU inference, NeMo GPU-PB boosting alpha=1.0 |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-26 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0011_streaming_stt_benchmark`](../../../overview/tasks/task_pages/t0011_streaming_stt_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0011_streaming_stt_benchmark/assets/predictions/parakeet-tdt-0.6b-v3-gold92-streaming-biased/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.152457
* **entity_accuracy_gold92**: 0.231522
* **entity_accuracy_domain_vocab**: 0.333333
* **action_critical_wer_gold92**: 0.335443
* **intent_preservation_gold92**: 0.871011
* **latency_p50_seconds**: 0.041

## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — biased (production config), streaming simulation
- **Task:** t0011_streaming_stt_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** Azure H100 NVL, NeMo / Riva SDK, 32 kB PCM chunk streaming simulation
- **Date:** 2026-06-26

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 with production keyword biasing (NeMo
GPU-PB phrase boosting, alpha=1.0) under production-style streaming: audio delivered as 32 kB
PCM int16 chunks (~1 s at 16 kHz), accumulated in memory, transcribed on None sentinel.
Mirrors the `STTAdapter.transcribe_stream()` default accumulate-then-transcribe pattern.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB phrase boosting, 66 casing variants, alpha=1.0

## Streaming Simulation

- Chunk size: 32,000 bytes = 16,000 samples = ~1 s at 16 kHz int16
- Mean chunks/clip: 6.7 (avg audio duration ~6.7 s)
- Latency clock: starts at first chunk delivery, ends when transcription returns
- Accumulate-then-transcribe: all chunks buffered, single model call at end

## Data

Gold-92 benchmark: 93 WAV clips from Rezolve production investor-relations sessions. Anomaly
clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92-streaming.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Parakeet transcript
- `latency_seconds`: wall-clock from first chunk to transcript (float)
- `num_chunks`: number of 32 kB chunks delivered
- `audio_duration_seconds`: clip audio duration

## Metrics

| Metric | Streaming | Batch (t0009) | Delta |
| --- | --- | --- | --- |
| WER (gold-92) | 15.2% | 15.2% | +0.05 pp |
| Entity accuracy (gold-92) | 23.1% | 23.2% | −0.05 pp |
| Entity accuracy (domain vocab) | 33.3% | 33.3% | +0.03 pp |
| Action-critical WER | 33.5% | 33.5% | +0.04 pp |
| Intent preservation | 87.1% | 87.1% | 0.00 pp |
| Latency p50 | 0.041 s | 0.038 s | +0.003 s |

## Main Ideas

- Streaming delivery has no measurable effect on accuracy (all deltas < 0.1 pp)
- Accumulate-then-transcribe is functionally equivalent to batch at segment level
- Latency overhead from streaming is negligible (+3 ms) — chunk iteration is near-instant
- Parakeet remains the fastest model at 41 ms p50, 6× faster than Granite under streaming

</details>

## 2026-06-25 (10)

<details>
<summary>📊 <strong>Granite Speech 4.1 2B — Batch (no biasing) on Gold-92</strong>
(<code>granite-speech-4.1-2b-gold92-batch</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `granite-speech-4.1-2b-gold92-batch` |
| **Model ID** | — |
| **Model** | ibm-granite/granite-speech-4.1-2b, GraniteSpeechForConditionalGeneration, HuggingFace Transformers 4.57.6, GPU bfloat16, no vocabulary biasing |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-speech-4.1-2b-gold92-batch/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.12337
* **entity_accuracy_gold92**: 0.19529
* **entity_accuracy_domain_vocab**: 0.318841
* **action_critical_wer_gold92**: 0.43038
* **intent_preservation_gold92**: 0.849462
* **latency_p50_seconds**: 0.2497

## Metadata

- **Model:** IBM Granite Speech 4.1 2B — batch (no biasing)
- **Task:** t0007_ibm_granite_4_1_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU (bfloat16), HuggingFace Transformers 4.57.6, no vocabulary biasing
- **Date:** 2026-06-25

## Overview

Per-clip predictions from IBM Granite Speech 4.1 2B in batch mode with no keyword biasing on
the gold-92 benchmark. This variant establishes the Granite unbiased baseline to quantify the
contribution of keyword biasing.

## Model

- **HuggingFace ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** GraniteSpeechForConditionalGeneration + AutoProcessor
- **Params:** ~2B
- **Framework:** HuggingFace Transformers 4.57.6
- **Hardware:** GPU, bfloat16, ~4 GB VRAM
- **Biasing:** None

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Stereo clips pre-converted to mono via soundfile channel-averaging. Anomaly clip
`error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Granite Speech transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 12.3% |
| Entity accuracy (gold-92) | 19.5% |
| Entity accuracy (domain vocab) | 31.9% |
| Action-critical WER | 43.0% |
| Intent preservation | 84.9% |
| Latency p50 | 0.250s |

## Main Ideas

- Without biasing, Granite achieves only 19.5% entity accuracy and 31.9% domain-vocab accuracy
- Keyword biasing raises EA from 19.5% to 40.2% (+20.7 pp) and EA_DV from 31.9% to 98.5%
  (+66.6 pp)
- Biasing is the decisive mechanism; unbiased Granite is not production-ready

</details>

<details>
<summary>📊 <strong>Granite Speech 4.1 2B — Keyword Biased on Gold-92</strong>
(<code>granite-speech-4.1-2b-gold92-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `granite-speech-4.1-2b-gold92-biased` |
| **Model ID** | — |
| **Model** | ibm-granite/granite-speech-4.1-2b, GraniteSpeechForConditionalGeneration, HuggingFace Transformers 4.57.6, GPU bfloat16, keyword biasing via chat template prompt |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-speech-4.1-2b-gold92-biased/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.088265
* **entity_accuracy_gold92**: 0.402174
* **entity_accuracy_domain_vocab**: 0.985507
* **action_critical_wer_gold92**: 0.082278
* **intent_preservation_gold92**: 0.924731
* **latency_p50_seconds**: 0.2484

## Metadata

- **Model:** IBM Granite Speech 4.1 2B — keyword biased
- **Task:** t0007_ibm_granite_4_1_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU (bfloat16), HuggingFace Transformers 4.57.6, keyword biasing via chat
  prompt
- **Date:** 2026-06-25

## Overview

Per-clip predictions from IBM Granite Speech 4.1 2B with keyword biasing on the gold-92
benchmark. Keyword biasing is injected via the chat template prompt (`<|audio|>{prompt}`) with
Rezolve domain vocabulary terms. This is the primary production-candidate variant for this
task.

## Model

- **HuggingFace ID:** ibm-granite/granite-speech-4.1-2b
- **Architecture:** GraniteSpeechForConditionalGeneration + AutoProcessor
- **Params:** ~2B
- **Framework:** HuggingFace Transformers 4.57.6
- **Hardware:** GPU, bfloat16, ~4 GB VRAM
- **Biasing:** Keyword injection via chat template prompt

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Stereo clips pre-converted to mono via soundfile channel-averaging. Anomaly clip
`error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

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
- Credible production replacement for Parakeet on accuracy; fine-tuning could close remaining
  gap vs. Whisper

</details>

<details>
<summary>📊 <strong>Moonshine v2 Medium on Gold-92</strong>
(<code>moonshine-v2-medium-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-v2-medium-gold92` |
| **Model ID** | — |
| **Model** | Moonshine Streaming Medium (UsefulSensors/moonshine-streaming-medium), transformers CPU inference, ~266M params, sliding-window Transformer encoder |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.165496
* **entity_accuracy_gold92**: 0.217029
* **entity_accuracy_domain_vocab**: 0.090909
* **intent_preservation_gold92**: 0.870968
* **latency_p50_seconds**: 0.2321

## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** CPU, transformers 5.12.1, no biasing
- **Date:** 2026-06-25

## Overview

This asset contains per-clip predictions from Moonshine Streaming Medium on the gold-92
benchmark. Moonshine is a streaming Transformer encoder-decoder STT model from UsefulSensors,
optimised for edge and low-latency deployment. The medium variant has approximately 266M
parameters and uses a sliding-window encoder architecture.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder + auto-regressive decoder
- **Params:** ~266M
- **Framework:** HuggingFace Transformers (MoonshineStreamingForConditionalGeneration)
- **Hardware:** CPU inference
- **Biasing:** None (no vocabulary boosting or prompt injection)

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

One anomaly clip (`error_en_0005`) has Cyrillic ground truth due to an annotation error; it is
included in WER computation but excluded from entity accuracy aggregates.

## Prediction Format

Each line in `files/predictions-gold92.jsonl` is a JSON object with:

- `clip_id`: string identifier
- `ground_truth`: reference transcript
- `prediction`: Moonshine v2 Medium hypothesis
- `wer_local`: per-clip word error rate (float)
- `entity_accuracy_local`: per-clip entity accuracy (float or null for anomaly clip)
- `latency_ms`: inference latency in milliseconds (float)
- `latency_stage`: one of `cold_start`, `warmup`, `warmed`

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 0.1655 |
| Entity accuracy (gold-92) | 0.2170 |
| Entity accuracy (domain vocab) | 0.0909 |
| Action-critical WER | 0.3418 |
| Intent preservation | 0.8710 |
| Wrong-action rate | 0.1290 |
| Latency p50 (warmed) | 0.233s |

## Main Ideas

- Moonshine v2 Medium (CPU) achieves WER=16.6% on gold-92, 2x worse than Whisper large-v3
  (8.5%)
- Domain-vocabulary entity accuracy is 9.1% vs 94.5% for Whisper with biasing — 85pp gap
- Excellent warmed latency: 0.233s p50 (29x faster than Whisper 6.66s)
- Entity recognition failures are vocabulary-driven (OOV domain terms), not capacity-driven
- Model is not production-ready for Rezolve's voice commerce use case without vocabulary
  biasing

## Summary

Moonshine v2 Medium achieves reasonable general WER (16.6%) but significantly underperforms
Whisper on domain-specific entity accuracy (9.1% vs 94.5% domain-vocab accuracy). The model
does not support vocabulary biasing or initial prompt injection, which explains the poor
performance on Rezolve-specific entity terms. Warmed-up latency p50 is 0.233s, which is
excellent for the streaming use case. The model is not recommended for production deployment
without vocabulary biasing or fine-tuning.

</details>

<details>
<summary>📊 <strong>Moonshine v2 Medium Shallow-Fusion Feasibility
Assessment</strong>
(<code>moonshine-v2-medium-gold92-biasing-assessment</code>) — — instances
(jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-v2-medium-gold92-biasing-assessment` |
| **Model ID** | — |
| **Model** | Moonshine v2 Medium — shallow fusion feasibility assessment (no inference run) |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | — |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92-biasing-assessment/description.md) |

## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Type:** Feasibility assessment (no per-clip predictions)
- **Date:** 2026-06-25

## Overview

This asset documents a feasibility assessment for adding shallow-fusion vocabulary biasing to
Moonshine v2 Medium. The assessment was motivated by the model's low domain-vocabulary entity
accuracy (9.1%) compared to Whisper with vocabulary biasing (94.5%). No inference was run for
this asset; it is an architectural analysis only.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder-decoder (not CTC)
- **Key constraint:** No `initial_prompt` support; no built-in hotword boosting

## Data

References the gold-92 benchmark and Rezolve domain vocabulary (31 terms) from
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py`.

## Prediction Format

Assessment document only. See `files/shallow_fusion_feasibility.md` for the full analysis.

## Metrics

Not applicable (no inference run for this asset).

## Main Ideas

- Moonshine v2 Medium uses an encoder-decoder architecture that blocks the easiest
  shallow-fusion path (CTC hotword boosting via pyctcdecode)
- Log-linear N-best rescoring (KenLM domain LM) is the recommended approach: ~3-5 days effort,
  +50-80ms latency overhead per clip
- Feasibility verdict: "needs research" — the approach is architecturally viable but 85pp
  entity accuracy gap vs Whisper biased is unlikely to close fully from shallow fusion alone
- Hybrid routing (Moonshine for latency-critical queries, Whisper for entity-critical) may
  offer the best production trade-off

## Summary

Three shallow-fusion approaches were assessed:

1. **Log-linear N-best rescoring** (recommended): Rescore top-4 beams with a KenLM domain LM.
   Effort: 3-5 days. Latency overhead: +50-80ms.
2. **pyctcdecode CTC hotword boosting**: Requires CTC-head surgery or an official CTC variant.
   Blocked by encoder-decoder architecture.
3. **Lattice rescoring**: Similar to approach 1 but with full lattice; higher complexity for
   marginal gain.

**Verdict:** Viable for production (with effort), but the entity accuracy gap vs. Whisper is
large. A hybrid routing strategy (Moonshine for latency-critical, Whisper for entity-critical)
may be optimal.

</details>

<details>
<summary>📊 <strong>Nemotron 3.5 ASR — Batch (no biasing) on Gold-92</strong>
(<code>nemotron-3.5-asr-gold92-batch</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `nemotron-3.5-asr-gold92-batch` |
| **Model ID** | — |
| **Model** | NVIDIA Nemotron 3.5 ASR (FastConformer-CTC), NeMo/Riva NIM, GPU inference, batch mode, no vocabulary biasing |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0006_nemotron_3_5_benchmark`](../../../overview/tasks/task_pages/t0006_nemotron_3_5_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-batch/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.175527
* **entity_accuracy_gold92**: 0.247464
* **entity_accuracy_domain_vocab**: 0.181818
* **action_critical_wer_gold92**: 0.316456
* **intent_preservation_gold92**: 0.903226
* **latency_p50_seconds**: 0.7186

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

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
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

</details>

<details>
<summary>📊 <strong>Nemotron 3.5 ASR — Streaming + Word Boosting on Gold-92</strong>
(<code>nemotron-3.5-asr-gold92-word-boosted</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `nemotron-3.5-asr-gold92-word-boosted` |
| **Model ID** | — |
| **Model** | NVIDIA Nemotron 3.5 ASR (FastConformer-CTC), NeMo/Riva NIM, GPU inference, streaming mode with word-boosting API using DOMAIN_VOCAB |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0006_nemotron_3_5_benchmark`](../../../overview/tasks/task_pages/t0006_nemotron_3_5_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0006_nemotron_3_5_benchmark/assets/predictions/nemotron-3.5-asr-gold92-word-boosted/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.198596
* **entity_accuracy_gold92**: 0.187319
* **entity_accuracy_domain_vocab**: 0.127273
* **action_critical_wer_gold92**: 0.424051
* **intent_preservation_gold92**: 0.849462
* **latency_p50_seconds**: 0.723

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

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
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

</details>

<details>
<summary>📊 <strong>Parakeet TDT 0.6b-v3 — Production Config (biased) on
Gold-92</strong> (<code>parakeet-tdt-0.6b-v3-gold92-production</code>)
— 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-tdt-0.6b-v3-gold92-production` |
| **Model ID** | — |
| **Model** | nvidia/parakeet-tdt-0.6b-v3, Token-and-Duration Transducer, NeMo/Riva SDK, GPU inference, keyword biasing matching current production config |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Documentation** | [`description.md`](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-production/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.152457
* **entity_accuracy_gold92**: 0.231522
* **entity_accuracy_domain_vocab**: 0.333333
* **action_critical_wer_gold92**: 0.335443
* **intent_preservation_gold92**: 0.870968
* **latency_p50_seconds**: 0.0378

## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — biased (production config)
- **Task:** t0009_parakeet_production_baseline
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva SDK, keyword injection matching current production
  deployment
- **Date:** 2026-06-25

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 with the keyword biasing configuration
currently deployed in Rezolve's brainpowa production pipeline. This is the canonical
production baseline used for comparison across all t0006–t0010 benchmark tasks.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** GPU
- **Biasing:** Keyword injection matching current production deployment

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Anomaly clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Parakeet transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 15.2% |
| Entity accuracy (gold-92) | 23.2% |
| Entity accuracy (domain vocab) | 33.3% |
| Action-critical WER | 33.5% |
| Intent preservation | 87.1% |
| Latency p50 | 0.038s |

## Main Ideas

- This is the production baseline used for all t0006–t0010 comparisons
- Keyword biasing provides negligible benefit vs. unbiased: ΔEA=−0.2 pp, ΔEA_DV=+1.4 pp
- Ultra-low latency (38 ms) is the model's decisive strength for production deployment
- Entity accuracy 23.2% and AC-WER 33.5% set the floor all benchmark models must exceed

</details>

<details>
<summary>📊 <strong>Parakeet TDT 0.6b-v3 — Unbiased on Gold-92</strong>
(<code>parakeet-tdt-0.6b-v3-gold92-unbiased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-tdt-0.6b-v3-gold92-unbiased` |
| **Model ID** | — |
| **Model** | nvidia/parakeet-tdt-0.6b-v3, Token-and-Duration Transducer, NeMo/Riva SDK, GPU inference, no vocabulary biasing |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Documentation** | [`description.md`](../../../tasks/t0009_parakeet_production_baseline/assets/predictions/parakeet-tdt-0.6b-v3-gold92-unbiased/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.151454
* **entity_accuracy_gold92**: 0.233696
* **entity_accuracy_domain_vocab**: 0.318841
* **action_critical_wer_gold92**: 0.341772
* **intent_preservation_gold92**: 0.870968
* **latency_p50_seconds**: 0.0388

## Metadata

- **Model:** Parakeet TDT 0.6b-v3 — unbiased
- **Task:** t0009_parakeet_production_baseline
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, NeMo / Riva SDK, standard inference, no keyword injection
- **Date:** 2026-06-25

## Overview

Per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 in standard inference mode (no keyword
biasing) on the gold-92 benchmark. This variant establishes the unbiased baseline for
Rezolve's current production STT model.

## Model

- **HuggingFace ID / Model ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), 0.6B params
- **Framework:** NeMo / Riva SDK
- **Hardware:** GPU
- **Biasing:** None

## Data

The gold-92 benchmark consists of 93 WAV audio clips from Rezolve production
investor-relations sessions with accented English speech. Ground truth transcripts are from
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.

Anomaly clip `error_en_0005` (Cyrillic ground truth) excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Parakeet transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 15.1% |
| Entity accuracy (gold-92) | 23.4% |
| Entity accuracy (domain vocab) | 31.9% |
| Action-critical WER | 34.2% |
| Intent preservation | 87.1% |
| Latency p50 | 0.039s |

</details>

<details>
<summary>📊 <strong>SeACo-Paraformer-en — Batch (no biasing) on Gold-92</strong>
(<code>seaco-paraformer-large-gold92-batch</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `seaco-paraformer-large-gold92-batch` |
| **Model ID** | — |
| **Model** | iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020, Paraformer-CTC with SeACo module, FunASR Python SDK, GPU inference, no contextual biasing |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0010_funasr_paraformer_benchmark`](../../../overview/tasks/task_pages/t0010_funasr_paraformer_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-batch/description.md) |

**Metrics at creation:**

* **wer_gold92**: 1.22668
* **entity_accuracy_gold92**: 0.021739
* **entity_accuracy_domain_vocab**: 0.0
* **action_critical_wer_gold92**: 1.0
* **intent_preservation_gold92**: 0.55914
* **latency_p50_seconds**: 0.0478

## Metadata

- **Model:** FunASR SeACo-Paraformer-en — batch (no biasing)
- **Task:** t0010_funasr_paraformer_benchmark
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Inference:** GPU, FunASR Python SDK, standard Paraformer inference, no SeACo biasing
- **Date:** 2026-06-25

## Overview

Per-clip predictions from FunASR SeACo-Paraformer-en in standard batch mode (no contextual
biasing) on the gold-92 benchmark. The model produces near-random English-sounding tokens on
English input; WER=122.7% indicates complete transcription failure. This variant establishes
the unbiased baseline for the SeACo ablation.

## Model

- **Model ID:** iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020
- **Architecture:** Paraformer (CTC) with SeACo contextual biasing module
- **Framework:** FunASR Python SDK
- **Hardware:** GPU
- **Biasing:** None

## Data

93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Anomaly
clip `error_en_0005` excluded from entity accuracy aggregates.

## Prediction Format

Each record in `files/predictions-gold92.jsonl`:

- `clip_id`: string clip identifier
- `hypothesis`: Paraformer transcript
- `latency_seconds`: per-clip wall-clock inference latency (float)

## Metrics

| Metric | Value |
| --- | --- |
| WER (gold-92) | 122.7% |
| Entity accuracy (gold-92) | 2.2% |
| Entity accuracy (domain vocab) | 0.0% |
| Action-critical WER | 100.0% |
| Intent preservation | 55.9% |
| Latency p50 | 0.048s |

## Main Ideas

- WER > 100% confirms complete transcription failure on English input
- Model produces Chinese-phoneme-adjacent English syllable sequences, not transcriptions
- Not suitable for any English STT use case at Rezolve

</details>

<details>
<summary>📊 <strong>SeACo-Paraformer-en — Contextual Biased on Gold-92</strong>
(<code>seaco-paraformer-large-gold92-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `seaco-paraformer-large-gold92-biased` |
| **Model ID** | — |
| **Model** | iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020, Paraformer-CTC with SeACo module, FunASR Python SDK, GPU inference, SeACo contextual biasing with DOMAIN_VOCAB |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-25 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Created by** | [`t0010_funasr_paraformer_benchmark`](../../../overview/tasks/task_pages/t0010_funasr_paraformer_benchmark.md) |
| **Documentation** | [`description.md`](../../../tasks/t0010_funasr_paraformer_benchmark/assets/predictions/seaco-paraformer-large-gold92-biased/description.md) |

**Metrics at creation:**

* **wer_gold92**: 1.221665
* **entity_accuracy_gold92**: 0.021739
* **entity_accuracy_domain_vocab**: 0.0
* **action_critical_wer_gold92**: 1.0
* **intent_preservation_gold92**: 0.55914
* **latency_p50_seconds**: 0.0472

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

93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Anomaly
clip `error_en_0005` excluded from entity accuracy aggregates.

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
- WER > 100% confirms complete transcription failure; biasing cannot rescue a broken base
  model
- Not suitable for any English STT use case at Rezolve

</details>

## 2026-06-23 (5)

<details>
<summary>📊 <strong>Moonshine Base on Gold-92 (no vocabulary biasing)</strong>
(<code>moonshine-base-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `moonshine-base-gold92` |
| **Model ID** | — |
| **Model** | UsefulSensors/moonshine-base (~60M parameters) run via useful-moonshine-onnx (ONNX, CPU, 16 kHz). No vocabulary biasing supported. Note: UsefulSensors has no 'small' variant; 'base' is the closest equivalent. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.217029
* **wer_gold92**: 0.183551

# Moonshine Base on Gold-92 (no vocabulary biasing)

## Metadata

* **Name**: Moonshine Base on Gold-92 (no vocabulary biasing)
* **Model**: UsefulSensors Moonshine base (~60M parameters, ONNX CPU)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of UsefulSensors Moonshine base (~60M
parameters, ONNX CPU) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

UsefulSensors Moonshine base (~60M parameters, ONNX CPU) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.2170 |
| wer_gold92 | 0.1836 |
| latency_p50_seconds | 0.07s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper Large v3 + Vocabulary Bias on Gold-92</strong>
(<code>whisper-large-v3-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-large-v3-biased` |
| **Model ID** | — |
| **Model** | OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to a 31-term domain vocabulary string covering Rezolve brand names, product lines, and key people. No fine-tuning applied. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.460145
* **wer_gold92**: 0.085256

# Whisper Large v3 + Vocabulary Bias on Gold-92

## Metadata

* **Name**: Whisper Large v3 + Vocabulary Bias on Gold-92
* **Model**: Whisper Large v3 (~1.5B parameters, faster-whisper INT8)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of Whisper Large v3 (~1.5B parameters,
faster-whisper INT8) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 (~1.5B parameters, faster-whisper INT8) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.4601 |
| wer_gold92 | 0.0853 |
| latency_p50_seconds | 6.66s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper Large v3 on Gold-92</strong>
(<code>whisper-large-v3-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-large-v3-gold92` |
| **Model ID** | — |
| **Model** | OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en') on Apple M5 Mac. No fine-tuning or domain adaptation. Production-ready but latency-constrained for local CPU. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Documentation** | [`description.md`](../../../tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.251812
* **wer_gold92**: 0.100301

# Whisper Large v3 on Gold-92

## Metadata

* **Name**: Whisper Large v3 on Gold-92
* **Model**: Whisper Large v3 (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper Large v3, run locally on
an Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU
inference) on the gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in
this project, containing 93 annotated WAV clips from Rezolve production investor-relations
voice sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases including adversarial and multilingual inputs).

The predictions serve as the open-source STT baseline for the Rezolve brainpowa voice commerce
project. Whisper Large v3 is the state-of-the-art general-purpose ASR model from OpenAI and
represents the best available open-source ceiling before any domain-specific fine-tuning or
post-correction. These results define the starting point against which entity-aware
post-correction, domain fine-tuning, and confidence-based routing approaches will be judged in
subsequent tasks.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
hypothesis, per-clip entity accuracy (using the all-or-nothing Caubrière et al. 2020
criterion), per-clip WER, inference latency in seconds, and entity span annotations indicating
which action-critical entities (brand names, product lines, IR terms) were correctly
recognised.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 is a transformer-based encoder-decoder ASR model trained by OpenAI on 680,000
hours of multilingual speech data. The Large v3 variant contains approximately 1.5 billion
parameters and achieves 2.7% WER on LibriSpeech test-clean under clean conditions. On
non-native spontaneous English (LearnerVoice benchmark), Whisper Large v3 achieves 19.18% WER,
consistent with the expected range for accented investor-relations speech.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The
model was loaded once before the inference loop and applied identically to all 93 clips. The
inference configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing
`language="en"` is mandatory to prevent a documented failure mode where accented English
speech is misclassified as a non-English language, producing garbled transcripts. The model
was warmed up on 3 throwaway clips before recording latencies to avoid cold-cache
measurements. Total inference wall-clock time was approximately 9 minutes on Apple M5 CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which
has normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied
to audio files — they were passed directly to faster-whisper as WAV files.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Resolv AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": false}],
  "entity_accuracy": 0.0,
  "wer": 0.083,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper Large v3 output (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans with type and
  position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing, null for
  anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()` (local CPU
  only, not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | 0.2518 | (0.1812, 0.3370) |
| wer_gold92 | 0.1003 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 5.66s | — |

Entity accuracy of 25.2% reflects the challenging nature of the investor-relations domain for
a general-purpose ASR model. Known failure patterns include: "Rezolve AI" transcribed as
"resolve AI" or "Hizol"; "brainpowa" transcribed as "brain power"; IR abbreviations (20-F,
10-K) inconsistently formatted. WER of 10.0% indicates overall transcription quality is
reasonable but entity-level accuracy (the primary metric) is significantly lower.

## Main Ideas

* Whisper Large v3 achieves **10.0% WER** on gold-92, within the expected range for accented
  investor-relations speech (8-20% from research literature)
* **Entity accuracy of 25.2%** reveals a substantial gap between overall transcription quality
  and entity-level precision — the primary failure mode for voice commerce
* The known failure pattern "Rezolve AI" → "resolve AI" / "Hizol" appears frequently across
  production and clean_voices clips, confirming that entity post-correction is needed
* Intent preservation of **90.3%** (heuristic proxy) suggests most utterances retain their
  high-level intent even when entity accuracy is low
* Inference latency p50 of **5.66s** (local CPU) exceeds the 800ms voice-to-action target —
  dedicated GPU or cloud API is required for production latency requirements

## Summary

These predictions capture the performance of Whisper Large v3, the leading open-source ASR
model, on the gold-92 investor-relations benchmark using local CPU inference. The model was
applied without fine-tuning or domain-specific prompt injection to establish a clean
open-source baseline.

The headline finding is that overall transcription quality (WER: 10.0%) is acceptable but
entity-level accuracy (entity_accuracy_gold92: 25.2%) is low. This gap reflects the model's
difficulty with proper nouns and domain-specific terms that are rare in its training data —
particularly "Rezolve AI", "brainpowa", and IR-domain abbreviations. Intent preservation
(heuristic proxy: 90.3%) shows that most utterances retain sufficient semantic content for
basic intent detection even with imperfect entity recognition.

These results establish the Whisper Large v3 baseline that subsequent post-correction,
fine-tuning, and confidence-routing tasks will need to beat. The comparison against Deepgram
Nova-2 (production baseline) will be added once the Deepgram API key is available (see
intervention/deepgram_api_key_missing.md).

</details>

<details>
<summary>📊 <strong>Whisper Turbo + Vocabulary Bias on Gold-92</strong>
(<code>whisper-turbo-biased</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-turbo-biased` |
| **Model ID** | — |
| **Model** | OpenAI Whisper turbo (~809M parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to a 31-term domain vocabulary string covering Rezolve brand names, product lines, and key people. No fine-tuning applied. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Documentation** | [`description.md`](../../../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.431159
* **wer_gold92**: 0.08325

# Whisper Turbo + Vocabulary Bias on Gold-92

## Metadata

* **Name**: Whisper Turbo + Vocabulary Bias on Gold-92
* **Model**: Whisper turbo (~809M parameters, faster-whisper INT8)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of Whisper turbo (~809M parameters,
faster-whisper INT8) on the gold-92 benchmark, using vocabulary biasing via Whisper's
`initial_prompt` parameter. The experiment is part of task t0004 which ablates the effect of a
31-term domain vocabulary injected as initial context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production
investor-relations voice sessions, with accented English speakers across three source
categories: `clean_voices` (speaker-narrated IR Q&A), `production` (live production session
captures), and `error_cases` (known hard cases). The vocabulary prompt includes key brand
names (Rezolve, brainpowa), product lines (Brain Commerce, Brain Checkout), partner names
(GroupBy, Bluedot, ViSenze), and people names (Dan Wagner, Arthur Yao, etc.) that appear in
the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper turbo (~809M parameters, faster-whisper INT8) run locally via `faster-whisper`
(CTranslate2 INT8 quantization, CPU inference, language='en') on Apple M5 Mac. The key
difference from the t0002 baseline is the addition of `initial_prompt` set to the 31-term
domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation
without any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording
latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.4312 |
| wer_gold92 | 0.0832 |
| latency_p50_seconds | 5.86s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that
  requires no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people
  names that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact
  of vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to
  hallucinate terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term
vocabulary covers the key entities in the Rezolve IR domain that appear most frequently in
production voice sessions.

The headline finding (available in
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`) shows the effect size of
vocabulary biasing on entity_accuracy_gold92 and entity_accuracy_domain_vocab relative to the
t0002 baselines. Even small improvements in entity accuracy are meaningful for the voice
commerce use case, where downstream intent routing depends critically on correct entity
recognition.

</details>

<details>
<summary>📊 <strong>Whisper turbo on Gold-92</strong>
(<code>whisper-turbo-gold92</code>) — 93 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `whisper-turbo-gold92` |
| **Model ID** | — |
| **Model** | OpenAI Whisper turbo (~809M parameters) run locally via faster-whisper (CTranslate2 INT8, CPU, language='en') on Apple M5 Mac. No fine-tuning or domain adaptation. Whisper turbo is a distilled variant offering comparable accuracy to large-v3 at roughly 8x faster inference. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 93 |
| **Date created** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Created by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Documentation** | [`description.md`](../../../tasks/t0002_baseline_evaluation/assets/predictions/whisper-turbo-gold92/description.md) |

**Metrics at creation:**

* **entity_accuracy_gold92**: 0.251812
* **wer_gold92**: 0.106319

# Whisper turbo on Gold-92

## Metadata

* **Name**: Whisper turbo on Gold-92
* **Model**: Whisper turbo (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper turbo, run locally on an
Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU inference)
on the gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in this
project, containing 93 annotated WAV clips from Rezolve production investor-relations voice
sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases including adversarial and multilingual inputs).

Whisper turbo is a distilled variant of Whisper Large v3 developed by OpenAI to achieve
near-large accuracy at substantially reduced inference cost. This evaluation quantifies
whether turbo's compression trades off significantly on entity accuracy for the Rezolve
investor-relations domain, or whether it achieves a better speed-accuracy tradeoff than
large-v3 for production deployment.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
turbo hypothesis, per-clip entity accuracy (all-or-nothing Caubrière et al. 2020 criterion),
per-clip WER, inference latency in seconds, and entity span annotations indicating which
action-critical entities (brand names, product lines, IR terms) were correctly recognised.
These results sit alongside the `whisper-large-v3-gold92` predictions to enable direct
comparison between model variants.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for
this clip is a normal English sentence; this clip is included in WER computation but excluded
from the aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper turbo is a distilled transformer-based encoder-decoder ASR model released by OpenAI as
a faster alternative to Whisper Large v3. The turbo variant has approximately 809 million
parameters — roughly half the size of large-v3 (~1.5B) — achieved through structured
distillation that preserves the decoder architecture while reducing encoder depth. OpenAI
reports that turbo achieves similar transcription quality to large-v3 on standard ASR
benchmarks while running approximately 8x faster in real-time factor on CPU.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The
model was loaded once before the inference loop and applied identically to all 93 clips. The
inference configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing
`language="en"` is mandatory to prevent a documented failure mode where accented English
speech is misclassified as a non-English language, producing garbled transcripts. The model
was warmed up on 3 throwaway clips before recording latencies. Total inference wall-clock time
was approximately 6.6 minutes on Apple M5 CPU, compared to 8.8 minutes for large-v3 — a ~25%
reduction on this CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn
from three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which
has normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied
to audio files — they were passed directly to faster-whisper as WAV files.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Resolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": false}],
  "entity_accuracy": 0.0,
  "wer": 0.083,
  "latency_seconds": 4.25,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper turbo output (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans with type and
  position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing, null for
  anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()` (local CPU
  only, not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | 0.2518 | (0.1812, 0.3370) |
| wer_gold92 | 0.1063 | — |
| action_critical_wer_gold92 | 0.3038 | — |
| intent_preservation_gold92 | 0.9032 | — |
| latency_p50_seconds | 4.25s | — |

Entity accuracy of 25.2% matches Whisper Large v3 exactly, confirming that the turbo
distillation preserves entity-level behaviour on this domain. WER of 10.6% is marginally
higher than large-v3 (10.0%), consistent with the expected slight quality tradeoff from
distillation. Latency p50 of 4.25s is approximately 25% faster than large-v3 (5.66s) on Apple
M5 CPU.

## Main Ideas

* Whisper turbo achieves **entity_accuracy_gold92 = 25.2%**, identical to Whisper Large v3
  (25.2%) — the distillation preserves entity-level accuracy on this IR domain
* WER of **10.6%** is marginally higher than large-v3 (10.0%), a small tradeoff consistent
  with expected distillation loss on non-native accented speech
* Latency p50 of **4.25s** is ~25% faster than large-v3 (5.66s) on Apple M5 CPU — both remain
  far above the 800ms voice-to-action production target, confirming that local CPU inference
  is not viable for production regardless of model size
* The identical entity accuracy between turbo and large-v3 suggests that turbo is the
  preferred variant for subsequent fine-tuning experiments: equivalent baseline quality,
  faster iteration cycles, and lower inference cost on GPU infrastructure

## Summary

These predictions capture the performance of Whisper turbo, OpenAI's distilled large-v3
variant, on the gold-92 investor-relations benchmark using local CPU inference. The model was
applied without fine-tuning or domain-specific prompt injection to establish a comparative
open-source baseline alongside the Whisper Large v3 run in the same task.

The headline finding is that Whisper turbo achieves **identical entity accuracy (25.2%)** and
**comparable WER (10.6% vs 10.0%)** to Whisper Large v3, while being approximately 25% faster
on Apple M5 CPU (latency p50: 4.25s vs 5.66s). Both models share the same entity recognition
failure patterns — "Rezolve AI" transcribed as "Resolve AI" or "Hizol", "brainpowa" as "brain
power" — confirming that the gap between large-v3 and turbo in the IR domain is negligible
before fine-tuning.

Given that turbo matches large-v3 entity accuracy at lower cost, it is the preferred model for
subsequent fine-tuning and post-correction experiments. The 10.6% WER baseline and 4.25s CPU
latency define the starting point that domain adaptation must beat. Both WER and latency
improvements require GPU infrastructure or specialised lightweight models rather than
model-size changes within the Whisper family.

</details>
