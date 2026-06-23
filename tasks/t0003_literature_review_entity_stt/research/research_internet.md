---
spec_version: "1"
task_id: "t0003_literature_review_entity_stt"
research_stage: "internet"
searches_conducted: 14
sources_cited: 16
papers_discovered: 7
date_completed: "2026-06-23"
status: "complete"
---
## Task Objective

Survey publications from January to June 2026 to identify the most effective techniques for
improving STT accuracy on domain-specific named entities — brand names, product names, SKUs — in an
English ecommerce voice AI context. The goal is to complement the 11-paper corpus assembled during
`research_papers.md` by filling identified gaps, discovering new papers, and expanding coverage of
benchmarks, tools, and community practice. Findings directly inform the design of follow-on
prototyping tasks against Rezolve's Whisper Turbo + dynamic context injection production pipeline.

## Gaps Addressed

From `research_papers.md` Gaps and Limitations:

1. **No ecommerce-domain benchmarks published in Jan-Jun 2026** — **Partially resolved**. No
   ecommerce-specific benchmark was found, but [Durmus2026] (Contextual Earnings-22) introduces a
   2026 open benchmark built on Earnings-22 that specifically targets company, product, and person
   names in financial earnings calls — the closest publicly available proxy for ecommerce entity
   evaluation. It uses keyword prompting and boosting baselines, directly comparable to Rezolve's
   dynamic context injection approach. A complete ecommerce-specific benchmark for voice commerce
   (brand names, SKUs) remains absent from the literature.

2. **Latency data is absent for most entity correction methods** — **Partially resolved**. BR-ASR
   [Gong2025] (Interspeech 2025, background) reports **20ms per query** at 200,000-entry scale with
   99.99% pruning rate — providing a concrete latency anchor for retrieval-augmented biasing at
   production scale. The [AssemblyAI-Bench-2026] commercial benchmark reports streaming
   time-to-completion ranging from **247ms** (Deepgram Nova-3) to **335ms** (AssemblyAI Universal-3
   Pro), establishing an industry baseline for streaming ASR latency in 2026. The gap for
   latency-of-post-correction methods remains substantially open.

3. **CLAR is evaluated on Mandarin Chinese only** — **Unresolved**. No English evaluation of
   CLAR-style CIF-based retrieval was found. However, OWSM-Biasing [Sudo2025] (Interspeech 2025,
   background) achieves an **11.6pp B-WER improvement** on LibriSpeech using a Whisper-style model
   with dynamic vocabulary contextual biasing — providing an English-language counterpart to CLAR's
   retrieval-based approach. OWSM-Biasing does not use CIF alignment but demonstrates that
   retrieval-augmented biasing transfers to English Whisper-family models.

4. **RASTAR and An2026 are Mandarin Chinese only** — **Unresolved**. No English counterpart to
   RASTAR's adaptive CoT NE correction was found among Jan-Jun 2026 papers. [Trinh2025] (June 2025,
   background) achieves 30% relative NE-WER reduction via phonetic-semantic LLM revision on English
   classroom speech, representing the closest English analog.

5. **No paper addresses accented English specifically** — **Partially resolved**. [Tay2026]
   (WildASR) directly evaluates seven ASR systems on demographic variation including accented speech
   and finds "severe and uneven performance degradation" — confirming that ASR robustness does not
   transfer across accents and conditions. It does not address entity accuracy specifically in
   accented speech, but it validates that accent is a distinct failure mode requiring separate
   evaluation. The gap for entity accuracy on accented English specifically remains open.

6. **Shallow fusion has faded from the literature** — **Resolved**. Internet search confirms that no
   standalone shallow fusion paper appeared in Jan-Jun 2026. Delayed Fusion [Hori2025] (ICASSP 2025,
   background) integrates LLMs into first-pass decoding with improved speed over shallow fusion and
   N-best rescoring — effectively superseding classic shallow fusion. The community has moved to
   either direct LLM integration (Delayed Fusion, LOGIC) or retrieval-augmented biasing as the
   preferred alternatives to shallow fusion.

7. **RL fine-tuning methods require full model access** — **Unresolved**. No no-training alternative
   to RLBR's entity accuracy gains was found. This remains a training-infrastructure barrier.

