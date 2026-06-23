---
spec_version: "3"
paper_id: "10.21437_Interspeech.2020-1338"
citation_key: "Liu2020"
summarized_by_task: "t0002_baseline_evaluation"
date_summarized: "2026-06-23"
---

# Statistical Testing on ASR Performance via Blockwise Bootstrap

## Metadata

* **File**: `files/liu_2020_blockwise-bootstrap-asr.pdf`
* **Published**: 2020
* **Authors**: Zhe Liu 🇺🇸, Fuchun Peng 🇺🇸
* **Venue**: Interspeech 2020
* **DOI**: `10.21437/Interspeech.2020-1338`

## Abstract

A common question being raised in automatic speech recognition (ASR) evaluations is how reliable
is an observed word error rate (WER) improvement comparing two ASR systems, where statistical
hypothesis testing and confidence interval (CI) can be utilized to tell whether this improvement is
real or only due to random chance. The bootstrap resampling method has been popular for such
significance analysis which is intuitive and easy to use. However, this method fails in dealing
with dependent data, which is prevalent in speech world - for example, ASR performance on
utterances from the same speaker could be correlated. In this paper we present blockwise bootstrap
approach - by dividing evaluation utterances into nonoverlapping blocks, this method resamples
these blocks instead of original data. We show that the resulting variance estimator of absolute
WER difference between two ASR systems is consistent under mild conditions. We also demonstrate
the validity of blockwise bootstrap method on both synthetic and real-world speech data.

## Overview

Liu and Peng address a practical but under-served problem in ASR research: how to correctly
quantify statistical uncertainty when comparing two systems' WERs on an evaluation set. The
conventional approach — resampling individual utterances using ordinary bootstrap — assumes that
utterance-level errors are independent and identically distributed. This assumption breaks down
whenever utterances cluster by speaker, topic, or recording session, which is the rule rather than
the exception in real evaluation datasets.

The paper introduces blockwise bootstrap for ASR evaluation. The key idea is to partition
evaluation utterances into semantically coherent, non-overlapping blocks (e.g., by speaker or
conversation), then resample complete blocks with replacement rather than individual utterances.
This preserves within-block correlation structure while treating blocks as independent units. The
authors derive a formal L2-consistency result showing their blockwise variance estimator converges
to the true variance as the dataset grows, provided both the number of blocks and block size tend
to infinity. A practical corollary relaxes the strict uncorrelation assumption between blocks to a
weaker moment condition.

The paper validates the method on two fronts. Simulation experiments with synthetic data show
conclusively that ordinary bootstrap dramatically undercovers when utterance errors are correlated:
at block size d=30 and correlation ρ=0.4, ordinary bootstrap CI coverage drops to **41.2%** while
blockwise bootstrap holds at **95.9%**. Real-data experiments on a Conversational Speech dataset
(13,987 utterances, 235 blocks) and the AMI Meeting corpus (25,741 utterances, 135 blocks) confirm
that blockwise CIs are **1.5x** (Conversation) to **2x** (AMI) wider than ordinary bootstrap CIs,
meaning ordinary bootstrap systematically underestimates uncertainty and risks false-positive
claims of improvement.

The paper is concise (5 pages), mathematically grounded, and practically focused. It does not
require code beyond basic resampling loops, and the block structure is simply the set of speaker or
conversation IDs already present in most evaluation metadata.

## Architecture, Models and Methods

**Bootstrap baseline.** Standard utterance-level bootstrap (Bisani & Ney, 2004) resamples n
utterances with replacement B times, recomputes ΔW = WER_B − WER_A on each resample, and reads
off 2.5/97.5 empirical percentiles as the 95% CI.

**Blockwise bootstrap algorithm.** Given n evaluation utterances partitioned into K non-overlapping
blocks S_1, …, S_K, the method resamples K blocks with replacement to form each bootstrap
replicate. For replicate b, the statistic ΔW^(b) is computed over the concatenated utterances of
the K resampled blocks. With B = 1,000 replicates, the 95% CI is the (2.5th, 97.5th) empirical
percentile of {ΔW^(b)}. A Gaussian approximation variant using the sample standard deviation of
{ΔW^(b)} is also presented and shown to produce nearly identical CIs when B is large.

