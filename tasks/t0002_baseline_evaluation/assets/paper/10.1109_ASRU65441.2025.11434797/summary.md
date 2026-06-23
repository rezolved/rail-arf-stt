---
spec_version: "3"
paper_id: "10.1109_ASRU65441.2025.11434797"
citation_key: "Ayache2024"
summarized_by_task: "t0002_baseline_evaluation"
date_summarized: "2026-06-23"
---

# WhisperNER: Unified Open Named Entity and Speech Recognition

## Metadata

* **File**: `files/ayache_2024_whisperner-joint-asr-ner.pdf`
* **Published**: 2024 (arXiv); proceedings published December 2025
* **Authors**: Gil Ayache 🇮🇱, Menachem Pirchi 🇮🇱, Aviv Navon 🇮🇱,
  Aviv Shamsian 🇮🇱, Gill Hetz 🇮🇱, Joseph Keshet 🇮🇱
* **Venue**: 2025 IEEE Automatic Speech Recognition and Understanding
  Workshop (ASRU)
* **DOI**: `10.1109/ASRU65441.2025.11434797`

## Abstract

Integrating named entity recognition (NER) with automatic speech
recognition (ASR) can significantly enhance transcription accuracy and
enrich its content. We introduce WhisperNER, a novel model that
facilitates joint speech transcription and entity recognition.
WhisperNER supports open-type NER, enabling recognition of various
entities during inference. Building on recent advancements in open NER
research, we augment a large synthetic dataset with synthetic speech
samples. This approach enables us to train WhisperNER on numerous
examples with various NER tags. During training, the model is prompted
with NER labels and optimized to produce the transcribed utterance
alongside the corresponding tagged entities. For evaluation, we generate
synthetic speech for commonly used NER benchmarks and annotate existing
ASR datasets with open NER tags. Our experiments show that WhisperNER
outperforms natural baselines in both out-of-domain open-type NER and
supervised fine-tuning.

## Overview

WhisperNER addresses a fundamental limitation of pipeline-based
speech-NLP systems: error propagation. In standard pipelines an ASR
model transcribes audio to text and a separate NER model then labels
entities in that text. Transcription errors compound NER errors because
the NER component never sees the original audio signal. WhisperNER
eliminates the intermediate text representation by extending the Whisper
large-v2 encoder-decoder architecture to produce tagged transcriptions
directly from audio. The model receives a list of entity type labels as
a prompt injected into the decoder at inference time and outputs both the
transcription and any matched entity spans in a single decoding pass.

A critical design feature is open-type NER: the model is not trained to
recognise a fixed closed set of entities. Instead, it generalises to
entity types provided at inference time that it has never seen during
training. This is achieved by training on 350K synthetic examples drawn
from the NuNER dataset (Bogdanov et al., 2024), augmented with synthetic
speech generated via text-to-speech. The training set covers 1.8 million
unique entity types, forcing the decoder to treat entity labels as
generic instructions rather than memorised class labels.

The paper introduces three evaluation datasets — VoxPopuli-NER,
LibriSpeech-NER, and Fleurs-NER — created by annotating existing ASR
benchmarks with open-type NER labels using an LLM-based annotation
scheme. On zero-shot open-type NER, WhisperNER achieves **56.25 F1**
on VoxPopuli-NER, outperforming the best pipeline baseline (GLiNER at
**52.29 F1** average) while requiring no additional parameters beyond
the Whisper architecture. On supervised fine-tuning using MIT-Movie and
MIT-Restaurant, WhisperNER reaches **81.35 F1** and **72.74 F1**
respectively, surpassing pipeline competitors that add 248M-459M params.

The paper also introduces two practical mechanisms: logit-based
precision-recall control via an entity start-token bias, and negative
sampling with entity type dropout to reduce hallucination.

## Architecture, Models and Methods

**Base model.** WhisperNER is built on Whisper large-v2, an
encoder-decoder transformer. The encoder processes mel-spectrogram
features from raw audio. The decoder autoregressively generates tokens
conditioned on encoder hidden states and a user-supplied entity type
prompt.

**Prompt injection.** A set of entity type labels `t = [t1, t2, ...,
tk]` is prepended to the decoder context at decoding start. The decoder
generates tokens conditioned jointly on the audio encoder output and the
entity type prompt, interleaving transcribed text with entity span
markers.

**Entity tagging formats.** Two output formats are evaluated:
* *BIO tagging* (WhisperNER-BIO): each token tagged with B/I/O labels
  per entity type, e.g., `astronaut(B-occupation)`. Stronger per-token
  supervision but increases output sequence length substantially.
* *Start/end marker format* (WhisperNER): entities wrapped with markers,
  e.g., `<occupation>astronaut<occupation>>`. Adds fewer tokens, keeping
  sequence length close to the Whisper-only baseline.

**Training objective.** Standard cross-entropy over the full output
sequence (transcription + entity tags). The Whisper encoder is frozen;
only the decoder weights are updated. Training: 250K steps, learning
rate 1e-6, linear decay scheduler.

**Training data.** 350K samples from the NuNER synthetic dataset, each
augmented with synthetic audio generated via TTS. The dataset spans
1.8M unique entity types.

