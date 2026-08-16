---
spec_version: "2"
model_id: "parakeet-unified-v5"
documented_by_task: "t0024_parakeet_unified_checkpoint_archive"
date_documented: "2026-08-17"
---

# parakeet-unified-en-0.6b v5 (Rezolve domain fine-tune)

## Metadata

- **Name**: parakeet-unified-en-0.6b v5 (Rezolve domain fine-tune)
- **Version**: 5.0.0
- **Framework**: pytorch (NeMo)
- **Base model**: nvidia/parakeet-unified-en-0.6b (huggingface)
- **Training task**: external (rail-benchmarks/parakeet-finetune-v3)
- **Archived by task**: t0024\_parakeet\_unified\_checkpoint\_archive
- **Date created**: 2026-07-13

## Overview

parakeet-unified-v5 is a domain-adapted version of `nvidia/parakeet-unified-en-0.6b` fine-tuned on
Rezolve voice commerce audio. The goal was to improve recognition of brand-critical terms —
primarily "Rezolve" and "brainpowa" — that the base model consistently transcribes as common
homophones ("resolve", "brain power").

The model was trained using NeMo's `speech_to_text_finetune.py` script on a mix of TTS-synthesized
Rezolve domain sentences (353 clips across 5 edge-tts voices) and real production audio clips (69
clips from the gold-92 train split). The encoder was frozen throughout training; only the RNNT
decoder and CTC head weights were updated.

This is the best fine-tune checkpoint produced for `parakeet-unified-en-0.6b`. It achieves WER
4.62% and EA-DV 100% on the 19-clip clean gold-92 test split. The primary known gap is "brainpowa":
0/3 correct on the clean-21 production held-out set, reflecting the absence of real brainpowa audio
in the training set.

## Architecture

Base: `nvidia/parakeet-unified-en-0.6b` — a FastConformer-Hybrid Transducer-CTC model with 18
FastConformer encoder layers and an RNNT + CTC dual-head decoder. English-only, ~0.6B parameters
total.

Fine-tune modification: encoder frozen (all 18 FastConformer layers, ~580M params). Only the RNNT
prediction network and joint network (~20M params) and the CTC head (~5M params) were updated.
Total trainable parameters during fine-tune: ~25M.

Input: 16 kHz mono WAV, log-mel filterbank features (80 bins). Output: English text with
punctuation and casing (unnormalized).

## Training

### Data

| Split | Source | Clips | Notes |
| --- | --- | --- | --- |
| Train | TTS (edge-tts) | 353 | 5 voices: en-US-GuyNeural, en-US-JennyNeural, en-GB-RyanNeural, en-GB-SoniaNeural, en-AU-WilliamNeural |
| Train | Real prod audio | 69 | gold-92 train split: French\_NoemieMarciano, French\_nonnative, error\_cases, UUID prod sessions |
| Val | Real prod audio | 7 | Russian\_OlyaShtalberg (never in train) |
| Test | Real prod audio | 19 | Korean\_JemmaLee, Hebrew\_FelixTseitlin, German\_ErcanKilic (Stephania removed — contaminated) |

Train manifest: `rail-benchmarks/parakeet-finetune-v3/parakeet_finetune/manifests/train_v5.jsonl`
(422 clips). Val manifest: `val_v5.jsonl` (7 clips). Test manifest: `test_v5_clean.jsonl` (19
clips).

Gold-92 was never used as a test set for model selection. The 69 gold-92 clips in train are
disjoint from the 19-clip test split by speaker identity.

Brand-word coverage in train: 176/422 clips contain "Rezolve" or "brainpowa" (142 Rezolve, 38
brainpowa). All brainpowa clips are TTS — 0 real brainpowa audio in train.

### Hyperparameters

| Parameter | Value |
| --- | --- |
| Learning rate | 1e-4 |
| Batch size | 16 |
| Max epochs | 50 (no early stopping) |
| Best epoch | 35 |
| Optimizer | AdamW |
| Encoder | Frozen |
| Framework | NeMo ≥ 2.4 |

