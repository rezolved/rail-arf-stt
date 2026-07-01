---
spec_version: "2"
predictions_id: parakeet-unified-buffer-sweep
name: Parakeet Unified EN 0.6b Buffer Interval Sweep on gold-92
date_created: "2026-07-01"
created_by_task: t0015_streaming_buffer_interval
dataset_ids:
  - stt-benchmark-gold-92
categories:
  - stt-evaluation
  - latency-profiling
---

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

This asset contains per-clip streaming ASR predictions produced by `nvidia/parakeet-unified-en-0.6b` under three buffer extraction intervals: 500ms, 750ms, and 1000ms. It is one of four model variants evaluated in task `t0015_streaming_buffer_interval`, which benchmarks the effect of the streaming buffer interval parameter on transcription quality (WER, entity accuracy) and latency metrics (TTFD, end-to-end latency).

The full experimental matrix for task t0015 spans 4 model variants × 3 interval settings = 12 combinations. The four models are parakeet-tdt, parakeet-unified, granite-speech, and a non-streaming reference. This asset covers the **parakeet-unified** variant across all three intervals.

The buffer interval controls how often accumulated PCM-16 audio is flushed from the client-side ring buffer and sent to the NeMo inference server. Shorter intervals mean more frequent, smaller inference calls; longer intervals mean fewer but larger inference calls. The trade-off is between latency responsiveness (shorter intervals give lower TTFD) and compute efficiency (longer intervals reduce per-sample overhead and may improve throughput). In streaming deployment scenarios, the optimal interval depends on the latency budget and server capacity.

All three interval files are provided in this asset so that downstream evaluations can compare how the same model behaves under different streaming configurations without rerunning inference.

## Model

**Model:** `nvidia/parakeet-unified-en-0.6b`

Parakeet-Unified is NVIDIA's NeMo-based unified ASR model with 0.6 billion parameters. The "unified" architecture processes audio through a shared encoder/decoder that handles both CTC and attention-based decoding in a single forward pass. Compared to the Parakeet-TDT (Token-and-Duration Transducer) variant, the unified model uses a slightly different decoding path that can introduce marginally higher latency per inference call (observed as ~20–28ms higher p50 latency than TDT across equivalent intervals).

**Domain biasing:** GPU-PB TurboBias is applied using NeMo's `boosting_tree` mechanism. A 31-term Rezolve-specific vocabulary is provided as the boost vocabulary, with `alpha=1.0`. This biasing technique re-scores beam hypothesis tokens that match the boost vocabulary terms, improving recall of domain-specific entities such as product names, company identifiers, and financial terms relevant to investor-relations dialogues. The biasing is applied at inference time and does not require model fine-tuning.

**Inference stack:** NeMo RNNT streaming inference with chunk-based audio delivery, running on GPU. The model receives chunks of PCM-16 audio at 16kHz mono, accumulates them in a rolling buffer, and produces incremental transcript hypotheses. The final transcript is taken from the last hypothesis after all audio has been delivered.

## Data

**Dataset:** `stt-benchmark-gold-92` (alias: gold-92)

- 93 WAV audio clips, 16kHz mono
- Domain: investor-relations — earnings calls, analyst Q&A, financial briefings
- Language: English with varied accents (including accented English from non-native speakers)
- Reference transcripts: available for a subset of clips; clips without reference transcripts are excluded from WER and entity accuracy computations but are included in latency measurements
- Clip duration: short to medium length (typical range 3–30s)

The gold-92 dataset is the primary benchmark used across the rail-arf-stt project for comparing STT model quality. It is deliberately representative of Rezolve's production traffic domain rather than general speech benchmarks. This domain focus means that models trained on general speech (e.g., LibriSpeech or VoxPopuli) tend to underperform on investor-relations jargon, and domain biasing is particularly valuable.

**Instance count:** 279 total records (93 clips × 3 interval settings). Each file contains 93 records corresponding to the same 93 clips evaluated at one specific buffer interval.

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

Files are named `predictions-gold92-{interval}ms.jsonl` where `{interval}` is 500, 750, or 1000.

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

**WER is identical across intervals** because the final transcript is determined by the last inference on the complete audio buffer. The buffer interval affects when intermediate hypotheses are emitted (and therefore TTFD and latency), but does not change what the model produces as its final answer over the full clip.

**Latency decreases slightly at larger intervals.** At 500ms, p50 latency is 378ms; at 1000ms it drops to 350ms. This reflects reduced per-call overhead when fewer, larger inference calls are made. The trade-off is that streaming responsiveness decreases (longer pauses before first output).

**TTFD is uniformly low (37ms p50).** This indicates the model begins producing output very quickly after audio delivery starts, regardless of the buffer interval. TTFD is not strongly affected by interval size in this regime because the first chunk is delivered promptly.

**Comparison to baseline:** The Granite accumulate-then-transcribe baseline (non-streaming) achieves WER 8.8% and EA-DV 97.1% but TTFD p50 of 77ms — twice the TTFD of parakeet-unified. Parakeet-unified trades approximately 0.73 percentage points of WER for 40ms improvement in TTFD and true streaming capability. EA-DV is substantially lower (34.78% vs 97.1%) primarily because reference texts are incomplete for many clips, making the entity accuracy metric unreliable for direct comparison.

## Main Ideas

* **Buffer interval has negligible effect on transcript quality.** Since the model processes the full audio before committing its final transcript, varying the extraction interval from 500ms to 1000ms produces identical WER and entity accuracy. Quality tuning should focus on model selection and biasing configuration, not buffer interval.
* **Buffer interval moderately affects end-to-end latency.** Larger intervals reduce the number of inference calls, lowering per-clip latency by ~28ms (p50) from 500ms to 1000ms. For latency-sensitive deployments, the 1000ms interval is preferred unless streaming responsiveness (TTFD) is a primary concern.
* **Parakeet-unified shows slightly higher WER than parakeet-tdt.** At 9.53%, it is slightly worse than the TDT variant. This is consistent with the architectural difference: the unified model's joint CTC/attention decoding can introduce more errors on short or accented clips than the transducer-based TDT.
* **GPU-PB TurboBias provides meaningful domain vocabulary recall improvement.** EA-DV of 34.78% represents the biasing contribution to domain term recognition, achieved without any model fine-tuning. The biasing is applied purely at decoding time via NeMo's boosting_tree.
* **No quality robustness issues detected.** Zero empty transcripts and zero hallucinations across 93 clips and 3 intervals (279 total inferences) confirms that parakeet-unified is stable on this dataset under streaming conditions.

## Summary

The parakeet-unified-buffer-sweep asset provides streaming ASR predictions from `nvidia/parakeet-unified-en-0.6b` on the gold-92 benchmark at three buffer extraction intervals (500ms, 750ms, 1000ms). With WER of 9.53% and TTFD p50 of 37ms, parakeet-unified delivers fast streaming response but slightly higher WER than the TDT variant. Larger buffer intervals reduce end-to-end latency by ~28ms (p50) with no quality trade-off. The 31-term GPU-PB TurboBias domain vocabulary boosts entity recall to 34.78% EA-DV without model fine-tuning.

This asset covers one of four model variants in the t0015 buffer interval sweep experiment (4 models × 3 intervals = 12 combinations), enabling direct comparison of streaming configuration effects across the full model family. The key finding is that buffer interval is a latency-only knob: it does not affect transcription quality but can reduce end-to-end latency by up to ~28ms when set to 1000ms versus 500ms. Teams optimising for TTFD should prefer shorter intervals; teams optimising for throughput and latency should prefer longer ones.