**Negative sampling.** Each training example is augmented with negative
entity labels sampled from a randomly selected other training example
(approximately 2 negative examples per positive, ~66% negative types).
This teaches the model to suppress entity tags for absent types. Ablation
shows this contributes the largest single F1 gain (+7.92 F1 on MIT
benchmarks from 17.91 to 25.83).

**Entity type dropout.** A random subset of entity types is dropped from
both the prompt and output sequence during training, reducing entity
hallucination at inference. Combined with negative sampling, F1 rises
from 25.83 to 26.44 with improved WER (8.28 to 8.05).

**Precision-recall control.** A scalar bias is added to the entity start
token `<` logit at inference time. Positive bias raises recall; negative
bias raises precision. Evaluated on VoxPopuli-NER; shown to give
significant control over the precision-recall curve without retraining.

**Baselines.** Three pipeline systems: GLiNER-L (encoder transformer,
zero-shot NER, +459M params), NuNER zero-span (GLiNER architecture on
NuNER data, +459M params), and GNER-T5-base (generative T5 NER,
+248M params). All use Whisper large-v2 as the ASR frontend.

**Evaluation metrics.** NER F1 (span-level: both transcript text AND NER
label must be correct — a demanding dual requirement) and WER.

**Evaluation datasets:**
* VoxPopuli-NER: 879 samples, 2,469 unique entity types (political).
* LibriSpeech-NER: 1,604 samples, 3,674 unique entity types (audiobook).
* Fleurs-NER: 441 samples, 1,440 unique entity types (multilingual,
  English subset).
* MIT-Movie: ~14K samples, 12 entity types (supervised fine-tuning).
* MIT-Restaurant: ~10K samples, 8 entity types (supervised fine-tuning).

MIT benchmarks converted to speech using AWS Polly TTS for evaluation.

## Results

* Zero-shot average F1 (3 benchmarks): WhisperNER **53.53**, GLiNER
  **52.29**, NuNER **49.64**, GNER-T5-base **42.72**
* VoxPopuli-NER zero-shot F1: WhisperNER **56.25**, WhisperNER-BIO
  **55.79**, GLiNER **53.55**, NuNER **52.18**, GNER **45.31**
* LibriSpeech-NER zero-shot F1: WhisperNER **50.84**, WhisperNER-BIO
  **50.40**, GLiNER **48.97**, NuNER **43.65**, GNER **35.68**
* Fleurs-NER zero-shot F1: WhisperNER-BIO **54.42**, WhisperNER
  **53.50**, GLiNER **54.35**, NuNER **53.11**, GNER **47.15**
* WER cost of NER (VoxPopuli): WhisperNER **9.22%** vs pipeline
  baseline **8.32%** — overhead of **+0.90 pp**
* Supervised fine-tuning MIT-Movie: WhisperNER **81.35 F1** /
  **2.31% WER**, WhisperNER-BIO **80.91 / 2.64**, GLiNER **75.34 /
  3.34**, NuNER **75.25 / 3.34**, GNER **61.12 / 3.34**
* Supervised fine-tuning MIT-Restaurant: WhisperNER-BIO **72.74 F1** /
  **4.74% WER**, WhisperNER **71.51 / 4.02**, NuNER **71.40 / 5.48**,
  GLiNER **71.09 / 5.48**, GNER **57.90 / 5.48**
* Parameter overhead vs pipeline baselines: WhisperNER **0 extra
  parameters**; GLiNER/NuNER add **459M**; GNER adds **248M**
* Negative sampling ablation (25K steps, MIT benchmarks): no negatives
  **17.91 F1**, +negatives **25.83 F1**, +negatives +dropout **26.44 F1**
* Optimal negative examples: 2 negatives gives best F1 (**26.43**) at
  near-best WER (**8.31%**)
* Zero-shot cross-lingual (English-trained model on VoxPopuli):
  Spanish **29.3 F1 / 4.8% WER**, French **28.6 F1 / 13.9% WER**

## Innovations

### Joint ASR + Open-Type NER in a Single Decoder Pass

WhisperNER is the first model to perform open-type NER directly from
speech in a single autoregressive decoder pass. Prior end-to-end NER-
from-speech models supported only fixed, closed entity sets. Prompting
the decoder with entity type labels at inference time allows any entity
category to be targeted, including types unseen during training.

### Prompt-Based Entity Generalisation via Synthetic Data

Training on 350K samples spanning 1.8M unique entity types forces the
model to treat NER labels as generic instructions rather than memorised
class tokens. This design is the key mechanism for open-type
generalisation and separates WhisperNER from closed-set SLU models.

### Logit-Based Precision-Recall Control

Standard discriminative NER models tune precision-recall via
classification thresholds. Generative autoregressive models do not
expose such thresholds directly. WhisperNER adds a scalar bias to the
entity start token logit at inference time, giving users control over
the tradeoff without retraining — practical for production deployments
where false-positive and false-negative costs differ.

### Negative Sampling and Entity Type Dropout

