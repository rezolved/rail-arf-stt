---
spec_version: "2"
predictions_id: "parakeet-unified-ft-nobias-clean-eval-v2"
documented_by_task: "t0026_biasing_on_finetune_ablation"
date_documented: "2026-09-02"
---
# parakeet-unified-v5 (fine-tuned, no bias) on clean_eval_v2

## Metadata

- **Name**: parakeet-unified-v5 (fine-tuned, no bias) on clean_eval_v2
- **Model**: parakeet-unified-v5 (nvidia/parakeet-unified-en-0.6b fine-tuned on Rezolve domain
  audio, encoder frozen)
- **Datasets**: none registered — raw path
  `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/`
- **Format**: jsonl
- **Instances**: 91
- **Created by**: t0026_biasing_on_finetune_ablation

## Overview

These predictions are Arm C of the `t0026` 2x2 ablation that crosses GPU-PB context biasing against
`parakeet-unified` fine-tuning on the 91-clip `clean_eval_v2` holdout. Arm C runs the fine-tuned
`parakeet-unified-v5` checkpoint with `malsd_batch` decoding and no boosting tree, so it isolates
the effect of domain fine-tuning alone, with no context-biasing contribution.

This completes Part B of `t0024_biasing_pareto_and_ft_biasing_ablation`, which was deferred
(suggestion `S-0024-01`) because the fine-tuned checkpoint could not be found on any reachable
machine at the time. Both blockers are now resolved: the checkpoint is archived as DVC model asset
`parakeet-unified-v5` (`t0024_parakeet_unified_checkpoint_archive`), and a decontaminated 91-clip
holdout, `clean_eval_v2`, exists from `t0021_parakeet_finetune_vs_biasing`.

The four arms (A base/no-bias, B base/biased, C fine-tuned/no-bias, D fine-tuned/biased) all run on
the identical 91 clips with one shared scoring function, so this arm's numbers are directly
comparable to the other three. The project question this arm helps answer: does GPU-PB biasing still
add brand accuracy once the model is already fine-tuned on Rezolve domain audio, or do the two
techniques recover the same errors?

## Model

The model is `parakeet-unified-v5`, the DVC-archived NeMo checkpoint from
`tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/`. It is
`nvidia/parakeet-unified-en-0.6b` — a FastConformer-Hybrid Transducer-CTC architecture,
English-only, 0.6B parameters — fine-tuned on 422 Rezolve domain clips (353 TTS-synthesized + 69
real production clips), with the encoder frozen and only the RNNT decoder and CTC head updated.
Training used AdamW, learning rate 1e-4, batch size 16, up to 50 epochs with no early stopping; the
best epoch by validation WER was epoch 35 (`best_val_wer` 0.0556). On its own held-out 19-clip
gold-92 test split (4 brand clips), the checkpoint reached `test_wer` 0.0462 and `test_ea_dv` 1.0,
though on the 3-clip `brainpowa_clean21` slice it scored 0/3 correct.

For this arm, the checkpoint is loaded with
`nemo.collections.asr.models.ASRModel.restore_from(checkpoint_path)` and
`boosting.apply_malsd_no_boost(model)` is applied — `malsd_batch` decoding with no context-biasing
phrase tree attached. This matches Arm A's decoding path exactly except for the fine-tuned weights,
so any metric delta between A and C is attributable to fine-tuning alone.

## Data

The evaluation set is `clean_eval_v2`, a 91-clip decontaminated holdout: 43 brand-containing clips
(40 Rezolve + 3 brainpowa) and 48 neutral clips, drawn from a mix of `quepasa_prod` (real production
sessions) and `clean_eval_21` sources. There is no registered `dataset` asset for `clean_eval_v2`;
the raw manifest and audio live at `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/`
(`manifest.jsonl` + `audio/`, DVC-tracked). `t0026` fixed the manifest's absolute macOS
`audio_filepath` values to resolve on the GPU machine (`data/clean_eval_v2_manifest_fixed.jsonl`,
gitignored, machine-specific) without modifying `t0021`'s files. All four ablation arms consume this
same fixed manifest and the same loaded audio.

## Prediction Format

Each line of `predictions-clean-eval-v2.jsonl` is a JSON object with the following fields:

- `clip_id` (string) — unique clip identifier
- `ref` (string) — ground-truth reference transcript
- `hyp` (string) — model hypothesis transcript (empty string on decode failure)
- `brand` (string `"Rezolve"`, string `"brainpowa"`, or `null`) — brand mentioned in `ref`, or
  `null` for neutral clips
- `label` (string `"EXACT"`, `"PHONETIC"`, `"GARBAGE"`, or `null`) — how well the brand term was
  recognized in `hyp`; `null` for non-brand clips
- `wer` (float or `null`) — word error rate for this clip against `ref`; `null` if the clip couldn't
  be decoded
- `latency_seconds` (float) — average per-item inference time for this arm's single batched
  `transcribe()` call, stamped identically on every record in the arm (not a true per-clip
  measurement)
- `source` (string `"quepasa_prod"` or `"clean_eval_21"`) — which sub-source of `clean_eval_v2` the
  clip came from

