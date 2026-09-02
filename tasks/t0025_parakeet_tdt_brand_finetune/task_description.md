# Task t0025 — parakeet-tdt-0.6b-v3 brand-aware fine-tune

## Goal

Fine-tune `nvidia/parakeet-tdt-0.6b-v3` on Rezolve domain audio so that brand-critical terms
("Rezolve", "brainpowa", and related product names) are recognised correctly by the acoustic model
itself, reducing dependence on runtime GPU-PB phrase boosting (TurboBias) alone.

Primary metric: **EA-DV** on the `clean_eval_v2` held-out set (91 clips). Secondary: WER, intent
preservation, training efficiency. gold-92 is **not** a valid held-out set for this task — see
"Held-out test sets" below.

## Background

Previous domain adaptation work targeted `parakeet-unified-en-0.6b` (a Hybrid Transducer-CTC model).
This task shifts to `parakeet-tdt-0.6b-v3` (pure TDT, 25-language), which is the model currently in
production in `brainpowa-realtime-api`.

Key findings from prior tasks that motivate this task:

- **t0021**: finetune of `parakeet-unified-en-0.6b` achieved EA-DV 38% on clean-21 vs 0% for biasing
  alone. Biasing has near-zero ceiling on unseen clips for "Rezolve"/"brainpowa".
- **t0023**: `parakeet-tdt-0.6b-v3` with `malsd_batch` beam + GPU-PB biasing achieved Brand EXACT
  57% and WER 11.3% on gold-92. Biasing alone cannot close the gap to >80% brand recall.
- **Parakeet v5 finetune** (t0024, parakeet-unified): WER 4.62%, EA-DV 100% on a gold-92 test split
  — treat that figure as inflated, since 60 of gold-92's 93 clips are inside `train_v5` — but
  brainpowa = 0/3 correct on clean-21. Encoder was frozen — acoustic confusion between
  "Rezolve"/"resolve" not addressed at encoder level.
- **Architecture difference**: `parakeet-tdt-0.6b-v3` is pure TDT (no CTC head); NeMo finetune
  configs from the unified model are not compatible. Requires TDT-specific
  `speech_to_text_finetune.yaml` and NeMo ≥ 2.4.

## Runs

| Run | Encoder | Data | Purpose |
| --- | --- | --- | --- |
| A — frozen-encoder baseline | Frozen | train_v5 + 3× brand oversample | Reproduce v5 approach on TDT architecture; establish baseline |
| B — partial-unfreeze | Top 4 FastConformer layers unfrozen, lr_mult=0.1 | Same as Run A | Test whether encoder unfreezing improves acoustic separation of homophones |

Both runs use the same manifest splits. Note that gold-92 **is** partly in the train split — 60 of
its 93 clips come along with `train_v5` — which is why `clean_eval_v2`, not gold-92, is this task's
held-out set. See "Held-out test sets" and Pitfall 3.

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
production clips containing brand words, so the checkpoint-selection signal is brand-sensitive.

**Do not source those clips from `clean_eval_v2` or from the old `clean_eval/` (clean-21) set** —
clean-21's clips are inside `clean_eval_v2`, so borrowing from either one contaminates the only
valid held-out set this task has. Draw them from quepasa production logs that are not in
`clean_eval_v2/manifest.jsonl`, or from the gold-92 clips already inside `train_v5` (those are
burned for eval purposes anyway, so reusing them for validation costs nothing). Verify the final
`val_v6.jsonl` against both `train_v6.jsonl` and `clean_eval_v2/manifest.jsonl` and fail loudly on
any overlap with either.

### Held-out test sets (never in train or val)