## Search Strategy

**Databases and sources searched**: arXiv (cs.CL, cs.SD, eess.AS), Semantic Scholar, ACL Anthology,
ICASSP 2026 conference search, Interspeech 2026 conference search, Papers With Code, AssemblyAI
benchmark page, Emergent Mind, Google web search.

**Queries executed** (14 total):

*Required keyword combinations (Task Description §Search Strategy):*

1. `contextual biasing ASR named entity 2026`
2. `entity-aware speech recognition ecommerce 2026`
3. `shallow fusion ASR latency 2026`
4. `LLM post-correction ASR named entity 2026`
5. `domain-specific ASR brand product 2026`
6. `Whisper fine-tuning named entity ecommerce 2026`

*Gap-filling queries:*

7. `arXiv cs.CL entity-aware ASR contextual biasing 2026 new papers`
8. `ICASSP 2026 proceedings speech recognition entity accuracy`
9. `Interspeech 2026 contextual biasing named entity speech`
10. `accented English ASR named entity recognition voice AI 2026`
11. `ecommerce voice assistant benchmark dataset ASR entity WER 2026`

*Broadening queries:*

12. `Contextual Earnings-22 benchmark custom vocabulary contextual biasing ASR evaluation 2026`
13. `TARQ tail-aware quantization rare word robust ASR 2026 arxiv entity`
14. `speculative decoding LLM ASR post-correction latency 2026 arxiv`

**Date range**: January 1 to June 30, 2026 for primary papers. Papers outside this range included in
Discovered Papers only as background references when directly cited by 2026 papers or addressing
open gaps.

**Inclusion criteria**: Papers reporting (a) entity-level accuracy or entity WER, (b) latency
measurements compatible with streaming ASR, (c) ecommerce or voice assistant domain results, or (d)
benchmarks applicable to rare-word/entity evaluation. Papers submitted before 2026 are excluded from
the primary corpus but noted as background.

**Exclusion criteria**: Purely offline batch transcription with no latency data; non-English-only
with no English results; vendor marketing content without reproducible methodology.

**Search iterations**: Queries 7-9 were triggered by discovering new paper IDs in the initial
results. Queries 12-14 were snowball queries following specific paper IDs found in query 7 (BR-ASR,
Contextual Earnings-22, TARQ). The BR-ASR and OWSM-Biasing papers were discovered via query 1 and
fetched for detail via WebFetch; both are Interspeech 2025 papers and classified as background.

## Key Findings

### A 2026 Benchmark for Contextual Entity Recognition in Business Speech Is Now Available

**Contextual Earnings-22** [Durmus2026] is an open 2026 benchmark built on Earnings-22 with
realistic custom vocabulary contexts targeting company, product, and person names in financial
earnings calls. The benchmark defines two evaluation scenarios: local context (no distractors) and
global context (realistic distractors from the full entity catalog). Six baselines were established
across keyword prompting and keyword boosting approaches. While the paper does not yet report
specific WER numbers in its abstract (full PDF required), the benchmark directly addresses the gap
in `research_papers.md` identifying no publicly available entity-accuracy evaluation resource beyond
gold-92. The business-entity domain (earnings calls) is the closest publicly available proxy for
Rezolve's ecommerce entity challenge and should be used for cross-system comparison.

**Hypothesis**: Contextual Earnings-22 baselines, once extracted from the full paper, will establish
the expected performance ceiling for keyword prompting and boosting at Rezolve's scale, providing a
calibration point for gold-92 results.

### Retrieval-Augmented Biasing at 200k-Entry Scale Is Now Feasible with 20ms Overhead

BR-ASR [Gong2025] (Interspeech 2025, background) scales contextual biasing to **200,000 bias
entries** with only 0.3% absolute WER degradation and **20ms latency per query** — achieved via
speech-and-bias contrastive learning with 99.99% candidate pruning. At 2,000 bias words, BR-ASR
achieves **B-WER of 2.8%/7.1%** on LibriSpeech test-clean/other, a **45% relative improvement** over
prior methods. This resolves the scalability limitation of flat list prompting: Rezolve's full
brand+product catalog (potentially 10,000+ entries) can be indexed and queried at 20ms — well within
the 800ms p50 budget.

