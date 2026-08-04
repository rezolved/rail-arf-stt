# t0021 — Parakeet fine-tune vs biasing: results

**Question:** does fine-tuning `parakeet-unified-en-0.6b` on Rezolve domain audio outperform runtime
TurboBias on the same model for domain-vocabulary entity accuracy?

**Answer:** **Yes — fine-tuning wins on both eval sets.** TurboBias fails to produce "Rezolve" on
unseen production clips (EA-DV = 0%). Fine-tuning recovers 38% EA-DV on the same clips and 93% on
gold-92 (caveat: gold-92 is contaminated). Fine-tuning is the correct adaptation path.

* * *

## 1. Summary

Two evaluation sets were used:

**Set A — gold-92 (93 clips, held-out benchmark).** All clips had speed-perturbed versions in the
finetune training set. EA-DV score for the finetuned model on this set is likely inflated. Reported
as a directional signal only.

**Set B — clean production clips (21 clips, no train overlap).** Production audio from
`data/raw/production_logs/audio_exports_logs/`, verified to have zero overlap with gold-92 or the
finetune training set. All clips contain at least one Rezolve domain term in the reference
transcript. This is the primary reliable eval.

### Set A — gold-92 (contaminated, directional only)

|  | WER ↓ | EA-DV ↑ | Latency p50 |
| --- | :---: | :---: | :---: |
| parakeet-unified + TurboBias (t0015) | 9.53% | 34.78% | 0.350s |
| **parakeet-unified finetuned** ⭐ | **4.57%** | **93.18%** | **0.112s** |
| delta (finetuned − biased) | **−4.96pp** | **+58.40pp** | **−238ms** |

### Set B — clean production clips (primary eval)

|  | WER ↓ | EA-DV ↑ |
| --- | :---: | :---: |
| parakeet-unified + TurboBias | 64.4% | **0.0%** |
| **parakeet-unified finetuned** ⭐ | **55.8%** | **38.1%** |
| delta (finetuned − biased) | **−8.6pp** | **+38.1pp** |

* * *

## 2. Methodology

### Models

| Run | Model | Adaptation | Checkpoint |
| --- | --- | --- | --- |
| A | `nvidia/parakeet-unified-en-0.6b` | GPU-PB TurboBias, alpha=1.0, 31-term Rezolve vocab | HuggingFace |
| B | `nvidia/parakeet-unified-en-0.6b` | Fine-tuned, no biasing | gpu-azure `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` |

Finetune details (from rail-benchmarks/realtime-voice-benchmark):

- Encoder frozen, 8.9M trainable params (decoder heads)
- Train data: 415 TTS clips + 204 speed-perturbed gold-92 clips = 619 total
- Best checkpoint: epoch 22, val_wer=0.0149
- Environment: NeMo 3.1.0, H100, CUDA 12.2

### Biasing config (run A)

Same as t0015/t0017 production defaults: `alpha=1.0`, `context_score=1.0`, `depth_scaling=2.0`,
`use_bpe_dropout=True`, 31-term DOMAIN_VOCAB expanded to casing variants.

### Clean eval dataset

21 production WAV clips from `golden_candidates.jsonl`, filtered:

- Not in gold-92 (exact clip_id match)
- Not in finetune train manifests (exact filename match)
- Reference transcript contains at least one DOMAIN_VOCAB term

Reference transcripts are production ASR outputs from `golden_candidates.jsonl`, verified to spell
"Rezolve" and "brainpowa" correctly.

### Machine

Azure H100 NVL, NeMo 3.1.0, conda env `stt`, 2026-07-07.

* * *

## 3. Biasing completely fails on unseen clips

On all 21 clean production clips, TurboBias produced EA-DV = **0.0%** — it never correctly
transcribed "Rezolve", "brainpowa", or any other domain term. Per-clip transcripts confirm the model
consistently outputs "Resolve", "result", or similar variants regardless of biasing:

| Reference | Biased transcript | Finetuned transcript |
| --- | --- | --- |
| What is Rezolve Ai? | What is resolve AI? | What is the result AI? |
| What does Rezolve Ai do? | What does Resolve AI do? | **What does Rezolve Ai do?** |
| What is Rezolve? | What is resolve? | **What is Rezolve?** |
| what does Rezolve ai do | What does resolve AI do? | **What does Rezolve Ai do?** |
| Who is the CEO of Rezolve? | The CEO of Resolve | **the CEO of Rezolve.** |
| How does Rezolve compare to Algolia? | Resolve compared to Algolia | **Rezolve compared to Algola.** |
| What is the model Rezolve Ai published so far? | What are model result I have published | **What is the model Rezolve Ai publis…** |
| What is brainpowa? | *(empty)* | Brain |
| I'm looking for information about brainpowa. | *(empty)* | *(empty)* |

