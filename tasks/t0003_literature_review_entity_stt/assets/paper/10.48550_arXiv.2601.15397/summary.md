---
spec_version: "3"
paper_id: "10.48550_arXiv.2601.15397"
citation_key: "Wang2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# Beyond Prompting: Efficient and Robust Contextual Biasing for Speech LLMs via Logit-Space Integration (LOGIC)

## Metadata

* **File**: `files/wang_2026_logic-contextual-biasing-speech-llm.pdf`
* **Published**: 2026
* **Authors**: Peidong Wang 🇺🇸
* **Venue**: arXiv preprint (withdrawn v2, v1 accessible)
* **DOI**: `10.48550/arXiv.2601.15397`

## Abstract

The rapid emergence of new entities—driven by cultural shifts, evolving trends, and personalized
user data—poses a significant challenge for existing Speech Large Language Models (Speech LLMs).
While these models excel at general conversational tasks, their static training knowledge limits
their ability to recognize domain-specific terms such as contact names, playlists, or technical
jargon. Existing solutions primarily rely on prompting, which suffers from poor scalability: as the
entity list grows, prompting encounters context window limitations, increased inference latency, and
the "lost-in-the-middle" phenomenon. An alternative approach, Generative Error Correction (GEC),
attempts to rewrite transcripts via post-processing but frequently suffers from "over-correction",
introducing hallucinations of entities that were never spoken. In this work, we introduce LOGIC
(Logit-Space Integration for Contextual Biasing), an efficient and robust framework that operates
directly in the decoding layer. Unlike prompting, LOGIC decouples context injection from input
processing, ensuring constant-time complexity relative to prompt length. Extensive experiments using
the Phi-4-MM model across 11 multilingual locales demonstrate that LOGIC achieves an average 9%
relative reduction in Entity WER with a negligible 0.30% increase in False Alarm Rate.

## Overview

LOGIC addresses a practical failure mode in deploying Speech LLMs in production: these models are
strong at conversational tasks but poor at rare and domain-specific entities (contact names, song
titles, brand names, technical jargon). Two prevailing remedies both have critical shortcomings.
Prompting (in-context learning) requires injecting a phrase list into the system prompt, but this
collapses when the phrase list grows to thousands of entries — context window limits, quadratic
self-attention costs, and the "lost-in-the-middle" phenomenon degrade model behaviour to the point
where the model may simply recite the entire entity list rather than transcribe the audio. GEC
(Generative Error Correction), the other common approach, uses a text LLM to rewrite ASR output
against a bias list, but introduces hallucinations: the model inserts entities that were never
spoken, based on text similarity rather than acoustic evidence.

LOGIC operates at inference time by intercepting the logit vector at each auto-regressive decoding
step and adding a sparse bonus to tokens that form valid continuations of a prefix tree (Trie) built
from the entity phrase list. The Trie is tokenizer-aware, handling subword segmentation ambiguities
through a Multi-Path Tokenization strategy that inserts all valid token-level representations of
each entity. Two complementary strategies — Immediate Prefix Boosting (IPB) and Retroactive Score
Rectification (RSR) — govern the Recall/FAR tradeoff. IPB applies the biasing bonus from the Trie
root, maximising recall for short entities like surnames. RSR revokes accumulated bonuses for any
hypothesis path that diverges from the Trie before completing a full entity string, preventing the
model from hallucinating the tail of a partially matched entity.

The engineering implementation targets production throughput. Rather than iterating over the full
vocabulary at each step (>150,000 tokens for Phi-4-Mini), a custom sparse CUDA kernel updates only
the Trie-child indices, keeping the vocabulary iteration cost at O(D) where D is the maximum Trie
out-degree (typically fewer than 100 tokens). This is deployed as a custom LogitsProcessor on the
vLLM inference platform with zero-copy Trie state in GPU shared memory.

Results across 11 multilingual locales using Phi-4-Mini show consistent EWER reduction averaging
**9%** in the robust configuration (λ ≈ 0.4–0.6) and **17%** in an aggressive configuration (λ ≈
0.8–1.0), with real-time factor overhead of only **+2.8%** (RTF 0.0990 → 0.1018 on NVIDIA A100).
False Alarm Rate increase averages just **0.30%** in the robust setting, and is exactly 0% for
Korean (ko-KR), Spanish Mexico (es-MX), German (de-DE), and Japanese (ja-JP).

## Architecture, Models and Methods

**Base model**: Phi-4-Mini (open-source multimodal Speech LLM by Microsoft, SentencePiece tokenizer
with vocabulary >150,000 tokens). Phi-4-Mini processes audio directly in an end-to-end fashion
without a separate ASR cascade.

**Trie construction**: Given entity phrase list O = {E1, ..., EN}, each entity is tokenized under
multiple context variants (e.g., with/without leading whitespace, capitalisation variants) to handle
SentencePiece's context-dependent segmentation. All variants are inserted into a Token-Level Prefix
Tree (Trie) T. Each node stores valid next-token children.

