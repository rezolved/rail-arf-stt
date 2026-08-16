# Task t0025 — parakeet-tdt-0.6b-v3 brand-aware fine-tune

## Goal

Fine-tune `nvidia/parakeet-tdt-0.6b-v3` on Rezolve domain audio so that brand-critical terms
("Rezolve", "brainpowa", and related product names) are recognised correctly by the acoustic model
itself, reducing dependence on runtime GPU-PB phrase boosting (TurboBias) alone.

Primary metric: **EA-DV** on the clean-21 held-out set and on gold-92. Secondary: WER, intent
preservation, training efficiency.

## Background

Previous domain adaptation work targeted `parakeet-unified-en-0.6b` (a Hybrid Transducer-CTC model).
This task shifts to `parakeet-tdt-0.6b-v3` (pure TDT, 25-language), which is the model currently in
production in `brainpowa-realtime-api`.

Key findings from prior tasks that motivate this task:

- **t0021**: finetune of `parakeet-unified-en-0.6b` achieved EA-DV 38% on clean-21 vs 0% for biasing
  alone. Biasing has near-zero ceiling on unseen clips for "Rezolve"/"brainpowa".
- **t0023**: `parakeet-tdt-0.6b-v3` with `malsd_batch` beam + GPU-PB biasing achieved Brand EXACT
  57% and WER 11.3% on gold-92. Biasing alone cannot close the gap to >80% brand recall.
- **Parakeet v5 finetune** (t0024, parakeet-unified): WER 4.62%, EA-DV 100% on gold-92 test split,
  but brainpowa = 0/3 correct on clean-21. Encoder was frozen — acoustic confusion between
  "Rezolve"/"resolve" not addressed at encoder level.
- **Architecture difference**: `parakeet-tdt-0.6b-v3` is pure TDT (no CTC head); NeMo finetune
  configs from the unified model are not compatible. Requires TDT-specific
  `speech_to_text_finetune.yaml` and NeMo ≥ 2.4.

## Runs

| Run | Encoder | Data | Purpose |
| --- | --- | --- | --- |
| A — frozen-encoder baseline | Frozen | train_v5 + 3× brand oversample | Reproduce v5 approach on TDT architecture; establish baseline |
| B — partial-unfreeze | Top 4 FastConformer layers unfrozen, lr_mult=0.1 | Same as Run A | Test whether encoder unfreezing improves acoustic separation of homophones |

Both runs use the same manifest splits. gold-92 is **never** in the train or val split.

## Data

### Training manifest

Base: `rail-benchmarks/parakeet-finetune-v3/parakeet_finetune/manifests/train_v5.jsonl` (422 clips:
353 TTS + 69 real prod clips).

Apply brand-word oversampling: clips whose transcript contains "Rezolve", "brainpowa", or "Rezolve
AI" are duplicated 3× in the manifest (data-side, no loss weighting). Produces `data/train_v6.jsonl`
(~598 clips after oversampling 176 brand clips).

Do **not** add gold-92 clips beyond the 69 already in the v5 train split.

### Validation manifest

Produce `data/val_v6.jsonl`: take `val_v5.jsonl` (7 clips, Russian_OlyaShtalberg) and add 5–10
production clips containing brand words from the clean-21 set, so early-stopping signal is
brand-sensitive. These val clips must never be in the train manifest.

### Held-out test sets (never in train or val)

- `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/` — 21 production clips (primary)
- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/` — gold-92 regression set

### Transcript normalisation

`parakeet-tdt-0.6b-v3` was trained on **unnormalized** text (raw punctuation, casing, numbers as
digits). Spot-check 10 entries from `train_v5.jsonl` before reuse — if normalized, re-transcribe
from source audio.

### Manifest path fix

All paths in `train_v5.jsonl` are absolute Azure VM paths (`/home/azureuser/...`). The manifest
preparation script must remap them to actual paths on the new VM before training.

## Training Protocol

### NeMo config (TDT-specific)

```yaml
model:
  train_ds:
    manifest_filepath: tasks/t0025_parakeet_tdt_brand_finetune/data/train_v6.jsonl
    batch_size: 16
    shuffle: true
  validation_ds:
    manifest_filepath: tasks/t0025_parakeet_tdt_brand_finetune/data/val_v6.jsonl
    batch_size: 16
  init_from_pretrained_model: "nvidia/parakeet-tdt-0.6b-v3"

trainer:
  max_epochs: 50
  # No early stopping — run all 50 epochs, select best checkpoint by val WER

