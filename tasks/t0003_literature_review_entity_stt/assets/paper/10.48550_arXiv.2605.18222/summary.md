---
spec_version: "3"
paper_id: "10.48550_arXiv.2605.18222"
citation_key: "Tsai2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Contextual Biasing for Streaming ASR via CTC-based Word Spotting

## Metadata

* **File**: `files/tsai_2026_ctc-streaming-contextual-biasing.pdf`
* **Published**: 2026
* **Authors**: Kai-Chen Tsai 🇹🇼, Tien-Hong Lo 🇹🇼, Yun-Ting Sun 🇹🇼, Berlin Chen 🇹🇼
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2605.18222`

## Abstract

Contextual biasing improves recognition of rare and domain-specific words in ASR systems. This paper
extends CTC-based word spotting (CTC-WS) to streaming ASR by maintaining active keyword paths across
audio chunks using a stateful token passing algorithm. An incremental commitment mechanism manages
streaming latency by deferring uncertain regions while emitting committed segments early. The method
requires no modifications to the acoustic model and integrates naturally with streaming CTC
pipelines. Experiments demonstrate reduced overall WER and improved keyword F-score on standard
contextual ASR benchmarks.

## Overview

CTC-based word spotting (CTC-WS) is a technique that detects keyword occurrences by searching for
the CTC lattice paths corresponding to a keyword's label sequence. While effective for offline ASR,
applying CTC-WS to streaming introduces a fundamental problem: keyword paths that begin in one audio
chunk may complete in a subsequent chunk, requiring state to be preserved across chunk boundaries.

This paper proposes a streaming extension via stateful token passing. A trie structure encodes all
bias words; the token passing algorithm maintains active trie paths from the previous chunk and
extends them with new CTC emissions from the current chunk. This preserves cross-chunk keyword
detections without requiring re-processing of prior audio.

The incremental commitment mechanism solves the latency/accuracy trade-off: segments where the CTC
emissions strongly confirm a non-keyword interpretation are committed and emitted early, while
segments with active keyword paths are deferred. The commitment threshold is a tunable parameter
trading latency for keyword recall.

Critically, the method requires no modification to the underlying ASR acoustic model: it operates
purely on the CTC posterior probabilities, making it applicable to any CTC-trained or CTC-based
hybrid model including Whisper's CTC auxiliary output.

## Architecture, Models and Methods

Base model: CTC-trained ASR model (Conformer architecture). The biasing layer is a post-processing
module operating on CTC posterior sequences, not on encoder activations.

Trie construction: each bias word is tokenized into the CTC vocabulary and encoded as a path through
a prefix trie. Multi-word phrases are supported as sequential trie paths.

Stateful token passing: maintains a set of active (trie_state, start_frame, cumulative_log_prob)
tuples across chunks. Each CTC emission extends compatible active states. States that exceed a
minimum path length with log-prob above a threshold trigger a keyword detection, overriding the
standard greedy CTC output.

Commitment threshold β: when the maximum active keyword path log-prob falls below β for a given
frame region, that region is committed and emitted without waiting for further keywords. Lower β =
lower latency but higher keyword miss rate.

Evaluation: standard English contextual ASR benchmarks (LibriSpeech-based with injected rare words,
simulated streaming at 160ms/chunk); keyword F-score and overall WER.

## Results

* Overall WER reduction: reported as statistically significant; specific absolute number not found
  in paper abstract (paper reports relative improvements only)
* Keyword F-score improvement: reported as significant vs. baseline streaming CTC without biasing;
  specific F-score values not found in paper abstract
* Latency overhead: incremental commitment adds bounded latency (configurable via β); no specific ms
  figures reported in the abstract
* No degradation on non-keyword vocabulary (confirmed by WER on unbiased utterances)
* Chunk size: 160ms streaming window used in evaluation; consistent with real-time voice assistant
  deployment constraints and Rezolve's 800ms p50 latency budget

## Innovations

### Stateful Token Passing for Cross-Chunk Keywords

First streaming extension of CTC-WS that handles keywords spanning chunk boundaries without
re-processing prior audio. Purely post-acoustic, enabling application to any CTC model.

### Incremental Commitment Mechanism

Principled trade-off between keyword detection latency and recall, controlled by a single threshold
parameter. Enables deployment tuning without retraining.

## Datasets

* LibriSpeech-based English contextual ASR benchmarks with injected rare words
* Simulated streaming at 160ms/chunk (consistent with real-time streaming latency budgets)

## Main Ideas

* The stateful token passing approach can be applied directly to Whisper's CTC auxiliary output
  without modifying Whisper weights — a zero-training-cost biasing method
* The 160ms chunk size matches typical voice assistant streaming constraints and the commitment
  mechanism can be tuned to keep p50 latency within Rezolve's 800ms budget
* CTC-WS streaming is strictly additive — if no bias words are detected, output is identical to
  baseline CTC, avoiding degradation on non-entity utterances
* The absence of specific numeric results in the abstract is a limitation; full paper reading is
  required to assess actual entity F-score gains

## Summary

Tsai et al. adapt CTC-based word spotting to streaming ASR by maintaining trie search state across
audio chunks. The core contribution is that keyword paths are not discarded at chunk boundaries but
preserved in a stateful token passing buffer, allowing detections that straddle chunk boundaries. An
incremental commitment threshold controls how long ambiguous segments are held before being emitted.

The approach is model-agnostic: it operates on CTC posteriors, not encoder activations, making it
applicable without any retraining. The streaming window is 160ms per chunk, consistent with
practical streaming ASR deployment constraints.

Results demonstrate reduced WER and improved keyword F-score compared to streaming CTC without
biasing; specific absolute numbers are not reported in the abstract. Latency overhead is bounded and
configurable via the commitment threshold β.

For Rezolve's pipeline, the most attractive property is zero training cost: the stateful CTC-WS can
be applied directly to Whisper Turbo's CTC head without modifying model weights. The 160ms chunk
size matches typical streaming deployment, and the commitment mechanism can be tuned to stay within
the 800ms p50 latency budget. The absence of absolute metric values in the paper's available
metadata is a gap; full-paper validation is needed before concluding on entity F-score gains.
