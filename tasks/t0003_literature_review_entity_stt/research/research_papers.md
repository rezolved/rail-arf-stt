---
spec_version: "1"
task_id: "t0003_literature_review_entity_stt"
research_stage: "papers"
papers_reviewed: 11
papers_cited: 11
categories_consulted:
  - "entity-correction"
  - "stt-evaluation"
  - "latency-profiling"
  - "confidence-routing"
  - "whisper-finetuning"
date_completed: "2026-06-23"
status: "complete"
---
## Task Objective

This task surveys publications from January to June 2026 to identify the most effective techniques
for improving STT accuracy on domain-specific named entities — brand names, product names, and SKUs
— in an English ecommerce voice AI context. Rezolve's production pipeline uses Whisper Turbo with
dynamic context injection (runtime hotword list passed to the decoder) as its ASR system. The
gold-92 benchmark confirms that entity accuracy is the primary bottleneck, with brand names, product
names, and SKUs frequently mangled or dropped, causing wrong-action rates that exceed the 2% target.
The survey covers four technique families: contextual biasing, shallow fusion, entity-aware ASR
training, and LLM post-correction. Findings directly inform the design of follow-on prototyping
tasks and the decision of which approaches to evaluate against Whisper Turbo + dynamic context
injection on the gold-92 benchmark.

## Category Selection Rationale

The following five categories from `meta/categories/` are directly relevant to this literature
survey.

**Included:**

* `entity-correction` — The primary research target. Papers in this category address the core
  problem: improving transcription accuracy of brand names, product names, and SKUs. All four
  technique families surveyed (contextual biasing, shallow fusion, entity-aware training, LLM
  post-correction) are represented here.

* `stt-evaluation` — Measurement methodology is inseparable from the research question. Several 2026
  papers propose new evaluation metrics (S2ER, E-WER) that are more appropriate than WER for
  entity-accuracy assessment. Papers here also provide benchmark baselines.

* `latency-profiling` — The 800ms p50 latency constraint is a hard filter on viable techniques.
  Papers reporting latency numbers or streaming architectures are directly actionable for pipeline
  design.

* `confidence-routing` — LLM post-correction papers (Zheng2026, Kumar2026, Jiang2026) all involve
  confidence-based decisions about when to apply correction. Confidence routing is the downstream
  consumer of any entity correction improvement.

* `whisper-finetuning` — Ron2026 directly demonstrates Whisper-specific context injection via
  initial_prompt, which is applicable to Rezolve's Whisper Turbo checkpoint without retraining.

**Excluded:**

* `audio-datasets` — No 2026 papers on ecommerce-specific audio dataset creation were found; the
  gold-92 benchmark was created in t0001 and is not a literature target.

* `commercial-apis` — No 2026 papers compare commercial API entity accuracy against open-source
  alternatives in ecommerce domains.

## Key Findings

### Contextual Biasing Remains the Dominant Paradigm but is Rapidly Evolving

Contextual biasing — injecting a runtime list of domain terms into the decoder — remains the primary
technique for entity-accurate ASR in 2026. However, the approach has evolved substantially from flat
word-list prompting toward retrieval-augmented and RL-optimized variants.

Flat prompting approaches (injecting a list of 100-1000 words as decoder context) are the baseline
against which all 2026 methods are measured. The RLBR method [Ren2026] reports B-WER of 0.59%/2.11%
(test-clean/test-other) at 100 bias words on LibriSpeech, achieved by training a speech LLM with a
reinforcement learning reward that weights bias word correctness 5× higher than standard tokens.
This is the lowest B-WER reported among the surveyed 2026 methods on a standard English benchmark.

IBM Research [Novitasari2026] addresses a practical gap in phoneme-assisted biasing: the requirement
for a G2P system. Their common-word cue approach achieves a 16.3% reduction in bias word recognition
errors without G2P, applicable to product names and SKUs that resist standard phonemization. The
method is additive to other biasing approaches.