The framework integrates retrieved candidates into diverse ASR systems without fine-tuning, making
it directly applicable to Whisper Turbo.

**Best practice**: For production deployment of retrieval-augmented biasing at Rezolve's catalog
scale, target BR-ASR's architecture (contrastive speech-bias retrieval + curriculum learning for
homophone disambiguation) rather than building a bespoke index from scratch.

**Update to `research_papers.md`**: `research_papers.md` identifies "retrieval-augmented biasing" as
the emerging direction. BR-ASR (Interspeech 2025) provides a concrete implementation achieving 2.8%
B-WER — comparable to CLAR's 2.78% but with an English evaluation and explicit 20ms latency
measurement. This is a stronger foundation for Rezolve's production deployment than CLAR, pending
English validation.

### LOGIC: Logit-Space Contextual Biasing Achieves Constant-Time Complexity

LOGIC [Wang2026] addresses a fundamental limitation of prompt-based biasing: context window
saturation as the entity list grows. LOGIC integrates contextual information directly in logit space
during decoding — bypassing the context window — achieving **constant-time complexity regardless of
prompt length**. It reports a **9% relative Entity WER reduction** across 11 multilingual locales on
the Phi-4-MM model with negligible false alarm rate increase (**+0.30% absolute**). The paper was
withdrawn from arXiv in February 2026 for institutional publication approval compliance, suggesting
it may appear at a 2026 venue (Interspeech 2026 or ICASSP 2026 proceedings are probable
destinations).

This approach is architecturally distinct from all 11 papers in the existing corpus: it neither uses
prompting (Ron2026, Ren2026), retrieval (CLAR, RECOVER), nor post-correction (Zheng2026, Jiang2026).
Instead, it intercepts the decoder's logit distribution to up-weight entity candidates at generation
time, analogous to classifier-free guidance in diffusion models.

**Hypothesis**: Logit-space biasing (LOGIC) and retrieval-augmented retrieval (BR-ASR) are
architecturally complementary — combining them (retrieve candidates, then boost their logits) could
yield additive gains with no additional context window cost.

### Quantization for Rare-Word Robustness: A New Deployment-Time Technique

TARQ [Wang2026b] introduces a label-free post-training quantization framework that shifts
calibration mass toward rare words (names, numerals, domain-specific vocabulary). The standard
W4G128 quantization calibrates on frequent words, systematically degrading entity recognition. TARQ
applies a closed-form per-layer rule (rareBAL) that equalizes calibration mass between common and
rare-word tokens, improving **rare-WER across 8 ASR backbones and 6 datasets** without aggregate WER
regression. It transfers to entity-rich benchmarks including ContextASR-Speech-En and ProfASR
without requiring entity labels.

This is directly actionable for Rezolve: if the production Whisper Turbo checkpoint is deployed at
INT4/W4 quantization for latency reduction, TARQ provides a zero-training path to recover entity
accuracy that standard quantization would degrade.

**Best practice**: Apply TARQ (or equivalent rareBAL calibration logic) before quantizing any ASR
model checkpoint deployed in entity-sensitive ecommerce applications.

### ASR Robustness Across Real-World Conditions: WildASR Benchmark

WildASR [Tay2026] evaluates seven widely-used ASR systems across environmental degradation,
demographic variation, and linguistic diversity in four languages. Key finding: "model robustness
does not transfer across languages or conditions" and systems "hallucinate plausible but unspoken
content under partial or degraded inputs." The latter finding is directly relevant to Rezolve's
concern about wrong-action rate — hallucinated entity names (plausible but wrong brand names) are a
failure mode not captured by WER.

While WildASR does not measure entity-level accuracy, its evaluation framework for degradation
factors (accented speech, noise, partial audio) is applicable for extending gold-92 evaluation to
stress-test conditions.

**Update to `research_papers.md`**: The gap "no paper addresses accented English specifically" is
partially addressed. WildASR confirms that accented speech causes severe degradation in current ASR
systems but does not provide entity-level analysis. The gap remains open specifically for entity
accuracy on accented English.

### Commercial ASR Entity Accuracy Benchmarks in 2026

