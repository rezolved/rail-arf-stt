---
spec_version: "3"
paper_id: "10.48550_arXiv.2505.12969"
citation_key: "Wang2025"
summarized_by_task: "t0014_granite_short_clip_robustness"
date_summarized: "2026-06-29"
---

# Calm-Whisper: Reduce Whisper Hallucination On Non-Speech By Calming Crazy Heads Down

## Metadata

* **File**: `files/wang_2025_calm-whisper-hallucination.pdf`
* **Published**: 2025
* **Authors**: Yingzhi Wang 🇸🇦, Anas Alhmoud 🇸🇦, Saad Alsahly 🇸🇦,
  Muhammad Alqurishi 🇸🇦, Mirco Ravanelli 🇨🇦
* **Venue**: Interspeech 2025
* **DOI**: `10.48550/arXiv.2505.12969`

## Abstract

OpenAI's Whisper has achieved significant success in Automatic Speech Recognition. However, it has
consistently been found to exhibit hallucination issues, particularly in non-speech segments, which
limits its broader application in complex industrial settings. In this paper, we introduce a novel
method to reduce Whisper's hallucination on non-speech segments without using any pre- or
post-possessing techniques. Specifically, we benchmark the contribution of each self-attentional
head in the Whisper-large-v3 decoder to the hallucination problem by performing a head-wise mask.
Our findings reveal that only 3 of the 20 heads account for over 75% of the hallucinations on the
UrbanSound dataset. We then fine-tune these three crazy heads using a collection of non-speech
data. The results show that our best fine-tuned model, namely Calm-Whisper, achieves over 80%
reduction in non-speech hallucination with only less than 0.1% WER degradation on LibriSpeech
test-clean and test-other.

## Overview

Whisper-large-v3 produces transcription hallucinations on silent or non-speech audio segments at
a rate of **99.97%** — meaning that practically every non-speech clip fed to the model yields
fabricated text output. This paper diagnoses and remedies that failure mode through a targeted
surgical intervention rather than through external pre-/post-processing heuristics (e.g., VAD
filtering or output post-screening).