**Consistency theorem.** The blockwise variance estimator σ̂² (standardized sample variance of
block-level ΔW estimates) is L2-consistent: σ̂² → σ² as n → ∞, provided (1) both K_n (number of
blocks) and d_n (utterances per block) go to infinity with n, and (2) different blocks are
uncorrelated. A corollary relaxes the uncorrelated-blocks condition to a fourth-moment condition,
making the theory applicable to data where cross-block correlations are weak but nonzero.

**Simulation setup.** n = 3,000 utterances, m = 100 words each. True WER_A = 10.0%,
WER_B = 9.5%, so ΔW = −0.5%. Correlated errors generated via Gaussian copula with block
correlation ρ ∈ {0, 0.05, 0.1, 0.2, 0.4} and block size d ∈ {5, 30}. Each configuration
replicated 1,000 times; CI coverage measured as fraction of replicates containing the true ΔW.
B = 1,000 bootstrap replicates per run.

**Real-data setup.** Two evaluation sets: (1) Conversational Speech — 13,987 utterances,
160,338 words, 235 conversation-level blocks; (2) AMI Meeting — 25,741 utterances, 189,590 words,
135 speaker-meeting blocks. An in-house baseline (system A) and improved model (system B) were
compared. Blocks defined by conversation identity (Conversation data) or by speaker within each
meeting (AMI).

## Results

* Ordinary bootstrap CI coverage at d=5, ρ=0.4: **76.9%** (target: 95%); blockwise: **94.0%**
* Ordinary bootstrap CI coverage at d=30, ρ=0.05: **78.1%**; blockwise: **95.2%**
* Ordinary bootstrap CI coverage at d=30, ρ=0.4: **41.2%**; blockwise: **95.9%**
* When ρ=0 (independent data), both methods agree: coverage ~**94.1%** (ordinary) vs ~**94.7%**
  (blockwise) — confirming no accuracy loss on independent data
* Ordinary bootstrap CI width: **0.0030** (constant regardless of correlation or block size)
* Blockwise bootstrap CI width at d=30, ρ=0.4: **0.0105** — **3.5x wider** than ordinary
* Conversation real data: seboot = **0.074%**, seblockBoot = **0.116%** (**1.57x** larger);
  ordinary CI (−1.61%, −1.32%) vs blockwise CI (−1.69%, −1.24%)
* AMI Meeting real data: seboot = **0.067%**, seblockBoot = **0.153%** (**2.28x** larger);
  ordinary CI (−1.94%, −1.67%) vs blockwise CI (−2.09%, −1.51%)
* Percentile CIs and Gaussian approximation CIs agree closely in all real-data experiments

## Innovations

### First Blockwise Bootstrap for ASR Evaluation

Prior work (Bisani & Ney, 2004) applied standard i.i.d. bootstrap to ASR significance testing.
This paper is the first to adapt the blockwise bootstrap — originally developed for dependent time
series (Hall 1985, Carlstein 1986) — to ASR evaluation, where dependence arises from speaker or
topic clustering rather than temporal autocorrelation. The transfer is non-trivial: blocks are
defined by evaluation metadata (speaker or session IDs), not by consecutive time indices.

### Formal Consistency Proof for ASR Setting

The authors derive an L2-consistency theorem for their blockwise variance estimator in the ASR
context, plus a corollary relaxing strict independence-between-blocks to a fourth-moment condition.
This is the first theoretical justification for bootstrap-based WER variance estimation under
dependent speech data, and it sets conditions (both K_n and d_n must grow) that directly inform
how to size evaluation sets.

### Quantified Failure Mode of Ordinary Bootstrap

The paper provides the first systematic quantification of how badly ordinary bootstrap fails under
realistic ASR dependency levels. The simulation table (Table 1) with coverage rates across
combinations of block size and correlation strength can serve as a reference when deciding whether
standard bootstrap is safe to use for a given evaluation dataset.

