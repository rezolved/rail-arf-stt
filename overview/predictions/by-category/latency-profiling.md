# Predictions: `latency-profiling`

7 predictions asset(s).

[Back to all predictions](../README.md)

---

<details>
<summary>📊 <strong>Granite Speech 4.1 2B Buffer Interval Sweep on gold-92</strong>
(<code>granite-buffer-sweep</code>) — 279 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `granite-buffer-sweep` |
| **Model ID** | — |
| **Model** | ibm-granite/granite-speech-4.1-2b (2B params, seq2seq speech LLM) biased via keyword prompt injection: 'transcribe the speech to text. Keywords: Rezolve, brainpowa, ...' (31 domain terms). |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 279 |
| **Date created** | 2026-07-01 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Documentation** | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/granite-buffer-sweep/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.0883
* **entity_accuracy_gold92**: 0.9625
* **entity_accuracy_domain_vocab**: 0.971
* **latency_p50_seconds_500ms**: 1.232
* **latency_p50_seconds_750ms**: 1.212
* **latency_p50_seconds_1000ms**: 1.113
* **ttfd_p50_seconds_500ms**: 0.077
* **ttfd_p50_seconds_750ms**: 0.076
* **ttfd_p50_seconds_1000ms**: 0.075

## Metadata

| Field | Value |
|---|---|
| Predictions ID | granite-buffer-sweep |
| Task | t0015_streaming_buffer_interval |
| Model | ibm-granite/granite-speech-4.1-2b |
| Dataset | stt-benchmark-gold-92 (gold-92), 93 clips |
| Instance count | 279 (93 clips × 3 intervals) |
| Intervals tested | 500ms, 750ms, 1000ms |
| Date created | 2026-07-01 |
| WER | 8.83% |
| Entity Accuracy | 96.25% |
| EA Domain Vocab | 97.10% |

## Overview

This asset contains predictions from IBM Granite Speech 4.1 2B evaluated under a streaming
buffer interval sweep on the gold-92 benchmark dataset. The benchmark task
(t0015_streaming_buffer_interval) evaluates 4 models across 3 buffer extraction intervals
(500ms, 750ms, 1000ms), for a total of 12 model-interval combinations. This asset covers the
Granite Speech 4.1 2B model across all three intervals.

The streaming buffer approach accumulates incoming PCM-16 audio chunks and re-transcribes the
accumulated buffer at regular intervals. The interval parameter controls how frequently this
re-transcription occurs: at 500ms, the model transcribes every half-second of audio
accumulation; at 1000ms, it transcribes once per second. The final transcript is taken from
the last inference call when the audio clip ends. Because WER and entity accuracy are computed
on the final transcript, these quality metrics are identical across intervals for the same
clip — the interval only affects latency and TTFD (time to first decode).

Granite Speech 4.1 2B is a seq2seq speech language model from IBM, capable of accepting
natural-language prompts alongside the audio input. This property enables keyword prompt
injection biasing, where a curated list of 31 domain-specific terms is supplied in the
transcription prompt to steer the model toward correct recognition of proper nouns and
technical vocabulary.

Granite achieves the best WER (8.83%) of all models benchmarked in this task, and dramatically
outperforms the Parakeet CTC and RNNT models on entity recognition. Its main trade-off is
higher latency: as a seq2seq architecture, it is slower than CTC/RNNT models, with p50 latency
of 1.1–1.2 seconds depending on interval.

## Model

**Model:** ibm-granite/granite-speech-4.1-2b **Architecture:** Sequence-to-sequence speech
language model (2B parameters) **Biasing method:** Keyword prompt injection (not NeMo GPU-PB)

Granite Speech 4.1 2B is a multimodal model that processes audio together with a text prompt.
The prompt used for all clips in this asset is:

> "transcribe the speech to text. Keywords: Rezolve, brainpowa, ..." (31 domain terms total)

The 31 domain terms span Rezolve-specific product names, brand names, and technical vocabulary
that appear in the investor-relations audio corpus (e.g., "Rezolve", "brainpowa", and other
proprietary terms). Keyword prompt injection is an intrinsic biasing mechanism that does not
require a separate biasing model or GPU-accelerated prefix boosting (unlike NeMo GPU-PB used
for Parakeet models). This makes Granite's biasing simpler to deploy but also means the
biasing is "soft" — the model is guided but not forced to prefer the listed terms.

The seq2seq architecture means Granite generates its transcript autoregressively, token by
token, after processing the full audio context. This makes it inherently slower than
discriminative (CTC/RNNT) models, which produce all output frames in a single forward pass.
However, the generative nature also makes Granite more robust to complex pronunciation
patterns and accented speech, which is why it achieves the lowest WER of all four benchmarked
models.

A non-streaming baseline for Granite (accumulate-then-transcribe, from task t0014) achieved
WER 8.8%, EA-DV 97.1%, and TTFD p50 77ms. The streaming buffer sweep results match this
baseline almost exactly, confirming that Granite's final-transcript quality is robust to
partial audio buffering — the model transcribes the full clip accurately regardless of how
many intermediate inference calls were made during streaming.

## Data