Example rows:

```json
{"clip_id": "daf24b29-a43c-4ed2-878d-48790bfd9a9c_turn1", "ref": "How does Rezolve compare to Algolia?", "hyp": "Rezolve compared to Algola.", "brand": "Rezolve", "label": "EXACT", "wer": 0.6666666666666666, "latency_seconds": 0.0219, "source": "clean_eval_21"}
{"clip_id": "c484ffde-0ad6-4ead-9c41-9ae62d66d88d_turn2", "ref": "I'm looking for information about brainpowa.", "hyp": "", "brand": "brainpowa", "label": "GARBAGE", "wer": 1.0, "latency_seconds": 0.0219, "source": "clean_eval_21"}
```

The first row shows the brand token surviving intact ("Rezolve") even though the rest of the
utterance is garbled — an `EXACT` label only requires the brand span itself to match, not the full
sentence. The second row is a full decode failure (empty hypothesis) on a `brainpowa` clip, labeled
`GARBAGE`.

## Metrics

From `tasks/t0026_biasing_on_finetune_ablation/results/ablation_metrics.json`, key `"C"`:

| Metric | Value |
| --- | --- |
| `brand_exact_rate` (overall) | **79.07%** (34/43) |
| `brand_exact_rate` (Rezolve) | **82.5%** (33/40) |
| `brand_exact_rate` (brainpowa) | 33.3% (1/3) |
| `neutral_wer` | **27.14%** |
| `overall_wer` | 28.01% |
| `avg_inference_time_per_item_seconds` | 0.0219 s |
| `n_clips` / `n_brand_clips` / `n_neutral_clips` | 91 / 43 / 48 |
| `successful_requests` / `total_requests` | 91 / 91 |

For context, the other three arms from the same `ablation_metrics.json` run:

| Arm | brand_exact_rate (overall) | neutral_wer |
| --- | --- | --- |
| A — base, no bias | 0.0% | 8.12% |
| B — base + GPU-PB bias | 37.21% | 12.68% |
| **C — fine-tuned, no bias (this asset)** | **79.07%** | **27.14%** |
| D — fine-tuned + GPU-PB bias | 83.72% | 48.79% |

## Main Ideas

* Fine-tuning alone lifts `brand_exact_rate` from arm A's **0.0% floor to 79.07%** — the single
  largest jump in the 2x2 grid, confirming that domain fine-tuning is the dominant lever for brand
  recognition, well ahead of biasing alone (arm B's 37.21%).
* That gain is not free: `neutral_wer` rises from arm A's 8.12% to **27.14%** here (arm B stays much
  closer to baseline at 12.68%), meaning fine-tuning trades general transcription quality on
  non-brand speech for brand accuracy — a real regression risk if this checkpoint were deployed
  without also addressing neutral-utterance WER.
* The `brainpowa` breakdown (33.3%, 1/3 clips) is not resolvable from n=3 and should be treated as
  anecdotal only, consistent with the checkpoint's own test-split result of 0/3 on
  `brainpowa_clean21` — the fine-tune's brainpowa coverage is a genuine open question, not settled
  by either measurement.
* Comparing to arm D (fine-tuned + bias, 83.72% brand / 48.79% neutral WER) shows biasing on top of
  fine-tuning buys only a further +4.65 points of brand accuracy while nearly doubling the neutral
  WER cost relative to this arm — the two levers are not simply additive in their neutral-WER
  tradeoff, which is central evidence for the task's redundant-vs-complementary question.

## Summary

This predictions asset holds the 91 per-clip outputs of Arm C in the `t0026` 2x2 ablation: the
fine-tuned `parakeet-unified-v5` checkpoint (`nvidia/parakeet-unified-en-0.6b`, encoder frozen, best
epoch 35 by validation WER) decoded with `malsd_batch` and no GPU-PB boosting tree, run on the
91-clip `clean_eval_v2` holdout (43 brand clips: 40 Rezolve + 3 brainpowa; 48 neutral clips). It
isolates the effect of domain fine-tuning by itself, with the biasing variable held at "off."

The headline result is a large brand-accuracy gain from fine-tuning alone — `brand_exact_rate`
overall rises from arm A's 0.0% to **79.07%** (Rezolve-only: 82.5%) — but at a real cost to general
transcription quality: `neutral_wer` rises from arm A's 8.12% to **27.14%**, more than three times
the neutral-WER cost that biasing alone (arm B, 12.68%) incurs for a smaller brand-accuracy gain
(37.21%). `overall_wer` for this arm is 28.01%, and average inference time (0.0219 s/item) is
essentially unchanged from the base model's 0.0245 s/item.

Against the other arms, this asset shows fine-tuning is a much stronger single lever for brand
accuracy than biasing, but it is also the arm most responsible for the neutral-WER cost that
compounds further when biasing is added on top (arm D: 48.79% neutral WER). This tension between
brand accuracy and neutral-speech WER is the key tradeoff the task's answer asset needs to resolve
when judging whether biasing is complementary to, or redundant with, fine-tuning.
