---
spec_version: "3"
paper_id: "10.48550_arXiv.2602.18966"
citation_key: "Ron2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Whisper: Courtside Edition — Multi-Agent LLM Pipeline for Domain-Specific ASR via

Context Generation

## Metadata

* **File**: `files/ron_2026_whisper-courtside-llm-context.pdf`
* **Published**: 2026
* **Authors**: Yonathan Ron 🇮🇱, Shiri Gilboa 🇮🇱, Tammuz Dubnov 🇮🇱 (Reichman University)
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2602.18966`

## Abstract

Whisper's initial_prompt parameter allows injecting up to 224 tokens of context to guide decoding,
but standard pipelines do not exploit this capability for domain-specific entity recognition. This
paper proposes a multi-agent LLM pipeline with six specialized agents (topic classification, named
entity recognition, jargon extraction, decision filtering, candidate selection, prompt construction)
that intercept Whisper's initial transcript and generate a compact context prompt. Evaluated on 421
NBA basketball commentary segments dense in proper nouns and technical jargon, the full pipeline
achieves 17.0% relative WER reduction (0.217 to 0.180, p < 0.001), improving 40.1% of segments while
degrading only 7.1%. No Whisper retraining is required.

## Overview

Ron et al. observe that Whisper's initial_prompt parameter — designed for multi-segment
transcription context — can be repurposed as a domain context injection mechanism. By feeding
Whisper's own preliminary transcript through a multi-agent pipeline that extracts domain signals and
constructs a compact prompt, the paper demonstrates that Whisper's decoder can be guided toward
correct entity recognition without any model modification.

The six-agent pipeline is inspired by human transcription workflows: a transcriptionist who knows
the topic area makes fewer entity errors. The topic classification agent identifies the domain (NBA
basketball); the NER agent extracts player names and team names using fuzzy matching (Levenshtein
distance, threshold τ=0.75); the jargon extraction agent identifies technical terms via RAKE and
YAKE. A decision filter prevents over-prompting by removing redundant or low-confidence candidates.

The evaluation domain — NBA basketball commentary — is analogous to ecommerce voice AI: dense proper
nouns (player names, team names), technical jargon (play types, positions), and rapid speech. The
17.0% relative WER reduction (0.217 → 0.180) comes primarily from entity correction: error analysis
shows 35% of improvements are in names, 28% in jargon.

## Architecture, Models and Methods

**Agent 1 — Topic Classification**: LLM-prompted (GPT-4-class) to identify domain and subtopic from
the preliminary transcript.

**Agent 2 — Named Entity Recognition**: NER model (spaCy-based) extracts entity spans; fuzzy
matching against a curated entity database (NBA player roster, team names) using Levenshtein
distance with threshold τ=0.75.

**Agent 3 — Jargon Extraction**: RAKE + YAKE keyword extraction from the preliminary transcript;
cross-referenced against a domain glossary.

**Agent 4 — Decision Filter**: Removes candidates with low confidence or already correctly
transcribed in the preliminary output. Prevents the prompt from filling with noise that would
distract Whisper's decoder.

**Agent 5 — Candidate Selection**: Selects the top-N candidates fitting within the 224-token budget.
Priority: rare entities > jargon > common terms.

**Agent 6 — Prompt Construction**: Formats selected candidates as natural language context: "This is
NBA basketball commentary featuring players [names] using terms [jargon]."

Whisper model: whisper-large-v3. No retraining. Evaluation: 421 segments, 10-30 seconds each,
expert-annotated WER. Statistical test: paired t-test, p < 0.001.

## Results

* Full pipeline (P4) WER: **0.180** vs. baseline **0.217** (**17.0%** relative reduction)
* Segments improved: **40.1%** of test segments
* Segments degraded: **7.1%** of test segments (net positive in 33% of cases)
* Error type breakdown: Names **35%**, Jargon **28%**, Accent **22%**, Segmentation **15%**
* Ablation — topic-only prompt: **6.2%** relative WER reduction
* Ablation — entities only: **11.4%** relative WER reduction
* Ablation — entities + jargon: **14.8%** relative WER reduction
* Latency: Not reported (multi-agent pipeline implies 500ms+ overhead in practice)

## Innovations

### Repurposing Whisper's initial_prompt for Domain Context

Demonstrates that the initial_prompt mechanism, designed for document-level context, is effective as
a per-segment domain entity injection vector. Requires only Whisper API access, no model weights.

### Multi-Agent Entity Extraction Pipeline

Six-agent pipeline with a decision filter that prevents over-prompting. The filter is the key
practical contribution: unconstrained entity injection degrades Whisper performance by overwhelming
the context window with noise.

## Datasets

* **NBA commentary dataset**: 421 segments, 10-30s each; English; expert WER annotation; dense
  proper nouns (player names, team names) and jargon; created by authors; not public
* **NBA entity database**: curated roster and terminology list for fuzzy matching

## Main Ideas

* Whisper Turbo's initial_prompt parameter is directly exploitable for Rezolve's dynamic entity
  lists without any model modification — this is the simplest possible integration
* The decision filter preventing over-prompting is a critical implementation detail: without it,
  Whisper's context window is dominated by noise and performance degrades
* 17.0% relative WER reduction on entity-dense domain speech directly benchmarks the approach in a
  domain analogous to ecommerce (dense proper nouns, no model training)
* The fuzzy matching threshold τ=0.75 (Levenshtein) is an engineering parameter that should be tuned
  on gold-92 to find the optimal precision/recall trade-off for Rezolve's brand and product
  vocabulary

## Summary

Ron et al. demonstrate that Whisper's initial_prompt parameter can be systematically exploited for
domain-specific entity recognition without model retraining. A six-agent LLM pipeline extracts
domain signals from Whisper's preliminary transcript and constructs a compact prompt that guides the
decoder toward rare entity recognition.

The pipeline processes topic classification, NER with fuzzy matching, jargon extraction, and a
decision filter that prevents over-prompting. Evaluation on 421 NBA basketball commentary segments
(dense proper nouns and technical jargon) shows a **17.0% relative WER reduction** (0.217 → 0.180, p
< 0.001), improving **40.1%** of segments while degrading only **7.1%**.

The approach is architecturally straightforward and requires only Whisper API access. The decision
filter is the key practical contribution: it prevents Whisper's 224-token context window from being
filled with low-confidence candidates that degrade performance. Error analysis confirms that the
gains are entity-driven (35% names, 28% jargon).

For Rezolve, this approach is the most immediately deployable: it leverages the existing Whisper
Turbo checkpoint and adds an LLM-based prompt generation step with no model training. The NBA domain
closely parallels ecommerce in entity density and proper noun challenges. The main engineering work
is tuning the fuzzy matching threshold for Rezolve's brand/product vocabulary and ensuring the
multi-agent latency fits within the 800ms p50 budget.
