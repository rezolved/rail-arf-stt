# t0023 — Validation: Current Prod vs Recommended Config

**Eval:** all 93 gold-92 clips (35 brand, 58 neutral) | Azure H100 | 2026-07-08

## Summary

| Metric | Current prod | Recommended | Delta |
|--------|-------------|-------------|-------|
| Brand EXACT (35 clips) | 0/35 (0%) | 20/35 (57%) | **+57.1%** |
| Brand PHONETIC | 30/35 | 13/35 | — |
| Brand GARBAGE | 5/35 | 2/35 | — |
| Brand WER | 20.3% | 10.8% | -9.5% |
| Neutral WER (58 clips) | 14.5% | 11.6% | -2.9% |
| Overall WER (93 clips) | 16.7% | 11.3% | -5.4% |

## Config

| | Baseline | Recommended |
|---|---|---|
| Model | parakeet-tdt-0.6b-v3 | parakeet-unified-en-0.6b |
| Strategy | greedy_batch | malsd_batch |
| context_score | 1.0 | 3.0 |
| depth_scaling | 2.0 | 0.5 |
| alpha | 1.0 | 1.5 |

## Verdict

**SHIP IT — large brand gain, neutral WER acceptable**

- Brand EXACT: 0% → 57% (+57.1%)
- Neutral WER: 14.5% → 11.6% (-2.9%)
- Overall WER: 16.7% → 11.3% (-5.4%)
