---
spec_version: "3"
paper_id: "10.48550_arXiv.2505.08699"
citation_key: "Saon2025"
summarized_by_task: "t0014_granite_short_clip_robustness"
date_summarized: "2026-06-29"
---
# Granite-speech: open-source speech-aware LLMs with strong English ASR capabilities

## Metadata

* **File**: `files/saon_2025_granite-speech-asr.pdf`
* **Published**: 2025
* **Authors**: George Saon 🇺🇸, Avihu Dekel 🇺🇸, Alexander Brooks 🇺🇸, Tohru Nagano 🇺🇸, Abraham Daniels
  🇺🇸, Aharon Satt 🇺🇸, Ashish Mittal 🇺🇸, Brian Kingsbury 🇺🇸, David Haws 🇺🇸, Edmilson Morais 🇺🇸,
  Gakuto Kurata 🇺🇸, Hagai Aronowitz 🇺🇸, Ibrahim Ibrahim 🇺🇸, Jeff Kuo 🇺🇸, Kate Soule 🇺🇸, Luis Lastras
  🇺🇸, Masayuki Suzuki 🇺🇸, Ron Hoory 🇺🇸, Samuel Thomas 🇺🇸, Sashi Novitasari 🇺🇸, Takashi Fukuda 🇺🇸,
  Vishal Sunder 🇺🇸, Xiaodong Cui 🇺🇸, Zvi Kons 🇺🇸
* **Venue**: arXiv preprint
* **DOI**: `10.48550/arXiv.2505.08699`

## Abstract