Streaming-compatible contextual biasing is demonstrated by [Tsai2026], who extend CTC-based word
spotting to streaming ASR via stateful token passing across audio chunks. The approach requires no
modification to the underlying acoustic model and integrates with any CTC-trained system including
Whisper's CTC auxiliary output.

**Hypothesis**: The community is converging on retrieval-augmented biasing (finding the right
entities from a large corpus before injection) as the solution to the scalability wall of flat list
prompting. As bias lists grow to 1000+ entries, flat prompting degrades; retrieval narrows the
effective context to the most relevant 10-20 entities.

**Best practice**: For bias lists under 200 words, flat prompting is competitive. For bias lists of
500-1000+ (Rezolve's dynamic brand catalog), retrieval-augmented injection is recommended.

### Retrieval-Augmented Biasing Achieves State-of-the-Art Entity WER

CLAR [Huang2026] achieves the strongest entity retrieval and correction performance among the
surveyed papers: **97.03% Recall@1**, **0.92% CER**, and **2.78% B-WER** on AISHELL-1-NE,
representing a 9.14pp B-WER reduction over the SeACo-Paraformer baseline. The approach uses
CIF-based monotonic alignment to produce token-level acoustic representations without timestamps,
enabling length-aware localized matching that specifically addresses the short-entity dilution
problem (1-3 syllable brand names lost in global-average-pooled embeddings).

RECOVER [Kumar2026] takes a complementary approach: rather than improving retrieval, it exploits
N-best hypothesis diversity. By collecting the top-5 ASR hypotheses and using GPT-4o to select the
most entity-informative one for correction, RECOVER achieves 8-46% relative E-WER reductions across
five diverse English domains. Earnings-21 (the most ecommerce-analogous domain) sees 33-35% relative
E-WER reduction. The key finding is that the 1-best hypothesis frequently omits rare entities that
appear in lower-ranked hypotheses, and LLM-based hypothesis selection (LLM-Select) is the most
robust strategy across domains.

RASTAR [An2026] provides a complementary perspective using adaptive chain-of-thought reasoning for
NE correction: 17.96% and 34.42% relative NE-CER reduction on AISHELL-1 and Homophone test sets
respectively. The adaptive reasoning depth (30-40% token reduction vs. full CoT) is specifically
relevant for latency-sensitive deployment.

These three papers converge on a shared finding: entity correction is most effective when the system
has access to a curated entity repository and uses phonetic-acoustic similarity (not just semantic
similarity) as the retrieval signal.

**Hypothesis**: Combining CLAR-style acoustic retrieval (getting the right entity candidates) with
RECOVER-style multi-hypothesis selection (exploiting N-best diversity) would yield additive gains in
entity accuracy.

**Best practice**: Build a curated entity repository of brand names, product names, and SKUs with
their phonetic representations. Use acoustic similarity retrieval to narrow the candidate list
before injection or correction.

### LLM Post-Correction Improves Semantic Accuracy Beyond What WER Captures

A consistent finding across [Zheng2026], [Jiang2026], and [Kumar2026] is that WER substantially
understates the semantic accuracy improvements achieved by LLM post-correction. The Agentic ASR
paper [Jiang2026] demonstrates this most dramatically: S2ER (Sentence-level Semantic Error Rate)
collapses from 19-28% to under 2% across 10 correction loops on GigaSpeech, WenetSpeech, and
AISHELL-NER, while WER decreases only modestly from 10-12% to 9-10%. Named entity error rates
improve from ~2% to <1% within the first few correction turns.

Zheng2026 [Zheng2026] reports a 14.51% WER reduction with +7.66pp Slot Micro F1 improvement on the
difficult stratum of SAP-Hypo5, and demonstrates that selective span editing (rewriting only
uncertain spans identified by hypothesis agreement) reduces hallucination by ~30% compared to
unconstrained LLM rewriting.

Ron2026 [Ron2026] demonstrates 17.0% relative WER reduction on entity-dense NBA commentary using
Whisper's initial_prompt parameter with a six-agent LLM pipeline — no model retraining required. The
multi-agent approach extracts topic, entities, and jargon from the initial transcript to construct a
context prompt that guides the decoder.

**Best practice**: Use S2ER or Slot F1 on entity spans as the primary evaluation metric for voice
commerce ASR, not aggregate WER. Wrong-action rate correlates with S2ER, not WER.

**Contradiction**: Zheng2026 finds that selective span rewriting reduces hallucinations vs.
unconstrained rewriting, while Jiang2026 shows multi-turn unconstrained correction achieves
near-zero S2ER after 10 loops. The difference is that Jiang2026 uses user feedback to constrain each
turn, while Zheng2026 operates single-pass without user confirmation. For a voice commerce assistant
where user confirmation is available (clarification routing), multi-turn correction is viable; for
fully automated correction, selective editing is safer.

### Reasoning-Based Context Exploitation Provides Modest but Consistent Entity Gains

Poncelet2026 [Poncelet2026] trains a speech-LLM to use broad metadata descriptions (e.g., video
topics) as chain-of-thought context for ASR correction, achieving named entity WER improvements from
23.9% to 23.3% (−0.6pp absolute, −2.5% relative) on M3AV YouTube-derived test sets. While the
absolute gain is smaller than retrieval-based methods, the approach is complementary: it addresses
entities that are absent from a pre-defined bias list but inferrable from session context (e.g., a
brand name discoverable from a product category).

The paper constructs 400 hours of reasoning-chain training data automatically using GPT-4o paired
with video metadata, without human annotation. This training data construction pipeline is
applicable to Rezolve's session logs (user browsing history, cart contents, prior queries) to build
an ecommerce-specific contextual reasoning dataset.

**Hypothesis**: For Rezolve's pipeline, session-level metadata (product category browsed, recent
search queries, cart contents) is a richer contextual signal than a flat hotword list for recovering
brand and product names absent from the static bias vocabulary.