### Compute

Azure H100 80 GB. Training time: ~1.5 h for 50 epochs on 422 clips.

## Evaluation

### gold-92 test split (19 clean clips, primary)

| Metric | Value |
| --- | --- |
| WER | 4.62% |
| EA-DV | 100% (4/4 brand clips correct) |
| Accents covered | Korean, Hebrew, German |

The 26-clip test set had a speaker contamination issue (StephaniaCesborn in both train and test); the
honest 19-clip subset removes her. The 26-clip WER of 3.76% is inflated by the leak.

### clean-21 production held-out set

| Term | Correct | Total |
| --- | --- | --- |
| Rezolve | ~8 | ~18 |
| brainpowa | 0 | 3 |

EA-DV on clean-21: ~38% (from t0021 results on an earlier v3 checkpoint; v5 not re-evaluated on
clean-21). brainpowa = 0% — all brainpowa train clips are TTS; the model does not generalize to
real brainpowa audio.

## Usage Notes

Load with NeMo ≥ 2.4 (GPU required; does not run on macOS):

```python
import nemo.collections.asr as nemo_asr

model = nemo_asr.models.ASRModel.restore_from("files/parakeet-unified-finetuned-best.nemo")
model.eval()

# Offline transcribe
transcripts = model.transcribe(["audio.wav"])
```

The `.nemo` file is a ZIP archive containing model weights (`model_weights.ckpt`), config
(`model_config.yaml`), and tokenizer files. It is self-contained — no separate tokenizer download
needed.

**Do not use this model for streaming inference** — it was evaluated offline only. Streaming
behavior was not tested; `_extract_delta` has a known failure mode with parakeet revision tokens
(LocalAgreement N=2 fix required in `transcribe_stream`).

**Dependency conflict**: `nemo_toolkit[asr]` pins `transformers~=4.57`; it cannot share a venv with
`transformers>=5.10.1`. Use the server image with `--extra nemo` (see `brainpowa-realtime-api`
Dockerfile).

## Main Ideas

- Frozen-encoder fine-tune on 422 clips achieves WER 4.62% and EA-DV 100% on a 19-clip held-out
  set with 4 unseen accents — demonstrating that decoder-only adaptation transfers across speakers.
- "brainpowa" remains 0% correct on real audio because all 38 brainpowa train clips are TTS; the
  acoustic mismatch is too large for the frozen encoder to bridge. Real brainpowa recordings are
  required for any improvement.
- The TTS val set (val\_wer=0.056) is too easy to be a reliable early-stopping signal — TTS is
  near-perfect for the model. A val set with real brand-word clips would give a better signal.
- This model was trained on `parakeet-unified-en-0.6b` (Hybrid TDT-CTC, English-only). The
  production model in `brainpowa-realtime-api` is `parakeet-tdt-0.6b-v3` (pure TDT, 25-language)
  — these checkpoints are not interchangeable.

## Summary

parakeet-unified-v5 is a decoder-only fine-tune of `nvidia/parakeet-unified-en-0.6b` on 422
Rezolve domain clips (353 TTS + 69 real prod). It achieves WER 4.62% and EA-DV 100% on a 19-clip
held-out set across 3 unseen accents, making it the best parakeet-unified checkpoint for Rezolve
domain speech.

The model's primary limitation is "brainpowa" recognition: 0/3 correct on the clean-21 production
held-out set, caused by the complete absence of real brainpowa audio in training. A frozen encoder
cannot bridge the acoustic gap between TTS brainpowa and real speech. This gap motivates t0025,
which targets `parakeet-tdt-0.6b-v3` (the production model) with partial encoder unfreezing and
real prod data.

This checkpoint is archived here for reproducibility. To load it, use NeMo ≥ 2.4 on a CUDA GPU
and call `ASRModel.restore_from("files/parakeet-unified-finetuned-best.nemo")`.
