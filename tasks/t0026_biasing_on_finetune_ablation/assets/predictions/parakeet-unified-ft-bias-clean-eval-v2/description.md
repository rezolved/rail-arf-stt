---
spec_version: "2"
predictions_id: "parakeet-unified-ft-bias-clean-eval-v2"
documented_by_task: "t0026_biasing_on_finetune_ablation"
date_documented: "2026-09-02"
---
# parakeet-unified-v5 (fine-tuned) + GPU-PB biasing on clean_eval_v2 (Arm D)

## Metadata

* **Name**: parakeet-unified-v5 (fine-tuned) + GPU-PB biasing on clean_eval_v2 (Arm D)
* **Model**: parakeet-unified-v5 (fine-tuned checkpoint) + GPU-PB context biasing
* **Datasets**: clean_eval_v2 (no registered dataset asset — see `## Data`)
* **Format**: jsonl
* **Instances**: 91
* **Created by**: t0026_biasing_on_finetune_ablation

## Overview

These predictions are Arm D of a 2x2 ablation crossing GPU-PB context biasing with
`parakeet-unified` domain fine-tuning on the 91-clip `clean_eval_v2` holdout. Arm D is the cell no
prior task has run: the fine-tuned checkpoint `parakeet-unified-v5`, decoded with `malsd_batch` beam
search and a GPU-PB boosting tree stacked on top of it. This completes Part B of
`t0024_biasing_pareto_and_ft_biasing_ablation`, which deferred exactly this run because the
fine-tuned checkpoint could not be located on any reachable machine at the time (suggestion
`S-0024-01`).

The purpose of this arm is to answer whether context biasing still adds brand accuracy once the
model has already been fine-tuned on Rezolve domain audio, or whether the two techniques are
redundant — i.e. whether biasing and fine-tuning fix the same errors or complementary ones. Three
sibling arms (A: base/no-bias, B: base+bias, C: fine-tuned/no-bias) were produced by other subagents
on the same 91 clips with the same shared scoring function, enabling direct paired comparison. This
asset documents Arm D specifically and cites Arm C for contrast, since C is Arm D's nearest
comparator (same checkpoint, biasing on vs. off).

## Model

The base model is `nvidia/parakeet-unified-en-0.6b`, a FastConformer-Hybrid Transducer-CTC
architecture (18 encoder layers, ~0.6B params total, English-only). The checkpoint used here is
`parakeet-unified-v5`, archived as a DVC model asset at
`tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/`. It was produced
by fine-tuning only the RNNT decoder and CTC head (~25M trainable params) with the encoder frozen,
on 422 Rezolve domain clips (353 TTS-synthesized + 69 real production clips), using AdamW at
learning rate 1e-4, batch size 16, for 50 epochs (best epoch 35 by validation WER). On its own
19-clip gold-92 test split, this checkpoint reaches WER 4.62% and EA-DV 100%, but 0/3 correct on
real "brainpowa" audio (all brainpowa training clips are TTS-only).

For this arm, the checkpoint is loaded with `nemo.collections.asr.models.ASRModel.restore_from(...)`
(confirmed in `code/run_ablation.py`) and decoded with `malsd_batch` beam search plus a GPU-PB
boosting tree applied via `boosting.apply_malsd_boost(...)` (confirmed in `code/boosting.py`), using
the fixed cell `context_score=3.0, depth_scaling=0.5, alpha=1.5`. This cell is the Pareto-frontier
biasing configuration selected on the *base* model by the prior task
`t0024_biasing_pareto_and_ft_biasing_ablation` (60.0% `brand_exact_rate` at 8.7% `neutral_wer` on
that sweep); it is applied here unchanged, not re-swept for the fine-tuned checkpoint.

## Data

Evaluation used the 91-clip `clean_eval_v2` holdout: 43 brand-containing clips (40 Rezolve, 3
brainpowa) and 48 neutral clips, mixing `quepasa_prod` (real production audio) and `clean_eval_21`
sources per the `source` field in each prediction row. `clean_eval_v2` has **no registered `dataset`
asset** in this project — `dataset_ids` is intentionally empty (`[]`). The raw manifest lives at
`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/`; this task additionally produced a
gitignored, path-fixed copy of the manifest at
`tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl` to resolve
absolute macOS audio paths on the GPU machine, without modifying t0021's files. All 91 clips were
successfully transcribed (91/91 `successful_requests`).

## Prediction Format

Each line of `predictions-clean-eval-v2.jsonl` is a JSON object, for example:

```json
{"clip_id": "1e1de7a1-11e0-4705-b923-ff0e6af87cde_turn4", "ref": "What is Rezolve Ai?", "hyp": "What is Rezolve Ai?", "brand": "Rezolve", "label": "EXACT", "wer": 0.0, "latency_seconds": 0.022, "source": "clean_eval_21"}
```

Fields:

* `clip_id` — unique identifier for the clip
* `ref` — ground-truth reference transcript
* `hyp` — model hypothesis transcript
* `brand` — `"Rezolve"`, `"brainpowa"`, or `null` for the 48 neutral (non-brand) clips
* `label` — `"EXACT"`, `"PHONETIC"`, or `"GARBAGE"` for brand clips; `null` for neutral clips
* `wer` — per-clip word error rate (float, 0.0–1.0+)
* `latency_seconds` — per-clip inference latency in seconds
* `source` — `"quepasa_prod"` (real production audio) or `"clean_eval_21"` (prior clean holdout)