### Streaming Latency is Achievable Under 300ms for ASR-Only Stage

Moonshine v2 [Kudlur2026] establishes concrete latency benchmarks for streaming ASR on Apple Silicon
M3: Tiny (33.57M params) achieves **50ms** with 8.03% CPU load, Small (123.36M params) achieves
**148ms**, and Medium (244.93M params) achieves **258ms**. The Medium model runs 43.7× faster than
Whisper Large v3 at 6.65% average WER on the Open ASR leaderboard.

These numbers confirm that the pure ASR stage can consume 50-260ms of the 800ms p50 budget, leaving
540-750ms for downstream entity correction, confidence routing, and LLM calls. The Small variant
(148ms, 7.84% WER) represents the best trade-off point for Rezolve's latency budget.

**Caveat**: Moonshine v2 reports no entity-specific accuracy on ecommerce terms. Adopting it would
require validating entity accuracy on gold-92.

**Contradiction between streaming methods**: CLAR [Huang2026] achieves superior entity accuracy
(B-WER 2.78%) but is tested only on offline Mandarin Chinese benchmarks. CTC streaming biasing
[Tsai2026] is latency-compatible but reports only keyword F-score improvements without absolute
numbers. Combining these two is an open engineering problem.

## Methodology Insights

* **Evaluation metric**: Replace aggregate WER with S2ER [Jiang2026] and E-WER [Kumar2026] for
  gold-92 evaluation. Compute Slot F1 on entity-tagged spans (brand names, product names, SKUs).
  Annotate gold-92 transcripts with entity span offsets to enable these metrics.

* **N-best hypothesis collection**: Collect top-5 beam search hypotheses from Whisper Turbo at
  inference time (zero training cost). Use LLM-Select [Kumar2026] to choose the most
  entity-informative hypothesis before downstream processing. This alone yields 33-35% relative
  E-WER reduction on Earnings-21 (ecommerce-analogous domain).

