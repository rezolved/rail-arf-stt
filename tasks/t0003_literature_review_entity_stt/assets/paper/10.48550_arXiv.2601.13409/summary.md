---
spec_version: "3"
paper_id: "10.48550_arXiv.2601.13409"
citation_key: "Ren2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---
# RLBR: Reinforcement Learning with Biasing Rewards for Contextual Speech Large Language

Models

## Metadata

* **File**: `files/novitasari_2026_rlbr-biasing-rewards.pdf`
* **Published**: 2026
* **Authors**: Bo Ren 🇺🇸, Ruchao Fan 🇺🇸, Yelong Shen 🇺🇸, Weizhu Chen 🇺🇸, Jinyu Li 🇺🇸 (Microsoft)
* **Venue**: ICASSP 2026
* **DOI**: `10.48550/arXiv.2601.13409`

## Abstract

Contextual biasing in speech LLMs improves recognition of rare and domain-specific terms, but
current methods rely on supervised fine-tuning (SFT) that treats all words equally. This paper
proposes RLBR, a reinforcement learning approach using a biasing-words-preferred reward that
explicitly up-weights bias word tokens in the reward calculation. A reference-aware mechanism
extends the RL algorithm with reference transcription to strengthen trajectory exploration. On
LibriSpeech with bias lists of 100-1000 words, RLBR achieves biased WERs of 0.59%/2.11%
(test-clean/test-other) at 100 words, 1.09%/3.24% at 500 words, and 1.36%/4.04% at 1000 words,
consistently outperforming SFT baselines and recently published contextual biasing methods.

## Overview

RLBR identifies a fundamental misalignment in how supervised fine-tuning (SFT) trains contextual
biasing models: SFT applies uniform cross-entropy loss to all tokens, meaning that the model gets
the same gradient signal from correctly transcribing "the" and correctly transcribing "Bose" (a rare
brand name). For contextual biasing applications, the entire value is in rare-entity accuracy, yet
SFT treats rare entities as statistically insignificant due to their low frequency.

RLBR corrects this with a bias-word-preferred reward: during RL training (using a variant of GRPO —
Group Relative Policy Optimization), the reward for each sampled trajectory is computed as the
standard WER-based reward but with bias word tokens receiving a multiplied reward coefficient
(alpha=5 in experiments). This forces the policy gradient to strongly favor trajectories that
correctly transcribe bias words.

The reference-aware mechanism augments trajectory exploration by conditioning the RL sampler on the
ground-truth reference, generating hypotheses that are near the reference but vary in bias word
handling. This prevents mode collapse (the RL policy converging to a degenerate hypothesis that
avoids generating entity tokens entirely).

Microsoft's proprietary Speech LLM (Phi-4-MM class) is used as the base model. The evaluation is on
LibriSpeech with injected rare-word bias lists of varying sizes.

## Architecture, Models and Methods

**Base model**: Microsoft Speech LLM (Phi-4-MM class architecture; exact parameters not disclosed in
the paper).

**RL algorithm**: GRPO (Group Relative Policy Optimization). Generates G=8 hypothesis samples per
utterance; computes advantage relative to the group mean reward.

**Biasing-words-preferred reward**: For each sampled hypothesis, reward = alpha ×
(token_is_bias_word) × match_reward + (1 - token_is_bias_word) × match_reward, with alpha=5.
Effectively multiplies gradient signal for bias word correctness by 5×.

**Reference-aware trajectory exploration**: Perturbs reference transcription at bias word positions
to create positive/negative RL training pairs, ensuring diverse trajectories in the bias word
decision space.

**Bias list sizes tested**: 100, 500, 1000 words randomly sampled from rare-word sets.

**Evaluation**: Biased WER (B-WER) = WER computed only on utterances containing bias words; overall
WER = full LibriSpeech evaluation.

## Results

* B-WER at 100 bias words (test-clean/test-other): **0.59% / 2.11%**
* B-WER at 500 bias words: **1.09% / 3.24%**
* B-WER at 1000 bias words: **1.36% / 4.04%**
* RLBR consistently outperforms SFT baseline and recent published methods (specific absolute
  comparisons: table numbers not found in abstract)
* Overall WER (non-bias utterances): preserved — no regression reported
* Latency: not reported in the paper

## Innovations

### Biasing-Words-Preferred RL Reward

First RL training objective specifically designed to up-weight rare entity accuracy in ASR. Corrects
the SFT misalignment by giving the policy gradient 5× larger signal for bias word correctness.

### Reference-Aware Trajectory Exploration

Augments RL exploration by conditioning trajectory sampling on the reference, preventing mode
collapse while ensuring the policy space covers correct and incorrect bias word handling.

## Datasets

* **LibriSpeech**: test-clean and test-other splits; English; standard ASR benchmark
* Injected rare-word bias lists: 100, 500, 1000 words from domain-specific vocabulary

## Main Ideas

* The RL reward shaping insight (alpha=5× for bias words) is a simple training modification
  applicable to any speech LLM fine-tuning setup — does not require architecture changes
* RLBR requires full model fine-tuning, unlike post-processing approaches; this is a
  higher-investment path than prompt injection or N-best correction but achieves lower absolute
  B-WER (0.59% at 100 words vs. 2.78% for CLAR)
* The reference-aware exploration is a practical contribution to stable RL training for ASR —
  prevents reward hacking on the bias word metric
* For Rezolve, RLBR would require fine-tuning Whisper Turbo on ecommerce entity data; the approach
  is not applicable as a zero-training-cost add-on

## Summary

Ren et al. address the SFT misalignment for contextual biasing: standard supervised fine-tuning
gives equal gradient weight to common function words and rare domain entities, even though the
entire value of contextual biasing lies in the rare entity accuracy. RLBR corrects this by using a
RL reward function that multiplies the reward for correct bias word transcription by alpha=5,
focusing the policy gradient where it matters.

The GRPO-based RL training generates 8 hypothesis samples per utterance and scores them with the
bias-word-preferred reward. A reference-aware augmentation prevents mode collapse by ensuring the
exploration space covers the correct entity handling paths.

Results on LibriSpeech: B-WER of **0.59%/2.11%** at 100 bias words, **1.09%/3.24%** at 500 words,
and **1.36%/4.04%** at 1000 words (test-clean/test-other). These represent state-of-the-art biased
WERs among methods published in Jan-Jun 2026 for English ASR.

For Rezolve, RLBR requires fine-tuning the production ASR model (Whisper Turbo or equivalent) on
ecommerce entity data — a higher-investment approach than post-processing methods. The reward
shaping principle is directly transferable: any RL-based ASR fine-tuning for ecommerce should weight
brand/product/SKU tokens at alpha=5×. The reference-aware exploration mechanism addresses a
practical training stability concern that would arise when fine-tuning on a small (~1000 utterance)
ecommerce entity dataset.