**Dataset:** stt-benchmark-gold-92 (gold-92) **Clips:** 93 WAV files, 16kHz mono, variable
duration **Domain:** Investor-relations, earnings calls, product presentations **Speech
characteristics:** Accented English (British, non-native speakers), domain-specific proper
nouns, mixed technical and financial vocabulary

The gold-92 dataset is a curated benchmark of 93 audio clips drawn from investor-relations
content relevant to the Rezolve AI product domain. Clips contain a variety of speakers with
accented English pronunciation. The reference transcripts were manually verified. This dataset
is particularly challenging for generic STT models due to the high density of brand names,
product names, and neologisms (e.g., "brainpowa") that are absent from standard acoustic model
training corpora.

Each of the three JSONL files in this asset (500ms, 750ms, 1000ms) contains predictions for
all 93 clips at the corresponding buffer extraction interval, giving 279 prediction records in
total. Fields recorded per clip include `clip_id`, `duration_s`, `transcript` (final predicted
text), `reference_text`, `is_empty`, `is_hallucination`, `ttfd_seconds`, `latency_seconds`,
`interval_ms`, `n_chunks`, and `n_inferences`.

Zero clips produced empty transcripts across all intervals, and zero hallucinations were
detected. This reflects Granite's strong reliability on the gold-92 domain, even when running
in streaming mode with frequent partial-audio inference calls.

## Prediction Format

Each file is JSONL (one JSON object per line). Fields:

| Field | Type | Description |
|---|---|---|
| clip_id | string | Unique clip identifier matching gold-92 dataset |
| duration_s | float | Audio clip duration in seconds |
| transcript | string | Final predicted transcript text |
| reference_text | string | Ground-truth reference transcript |
| is_empty | bool | True if transcript is empty or whitespace only |
| is_hallucination | bool | True if transcript is flagged as hallucination |
| ttfd_seconds | float | Time to first decode (seconds from stream start) |
| latency_seconds | float | Total transcription latency (seconds) |
| interval_ms | int | Buffer extraction interval in milliseconds |
| n_chunks | int | Number of audio chunks accumulated |
| n_inferences | int | Number of model inference calls made |

The three files differ only in `interval_ms`, `n_chunks`, `n_inferences`, `ttfd_seconds`, and
`latency_seconds`. The `transcript` and all quality metrics are computed on the final
transcript after the clip ends.

## Metrics

Quality metrics are computed on the final transcript (identical across intervals for the same
clip):

| Metric | Value |
|---|---|
| WER (gold-92) | 8.83% |
| Entity Accuracy (gold-92) | 96.25% |
| EA Domain Vocab | 97.10% |
| Empty transcripts | 0 |
| Hallucinations | 0 |

Latency and TTFD metrics vary by interval:

| Interval | Latency p50 | TTFD p50 |
|---|---|---|
| 500ms | 1.232s | 0.077s |
| 750ms | 1.212s | 0.076s |
| 1000ms | 1.113s | 0.075s |

Key observations:
- **WER 8.83%** is the best of all four models benchmarked in t0015, making Granite the
  highest-quality transcription model in this sweep.
- **Entity Accuracy 96.25%** and **EA Domain Vocab 97.10%** are dramatically higher than the
  Parakeet models, demonstrating the effectiveness of keyword prompt injection for
  domain-specific vocabulary.
- **Latency increases at shorter intervals**: at 500ms, Granite makes more inference calls per
  clip (shorter buffering window means more frequent re-transcription), which adds overhead.
  Going from 500ms to 1000ms reduces latency p50 by ~10% (1.232s → 1.113s).
- **TTFD is nearly constant** at 75–77ms across intervals. Shorter intervals trigger the first
  decode sooner in absolute time, but the difference is minimal (2ms between 500ms and 1000ms
  intervals).
- **Latency is the main trade-off**: Granite's p50 latency of 1.1–1.2s is significantly higher
  than the Parakeet models due to autoregressive seq2seq decoding.

## Main Ideas

* **Keyword prompt injection outperforms NeMo GPU-PB for entity recall.** Unlike the Parakeet
  models (which use NeMo GPU prefix boosting), Granite relies on natural-language keyword
  injection in the transcription prompt. This soft biasing mechanism is easier to deploy and,
  in this benchmark, produces better entity accuracy (96.25% vs lower scores for Parakeet
  variants). The 31 domain terms are listed directly in the prompt, guiding but not forcing
  the model.

* **Buffer interval is a latency knob, not a quality knob.** Because WER and entity accuracy
  are computed on the final transcript (after the last inference call), they are independent
  of the buffer interval. The interval only affects how many inference calls occur during
  streaming and therefore total processing time. A 1000ms interval reduces inference call
  frequency and lowers latency p50 by ~10% compared to 500ms, with negligible cost to TTFD.

* **Streaming Granite matches non-streaming baseline.** The Granite non-streaming
  accumulate-and-transcribe baseline (task t0014) achieved WER 8.8% and EA-DV 97.1% —
  essentially identical to the streaming buffer sweep results. This confirms that introducing
  intermediate inference calls during streaming does not degrade Granite's final transcript
  quality. The model is robust to being shown partial audio.

* **Zero failures across all intervals.** No empty transcripts and no hallucinations were
  observed across 279 prediction records (93 clips × 3 intervals). This stands in contrast to
  some alternative models that show occasional hallucinations on very short clips. Granite's
  prompt-conditioned generation appears to constrain output to plausible transcription
  outputs.