* **Whisper initial_prompt exploitation**: Implement the Ron2026 [Ron2026] pipeline: run Whisper on
  the utterance, extract entity candidates via NER + fuzzy matching (Levenshtein τ=0.75) against the
  brand/product catalog, construct a compact context prompt (≤224 tokens), and re-run Whisper with
  the prompt. Expected WER reduction: 17% relative on entity-dense domains. No model retraining
  required.

* **Retrieval index**: Build a phonetic-acoustic entity index using the CIF-alignment approach from
  CLAR [Huang2026] or the phonetic edit-distance retrieval from RASTAR [An2026]. Index should
  include all Rezolve brand names, product names, and SKUs with their phonetic representations (IPA
  or romanized).

* **RL fine-tuning of Whisper Turbo**: If model retraining is in scope, apply RLBR [Ren2026] reward
  shaping: assign alpha=5× reward multiplier to brand/product/SKU tokens during RL fine-tuning. The
  reference-aware trajectory augmentation is needed to prevent mode collapse on a small (~1000
  utterance) ecommerce entity dataset.

* **Adaptive reasoning depth**: For LLM post-correction, implement difficulty classification from
  A-STAR [An2026]: use phonetic similarity between ASR output and entity repository candidates as
  the difficulty signal. Apply full CoT only for phonetically ambiguous entities, direct lookup for
  clear matches. This achieves 30-40% token reduction vs. uniform CoT.

* **Session metadata context**: Implement metadata-driven reasoning chains from Poncelet2026
  [Poncelet2026]: at inference time, include product category, recent searches, and cart contents as
  text context alongside the audio. Fine-tune on (audio, session metadata, chain-of-thought, correct
  transcript) training tuples derived from gold-92 and production session logs.

* **Latency budget allocation**: Based on Moonshine v2 benchmarks [Kudlur2026]: allocate ~150ms for
  streaming ASR (Small model), ~150ms for entity retrieval + prompt construction, ~300ms for
  optional LLM post-correction (distilled 7B corrector). Total: ~600ms p50, leaving 200ms margin for
  network and routing overhead.

## Gaps and Limitations

**No ecommerce-domain benchmarks published in Jan-Jun 2026.** All surveyed papers evaluate on
standard benchmarks (LibriSpeech, AISHELL-1, CommonVoice, Earnings-21) or domain-specific datasets
(NBA, medical, air traffic control) that are not publicly ecommerce. The closest analog is
Earnings-21 (financial entity names). No paper in the survey period reports entity accuracy on a
dataset containing brand names, product SKUs, or ecommerce-specific terminology. Gold-92 remains the
only available evaluation resource for Rezolve's specific challenge.

**Latency data is absent for most entity correction methods.** Only Moonshine v2 [Kudlur2026] and
Tsai2026 [Tsai2026] provide concrete latency measurements. CLAR, RASTAR, RECOVER, Ren2026, and all
reasoning-based methods report accuracy improvements without per-utterance inference time
measurements. Latency compatibility with the 800ms p50 target must be estimated by proxy (model
size, number of LLM calls, reported token counts) or measured empirically.

**CLAR is evaluated on Mandarin Chinese only.** The strongest retrieval-based contextual biasing
method in the survey (CLAR, B-WER 2.78%) has no English evaluation. Whether CIF-based alignment
transfers to English phonology and Whisper's tokenization is an open empirical question.

**RASTAR and An2026 are Mandarin Chinese only.** Same limitation as CLAR: the adaptive
chain-of-thought NE correction results are on AISHELL-1 (Mandarin), not English.

**No paper addresses accented English specifically.** Gold-92 contains accented English
(investor-relations domain). None of the surveyed papers evaluate on accented English speech. The
LLM post-correction methods (Zheng2026 focuses on dysarthric speech) provide the closest analog, but
accent-induced entity errors may have different characteristics than dysarthria-induced errors.

