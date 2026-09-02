---
spec_version: "2"
predictions_id: "parakeet-unified-base-bias-clean-eval-v2"
documented_by_task: "t0026_biasing_on_finetune_ablation"
date_documented: "2026-09-02"
---
# parakeet-unified base model + GPU-PB biasing on clean_eval_v2

## Metadata

* **Name**: parakeet-unified base model + GPU-PB biasing on clean_eval_v2
* **Model**: nvidia/parakeet-unified-en-0.6b (HuggingFace pretrained, no fine-tuning)
* **Datasets**: clean_eval_v2 (no registered `dataset` asset — see `## Data`)
* **Format**: jsonl
* **Instances**: 91
* **Created by**: t0026_biasing_on_finetune_ablation

## Overview

These predictions are Arm B of the 2x2 ablation run by `t0026_biasing_on_finetune_ablation`, which
crosses GPU-PB context biasing against `parakeet-unified` fine-tuning on the 91-clip `clean_eval_v2`
holdout. Arm B isolates the effect of context biasing alone: it runs the unmodified HuggingFace
pretrained checkpoint with `malsd_batch` decoding plus a GPU-PB boosting tree seeded with the brand
key phrases, and no domain fine-tuning. It exists specifically to answer whether biasing recovers
brand-entity accuracy on a model that has never seen Rezolve-domain audio, and to serve as the
biasing-only reference point against which Arm D (fine-tuning + biasing) is judged to determine
whether the two techniques are complementary or redundant.

The four arms in this ablation (A: base/no-bias, B: base/bias, C: fine-tuned/no-bias, D:
fine-tuned/bias) share one manifest, one scoring function, and one GPU session, so metrics are
directly comparable across arms without confounds from decoder-strategy or hardware differences.
This asset captures only Arm B's per-clip output.

## Model

The model is `nvidia/parakeet-unified-en-0.6b`, loaded directly from HuggingFace with no additional
training — it is not a project model asset, hence `model_id` is `null` here (there is no local
checkpoint file to register; the weights are pulled from the public HuggingFace hub at run time and
are not otherwise tracked in this project). Decoding uses the `malsd_batch` strategy with
`beam.beam_size=4`, matching every other arm in the ablation so that decoder strategy is never a
confound (REQ-2 of `plan/plan.md`).

On top of that shared decoding config, Arm B attaches a GPU-PB boosting tree via
`code/boosting.py::apply_malsd_boost`, configured with `context_score=3.0`, `depth_scaling=0.5`, and
`beam.boosting_tree_alpha=1.5`. This is the single Pareto-frontier cell selected by the prior task
`t0024_biasing_pareto_and_ft_biasing_ablation` (recorded in that task's
`results/pareto_unified.json`, where it scored 60.0% `brand_exact_rate` at 8.7% `neutral_wer` on a
different sweep set) — it was not re-swept here, only re-validated on the `clean_eval_v2` holdout.
The boosting tree's `key_phrases_list` is populated with the brand terms this project tracks
(Rezolve and brainpowa variants).

## Data

The evaluation set is `clean_eval_v2`, a 91-clip decontaminated holdout produced by
`t0021_parakeet_finetune_vs_biasing` specifically because the original `gold-92` benchmark was found
to be contaminated for fine-tuning-related tasks (see `t0025`). It contains 43 brand-containing
clips (40 Rezolve + 3 brainpowa) and 48 neutral clips with no brand mention. Clips come from two
sources tagged in the `source` field: `clean_eval_21` (curated brand-focused turns) and
`quepasa_prod` (production session audio, mostly neutral).

`clean_eval_v2` has **no registered `dataset` asset** in this project, so `dataset_ids` is `[]`
above. The raw manifest and audio live at
`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/` (git-tracked manifest, DVC-tracked
audio) — that path is the canonical reference until a `dataset` asset is created for it. This task
additionally produced a path-corrected copy of the manifest
(`tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl`, gitignored,
machine-specific) purely to resolve audio file paths on the GPU host; it introduces no content
changes to the clips or references.

## Prediction Format

Each line of `predictions-clean-eval-v2.jsonl` is a JSON object, for example:

```json
{"clip_id": "1e1de7a1-11e0-4705-b923-ff0e6af87cde_turn4", "ref": "What is Rezolve Ai?", "hyp": "What is rezolve AI?", "brand": "Rezolve", "label": "PHONETIC", "wer": 0.0, "latency_seconds": 0.0239, "source": "clean_eval_21"}
```

Fields:

