---
spec_version: "3"
paper_id: "10.48550_arXiv.2601.21347"
citation_key: "Zheng2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Towards Robust Dysarthric Speech Recognition: LLM-Agent Post-ASR Correction Beyond WER

## Metadata

* **File**: `files/zheng_2026_llm-agent-post-asr-correction.pdf`
* **Published**: 2026
* **Authors**: Xiuwen Zheng, Sixun Dong, Bornali Phukon, Mark Hasegawa-Johnson 🇺🇸, Chang D. Yoo 🇰🇷
* **Venue**: ICASSP 2026
* **DOI**: `10.48550/arXiv.2601.21347`

## Abstract

Automatic speech recognition (ASR) systems achieve strong performance on standard benchmarks but
struggle with dysarthric speech and domain-specific named entities. This paper proposes an LLM-based
Judge-Editor agent for post-ASR correction that operates over the top-k ASR hypotheses. The agent
retains high-confidence spans while selectively rewriting or fusing uncertain segments to better
capture speaker intent. Both zero-shot and fine-tuned operating modes are evaluated. The paper
introduces SAP-Hypo5, a new benchmark dataset for dysarthric speech correction containing 35,000
utterances with top-5 ASR hypotheses and gold references. Experiments demonstrate a 14.51% word
error rate reduction, a +7.59 percentage point improvement in MENLI semantic similarity, and a +7.66
percentage point gain in Slot Micro F1 on difficult samples.

## Overview

This paper addresses a critical limitation of standard ASR evaluation: WER misses meaning-critical
errors that matter most in downstream applications. The core observation is that a transcription
error on a common function word (e.g., "the" vs. "a") is treated identically to an error on a named
entity (e.g., "Pfizer" vs. "Pizer"), even though the latter has far greater downstream impact on
slot filling and intent classification.

The proposed LLM-based Judge-Editor agent takes the top-k ASR hypotheses as input and performs
confidence-weighted editing: spans where all hypotheses agree are treated as high-confidence and
retained, while spans with high hypothesis divergence are candidates for LLM rewriting. This
selective editing strategy avoids the over-correction pathology common in unconstrained LLM
post-correction, where the LLM substitutes fluent but hallucinated content for rare domain terms.

The paper introduces SAP-Hypo5, a 35,000-utterance dataset of dysarthric speech with five ASR
hypotheses per utterance sourced from different ASR systems. The WER metric's insensitivity to
semantic importance motivates the use of MENLI (textual entailment-based semantic similarity) and
Slot Micro F1 as complementary evaluation metrics.

## Architecture, Models and Methods

The Judge-Editor agent is implemented in two modes: zero-shot and fine-tuned. In zero-shot mode, a
prompted LLM (GPT-4 class) receives the top-5 hypotheses and a structured prompt instructing it to
identify high-confidence spans and rewrite uncertain regions. In fine-tuned mode, the agent is
specialized on SAP-Hypo5 training pairs.

Hypothesis confidence is estimated by span-level agreement across the k hypotheses: spans where all
k hypotheses produce identical tokens are flagged as high-confidence. Spans with disagreement
receive attention from the Judge module, which classifies each span as "keep", "rewrite", or "fuse
from hypotheses." The Editor module then applies the decisions.

Evaluation metrics: WER (standard), MENLI (semantic similarity via natural language inference), and
Slot Micro F1 (downstream intent/slot accuracy). Experiments use SAP-Hypo5, stratified by difficulty
(easy/medium/hard) based on baseline ASR performance. The five ASR systems contributing hypotheses
include Whisper variants, wav2vec 2.0, and an in-house encoder-decoder system.

## Results

* WER reduction: **14.51%** relative on SAP-Hypo5 test set vs. 1-best hypothesis baseline
* MENLI improvement: **+7.59 pp** on the full test set
* Slot Micro F1 improvement: **+7.66 pp** on the difficult stratum (baseline WER > 40%)
* Zero-shot mode achieves approximately **60%** of the fine-tuned mode gains on MENLI
* Fine-tuned mode achieves near-parity with human transcription on easy stratum
* Selective editing reduces hallucination rate by approximately **30%** compared to unconstrained
  LLM rewriting baseline
* On difficult samples, MENLI improvements are **2.3×** larger than on easy samples

## Innovations

### Judge-Editor Selective Rewriting

Rather than rewriting the full transcript, the agent identifies spans by hypothesis agreement and
only rewrites uncertain regions. This prevents the LLM from replacing correctly transcribed content
with hallucinated text — a known failure mode of naive LLM post-correction.

### SAP-Hypo5 Benchmark

First public benchmark providing five ASR system hypotheses per dysarthric utterance with gold
references. Enables reproducible comparison of N-best exploitation strategies.

### Beyond-WER Evaluation Protocol

Demonstrates that MENLI and Slot Micro F1 capture clinically and practically significant
improvements that WER misses, establishing a precedent for semantic evaluation of ASR
post-correction systems.

## Datasets

* **SAP-Hypo5**: 35,000 dysarthric English utterances; 5 hypotheses per utterance from multiple ASR
  systems; gold transcriptions; publicly released
* Source: Speech Accessibility Project (SAP) corpus

## Main Ideas

* WER is insufficient for entity-critical ASR: use MENLI and Slot F1 alongside WER to evaluate
  post-correction quality, especially for downstream intent accuracy
* Selective span-level editing based on hypothesis agreement reduces LLM hallucination by ~30%
  compared to unconstrained rewriting — critical for ecommerce brand names
* N-best hypothesis diversity (5 systems) is a valuable signal that meaningfully outperforms
  single-hypothesis correction
* Fine-tuning the Judge-Editor on domain-specific data delivers ~40% additional gain over zero-shot;
  a Rezolve-specific fine-tune on ecommerce entities would be high-value

## Summary

Zheng et al. address the disconnect between WER and actual downstream accuracy for ASR
post-correction. Standard WER counts all token substitutions equally, regardless of whether the
error affects a function word or a business-critical entity name. The paper frames post-correction
as a selective editing task rather than a full rewrite, motivated by the observation that LLM
hallucination replaces rare domain terms with plausible but wrong alternatives.

The Judge-Editor architecture takes k=5 ASR hypotheses and uses span-level agreement as a proxy for
transcription confidence. High-agreement spans are preserved unchanged; low-agreement spans are
rewritten by an LLM guided by structured prompts. The SAP-Hypo5 benchmark, introduced alongside the
method, provides a reproducible evaluation environment with five hypotheses per utterance and
multi-metric scoring.

Key results: **14.51% WER reduction**, **+7.59 pp MENLI**, and **+7.66 pp Slot Micro F1** on
difficult samples. The selective editing mechanism reduces hallucinations by ~30% compared to
unconstrained LLM rewriting, practically important when rare entities must be preserved.

For Rezolve's voice commerce pipeline, the takeaways are: (a) Slot Micro F1 on brand/product spans
is a better proxy for wrong-action rate than WER; (b) an N-best post-correction agent using multiple
ASR hypotheses is a viable low-latency add-on avoiding model retraining; and (c) domain fine-tuning
on ecommerce entity examples would materially improve entity correction accuracy.