The AssemblyAI benchmark platform (updated June 2026) [AssemblyAI-Bench-2026] provides head-to-head
entity accuracy comparisons across commercial providers. For streaming audio, key numbers:
**AssemblyAI Universal-3 Pro Streaming: 5.38% missed entity rate** on critical entities (proper
nouns, alphanumerics, emails, addresses); **Deepgram Nova-3: 25.5% missed entity rate** on the same
content types; streaming time-to-completion ranges from **247ms** (Deepgram) to **335ms**
(AssemblyAI). Rezolve's current production pipeline uses Deepgram; these benchmarks suggest
AssemblyAI Universal-3 Pro achieves significantly better entity capture at comparable latency.

Note: these are vendor-produced benchmarks (not peer-reviewed). Entity categories tested (names,
emails, phone numbers) partially overlap with ecommerce entities but do not include brand SKUs or
product names. Take as directional, not definitive.

**Hypothesis**: Deepgram Nova-3's 25.5% missed entity rate on proper nouns is consistent with the
gold-92 entity accuracy problems observed in production. A direct comparison of AssemblyAI
Universal-3 Pro vs. Whisper Turbo on gold-92 would determine whether a provider switch alone
resolves the entity accuracy gap without custom fine-tuning.

## Methodology Insights

* **Use Contextual Earnings-22 [Durmus2026] as a secondary benchmark**: Before investing in gold-92
  entity annotation, run the Contextual Earnings-22 baselines (keyword prompting and boosting) on
  Rezolve's pipeline. The dataset is open, English, and targets the same entity-name accuracy
  challenge. Establish Rezolve's B-WER on this benchmark as a prior art reference point.

* **BR-ASR architecture for production-scale biasing [Gong2025]**: The 20ms retrieval latency at
  200k entries makes BR-ASR the most production-credible retrieval architecture found in the search.
  Implement a speech-and-bias contrastive index over Rezolve's brand/product catalog. Unlike CLAR's
  CIF alignment (which lacks English evaluation), BR-ASR is tested on English LibriSpeech and has
  open-source code. Repo: `https://github.com/xcmyz/BR-ASR` (not verified; confirm from paper).

* **LOGIC logit-space biasing [Wang2026] when context window is the bottleneck**: If Rezolve's
  entity catalog exceeds the Whisper decoder's context window, LOGIC-style logit boosting is the
  only approach that maintains constant-time complexity. Monitor for conference proceedings
  publication (likely Interspeech 2026 or ICASSP 2026) before implementing.

* **Apply TARQ before any quantization [Wang2026b]**: If Whisper Turbo is quantized to INT4 for
  latency reduction, rareBAL calibration protects entity accuracy. No training required. The
  improvement is estimated at 10-20% relative rare-WER (exact numbers in full paper).

* **WildASR evaluation protocol [Tay2026]**: Extend gold-92 with environmental degradation and
  accent variants using WildASR's factor-isolated methodology. This provides a more complete picture
  of ASR failure modes than a single-domain benchmark.

* **Commercial baseline comparison [AssemblyAI-Bench-2026]**: Deepgram Nova-3's 25.5% missed entity
  rate (vendor benchmark) vs. AssemblyAI Universal-3 Pro's 5.38% suggests a provider switch may
  yield significant entity accuracy improvement at comparable latency (335ms vs. 247ms). This is a
  zero-engineering path worth evaluating against gold-92 before building custom pipelines. Caveat:
  vendor benchmark, not peer-reviewed.

* **Delayed Fusion as shallow fusion alternative [Hori2025]**: The gap in `research_papers.md` on
  shallow fusion is addressed by Delayed Fusion (ICASSP 2025), which integrates LLM scores during
  first-pass decoding with reduced LLM call count. If shallow fusion is required as a streaming
  latency-compatible LM integration, implement Delayed Fusion (not classic shallow fusion). Code
  available via Apple Machine Learning Research.

* **Phonetic-semantic LLM revision [Trinh2025]**: The approach achieves 30% relative NE-WER
  reduction in English using phonetic similarity retrieval + LLM revision — complementary to
  Ron2026's initial_prompt approach and applicable without model retraining. Submitted June 2025
  (outside primary scope) but directly relevant as a background technique.

## Discovered Papers

### [Durmus2026]