Training with negative entity labels and random entity type dropout
substantially reduces entity hallucination and improves generalisation.
The +7.92 F1 gain from negative sampling alone is the largest
contributor to final model quality.

### Open-Type NER Speech Benchmarks

VoxPopuli-NER, LibriSpeech-NER, and Fleurs-NER are released as new
evaluation benchmarks filling a gap in speech-NER evaluation
infrastructure, enabling future work to measure open-type NER on speech
without constructing new datasets.

## Datasets

* **VoxPopuli** (Wang et al., 2021): multilingual speech corpus, English
  subset. VoxPopuli-NER: 879 samples, 2,469 unique entity types.
  License: CC0.
* **LibriSpeech** (Panayotov et al., 2015): audiobook ASR corpus, clean
  subset. LibriSpeech-NER: 1,604 samples, 3,674 unique entity types.
  License: CC BY 4.0.
* **Fleurs** (Conneau et al., 2022): multilingual speech, English subset.
  Fleurs-NER: 441 samples, 1,440 unique entity types. License: CC BY 4.0.
* **MIT-Movie / MIT-Restaurant** (Liu et al., 2013): closed-set NER
  benchmarks; ~14K and ~10K text samples, 12 and 8 entity types. Speech
  versions generated via AWS Polly TTS.
* **NuNER synthetic dataset** (Bogdanov et al., 2024): large-scale
  textual open NER training data; 350K samples selected by WhisperNER
  authors, 1.8M unique entity types. TTS audio added for training.

All evaluation datasets (VoxPopuli-NER, LibriSpeech-NER, Fleurs-NER,
augmented NuNER) are released publicly alongside source code and model
weights at the authors' repository.

## Main Ideas

* Joint ASR+NER in a single model eliminates error propagation from the
  ASR stage and adds zero parameters over the Whisper backbone —
  directly applicable to Rezolve's entity accuracy goal without adding
  a separate NER component on top of Whisper.
* Open-type NER via prompt injection means WhisperNER can target
  Rezolve-specific entity categories (brand names, SKUs, product lines)
  at inference time by listing them in the entity type prompt — no
  retraining required to add or change entity types.
* The logit-based precision-recall control maps directly onto the
  Rezolve confidence-routing framework: a conservative negative bias
  raises precision (fewer false entity extractions), supporting an
  "accept" routing policy; a positive bias raises recall, supporting
  a "correct/clarify" policy where missing entities are the primary
  risk.
* WER overhead is small but real (+0.9 pp on VoxPopuli). This must be
  measured on gold-92 to confirm it stays within the <8% action-
  critical WER target.
* The synthetic-speech training data (TTS-augmented NuNER) introduces
  acoustic mismatch with natural speech — the paper flags this as a
  limitation. Rezolve production audio (accented English, ecommerce
  domain) may show larger WER degradation; domain fine-tuning on
  production audio would likely be needed before deployment.
* Publicly released model weights allow low-cost evaluation of
  WhisperNER on gold-92, making it a strong candidate to include in
  t0002_baseline_evaluation alongside Deepgram and plain Whisper
  Large v3.

## Summary

Ayache et al. propose WhisperNER to solve error propagation in
pipeline-based speech-NLP systems. In standard ASR+NER pipelines,
transcription errors in the first stage degrade entity recognition in
the second stage. The paper also identifies a key gap: existing end-to-
end NER-from-speech models support only fixed, closed entity sets,
limiting their applicability to dynamic or domain-specific scenarios
where entity vocabularies change over time.

WhisperNER extends Whisper large-v2 by conditioning the decoder on a
user-supplied list of entity type labels at inference time. The model is
trained on 350K samples from the NuNER synthetic dataset augmented with
TTS-generated audio, spanning 1.8M unique entity types. Training
incorporates negative entity sampling (~66% negative types per example)
and entity type dropout to reduce hallucination. Only the decoder is
updated; the Whisper encoder is frozen. A scalar logit bias on the
entity start token provides inference-time precision-recall control
without retraining.

On zero-shot open-type NER, WhisperNER achieves **53.53 F1** averaged
across VoxPopuli-NER, LibriSpeech-NER, and Fleurs-NER, outperforming
the best pipeline baseline (GLiNER at **52.29 F1**) while adding no
parameters over Whisper large-v2. Pipeline baselines add 248M-459M
NLP parameters on top of the same Whisper backbone. On supervised fine-
tuning, WhisperNER reaches **81.35 F1** on MIT-Movie at **2.31% WER**,
outperforming all baselines on both metrics simultaneously. The WER cost
of NER integration is modest at approximately +0.9 pp on VoxPopuli.

For the Rezolve STT project, WhisperNER is the most directly relevant
paper in the corpus: it directly targets the entity accuracy problem by
integrating NER into ASR, uses the same Whisper architecture targeted
for fine-tuning in this project, and its open-type prompt interface
allows Rezolve-specific entities to be targeted without retraining. The
logit-bias precision-recall control maps onto the confidence-routing
framework. The main open question is performance on gold-92 (accented
English production audio), given the known acoustic mismatch from
synthetic TTS training data. A baseline evaluation of the released
WhisperNER model on gold-92 should be part of t0002_baseline_evaluation.
