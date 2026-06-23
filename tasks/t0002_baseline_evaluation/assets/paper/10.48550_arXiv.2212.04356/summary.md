---
spec_version: "3"
paper_id: "10.48550_arXiv.2212.04356"
citation_key: "Radford2022"
summarized_by_task: "t0002_baseline_evaluation"
date_summarized: "2026-06-23"
---
# Robust Speech Recognition via Large-Scale Weak Supervision

## Metadata

* **File**: `files/radford_2023_whisper-robust-speech-recognition.pdf`
* **Published**: 2022
* **Authors**: Alec Radford 🇺🇸, Jong Wook Kim 🇺🇸, Tao Xu 🇺🇸, Greg Brockman 🇺🇸, Christine McLeavey
  🇺🇸, Ilya Sutskever 🇺🇸
* **Venue**: arXiv preprint (eess.AS)
* **DOI**: `10.48550/arXiv.2212.04356`

## Abstract

We study the capabilities of speech processing systems trained simply to predict large amounts of
transcripts of audio on the internet. When scaled to 680,000 hours of multilingual and multitask
supervision, the resulting models generalize well to standard benchmarks and are often competitive
with prior fully supervised results but in a zero-shot transfer setting without the need for any
fine-tuning. When compared to humans, the models approach their accuracy and robustness. We are
releasing models and inference code to serve as a foundation for further work on robust speech
processing.

## Overview

Whisper is OpenAI's large-scale weakly supervised speech recognition system, trained on 680,000
hours of audio paired with transcripts collected from the internet. The central thesis is that prior
STT work over-relied on small, high-quality supervised datasets and expensive fine-tuning steps,
leaving a large gap between in-distribution performance and real-world robustness. By scaling weak
supervision by two orders of magnitude beyond prior work (SpeechStew topped out at 5,140 hours), the
authors demonstrate that a single model can transfer zero-shot to a broad range of domains without
any dataset-specific adaptation.

The paper makes a careful distinction between in-distribution and out-of-distribution
generalization. Supervised LibriSpeech models achieve very low WER on that benchmark but make
roughly twice as many errors as humans when evaluated on other datasets. Whisper Large V2 achieves a
**55.2%** average relative error reduction over the best comparable supervised model when evaluated
on 13 out-of-distribution datasets, despite similar LibriSpeech performance.

Beyond English transcription, Whisper is trained as a multitask model: it handles 99 languages,
X-to-English speech translation (125,000 hours of training data), language identification, voice
activity detection, and timestamp-aligned transcription — all from a single model controlled by
special decoder tokens. The authors release five model sizes (Tiny through Large V2) covering 39M to
1.55B parameters and open-source the inference code and text normalizer.

A secondary contribution is a detailed text normalizer that avoids penalising Whisper for innocuous
formatting differences (contractions, punctuation, number representation) versus genuine
transcription errors. The authors also develop robust long-form transcription heuristics — beam
search with temperature fallback, voice activity detection, and initial timestamp constraints — that
reduce average long-form WER from **11.0** (greedy only) to **10.0**.

## Architecture, Models and Methods

**Architecture**: Encoder-decoder Transformer (Vaswani et al., 2017). Input audio is resampled to 16
kHz and converted to an 80-channel log-magnitude Mel spectrogram using 25 ms windows with 10 ms
stride. The encoder uses a 2-layer Conv1D stem (filter width 3, GELU activation, stride 2 on second
layer) followed by Transformer blocks with sinusoidal position embeddings and pre-activation
residual connections. The decoder uses learned position embeddings with tied input-output token
representations. Encoder and decoder share the same width and depth.

**Model family** (Table 1):

| Model | Layers | Width | Heads | Parameters |
| --- | --- | --- | --- | --- |
| Tiny | 4 | 384 | 6 | 39M |
| Base | 6 | 512 | 8 | 74M |
| Small | 12 | 768 | 12 | 244M |
| Medium | 24 | 1024 | 16 | 769M |
| Large | 32 | 1280 | 20 | 1550M |

**Tokenizer**: Byte-level BPE from GPT-2 for English-only models; vocabulary refitted (same size)
for multilingual models.

**Multitask format**: Tasks are specified via special decoder tokens in sequence:
`<|startoftranscript|>` → language tag (99 tokens) → `<|transcribe|>` or `<|translate|>` → optional
`<|notimestamps|>` → output tokens → `<|endoftranscript|>`. The decoder is conditioned on previous
transcript context with 50% probability.

**Training data**: 680,000 hours of audio-transcript pairs scraped from the internet, split as 65%
English STT (438,218 h), 18% X→en translation (125,739 h), 17% multilingual STT (117,113 h covering
96 languages). Machine-generated transcripts are filtered with heuristics (case patterns,
punctuation absence, language mismatch via CLD2). Audio is segmented into 30-second chunks.