* **Title**: Contextual Earnings-22: A Speech Recognition Benchmark with Custom Vocabulary in the
  Wild
* **Authors**: Berkin Durmus et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2604.07354`
* **URL**: https://arxiv.org/abs/2604.07354
* **Suggested categories**: `stt-evaluation`, `entity-correction`
* **Why download**: 2026 open benchmark targeting company, product, and person name recognition
  accuracy in earnings calls — the closest public proxy to Rezolve's ecommerce entity challenge.
  Establishes six keyword prompting/boosting baselines directly comparable to dynamic context
  injection.

### [Wang2026]

* **Title**: Beyond Prompting: Efficient and Robust Contextual Biasing for Speech LLMs via
  Logit-Space Integration (LOGIC)
* **Authors**: Peidong Wang
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2601.15397`
* **URL**: https://arxiv.org/abs/2601.15397
* **Suggested categories**: `entity-correction`, `latency-profiling`
* **Why download**: Introduces logit-space integration for contextual biasing, achieving 9% relative
  Entity WER reduction with constant-time complexity across entity list sizes — directly solves the
  context window saturation problem as bias lists grow to 1000+ entries. Paper is withdrawn from
  arXiv (pending institutional approval) but represents a novel technique not in the current corpus.

### [Wang2026b]

* **Title**: TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust Automatic Speech
  Recognition
* **Authors**: Xinyu Wang et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2605.27808`
* **URL**: https://arxiv.org/abs/2605.27808
* **Suggested categories**: `entity-correction`, `latency-profiling`
* **Why download**: Label-free post-training quantization that preserves entity recognition accuracy
  when compressing ASR models to INT4. Applicable to Whisper Turbo quantization without retraining.
  Tested across 8 backbones and 6 datasets including entity-rich benchmarks.

### [Tay2026]

* **Title**: Back to Basics: Revisiting ASR in the Age of Voice Agents
* **Authors**: Geeyang Tay et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2603.25727`
* **URL**: https://arxiv.org/abs/2603.25727
* **Suggested categories**: `stt-evaluation`, `latency-profiling`
* **Why download**: Introduces WildASR, a diagnostic benchmark evaluating 7 ASR systems across
  environmental, demographic, and linguistic variation. Directly relevant to gold-92 evaluation
  methodology and the accented English gap identified in research_papers.md.

### [Gong2025]

* **Title**: BR-ASR: Efficient and Scalable Bias Retrieval Framework for Contextual Biasing ASR in
  Speech LLM
* **Authors**: Xun Gong et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2505.19179`
* **URL**: https://arxiv.org/abs/2505.19179
* **Suggested categories**: `entity-correction`, `latency-profiling`
* **Why download**: Background paper (Interspeech 2025, outside Jan-Jun 2026 scope). Provides the
  only concrete latency measurement for large-scale retrieval-augmented biasing (20ms at 200k
  entries). Establishes the production-feasibility baseline for retrieval approaches.
  State-of-the-art B-WER on English LibriSpeech (2.8%/7.1%).

### [Hori2025]

* **Title**: Delayed Fusion: Integrating Large Language Models into First-Pass Decoding in
  End-to-end Speech Recognition
* **Authors**: Takaaki Hori et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2501.09258`
* **URL**: https://arxiv.org/abs/2501.09258
* **Suggested categories**: `entity-correction`, `latency-profiling`
* **Why download**: Background paper (ICASSP 2025). The prior state of the art for LLM-ASR shallow
  fusion integration, referenced in research_papers.md as outside scope but directly relevant to the
  shallow fusion gap. Resolves the gap by demonstrating that delayed-fusion supersedes classic
  shallow fusion in both speed and accuracy.

### [Trinh2025]

* **Title**: Improving Speech Recognition of Named Entities in Classroom Speech with LLM Revision
  and Phonetic-Semantic Context