**Logit integration formula** (Equation 1): At decoding step t with logit vector zt ∈ R^|V|, biased
logits z'*t are computed as: `z'_t[k] = zt[k] + I(k ∈ Children(s_{t-1}^(b))) · λ` where λ is the
biasing bonus hyperparameter and s*{t-1}^(b) is the current Trie state for beam hypothesis b.

**Immediate Prefix Boosting (IPB)**: Bonus λ is applied starting from the Trie root state (the first
token of any entity), unlike prior methods that skip the first token to avoid false alarms. This
maximises recall for short entities (e.g., two-character Chinese surnames) at the cost of higher
initial false alarm risk, which RSR then manages.

**Retroactive Score Rectification (RSR)**: Each hypothesis maintains a cumulative bonus accumulator
Φt. When a beam hypothesis diverges from the Trie mid-entity (mismatch), its beam score is penalized
by subtracting all accumulated bonuses: `Score_t = BaseScore_t - Φ_{t-1}`. This prevents the "sunk
cost" effect where partial matches inflate a hypothesis score enough to hallucinate the entity
completion.

**Inference implementation**: Custom LogitsProcessor for vLLM; sparse CUDA kernel updates only
Trie-child indices per step, O(D) per step with D < 100 typically; Trie in GPU shared memory
(zero-copy); fully vectorised for batch inference.

**Evaluation metrics**:

* WER: standard word error rate across full utterance
* EWER: entity word error rate computed only over ground-truth entity spans
* Entity Recall: percentage of ground-truth entities correctly transcribed
* FAR: false alarm rate — incorrect entity insertions per utterance
* RTF: real-time factor (processing time / audio duration), 90th percentile

**Experimental design**: Two configurations tested: Robust (λ ≈ 0.4–0.6, minimises FAR) and
Aggressive (λ ≈ 0.8–1.0, maximises recall). Evaluated on an internal Microsoft ASR test suite
covering 11 locales: en-US, ko-KR, zh-CN, es-ES, es-MX, en-GB, de-DE, fr-FR, it-IT, ja-JP, pt-BR.
Test sets focus on Person Names (PNAMEs); entity counts range from ~460 (de-DE) to >2100 (it-IT) per
locale. Hardware: NVIDIA A100 GPUs.

## Results

* Average EWER relative reduction: **9%** (robust, λ ≈ 0.4–0.6) across all 11 locales
* Average EWER relative reduction: **17%** (aggressive, λ ≈ 0.8–1.0) across all 11 locales
* Top robust gains: fr-FR **19%**, es-MX **17%**, de-DE **14%**, en-US **11%**
* Lowest robust gains: it-IT **2%**, es-ES **5%**, en-GB **5%**
* Aggressive gains vs robust gains delta: pt-BR +15 pp (21% total), zh-CN +11 pp (20% total), es-MX
  +11 pp (28% total), fr-FR +10 pp (29% total)
* Average FAR increase: **+0.30%** (robust), with exactly 0% increase for ko-KR, es-MX, de-DE, ja-JP
* en-US Entity Recall: baseline **75.00%** → LOGIC **77.53%** (robust)
* zh-CN Entity Recall: baseline **59.02%** → LOGIC **63.47%** (robust)
* ja-JP EWER: baseline **42.10** → LOGIC **39.51** (robust, **6%** relative improvement)
* RTF overhead: baseline **0.0990** → LOGIC **0.1018** = **+2.8%** (NVIDIA A100, 2210 phrases)
* WER: comparable or slightly improved vs baseline in most locales (en-US: 9.8 → 9.7, de-DE: 6.9 →
  6.8); no regression observed

## Innovations

### Logit-Space Biasing for Speech LLMs

Prior contextual biasing research targets traditional encoder-decoder ASR (Whisper, RNN-T,
CTC-based). LOGIC is among the first frameworks to apply Trie-based logit injection directly to
auto-regressive Speech LLMs that process raw audio end-to-end. Decoupling context injection from
input processing achieves O(1) complexity with respect to prompt length, solving the quadratic
self-attention scaling problem that makes prompting infeasible beyond a few dozen entities.

### Multi-Path Tokenization for Subword Trie Construction

SentencePiece tokenization is context-sensitive: the same entity string produces different token
sequences depending on surrounding characters (e.g., "Alex" → ["Alex"] vs. ["Al", "ex"] vs.
[" Alex"]). LOGIC inserts all valid tokenization variants into the Trie simultaneously, ensuring
entity coverage regardless of context position. This is a non-trivial engineering contribution with
direct impact on recall for any Speech LLM using subword tokenization.

### IPB + RSR Dual Strategy

The combination of Immediate Prefix Boosting and Retroactive Score Rectification provides a
principled tradeoff dial: IPB maximises sensitivity (recall) while RSR suppresses false alarms by
retroactively penalising partial match paths that fail to complete. This breaks the traditional
Recall/FAR tradeoff present in shallow fusion methods, achieving high recall (**+9–17%** EWER) with
near-zero FAR increase (**+0.30%** average, 0% for several locales).

### Sparse CUDA Kernel Implementation

The production-grade sparse kernel enables LOGIC to run in real-time on large-vocabulary Speech LLMs
(>150,000 tokens). By reducing per-step complexity from O(|V|) to O(D) where D is the maximum Trie
out-degree (<100 typically), LOGIC adds only **+2.8% RTF** overhead. This makes it deployable in
latency-sensitive voice assistant pipelines meeting the Rezolve 800 ms p50 budget.

## Datasets

* **Internal Microsoft PNAME test suite**: 11 locales (en-US, ko-KR, zh-CN, es-ES, es-MX, en-GB,
  de-DE, fr-FR, it-IT, ja-JP, pt-BR). Person Name (PNAME) utterances from naturally spoken audio.
  Entity counts per locale: ~460 entities (de-DE) to >2100 entities (it-IT). Not publicly available
  — internal Microsoft dataset.
* **Phi-4-Mini** used as the base model; no additional training was performed. Phi-4-Mini is
  publicly available on Hugging Face under a Microsoft Research License.

No public benchmark datasets (LibriSpeech, SLURP, etc.) were used. All evaluation was performed on
the internal Microsoft PNAME test suite.

## Main Ideas

* LOGIC's logit-space approach sidesteps the scalability wall of prompting entirely — the entity
  list can grow to thousands of phrases with no change in inference latency, making it suitable for
  Rezolve's full product/brand catalog injection without context window constraints.
* The **+2.8% RTF overhead** on A100 is highly relevant to the Rezolve 800 ms p50 budget: for a
  pipeline where STT decoding takes ~300–400 ms, adding less than 3% latency overhead is negligible
  compared to the **9–17% EWER improvement** on entity spans.
* RSR's hallucination suppression directly addresses a key risk for ecommerce voice AI — inserting a
  brand name or SKU that was never spoken causes incorrect purchase actions, which is worse than a
  generic WER error. RSR brings FAR increase to **+0.30%** average.
* The Multi-Path Tokenization strategy is essential for any Trie-based biasing applied to
  SentencePiece-tokenised Speech LLMs. Naive single-path Trie insertion will miss a substantial
  fraction of entities at non-sentence-initial positions.
* Prompting-based biasing fails catastrophically with even moderate entity list sizes (460 entities
  in de-DE), confirming that prompting is not viable for Rezolve's catalog-scale entity injection.
* LOGIC is evaluated only on Person Names; product names, brand names, and SKUs may have different
  phonetic/tokenization characteristics. Rezolve must validate LOGIC on its own entity types and may
  need to tune the bonus λ for each entity category.

## Summary

LOGIC (Logit-Space Integration for Contextual Biasing) addresses the inability of Speech LLMs to
reliably recognise domain-specific entities — brand names, contact names, product identifiers —
without the scalability failures of prompting or the hallucination failures of generative error
correction. The paper motivates the problem by demonstrating that prompting collapses with as few as
460 entities (exhibiting "list-vomiting" output) and that GEC introduces hallucinated entities based
on textual similarity rather than acoustic evidence. LOGIC is proposed as a decoding-layer
alternative that injects entity bias directly into the logit distribution at each auto-regressive
step using a subword-aware prefix tree, achieving O(1) complexity with respect to entity list size.

The method constructs a Token-Level Trie from the entity phrase list using Multi-Path Tokenization
to handle SentencePiece's context-dependent subword segmentation, then applies a sparse logit bonus
at each decoding step for tokens that extend a valid Trie path. Immediate Prefix Boosting (IPB)
fires the bias from the very first token of any entity to maximise recall for short entries, while
Retroactive Score Rectification (RSR) penalises hypotheses that accumulate partial-match bonuses but
diverge before completing the entity string. The CUDA implementation uses a sparse kernel with O(D)
per-step complexity, deployed as a vLLM LogitsProcessor with zero-copy GPU state.

Experiments using Phi-4-Mini across 11 multilingual locales on an internal Microsoft Person Name
test suite show **9% average relative EWER improvement** in a conservative configuration and **17%**
in an aggressive configuration, with average FAR increase of just **+0.30%** and RTF overhead of
only **+2.8%** on A100 GPUs. French (**19%**), German (**14%**), and Mexican Spanish (**17%**) see
the strongest improvements. The method generalises to logographic languages (zh-CN **9%**, ja-JP
**6%**) despite the added complexity of context-sensitive subword tokenization.

For the Rezolve STT project, LOGIC is directly actionable as a production-grade entity-biasing layer
for any Speech LLM (Phi-4, GPT-4o Audio) used as a replacement for or complement to Deepgram. Its
near-zero latency overhead is compatible with the 800 ms p50 voice-to-action budget, and RSR's
hallucination suppression is critical for ecommerce where false entity insertions cause incorrect
purchase actions. The key validation gap is whether the EWER improvements on Person Names transfer
to Rezolve's entity types (brand names, product lines, investor-relations terms), which have
different phonetic distributions and may require independent tuning of the biasing bonus λ per
entity category.
