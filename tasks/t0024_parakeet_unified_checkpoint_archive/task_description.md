# Task t0024 — parakeet-unified-v5 checkpoint — DVC archive

## Goal

Register the best `parakeet-unified-en-0.6b` fine-tune checkpoint (v5-retrain, epoch 35) as a model
asset in `rail-arf-stt` with DVC tracking, so it can be reproduced from any machine with `dvc pull`.

## Background

The v5-retrain checkpoint is the current best fine-tuned model for Rezolve domain speech
recognition: WER 4.62%, EA-DV 100% on the gold-92 test split (19 clean clips, 4 unseen accents). It
was produced in `rail-benchmarks` and is stored only on local disk at
`rail-benchmarks/parakeet-finetune-v3/v5-retrain/parakeet-unified-finetuned-best.nemo` (~2.3 GB). It
is not tracked in any DVC store — if the local machine is lost, the checkpoint is gone.

This task does **not** retrain any model — it is purely infrastructure (copy, `dvc add`, register
asset metadata, `dvc push`).

Earlier checkpoints (v3, v4-stage2) are not archived — they are superseded by v5 and not needed for
downstream work.

## Steps

1. Create the model asset folder:
   `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/`
2. Copy `rail-benchmarks/parakeet-finetune-v3/v5-retrain/parakeet-unified-finetuned-best.nemo` into
   `files/`.
3. Run
   `dvc add tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/`.
4. Write `details.json` and `description.md` for the asset.
5. Run `dvc push` — uploads ~2.3 GB to `azure://ml-dvc-datasets/datasets/rail-arf-stt`.
6. Commit `.dvc` pointer files and asset metadata to git. Never commit the `.nemo` bytes.

## Model Asset

### parakeet-unified-v5

- `model_id`: `parakeet-unified-v5`
- Base: `nvidia/parakeet-unified-en-0.6b` (Hybrid Transducer-CTC, English-only)
- Trained externally in `rail-benchmarks/parakeet-finetune-v3/`; `training_task_id: "external"`
- Epoch 35/50, val_wer 0.056 (TTS val set — too easy, not a reliable signal)
- Train data: TTS 353 clips + gold-92 train split 69 clips; encoder frozen throughout
- WER 4.62%, EA-DV 100% on 19-clip clean gold-92 test split (4 unseen accents)
- brainpowa: 0/3 correct on clean-21 — known gap

## Expected Assets

One model asset: `parakeet-unified-v5` with the `.nemo` file DVC-tracked.

## Compute

No GPU needed. Local upload only. Estimated time: 30–60 min depending on upload speed.

## Dependencies

No dependencies. File is already on local disk.

## Pitfalls

1. `.nemo` file must never be committed to git — only the `.dvc` pointer file.
2. Verify `dvc push` succeeded before opening the PR.
3. `training_task_id` in `details.json` = `"external"` — trained outside `rail-arf-stt`.