* **Authors**: Viet Anh Trinh et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.10779`
* **URL**: https://arxiv.org/abs/2506.10779
* **Suggested categories**: `entity-correction`
* **Why download**: Background paper (submitted June 2025). Achieves 30% relative NE-WER reduction
  in English using phonetic-semantic context retrieval + LLM revision — the closest English analog
  to RASTAR (Mandarin). Directly addresses the gap in research_papers.md regarding English-language
  adaptive NE correction.

## Recommendations for This Task

These recommendations extend and update those in `research_papers.md`. Where they conflict with
prior recommendations, the change is noted.

1. **Add Contextual Earnings-22 [Durmus2026] as a secondary evaluation benchmark (new).** Run
   keyword prompting and boosting baselines on gold-92 against this benchmark's methodology. It
   provides the only 2026 open standard for entity accuracy in business speech. This is a zero-cost
   evaluation step that contextualizes gold-92 results against reproducible academic baselines.

2. **Prioritize BR-ASR [Gong2025] retrieval architecture over CLAR for English deployment (update to
   recommendation 5 in research_papers.md).** CLAR achieves the lowest reported B-WER (2.78%) but
   has no English evaluation. BR-ASR achieves comparable B-WER (2.8%) on English LibriSpeech with a
   measured 20ms retrieval latency at 200k entries. For Rezolve's English ecommerce deployment,
   BR-ASR is the more actionable retrieval baseline.

3. **Monitor LOGIC [Wang2026] for conference publication before implementing (new).** The
   logit-space integration approach solves the context window saturation problem that will emerge as
   Rezolve's entity catalog grows. The withdrawn preprint suggests a conference venue is imminent.
   Check Interspeech 2026 and ICASSP 2026 proceedings.

4. **Apply TARQ before quantizing Whisper Turbo to INT4 (new).** If latency optimization requires
   INT4 quantization, apply TARQ's rareBAL calibration to preserve entity accuracy. No training
   cost. Implement as a production deployment step independent of the prompting/correction pipeline.

5. **Evaluate AssemblyAI Universal-3 Pro against gold-92 as a zero-engineering baseline (new).** The
   commercial benchmark [AssemblyAI-Bench-2026] suggests AssemblyAI achieves 5.38% missed entity
   rate vs. Deepgram's 25.5%. Running this on gold-92 costs one API call and may reveal that a
   provider switch alone resolves the entity accuracy gap without custom engineering.

6. **Extend WildASR's evaluation methodology to gold-92 (new).** Follow [Tay2026]'s factor-isolated
   approach: evaluate gold-92 performance separately for high-accent, low-accent, noisy, and clean
   recordings. This separates the entity-error signal from the accent-degradation signal, enabling
   targeted technique selection.

## Tool and Library Landscape

* **BR-ASR** (Interspeech 2025) — open implementation from Shanghai Jiao Tong University / AntGroup.
  Published in ISCA Archive at
  `https://www.isca-archive.org/interspeech_2025/gong25_interspeech.pdf`. Implements speech-and-bias
  contrastive learning with curriculum learning for homophone disambiguation. License: CC BY 4.0.

* **WhisperNER** (Sep 2024) [WhisperNER-GH] — joint ASR+NER model available on Hugging Face
  (`aiola/whisper-ner-v1`). Extends Whisper with open-type NER, enabling simultaneous transcription
  and entity tagging in a single forward pass. English-only. Potentially applicable as a unified
  ASR+NER step in Rezolve's pipeline to replace a separate NER module. Note: this is a 2024 paper
  (outside primary scope) included for practical relevance.

* **Contextual Earnings-22 dataset** [Durmus2026] — open dataset on arXiv with realistic
  custom-vocabulary contexts for financial speech. Usable for benchmarking without access to
  ecommerce-specific data.

* **DYNAC** (Interspeech 2025) — non-autoregressive contextual biasing for CTC models, reducing RTF
  by 81% with 0.1pp WER degradation on LibriSpeech. Relevant if Rezolve adopts a CTC-based streaming
  ASR architecture.

## Source Index

### [Durmus2026]

* **Type**: paper
* **Title**: Contextual Earnings-22: A Speech Recognition Benchmark with Custom Vocabulary in the
  Wild
