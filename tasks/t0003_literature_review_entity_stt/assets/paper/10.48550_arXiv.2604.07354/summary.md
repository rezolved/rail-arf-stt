---
spec_version: "3"
paper_id: "10.48550_arXiv.2604.07354"
citation_key: "Durmus2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---

# Contextual Earnings-22: A Speech Recognition Benchmark with Custom Vocabulary in the Wild

## Metadata

* **File**: `files/durmus_2026_contextual-earnings-22.pdf`
* **Published**: 2026
* **Authors**: Berkin Durmus 🇺🇸, Chen Cen 🇺🇸, Eduardo Pacheco 🇺🇸, Arda Okan 🇺🇸,
  Atila Orhon 🇺🇸
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2604.07354`

## Abstract

The accuracy frontier of speech-to-text systems has plateaued on academic benchmarks. In contrast,
industrial benchmarks and adoption in high-stakes domains suggest otherwise. We hypothesize that the
primary difference between the two is contextual conditioning: Academic benchmarks are dominated by
frequently encountered general vocabulary that is relatively easy to recognize compared with rare and
context-defined custom vocabulary that has disproportionate impact on the usability of speech
transcripts. Despite progress on contextual speech-to-text, there is no standardized benchmark. We
introduce Contextual Earnings-22, an open dataset built upon Earnings-22, with realistic custom
vocabulary contexts to foster research and reveal latent progress. We set six strong baselines for
two dominant approaches: keyword prompting and keyword boosting. Experiments show both reach
comparable and significantly improved accuracy when scaled from proof-of-concept to large-scale
systems.

## Overview

This paper addresses a critical gap between academic STT benchmarks and real-world deployment
performance. The authors observe that top models on the Hugging Face OpenASR Leaderboard (as of
December 2025) cluster so tightly on standard WER that differences are nearly meaningless — yet
industrial users still struggle with transcript quality in specialized domains. The root cause
identified is custom vocabulary: domain-specific proper nouns (company names, product names, person
names) account for a disproportionate share of transcript failures even when overall WER looks good.

The paper introduces Contextual Earnings-22, a new benchmark built on the existing Earnings-22
corpus of earnings call recordings. The benchmark pairs 760 manually reviewed 15-second audio clips
with realistic keyword context lists targeting person, company, and product names. Critically, the
benchmark tests two context regimes: local context (only keywords present in the clip, an idealized
scenario) and global context (all keywords from the full one-hour earnings call, including many
distractors, a deployment-realistic scenario). This dual-regime design captures the precision-recall
trade-off that real-world deployments must navigate.

Six STT systems are benchmarked: three commercial APIs with keyword prompting (Deepgram Nova-3,
OpenAI Whisper-1, AssemblyAI), one open-source Whisper variant (Large-v3-turbo) with prompting,
and two keyword boosting configurations using the CTC-WS method with FastConformer and Parakeet-TDT
models. The evaluation shows that all systems improve keyword F-score when context is provided, but
WER changes are inconsistent. This decoupling motivates the paper's dual-metric reporting: keyword
F-score for contextual term accuracy, and WER for transcript-level quality.

The benchmark, transcripts, context lists, and evaluation harness are released publicly, filling a
gap where prior contextual STT work relied on private, synthetic, or narrowly-scoped datasets.

## Architecture, Models and Methods

**Dataset Construction Pipeline**: The benchmark derives from Earnings-22, a corpus of
approximately 1-hour earnings call recordings per company. A 55-file subset is processed. An
LLM-based named-entity extraction pass (GPT-5) runs over each call transcript to extract candidate
keywords across three categories: person names, company names, and product names. Candidate keywords
are post-processed deterministically: de-duplication across surface forms, punctuation and
whitespace normalization, and filtering of generic strings.

**Audio Clip Extraction**: Keyword mentions are located in transcripts and 15-second audio windows
are extracted, centered on each keyword mention. Forced alignment using a wav2vec-based aligner maps
transcript segments to audio boundaries. This yields clips with associated local context (keywords
in the clip) and global context (all keywords from the full source call).

**Manual Review**: All 760 candidate clips undergo human review checking transcript fidelity,
keyword validity, and alignment sanity. Review corrects mis-heard names, casing/punctuation
inconsistencies, acronym formatting, and boundary errors for multi-word entities. Result: **98.7%**
of samples are free of inaudible and `<unk>` tags; **29.5%** of clips receive word-level corrections
affecting **411 words** in total.

**Dataset Split**: 760 total clips split at source-audio level to prevent leakage. Validation:
130 clips, 9 source files, 9.14 source hours, 248 keyword instances, 134 unique keywords. Test:
630 clips, 46 source files, 58.47 source hours, 1,259 keyword instances, 738 unique keywords.

**Metrics**: Two complementary metrics. WER is standard word-level edit distance between hypothesis
and reference. Keyword Precision/Recall/F-score measures contextual term accuracy: a keyword is
True Positive (TP) only if it matches the reference text at the aligned location (computed via
minimum edit distance). False Negatives are keywords in reference but not hypothesis; False Positives
are keywords in hypothesis but not reference, including misaligned correct text.

**Evaluated Systems**:
* Deepgram Nova-3: commercial API with keyword prompting
* OpenAI Whisper-1: commercial API (Whisper Large v2 architecture) with prompt-based conditioning
* AssemblyAI: commercial API with keyword prompting
* Whisper OSS Large-v3-turbo: open-source Whisper with prompt parameter conditioning
* CTC-WS with STT-FastConformer-CTC-Large: keyword boosting via CTC-based word spotter, calibrated
  on validation split
* Argmax Parakeet-TDT-0.6B-v2 + CTC-WS: state-of-the-art open STT with CTC-WS boosting using a
  separate CTC backbone (Parakeet-TDT-CTC-110M) for keyword scoring; hyperparameters calibrated on
  validation split

## Results

* All six systems achieve higher keyword F-score with context than without — contextual conditioning
  consistently improves recognition of domain-specific terms across both prompting and boosting
  approaches.
* WER changes under context are smaller and less consistent than keyword F-score changes; some
  systems improve WER, others show little change, others worsen WER despite markedly better
  keyword F-score.
* OpenAI Whisper-1 WER **increases** under context conditioning in the benchmark, illustrating that
  keyword F-score and WER can move in opposite directions.
* Local context (no distractors) is systematically easier than global context — most systems move to
  higher F-score iso-curves under local context, reflecting higher precision and/or recall when
  context is concise and relevant.
* Global context primarily stresses precision — distractor keywords that are plausible but absent
  from the clip cause false positive insertions, reducing precision while recall may remain strong.
* The shift between local and global context differs by system family: some systems show large
  precision gains under local context (consistent with distractors being dominant error source);
  others show larger recall shifts, suggesting sensitivity to context formatting or conditioning
  mechanism.
* Keyword boosting (CTC-WS-based) and keyword prompting reach comparable keyword F-score when both
  are scaled to large-system configurations; proof-of-concept smaller configurations lag behind.
* Failure modes include: hallucination of context terms not spoken in audio, partial/empty outputs,
  and language switching when prompt perturbs decoding trajectory (observed as Swedish output for
  an English clip when context list contained non-English-sounding names).
* Manual review achieved **98.7%** artifact-free transcripts and corrected **411 words** across
  **29.5%** of clips, demonstrating substantial transcript quality improvement over raw Earnings-22.

Note: Exact per-system WER and keyword F-score values are presented as scatter plots in Figures 1
and 3; supplementary Tables S1 and S2 contain the exact numbers. The main text reports directional
findings with qualitative characterizations rather than inline exact values.

## Innovations

### First Standardized Contextual STT Benchmark with Realistic Distractors

Prior contextual STT work evaluates on private datasets, synthetic bias lists (rare LibriSpeech
words plus random distractors), or limited cleaned subsets of Earnings-22. Contextual Earnings-22
provides the first public benchmark pairing short domain-dense clips with naturally-occurring custom
vocabulary contexts — both precise local context and deployment-realistic global context with
distractors. This enables true apples-to-apples comparison between keyword prompting and keyword
boosting at scale.

### Dual-Regime Evaluation Design

The benchmark explicitly tests two context regimes corresponding to distinct real-world deployment
scenarios. Local context measures the idealized case where the keyword list is perfectly relevant.
Global context (full call-level keyword inventory) measures robustness to realistic noisy lists
containing many plausible-but-absent terms. This design reveals that precision and recall respond
differently to each regime and that system families have characteristic precision-recall profiles.

### Dual-Metric Reporting: Keyword F-Score Alongside WER

The paper argues that aggregate WER alone is an insufficient proxy for real-world transcript
utility, and demonstrates empirically that keyword F-score and WER can move in opposite directions.
The keyword-centric metric (precision/recall/F-score on the provided context list) directly measures
the aspect of transcript quality most impactful for domain-specific applications.

### Manual Transcript Correction at Scale

Rather than relying on original Earnings-22 transcripts, all 760 clips are manually reviewed and
corrected. The resulting ground-truth quality (**98.7%** artifact-free) is substantially higher than
prior cleaned Earnings-22 subsets, enabling reliable keyword-level evaluation.

## Datasets

* **Contextual Earnings-22** (this paper): 760 manually reviewed 15-second clips from 55 earnings
  call recordings, with keyword context lists per clip. Split: 130 validation, 630 test. Keywords
  cover person names, company names, and product names. Language: English. Intended release upon
  acceptance. Built on Earnings-22 base corpus.
* **Earnings-22** (Del Rio et al., 2022): Source corpus of approximately 1-hour earnings call
  recordings. Public, available at https://arxiv.org/abs/2203.15591.
* **ConEC** (Huang et al., 2024): Earnings call dataset with biasing lists from external sources
  (slides, earnings releases, participant metadata). Sentence-level segmented with WER-based
  evaluation on long-form audio. Public.
* **Earnings22-Cleaned-AA** (Artificial Analysis, 2026): Small cleaned subset of Earnings-22
  targeting reference quality but without contextual vocabulary or evaluation protocols.

## Main Ideas

* Custom vocabulary accuracy (entity-centric metrics) is a better proxy for real-world STT utility
  than aggregate WER when overall WER is near-saturated. This directly validates Rezolve's decision
  to measure entity accuracy on brand names, products, and investor-relations terms independently
  of overall WER on the gold-92 benchmark.
* Keyword prompting and keyword boosting both work at scale; the benchmark offers concrete baselines
  for both. For Rezolve, both Deepgram keyterm prompting and open-source CTC-WS boosting are worth
  evaluating on the gold-92 benchmark.
* The local-vs-global context distinction is practically critical: a global entity list covering all
  Rezolve products, brands, and investor-relations terms will include distractors for any given
  utterance, causing precision loss from false insertions that directly increases wrong-action rate.
  List curation or ranking strategies should be evaluated.
* Keyword precision and recall can move in opposite directions across systems under the same context
  list — reporting both is essential; a precision-first strategy may matter more than recall for
  Rezolve's wrong-action rate constraint.
* The benchmark construction pipeline (LLM NER + forced alignment + manual review) is a replicable
  recipe for curating domain-specific evaluation sets, applicable to building or extending the
  gold-92 benchmark with more entity types and verified ground truth.

## Summary

Durmus et al. introduce Contextual Earnings-22, a standardized benchmark for evaluating STT systems
on custom vocabulary — specifically proper nouns including person names, company names, and product
names in earnings call recordings. The motivation is a demonstrable mismatch between academic
benchmark WER (where top systems cluster tightly) and real-world transcript utility in domain-heavy
applications. The authors argue that contextual conditioning on a custom vocabulary list is the
primary differentiator, and that no prior public benchmark provides the structure to measure it
rigorously across competing systems.

The benchmark is built from 55 earnings call recordings in the Earnings-22 corpus. An LLM-based NER
pass (GPT-5) extracts keyword candidates; forced alignment clips 15-second audio windows around
keyword mentions; and manual review corrects transcript artifacts in all 760 clips, achieving
**98.7%** artifact-free quality with **29.5%** of clips requiring corrections. The benchmark tests
two context regimes — local (precise, no distractors) and global (full call inventory with
distractors) — and uses both WER and keyword Precision/Recall/F-score for evaluation. Six systems
are benchmarked: three commercial keyword-prompting APIs, one open-source Whisper, and two CTC-WS
keyword-boosting configurations.

All six systems improve keyword F-score under context conditioning, validating that both prompting
and boosting approaches help. However, WER changes are inconsistent — OpenAI Whisper-1's WER
worsens under context despite better keyword F-score — demonstrating that the two metrics capture
different aspects of quality and should both be reported. Global context stresses precision (
distractor-induced false insertions), while local context primarily improves recall. Keyword
boosting and keyword prompting reach comparable accuracy when scaled to large models. Failure modes
include hallucinations, partial outputs, and language switching when prompts containing
non-English-sounding names perturb decoding.

For this project, Contextual Earnings-22 is a methodological reference for both evaluation design
and entity correction strategy. The paper validates keyword-centric evaluation as a necessary
supplement to WER, directly aligned with Rezolve's entity accuracy goal on the gold-92 benchmark.
The dual-regime design maps onto Rezolve's scenario where a global entity vocabulary (all brands,
products, investor-relations terms) will contain distractors for any given utterance, and precision
loss from false insertions is a direct threat to the wrong-action rate target of less than 2%. The
benchmark's construction pipeline is a replicable recipe for extending the gold-92 benchmark, and
the comparison of prompting vs. boosting baselines provides concrete references for the entity
correction experiments planned in this project.
