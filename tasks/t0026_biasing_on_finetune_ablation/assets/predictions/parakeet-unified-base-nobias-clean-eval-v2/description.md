---
spec_version: "2"
predictions_id: "parakeet-unified-base-nobias-clean-eval-v2"
documented_by_task: "t0026_biasing_on_finetune_ablation"
date_documented: "2026-09-02"
---
# parakeet-unified base, no bias, on clean_eval_v2

## Metadata

* **Name**: parakeet-unified base, no bias, on clean_eval_v2
* **Model**: nvidia/parakeet-unified-en-0.6b (HuggingFace pretrained, no fine-tuning, no local model
  asset)
* **Datasets**: none registered — see `## Data` below
* **Format**: jsonl
* **Instances**: 91
* **Created by**: t0026_biasing_on_finetune_ablation

## Overview

These predictions are Arm A of `t0026_biasing_on_finetune_ablation`'s 2x2 ablation of GPU-PB context
biasing crossed with `parakeet-unified` fine-tuning. Arm A is the "neither lever pulled" cell: the
unmodified `nvidia/parakeet-unified-en-0.6b` HuggingFace checkpoint, decoded with `malsd_batch` and
the boosting tree explicitly disabled (`apply_malsd_no_boost`), run once over the full 91-clip
`clean_eval_v2` holdout.

The task exists to answer whether GPU-PB context biasing still helps once a model has already been
fine-tuned on Rezolve domain audio, or whether the two techniques just recover the same errors —
completing Part B of `t0024_biasing_pareto_and_ft_biasing_ablation`, which was deferred because the
fine-tuned checkpoint and a decontaminated eval set were not both available at the time. Arm A's
role in that 2x2 design is to establish the floor: the brand-accuracy baseline with no fine-tuning
and no biasing, against which Arm B (bias only), Arm C (fine-tune only), and Arm D (both) are
compared. All four arms share one manifest, one scoring function, and one GPU session, so
differences between arms are attributable only to the model checkpoint and the presence of the
boosting tree.

## Model

The model is `nvidia/parakeet-unified-en-0.6b`, loaded via
`nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-unified-en-0.6b")` — the stock
HuggingFace pretrained checkpoint with no Rezolve-specific fine-tuning applied
(`code/run_ablation.py` `_load_model`, `ARM_USES_FINETUNED["A"] = False`). Decoding used
`malsd_batch` throughout the ablation (so decoder strategy is never confounded with the biasing
effect across arms), but for Arm A the boosting tree was left disabled via
`boosting.apply_malsd_no_boost(model)` (`ARM_USES_BOOST["A"] = False`) — no GPU-PB context phrases,
no `context_score`/`depth_scaling`/`alpha` weighting. `model_id` is `null` in `details.json` because
this is an unmodified upstream checkpoint pulled directly from HuggingFace at run time; no local
model asset was created for it (there is nothing Rezolve-specific to archive — the exact same
weights are one `from_pretrained()` call away for anyone re-running this).

## Data

The evaluation set is `clean_eval_v2`, a 91-clip decontaminated holdout produced by
`t0021_parakeet_finetune_vs_biasing` specifically to avoid the gold-92 contamination found for this
line of research: 43 brand-containing clips (40 mentioning "Rezolve", 3 mentioning "brainpowa") and
48 neutral clips, drawn from a mix of real quepasa production sessions (`source: "quepasa_prod"`)
and a curated set (`source: "clean_eval_21"`). `clean_eval_v2` has **no registered `dataset` asset**
in this project — `dataset_ids` is intentionally `[]`. The raw manifest and audio live at
`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/`; this task consumed a machine-local
copy of the manifest with `audio_filepath` values rewritten to resolve on the GPU host
(`tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl`, gitignored, per
REQ-4 of `plan/plan.md`), without modifying any of t0021's committed files. No other preprocessing
was applied to the audio beyond standard loading (`code/audio_io.py`).

Ground-truth brand detection (`scoring.brand_in_ref`) matches only `EXACT_PATTERNS` against the
reference text — the phonetic patterns used for scoring hypotheses are deliberately excluded here,
because on `clean_eval_v2` the `brainpowa` phonetic pattern (`\brain.?com`) collides with 11 clips
that mention "Brain Commerce," an unrelated real Rezolve product name. Restricting reference
matching to exact patterns reproduces the dataset's documented 43/48 brand/neutral split exactly
(see `code/scoring.py` docstring for the full rationale).

## Prediction Format

`files/predictions-clean-eval-v2.jsonl` has 91 lines, one JSON object per clip, with these fields:

* `clip_id` (string) — unique clip identifier, e.g. `"1e1de7a1-11e0-4705-b923-ff0e6af87cde_turn4"`
* `ref` (string) — ground-truth reference transcript
* `hyp` (string) — model hypothesis transcript; empty string if audio decode failed for that clip
  (none did in this run — see `## Metrics`)
* `brand` (string or null) — `"Rezolve"` or `"brainpowa"` if the reference contains that brand term
  (via `EXACT_PATTERNS`), else `null` for neutral clips