* **Latency vs. quality trade-off favors 1000ms for production.** Given that quality is
  constant across intervals and latency improves at 1000ms, the 1000ms buffer interval is the
  recommended operating point for Granite in a production streaming pipeline where latency
  matters and TTFD requirements are loose (sub-100ms TTFD is met at all intervals).

## Summary

This asset provides per-clip streaming predictions for Granite Speech 4.1 2B
(ibm-granite/granite-speech-4.1-2b) on the gold-92 benchmark (93 clips, investor-relations
domain, accented English). The model was evaluated at three buffer extraction intervals —
500ms, 750ms, and 1000ms — producing 279 prediction records in total. Granite achieves the
best quality of all models in the t0015 benchmark: WER 8.83%, entity accuracy 96.25%, and
domain vocab entity accuracy 97.10%. These quality gains are attributable to the model's
generative seq2seq architecture and its ability to accept keyword prompt injection biasing
with 31 domain-specific terms. Quality is independent of buffer interval, as all three
intervals produce identical final transcripts per clip.

The main trade-off is latency: Granite's autoregressive decoding yields p50 latency of 1.1–1.2
seconds, higher than CTC/RNNT alternatives. Within the sweep, increasing the interval from
500ms to 1000ms reduces latency p50 by approximately 10% (1.232s → 1.113s) at negligible cost
to TTFD (77ms → 75ms). For production deployments prioritizing transcript quality over raw
speed, the 1000ms interval offers the best latency-quality trade-off for Granite. No empty
transcripts or hallucinations were observed across all 279 records, confirming Granite's
reliability on this domain.

</details>

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
<summary>📊 <strong>Multitalker Parakeet Streaming 0.6b-v1 Buffer Interval Sweep on
gold-92</strong> (<code>multitalker-parakeet-buffer-sweep</code>) — 279
instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `multitalker-parakeet-buffer-sweep` |
| **Model ID** | — |
| **Model** | nvidia/multitalker-parakeet-streaming-0.6b-v1 (NeMo EncDecMultiTalkerRNNTBPE, 0.6B params) with internal VAD logic and GPU-PB TurboBias attempt. Patched _transcribe_forward for single-speaker mode. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 279 |
| **Date created** | 2026-07-01 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Documentation** | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/multitalker-parakeet-buffer-sweep/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.1334
* **entity_accuracy_gold92**: 0.2219
* **entity_accuracy_domain_vocab**: 0.3188
* **latency_p50_seconds_500ms**: 0.254
* **latency_p50_seconds_750ms**: 0.251
* **latency_p50_seconds_1000ms**: 0.242
* **ttfd_p50_seconds**: 0.064

## Metadata

- **Predictions ID:** multitalker-parakeet-buffer-sweep
- **Model:** nvidia/multitalker-parakeet-streaming-0.6b-v1
- **Task:** t0015_streaming_buffer_interval
- **Dataset:** stt-benchmark-gold-92 (93 clips)
- **Intervals tested:** 500ms, 750ms, 1000ms
- **Total instances:** 279 (93 clips × 3 intervals)
- **Inference:** GPU, NeMo SDK, streaming mode with internal VAD
- **Date:** 2026-07-01

## Overview

This asset contains per-clip streaming predictions from
nvidia/multitalker-parakeet-streaming-0.6b-v1 across a sweep of three buffer extraction
intervals: 500ms, 750ms, and 1000ms. The experiment is part of a broader benchmark covering 4
streaming STT models × 3 intervals = 12 combinations, with this asset covering the multitalker
model variant.

The core question is whether the buffer extraction interval affects transcription quality or
end-to-end latency for a model that uses internal Voice Activity Detection (VAD) to decide
segment boundaries. Unlike parakeet-tdt, which relies entirely on the streaming harness for
flush timing, the multitalker model determines internally when to emit a final token sequence.
The buffer interval therefore controls how frequently the harness polls and extracts partial
results, but does not itself define segment boundary decisions — those are owned by the
model's VAD module.

The sweep reveals that WER (13.34%), entity accuracy (22.19%), and domain-vocab entity
accuracy (31.88%) are identical across all three intervals, confirming that the final
transcript is invariant to flush cadence. Only latency varies: p50 latency drops from 254ms at
500ms interval to 242ms at 1000ms interval, a counterintuitive result explained by reduced
polling overhead and fewer partial-result extraction calls at wider intervals.

This asset provides the raw per-clip JSONL files for downstream evaluation, ablation, and
comparison against the Granite accumulate-then-transcribe baseline (WER 8.8%, EA-DV 97.1%,
TTFD 77ms p50) and the parakeet-tdt streaming model.

## Model

- **Model ID:** nvidia/multitalker-parakeet-streaming-0.6b-v1
- **Architecture:** NeMo EncDecMultiTalkerRNNTBPE (Recurrent Neural Network Transducer with
  multi-talker decoder), 0.6B parameters
- **Internal VAD:** Yes — the model has its own Voice Activity Detection logic that determines
  segment boundaries. This is the key architectural difference from parakeet-tdt-streaming,
  which relies on the harness for flush decisions.
