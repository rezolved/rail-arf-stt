---
spec_version: "3"
paper_id: "10.1109_ICASSP49660.2025.10890105"
citation_key: "Baranski2025"
summarized_by_task: "t0014_granite_short_clip_robustness"
date_summarized: "2026-06-29"
---

# Investigation of Whisper ASR Hallucinations Induced by Non-Speech Audio

## Metadata

* **File**: `files/baranski_2025_whisper-hallucinations-nonspeech.pdf`
* **Published**: 2025
* **Authors**: Mateusz Barański 🇵🇱, Jan Jasiński 🇵🇱, Julitta Bartolewska 🇵🇱,
  Stanisław Kacprzak 🇵🇱, Marcin Witkowski 🇵🇱, Konrad Kowalczyk 🇵🇱
* **Venue**: ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal
  Processing (ICASSP)
* **DOI**: `10.1109/ICASSP49660.2025.10890105`

## Abstract

Hallucinations of deep neural models are amongst key challenges in automatic speech recognition
(ASR). In this paper, we investigate hallucinations of the Whisper ASR model induced by non-speech
audio segments present during inference. By inducting hallucinations with various types of sounds,
we show that there exists a set of hallucinations that appear frequently. We then study
hallucinations caused by the augmentation of speech with such sounds. Finally, we describe the
creation of a bag of hallucinations (BoH) that allows to remove the effect of hallucinations
through the post-processing of text transcriptions. The results of our experiments show that such
post-processing is capable of reducing word error rate (WER) and acts as a good safeguard against
problematic hallucinations.

## Overview

This paper systematically investigates a specific failure mode of the Whisper ASR model: generating
hallucinated text when the input audio contains no speech at all. The authors run Whisper large-v3
on a dataset of 301,317 non-speech audio files assembled from four public collections (Audioset,
Musan, UrbanSound8K, FSD50K) plus synthesized noise and silence. Any text output from these files
is definitionally a hallucination, enabling clean measurement without relying on phonetic or
semantic similarity thresholds.

The study finds that hallucinations occur in **40.3%** of inferences on non-speech audio. A key
finding is that hallucinated outputs are highly concentrated: just 1,270 unique strings account for
**67.08%** of all hallucinations, and two phrases alone ("thank you" and "thanks for watching")
account for **35%** of all occurrences. This pattern reflects Whisper's training on YouTube video
transcriptions, which explain YouTube-specific phrases like "thanks for watching" and "subtitles
by the amara org community." The authors construct a Bag of Hallucinations (BoH) — a filtered list
of problematic outputs — by applying an n-gram language model filter (log probability < −10) and a
frequency threshold (more than four occurrences in non-speech inferences).

The paper then extends to speech augmented with non-speech sounds, showing that even when the core
utterance is clean, prepended or appended noise segments reliably trigger hallucinations, with rates
rising steeply when total audio duration exceeds 30 seconds (Whisper's processing segment
boundary). The authors evaluate multiple mitigation strategies — beam size reduction, Whisper's
hallucination silence threshold parameter, Voice Activity Detection (VAD) pre-processing, and their
own BoH-based post-processing — against WER on augmented speech files. The best single approach is
SileroVAD pre-processing (**8.0% WER** non-overlap), and combining SileroVAD with delooping and
BoH removal achieves **6.5% WER** (non-overlap), down from a baseline of **104.8% WER** without
any mitigation.

The practical implication is direct: for any deployment where audio clips may begin or end with
non-speech (ambient noise, silence pads, hold music, device sounds), Whisper will insert spurious
text at a high rate. The BoH-based filter is a lightweight defensive layer applicable as a
post-processing step without modifying the ASR model or pipeline, making it directly relevant to
Rezolve's voice commerce STT harness where short production clips with ambient lead-in/lead-out are
common.

## Architecture, Models and Methods

**ASR model**: Whisper large-v3, temperature = 0 (deterministic/greedy decoding), language forced
to English, other parameters at OpenAI defaults. Transcriptions are normalized using the OpenAI
basic normalizer. Looping (repeated text fragments) is detected and removed before analysis.

**Experiment 1 — exhaustive hallucination collection** (non-speech only): 301,317 audio files
from Audioset (253,278 files), FSD50K (29,074), UrbanSound8K (8,733), Musan (931), plus 9,301
synthetic noise/silence files. All files tagged as containing speech, human voices, singing, or
music were removed.

**Experiment 2 — duration effects**: A subset of 200 files from Experiment 1, cropped or
concatenated to produce clips of lengths 1 s, 10 s, 20 s, and 30 s. Metrics reported: hallucination
rate, looping rate, preservation of original hallucination, Top-30 overlap.