* `label` (string or null) — how the brand term appears in `hyp`: `"EXACT"` (correctly transcribed),
  `"PHONETIC"` (a near-homophone miss, e.g. "resolve" for "Rezolve"), or `"GARBAGE"` (transcribed as
  something unrelated, or dropped entirely); `null` when `brand` is `null`
* `wer` (float) — word error rate for this clip via Levenshtein edit distance over lowercased word
  tokens, 0.0 (perfect) upward
* `latency_seconds` (float) — the arm's average per-item inference time, stamped identically on
  every record in the arm; `run_ablation.py` batches `transcribe()` across the whole arm and divides
  one wall-clock elapsed time by clip count, so this is **not** a true per-clip latency measurement
  (see `code/run_ablation.py` comment above `avg_latency`)
* `source` (string) — `"quepasa_prod"` or `"clean_eval_21"`, the clip's provenance

Example rows (brand clips, both misfires typical of the unbiased base model):

```json
{"clip_id": "1e1de7a1-11e0-4705-b923-ff0e6af87cde_turn4", "ref": "What is Rezolve Ai?", "hyp": "What is resolve AI?", "brand": "Rezolve", "label": "PHONETIC", "wer": 0.25, "latency_seconds": 0.0245, "source": "clean_eval_21"}
{"clip_id": "c484ffde-0ad6-4ead-9c41-9ae62d66d88d_turn2", "ref": "I'm looking for information about brainpowa.", "hyp": "", "brand": "brainpowa", "label": "GARBAGE", "wer": 1.0, "latency_seconds": 0.0245, "source": "clean_eval_21"}
```

The first row shows the model's dominant failure mode on "Rezolve": a phonetically plausible but
wrong substitution ("resolve"). The second shows a `brainpowa` clip decoded as an empty string —
scored as `GARBAGE` with `wer=1.0`.

## Metrics

Computed by `code/run_ablation.py` `_aggregate_metrics` and stored under key `"A"` in
`results/ablation_metrics.json`:

| Metric | Value |
| --- | --- |
| `brand_exact_rate` (overall, n=43) | **0.0%** |
| `brand_exact_rate` (Rezolve, n=40) | **0.0%** |
| `brand_exact_rate` (brainpowa, n=3) | **0.0%** |
| `neutral_wer` (n=48) | **8.12%** |
| `overall_wer` (n=91) | **24.69%** |
| Avg inference time / item | **0.0245 s** |
| Successful / total requests | **91 / 91** |

Zero of the 43 brand clips were transcribed with an exact match on "Rezolve" or "brainpowa" — every
single one fell to `PHONETIC` or `GARBAGE`. `neutral_wer` (8.12%) is far lower than `overall_wer`
(24.69%), confirming the brand clips are the entire source of the model's elevated error rate:
non-brand speech is transcribed reasonably well by the base model.

## Main Ideas

* **This is the 2x2 design's floor.** With no fine-tuning and no context biasing, brand `EXACT`
  accuracy is exactly **0%** across all 43 brand clips (both Rezolve and brainpowa sub-splits). The
  base `parakeet-unified` model has no mechanism to recover Rezolve-specific proper nouns, and
  consistently mishears "Rezolve" as phonetic near-misses like "resolve," "result," or "visual" —
  see the example rows above.
* **The gap is brand-specific, not general ASR quality.** `neutral_wer` of 8.12% shows the base
  model handles ordinary speech acceptably; the 24.69% `overall_wer` is driven almost entirely by
  the 43 brand clips, where wrong brand words inflate WER even on clips that are otherwise
  transcribed correctly.
* **Arms B, C, and D are measured against this exact 0% floor.** Any brand accuracy gain reported
  for GPU-PB biasing alone (Arm B), fine-tuning alone (Arm C), or both together (Arm D) is a gain
  over a model that recovers no brand mentions whatsoever — there is no risk of this baseline
  flattering a weak intervention.
* **Inference is fast and uniform across arms** (~24.5 ms/item here), so any latency differences
  observed between arms in this ablation come from the boosting tree or checkpoint, not from noise
  in this baseline measurement.

## Summary

This predictions asset is Arm A of the `t0026_biasing_on_finetune_ablation` 2x2 ablation: the
unmodified `nvidia/parakeet-unified-en-0.6b` HuggingFace checkpoint, decoded with `malsd_batch` and
no GPU-PB boosting tree, run over the full 91-clip `clean_eval_v2` holdout (43 brand clips — 40
Rezolve, 3 brainpowa — and 48 neutral clips). All 91 requests succeeded; no clips failed to decode.

The headline result is a clean floor: **0% brand `EXACT` rate** across every brand sub-split, with
`neutral_wer` at 8.12% and `overall_wer` at 24.69%. The base model has no ability to correctly
transcribe "Rezolve" or "brainpowa" without either fine-tuning or context biasing — every brand
mention falls to a phonetic near-miss or garbage transcription, while ordinary speech is transcribed
reasonably well. This baseline anchors the comparison for Arms B (bias only), C (fine-tune only),
and D (both), letting the task's answer asset attribute any brand-accuracy improvement in those arms
unambiguously to the intervention being tested rather than to measurement noise in an already-strong
baseline.