- **GPU-PB TurboBias:** Attempted — the GPU-PB TurboBias prefix-beam biasing mechanism was
  applied to the model. However, the multitalker architecture may not fully support TurboBias,
  meaning biasing may have had no effect or partial effect on the output.
- **Patch applied:** `_transcribe_forward` was patched to handle missing speaker targets,
  enabling single-speaker mode. The model is designed for multi-speaker diarization but the
  gold-92 benchmark contains single-speaker clips; without the patch, inference would fail on
  clips where no speaker target tensor is supplied.
- **Framework:** NeMo Python SDK, GPU inference
- **Streaming mode:** The model is fed audio chunks at each interval boundary; internal VAD
  decides when to flush accumulated audio into a final token sequence.

## Data

- **Dataset:** stt-benchmark-gold-92
- **Clips:** 93 WAV files, 16kHz mono, investor-relations domain, accented English
- **Source:** `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`
- **Ground truth:** Annotated reference transcripts; entity annotations cover brand names,
  product names, and domain-specific vocabulary relevant to Rezolve's ecommerce voice
  platform.
- **Split:** All 93 clips used for inference at each of the three intervals, yielding 279
  total records across the three JSONL files.
- **Note:** The gold-92 dataset is a held-out regression set — it is never used for training
  or fine-tuning.

## Prediction Format

Each line in the JSONL files is a JSON object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `clip_id` | string | Unique clip identifier matching gold-92 dataset |
| `duration_s` | float | Duration of the WAV clip in seconds |
| `transcript` | string | Final transcript produced by the model |
| `reference_text` | string | Ground-truth reference transcript |
| `is_empty` | bool | True if the model produced no output |
| `is_hallucination` | bool | True if the model produced speech not in the audio |
| `ttfd_seconds` | float | Time-to-first-decode: seconds from audio start to first token |
| `latency_seconds` | float | End-to-end latency: seconds from audio start to final token |
| `interval_ms` | int | Buffer extraction interval in milliseconds (500, 750, or 1000) |
| `n_chunks` | int | Number of audio chunks fed to the model |
| `n_inferences` | int | Number of model inference calls made during streaming |
| `model_has_internal_vad` | bool | Always true for this model |

Three files are provided, one per interval:

- `files/predictions-gold92-500ms.jsonl` — 93 clips at 500ms extraction interval
- `files/predictions-gold92-750ms.jsonl` — 93 clips at 750ms extraction interval
- `files/predictions-gold92-1000ms.jsonl` — 93 clips at 1000ms extraction interval

## Metrics

Transcription quality metrics are identical across all three intervals because the model's
internal VAD determines segment boundaries independently of the polling cadence. Only latency
varies:

| Metric | 500ms | 750ms | 1000ms |
| --- | --- | --- | --- |
| WER (gold-92) | 13.34% | 13.34% | 13.34% |
| Entity accuracy (gold-92) | 22.19% | 22.19% | 22.19% |
| EA domain vocab | 31.88% | 31.88% | 31.88% |
| Latency p50 | 0.254s | 0.251s | 0.242s |
| TTFD p50 | 0.064s | 0.064s | 0.064s |
| Empty transcripts | 0 | 0 | 0 |
| Hallucinations | 0 | 0 | 0 |

**Comparison vs Granite baseline** (accumulate-then-transcribe, non-streaming):

| Metric | Multitalker (1000ms) | Granite baseline | Delta |
| --- | --- | --- | --- |
| WER | 13.34% | 8.8% | +4.54 pp |
| EA domain vocab | 31.88% | 97.1% | −65.2 pp |
| TTFD p50 | 0.064s | 0.077s | −13ms |
| Latency p50 | 0.242s | N/A (batch) | — |

The multitalker model achieves faster TTFD than Granite's batch mode (64ms vs 77ms), but at
significant cost to entity accuracy on domain vocabulary (31.88% vs 97.1%). The WER gap (4.54
percentage points) is meaningful but secondary to the entity accuracy collapse, which is the
primary concern for Rezolve's investor-relations use case.

## Main Ideas

* **Internal VAD decouples quality from flush cadence.** The multitalker model's built-in VAD
  means that changing the buffer extraction interval from 500ms to 1000ms has zero effect on
  transcription quality. WER, entity accuracy, and domain-vocab accuracy are all identical
  across intervals. This is the expected behavior for an architecture that owns its own
  segment boundary decisions.

* **TTFD at 64ms — twice the parakeet-tdt latency.** The internal VAD introduces a buffering
  overhead: the model must accumulate enough audio to confidently detect voice activity before
  emitting the first token. This results in a TTFD p50 of 64ms, approximately double the
  parakeet-tdt streaming baseline. For the gold-92 use case (investor-relations Q&A, clips
  averaging 5–8 seconds), this is acceptable, but for short utterances it becomes noticeable.

* **Wider intervals reduce end-to-end latency.** Despite the VAD decoupling quality, latency
  still improves as the interval widens: 254ms at 500ms → 242ms at 1000ms. This is due to
  reduced polling overhead — fewer extraction calls means less Python-level coordination cost
  between the streaming harness and the model. The 12ms saving is modest but consistent.