**Experiment 3 — sound category effects**: The AudioSet eval split (8,272 files of 10 s) filtered
as in Experiment 1, stratified by 6 AudioSet main categories (Human, Animal, Sounds of Things,
Source-ambiguous, Environmental/Background, Natural Sounds).

**Bag of Hallucinations (BoH) construction**: Raw hallucination list filtered by (a) n-gram log
probability < −10 using a KenLM English Wikipedia model, and (b) occurrence count > 4. Aho-Corasick
string matching is used for efficient lookup during post-processing. An optional forced phoneme
alignment step (wav2vec 2.0) can confirm detections by checking phoneme duration and probability
anomalies.

**Experiments 4–5 — augmented speech**: 80 Common Voice English files (avg. 10 s, correctly
transcribed baseline), augmented with non-speech clips of 1 s / 10 s / 20 s / 30 s at SNR = 9 dB.
Two scenarios: non-overlapped (NO, noise prepended/appended) and overlapping (OL, noise mixed with
speech). Total augmented dataset: 416,000 files. Experiment 5 uses silence augmentation (960 files)
for comparison.

**Experiment 6 — Whisper parameter tuning**: Beam sizes {1, 3, 5} and hallucination silence
threshold parameter {1, 5, 10, 20 seconds} evaluated on the augmented speech dataset.

**Experiment 7 — mitigation comparison**: Methods compared — (1) no post-processing, (2) beam
size = 1, (3) hallucination silence threshold = 20, (4) WebRTC VAD, (5) SileroVAD,
(6) delooping + BoH removal, (7) SileroVAD + delooping + BoH. VAD methods concatenate detected
speech segments before submitting to Whisper. WER evaluation uses fresh Freesound files not used
to build BoH. DCCRN denoising was also tested but did not reduce hallucinations.

## Results

* Whisper large-v3 hallucinated on **40.3%** of 301,317 non-speech audio files; **9.1%** of
  hallucinations involved looping
* **1,270** unique strings appeared more than once, accounting for **67.08%** of all
  hallucinations (41,231 unique outputs in total)
* "thank you" alone: **24.76%** of all hallucinations; "thanks for watching": **10.32%** —
  together these two cover **~35%** of all hallucinated outputs
* Duration effects on non-speech clips: 1 s → **52.1%** hallucination rate; 10 s → **11.6%**
  (lowest); 20 s → **27.4%**; 30 s → **62.3%**
* Speech augmented with 30 s non-speech: detected hallucination **44.5%** (NO) / **46.1%** (OL)
* Beam size 5 increases detected hallucinations to **28.2%** vs. beam=1 at **19.5%** (NO case)
* Hallucination silence threshold = 20 s reduces hallucination rate to **14.7%** (NO) — modest
  improvement vs. **21.3%** baseline
* **Baseline WER** (no mitigation): **104.8%** (NO) / **112.0%** (OL)
* Hallucination silence threshold = 20: WER **39.8%** (NO) / **53.7%** (OL)
* WebRTC VAD: WER **68.3%** (NO) / **75.4%** (OL)
* Delooping + BoH alone: WER **17.1%** (NO) / **21.1%** (OL), detected hallucinations **0.0%**
* SileroVAD alone: WER **8.0%** (NO) / **10.8%** (OL)
* SileroVAD + delooping + BoH (best): WER **6.5%** (NO) / **9.4%** (OL), hallucinations **0.0%**

## Innovations

### Bag of Hallucinations (BoH)

A systematically derived, publicly released list of Whisper hallucination strings filtered by
n-gram language model probability and occurrence frequency. Unlike ad-hoc blacklists, the BoH is
constructed from a large-scale empirical study and is available at
https://github.com/DSP-AGH/ICASSP2025_Whisper_Hallucination. The BoH is customisable: the
filtration criteria can be adjusted for different use cases (e.g., removing "subtitles by ..." when
transcribing physician dictation).

### Large-Scale Non-Speech Hallucination Taxonomy

The first systematic study using 301,317 non-speech audio files to characterise Whisper's
hallucination distribution, revealing the strong concentration of outputs and the YouTube
transcription artefacts embedded in Whisper's training data.

### Duration-Hallucination Interaction Discovery

The paper identifies that Whisper's 30-second segment boundary is a primary driver of hallucination
rate increases. Clips that cross this boundary trigger Whisper's internal heuristics and produce a
disproportionately high number of Top-30 hallucinations rather than audio-specific outputs. This
finding directly informs how audio should be chunked before ASR inference.