**Primary — `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/`, 91 clips.** This
supersedes the 21-clip `clean_eval/` set that earlier drafts of this task named. `clean_eval_v2` was
added by `t0021` (PR #23) and independently re-verified: zero overlap with `train_v5` by audio
filename, zero overlap with this task's `train`/`val` manifests, zero overlap with gold-92. Audio is
DVC-tracked (`audio.dvc`, 91 files) — `dvc pull` it before evaluating. This task's own
`data/test/manifest.jsonl` (47 clips) is a subset of `clean_eval_v2`; report on the full 91 so the
numbers are comparable with t0026 and any future checkpoint.

Composition: 43 clips carry a brand term — 40 `Rezolve` mentions, **only 3 `brainpowa`**. Report
`Rezolve` and `brainpowa` separately and treat any `brainpowa` delta as anecdotal, not a
measurement. This is the same power gap Pitfall 4 escalates.

**gold-92 is NOT a valid held-out set for this task.** `train_v5` contains **60 of gold-92's 93
clips** by exact `clip_id` — not speed-perturbed derivatives, the same recordings. Any EA-DV or WER
figure on the full gold-92 for a checkpoint trained on `train_v5` is inflated and must not be
reported as a regression result. This is exactly how `parakeet-unified-v5` came to claim EA-DV 100%
on gold-92.

The 33 uncontaminated gold-92 clips are not a usable substitute either, and the reason matters:
**all 33 are `source: clean_voices`**. Every one of the 34 `production` clips and all 13
`error_cases` clips sits inside `train_v5`. So the clean remainder contains no real production audio
and no error cases at all — precisely the two conditions this fine-tune is meant to improve — and
only 8 of the 33 carry a brand term. Do not compute brand accuracy on 8 clips.

If a gold-92 number is wanted for continuity with earlier tasks, compute it on the 33-clip
`clean_voices` remainder, label it explicitly as `gold92_clean_voices_n33`, and state in
`results_detailed.md` that it is a reference figure on studio-voice audio only, not a regression
gate.

### Transcript normalisation

`parakeet-tdt-0.6b-v3` was trained on **unnormalized** text (raw punctuation, casing, numbers as
digits). Spot-check 10 entries from `train_v5.jsonl` before reuse — if normalized, re-transcribe
from source audio.

### Manifest path fix

All paths in `train_v5.jsonl` are absolute Azure VM paths (`/home/azureuser/...`). The manifest
preparation script must remap them to actual paths on the new VM before training.

`clean_eval_v2/manifest.jsonl` has the same problem from the other direction — its `audio_filepath`
values are absolute paths from the annotator's laptop (`/Users/margotiamanova/Desktop/...`). Remap
them relative to the repo root before evaluating, and do not commit machine-specific paths back.

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

Compute for both runs on `clean_eval_v2` (91 clips), with BCa bootstrap 95% CI (n=1000):

- `entity_accuracy_domain_vocab` (EA-DV) — primary; brand terms "Rezolve", "brainpowa", reported
  both together and split per term
- WER over the 48 non-brand clips (the cost side of the tradeoff) and over all 91
- `efficiency_training_time_seconds` (per run)
- `efficiency_inference_time_per_item_seconds` (on `clean_eval_v2`)

Note that the registered gold-92 metrics (`entity_accuracy_gold92`, `wer_gold92`,
`intent_preservation_gold92`) are defined against gold-92 ground truth and therefore **cannot** be
reported for this task's checkpoints — 60 of the 93 clips are in `train_v5`. Compute the same
quantities on `clean_eval_v2` under task-local names, leave `results/metrics.json` empty if no
registered metric legitimately applies, and say so in the results rather than reporting a
contaminated number under a registered metric id.

Optional continuity figure: `gold92_clean_voices_n33` as described in "Held-out test sets" —
reference only, never a gate.

Also report: brand EXACT match separately for "Rezolve" and "brainpowa" (as in t0023).

## Assets

### Model asset

Best checkpoint for Run B: `parakeet-tdt-0.6b-v3-brand-v1`. Track with DVC (`dvc add`). Also save
Run A best checkpoint for ablation (DVC-tracked, but not the primary model asset).

### Predictions assets

1. `predictions-cleanevalv2-run-a.jsonl` — Run A on `clean_eval_v2`
2. `predictions-cleanevalv2-run-b.jsonl` — Run B on `clean_eval_v2`
3. `predictions-gold92-cleanvoices-run-b.jsonl` — Run B on the 33-clip uncontaminated gold-92
   remainder (reference only; the full gold-92 is contaminated for this checkpoint)

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

1. Does fine-tuning `parakeet-tdt-0.6b-v3` achieve EA-DV > 60% on `clean_eval_v2` (vs 0% for
   biasing)?
2. Does encoder unfreezing (Run B) improve brand recognition vs frozen encoder (Run A)? This is the
   central question — `parakeet-unified-v5` froze the encoder and left `brainpowa` at 0/3, and the
   `Rezolve`/`resolve` confusion is acoustic, so a frozen encoder cannot address it. No other task
   tests this.
3. Does the fine-tuned model regress on general WER vs the base model, measured on the 48 non-brand
   clips of `clean_eval_v2`? (Not on gold-92 — contaminated.)
4. Does combining Run B with GPU-PB biasing at inference push brand EXACT above 80%? Note this is
   the TDT-architecture counterpart of the question `t0026` answers for `parakeet-unified`; the two
   results are not interchangeable, but read t0026's verdict before designing this arm.

## Compute

**Machine: `LLM-T1-NC80`, GPU 0 — `CUDA_VISIBLE_DEVICES=0`.** Not a suggestion; pin it. This is the
only entry in `project/azure_vm.json` and the only box carrying the `stt` conda env with **NeMo
3.1.0** (well above this task's NeMo ≥ 2.4 requirement — nothing to install), the HF model cache
including `parakeet-tdt-0.6b-v3`, and `/mnt/finetune-checkpoints/`. Every successful GPU run in this
project happened here: t0014, t0015, t0017.

The box has 2xH100 NVL and 880 GB RAM, and `t0026` is pinned to `CUDA_VISIBLE_DEVICES=1` so the two
tasks cannot collide on the same device. Set the variable explicitly in every command; do not rely
on the default.

**This task may run concurrently with `t0026`.** `LLM-T1-NC80` declares `max_concurrent_tasks: 2`,
and `acquire` joins a `Running` VM that already carries an ARF lock rather than refusing it (PR
#25). In practice `t0026` starts first — it is ready now, while this task still needs its
`val_v6.jsonl` built — so this task will usually be the one joining an already-running box. When
that happens its acquire output reports `started_vm: false`, and **teardown must then be called with
`--joined-running-vm`**, or the shared VM window is billed twice in the project cost total.

Within this task, Run A and Run B still run **sequentially** on GPU 0, not side by side.

Never install or upgrade packages in the shared `stt` conda environment while `t0026` is running on
the other GPU — a version change under a live sibling job breaks it mid-run. Clone the environment
if this task needs different packages.

`FT-MC` was removed from the pool on 2026-08-26 after its single use (t0024) failed on a missing
`stt` env — $14.06, zero results. Do not reach for it.

Two operational rules that have already cost this project money:

* **Refresh the SSH HostName after every VM start** — Azure reassigns the public IP and the static
  alias goes stale, failing as `failure_phase="ssh_connect"`. See
  `docs/northeurope_pool_runbook.md`.
* **Write nothing durable to `/mnt`** — ephemeral local disk, wiped on stop/start. This is how the
  t0021 checkpoint was lost. Checkpoints go to the task folder and get `dvc push`ed before teardown.

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
- `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/` — DVC-tracked, `dvc pull` required

Prior tasks for context (not blocking): t0021, t0023, t0024.

## Pitfalls

1. **Wrong NeMo config**: use `speech_to_text_finetune.yaml` with `model_type: tdt`, not the unified
   model config. Verify with a dry-run before full training.
2. **Absolute path remapping**: `train_v5.jsonl` paths are `/home/azureuser/...` — remap to actual
   VM paths in the manifest preparation script.
3. **gold-92 leakage is already present and is accepted, not prevented.** Earlier drafts of this
   task said to cross-check train/val clip IDs against
   `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` and fail
   loudly on overlap — that contradicted the Data section, which deliberately keeps the gold-92
   clips already present in `train_v5`. The measured overlap is 60 of 93. The resolution is to keep
   the training data as is and **drop gold-92 as the eval set**, not to strip the training data.
   What must still fail loudly is overlap between train/val and `clean_eval_v2` — verify that before
   training, since `clean_eval_v2` is now the only real held-out set.
4. **brainpowa gap**: even after 3× oversampling, brainpowa in train_v5 = 37 TTS + 1 real clip. If
   Run B scores 0% on the 3 brainpowa clips in `clean_eval_v2`, escalate: 3 clips cannot settle the
   question either way, so the escalation is for more data, not a verdict. Request real prod
   recordings or extract from `brainpowa-realtime-api` session logs.
5. **DVC push before PR**: checkpoint files are ~2.3 GB; always `dvc push` before opening the PR.