* `clip_id` — unique identifier for the audio clip
* `ref` — ground-truth reference transcript
* `hyp` — the model's decoded hypothesis text
* `brand` — `"Rezolve"`, `"brainpowa"`, or `null` for the 48 neutral (non-brand) clips
* `label` — brand-match category for brand clips: `"EXACT"` (verbatim match), `"PHONETIC"`
  (recognizable near-homophone, e.g. "rezolve" for "Rezolve"), or `"GARBAGE"` (unrecognizable or
  missing); `null` for neutral clips
* `wer` — per-clip word error rate between `ref` and `hyp`
* `latency_seconds` — per-clip inference latency in seconds
* `source` — provenance tag, `"quepasa_prod"` or `"clean_eval_21"`

Two representative rows: clip `1e1de7a1-...` (ref "What is Rezolve Ai?") is decoded as "What is
rezolve AI?" — labeled `PHONETIC` because "rezolve" is recognizable but lowercase/uncapitalized, at
`wer=0.0` since word-level tokens still match. Clip `a51ce143-...` (ref containing "...working on
AI-driven solutions for commerce and retail. As a full-time employee, you'll be part of our team at
brainpowa...") collapses to the single word "fulfillment" — labeled `GARBAGE` at `wer=1.0`, showing
that even with biasing active, long or acoustically difficult brainpowa-context clips can still fail
completely.

## Metrics

From `tasks/t0026_biasing_on_finetune_ablation/results/ablation_metrics.json`, key `"B"`:

| Metric | Value |
| --- | --- |
| `brand_exact_rate` (overall) | **37.21%** (16/43) |
| `brand_exact_rate` (Rezolve only) | **37.5%** (15/40) |
| `brand_exact_rate` (brainpowa only) | **33.33%** (1/3, n=3 — anecdotal) |
| `neutral_wer` | **12.68%** |
| `overall_wer` | **25.63%** |
| Avg. inference time / item | **0.0239 s** |
| Clips scored | 91/91 (91 brand + neutral clips; 43 brand, 48 neutral) |

For comparison, Arm A (base model, no bias, same 91 clips) scores `brand_exact_rate.overall = 0.0%`
and `neutral_wer = 8.12%` (from the same `ablation_metrics.json`, key `"A"`).

## Main Ideas

* This is the **bias-only, no-fine-tune** arm: biasing lifts `brand_exact_rate` from Arm A's
  **0.0%** floor to **37.21%** on a model that has never seen Rezolve-domain training audio,
  confirming GPU-PB context biasing works as a pure inference-time intervention independent of
  fine-tuning.
* That gain is not free: `neutral_wer` rises from Arm A's **8.12%** to **12.68%** (+4.56 points) on
  the 48 non-brand clips, because the boosting tree's key phrases occasionally get inserted into
  neutral audio that only phonetically resembles a brand term (e.g. "Brain Commerce" queries in the
  `quepasa_prod` source decoding toward brain-power-like text) — the classic biasing-precision
  tradeoff.
* Arm B's 37.21% is well below Arm C (fine-tuned, no bias, 79.07%) and Arm D (fine-tuned + bias,
  83.72%) from the same `ablation_metrics.json`, showing that on this holdout, domain fine-tuning
  alone recovers far more brand accuracy than inference-time biasing alone — biasing is a
  complementary lever, not a substitute for fine-tuning.
* `PHONETIC` labels (e.g. "rezolve" instead of "Rezolve") dominate the correct-ish failures in this
  arm, suggesting biasing nudges the decoder toward the right acoustic region without fully
  correcting capitalization/normalization — a partial win that still requires downstream text
  normalization to count as a true entity match in a real voice-commerce pipeline.

## Summary

This predictions asset holds the 91 per-clip outputs of Arm B in the
`t0026_biasing_on_finetune_ablation` 2x2 ablation: the pretrained `nvidia/parakeet-unified-en-0.6b`
base model, decoded with `malsd_batch` and a GPU-PB context-biasing tree at the previously-selected
Pareto cell (`context_score=3.0, depth_scaling=0.5, alpha=1.5`), evaluated on the 91-clip
`clean_eval_v2` holdout (43 brand clips, 48 neutral). No fine-tuning was applied to the model in
this arm — it exists to isolate what biasing alone contributes.

The headline finding is that biasing alone raises brand-entity accuracy substantially over the
unbiased base model (0.0% -> 37.21% `brand_exact_rate`) but at a real cost to general transcription
quality on neutral speech (`neutral_wer` 8.12% -> 12.68%), and that this bias-only result is far
below what fine-tuning achieves on its own (Arm C: 79.07%) or fine-tuning plus biasing together (Arm
D: 83.72%). For this project's decision of whether biasing is complementary to or redundant with
fine-tuning, Arm B establishes the biasing-only floor: the incremental value of adding biasing on
top of an already fine-tuned model (Arm D vs. Arm C) is the number that actually answers that
question, and this asset provides the reference point needed to interpret that comparison correctly.