optim:
  lr: 1.0e-4
  # Run B only: param_groups with lr_mult=0.1 on encoder layers 14-17 (top 4 of 18)
```

Use `speech_to_text_finetune.yaml` with `model_type: tdt`. Dry-run config loading before starting
full train to catch config mismatches early.

Log per-epoch: training loss, val WER. Select best checkpoint by val WER. Run all 50 epochs — do
**not** use early stopping.

### Brand-word oversampling

```python
BRAND_TERMS = ["Rezolve", "brainpowa", "Rezolve AI"]
OVERSAMPLE_FACTOR = 3

def should_oversample(transcript: str) -> bool:
    return any(term.lower() in transcript.lower() for term in BRAND_TERMS)
```

Duplicate matching entries `OVERSAMPLE_FACTOR - 1` extra times. Save as
`tasks/t0025_parakeet_tdt_brand_finetune/data/train_v6.jsonl`.

## Metrics

Compute for both runs on both test sets (clean-21 and gold-92), with BCa bootstrap 95% CI (n=1000):

- `entity_accuracy_domain_vocab` (EA-DV) — primary; brand terms "Rezolve", "brainpowa"
- `entity_accuracy_gold92` (EA)
- `wer_gold92` (WER)
- `intent_preservation_gold92`
- `efficiency_training_time_seconds` (per run)
- `efficiency_inference_time_per_item_seconds` (on gold-92)

Also report: brand EXACT match separately for "Rezolve" and "brainpowa" (as in t0023).

## Assets

### Model asset

Best checkpoint for Run B: `parakeet-tdt-0.6b-v3-brand-v1`. Track with DVC (`dvc add`). Also save
Run A best checkpoint for ablation (DVC-tracked, but not the primary model asset).

### Predictions assets

1. `predictions-clean21-run-a.jsonl` — Run A on clean-21
2. `predictions-clean21-run-b.jsonl` — Run B on clean-21
3. `predictions-gold92-run-b.jsonl` — Run B on gold-92 (regression check)

## Expected Output

### Tables

1. Run A vs Run B: EA-DV, WER, EA, intent, brand EXACT per term, training time
2. vs t0023 biasing baseline: EA-DV, brand EXACT
3. Epoch learning curve: val WER per epoch for Run B

### Charts

- `results/images/epoch_curve_run_b.png` — val WER vs epoch
- `results/images/brand_exact_comparison.png` — bar: t0023-biasing vs Run A vs Run B

All charts embedded in `results_detailed.md`.

### Key Questions

1. Does fine-tuning `parakeet-tdt-0.6b-v3` achieve EA-DV > 60% on clean-21 (vs 0% for biasing)?
2. Does encoder unfreezing (Run B) improve brand recognition vs frozen encoder (Run A)?
3. Does the fine-tuned model regress on general WER vs the base model on gold-92?
4. Does combining Run B with GPU-PB biasing at inference push brand EXACT above 80%?

## Compute

**GPU**: Azure H100 (80 GB). One H100 sufficient for both runs sequentially.

| Run | Estimated time | Estimated cost |
| --- | --- | --- |
| A — frozen encoder, 50 epochs | ~1.5 h | ~$21 |
| B — partial unfreeze, 50 epochs | ~2 h | ~$28 |
| Eval (both runs, both test sets) | ~0.5 h | ~$7 |
| **Total** | ~4 h | ~$56 |

Tear down the VM immediately after eval completes.

## Dependencies

No hard dependencies. Reuses existing manifests and data on disk:

- `rail-benchmarks/parakeet-finetune-v3/parakeet_finetune/manifests/train_v5.jsonl`
- `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/`
- `tasks/t0001_stt_benchmark/`

Prior tasks for context (not blocking): t0021, t0023, t0024.

## Pitfalls

1. **Wrong NeMo config**: use `speech_to_text_finetune.yaml` with `model_type: tdt`, not the unified
   model config. Verify with a dry-run before full training.
2. **Absolute path remapping**: `train_v5.jsonl` paths are `/home/azureuser/...` — remap to actual
   VM paths in the manifest preparation script.
3. **gold-92 leakage**: cross-check all train/val clip IDs against
   `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl`. Fail
   loudly on any overlap.
4. **brainpowa gap**: even after 3× oversampling, brainpowa in train_v5 = 37 TTS + 1 real clip. If
   Run B scores 0% on brainpowa clean-21, escalate: request real prod recordings or extract from
   `brainpowa-realtime-api` session logs.
5. **DVC push before PR**: checkpoint files are ~2.3 GB; always `dvc push` before opening the PR.