The core diagnostic finding is that Whisper's 20 decoder self-attention heads are not equally
responsible for hallucinations. By systematically masking each head in isolation and in
combinations, the authors identify that three "crazy heads" (#1, #6, and #11) collectively
account for over **75%** of hallucinations on UrbanSound8K non-speech clips. Masking all three
drops the hallucination rate from **99.97%** to **24.10%**, but at the cost of **+1.45%** WER
on LibriSpeech test-clean.

Rather than leaving those heads masked (which degrades speech transcription), the authors
fine-tune only those three heads on 105 hours of non-speech audio paired with blank (empty)
target labels. The intuition is to teach the problematic heads that non-speech input should
produce no output — without touching the weights responsible for accurate speech transcription.
The best configuration (5-epoch fine-tune) achieves a hallucination rate of **15.51%** on
UrbanSound8K — an **84.5%** relative reduction — while WER on LibriSpeech test-clean increases
by only **+0.07%** (from **2.12%** to **2.19%**) and test-other by only **+0.06%** (from
**4.07%** to **4.13%**). This demonstrates that hallucination and speech accuracy can be
decoupled by constraining the intervention to specific attention heads.

Additionally, the long hallucinations (sequences exceeding 5 tokens) drop from **742** instances
to **91** after 5-epoch fine-tuning, meaning the remaining hallucinations are much shorter and
less disruptive. The most common hallucination was the single word "so", which appeared in
**55.2%** of hallucinating UrbanSound clips before intervention.

## Architecture, Models and Methods

**Base Model**: Whisper-large-v3 — OpenAI's largest released Whisper checkpoint, with a standard
encoder-decoder transformer architecture. The decoder has 20 self-attention heads per layer.

**Head Attribution via Masking**: Each of the 20 decoder self-attention heads is zeroed out
individually (head-wise masking), and the hallucination rate on UrbanSound8K non-speech clips is
measured. The 8 heads where masking reduces hallucination are labelled "hallucinatory heads":
#0, #1, #3, #4, #6, #8, #11, #19. Combinations of heads #1, #6, and #11 are then evaluated to
find the minimal set that captures the largest hallucination reduction. Masking all three yields a
hallucination rate of **24.10%** (vs. **99.97%** baseline), while masking a fourth head (#0)
degrades WER catastrophically to **15.87%** test-clean.

**Fine-Tuning Procedure**: All Whisper-large-v3 parameters are frozen except the query, key,
value, and output projection weights belonging to heads #1, #6, and #11 across all decoder layers.
The model is trained on **105 hours** of non-speech audio drawn from three datasets (AudioSet
subset, DEMAND, MUSAN music+noise), each paired with a blank target label sequence. The training
objective is cross-entropy loss between model output and the blank target.

**Hyperparameters**:

* Learning rate: **1 × 10⁻⁶**
* Warm-up: approximately **15%** of total iterations
* Total batch size: **128**
* Training duration: 3 and 5 epochs evaluated; optimal depth between 5-6 epochs
* Frozen parameters: all except heads #1, #6, #11 in all decoder layers

**Evaluation Metrics**:

* Hallucination rate: percentage of UrbanSound8K clips for which the model outputs any
  non-blank transcript
* WER: computed on LibriSpeech test-clean and test-other with the original Whisper decoding
  pipeline, measuring regression on standard speech transcription

**Baseline Comparison**: Conformer-CTC-large is reported as a non-generative CTC-based baseline,
which achieves a hallucination rate of **13.52%** — representing the approximate floor for a
comparable model class that does not use autoregressive decoding.

## Results

* Whisper-large-v3 baseline hallucination rate on UrbanSound8K: **99.97%**
* Conformer-CTC-large hallucination rate (reference baseline): **13.52%**
* Masking only head #1: reduces hallucination by **>30%** (largest single-head contribution)
* Masking heads #1, #6, #11 (best 3-head mask): hallucination rate **24.10%**, WER test-clean
  **3.57%** (+**1.45%** absolute vs. baseline **2.12%**)
* Adding head #0 to mask: hallucination rate **28.91%** (worse), WER test-clean **15.87%**
  (catastrophic degradation)
* Fine-tune 3 heads × 3 epochs: hallucination rate **69.79%**, WER test-clean **2.16%** (+0.04%)
* Fine-tune 3 heads × 5 epochs (Calm-Whisper best): hallucination rate **15.51%** (**>80%**
  reduction vs. **99.97%**), WER test-clean **2.19%** (+**0.07%**), WER test-other **4.13%**
  (+**0.06%**)
* Long hallucinations (>5 tokens): reduced from **742** to **91** after 5-epoch fine-tuning
* Most common hallucination: word "so", representing **55.2%** of hallucinated clips
* Full decoder fine-tune (3 epochs): WER collapses to **100%** — confirms broad-scope fine-tuning
  destroys the model; head-specific targeting is essential

## Innovations

### Head-Wise Hallucination Attribution

For the first time, the paper systematically attributes Whisper's non-speech hallucination to
specific decoder self-attention heads through individual and combinatorial masking. Prior work
treated hallucination as a model-level property; this paper shows it is concentrated in fewer
than **15%** of attention heads (3 of 20), enabling precision intervention.

### Surgical Head-Only Fine-Tuning

By freezing all parameters except those belonging to the three identified "crazy heads", the
method avoids the speech-accuracy regression that affects broader fine-tuning approaches. The
full-decoder fine-tune baseline collapses to **100% WER**, confirming that surgical targeting is
not just efficient but necessary for preserving speech quality.

### Non-Speech Training Data Recipe

The paper constructs a 105-hour collection of pure non-speech audio from AudioSet, DEMAND, and
MUSAN, paired with blank targets, as a targeted training signal to suppress hallucination. This
construction recipe is reusable for any Whisper-class model.

## Datasets

**UrbanSound8K** (hallucination evaluation):

* 8,732 labeled audio clips, up to 4 seconds each
* 10 urban sound classes (sirens, dog barks, drilling, etc.)
* No speech content — used purely to trigger non-speech hallucination
* Publicly available; standard benchmark for environmental sound classification

**LibriSpeech test-clean / test-other** (WER evaluation):

* Standard English read-speech benchmark
* test-clean: ~2,620 utterances, clean recording conditions
* test-other: ~2,939 utterances, more varied acoustic conditions
* Publicly available; standard Whisper evaluation set

**AudioSet** (fine-tuning, subset of 11,753 clips):

* 527 sound event classes; human speech segments manually excluded
* Publicly available (YouTube-sourced, Creative Commons license for annotations)

**DEMAND** (fine-tuning):

* 18 diverse acoustic environments (office, kitchen, street, etc.)
* 16-channel microphone array recordings; publicly available

**MUSAN** (fine-tuning, music + noise subsets only):

* Diverse music genres and noise sources; speech subset excluded; publicly available

## Main Ideas

* Whisper-large-v3's near-total hallucination on non-speech (**99.97%** rate) is a critical
  failure mode for production pipelines where audio may contain pauses, background noise, or
  non-speech events — directly relevant to Rezolve's voice commerce use case where short clips
  and silences are common.
* Only 3 of 20 decoder attention heads are responsible for >75% of hallucinations; fine-tuning
  only those heads achieves **>80% hallucination reduction** while keeping WER degradation below
  **0.1%** — a strongly favourable trade-off for production deployment.
* The head-specific fine-tuning approach is applicable to any Whisper checkpoint (Whisper-medium,
  Whisper-small, Granite STT variants) by running the same head-masking attribution study per
  model; the "crazy head" indices will differ per model size.
* Adopting Calm-Whisper or its fine-tuning recipe could reduce false transcription events on
  short Rezolve production clips without requiring VAD pre-filtering or post-processing
  heuristics, simplifying the production pipeline.
* The non-speech training corpus (AudioSet + DEMAND + MUSAN, 105 hours total) is freely available
  and lightweight; replicating this fine-tune requires no proprietary data.

## Summary

This paper targets a severe and practically important failure mode of Whisper-large-v3:
hallucination on non-speech audio. With a baseline hallucination rate of **99.97%** on
UrbanSound8K — meaning virtually every non-speech clip produces fabricated text — Whisper is
unsafe to deploy in production pipelines that handle mixed-content audio without external VAD
safeguards. The authors set out to eliminate this hallucination from within the model, without
adding inference-time complexity or external pre/post-processing.

The technical approach proceeds in two stages. First, a head-wise masking study isolates which of
Whisper-large-v3's 20 decoder self-attention heads contributes most to hallucination. Three heads
(#1, #6, #11) are identified as responsible for over **75%** of the problem. Second, only the
weights of those three heads are fine-tuned on 105 hours of pure non-speech audio (AudioSet,
DEMAND, MUSAN) paired with blank target labels. All other weights remain frozen, preventing
regression on standard speech transcription tasks.

The results are striking: the best model (5-epoch fine-tune) reduces hallucination on UrbanSound8K
from **99.97%** to **15.51%** — an **84.5%** relative reduction — while WER on LibriSpeech
test-clean rises by only **+0.07%** (from **2.12%** to **2.19%**). Long hallucinations exceeding
5 tokens drop from **742** instances to **91**. The paper also demonstrates that broader fine-tuning
(full decoder) completely destroys transcription quality (**100% WER**), confirming that surgical
head-level targeting is essential. The Calm-Whisper hallucination rate of **15.51%** approaches the
**13.52%** of Conformer-CTC-large — a CTC-based model fundamentally less prone to autoregressive
hallucination — validating that the gap can be largely closed through targeted fine-tuning.

For this project, Calm-Whisper is directly relevant to the robustness goal of evaluating
Whisper-class models on short production audio clips from Rezolve voice commerce sessions. Short
clips, silences, and background noise are common in that setting, and the **99.97%** baseline
hallucination rate means any such segment would produce spurious transcripts corrupting downstream
entity recognition and intent parsing. Adopting the Calm-Whisper fine-tuning recipe — or applying
an equivalent head-attribution study to Granite STT or another Whisper-variant — could be a
low-cost, high-impact robustness improvement for the Rezolve pipeline, with negligible WER
regression cost.
