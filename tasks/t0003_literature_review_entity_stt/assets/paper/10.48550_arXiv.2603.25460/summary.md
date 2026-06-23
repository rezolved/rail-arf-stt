---
spec_version: "3"
paper_id: "10.48550_arXiv.2603.25460"
citation_key: "Huang2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# CLAR: CIF-Localized Alignment for Retrieval-Augmented Speech LLM-Based Contextual ASR

## Metadata

* **File**: `files/huang_2026_clar-retrieval-augmented-asr.pdf`
* **Published**: 2026
* **Authors**: Shangkun Huang 🇨🇳, Huan Wei 🇨🇳, Yunzhang Chen 🇨🇳
* **Venue**: Interspeech 2026
* **DOI**: `10.48550/arXiv.2603.25460`

## Abstract

Contextual ASR systems for speech LLMs commonly employ shallow fusion or prompt injection to bias
decoding toward domain-specific hotwords. These approaches suffer from feature dilution (global
pooling loses fine-grained entity cues) and weak-supervision misalignment (prompt tokens misalign
with acoustic positions). CLAR proposes a dual-encoder retrieval system using Continuous
Integrate-and-Fire (CIF) to learn monotonic token-level acoustic alignments without requiring
timestamps. A length-aware localized window matching mechanism precisely anchors short-entity
acoustic cues. Multi-granularity contrastive training combines global sentence-level and local
hotword-level objectives. The retrieved top-ranked hotwords are injected as contextual prompts to a
Speech LLM without shallow fusion. On AISHELL-1-NE, CLAR achieves Recall@1 of 97.03% and B-WER of
2.78%, improving over the SeACo-Paraformer baseline by 3.93pp CER and 9.14pp B-WER.

## Overview

CLAR diagnoses two fundamental problems with how existing contextual ASR systems retrieve and inject
hotwords into speech LLMs. First, global-average-pooling encoders dilute entity representations: a
4-second utterance containing a 3-syllable brand name produces one averaged representation, making
short entities acoustically invisible. Second, prompt injection approaches misalign text tokens with
acoustic positions because the speech LLM's attention mechanism cannot reliably ground short prompt
phrases to specific audio regions.

The CIF mechanism addresses both problems simultaneously. CIF (Continuous Integrate-and-Fire) is a
differentiable acoustic boundary detector: it accumulates frame-level weights until a threshold is
exceeded, then "fires" to produce a token-level representation. This generates monotonic alignments
that correspond to actual acoustic segments, enabling the system to extract a localized acoustic
representation for exactly the frames where an entity appears.

The length-aware localized window matching is the second key innovation: rather than matching a
hotword embedding against the full-utterance speech embedding, CLAR computes a sliding window over
the CIF-aligned frames with a window size proportional to the expected entity duration. This is
specifically designed to handle short entities (1-3 syllables) that are otherwise dominated by
surrounding context in global matching.

## Architecture, Models and Methods

**Dual encoder**: Paraformer speech encoder (Chinese ASR, modified to output frame-level features)
paired with Chinese-RoBERTa text encoder. Both project into a shared 768-dim embedding space via
linear projections.

**CIF predictor**: A lightweight convolutional module applied on top of Paraformer frame-level
features. Produces scalar weights per frame; weights accumulate until reaching threshold beta=1.0,
triggering a "fire" event that sums weighted frames into a single token-level acoustic vector.

**Length-aware localized matching**: Window size W = max(3, round(entity_char_length × 2)) CIF
tokens. Hotword embedding is matched against every window position via cosine similarity; the
maximum similarity score is the retrieval score.

**Training objectives**: Three losses — global sentence-level contrastive loss (InfoNCE, temperature
0.07), local hotword-level contrastive loss (same structure, applied to CIF segments), and CIF
quantity regularization (ensures number of CIF tokens approximates ground-truth token count).
Combined with equal weights.

**Inference**: Top-5 retrieved hotwords are formatted as a text prompt and injected into the Speech
LLM's context window. No shallow fusion weight tuning required.

