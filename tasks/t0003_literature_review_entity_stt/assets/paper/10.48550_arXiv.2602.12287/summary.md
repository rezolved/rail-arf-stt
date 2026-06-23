---
spec_version: "3"
paper_id: "10.48550_arXiv.2602.12287"
citation_key: "An2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Retrieval-Augmented Self-Taught Reasoning Model with Adaptive Chain-of-Thought for ASR

Named Entity Correction

## Metadata

* **File**: `files/an_2026_retrieval-augmented-ner-asr.pdf`
* **Published**: 2026
* **Authors**: Junjie An 🇨🇳, Jingguang Tian 🇨🇳, Tianyi Wang 🇨🇳, Yu Gao 🇨🇳, Xiaofeng Mou 🇨🇳, Yi Xu 🇨🇳
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2602.12287`

## Abstract

ASR systems frequently misrecognize domain-specific named entities. This paper proposes RASTAR, a
retrieval-augmented framework combining a BERT-based Rephrasing Language Model (RLM) for named
entity recognition with phonetic-level edit-distance retrieval, and A-STAR, an adaptive
chain-of-thought self-taught reasoning model that dynamically adjusts reasoning depth based on task
difficulty. Three difficulty levels (Simple, Challenging, Formidable) trigger increasing
chain-of-thought depth. Trained on Qwen3 (0.6B and 8B variants) with DPO. On AISHELL-1, RLM achieves
94.18% F1 vs. 91.97% for DANCER baseline. RASTAR achieves 17.96% and 34.42% relative NE-CER
reduction on AISHELL-1 and Homophone test sets. Token efficiency: 30-40% fewer reasoning tokens vs.
full chain-of-thought.

## Overview

RASTAR addresses the two-stage challenge of named entity correction in ASR: first, identify which
spans in the ASR output are named entities that may be misrecognized; second, retrieve the correct
entity from a domain entity repository and substitute it. The paper proposes a unified framework
that handles both stages with complementary components.

The Rephrasing Language Model (RLM) is a BERT-based model trained to identify entity spans in ASR
outputs using bidirectional encoding. Rather than tagging at character level, RLM uses a masked
language modeling objective: entity spans are masked and the model is trained to reconstruct the
correct entity, leveraging context from the full utterance.

The A-STAR reasoning model introduces adaptive chain-of-thought depth based on task difficulty
classification. For easy entities (high phonetic similarity to the spoken form), a direct answer is
produced with minimal chain-of-thought. For challenging entities (partial similarity), a short
reasoning chain is generated. For formidable entities (low similarity, likely homophones), a full
reasoning chain is generated. This adaptive strategy reduces unnecessary token generation by 30-40%
while preserving correction accuracy.

## Architecture, Models and Methods

**RLM**: BERT-base-Chinese (or equivalent). Masked language modeling pre-training continued on
entity-annotated ASR data. Concatenates ASR hypothesis with mask sequences at entity positions;
fine-tuned on (erroneous hypothesis, gold entity) pairs.

**Phonetic retrieval**: Normalized edit distance on romanized Mandarin (Pinyin) between the ASR
output entity string and candidate entities in the repository. Top-k=3 candidates retrieved.

**A-STAR**: Qwen3-8B (primary) and Qwen3-0.6B (efficiency variant). Self-taught training via Direct
Preference Optimization (DPO) on synthetic difficulty-stratified pairs. Difficulty classification:
cosine similarity between ASR entity embedding and gold entity embedding in a shared phonetic space.
Beta=0.1.

Training: 8×40GB NVIDIA H20 GPUs; 1,800 DPO samples for 8B; 6,880 for 0.6B.

**Entity repository**: 16,168 distinct named entities from the evaluation domain.

Evaluation: NER F1 (RLM quality), NE-CER (named entity character error rate, primary metric for
end-to-end correction quality), token count (efficiency measure).

## Results

* RLM NER F1 on AISHELL-1: **94.18%** (vs. DANCER baseline: **91.97%**)
* RLM NER F1 on Homophone test: **83.91%** (vs. DANCER: **74.82%**)
* RASTAR (8B) NE-CER on AISHELL-1: **6.21%** (**17.96%** relative reduction)
* RASTAR (8B) NE-CER on Homophone: **7.43%** (**34.42%** relative reduction)
* Token reduction (8B vs. full CoT): **30%** on AISHELL-1, **21%** on Homophone
* Qwen3-0.6B achieves comparable NER F1 to 8B with **40%** nothinking on simple cases
* No latency measurements reported in the paper

## Innovations

### Adaptive Chain-of-Thought Depth (A-STAR)

First application of difficulty-adaptive reasoning depth to ASR NE correction. Reduces inference
cost by 30-40% while preserving correction quality. DPO training on difficulty-stratified synthetic
pairs eliminates need for human-annotated reasoning chains.

### RLM Masked Language Modeling for NE Identification

BERT-based masked reconstruction of entity spans, leveraging bidirectional context. Outperforms
sequence tagging baselines (DANCER) by +2.2pp F1 on standard, +9.1pp on phonetically confusing
entities.

## Datasets

* **AISHELL-1**: ~170 hours Mandarin Chinese read speech; standard benchmark; public
* **Homophone test set**: 115 phonetically confusing utterances from AISHELL-1; tests the hardest NE
  correction cases
* **AISHELL-NER**: Named entity annotations for AISHELL-1
* **Entity repository**: 16,168 entities used for retrieval

## Main Ideas

* Adaptive chain-of-thought depth (30-40% token reduction) makes the approach more
  latency-compatible than full-CoT reasoning models — relevant for 800ms pipeline
* The Homophone test (34.42% NE-CER reduction) is the most analogous to Rezolve's challenge: brand
  names that sound similar to common words
* The RLM approach (BERT-based, low-compute) for entity span detection is applicable as a
  lightweight first-pass before a heavier reasoning corrector
* Caveat: all experiments are Mandarin Chinese; English adaptation would require retraining on
  English entity-annotated ASR data

## Summary

An et al. propose RASTAR, a two-stage pipeline for named entity correction in ASR. The first stage
identifies entity spans using a BERT-based masked language model (RLM) trained on the distinction
between correct and ASR-corrupted entity forms. The second stage retrieves candidate entities
phonetically and applies an adaptive chain-of-thought reasoning model (A-STAR) to select and
substitute the correct entity.

A-STAR's difficulty-adaptive mechanism classifies each correction instance as Simple, Challenging,
or Formidable based on phonetic similarity, then applies proportional chain-of-thought depth. DPO
training on synthetic difficulty-stratified pairs eliminates manual annotation of reasoning chains.

Key results: **17.96%** and **34.42%** relative NE-CER reduction on AISHELL-1 and the harder
Homophone test respectively. Token reduction of 30-40% vs. full CoT. RLM achieves **94.18% F1** on
standard NE identification and **83.91%** on phonetically confusing cases.

For Rezolve, A-STAR's adaptive reasoning depth is the most attractive property: it reduces inference
cost for easy cases while preserving accuracy on hard ones (homophones). The English adaptation
requires training on English brand-name ASR data, but the framework is architecturally
straightforward. The Homophone results are directly relevant to ecommerce brand names that sound
like common English words.
