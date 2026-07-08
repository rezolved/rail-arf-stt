# t0023 — TDT vs Unified: GPU-PB Biasing Comparison

**Eval set:** gold-92, 35 brand clips (Rezolve/brainpowa), 10 neutral clips
**Date:** 2026-07-08 | **Machine:** Azure H100 NVL

## Results

| Config | Model | Strategy | Brand EXACT | Neutral WER |
|--------|-------|----------|-------------|-------------|
| **Current prod** | parakeet-tdt-0.6b-v3 | greedy_batch cs=1/ds=2/α=1 | 0/35 (0%) | ~15% (baseline) |
| TDT no boost | parakeet-tdt-0.6b-v3 | greedy_batch (no boost) | 0/35 (0%) | ~15% |
| **TDT best sweep** | parakeet-tdt-0.6b-v3 | malsd_batch cs=3.0/ds=0.5/α=3.0 | 21/35 (60%) | 64.9% |
| **Unified best (t0022)** | parakeet-unified-en-0.6b | malsd_batch cs=2.5/ds=0.5/α=2.5 | 24/35 (69%) | 27.9% |

## Verdict

**Unified** wins on brand EXACT (TDT best: 60% vs Unified best: 69%).

## Recommendation for prod migration

Switch to `parakeet-unified-en-0.6b` with:
```
strategy      = malsd_batch
beam_size     = 4
context_score = 2.5
depth_scaling = 0.5
alpha         = 2.5
```

Improvement over current prod: 0% → 69% brand EXACT (+69% pp)