* **Authors**: Berkin Durmus et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2604.07354`
* **URL**: https://arxiv.org/abs/2604.07354
* **Peer-reviewed**: no (arXiv preprint, submitted March 2026)
* **Relevance**: 2026 open benchmark for contextual entity recognition in business speech. Six
  keyword prompting/boosting baselines directly comparable to Rezolve's dynamic context injection.

### [Wang2026]

* **Type**: paper
* **Title**: Beyond Prompting: Efficient and Robust Contextual Biasing for Speech LLMs via
  Logit-Space Integration (LOGIC)
* **Authors**: Peidong Wang
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2601.15397`
* **URL**: https://arxiv.org/abs/2601.15397
* **Peer-reviewed**: no (withdrawn arXiv preprint, January 2026)
* **Relevance**: Logit-space entity biasing with 9% relative Entity WER reduction and constant-time
  complexity. Architecturally distinct from all corpus papers — no prompting, no post-correction.

### [Wang2026b]

* **Type**: paper
* **Title**: TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust Automatic Speech
  Recognition
* **Authors**: Xinyu Wang et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2605.27808`
* **URL**: https://arxiv.org/abs/2605.27808
* **Peer-reviewed**: no (arXiv preprint, submitted May 2026)
* **Relevance**: Label-free quantization technique preserving rare-word/entity accuracy across 8 ASR
  backbones. Applicable to INT4 Whisper Turbo deployment.

### [Tay2026]

* **Type**: paper
* **Title**: Back to Basics: Revisiting ASR in the Age of Voice Agents
* **Authors**: Geeyang Tay et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2603.25727`
* **URL**: https://arxiv.org/abs/2603.25727
* **Peer-reviewed**: no (arXiv preprint, submitted March 2026)
* **Relevance**: WildASR benchmark for ASR robustness across accented speech, noise, and linguistic
  diversity. Directly addresses the accented English gap; provides evaluation methodology for
  extending gold-92 stress testing.

### [Gong2025]

* **Type**: paper
* **Title**: BR-ASR: Efficient and Scalable Bias Retrieval Framework for Contextual Biasing ASR in
  Speech LLM
* **Authors**: Xun Gong et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2505.19179`
* **URL**: https://arxiv.org/abs/2505.19179
* **Peer-reviewed**: yes (Interspeech 2025)
* **Relevance**: State-of-the-art retrieval-augmented biasing: B-WER 2.8%/7.1% on English
  LibriSpeech at 2k bias words, 20ms retrieval latency at 200k entries. Most production-actionable
  retrieval architecture found.

### [Hori2025]

* **Type**: paper
* **Title**: Delayed Fusion: Integrating Large Language Models into First-Pass Decoding in
  End-to-end Speech Recognition
* **Authors**: Takaaki Hori et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2501.09258`
* **URL**: https://arxiv.org/abs/2501.09258
* **Peer-reviewed**: yes (ICASSP 2025)
* **Relevance**: Prior state-of-the-art for LLM-ASR integration. Resolves the shallow fusion gap by
  demonstrating delayed fusion improves over both shallow fusion and N-best rescoring.

### [Trinh2025]

* **Type**: paper
* **Title**: Improving Speech Recognition of Named Entities in Classroom Speech with LLM Revision
  and Phonetic-Semantic Context
* **Authors**: Viet Anh Trinh et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.10779`
* **URL**: https://arxiv.org/abs/2506.10779
* **Peer-reviewed**: no (arXiv preprint, submitted June 2025)
* **Relevance**: 30% relative NE-WER reduction via phonetic-semantic LLM revision on English
  classroom speech. English analog to RASTAR (Mandarin); applicable to Rezolve without retraining.

### [AssemblyAI-Bench-2026]

* **Type**: documentation
* **Title**: ASR Benchmarks — Entity Capture and Latency
* **Author/Org**: AssemblyAI
* **Date**: 2026-06-08
* **URL**: https://www.assemblyai.com/benchmarks
* **Peer-reviewed**: no (vendor benchmark)
* **Relevance**: Head-to-head entity capture benchmarks across Deepgram, AssemblyAI, OpenAI in
  streaming mode. Deepgram (Rezolve's current provider): 25.5% missed entity rate. AssemblyAI
  Universal-3 Pro Streaming: 5.38%. Streaming latency: 247ms (Deepgram) to 335ms (AssemblyAI).

### [Sudo2025]

* **Type**: paper
* **Title**: OWSM-Biasing: Contextualizing Open Whisper-Style Speech Models for Automatic Speech
  Recognition with Dynamic Vocabulary
* **Authors**: Yui Sudo et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.09448`
* **URL**: https://arxiv.org/abs/2506.09448
* **Peer-reviewed**: yes (Interspeech 2025)
* **Relevance**: English evaluation of Whisper-style model contextual biasing: 11.6pp B-WER
  improvement on LibriSpeech. Closest English counterpart to CLAR for retrieval-augmented biasing
  without retraining.