Granite-speech LLMs are compact and efficient speech language models specifically designed for
English ASR and automatic speech translation (AST). The models were trained by modality aligning the
2B and 8B parameter variants of granite-3.3-instruct to speech on publicly available open-source
corpora containing audio inputs and text targets consisting of either human transcripts for ASR or
automatically generated translations for AST. Comprehensive benchmarking shows that on English ASR,
which was our primary focus, they outperform several competitors' models that were trained on orders
of magnitude more proprietary data, and they keep pace on English-to-X AST for major European
languages, Japanese, and Chinese. The speech-specific components are: a conformer acoustic encoder
using block attention and self-conditioning trained with connectionist temporal classification, a
windowed query-transformer speech modality adapter used to do temporal downsampling of the acoustic
embeddings and map them to the LLM text embedding space, and LoRA adapters to further finetune the
text LLM. Granite-speech-3.3 operates in two modes: in speech mode, it performs ASR and AST by
activating the encoder, projector, and LoRA adapters; in text mode, it calls the underlying
granite-3.3-instruct model directly (without LoRA), essentially preserving all the text LLM
capabilities and safety. Both models are freely available on HuggingFace
(https://huggingface.co/ibm-granite/granite-speech-3.3-2b and
https://huggingface.co/ibm-granite/granite-speech-3.3-8b) and can be used for both research and
commercial purposes under a permissive Apache 2.0 license.

## Overview

IBM Research's Granite-speech paper introduces two open-source speech-aware LLMs — a 2B and an 8B
parameter variant — that achieve state-of-the-art English ASR on publicly available benchmarks while
being trained exclusively on open-source corpora. The core architectural novelty is the combination
of a conformer CTC encoder with a windowed query-transformer (Q-former) speech modality adapter that
downsamples acoustic embeddings by 10x total (2x at the conformer input via frame stacking, 5x
inside the Q-former) before passing them to the frozen Granite-3.3 LLM decoder. LoRA adapters of
rank 64 are applied to the query and value projection matrices of all LLM attention layers to tune
the LLM to the speech distribution without corrupting the underlying text model.

The key engineering decision distinguishing this work from competing speech-aware LLMs is the
dual-mode inference design: the same model instance serves as a full-capability text LLM when no
audio token is present, and seamlessly activates its speech pathway when an `<|audio|>` token
appears in the prompt. This design preserves all text capabilities — function calling, RAG,
safety/guardrails — at the cost of two LLM forward passes instead of one. The CTC encoder uses block
attention with a 4-second block size and self-conditioned CTC (loss weights 0.2 for the intermediate
layer, 0.8 for the final layer), conditioning the encoder on its own intermediate predictions.

The paper demonstrates through careful ablations that character-level CTC tokenization (42 outputs)
outperforms BERT uncased (32K BPE) and Granite tokenization (49K BPE) after joint LLM training.
Similarly, the windowed Q-former with block size K=15 and N=3 queries outperforms both MLP and
cross-attention projectors across all evaluated corpora. Balanced data sampling with α=0.6 also
improves validation loss, especially for smaller corpora.

On the final Apache 2.0 model comparison, the granite-speech-3.3-8b achieves the lowest WER on all
nine evaluation corpora except GigaSpeech and SPGI (both excluded from training), beating Whisper
Large v3, Gemini 2.0 Flash, Qwen2-Audio, and Phi-4-mm. The 2B variant is competitive, particularly
on AMI (meeting recordings with distant microphones), suggesting robustness to adverse acoustic
conditions even at the smaller scale.

## Architecture, Models and Methods

### Acoustic Encoder

The encoder is a 10-layer conformer stack with the following configuration:

* Input: 80-dimensional logmel features at 16 kHz extracted every 10 ms
* Temporal subsampling 2x at input (stacking consecutive frame pairs → 50 vectors/s, 160-dim)
* Linear projection to conformer input dimension of 1024
* 8 attention heads, attention head size 128, convolution kernel size 15, output dimension 42
* Block self-attention with 4-second block size (inspired by Google USM)
* Self-conditioned CTC: auxiliary CTC loss at middle layer (weight 0.2) + final layer (weight 0.8)
* Training: 20 epochs, 1.5M updates, AdamW, batch size 256, triangular LR from 5e-5 to 5e-4 (ramp
  over 6 epochs) then decay to 5e-6 (14 epochs)
* Augmentation: additive noise SNR −5…20 dB (probability 0.25), SpecAugment (probability 0.9)
* Parameters: 275M (10-layer used in final models) or 430M (16-layer ablation only)

### Speech Modality Adapter (Q-former)

* Two-layer windowed Q-former inspired by SALMONN architecture
* Block size K=15 frames, N=3 trainable queries per window → 5x temporal downsampling
* Overall acoustic compression: 100 Hz → 10 Hz (10x total after 2x input subsampling)
* Trained jointly with LoRA adapters (rank 64) on query and value projection matrices across all LLM
  attention layers; CTC encoder kept frozen during this phase
* Training criterion: next-token prediction cross-entropy on ASR/AST transcripts
* Training: 3 epochs, 660K updates, AdamW, peak LR 1e-4, warm-up 1K steps, batch 128 utterances
* Hardware: 32 H100 GPUs
* Balanced corpus sampling factor α=0.6

### Text LLM and LoRA

* Base models: granite-3.3-instruct (2B and 8B parameter variants)
* LoRA rank 64 applied to query and value projection matrices across all attention layers
* Two-mode operation: speech mode (encoder + Q-former + LoRA active) vs text mode (LoRA disabled)
* Inference: beam search beam size 4, batched inference 4 samples/batch, token repetition penalty
  3.0 on generated tokens only

### Speech Translation Data Generation

* Synthetic AST data generated by translating CommonVoice 17 English to 7 target languages
* Ensemble filtering: Phi-4 (primary) and MADLAD-3B/10B (secondary) translation models
* Data retained only where WER between two outputs ≤ 0.3 (en→de) or CER ≤ 0.4 (en→ja)
* Filtering retains less than 50% of original data; cosine similarity less effective than WER/BLEU
* Chain-of-thought AST training: 30% of examples include explicit [Transcription]+[Translation] tags
* 24 ASR prompt variations and 8 CoT-AST prompt variations used during training

## Results

* **granite-speech-3.3-8b** achieves lowest WER on 7 of 9 English ASR evaluation corpora among all
  compared models in the sub-8B parameter class
* LibriSpeech clean test: **1.5% WER** (8b) and **1.6% WER** (2b) on Apache 2.0 models
* LibriSpeech other test: **3.0% WER** (8b) and **3.4% WER** (2b) on Apache 2.0 models
* AMI SDM (distant microphone, most challenging): **26.1% WER** (8b) vs **26.7% WER** (2b); 2b model
  is surprisingly competitive on difficult acoustic conditions
* AMI IHM: **9.2% WER** (8b) vs **9.4% WER** (2b) on Apache 2.0 models
* CommonVoice: **7.0% WER** (8b) vs **8.1% WER** (2b) on Apache 2.0 models
* VoxPopuli: **5.8% WER** (8b) vs **6.2% WER** (2b) on Apache 2.0 models
* Q-former (K=15) outperforms MLP projector: **9.6% vs 10.4% WER** on CommonVoice (8b LLM base)
* Character tokenization outperforms Granite BPE after joint LLM training: **9.5% vs 9.8% WER** on
  CommonVoice (characters+LLM vs Granite tokenization+LLM)
* 16-layer encoder outperforms 10-layer on CommonVoice: **11.2% vs 13.3% WER** (standalone CTC)
* AST ensemble filtering: selecting 20% of data by WER threshold improves average BLEU by more than
  **10 BLEU points** on en→de compared to using all data

## Innovations

### Dual-Mode Speech/Text Inference

The model operates in two distinct modes controlled solely by whether an `<|audio|>` token is
present in the prompt. In text mode, granite-3.3-instruct runs with LoRA disabled, fully preserving
all text LLM capabilities including function calling, RAG, and safety guardrails. This design
eliminates the need to maintain separate model instances and ensures safety properties of the base
LLM transfer to the speech interface — a key finding validated by multi-stage toxicity testing with
BOLD, AttaQ, and Toxigen benchmarks.

### Windowed Q-Former Temporal Downsampler

Rather than using an MLP or global cross-attention projector, the paper adapts the SALMONN Q-former
to process variable-length audio by dividing acoustic embeddings into fixed windows of K frames and
applying N trainable queries per window. With K=15 and N=3, this achieves 5x temporal compression
while attending locally to each window. The Q-former consistently outperforms MLP and
cross-attention alternatives across 8 of 9 evaluation corpora.

### Self-Conditioned CTC Encoder Training

The encoder uses self-conditioned CTC, applying an auxiliary CTC loss at the middle encoder layer
(weight 0.2) alongside the final-layer CTC (weight 0.8). This causes intermediate representations to
condition on earlier encoder predictions, relaxing the conditional independence assumption of
standard CTC and improving encoder quality before joint LLM fine-tuning.

### Ensemble-Based AST Training Data Filtering

To generate reliable synthetic speech translation data, two MT models (Phi-4 primary, MADLAD
secondary) are used, and only examples where the two outputs agree below a WER/CER threshold are
retained. This strategy improves average BLEU by more than 10 points on en→de when keeping only 20%
of the data, demonstrating that translation quality filtering far outweighs quantity for AST.

## Datasets

### Training (ASR)

* **MLS English** — 44,000 hours, audiobooks, Apache 2.0
* **GigaSpeech** — 10,000 hours, YouTube/podcasts, non-commercial (excluded from Apache 2.0 models)
* **YODAS** — 10,000 hours, YouTube videos, Apache 2.0 (replaces GigaSpeech in released models)
* **SPGI Speech** — 5,000 hours, earnings reports, non-commercial (excluded from Apache 2.0 models)
* **CommonVoice 17.0** — 2,600 hours, user-uploaded audio, CC0
* **Fisher** — 2,000 hours, telephone conversations, LDC license
* **LibriSpeech** — 960 hours, audiobooks, CC BY 4.0
* **VoxPopuli** — 500 hours, European parliamentary speeches, CC0
* **Switchboard** — 260 hours, telephone conversations, LDC license
* **TED LIUM** — 200 hours, TED talks, non-commercial (excluded from Apache 2.0 models)
* **AMI** — 100 hours, meeting recordings, CC BY 4.0
* **Voicemail** — 80 hours, voicemail messages
* **CallHome** — 18 hours, telephone conversations, LDC license

### Evaluation (ASR)

CommonVoice, GigaSpeech, MLS English, LibriSpeech clean+other, SPGI, AMI IHM, AMI SDM, VoxPopuli

### Evaluation (AST)

* **CoVoST2** — En-De and En-Ja language pairs, BLEU metric; publicly available
* **FLEURS** — 7 language pairs (en→de, es, fr, it, ja, pt, zh), BLEU metric; publicly available

## Main Ideas

* Granite-speech-3.3-8b sets a new open-source English ASR baseline, beating Whisper Large v3 and
  Qwen2-Audio on 7 of 9 standard benchmarks — making it a high-priority candidate for evaluation in
  the Rezolve gold-92 benchmark against production Deepgram.
* The 2B model is surprisingly competitive on difficult acoustic conditions (AMI SDM: **26.7%** vs
  **26.1% WER** for 8b), offering a better latency–accuracy trade-off worth evaluating on short
  investor-relations clips where the smaller model may meet the 800 ms p50 budget more easily.
* The dual-mode architecture preserves full LLM capabilities in text mode — a single Granite-speech
  instance could serve as both STT and entity-aware post-correction LLM, potentially collapsing
  Rezolve's two-step Deepgram + LLM correction pipeline into one model call.
* Training on ~76K hours of Apache 2.0 audio beats models with far more proprietary training data,
  suggesting that fine-tuning Granite-speech on Rezolve production audio could yield significant
  entity accuracy gains with a small domain-specific dataset.
* Future work noted by authors includes contextual biasing for keyword recognition and previous
  dialog turns — directly aligned with Rezolve's entity boosting and confidence-routing objectives,
  making this paper a forward reference for those research directions.
* Character-level CTC tokenization outperforms BPE after joint LLM training — a design principle to
  carry forward when evaluating or fine-tuning any conformer-based encoder for Rezolve's
  domain-specific vocabulary.

## Summary

Saon et al. (IBM Research, 2025) introduce Granite-speech-3.3, a family of open-source speech-aware
LLMs in 2B and 8B parameter variants, designed primarily for English ASR. The central research
question is whether compact models trained exclusively on publicly licensed audio corpora (~76K
hours Apache 2.0 compatible data) can match or surpass models trained on orders of magnitude more
proprietary data. The motivation is both scientific — advancing open-source speech models — and
practical, enabling commercial deployment without licensing barriers.

The architecture integrates three components trained sequentially: a 10-layer conformer CTC encoder
with block attention and self-conditioned CTC (1.5M updates, 275M parameters), a windowed Q-former
speech modality adapter achieving 10x total acoustic compression (660K updates, 32 H100 GPUs), and
LoRA adapters (rank 64) applied to all LLM attention layers. The design supports dual-mode
inference: the same model weights serve as the base granite-3.3-instruct text LLM (LoRA off) or as a
speech-aware model (encoder + Q-former + LoRA active) depending on whether an `<|audio|>` token
appears in the prompt. Key training innovations include character-level CTC tokenization, balanced
corpus sampling with α=0.6, and ensemble-based MT filtering for synthetic AST data that retains
under 50% of examples but improves BLEU by more than 10 points.

The 8B model achieves the lowest WER among all sub-8B parameter models on 7 of 9 English ASR
benchmarks, including **1.5% WER** on LibriSpeech clean, **3.0%** on LibriSpeech other, **9.2%** on
AMI IHM, **26.1%** on AMI SDM, and **5.8%** on VoxPopuli — beating Whisper Large v3, Gemini 2.0
Flash, Qwen2-Audio, and Phi-4-mm. The 2B model is competitive, especially on AMI SDM (**26.7%
WER**), suggesting robustness to adverse acoustic conditions at smaller scale. Ablations confirm
that character-level CTC tokenization outperforms BPE variants after joint LLM training, and the
windowed Q-former outperforms MLP and cross-attention projectors.

For the Rezolve STT project, Granite-speech-3.3 is a high-priority candidate for the gold-92
benchmark evaluation. Its strong performance on conversational and meeting corpora (AMI, VoxPopuli)
that share acoustic characteristics with Rezolve production call-center audio makes it directly
relevant for entity accuracy benchmarking. The dual-mode design is particularly attractive: a single
model instance could handle both transcription and entity-aware post-correction, potentially
collapsing the two-step Deepgram + LLM correction pipeline and reducing voice-to-action latency
below the 800 ms p50 budget. The Apache 2.0 license removes all commercial deployment barriers, and
the planned future work on contextual biasing aligns directly with the Rezolve entity boosting
objective.