**Training**: AdamW optimiser, β1=0.9, β2=0.98, ε=10⁻⁶, weight decay=0.1, max grad norm=1.0. Linear
LR decay to zero after 2,048 warmup steps. 2²⁰ updates (~2-3 passes over the dataset). Batch size
256 segments. FP16 with dynamic loss scaling and activation checkpointing. No data augmentation or
regularisation for V1 Large. Large V2 adds SpecAugment (LibriSpeech Basic policy), Stochastic Depth
(0.1), and BPE Dropout (0.1) for 655,360 updates with batch 1024.

**Evaluation**: Zero-shot on all benchmarks — no training splits used. WER computed after extensive
text normalisation. Effective robustness measured relative to LibriSpeech across 12
out-of-distribution datasets.

**Long-form heuristics**: Beam search (5 beams), temperature fallback starting at 0 increasing by
0.2 to 1.0 if log-prob < −1 or gzip compression ratio > 2.4, VAD using no-speech probability
threshold 0.6 combined with log-prob threshold, previous-text conditioning when temperature < 0.5,
initial timestamp constrained to [0.0, 1.0] s.

## Results

* Whisper Large V2 achieves **2.7% WER** on LibriSpeech test-clean (beam search: **2.5%**), matching
  mid-2019 supervised state of the art.
* On 13 out-of-distribution datasets, Whisper Large V2 achieves **55.2%** average relative error
  reduction over the best supervised LibriSpeech model (wav2vec 2.0 Large, no LM).
* Best zero-shot WER on selected OOD benchmarks for Whisper Large V2: Artie **6.2%**, Common Voice
  **9.0%**, Fleurs En **4.4%**, TED-LIUM **4.0%**, CHiME-6 **25.5%**, CORAAL **16.2%**.
* On long-form transcription across 7 datasets, full heuristics reduce average WER from **11.0**
  (greedy) to **10.0**, outperforming NVIDIA STT Conformer-CTC Large and four commercial services.
* Human transcriber comparison on 25 Kincaid46 samples: Whisper WER **8.81%**; pure-human services
  ranged **8.65–10.5%**; computer-assisted best was **7.61%**, only 1.15 points better.
* On Multilingual LibriSpeech, zero-shot Whisper achieves **7.3 WER** averaged across 8 languages,
  outperforming fine-tuned XLS-R (**10.9**) and mSLAM-CTC (**9.7**).
* On CoVoST2 X→en speech translation, Whisper achieves **29.1 BLEU** zero-shot, a new state of the
  art (vs. Maestro 25.2, mSLAM-CTC 24.8).
* WER scaling with data: English WER drops from **30.5** (3,405 h) to **9.9** (681,070 h);
  multilingual WER from **92.4** to **29.2** over the same range.
* WER halves for approximately every **16×** increase in training data per language (log-log R² =
  **0.83** on Fleurs).
* Language identification accuracy on Fleurs: **64.5%** zero-shot vs. supervised SOTA **77.7%**
  (mSLAM-CTC); on the 82 overlapping languages: **80.3%**.

## Innovations

### Large-Scale Weak Supervision at 680,000 Hours

Prior weakly supervised STT datasets topped out at ~30,000 hours. Whisper scales to 680,000 hours by
sourcing audio-transcript pairs directly from the internet without requiring human-validated gold
transcripts. This two-order-of-magnitude increase eliminates the need for dataset-specific
fine-tuning to achieve competitive accuracy.

### Unified Multitask Format via Decoder Token Sequences

A single model handles transcription, translation, language identification, voice activity
detection, and timestamp alignment by prepending task-specifier tokens to the decoder input. This
eliminates the need for separate specialist models at each pipeline stage and enables prompting with
prior context or custom vocabulary.

### Zero-Shot Robustness as a Primary Evaluation Target

The paper establishes effective robustness — performance on out-of-distribution datasets relative to
a reference dataset — as the key metric. The analysis demonstrates that high in-distribution
accuracy can mask severe brittleness, and that zero-shot evaluation better predicts real-world
reliability.

### Text Normalisation for Fair WER Comparison

A detailed English text normaliser handles contractions, number/currency expressions, British vs.
American spellings, and punctuation differences before WER computation. Released open-source, this
normaliser enables fairer comparison of zero-shot models that produce natural transcriptions.

### Long-Form Transcription Heuristics

A practical set of decoding heuristics — beam search, temperature fallback, combined VAD thresholds,
previous-text conditioning, and initial timestamp constraint — enables reliable transcription of
arbitrarily long audio. Full heuristics reduce average WER from **11.0** to **10.0** on seven
long-form datasets.

## Datasets

**Training data** (collected from the internet, not publicly released):

* 438,218 hours English STT
* 125,739 hours X→en speech translation (98 source languages)
* 117,113 hours multilingual STT (96 languages)
* Total: 680,070 hours of audio-transcript pairs

