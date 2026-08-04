# Task t0021 — Parakeet fine-tune vs biasing — parakeet-unified on gold-92

## Goal

Determine whether fine-tuning `parakeet-unified-en-0.6b` on Rezolve domain audio outperforms runtime
TurboBias on the same model. Primary metric: **EA-DV**. Secondary: WER, EA, latency.

## Background

Two adaptation approaches exist for `parakeet-unified-en-0.6b`:

- **Biasing** (t0015): GPU-PB TurboBias with 31-term Rezolve domain vocabulary, alpha=1.0. EA-DV =
  34.78% on gold-92 (1000ms interval). Predictions already on disk at
  `tasks/t0015_streaming_buffer_interval/assets/predictions/parakeet-unified-buffer-sweep/files/predictions-gold92-1000ms.jsonl`.
- **Fine-tuning** (rail-benchmarks/realtime-voice-benchmark, parakeet_finetune task): encoder
  frozen, decoder fine-tuned on 557 Rezolve-domain clips (415 TTS + 204 speed-perturbed gold-92
  clips), early stop epoch 22, val_wer=0.0149. Checkpoint on gpu-azure:
  `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`.

The finetune task reported EA-DV 22% → 95% on a 102-clip eval. A direct comparison on gold-92 is
needed to confirm the gap.

## Runs

| Run | Adaptation | Source |
| --- | --- | --- |
| A | TurboBias, alpha=1.0 | Reuse t0015 `predictions-gold92-1000ms.jsonl` — **no new inference needed** |
| B | Fine-tuned, no biasing | Run on gpu-azure with `parakeet-unified-finetuned-best.nemo` |

## Metrics

Compute for both runs, BCa bootstrap 95% CI (n=1000):

- `wer`
- `ea`
- `ea_dv` (primary)
- `efficiency_inference_time_per_item_seconds` (run B only; run A latency from t0015)

## Expected Assets

- 1 prediction asset: `run_b_unified_finetuned` (run A reuses t0015 asset directly)
- 1 answer asset: comparison table, caveat on gold-92 overlap, production recommendation

## Compute

Run B on gpu-azure (H100, NeMo 3.1.0, checkpoint already present). Estimated wall-clock: <15 min.

## Key Questions

1. Does fine-tuning outperform biasing on EA-DV on gold-92?
2. Does fine-tuning hurt WER vs biasing baseline?
3. Given the train/test overlap caveat, is gold-92 EA-DV for run B reliable?

## Caveats

- Gold-92 train/test overlap: 204 gold-92 clips were speed-perturbed and used in fine-tuning. EA-DV
  for run B may be inflated. State this prominently in results.
- Fine-tune checkpoint lives outside this ARF project. Document checkpoint path and training config
  in the answer asset for reproducibility.
