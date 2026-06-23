---
spec_version: "3"
paper_id: "10.48550_arXiv.2602.12241"
citation_key: "Kudlur2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical Speech Applications

## Metadata

* **File**: `files/kudlur_2026_moonshine-v2-streaming-asr.pdf`
* **Published**: 2026
* **Authors**: Manjunath Kudlur 🇺🇸, Evan King 🇺🇸, James Wang 🇺🇸, Pete Warden 🇺🇸
* **Venue**: arXiv preprint (Useful Sensors)
* **DOI**: `10.48550/arXiv.2602.12241`

## Abstract

Moonshine v2 introduces an ergodic streaming encoder for ASR using sliding-window self-attention to
achieve bounded, low-latency inference while maintaining strong contextual understanding. The models
(Tiny: 33.57M, Small: 123.36M, Medium: 244.93M parameters) achieve state-of-the-art word error rates
on standard benchmarks while running significantly faster than comparably accurate models. On Apple
M3, the Medium model achieves 258ms latency at 28.95% compute load, while Tiny achieves 50ms at
8.03% compute load. The Medium model runs 43.7x faster than Whisper Large v3 at comparable accuracy.

## Overview

Moonshine v2 solves a fundamental problem in streaming ASR: standard transformer encoders require
processing the full utterance before producing output, creating latency proportional to utterance
length. The paper introduces an "ergodic" encoder design using sliding-window self-attention that
processes audio in fixed-size windows with bounded memory and constant-time per-step computation.

The key architectural insight is that sliding-window self-attention provides each frame with a fixed
receptive field regardless of utterance position. This makes the encoder stateless in the sense that
processing cost per audio chunk is fixed, enabling true real-time streaming. Unlike chunked or
CIF-based approaches that require special handling of chunk boundaries, the ergodic encoder
maintains a clean mathematical guarantee: the time-to-first-token and per-chunk processing time are
both bounded.

The paper focuses on on-device deployment, specifically targeting Apple Silicon. The competitive
benchmarking demonstrates that Moonshine v2 Medium achieves 6.65% average WER on the Open ASR
leaderboard — within 1-2 WER points of much larger models like Whisper Large v3 — while running
43.7× faster on the same hardware.

## Architecture, Models and Methods

Three model variants: Tiny (33.57M parameters), Small (123.36M), Medium (244.93M). All share the
ergodic encoder with sliding-window self-attention; the decoder is a standard autoregressive
transformer.

Sliding window size and overlap were tuned per model size. The encoder processes fixed-length audio
chunks with a fixed-width attention window, producing frame-level representations that are fed to
the decoder. The "ergodic" property refers to the statistical equivalence of time-averaged and
ensemble-averaged encoder representations under stationary assumptions — this ensures that the
chunk-by-chunk processing matches the quality of full-utterance processing asymptotically.

Evaluation uses the Open ASR Leaderboard benchmark suite. Hardware profiling is reported on Apple
M3. Latency is defined as wall-clock time from audio end to first decoded token.

## Results

* Tiny WER: **12.01%** average across Open ASR benchmarks
* Small WER: **7.84%** average
* Medium WER: **6.65%** average
* LibriSpeech test-clean (Medium): **2.08%** WER
* Earnings-22 (Tiny, domain-specific): **20.27%** WER
* Moonshine v2 Tiny latency (Apple M3): **50ms**, **8.03%** compute load
* Moonshine v2 Small latency (Apple M3): **148ms**, **17.97%** compute load
* Moonshine v2 Medium latency (Apple M3): **258ms**, **28.95%** compute load
* Speed advantage: v2 Medium is **43.7×** faster than Whisper Large v3
* Accuracy/size ratio: achieves accuracy comparable to models **6× larger**

## Innovations

### Ergodic Streaming Encoder

Sliding-window self-attention with a stationary per-chunk computational budget. Unlike prior
streaming methods that require special boundary handling or multi-pass decoding, the ergodic encoder
provides a clean bounded-latency guarantee.

### On-Device Latency Benchmarking

First systematic latency measurement of a streaming ASR model on Apple Silicon M3, providing
reference numbers directly relevant to voice assistant deployment on consumer hardware.

## Datasets

* **Open ASR Leaderboard**: composite benchmark including LibriSpeech, Earnings-22, and other test
  sets; public; English
* **LibriSpeech**: standard clean/other splits; well-known WER reference

## Main Ideas

* 50ms (Tiny) to 258ms (Medium) ASR latency on Apple M3 is well within the Rezolve 800ms p50 budget,
  leaving 542-750ms for downstream processing, post-correction, and routing
* The accuracy-vs-latency Pareto: Moonshine v2 Small (148ms, 7.84% WER) may be the best operating
  point for Rezolve's real-time pipeline — lower latency than Medium with only 1.2pp WER penalty
* The ergodic encoder architecture is a viable drop-in streaming replacement for Whisper Turbo with
  similar model sizes and significantly lower latency
* No entity-specific evaluation is reported; entity accuracy on domain-specific ecommerce terms
  would need separate assessment before adopting Moonshine for production

## Summary

Moonshine v2 addresses latency in on-device ASR through an ergodic streaming encoder that processes
audio in fixed-size chunks with bounded per-chunk computation. The motivation is that standard
transformer encoders block on full-utterance processing, creating latency proportional to utterance
length that is unacceptable for real-time voice assistants.

The architecture uses sliding-window self-attention to provide each audio frame a fixed receptive
field, enabling stateless chunk-by-chunk processing. Three model sizes (Tiny, Small, Medium) are
provided, all using the same encoder design with varying capacity. The decoder remains a standard
autoregressive transformer.

Measured on Apple M3, the Tiny model achieves **50ms** latency at **8.03%** compute load while the
Medium achieves **258ms** at **28.95%** load. Average WER ranges from **12.01%** (Tiny) to **6.65%**
(Medium) on the Open ASR leaderboard. The Medium model is **43.7×** faster than Whisper Large v3 at
1-2pp WER penalty.

For Rezolve's pipeline, Moonshine v2 represents a viable low-latency streaming ASR alternative that
fits comfortably within the 800ms p50 budget. The Small variant (148ms, 7.84% WER) is the most
promising trade-off point. However, no entity-level accuracy data is reported; domain-specific
evaluation on ecommerce entities is a prerequisite before production adoption.