### Lightweight Post-Processing Pipeline

A two-stage pipeline — delooping followed by Aho-Corasick BoH matching — achieves **17.1% WER**
on augmented speech with no model changes, outperforming beam size reduction and Whisper's native
hallucination silence threshold. When combined with SileroVAD, it reaches **6.5% WER**.

## Datasets

* **Audioset** (Google): ~2.1M clips (subset: 253,278 non-speech after filtering + 8,272 eval),
  10-second YouTube audio clips, 527 sound classes, publicly available
* **Musan**: 931 non-speech files (noise subset after speech/music removal), public domain
* **UrbanSound8K**: 8,733 non-speech files, 10 urban sound classes, publicly available
* **FSD50K** (Freesound 50K): 29,074 non-speech files, human-labeled, publicly available
* **Common Voice** (Mozilla): 80 English speech files used for augmentation experiments,
  average duration 10 s, publicly available under CC0
* **Freesound / freenoise.org**: Additional non-speech sound files for the final WER evaluation
  experiment, ensuring no overlap with the BoH training set
* Synthetic noise/silence: 9,301 generated files at lengths 0.1–30 s and volumes −30 to −2 dBFS

## Main Ideas

* Whisper hallucinations on non-speech audio are highly predictable — **35%** of all hallucinations
  are just two strings. A small BoH filter can catch the most damaging outputs with minimal false
  positive risk, applicable to the Rezolve post-correction pipeline as a low-cost safeguard.
* The 30-second segment boundary is a critical threshold: hallucination rate jumps sharply past
  this limit. Production audio clips for Rezolve should be chunked to stay under 30 seconds where
  possible.
* SileroVAD + BoH post-processing reduces WER from over **100%** to **6.5%** on heavily augmented
  speech. This motivates using VAD as a pre-processing step in the Rezolve STT harness to strip
  non-speech lead-in/lead-out before Whisper inference.
* Beam size reduction (beam=1) does not mitigate non-speech hallucinations; it produces nearly
  identical hallucination rates as the default (beam=5). Reducing beam size only affects WER when
  combined with other methods and should not be used as a standalone hallucination fix.
* The BoH pipeline is model-agnostic at the text output level — it can be applied to any Whisper
  variant (including fine-tuned versions) and provides a concrete baseline for evaluating whether
  Granite model outputs exhibit a different hallucination profile on short non-speech clips.

## Summary

Barański et al. investigate a well-known but under-characterised failure mode of Whisper ASR: the
generation of hallucinated text when the input audio contains no speech. Rather than relying on
imprecise phonetic similarity measures to define hallucinations, the paper constructs a controlled
setting — running Whisper exclusively on verified non-speech audio — where every output is
definitionally a hallucination. This clean experimental design enables a large-scale empirical
characterisation across 301,317 audio files from four public sound datasets, with additional
experiments on speech augmented with non-speech sounds.

The methodology proceeds through six experiment groups. Experiment 1 collects an exhaustive
hallucination list from non-speech audio; Experiments 2–3 examine how clip duration and sound
category affect hallucination rate. The authors construct the Bag of Hallucinations (BoH) by
filtering the raw list using an n-gram language model (log probability < −10) and a frequency
threshold (> 4 occurrences). Experiments 4–5 extend to augmented speech with different noise
durations and positions. Experiment 6 evaluates Whisper's internal parameters (beam size,
hallucination silence threshold). Experiment 7 benchmarks full mitigation strategies end-to-end
using WER on held-out Freesound material.

The headline results show hallucinations are surprisingly predictable: **40.3%** of non-speech
clips trigger a hallucination, but **35%** of all hallucinations are just two strings. The
30-second Whisper segment boundary is identified as a primary trigger for elevated hallucination
rates. Among mitigation strategies, SileroVAD + delooping + BoH achieves the best WER of **6.5%**
(non-overlap) versus a raw baseline of **104.8%**, while BoH alone (without VAD) achieves
**17.1% WER** — a strong result for a purely text-side, model-agnostic filter.

For this project (t0014, Granite short-clip robustness), the paper is directly relevant at two
levels. First, the hallucination patterns it documents for Whisper provide a benchmark against which
Granite's behaviour on short, potentially noisy clips can be compared — if Granite exhibits lower
hallucination rates on non-speech clips, that is a concrete robustness advantage. Second, the BoH
post-processing pipeline is immediately applicable as a defensive layer for the Rezolve STT harness
regardless of which model is used, offering measurable WER improvement with no model changes.