## Metrics

Computed on all 91 clips via the shared scoring function (`results/ablation_metrics.json`, key
`"D"`), with Arm C (fine-tuned, no bias) shown for contrast:

| Metric | Arm C (FT, no bias) | Arm D (FT + bias) |
| --- | --- | --- |
| `brand_exact_rate` (overall) | 79.07% | **83.72%** |
| `brand_exact_rate` (Rezolve) | 82.50% | **87.50%** |
| `brand_exact_rate` (brainpowa) | 33.33% | 33.33% |
| `neutral_wer` | 27.14% | **48.79%** |
| `overall_wer` | 28.01% | 45.68% |
| avg inference time/item (s) | 0.02194 | 0.02199 |

A paired McNemar test on brand correctness, arm C vs. arm D (`results/mcnemar_results.json`, key
`"c_vs_d"`), gives `b=1, c=3, n_discordant=4, p_value=0.625` — not statistically significant at any
conventional threshold. For contrast, base-vs-fine-tuned-plus-bias (`"b_vs_d"`) gives
`b=0, c=20, n_discordant=20, p_value≈1.9e-6` — biasing+fine-tuning together is highly significant
relative to biasing alone on the base model, but that comparison conflates two levers at once.

## Main Ideas

* Arm D has the **highest brand_exact_rate of all four arms** (83.72% overall, 87.50% on Rezolve),
  but the McNemar test isolating the effect of adding biasing on top of the already fine-tuned
  checkpoint (`c_vs_d`: b=1, c=3, n_discordant=4) gives **p=0.625** — with only 4 discordant clips,
  this gain over Arm C (fine-tuned, no bias, 79.07%) is not distinguishable from noise.
* That marginal, non-significant brand gain comes at a **large, real cost to neutral_wer**: 48.79%
  for Arm D vs. 27.14% for Arm C — nearly double. `overall_wer` likewise degrades from 28.01% to
  45.68%. Stacking the base-model-tuned biasing cell onto the fine-tuned checkpoint is not a free
  lunch: it substantially increases the boosting tree's over-triggering rate on non-brand speech,
  once the checkpoint already recognizes brand terms fairly well on its own.
* The over-triggering shows up as concrete brand-hallucination failures on neutral clips
  (`brand: null`) where the reference contains a similar-sounding but different term. For example,
  clip `sess_1c09809077b64d6c_user_vad_speech_000` has `ref: "My Brain Commerce page"` but
  `hyp: "Rezolve brainpowa page."` (wer 0.75), and clip
  `user_vad_speech_sess_ce0e8c43052d4c69_item_dea8c542adf24801` has
  `ref: "The main three reasons why I should buy Brain Cortex right now."` but
  `hyp: "Brain Power Rezolve Rezolve Rezolve Ai should buy brainpowa."` (wer 0.83) — the boosting
  tree is pulling "Rezolve"/"brainpowa" into hypotheses whose references say "Brain Commerce" or
  "Brain Cortex" instead.
* `brainpowa`-specific accuracy is identical between Arm C and Arm D (33.33%, i.e. 1/3 correct) —
  biasing neither helps nor hurts brainpowa recognition once fine-tuned, consistent with n=3 being
  too small to resolve any effect (per this task's rejection criteria, this is anecdotal only).

## Summary

This predictions asset is Arm D of the t0026 2x2 ablation: `parakeet-unified-v5` (the fine-tuned
checkpoint from `t0024_parakeet_unified_checkpoint_archive`) decoded with `malsd_batch` and a GPU-PB
boosting tree (`context_score=3.0, depth_scaling=0.5, alpha=1.5`) stacked on top, evaluated on all
91 clips of the `clean_eval_v2` holdout (43 brand, 48 neutral). It represents the previously unrun
cell combining a working fine-tuned checkpoint with working `malsd_batch` boosting.

The headline finding is a mixed one: Arm D achieves the highest brand_exact_rate of any arm tested
(83.72% overall, 87.50% Rezolve), edging out Arm C's fine-tuning-only 79.07%, but this edge is not
statistically significant (McNemar `c_vs_d` p=0.625 on only 4 discordant clips). Meanwhile Arm D's
neutral_wer (48.79%) is nearly double Arm C's (27.14%), driven by concrete brand-hallucination
failures where neutral references like "Brain Commerce" or "Brain Cortex" are mis-recognized as
"brainpowa" or "Rezolve" because the boosting tree — tuned for the base model — over-triggers once
stacked on a checkpoint that already handles brand terms reasonably well unaided.

For this project, the practical implication is that the base-model-tuned biasing cell should not be
assumed to transfer for free onto the fine-tuned checkpoint: it costs real general-WER accuracy for
a brand-accuracy gain that does not clear statistical significance at this sample size. A dedicated
re-sweep of the boosting parameters against the fine-tuned checkpoint (rather than reusing the
base-model Pareto cell) is the natural next step if this combination is to be pursued further.
