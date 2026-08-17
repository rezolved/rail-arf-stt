"""Fine-tune nvidia/parakeet-tdt-0.6b-v3 on brand-word dataset (t0025).

Strategy:
  - Freeze FastConformer encoder — 429 clips, avoid catastrophic forgetting
  - Train TDT decoder + joint network only
  - Data: 76 real gold + 353 TTS train, 18 gold val, 47 test (held out)

Usage (on gpu-azure):
    cd /home/azureuser/rail-arf-stt
    source .venv/bin/activate   # or whichever venv has nemo_toolkit
    python tasks/t0025_parakeet_tdt_brand_finetune/code/finetune.py
    python tasks/t0025_parakeet_tdt_brand_finetune/code/finetune.py --no-freeze
    python tasks/t0025_parakeet_tdt_brand_finetune/code/finetune.py --epochs 30 --lr 3e-4

Requirements:
    pip install nemo_toolkit[asr]>=2.0
    # parakeet-tdt-0.6b-v3 -> EncDecTDTBPEModel
"""

from __future__ import annotations

import argparse
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = TASK_DIR / "data"
CKPT_DIR = Path("/mnt/finetune-checkpoints-t0025")
MODEL_NAME = "nvidia/parakeet-tdt-0.6b-v3"


def _ds_config(manifest: str, batch_size: int, shuffle: bool) -> dict:
    return {
        "manifest_filepath": manifest,
        "sample_rate": 16000,
        "batch_size": batch_size,
        "trim_silence": False,
        "max_duration": 30.0,
        "min_duration": 0.1,
        "shuffle": shuffle,
        "num_workers": 2,
        "pin_memory": True,
    }


def freeze_encoder(model) -> None:
    frozen = 0
    for _, param in model.encoder.named_parameters():
        param.requires_grad = False
        frozen += param.numel()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Encoder frozen  : {frozen / 1e6:.1f}M params")
    print(f"Trainable       : {trainable / 1e6:.1f}M params")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pretrained", type=Path, default=None, help="Resume from .nemo checkpoint"
    )
    parser.add_argument("--train", type=Path, default=DATA_DIR / "train" / "manifest.jsonl")
    parser.add_argument("--val", type=Path, default=DATA_DIR / "val" / "manifest.jsonl")
    parser.add_argument("--out-dir", type=Path, default=CKPT_DIR)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--no-freeze", action="store_true")
    parser.add_argument("--no-early-stop", action="store_true")
    args = parser.parse_args()

    for p in [args.train, args.val]:
        if not p.exists():
            raise FileNotFoundError(f"Missing manifest: {p}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    import lightning.pytorch as pl
    import nemo.collections.asr as nemo_asr

    if args.pretrained:
        print(f"Loading checkpoint: {args.pretrained}")
        model = nemo_asr.models.EncDecTDTBPEModel.restore_from(str(args.pretrained))
    else:
        print(f"Loading {MODEL_NAME} ...")
        model = nemo_asr.models.EncDecTDTBPEModel.from_pretrained(MODEL_NAME)

    if not args.no_freeze:
        freeze_encoder(model)
    else:
        total = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Encoder unfrozen. Trainable: {total / 1e6:.1f}M (overfit risk on 429 clips)")

    model.setup_training_data(_ds_config(str(args.train), args.batch_size, shuffle=True))
    model.setup_validation_data(_ds_config(str(args.val), args.batch_size, shuffle=False))

    lr = args.lr
    if args.pretrained:
        lr = min(lr, 1e-5)
    elif not args.no_freeze:
        lr = min(lr, 5e-4)

    model.setup_optimization(
        {
            "_target_": "torch.optim.AdamW",
            "lr": lr,
            "weight_decay": 1e-3,
            "betas": [0.9, 0.98],
        }
    )

    checkpoint_cb = pl.callbacks.ModelCheckpoint(
        dirpath=str(args.out_dir),
        filename="parakeet-tdt-{epoch:02d}-{val_wer:.4f}",
        monitor="val_wer",
        mode="min",
        save_top_k=3,
        save_last=True,
        verbose=True,
    )
    lr_monitor = pl.callbacks.LearningRateMonitor(logging_interval="epoch")
    callbacks = [checkpoint_cb, lr_monitor]

    if not args.no_early_stop:
        callbacks.append(
            pl.callbacks.EarlyStopping(
                monitor="val_wer",
                patience=10,
                mode="min",
                verbose=True,
            )
        )

    trainer = pl.Trainer(
        devices=1,
        accelerator="gpu",
        max_epochs=args.epochs,
        callbacks=callbacks,
        log_every_n_steps=1,
        check_val_every_n_epoch=1,
        gradient_clip_val=1.0,
        precision="bf16-mixed",
        default_root_dir=str(args.out_dir),
    )

    print(f"\nFine-tuning: {args.epochs} epochs | lr={lr} | batch={args.batch_size}")
    print(f"Train : {args.train}  ({sum(1 for _ in args.train.open())} clips)")
    print(f"Val   : {args.val}  ({sum(1 for _ in args.val.open())} clips)")
    print(f"Ckpts → {args.out_dir}\n")

    trainer.fit(model)

    best = checkpoint_cb.best_model_path
    print(f"\nBest checkpoint : {best}")
    nemo_path = args.out_dir / "parakeet-tdt-finetuned-best.nemo"
    model.save_to(str(nemo_path))
    print(f"Saved .nemo     : {nemo_path}")


if __name__ == "__main__":
    main()