**Shallow fusion has faded from the literature.** No standalone shallow fusion paper was found in
Jan-Jun 2026. Shallow fusion appears only as a baseline against which newer methods are compared
(CLAR outperforms shallow fusion on B-WER). Delayed Fusion (Hori et al., ICASSP 2025) was the prior
state of the art for LLM-ASR integration, but it is outside the Jan-Jun 2026 window and is not
included as a cited paper asset.

**RL fine-tuning methods require full model access.** RLBR [Ren2026] achieves the lowest B-WER but
requires full model fine-tuning. Rezolve's Whisper Turbo checkpoint is commercially licensed; RL
fine-tuning may conflict with usage terms and requires a training infrastructure investment.

## Recommendations for This Task

1. **Implement Ron2026's initial_prompt pipeline first (zero training cost, immediate testing on
   gold-92).** The six-agent pipeline [Ron2026] exploits Whisper's existing initial_prompt mechanism
   with a multi-agent LLM that extracts entities and constructs a context prompt. No model
   retraining. Expected gain: 17% relative WER reduction on entity-dense domains. This is the
   fastest path to a measurable improvement on gold-92 and should be the first prototyping task.

2. **Add N-best hypothesis collection + LLM-Select post-correction (RECOVER pattern).** After
   implementing the prompt pipeline, add top-5 hypothesis collection from Whisper's beam search and
   apply GPT-4o-based LLM-Select + entity correction as in Kumar2026 [Kumar2026]. Expected gain on
   entity-rich domains: 33-35% relative E-WER reduction. Combined with Ron2026, these two
   prompt-engineering approaches require no model training.

3. **Evaluate Moonshine v2 Small as a streaming ASR replacement.** Moonshine v2 Small (148ms, 7.84%
   WER) fits the latency budget with substantial margin [Kudlur2026]. Run it against gold-92 to
   check entity accuracy before investing in contextual biasing on top of Whisper Turbo. If
   Moonshine v2 + Ron2026 pipeline matches or exceeds Whisper Turbo + current dynamic injection,
   switch the base model.

4. **Replace WER with S2ER and entity Slot F1 as gold-92 evaluation metrics.** Adopt the evaluation
   approach from Jiang2026 [Jiang2026] and Zheng2026 [Zheng2026]. Annotate gold-92 transcripts with
   entity span offsets and implement E-WER computation on those spans. This directly measures the
   wrong-action rate impact of entity errors, providing a better optimization target for all
   follow-on tasks.

5. **Defer RL fine-tuning (RLBR) and Chinese-only methods (CLAR, RASTAR) to later phases.** These
   approaches require either full model retraining (RLBR) or English adaptation work (CLAR, RASTAR).
   They are the highest-potential techniques but require infrastructure investment. Prototype the
   prompt-based approaches first to establish a baseline, then invest in training-based approaches
   if the prompt baseline is insufficient.

## Comparison Against Whisper Turbo + Dynamic Context Injection

The current production pipeline injects a runtime hotword list into Whisper Turbo's decoder as a
flat word list. This is a form of contextual biasing but lacks: (a) phonetic-acoustic retrieval
precision, (b) N-best hypothesis diversity exploitation, and (c) semantic context from session
metadata.

**Techniques reporting gains over a runtime hotword-biasing baseline:**

* RLBR [Ren2026] reports B-WER improvements over SFT baseline (which is analogous to flat
  prompting): 0.59% vs. higher values at 100 bias words. Relative gain not explicitly reported
  against flat prompting baseline but implied to be significant.
* CLAR [Huang2026] reduces B-WER from 12.92% (baseline) to 2.78% — a 78% relative reduction. The
  CLAR baseline includes shallow fusion variants that are stronger than flat list prompting.
* Ron2026 [Ron2026] adds 17.0% relative WER reduction on top of Whisper using the initial_prompt
  mechanism — directly comparable to Rezolve's current approach since initial_prompt is the
  mechanism Whisper Turbo uses for dynamic context injection.

**Latency-compatible techniques (sub-800ms p50 for ~5-second utterance):**

