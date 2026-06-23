---
spec_version: "3"
paper_id: "10.48550_arXiv.2603.16411"
citation_key: "Kumar2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# RECOVER: Robust Entity Correction via Agentic Orchestration of Hypothesis Variants for

Evidence-based Recovery

## Metadata

* **File**: `files/kumar_2026_recover-entity-correction.pdf`
* **Published**: 2026
* **Authors**: Abhishek Kumar, Aashraya Sachdeva
* **Venue**: Interspeech 2026
* **DOI**: `10.48550/arXiv.2603.16411`

## Abstract

RECOVER is an agentic correction framework that leverages multiple ASR hypotheses and LLM-based
correction to improve entity recognition in ASR transcripts. The framework evaluates four hypothesis
selection strategies: 1-Best, Entity-Aware Select, ROVER Ensemble, and LLM-Select. Tested on five
diverse datasets (Earnings-21, ATCO2, Eka-Medical, Common Voice, ContextASR-Bench), RECOVER achieves
8-46% relative reductions in entity-phrase word error rate (E-WER) with recall improvements up to 22
percentage points. LLM-Select using GPT-4o achieves optimal entity correction performance while
maintaining overall word error rates across datasets.

## Overview

RECOVER addresses the entity recognition gap in standard LLM-based post-correction: while LLMs
improve overall fluency, they struggle to recover entities absent from the 1-best hypothesis because
LLMs are biased toward frequent vocabulary. RECOVER's insight is that collecting multiple ASR
hypotheses (e.g., from beam search or multiple ASR systems) increases the probability that the
correct entity string appears somewhere in the hypothesis set, even if not in the 1-best output.

The framework treats the correction problem as evidence aggregation: gather hypotheses, select the
most entity-informative one, and pass it to an LLM corrector. Four selection strategies are
evaluated ranging from trivial (always use 1-best) to sophisticated (ask an LLM to select the best
hypothesis based on entity coverage). LLM-Select uses GPT-4o as a meta-selector, which provides
robustness across diverse domain conditions.

The evaluation covers five distinct domains: financial earnings calls (Earnings-21), air traffic
control (ATCO2), medical dictation (Eka-Medical), general speech (Common Voice), and a purposely
entity-dense benchmark (ContextASR-Bench). This cross-domain coverage is unusually broad for a
post-correction paper and enables assessment of technique robustness.

## Architecture, Models and Methods

**Hypothesis sources**: beam search top-5 from Whisper-large-v3; optionally multiple ASR systems.
Each hypothesis is a complete transcript of the utterance.

**Strategy 1 — 1-Best**: Use only the top hypothesis. Baseline.

**Strategy 2 — Entity-Aware Select**: Score each hypothesis by number of detected entity spans
(using an NER model); select the hypothesis with the most entities.

**Strategy 3 — ROVER Ensemble**: Token-level majority voting across all hypotheses; selects the
consensus token at each position.

**Strategy 4 — LLM-Select**: GPT-4o is prompted with all hypotheses and asked to select the best one
based on entity coverage and contextual plausibility. Most powerful but also highest-latency.

**Correction step**: The selected hypothesis is passed to GPT-4o with a domain-adapted prompt for
final correction. No additional ASR retraining.

**Metrics**: E-WER (entity-phrase word error rate computed over entity-tagged spans), overall WER,
recall (fraction of gold entities recovered).

## Results

* Earnings-21 E-WER reduction: **33-35%** relative (LLM-Select best strategy)
* ATCO2 E-WER reduction: **8-14.5%** relative
* Eka-Medical E-WER reduction: **17-23%** relative
* Common Voice E-WER reduction: **38-45%** relative
* ContextASR-Bench E-WER reduction: **6-20%** relative
* Entity recall improvement: up to **+22 pp** across datasets
* LLM-Select performs best or near-best on **4 of 5** datasets
* ROVER Ensemble sometimes introduces insertion noise on noisy domains (ATCO2)
* Overall WER preserved — RECOVER does not degrade non-entity tokens

## Innovations

### Multi-Strategy Hypothesis Selection for Entity Recovery

Systematic comparison of four hypothesis selection strategies with cross-domain evaluation.
Establishes that LLM-based meta-selection (LLM-Select) is the most robust strategy, outperforming
deterministic selection on diverse domains.

### E-WER: Entity-Phrase Word Error Rate

Evaluation metric focusing specifically on entity spans, providing a more granular measurement of
entity recovery quality than aggregate WER.

## Datasets

* **Earnings-21**: 2,086 segments from financial earnings calls; English; entity-rich
* **ATCO2**: 560 segments from air traffic control; English; narrow domain terminology
* **Eka-Medical**: 3,619 segments from medical dictation; English; medical entities
* **Common Voice**: 16,401 segments; diverse English; broad vocabulary
* **ContextASR-Bench**: 5,273 segments; entity-dense evaluation benchmark

## Main Ideas

* Multi-hypothesis LLM-Select achieves the widest range of E-WER reductions (8-46%) across domains —
  the method is robust to domain change, unlike single-strategy approaches
* The +22pp entity recall gain shows that the 1-best hypothesis frequently misses entities that
  appear in lower-ranked beams — collecting top-5 hypotheses is inexpensive and recovers significant
  entity coverage
* ROVER Ensemble degrades on noisy domains (ATCO2: insertion noise) — simple voting strategies are
  not universally safe; LLM-Select is safer
* For Rezolve, the Earnings-21 and ContextASR-Bench results are most analogous to ecommerce voice:
  entity-dense, English, business-critical accuracy requirements
* Latency concern: GPT-4o for both selection and correction adds 200-500ms per utterance in practice
  — local corrector distillation is required for 800ms budget

## Summary

Kumar and Sachdeva address the entity recovery gap in LLM post-correction by exploiting the N-best
hypothesis diversity from beam search. The core finding is that the 1-best hypothesis frequently
omits rare entities that appear in hypotheses ranked 2-5, and that collecting this diversity
significantly improves entity recovery when a smart selection strategy is applied.

RECOVER evaluates four hypothesis selection strategies from trivial (1-Best) to LLM-based
(LLM-Select with GPT-4o), measuring entity-phrase WER (E-WER) and recall on five diverse English
domains. LLM-Select is the most robust strategy, achieving the best or near-best E-WER on 4 of 5
datasets.

Key results: **8-46% relative E-WER reductions** and **up to +22pp entity recall** across datasets.
Earnings-21 (closest to Rezolve's entity-rich domain) sees **33-35% relative** E-WER reduction.
ROVER Ensemble degrades on noisy domains — LLM-based selection is required for reliable cross-domain
performance.

For Rezolve, RECOVER's multi-hypothesis approach is immediately applicable to the production Whisper
Turbo pipeline: collecting beam search top-5 is free, and the LLM-Select + correction approach adds
a post-processing layer with no model retraining. The main obstacle is latency: GPT-4o adds
200-500ms per utterance. A distilled local corrector (7B class) would be needed to meet the 800ms
p50 target.
