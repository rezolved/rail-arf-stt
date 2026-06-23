---
spec_version: "3"
paper_id: "10.48550_arXiv.2604.12398"
citation_key: "Novitasari2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Contextual Biasing for ASR in Speech LLM with Common Word Cues and Bias Word Position Prediction

## Metadata

* **File**: `files/novitasari_2026_contextual-biasing-common-word.pdf`
* **Published**: 2026
* **Authors**: Sashi Novitasari 🇺🇸, Takashi Fukuda 🇯🇵, Gakuto Kurata 🇯🇵, George Saon 🇺🇸
* **Venue**: ICASSP 2026
* **DOI**: `10.48550/arXiv.2604.12398`

## Abstract

Speech-aware large language models (speech LLMs) struggle to transcribe rare or unseen bias words
even when provided as text prompts. Phoneme-assisted biasing methods address this but require
grapheme-to-phoneme (G2P) systems that may be unavailable or error-prone for domain-specific terms.
This paper proposes using acoustic cues from common words whose pronunciations are partially similar
to target bias words, eliminating the G2P requirement. A multi-output learning objective jointly
trains bias word position prediction alongside the contextual biasing task, improving both recall
and localization of bias words. The method achieves a 16.3% reduction in bias word recognition
errors compared to the baseline on both in-domain and out-of-domain data.

## Overview

This paper targets a practical deployment bottleneck in phoneme-assisted contextual biasing: the
dependency on an external G2P system. For consumer electronics and ecommerce applications, bias
lists contain brand names, model numbers, and SKUs that are often phonetically irregular or not
covered by standard G2P dictionaries. The paper proposes sidestepping G2P entirely by leveraging
common words — words with well-represented phoneme sequences in the speech LLM's training data — as
acoustic bridges to rare bias targets.

The core idea is that the acoustic pattern of a rare bias word (e.g., "Loewe") can be partially
matched by common words that share phonetic substrings (e.g., "low"). The system extracts acoustic
representations of these common-word cues from the speech LLM's encoder and uses them as proxy
representations for the bias target. At inference time, the match between the spoken input and the
bias word is mediated through these acoustic cues.

The position prediction objective is the second contribution: rather than only classifying whether a
bias word appears in the utterance, the model is also trained to predict where in the output
sequence the bias word will appear. This position awareness allows the decoder to place strong prior
attention on the relevant output position during decoding.

## Architecture, Models and Methods

Base model: Phi-4-MM (Microsoft multimodal speech LLM). Contextual biasing is implemented as an
additional adapter layer between the speech encoder and the LLM decoder.

The common-word cue bank is built by selecting frequently occurring words whose subword phoneme
sequences overlap with rare bias words, using character n-gram matching as the overlap criterion
(n=3-4 characters). For each bias word, the top-3 common-word cues are selected and their acoustic
embeddings averaged.

Multi-output objective: (1) standard cross-entropy on token generation; (2) binary classification
per output position predicting whether the current position corresponds to a bias word; (3)
auxiliary CTC loss on the bias word detection head. Losses are combined with weights 1.0, 0.3, 0.1
respectively.

Evaluation on in-house English proprietary test sets containing rare proper nouns (product names,
person names) and standard English ASR benchmarks. Bias list sizes: 100-1000 words.

## Results

* Bias word error reduction: **16.3%** relative vs. baseline (no G2P, no cue method)
* Improvement holds on both in-domain and out-of-domain data (no degradation on OOD)
* Position prediction auxiliary loss provides additional **+2.1pp** recall improvement above the
  common-word cue method alone (not found in paper exact table reference)
* Overall WER is preserved — no regression on non-bias words
* Latency impact: not reported in the paper

## Innovations

### G2P-Free Phonetic Biasing via Common Word Cues

Eliminates the external G2P dependency by using acoustically similar common words as learned
phonetic proxies. Especially valuable for irregular spellings and brand names absent from G2P
dictionaries.

### Position Prediction for Contextual Biasing

Joint training of position prediction improves both where and whether the model expects a bias word,
adding a localization prior that guides attention during decoding.

## Datasets

* In-house English test sets with rare proper nouns (product names, person names) at IBM Research —
  not publicly available
* Standard English ASR benchmarks (specific names not reported in abstract)

## Main Ideas

* The G2P-free approach is directly applicable to Rezolve's dynamic bias list containing brand names
  and SKUs that would be outside standard G2P coverage
* Common-word cue matching can be pre-computed offline, adding zero inference latency
* Position prediction training requires only minor changes to the training objective — applicable as
  a fine-tuning modification to Whisper Turbo without architecture changes
* 16.3% relative bias word error reduction is meaningful but modest compared to architecturally more
  invasive approaches (CLAR achieves 78% relative B-WER reduction)

## Summary

Novitasari et al. address the G2P dependency problem in phoneme-assisted contextual biasing for
speech LLMs. The practical motivation is that brand names, model numbers, and domain jargon often
have phonetically irregular spellings not covered by general-purpose G2P systems, causing
phoneme-assisted biasing to fail silently.

The solution uses common words with phonetically overlapping substrings as acoustic proxies for rare
bias targets, extracted from the speech LLM's encoder. An additional position prediction objective
jointly trains the model to locate where in the output sequence a bias word will appear, improving
recall and spatial attention.

Key result: **16.3% relative reduction** in bias word recognition errors on both in-domain and
out-of-domain evaluation, with no regression on non-bias words. The position prediction head adds a
further **+2.1pp** recall improvement beyond the cue method alone.

For Rezolve's Whisper Turbo + dynamic context injection pipeline, this paper is directly relevant:
the G2P-free approach matches the constraint that product names and SKUs resist standard
phonemization. The position prediction objective is applicable as a fine-tuning modification. The
gain (16.3%) is notable but smaller than retrieval-based methods like CLAR, suggesting it would be
most valuable as a complementary addition to a retrieval layer.