| Technique | Estimated Latency | Basis |
| --- | --- | --- |
| Ron2026 initial_prompt pipeline | ~500-600ms | 148ms ASR + ~350-450ms multi-agent LLM |
| RECOVER LLM-Select (local 7B) | ~600ms | 150ms ASR + 300ms local 7B corrector |
| Tsai2026 CTC streaming biasing | ~200ms | 50-160ms streaming ASR + stateless biasing |
| Moonshine v2 Small + biasing | ~300ms | 148ms ASR + 150ms biasing overhead |
| RLBR (fine-tuned Whisper) | ~150ms | Model inference only, no post-processing |

**Techniques implementable without full model retraining:**

* Ron2026 [Ron2026]: Yes. Uses Whisper API + LLM agents. No weight modification.
* RECOVER [Kumar2026]: Yes. N-best collection + LLM post-correction. No training.
* Tsai2026 [Tsai2026]: Yes. CTC-WS operates on posteriors. No model modification.
* Poncelet2026 [Poncelet2026]: No. Requires speech-LLM fine-tuning on 400h training set.
* RLBR [Ren2026]: No. Requires full model RL fine-tuning.
* CLAR [Huang2026]: No. Requires training a CIF-based retrieval system on entity data.

**Estimated entity accuracy uplift vs. hotword baseline:**

| Technique | Estimated Entity Uplift | Evidence |
| --- | --- | --- |
| Ron2026 initial_prompt | ~15-20% relative WER reduction on entity spans | 17% rel. WER on NBA domain |
| RECOVER LLM-Select | ~30-35% relative E-WER reduction | Earnings-21 results |
| Ron2026 + RECOVER combined | ~35-45% relative entity error reduction | Additive, estimated |
| RLBR | ~50-60% relative B-WER reduction (vs. SFT) | LibriSpeech B-WER data |

**Ranked shortlist for prototyping (≤3 techniques):**

1. **Ron2026 initial_prompt multi-agent pipeline** — Zero training cost, directly applicable to
   Whisper Turbo, 17% relative WER reduction on entity-dense domain, latency-compatible. Prototype
   in the next task.

2. **RECOVER N-best + LLM-Select post-correction** — 33-35% relative E-WER on business domain, no
   training required, requires collecting top-5 hypotheses from Whisper beam search. Combine with
   Ron2026 in the same prototype task.

3. **RLBR or CLAR (pending evaluation of options 1-2)** — If prompt-based approaches achieve <50%
   reduction in wrong-action rate on gold-92, invest in training-based approaches. RLBR is preferred
   if model fine-tuning is permitted (reaches lowest B-WER). CLAR is preferred if an English
   adaptation is feasible (best retrieval architecture).

## Paper Index

### [Zheng2026]

* **Title**: Towards Robust Dysarthric Speech Recognition: LLM-Agent Post-ASR Correction Beyond WER
* **Authors**: Zheng et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2601.21347`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.21347/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: Demonstrates selective span rewriting for post-ASR correction achieving 14.51% WER
  reduction and +7.66pp Slot Micro F1. Introduces beyond-WER evaluation metrics (MENLI, Slot F1)
  applicable to Rezolve's wrong-action rate measurement.

### [Kudlur2026]

* **Title**: Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical Speech Applications
* **Authors**: Kudlur et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2602.12241`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12241/`
* **Categories**: `latency-profiling`, `stt-evaluation`
* **Relevance**: Provides concrete latency benchmarks (50-258ms on Apple M3) for streaming ASR,
  directly relevant to the 800ms p50 constraint. Demonstrates that ASR latency can be <150ms,
  leaving budget for post-correction.

### [An2026]

* **Title**: Retrieval-Augmented Self-Taught Reasoning Model with Adaptive Chain-of-Thought for ASR
  Named Entity Correction
* **Authors**: An et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2602.12287`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12287/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: Adaptive chain-of-thought reasoning for NE correction (17.96-34.42% relative NE-CER
  reduction) with 30-40% token efficiency gain vs. full CoT, relevant for latency-budget-conscious
  LLM post-correction design.