**Evaluation datasets** (all publicly available, used zero-shot):

* LibriSpeech (Panayotov et al., 2015) — clean read speech, English
* TED-LIUM 3 (Hernandez et al., 2018) — TED talks, English
* Common Voice 5.1 / 9.0 (Ardila et al., 2019) — crowd-sourced, multilingual
* Artie bias corpus (Meyer et al., 2020) — demographic bias subset of Common Voice
* CallHome + Switchboard (LDC2002S09 / LDC2002T43) — telephone, English
* WSJ (LDC93S6B / LDC94S13B) — read speech, English
* CORAAL (Kendall & Farrington, 2021) — African American Language, 231 interviews
* CHiME-6 (Watanabe et al., 2020) — far-field meeting speech, English
* AMI-IHM / AMI-SDM1 — meeting speech, English
* VoxPopuli (Wang et al., 2021) — EU parliament, 16 languages
* Fleurs (Conneau et al., 2022) — 102 languages, few-shot evaluation
* Multilingual LibriSpeech (MLS) — 8 languages
* CoVoST2 (Wang et al., 2020) — X→en translation, 21 languages
* Kincaid46 — 46 diverse English recordings used for human transcriber comparison
* Earnings-21 / Earnings-22 (Del Rio et al., 2021) — earnings calls, domain-specific English

## Main Ideas

* **Whisper Large V2 is the primary open baseline for this project**: it achieves **2.7% WER** on
  LibriSpeech test-clean and near-human performance in real-world conditions, making it the
  appropriate open-source comparator to production Deepgram on gold-92.
* **Zero-shot evaluation is essential**: fine-tuned supervised models overfit to benchmark
  distributions; Whisper shows a 55.2% relative WER gap vs. supervised models on OOD data. Gold-92
  must be treated as out-of-distribution for honest baseline numbers.
* **Domain fine-tuning is the clear path forward**: the paper explicitly flags fine-tuning as a
  promising unexplored direction; the data scaling law (WER halves every 16× training hours) gives a
  principled basis for estimating how much Rezolve production audio is needed.
* **Prompting via previous-text conditioning and custom vocabulary** is natively supported by
  Whisper's decoder — a direct mechanism for injecting Rezolve-specific entity lists (brand names,
  product lines, SKUs) without full fine-tuning.
* **Model size vs. latency must be benchmarked on gold-92**: Whisper Small (244M) achieves **3.3%
  WER** on LibriSpeech with beam search; the right tier for the 800 ms p50 budget needs explicit
  measurement on Rezolve audio.
* **Long-form decoding heuristics are required for production use**: raw greedy decoding produces
  11.0% average WER vs. 10.0% with full heuristics; production deployment must use beam search with
  temperature fallback.

## Summary

Radford et al. present Whisper, a speech recognition system trained on 680,000 hours of weakly
supervised audio-transcript pairs scraped from the internet. The central research question is
whether scaling weak supervision — using noisy but abundant internet data rather than expensive
human-validated corpora — can match or surpass fully supervised approaches while achieving
substantially better real-world robustness. The work is motivated by the observation that prior
state-of-the-art models trained on LibriSpeech are effectively measuring in-distribution
generalization, not the out-of-distribution robustness needed for production deployment.

The approach uses a standard encoder-decoder Transformer trained end-to-end on 30-second audio
segments with a multitask format: all tasks (transcription, translation, language ID, VAD, timestamp
alignment) are encoded as decoder token sequences, allowing a single model to replace multiple
pipeline stages. Training uses AdamW with linear LR decay for approximately 2-3 passes over the
dataset without data augmentation, relying on dataset diversity for robustness. Five model sizes are
released (39M–1.55B parameters). A text normalizer and long-form decoding heuristics are developed
as essential practical components.

The key findings are that Whisper Large V2 achieves **55.2%** average relative error reduction over
the best comparable supervised model on 13 OOD datasets despite similar LibriSpeech performance, and
its transcription quality approaches professional human transcribers on Kincaid46 (Whisper **8.81%**
WER vs. best human service **7.61%**). For translation, Whisper achieves **29.1 BLEU** on CoVoST2
zero-shot, a new state of the art. A strong data scaling law is identified: WER halves for every 16×
increase in per-language training hours (log-log R² = 0.83 on Fleurs). Multitask and multilingual
training provides positive transfer at large model sizes.

For this project, Whisper Large V2 is the open-source baseline to benchmark against production
Deepgram on gold-92. The paper directly supports the research roadmap: fine-tuning Whisper on
Rezolve production audio is the most direct path to improving entity accuracy on investor-relations
and ecommerce terms. The custom vocabulary prompting mechanism is immediately actionable for
injecting brand names and product entities. The model size family gives a latency-accuracy trade-off
ladder to explore within the 800 ms p50 constraint.
