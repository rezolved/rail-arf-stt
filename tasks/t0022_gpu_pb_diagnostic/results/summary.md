# t0022 GPU-PB Diagnostic — Summary

## Brand recognition rate per config

| Config | EXACT | PHONETIC | GARBAGE |
|--------|-------|----------|---------|
| a_greedy_no_boost | 0/35 (0%) | 32/35 | 3/35 |
| b_greedy_boost | 0/35 (0%) | 33/35 | 2/35 |
| c_beam_no_boost | 0/35 (0%) | 32/35 | 3/35 |
| d_beam_boost | 7/35 (20%) | 25/35 | 3/35 |

Greedy→beam delta (no boost): +0 clips exact

Best sweep cell: cs=2.5 ds=0.5 alpha=2.5 → brand_exact=0.686 neutral_wer=0.279

Dominant baseline failure: PHONETIC_NEIGHBOR
  → encoder hears the brand but maps to wrong token; boosting may help

Greedy boost gain: +0 clips (0% → 0%)

**VERDICT: config-fixable (use beam / tune params)**