### [Ron2026]

* **Title**: Whisper: Courtside Edition — Multi-Agent LLM Pipeline for Domain-Specific ASR via
  Context Generation
* **Authors**: Ron et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2602.18966`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/`
* **Categories**: `entity-correction`, `stt-evaluation`, `whisper-finetuning`
* **Relevance**: Demonstrates 17.0% relative WER reduction using Whisper's initial_prompt with a
  multi-agent LLM pipeline — directly applicable to Rezolve's Whisper Turbo checkpoint without model
  retraining. Highest immediate actionability.

### [Kumar2026]

* **Title**: RECOVER: Robust Entity Correction via Agentic Orchestration of Hypothesis Variants for
  Evidence-based Recovery
* **Authors**: Kumar and Sachdeva
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2603.16411`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.16411/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: 8-46% relative E-WER reduction across five domains via N-best hypothesis selection.
  Earnings-21 (business entities) shows 33-35% reduction — closest analog to Rezolve's ecommerce
  entity challenge. No retraining required.

### [Huang2026]

* **Title**: CLAR: CIF-Localized Alignment for Retrieval-Augmented Speech LLM-Based Contextual ASR
* **Authors**: Huang et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2603.25460`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25460/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: State-of-the-art retrieval-based contextual biasing (B-WER 2.78%, −9.14pp vs.
  baseline). CIF-based alignment directly addresses the short-entity dilution problem for 1-3
  syllable brand names. English adaptation is the key open question.

### [Novitasari2026]

* **Title**: Contextual Biasing for ASR in Speech LLM with Common Word Cues and Bias Word Position
  Prediction
* **Authors**: Novitasari et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2604.12398`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: G2P-free phonetic biasing (16.3% bias word error reduction) applicable to product
  names and SKUs that resist standard phonemization. Complementary to retrieval-based approaches.

### [Tsai2026]

* **Title**: Contextual Biasing for Streaming ASR via CTC-based Word Spotting
* **Authors**: Tsai et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2605.18222`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.18222/`
* **Categories**: `entity-correction`, `latency-profiling`, `stt-evaluation`
* **Relevance**: Streaming-compatible contextual biasing via stateful CTC-WS, requiring no acoustic
  model modification. Applicable to Whisper's CTC auxiliary head for zero-training streaming entity
  detection.

### [Jiang2026]

* **Title**: Towards Human-Like Interactive Speech Recognition With Agentic Correction and Semantic
  Evaluation
* **Authors**: Jiang et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2605.29430`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.29430/`
* **Categories**: `entity-correction`, `stt-evaluation`, `confidence-routing`
* **Relevance**: Introduces S2ER metric (LLM-judged semantic error rate) that closely proxies
  wrong-action rate. Demonstrates S2ER collapse from ~20% to <2% across correction turns. The S2ER
  metric is recommended for gold-92 evaluation.

### [Ren2026]

* **Title**: RLBR: Reinforcement Learning with Biasing Rewards for Contextual Speech Large Language
  Models
* **Authors**: Ren et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2601.13409`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.13409/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: Lowest B-WER achieved via RL reward shaping (0.59%/2.11% at 100 bias words). The
  alpha=5× reward multiplier for bias words is a transferable training principle for any ASR
  fine-tuning on ecommerce entity data.

### [Poncelet2026]

* **Title**: Towards Deep Contextual Reasoning from Broad Descriptions for ASR with Speech-LLM via
  Metadata-Driven Reasoning Chains
* **Authors**: Poncelet and Van hamme
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2606.10838`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2606.10838/`
* **Categories**: `entity-correction`, `stt-evaluation`
* **Relevance**: Session metadata (product category, search queries) as broad contextual description
  for chain-of-thought NE correction (NE WER: 23.9% → 23.3%). The automated training data
  construction pipeline is applicable to Rezolve's session logs.
