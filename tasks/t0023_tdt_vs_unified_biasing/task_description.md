# t0023 — TDT vs Unified: GPU-PB Biasing Comparison on gold-92

## Objective

Verify that `parakeet-unified-en-0.6b` with `malsd_batch` + optimal params
(cs=3.0, ds=0.5, alpha=1.5 from t0022) outperforms the current production model
`parakeet-tdt-0.6b-v3` with `greedy_batch` (current prod config) — and find the
best params for TDT too, so the comparison is fair (best vs best).

## Background

- **Current prod:** `parakeet-tdt-0.6b-v3`, `greedy_batch`, cs=1.0, ds=2.0, alpha=1.0
- **t0022 finding:** `greedy_batch` gives 0% brand EXACT; `malsd_batch` + cs=3.0/ds=0.5/alpha=1.5
  gives 60% brand EXACT on `parakeet-unified-en-0.6b`
- t0022 only tested unified model — TDT hasn't been swept yet
- We plan to migrate prod to unified, but need hard numbers for both

## What to run

1. **TDT sweep** — same malsd_batch param grid as t0022 on `parakeet-tdt-0.6b-v3`
2. **Unified re-run** — load t0022 sweep results (already done), no re-run needed
3. **Comparison table** — TDT best vs unified best, both vs current prod config

## Eval set

gold-92: 35 brand clips (Rezolve/brainpowa), 10 neutral clips.
NEVER use gold-92 for tuning — inference only.

## Usage

```bash
# On gpu-azure, conda env stt, from repo root
PYTHONPATH=. python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py
PYTHONPATH=. python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py --clips 5  # smoke test
PYTHONPATH=. python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py --skip-sweep  # TDT baseline only
```

## Expected outputs

- `results/tdt_sweep.jsonl` — 100 cells (same grid as t0022)
- `results/tdt_baseline.jsonl` — TDT with current prod config (greedy_batch, cs=1/ds=2/alpha=1)
- `results/comparison.md` — side-by-side table + verdict
