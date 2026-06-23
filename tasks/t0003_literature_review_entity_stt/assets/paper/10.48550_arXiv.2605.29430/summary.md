---
spec_version: "3"
paper_id: "10.48550_arXiv.2605.29430"
citation_key: "Jiang2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Towards Human-Like Interactive Speech Recognition With Agentic Correction and Semantic Evaluation

## Metadata

* **File**: `files/jiang_2026_agentic-asr-interactive.pdf`
* **Published**: 2026
* **Authors**: Zixuan Jiang 🇨🇳, Yanqiao Zhu 🇨🇳, Peng Wang 🇨🇳, Qinyuan Chen 🇨🇳, Xipeng Qiu 🇨🇳 (Fudan
  University), Kai Yu 🇨🇳 (Shanghai Jiao Tong University)
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2605.29430`

## Abstract

Current ASR evaluation relies on WER/CER, which treats all token errors equally and fails to capture
semantic meaning preservation. This paper proposes Agentic ASR, a closed-loop framework combining a
single-pass ASR front-end with semantic correction, intent routing, and reasoning-based editing. The
system introduces S2ER (Sentence-level Semantic Error Rate) as a new metric assessed via three-round
bidirectional LLM voting. An Interactive Simulation System benchmarks multi-turn refinement. On
GigaSpeech, WenetSpeech, and AISHELL-NER datasets, iterative interaction reduces S2ER from 19-28% to
under 2% across 10 loops, while WER decreases only modestly from 10-12% to 9-10%, demonstrating that
semantic errors are corrected far more efficiently than token errors.

## Overview

Agentic ASR frames speech recognition as a closed-loop multi-turn task rather than a single-pass
transcription. The core insight is that WER/CER are poor proxies for task-completion quality: a 1%
WER utterance may still have a wrong intent if the one wrong token happens to be the product name.
The paper introduces S2ER (Sentence-level Semantic Error Rate) to measure this gap.

The framework consists of three components: a Semantic Correction module that rewrites the raw ASR
hypothesis using interaction history; an Intent Router that classifies each correction turn as
confirmation, new input, or error correction; and a Reasoning Editor that uses a
Locate-Reason-Modify pipeline to apply targeted corrections to specific spans.

The multi-turn structure enables iterative refinement: in each loop, the system produces a
hypothesis, the user (or simulated user) responds with feedback, and the agent applies targeted
corrections. The S2ER metric evaluates semantic correctness via three rounds of bidirectional LLM
voting with 0.83-0.90 correlation to human judgment.

A key empirical finding is that S2ER collapses dramatically across 10 loops (from ~20% to ~2%) while
WER decreases only modestly (from ~12% to ~10%), confirming that semantic errors are concentrated in
a small subset of critical tokens — exactly the named entities and intent-bearing spans that matter
most for downstream action.

## Architecture, Models and Methods

**ASR front-end**: Whisper or FireRedASR (tested across multiple backends to confirm generality).

**Semantic Correction**: Qwen3-based LLM (8B and 32B tested) prompted with interaction history.
Produces a revised hypothesis incorporating user feedback.

**Intent Router**: Classifies each user utterance as: (a) acceptance of current hypothesis; (b) new
speech input; (c) partial correction with span specification.

**Reasoning Editor**: Locate-Reason-Modify pipeline — (1) locate the error span referenced by the
user; (2) reason about the intended token using domain knowledge; (3) apply minimal edit to the
hypothesis.

**S2ER metric**: LLM judge (Qwen3-32B) assigns a binary correct/incorrect label per sentence using
three-round bidirectional voting. Human-AI alignment: 0.83-0.90 correlation coefficient across test
sets.

**Interactive Simulation System (ISS)**: Automated multi-turn testing infrastructure using LLM-based
user simulator and TTS synthesis. Generates synthetic correction turns from gold transcriptions for
reproducible benchmarking.

## Results

* GigaSpeech S2ER: **21.47% → 3.49%** (Loop 0 → Loop 10)
* WenetSpeech S2ER: **19.46% → 1.80%** (Loop 0 → Loop 10)
* ASRU2019 code-switching S2ER: **28.57% → 1.36%**
* AISHELL-NER S2ER: **19.91% → 2.02%**
* GigaSpeech WER: **11.92% → 10.43%** (Loop 0 → Loop 10, much smaller gain)
* Named entity error rate: approximately **~2% → < 1%** on specialized NER datasets
* Qwen3-32B LLM judge correlation with human: **0.83-0.90**
* Majority-3 voting achieves optimal cost-benefit vs. single-judge protocol

## Innovations

### S2ER Semantic Error Rate Metric

New metric capturing whether ASR errors cause meaning change, not just token mismatch. LLM-judged
with high human correlation, provides a meaningful proxy for downstream task completion rate —
closer to Rezolve's wrong-action rate metric.

### Closed-Loop Agentic Correction

First systematic demonstration that multi-turn correction reduces semantic errors to near-zero while
WER remains flat, showing that the highest-value corrections (entity names) are achievable with
minimal turns.

### Interactive Simulation System

Automated multi-turn ASR evaluation infrastructure using simulated user responses, enabling
reproducible benchmarking of interactive ASR systems without human annotators.

## Datasets

* **GigaSpeech**: 10,000-hour English public dataset; test set used
* **WenetSpeech**: Mandarin Chinese large-scale dataset
* **ASRU2019**: Mandarin-English code-switching benchmark
* **AISHELL-NER**: Named entity annotated Mandarin speech

## Main Ideas

* S2ER is a better proxy for Rezolve's wrong-action rate than WER — adopting it for gold-92
  evaluation would more directly measure what matters
* Multi-turn agentic correction achieves <2% S2ER in 10 loops, but each loop adds latency; for a
  real-time voice assistant, at most 1-2 correction turns are feasible within the 800ms budget
* The entity error rate improvement (~2% → <1%) is achievable in a single correction turn for
  high-confidence misrecognitions, suggesting 1-shot post-correction is sufficient for most
  ecommerce entity errors
* The LLM backend (Qwen3-32B) adds significant inference cost — the paper's approach requires
  distillation or a lighter corrector model for latency-sensitive deployment

## Summary

Jiang et al. reframe ASR as a closed-loop interactive task and demonstrate that semantic errors
(wrong intent, wrong entity) are far more correctable than surface token errors. The motivating
observation is that WER fails to distinguish high-value errors (brand names, quantities) from
low-value ones (function words), understating how correctable business-critical mistakes actually
are.

The Agentic ASR framework adds semantic correction, intent routing, and reasoning-based editing on
top of a standard ASR front-end. The S2ER metric provides a semantically meaningful evaluation via
LLM judging with 0.83-0.90 human correlation. An Interactive Simulation System enables automated
multi-turn evaluation.

Key results: S2ER collapses from **~20-28% to <2%** across 10 correction loops while WER decreases
only from ~12% to ~10%. Named entity error rates improve from ~2% to <1% on specialized NER test
sets. The dramatic S2ER vs. WER divergence confirms that semantic errors concentrate in a small set
of critical tokens.

For Rezolve, the primary takeaway is the S2ER metric: adopting it for gold-92 evaluation would more
accurately measure wrong-action rate than WER. The multi-turn correction approach is appealing but
requires latency budgeting — at most 1-2 correction turns are feasible within 800ms. The heavy
Qwen3-32B backend requires distillation for production.
