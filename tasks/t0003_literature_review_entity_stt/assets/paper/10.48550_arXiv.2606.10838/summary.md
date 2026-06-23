---
spec_version: "3"
paper_id: "10.48550_arXiv.2606.10838"
citation_key: "Poncelet2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Towards Deep Contextual Reasoning from Broad Descriptions for ASR with Speech-LLM via

Metadata-Driven Reasoning Chains

## Metadata

* **File**: `files/poncelet_2026_deep-contextual-reasoning-asr.pdf`
* **Published**: 2026
* **Authors**: Jakob Poncelet 🇧🇪, Hugo Van hamme 🇧🇪 (KU Leuven)
* **Venue**: Interspeech 2026
* **DOI**: `10.48550/arXiv.2606.10838`

## Abstract

Speech recognition fails on rare, domain-specific terms and context-related named entities. Existing
contextualization methods bias decoding with keyword or phrase lists, which does not scale to broad
contextual descriptions and fails to exploit deeper semantic relationships. This paper trains a
speech-LLM to use broad descriptions (e.g., from video metadata) as weak semantic priors for
chain-of-thought contextual reasoning. A dataset of 400 hours of reasoning-augmented speech is
constructed by pairing erroneous transcripts with video metadata and LLM-generated reasoning
explanations. The speech-LLM is fine-tuned to produce: initial transcript, reasoning over context,
corrected transcript. On M3AV YouTube-derived test sets, the approach reduces overall WER from 9.4%
to 9.3%, rare word WER from 24.0% to 23.1%, and named entity WER from 23.9% to 23.3% vs. the
non-reasoning variant.

## Overview

Poncelet and Van hamme address the scalability ceiling of keyword-list contextual biasing: while
providing a list of 100-1000 domain terms works for narrow domains, it breaks down when the
contextual description is complex (a video topic, a product category, a user's browsing history).
The paper asks whether a speech-LLM can learn to reason from rich text descriptions rather than just
matching against flat keyword lists.

The training methodology creates reasoning chains automatically: given a speech segment with a known
erroneous transcript and associated video metadata (title, tags, description), an LLM generates a
natural language explanation of why the entity in the context should correct the error. These
(audio, context, reasoning, correction) tuples are used to fine-tune a speech-LLM to produce
chain-of-thought outputs in the format: `<initial-text> — <reasoning> — <final-text>`.

The 400-hour training set is derived from YouTube videos, combining ASR errors (75%) with
synthetically generated errors (25%) to ensure the model learns to correct without memorizing the
training domain. Four speech-LLM architectures are tested (Qwen2-Audio-7B, Qwen2.5-Omni,
Audio-Flamingo-3, Ultravox-v0.5) to confirm architectural generality.

## Architecture, Models and Methods

**Base models tested**: Qwen2-Audio-7B (primary), Qwen2.5-Omni, Audio-Flamingo-3, Ultravox-v0.5.

**Training data construction**: YouTube video segments paired with metadata (title, tags,
description). Erroneous transcripts sourced from Whisper-large-v3 outputs. LLM (GPT-4o) generates
reasoning explanations of the form: "Given the video is about [topic], the word '[error]' should be
'[correction]' because [reason]." 400 hours total; 75% real ASR errors, 25% synthetic perturbations.

**Fine-tuning**: Standard instruction tuning (SFT) on (audio, context, chain-of-thought target)
triples. Training on 8×A100 GPUs; batch size 16, 3 epochs, learning rate 2e-5.

**Evaluation**: M3AV test set (YouTube-derived, held out during training). Metrics: overall WER,
rare word WER (words with < 5 training occurrences), named entity WER (words matching a named entity
list). Chain-of-thought output parsed to extract final transcript only for WER computation.

## Results

* Overall WER: **9.3%** (reasoning model) vs. **9.4%** (non-reasoning baseline) on M3AV test set —
  Qwen2-Audio-7B
* Rare word WER: **23.1%** vs. **24.0%** baseline (−0.9pp absolute)
* Named entity WER: **23.3%** vs. **23.9%** baseline (−0.6pp absolute)
* Cross-model consistency: improvements held across all four tested architectures
* Dataset: ~75% ASR-based errors, ~25% synthetic; open-sourced for reproducibility

## Innovations

### Metadata-Driven Reasoning Chain Training

First method training speech-LLMs to perform chain-of-thought contextual reasoning from broad
metadata rather than narrow keyword lists. Enables reasoning about context types that cannot be
pre-enumerated (video topics, product categories).

### Automated Reasoning Chain Generation

Pipeline using GPT-4o to generate (error, context, explanation, correction) training tuples from
YouTube data at scale, enabling training without human annotation of reasoning chains.

## Datasets

* **M3AV**: YouTube-derived speech dataset, English; test set held out for evaluation
* **YouTube training set**: 400 hours with video metadata; 75% real errors, 25% synthetic;
  open-sourced

## Main Ideas

* The gains on named entity WER (−0.6pp absolute, −2.5% relative) are modest but consistent across
  four architectures, suggesting the approach is reliable even if not dramatic in magnitude
* Metadata-driven reasoning is complementary to keyword biasing — combining both approaches (keyword
  list + contextual description reasoning) should give larger gains
* For Rezolve, the "broad description" corresponds naturally to session metadata: product category
  browsed, recent search queries, cart contents. These are richer signals than a flat hotword list
  and could substantially improve named entity accuracy
* The training data construction pipeline (GPT-4o generating reasoning chains from metadata +
  erroneous transcripts) can be applied to Rezolve's production session data without any human
  annotation

## Summary

Poncelet and Van hamme train a speech-LLM to reason from broad contextual descriptions using
chain-of-thought fine-tuning. The motivation is that keyword lists cannot capture the semantic
richness of context available in real applications (video metadata, session context). The training
data is constructed automatically: GPT-4o generates reasoning chain explanations pairing ASR errors
with video metadata, creating 400 hours of reasoning-augmented training data.

The model is fine-tuned to produce initial transcript, reasoning, and corrected output. Four
speech-LLM architectures are tested on the M3AV YouTube test set. Results: overall WER improves from
**9.4% to 9.3%**, rare word WER from **24.0% to 23.1%**, named entity WER from **23.9% to 23.3%** —
modest but consistent improvements across all architectures.

The improvements are smaller in absolute terms than keyword-biasing methods but complement them:
reasoning over context semantics catches entity corrections that keyword matching misses (e.g.,
inferring a brand from product category context rather than requiring the exact brand name in the
bias list).

For Rezolve, the session metadata pipeline is particularly relevant: product categories, search
queries, and cart contents provide natural broad-description context for ecommerce voice sessions.
The automated training data construction from session logs and production transcripts could be
applied to the gold-92 domain without human annotation overhead.