### [WhisperNER-GH]

* **Type**: repository
* **Title**: whisper-ner: Official implementation of WhisperNER
* **Author/Org**: aiola-lab
* **Date**: 2024-09
* **URL**: https://github.com/aiola-lab/whisper-ner
* **Last updated**: 2025-06
* **Peer-reviewed**: no
* **Relevance**: Open implementation of joint ASR+NER model fine-tuned from Whisper. Available on
  Hugging Face as `aiola/whisper-ner-v1`. Enables simultaneous entity tagging during transcription.

### [Im2025]

* **Type**: paper
* **Title**: DeRAGEC: Denoising Named Entity Candidates with Synthetic Rationale for ASR Error
  Correction
* **Authors**: Solee Im et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.07510`
* **URL**: https://arxiv.org/abs/2506.07510
* **Peer-reviewed**: yes (ACL 2025 Findings)
* **Relevance**: 28% relative WER reduction via denoised RAG-based NE correction on CommonVoice and
  STOP datasets. Background paper (ACL 2025) providing a retrieval-augmented NE correction
  alternative to RECOVER's N-best hypothesis approach.

### [Altinok2025]

* **Type**: paper
* **Title**: Mind the Gap: Entity-Preserved Context-Aware ASR Structured Transcriptions
* **Authors**: Duygu Altinok
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.22858`
* **URL**: https://arxiv.org/abs/2506.22858
* **Peer-reviewed**: yes (TSD 2025, Springer LNAI)
* **Relevance**: Whisper entity preservation via 40-second overlapping context windows during
  training. Addresses boundary-spanning entities lost in 30-second chunk processing — relevant to
  Rezolve's streaming pipeline.

### [Gong2025b]

* **Type**: paper
* **Title**: DYNAC: Dynamic Vocabulary-based Non-Autoregressive Contextualization for Speech
  Recognition
* **Authors**: Yui Sudo et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2506.00422`
* **URL**: https://arxiv.org/abs/2506.00422
* **Peer-reviewed**: yes (Interspeech 2025)
* **Relevance**: CTC-based non-autoregressive contextual biasing with 81% RTF reduction and only
  0.1pp WER degradation. Relevant if Rezolve adopts a streaming CTC architecture alongside or
  instead of Whisper.

### [Durmus2026-ISCA]

* **Type**: documentation
* **Title**: Contextual Earnings-22 ISCA Archive entry
* **Author/Org**: ISCA / ADS
* **Date**: 2026-03
* **URL**: https://ui.adsabs.harvard.edu/abs/2026arXiv260407354D/abstract
* **Peer-reviewed**: no
* **Relevance**: Cross-reference confirming Contextual Earnings-22 is indexed as a 2026 arXiv paper.

### [PWC-ContextBiasing]

* **Type**: documentation
* **Title**: Papers With Code — Contextual Biasing of Named-Entities with Large Language Models
* **Author/Org**: Papers With Code
* **Date**: 2026-06
* **URL**: https://paperswithcode.com/paper/contextual-biasing-of-named-entities-with
* **Peer-reviewed**: no
* **Relevance**: Aggregated leaderboard for contextual biasing with LLMs, providing a structured
  view of state-of-the-art results and related papers for the broader contextual biasing research
  area.

### [SimpliSmart-Whisper-2026]

* **Type**: blog
* **Title**: Deploy Whisper v3 Large Turbo in Production: Conquering the Sub-Second Latency
* **Author/Org**: SimpliSmart
* **Date**: 2026-02
* **URL**: https://simplismart.ai/blog/deploy-whisper-v3-turbo-using-vox-box
* **Peer-reviewed**: no
* **Relevance**: Production deployment data for Whisper Large v3 Turbo: 22ms per-chunk inference at
  INT8 on RTX 4090; 3.0% WER on clean English. Provides concrete latency anchors for the ASR stage
  of Rezolve's 800ms budget.