Datasets: AISHELL-1 (training ASR), AISHELL-2 (training retriever), AISHELL-1-NE test set (808 test
utterances, 400 hotwords, 1334 dev utterances, 600 dev hotwords).

## Results

* Hotword Recall@1: **97.03%** on AISHELL-1-NE test set
* Hotword Recall@5: **99.75%**
* CER: **0.92%** (baseline SeACo-Paraformer: 4.85%; improved PAC baseline: 1.13%)
* B-WER: **2.78%** (SeACo-Paraformer: 11.92%; PAC: 3.07%)
* CER improvement over SeACo-Paraformer: **-3.93 pp** absolute
* B-WER improvement over SeACo-Paraformer: **-9.14 pp** absolute
* B-WER improvement over next-best PAC system: **-0.29 pp** absolute
* Unbiased CER (U-CER): **0.83%** (no degradation on non-entity tokens)

## Innovations

### CIF-Based Acoustic Token Alignment

First application of CIF for hotword retrieval alignment. CIF produces monotonic token-level
acoustic segments without requiring forced alignment or external timestamps, enabling precise
localized matching for short entities.

### Length-Aware Localized Window Matching

Windowing strategy calibrated to expected entity duration. Prevents short entity embeddings from
being dominated by surrounding context, directly addressing the dilution problem.

### Multi-Granularity Contrastive Training

Combines sentence-level and hotword-level contrastive objectives in a single training pass,
eliminating the need for separate retriever and ASR fine-tuning stages.

## Datasets

* **AISHELL-1**: ~170 hours Mandarin Chinese read speech; public; used for ASR training
* **AISHELL-2**: ~1000 hours Mandarin Chinese; public; used for retriever training
* **AISHELL-1-NE**: 808 test utterances with 400 hotword entities (R1: recall < 40% under base ASR);
  1334 dev utterances with 600 hotwords; Mandarin Chinese

## Main Ideas

* CIF-based localized alignment solves the short-entity dilution problem that plagues global-pooling
  retrieval — highly relevant for product SKUs and brand abbreviations that are 1-3 syllables long
* Length-aware windowing is a simple but effective engineering addition that can be applied to any
  retrieval-based contextual ASR system
* CLAR achieves state-of-the-art B-WER of 2.78% without shallow fusion — eliminating the LM
  interpolation weight tuning that makes shallow fusion deployment brittle
* Caveat: all experiments are on Mandarin Chinese; English evaluation is absent and transfer
  assumptions need empirical validation for Rezolve's English pipeline

## Summary

CLAR targets the representation dilution and alignment mismatches that limit retrieval-augmented
contextual ASR in speech LLMs. The paper provides a rigorous diagnosis of why global-pooling
encoders fail for short entities and why prompt injection creates alignment ambiguity. The proposed
solution — CIF-based monotonic alignment combined with length-aware localized window matching — is
principled and directly addresses both failure modes.

The dual-encoder system uses a Paraformer speech encoder with a CIF predictor alongside a
Chinese-RoBERTa text encoder, projecting into a shared embedding space. Multi-granularity
contrastive training (sentence-level + hotword-level) ensures the retriever can both retrieve the
right entity from the corpus and locate its acoustic position within the utterance.

Results on AISHELL-1-NE: **0.92% CER** and **2.78% B-WER**, state-of-the-art on this benchmark,
representing a **-9.14pp** B-WER improvement over SeACo-Paraformer. Hotword Recall@1 of **97.03%**
means nearly all relevant entities are retrieved before injection.

For Rezolve, CLAR's architecture is directly applicable to the Whisper Turbo + dynamic context
injection pipeline: the CIF localization principle can be applied to Whisper's encoder to improve
entity retrieval precision. The English adaptation requires training on English entity-annotated
data; the AISHELL-1-NE benchmark protocol (R1 hotwords with recall < 40% under base ASR) closely
mirrors the gold-92 challenge entities.