* **GPU-PB TurboBias impact uncertain.** TurboBias biasing was attempted but the
  EncDecMultiTalkerRNNTBPE architecture may not expose the same biasing hooks as parakeet-tdt.
  Entity accuracy at 31.88% (domain vocab) is significantly below the Granite baseline
  (97.1%), suggesting biasing was ineffective or absent. Further investigation is needed to
  confirm whether TurboBias applies to multitalker inference.

* **`_transcribe_forward` patch enables single-speaker inference.** The model expects
  multi-speaker speaker-target tensors. The patch allows it to run on single-speaker clips
  without crashing, but may not be optimal for single-speaker audio — the model may internally
  try to separate speakers in audio that has only one.

* **No empty transcripts or hallucinations.** Across all 279 records, zero clips produced
  empty output and zero were flagged as hallucinations. This is a positive reliability signal:
  the model never refuses to produce output and does not confabulate speech on silent or
  near-silent segments.

## Summary

The multitalker-parakeet-streaming-0.6b-v1 model achieves WER of 13.34% on gold-92, entity
accuracy of 22.19%, and domain-vocab entity accuracy of 31.88% — all invariant to buffer
extraction interval. TTFD p50 is 64ms and end-to-end latency p50 ranges from 242ms (1000ms
interval) to 254ms (500ms interval). The model produces no empty transcripts and no
hallucinations across all 279 clip-interval combinations.

The primary limitation is entity accuracy on domain vocabulary: at 31.88% vs the Granite
baseline of 97.1%, the model misses roughly two-thirds of domain-specific entities. This is
likely attributable to ineffective or unsupported TurboBias biasing on the multitalker
architecture. Until biasing is confirmed to work, the multitalker model is not suitable for
production deployment in Rezolve's investor-relations STT pipeline despite its competitive
streaming latency characteristics.

The buffer interval sweep confirms that 1000ms is the optimal operating point for this model:
lowest latency (242ms p50) with identical transcription quality to shorter intervals.

</details>