## Datasets

* **Synthetic simulation data**: 3,000 utterances × 100 words each, generated from Gaussian copula
  model with configurable block correlation; not a public dataset.
* **Conversational Speech**: 13,987 utterances, 160,338 words, 235 conversation blocks. Collected
  via crowd-sourcing and anonymized. Proprietary Facebook AI dataset; not publicly released.
* **AMI Meeting Corpus**: 25,741 utterances, 189,590 words, 135 speaker-meeting blocks. Publicly
  available at https://groups.inf.ed.ac.uk/ami/corpus/. Scenario and non-scenario meetings with
  4 participants each. License: Creative Commons Attribution 4.0.

## Main Ideas

* Ordinary bootstrap for WER significance testing is **invalid when utterances are correlated** —
  e.g., grouped by speaker, session, or topic. It produces CIs that are far too narrow, risking
  false-positive claims of improvement. At moderate real-world correlations coverage can fall below
  **50%** for a nominal 95% CI.
* **Blockwise bootstrap fixes this** by resampling speaker/session blocks rather than individual
  utterances. The procedure requires only that block IDs (e.g., speaker IDs) be present in the
  evaluation metadata — no distributional assumptions and negligible implementation complexity.
* The project success criterion requires **BCa bootstrap p < 0.05 on n = 93 paired samples**.
  The gold-92 benchmark likely contains multiple utterances per speaker from Rezolve production
  sessions. Blockwise bootstrap (or BCa) with speaker-level blocks should be used; ordinary
  bootstrap risks a false-positive significance claim.
* **Block definition matters**: for gold-92, speaker identity is the natural block unit. If
  multiple clips per speaker are present, grouping by speaker ID gives more valid CIs than treating
  utterances as independent.
* The method is computationally trivial: B = 1,000 bootstrap replicates run in seconds even on
  large datasets. There is no reason to use ordinary bootstrap when speaker IDs are available.

## Summary

Liu and Peng (2020) address a specific but important methodological gap in ASR evaluation: the
standard bootstrap procedure for WER confidence intervals assumes utterance-level independence, but
real evaluation sets almost always contain correlated utterances from the same speakers, sessions,
or topics. The paper proposes blockwise bootstrap, which resamples groups of correlated utterances
as atomic units, preserving within-group dependence while treating groups as independent. The
motivation is to prevent systematically overconfident claims of ASR improvement that arise when
ordinary bootstrap artificially narrows confidence intervals.

The method partitions utterances into K non-overlapping blocks using existing evaluation metadata
(e.g., speaker IDs), then resamples blocks with replacement B = 1,000 times. The 95% CI for ΔW is
the empirical (2.5%, 97.5%) percentile range of the B bootstrap statistics. The authors prove an
L2-consistency theorem showing the variance estimator converges to the true variance as both K and
block size grow with n. Simulation experiments with n = 3,000 utterances and correlation ρ up to
0.4 confirm that ordinary bootstrap coverage collapses to **41.2%** while blockwise bootstrap
consistently stays near **95%**.

Experiments on two real datasets confirm the failure of ordinary bootstrap in practice: blockwise
CIs are **1.5–2.3x** wider than ordinary bootstrap CIs. On the Conversational Speech dataset
(13,987 utterances, 235 blocks), the standard error increases from **0.074%** to **0.116%**; on
AMI Meeting (25,741 utterances, 135 blocks), from **0.067%** to **0.153%**. Neither method changes
the sign of the estimated WER difference, but ordinary bootstrap understates uncertainty by a large
margin, risking false-positive significance results.

For this project, the finding is directly actionable. The gold-92 benchmark likely contains
multiple utterances per speaker from Rezolve production sessions, creating exactly the within-
speaker correlation the paper diagnoses. The success criterion — beating Deepgram with BCa
bootstrap p < 0.05 on n = 93 paired samples — should use blockwise or BCa bootstrap with
speaker-level blocks rather than ordinary bootstrap. The implementation overhead is minimal: only
speaker IDs are needed as the block key.
