---
spec_version: "3"
paper_id: "10.48550_arXiv.2605.27808"
citation_key: "Wang2026b"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---

# TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust Automatic Speech Recognition

## Metadata

* **File**: `files/wang_2026_tarq-rare-word-quantization.pdf`
* **Published**: 2026
* **Authors**: Xinyu Wang 🇨🇦, Ziyu Zhao 🇨🇦, Ke Bai 🇺🇸, Silin Meng 🇺🇸,
  Dongming Shen 🇺🇸, Xiao-Wen Chang 🇨🇦, Yixuan He 🇺🇸
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2605.27808`

## Abstract

Data-aware post-training quantization (PTQ) minimizes a per-token reconstruction loss on a
small calibration corpus, implicitly weighting positions by their empirical frequency. For
Automatic Speech Recognition (ASR), this misaligns with tail-sensitive risk: names, numerals,
and domain-specific words receive proportionally little calibration mass. We propose Tail-Aware
Reconstruction Quantization (TARQ), a label-free PTQ framework that shifts calibration toward
the lexical tail via RAREBAL, a closed-form per-Linear-layer rule equalizing common/tail mass,
paired with a metric-consistent residual correction. TARQ requires no entity labels, no curated
calibration set, no validation decoding, and no additional training. Across eight ASR backbones
and six datasets at W4G128, TARQ improves mean rare-Word Error Rate (rare-WER) without an
aggregate-WER regression, achieves the lowest cross-corpus rare-WER swing among compared
methods, and transfers to entity-rich benchmarks (ProfASR, ContextASR-Speech-En) without
entity supervision.

## Overview

TARQ addresses a structural bias in data-aware post-training quantization (PTQ) for ASR
models. Standard PTQ methods such as GPTQ and AWQ minimize a reconstruction loss averaged
over calibration token positions. Because natural speech calibration corpora follow Zipfian
token-frequency distributions, common words dominate the calibration signal, and rare tokens
— including names, numerals, and domain-specific terms — contribute only in proportion to
their frequency. For aggregate WER this is harmless, but for entity-sensitive ASR (where brand
names, SKUs, and proper nouns drive business decisions), it silently degrades the very words
that matter most.

The paper first performs a diagnostic analysis showing that across all eight tested ASR
backbones, rare tokens hold only about 6.9% of the per-Linear-layer calibration trace mass
under the raw second-moment metric, even though they represent a much larger share of
recognition risk. The authors show that tighter optimization of the same frequency-weighted
objective (via OmniQuant iteration sweeps) does not close the gap — the asymmetry sits in
the calibration metric itself, not in solver quality. This is a key methodological distinction:
the problem is the loss function, not how well it is minimized.

TARQ addresses this through two closed-form components. RAREBAL replaces the standard
per-Linear-layer calibration metric with one that equalizes trace mass between common and
rare token groups, computed via a single scalar per layer derived from statistics already
accumulated during normal PTQ calibration. A propagation-aware residual correction keeps
the sequential layer-by-layer PTQ sweep aligned with the rebalanced metric, preventing drift
from earlier quantized layers from reverting the objective geometry.

The method is evaluated across 8 ASR backbones (five Whisper sizes, two Qwen3-ASR sizes,
Voxtral-Mini-3B) on six standard datasets and two entity-rich benchmarks. TARQ achieves
rank-1 mean plain WER on all eight backbones and rank-1 mean rare-WER on six of eight.
INT4 quantization with TARQ yields 1.06x–2.18x GPU speedups and 33%–67% VRAM reductions
over FP16 baselines, including tipping Whisper-large-v3 into CPU real time (RTF 0.87 vs
FP16 RTF 2.01).

## Architecture, Models and Methods

**Quantization setting.** All experiments use weight-only 4-bit group quantization with group
size 128 (W4G128). Activations remain in FP16. The quantized weight is a round-to-nearest
INT4 approximation using per-group scale: `W_hat = s * clamp(round(W/s), -8, 7)` where
`s = (max(W) - min(W)) / 15`.

**Calibration metric reformulation.** Standard PTQ data-aware methods minimize the
reconstruction loss `L_rec = (1/N) * sum_t ||DeltaW * x_t||^2` averaged uniformly over
all N calibration token positions. The per-layer second moment `H = sum_t x_t x_t^T` inherits
the frequency distribution of the calibration corpus. TARQ partitions positions into rare
(wordfreq Zipf score < 3, i.e., fewer than 1 occurrence per million words) and common
(Zipf >= 3). The group-partitioned second moments are `H_common` and `H_tail`.

**RAREBAL.** The rebalanced metric is `H_rB = H_common + lambda * H_tail`, where the
per-layer coefficient `lambda = tr(H_common) / tr(H_tail)` is derived by trace equalization,
setting each group's contribution to the reconstruction loss to be equal (50/50 split). This
is a closed-form, single-scalar operation per Linear layer. A cost-ratio parameter c can
adjust the split (c=1 defaults to equal weighting); ablation over c in [0.25, 4] confirms
c=1 is near-optimal.

**Propagation-aware residual correction.** The input-error cross-moment `H_delta = sum_t
(x_fp_t - x_t) x_t^T` captures drift from prior quantized layers. The propagation direction
is `D = W * H_delta * (H_rB + delta*I)^-1` and a scalar `alpha*` is fit by one-dimensional
least squares. The corrected target `W + alpha*D` is projected back into the W4G128 lattice.

**Backbones.** Whisper-tiny (39M), Whisper-base (74M), Whisper-small (244M), Whisper-medium
(769M), Whisper-large-v3 (1.55B), Qwen3-ASR-0.6B (600M), Qwen3-ASR-1.7B (1.7B),
Voxtral-Mini-3B-2507 (3B). All use publicly released checkpoint weights.

**Calibration.** 128 calibration utterances primary (LS-clean). Six calibration corpora tested:
LS-clean, SPGI, VoxPopuli, and three rare-density-sampled pools (r-top, r-mix, r-cross).

**Baselines.** RTN (round-to-nearest), GPTQ, AWQ, OmniQuant (iterative), GenPTQ
(mixed-precision 4-bit average). TARQ is hosted on GPTQ-style column-sweep solver.

**Evaluation.** Six ASR test sets subsampled to 3,000 utterances each (VoxPopuli uses full
1,842-utterance test). Two entity-rich benchmarks: ProfASR and ContextASR-Speech-En.
Metrics: plain WER and rare-WER (reference denominator restricted to Zipf < 3 tokens).
Hardware: single A100 GPU; CPU benchmarks on AMD EPYC 7V12 at 8 threads.

## Results

* TARQ achieves **rank-1 mean plain WER** on all 8 ASR backbones under LS-clean calibration
* TARQ achieves **rank-1 mean rare-WER** on 6 of 8 backbones; remaining 2 cells lose to
  GenPTQ by a thin margin
* Whisper-tiny plain WER: TARQ **14.03%** vs GPTQ **17.86%** vs AWQ **31.86%**;
  rare-WER: TARQ **55.93%** vs GPTQ **60.04%** vs AWQ **84.10%**
* Whisper-base rare-WER: TARQ **43.96%** vs GPTQ **47.57%** — improvement of **3.61 pp**
* Qwen3-ASR-0.6B rare-WER: TARQ **32.78%** vs GPTQ **34.11%** (**1.33 pp** gain)
* Cross-corpus rare-WER swing: TARQ **0.63 pp** vs OmniQuant **0.78 pp** vs GPTQ **2.51 pp**
  vs AWQ **5.95 pp** — TARQ is the most calibration-stable method
* Entity-rich transfer (W-base, ContextASR-Speech-En): TARQ plain WER **45.32%** vs GPTQ
  **46.42%** (**1.10 pp**); rare-WER **68.70%** vs GPTQ **69.60%** (**0.90 pp**)
* Entity-rich transfer (W-base, ProfASR): TARQ **12.92%** plain vs GPTQ **13.41%**;
  rare-WER **54.18%** vs GPTQ **54.97%** (**0.79 pp**)
* GPU speedup Qwen3-ASR-1.7B: **2.18x** vs FP16; VRAM reduction **46%**
* GPU speedup Whisper-large-v3: **1.63x** vs FP16; VRAM reduction **67%**
* CPU: Whisper-large-v3 reaches real time at RTF **0.87** (8 threads) vs FP16 RTF **2.01**
* Component ablation (W-base): RAREBAL alone rare-WER **44.63%**; residual alone **45.07%**;
  combined TARQ **43.96%** — RAREBAL provides most of the gain

## Innovations

### Diagnosis of Frequency-Weighted PTQ Damage

The paper provides the first systematic diagnosis that rare tokens hold only ~6.9% of
per-Linear-layer calibration trace mass across diverse ASR backbones, and crucially, that
tighter solver optimization does not close the rare-WER gap — the problem is structural to the
metric. This distinguishes between a metric-level fix (TARQ) and solver-level fixes (more
iterations, better optimizers), ruling out the latter as a solution class.

### RAREBAL: Label-Free Closed-Form Trace Equalization

RAREBAL is the first closed-form calibration metric rebalancing for rare-word-robust ASR PTQ.
It requires only the per-layer activation second moments already accumulated during PTQ,
computes a single scalar per Linear layer, and needs no entity labels, no curated corpus, no
backward pass, and no additional data. The cost ratio c=1 (equal common/tail weighting) is
algebraically principled and empirically near-optimal across backbones.

### Metric-Consistent Residual Correction

The residual correction keeps the sequential PTQ layer sweep aligned with the RAREBAL-
rebalanced metric, preventing the frequency-weighted geometry from re-asserting through
propagation drift. This makes TARQ internally consistent as a PTQ framework, not just a
per-layer patch.

### Cross-Corpus Calibration Stability

TARQ's 0.63 pp cross-corpus swing (vs 2.51/5.95 pp for GPTQ/AWQ) is the smallest among
all compared fixed-hyperparameter methods, achieved without rare-word data curation or
auxiliary optimization. The method is more robust to calibration set choice than enriching
the calibration corpus with manually selected rare samples.

## Datasets

* **LibriSpeech-clean / -other** (Panayotov et al., 2015): read audiobook speech; 3,000-
  utterance test subsamples; publicly available (CC BY 4.0)
* **SPGISpeech / SPGI** (O'Neill et al., 2021): professionally transcribed corporate earnings
  calls; 3,000-utterance subsample; mixed read and spontaneous speech
* **VoxPopuli** (Wang et al., 2021): European Parliament speech, English split; full 1,842-
  utterance test set; rich in proper names and numerals; publicly available
* **GigaSpeech** (Chen et al., 2021): 10,000-hour multi-domain corpus (audiobooks, podcasts,
  YouTube); 3,000-utterance subsample
* **TED-LIUM** (Hernandez et al., 2018): TED-talk speech; 3,000-utterance subsample
* **ProfASR** (Piskala, 2025): professional-domain speech (lectures and technical talks);
  entity-rich benchmark; research license
* **ContextASR-Speech-En** (Wang et al., 2025): contextual-entity-enriched ASR benchmark with
  high-density named entities in references; research license
* Calibration corpora drawn from training splits of LibriSpeech, SPGISpeech, and VoxPopuli;
  rare-biased pools (r-top, r-mix, r-cross) constructed by rare-density sampling

## Main Ideas

* **Quantization silently degrades entity transcription.** Standard W4G128 methods degrade
  rare-word recognition (brand names, SKUs, product terms) while aggregate WER looks
  acceptable. The gold-92 benchmark should report rare-WER in addition to aggregate WER
  to catch this failure mode.
* **TARQ enables entity-safe INT4 ASR deployment.** TARQ applied to Whisper-large-v3 or
  Qwen3-ASR-1.7B delivers 1.63x–2.18x GPU speedup and 46%–67% VRAM reduction with no
  rare-word accuracy regression, making quantized models viable for Rezolve's latency-
  constrained (<800 ms p50) voice-to-action pipeline.
* **Contextual biasing remains necessary for isolated rare proper nouns.** TARQ fails on
  short utterances dominated by a single rare proper noun with no phonetic context (e.g.,
  an isolated brand name). The paper explicitly flags inference-time contextual biasing as
  a complementary mitigation — directly pointing to the entity-correction track as necessary
  in combination with TARQ.
* **Calibration stability across corpora reduces production risk.** TARQ's 0.63 pp cross-
  corpus swing vs GPTQ's 2.51 pp means the approach is robust when production audio
  distribution shifts — relevant as Rezolve's product catalog and user population evolve.
* **Rarity-based metric reweighting transfers to entity benchmarks without entity labels.**
  This means TARQ can be applied before any Rezolve-specific entity vocabulary is curated,
  providing a baseline entity-accuracy improvement as a free side effect of quantization.

## Summary

TARQ diagnoses and fixes a structural flaw in data-aware post-training quantization for ASR:
standard calibration metrics inherit the Zipfian token-frequency distribution of the calibration
corpus, assigning only ~6.9% of trace mass to rare tokens (names, numerals, domain terms) that
represent a disproportionate share of recognition risk in entity-sensitive applications. The
research question is whether this metric-level imbalance — not solver quality — is the root
cause of rare-word degradation under W4G128 quantization of modern ASR models.

TARQ addresses this through RAREBAL, a closed-form per-Linear-layer trace equalization that
reweights the calibration metric to give equal mass to common and rare token groups, computed
from a single scalar derived from activation second moments already accumulated during PTQ.
A propagation-aware residual correction ensures the sequential layer sweep remains aligned
with the rebalanced metric. Both components require no entity labels, no additional data, and
no extra calibration pass, making TARQ a drop-in enhancement to any GPTQ-family solver.

Across 8 backbones and 6 datasets, TARQ achieves rank-1 mean plain WER on all backbones and
rank-1 mean rare-WER on 6 of 8, with a cross-corpus stability swing of just 0.63 pp vs 2.51 pp
for GPTQ. Entity-rich benchmarks (ProfASR, ContextASR-Speech-En) confirm transfer without
entity supervision. Deployment profiling shows 1.06x–2.18x GPU speedup and 33%–67% VRAM
reduction, with Whisper-large-v3 reaching CPU real time (RTF 0.87 at 8 threads).

For Rezolve's voice commerce pipeline, TARQ offers a practical path to compressed ASR without
sacrificing brand name and SKU recognition quality. The identified limitation — failure on
isolated rare proper nouns lacking phonetic context — directly motivates the entity-correction
research track in this project, confirming that inference-time contextual biasing or vocabulary
injection must complement quantization-time fixes. The paper's rare-WER metric also provides a
precise template for enriching the gold-92 benchmark evaluation beyond aggregate WER.