<details>
<summary>📊 <strong>Parakeet TDT 0.6b-v3 Buffer Interval Sweep on gold-92</strong>
(<code>parakeet-tdt-buffer-sweep</code>) — 279 instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-tdt-buffer-sweep` |
| **Model ID** | — |
| **Model** | nvidia/parakeet-tdt-0.6b-v3 (NeMo ASR, CTC-Attention hybrid, 0.6B params) with GPU-PB TurboBias boosting using Rezolve 31-term domain vocabulary, alpha=1.0. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 279 |
| **Date created** | 2026-07-01 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Documentation** | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-tdt-buffer-sweep/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.1525
* **entity_accuracy_gold92**: 0.2281
* **entity_accuracy_domain_vocab**: 0.3333
* **latency_p50_seconds_500ms**: 0.256
* **latency_p50_seconds_750ms**: 0.254
* **latency_p50_seconds_1000ms**: 0.25
* **ttfd_p50_seconds**: 0.032

## Metadata

- **Model:** nvidia/parakeet-tdt-0.6b-v3 with GPU-PB TurboBias domain biasing
- **Task:** t0015_streaming_buffer_interval
- **Dataset:** stt-benchmark-gold-92 (93 clips, 279 total prediction records across 3
  intervals)
- **Inference:** NeMo ASR streaming mode, GPU inference, Azure H100 NVL
- **Intervals Tested:** 500ms, 750ms, 1000ms buffer extraction intervals
- **Date:** 2026-07-01

## Overview

This asset contains per-clip predictions from nvidia/parakeet-tdt-0.6b-v3 (Token-and-Duration
Transducer, 0.6B parameters) across a sweep of three streaming buffer extraction intervals:
500ms, 750ms, and 1000ms. The experiment is part of a broader benchmark covering 4 models × 3
intervals = 12 combinations; this asset covers only the parakeet-tdt model.

In true streaming STT, audio is captured continuously and the model must decide when to
extract a partial or final transcript from the accumulated PCM buffer. The buffer extraction
interval controls how often the accumulated 16kHz mono PCM-16 audio is sent to the model for
inference during an active streaming session. A shorter interval means more frequent model
calls and lower TTFD (time to first decode), but potentially more redundant computation. A
longer interval batches more audio before each inference call, improving GPU utilization but
adding initial silence before the first output token appears.

Each of the 93 gold-92 clips was processed at each of the three intervals, yielding 279 total
records (93 × 3). Because the final transcript is computed from the complete audio regardless
of interval, WER and entity accuracy are identical across all three conditions — interval
affects only the streaming latency profile and TTFD.

GPU-PB TurboBias domain biasing is applied at every inference call using Rezolve's 31-term
domain vocabulary (brand names, product terms, financial entities relevant to
investor-relations sessions). Boosting alpha is set to 1.0.

## Model

- **HuggingFace ID:** nvidia/parakeet-tdt-0.6b-v3
- **Architecture:** Token-and-Duration Transducer (TDT), CTC-Attention hybrid decoder, 0.6B
  params
- **Framework:** NVIDIA NeMo / Riva SDK
- **Hardware:** Azure H100 NVL (GPU)
- **Biasing:** NeMo GPU-PB TurboBias phrase boosting, 31-term Rezolve domain vocabulary,
  alpha=1.0
- **Streaming mode:** Buffer extraction at configurable intervals (500ms, 750ms, 1000ms
  tested)

Parakeet TDT v3 is NVIDIA's production ASR model optimized for low-latency streaming
inference. The TDT architecture emits token predictions along with token duration estimates,
enabling word-level timestamp output without a separate forced-alignment pass. Under streaming
operation, the model maintains an internal RNN-T state across chunks, allowing efficient
incremental processing of incoming audio buffers.

## Data

The gold-92 benchmark consists of 93 WAV clips sourced from Rezolve production
investor-relations sessions. All clips are 16kHz mono, PCM-16 format, with durations ranging
from approximately 2s to 15s (mean ~6.7s). The domain is accented English with heavy use of
financial and investor-relations terminology (earnings, revenue, guidance, product names,
etc.).

Gold-92 is a held-out regression set — it is never used for training or fine-tuning. Clip
`error_en_0005` has Cyrillic ground truth and is excluded from entity accuracy aggregates but
included in WER computation. Many clips have no reference_text annotation, which suppresses
entity accuracy scores for those clips (they contribute 0/0 and are excluded from the
denominator).

## Prediction Format

Each JSONL file contains 93 records (one per clip). Fields per record:

- `clip_id` (string): unique clip identifier, e.g. `en_0001`
- `duration_s` (float): audio duration in seconds
- `transcript` (string): final parakeet-tdt hypothesis for the full clip
- `reference_text` (string): ground-truth transcript (may be empty string if not annotated)
- `is_empty` (bool): true if transcript is empty string or whitespace-only
- `is_hallucination` (bool): true if transcript contains content not present in source audio
- `ttfd_seconds` (float): time from streaming start to first non-empty output token (seconds)
- `latency_seconds` (float): total wall-clock time from first chunk delivery to final
  transcript
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
(32ms vs 77ms) is substantial but does not compensate for the accuracy gap in
investor-relations use cases where entity precision is critical.

Entity accuracy is low (22.81% / 33.33%) primarily because many gold-92 clips have no
reference_text annotation, causing them to contribute nothing to the numerator. The
domain-vocab metric (EA-DV = 33.33%) uses only clips where the reference text contains at
least one of the 31 domain vocabulary terms.

Three empty transcripts were observed (3/93 = 3.2% empty rate). No hallucinations detected
across all 279 records.

## Main Ideas

* **Buffer interval has no effect on accuracy.** WER, entity accuracy, and hallucination rate
  are identical at 500ms, 750ms, and 1000ms. The final transcript is determined by the
  complete audio signal, not by how many intermediate buffer extractions occurred.

* **Latency decreases slightly at larger intervals.** Parakeet p50 latency drops from 256ms
  (500ms interval) to 250ms (1000ms interval) — a 6ms improvement. This is consistent with
  reduced inference overhead from fewer model calls per clip. However, the effect is small
  relative to typical voice-to-action latency budgets (~800ms).

* **TTFD is very fast and interval-independent.** At 32ms p50 across all intervals,
  parakeet-tdt produces its first output token extremely quickly — well below the 77ms
  observed for Granite's accumulate-then-transcribe baseline. This makes parakeet attractive
  for use cases where streaming visual feedback (live transcript display) matters more than
  final accuracy.

* **WER 15.25% is materially higher than Granite (8.8%).** For investor-relations sessions
  where entity precision drives downstream action accuracy, this gap is significant. Domain
  vocabulary biasing at alpha=1.0 raises EA-DV to 33.33% but still far below Granite's 97.1%.

* **Practical implication: choose interval based on compute budget.** Since accuracy is
  unaffected, the optimal interval is determined by GPU utilization goals: larger intervals
  reduce inference calls per session, lowering GPU cost, with a marginal latency benefit.

## Summary

Parakeet TDT 0.6b-v3 with GPU-PB TurboBias was evaluated across three streaming buffer
extraction intervals (500ms, 750ms, 1000ms) on the gold-92 benchmark (93 clips). Accuracy
metrics (WER 15.25%, EA 22.81%, EA-DV 33.33%) are identical across all intervals, confirming
that buffer extraction frequency does not affect transcript quality. Latency decreases
marginally with larger intervals (256ms → 250ms p50), and TTFD remains a consistent 32ms
across all conditions. The model produces zero hallucinations and 3 empty transcripts.

Compared to the Granite accumulate-then-transcribe baseline (WER 8.8%, EA-DV 97.1%, TTFD
77ms), parakeet offers significantly faster TTFD but substantially lower accuracy on this
investor-relations domain, making it better suited to low-latency display use cases than
high-precision action routing. The buffer interval parameter does not change this conclusion —
any of the three tested intervals yields the same accuracy result.

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
<summary>📊 <strong>Parakeet Unified EN 0.6b Buffer Interval Sweep on
gold-92</strong> (<code>parakeet-unified-buffer-sweep</code>) — 279
instances (jsonl)</summary>

| Field | Value |
|---|---|
| **ID** | `parakeet-unified-buffer-sweep` |
| **Model ID** | — |
| **Model** | nvidia/parakeet-unified-en-0.6b (NeMo unified ASR, 0.6B params) with GPU-PB TurboBias boosting using Rezolve 31-term domain vocabulary, alpha=1.0. |
| **Datasets** | `stt-benchmark-gold-92` |
| **Format** | jsonl |
| **Instances** | 279 |
| **Date created** | 2026-07-01 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Created by** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Documentation** | [`description.md`](../../../tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-unified-buffer-sweep/description.md) |

**Metrics at creation:**

* **wer_gold92**: 0.0953
* **entity_accuracy_gold92**: 0.2344
* **entity_accuracy_domain_vocab**: 0.3478
* **latency_p50_seconds_500ms**: 0.378
* **latency_p50_seconds_750ms**: 0.358
* **latency_p50_seconds_1000ms**: 0.35
* **ttfd_p50_seconds**: 0.037

## Metadata

| Field | Value |
|---|---|
| Predictions ID | parakeet-unified-buffer-sweep |
| Task | t0015_streaming_buffer_interval |
| Dataset | stt-benchmark-gold-92 (gold-92) |
| Instance count | 279 (93 clips × 3 intervals) |
| Date created | 2026-07-01 |
| Model | nvidia/parakeet-unified-en-0.6b |
| Biasing | GPU-PB TurboBias, 31-term Rezolve domain vocabulary, alpha=1.0 |
| Intervals tested | 500ms, 750ms, 1000ms |

## Overview

This asset contains per-clip streaming ASR predictions produced by
`nvidia/parakeet-unified-en-0.6b` under three buffer extraction intervals: 500ms, 750ms, and
1000ms. It is one of four model variants evaluated in task `t0015_streaming_buffer_interval`,
which benchmarks the effect of the streaming buffer interval parameter on transcription
quality (WER, entity accuracy) and latency metrics (TTFD, end-to-end latency).

The full experimental matrix for task t0015 spans 4 model variants × 3 interval settings = 12
combinations. The four models are parakeet-tdt, parakeet-unified, granite-speech, and a
non-streaming reference. This asset covers the **parakeet-unified** variant across all three
intervals.

The buffer interval controls how often accumulated PCM-16 audio is flushed from the
client-side ring buffer and sent to the NeMo inference server. Shorter intervals mean more
frequent, smaller inference calls; longer intervals mean fewer but larger inference calls. The
trade-off is between latency responsiveness (shorter intervals give lower TTFD) and compute
efficiency (longer intervals reduce per-sample overhead and may improve throughput). In
streaming deployment scenarios, the optimal interval depends on the latency budget and server
capacity.

All three interval files are provided in this asset so that downstream evaluations can compare
how the same model behaves under different streaming configurations without rerunning
inference.

## Model

**Model:** `nvidia/parakeet-unified-en-0.6b`

Parakeet-Unified is NVIDIA's NeMo-based unified ASR model with 0.6 billion parameters. The
"unified" architecture processes audio through a shared encoder/decoder that handles both CTC
and attention-based decoding in a single forward pass. Compared to the Parakeet-TDT
(Token-and-Duration Transducer) variant, the unified model uses a slightly different decoding
path that can introduce marginally higher latency per inference call (observed as ~20–28ms
higher p50 latency than TDT across equivalent intervals).

**Domain biasing:** GPU-PB TurboBias is applied using NeMo's `boosting_tree` mechanism. A
31-term Rezolve-specific vocabulary is provided as the boost vocabulary, with `alpha=1.0`.
This biasing technique re-scores beam hypothesis tokens that match the boost vocabulary terms,
improving recall of domain-specific entities such as product names, company identifiers, and
financial terms relevant to investor-relations dialogues. The biasing is applied at inference
time and does not require model fine-tuning.

**Inference stack:** NeMo RNNT streaming inference with chunk-based audio delivery, running on
GPU. The model receives chunks of PCM-16 audio at 16kHz mono, accumulates them in a rolling
buffer, and produces incremental transcript hypotheses. The final transcript is taken from the
last hypothesis after all audio has been delivered.

## Data

**Dataset:** `stt-benchmark-gold-92` (alias: gold-92)

- 93 WAV audio clips, 16kHz mono
- Domain: investor-relations — earnings calls, analyst Q&A, financial briefings
- Language: English with varied accents (including accented English from non-native speakers)
- Reference transcripts: available for a subset of clips; clips without reference transcripts
  are excluded from WER and entity accuracy computations but are included in latency
  measurements
- Clip duration: short to medium length (typical range 3–30s)

The gold-92 dataset is the primary benchmark used across the rail-arf-stt project for
comparing STT model quality. It is deliberately representative of Rezolve's production traffic
domain rather than general speech benchmarks. This domain focus means that models trained on
general speech (e.g., LibriSpeech or VoxPopuli) tend to underperform on investor-relations
jargon, and domain biasing is particularly valuable.

**Instance count:** 279 total records (93 clips × 3 interval settings). Each file contains 93
records corresponding to the same 93 clips evaluated at one specific buffer interval.

## Prediction Format

Each JSONL file contains one JSON object per line. The fields are:

| Field | Type | Description |
|---|---|---|
| `clip_id` | string | Unique clip identifier, matching the gold-92 dataset |
| `duration_s` | float | Audio clip duration in seconds |
| `transcript` | string | Final ASR transcript produced by the model |
| `reference_text` | string | Ground-truth reference transcript (empty string if unavailable) |
| `is_empty` | bool | True if transcript is empty or whitespace-only |
| `is_hallucination` | bool | True if transcript is flagged as a hallucination (detected via heuristic rules) |
| `ttfd_seconds` | float | Time-to-first-decode: elapsed time from audio start until first non-empty hypothesis |
| `latency_seconds` | float | End-to-end latency from audio start to final transcript delivery |
| `interval_ms` | int | Buffer extraction interval used (500, 750, or 1000) |
| `n_chunks` | int | Number of audio chunks sent to the model |
| `n_inferences` | int | Number of inference calls made to the NeMo server |

Files are named `predictions-gold92-{interval}ms.jsonl` where `{interval}` is 500, 750, or
1000.

## Metrics

Metrics reported at creation time (aggregated across all 93 clips with available references):

| Metric | Value | Notes |
|---|---|---|
| WER (gold-92) | 9.53% | Word Error Rate; same across all intervals (identical final transcripts) |
| Entity Accuracy (heuristic) | 23.44% | Pattern-based entity match; low due to partial reference coverage |
| Entity Accuracy — Domain Vocab (EA-DV) | 34.78% | Restricted to Rezolve 31-term domain vocabulary |
| Latency p50 (500ms interval) | 0.378s | End-to-end latency median |
| Latency p50 (750ms interval) | 0.358s | End-to-end latency median |
| Latency p50 (1000ms interval) | 0.350s | End-to-end latency median |
| TTFD p50 (all intervals) | 0.037s | Time-to-first-decode; 37ms across all interval settings |
| Empty transcripts | 0 | No clips produced empty output |
| Hallucinations | 0 | No clips flagged as hallucinations |

**WER is identical across intervals** because the final transcript is determined by the last
inference on the complete audio buffer. The buffer interval affects when intermediate
hypotheses are emitted (and therefore TTFD and latency), but does not change what the model
produces as its final answer over the full clip.

**Latency decreases slightly at larger intervals.** At 500ms, p50 latency is 378ms; at 1000ms
it drops to 350ms. This reflects reduced per-call overhead when fewer, larger inference calls
are made. The trade-off is that streaming responsiveness decreases (longer pauses before first
output).

**TTFD is uniformly low (37ms p50).** This indicates the model begins producing output very
quickly after audio delivery starts, regardless of the buffer interval. TTFD is not strongly
affected by interval size in this regime because the first chunk is delivered promptly.

**Comparison to baseline:** The Granite accumulate-then-transcribe baseline (non-streaming)
achieves WER 8.8% and EA-DV 97.1% but TTFD p50 of 77ms — twice the TTFD of parakeet-unified.
Parakeet-unified trades approximately 0.73 percentage points of WER for 40ms improvement in
TTFD and true streaming capability. EA-DV is substantially lower (34.78% vs 97.1%) primarily
because reference texts are incomplete for many clips, making the entity accuracy metric
unreliable for direct comparison.

## Main Ideas

* **Buffer interval has negligible effect on transcript quality.** Since the model processes
  the full audio before committing its final transcript, varying the extraction interval from
  500ms to 1000ms produces identical WER and entity accuracy. Quality tuning should focus on
  model selection and biasing configuration, not buffer interval.
* **Buffer interval moderately affects end-to-end latency.** Larger intervals reduce the
  number of inference calls, lowering per-clip latency by ~28ms (p50) from 500ms to 1000ms.
  For latency-sensitive deployments, the 1000ms interval is preferred unless streaming
  responsiveness (TTFD) is a primary concern.
* **Parakeet-unified shows slightly higher WER than parakeet-tdt.** At 9.53%, it is slightly
  worse than the TDT variant. This is consistent with the architectural difference: the
  unified model's joint CTC/attention decoding can introduce more errors on short or accented
  clips than the transducer-based TDT.
* **GPU-PB TurboBias provides meaningful domain vocabulary recall improvement.** EA-DV of
  34.78% represents the biasing contribution to domain term recognition, achieved without any
  model fine-tuning. The biasing is applied purely at decoding time via NeMo's boosting_tree.
* **No quality robustness issues detected.** Zero empty transcripts and zero hallucinations
  across 93 clips and 3 intervals (279 total inferences) confirms that parakeet-unified is
  stable on this dataset under streaming conditions.

## Summary

The parakeet-unified-buffer-sweep asset provides streaming ASR predictions from
`nvidia/parakeet-unified-en-0.6b` on the gold-92 benchmark at three buffer extraction
intervals (500ms, 750ms, 1000ms). With WER of 9.53% and TTFD p50 of 37ms, parakeet-unified
delivers fast streaming response but slightly higher WER than the TDT variant. Larger buffer
intervals reduce end-to-end latency by ~28ms (p50) with no quality trade-off. The 31-term
GPU-PB TurboBias domain vocabulary boosts entity recall to 34.78% EA-DV without model
fine-tuning.

This asset covers one of four model variants in the t0015 buffer interval sweep experiment (4
models × 3 intervals = 12 combinations), enabling direct comparison of streaming configuration
effects across the full model family. The key finding is that buffer interval is a
latency-only knob: it does not affect transcription quality but can reduce end-to-end latency
by up to ~28ms when set to 1000ms versus 500ms. Teams optimising for TTFD should prefer
shorter intervals; teams optimising for throughput and latency should prefer longer ones.

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