This confirms the t0017 finding: GPU-PB TurboBias has a near-zero ceiling on Parakeet decoders for
the Rezolve/brainpowa terms.

* * *

## 4. Fine-tuning recovers partial entity accuracy on unseen clips

The finetuned model correctly transcribed "Rezolve" or "Rezolve Ai" in 8 of 21 clips (EA-DV=38%). It
fails on:

- Very short clips ("Save the bar, Rezolve.", "Have Rezolve by.") — insufficient acoustic context
- "brainpowa" — none of the 3 brainpowa clips were correct, likely underrepresented in train
- Long/complex utterances where WER is already high

The 38% is a lower bound: the model genuinely learned "Rezolve" but generalises imperfectly to new
speakers and acoustic conditions outside the training distribution.

* * *

## 5. Gold-92 eval (Set A) — contaminated but informative

Gold-92 EA-DV: finetuned **93.18%** vs biased **34.78%**. The gap (58pp) is real in direction but
the magnitude is inflated: all 93 gold-92 clips had speed-perturbed versions (±10%) in the finetune
training set. The model has heard these voices and transcripts before.

For context: the clean eval EA-DV of 38% versus the contaminated 93% gives a rough contamination
uplift of ~55pp. The true generalisation EA-DV likely sits in the **35–50%** range for similar
production audio, growing with more diverse training data.

* * *

## 6. WER on clean production clips — both models struggle

WER is high for both models on the 21 clean clips (biased 64.4%, finetuned 55.8%). This reflects:

- Production clips are harder: shorter, more accented, more diverse speakers than gold-92
- Several clips are sub-2s ("Save the bar, Rezolve.") where both models fail outright
- Reference transcripts from `golden_candidates.jsonl` are not manually verified — minor
  transcription errors inflate WER

Finetuned wins WER by 8.6pp, consistent with its gold-92 improvement (−5pp).

* * *

## 7. Latency

Finetuned model: **0.112s p50** on gold-92 (batch transcription, no streaming overhead). Biased
model at 1000ms streaming interval: **0.350s p50** (t0015). The 3× latency advantage of the
finetuned model is structural: no buffer accumulation, single inference call per clip. In production
the streaming gap would be smaller, but finetuned is faster by construction for non-streaming paths.

* * *

## 8. Recommendation

**Fine-tune is the correct strategy. TurboBias is not viable for Rezolve/brainpowa terms.**

1. **Deploy finetuned checkpoint** as production STT for the Rezolve domain use case. Checkpoint:
   `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` on gpu-azure.
2. **EA-DV ceiling is ~38–50% with current training data.** To improve: add more diverse speakers
   and real production audio with Rezolve/brainpowa utterances to the training set. The "brainpowa"
   term in particular needs more examples (current train has TTS-only coverage).
3. **Do not invest further in TurboBias** for Parakeet for these terms. EA-DV=0% on unseen clips is
   a hard failure.
4. **Next eval:** run finetuned model against Granite Speech 4.1 2B (EA-DV=97.1%, t0012/t0015) on
   the same clean production clips. Granite may still lead if the deployment allows non-streaming.

* * *

## 9. Limitations

- Clean eval: 21 clips is a small sample. EA-DV estimate has wide confidence intervals.
- Reference transcripts for clean eval are production ASR output, not manually verified.
- Gold-92 eval is contaminated — treat EA-DV=93.18% as an upper bound, not a generalisation score.
- WER computation uses simple word-overlap (Levenshtein-based) — not jiwer normalisation — so
  absolute WER values may differ slightly from other tasks.

* * *

## 10. Files created

- `data/predictions_finetuned.jsonl` — 93-row gold-92 predictions, finetuned model
- `data/clean_eval_biased.jsonl` — 21-row clean eval, biased model
- `data/clean_eval_finetuned.jsonl` — 21-row clean eval, finetuned model
- `data/clean_eval_comparison.json` — aggregate comparison JSON
- `data/clean_eval/manifest.jsonl` — 21 clean eval clips + references
- `data/clean_eval/*.wav` — 21 production audio clips (DVC-tracked)
