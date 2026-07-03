# Task t0019 — Parakeet-unified biasing improvement

## Goal

Improve GPU-PB TurboBias biasing quality on `parakeet-unified-en-0.6b` (winner of
[[t0017]]) beyond the current ~35% EA-DV baseline, without hurting WER/latency.

## Background

[[t0017]] found biasing barely helps Parakeet: EA-DV ~35%, model still writes
"Resolve"/"Rizol" instead of "Rezolve". Boosting params are untouched defaults
(`PARAKEET_BOOSTING_ALPHA=1.0`, `context_score=1.0`, `depth_scaling=2.0`,
t0017 `code/constants.py:35-37`). Phrase list only has casing variants (bug just fixed),
no phonetic/misspelling variants.

## Approaches to test (ranked by expected ROI)

1. **Boosting hyperparam sweep.** Grid over alpha (1.0-3.0), context_score, depth_scaling
   on gold-92, biased. Measure EA-DV vs WER (hallucination risk) trade-off. Cheap, reuses
   t0017 harness.
2. **Phrase-list expansion with phonetic/misspelling variants.** Add explicit near-miss
   forms (e.g. "Resolve", "Rizol" → "Rezolve") to the boosting phrase list, not just
   casing. Targets the known observed failure directly.
3. **Post-hoc `stt_replacements` fallback.** For terms biasing can't reliably fix,
   add deterministic post-decode string replacement (separate from boosting_tree,
   already exists as a channel in `brainpowa-realtime-api`). Belt-and-suspenders.

Deprioritized (higher cost, lower/uncertain ROI, skip unless above stall):
per-phrase weighting, beam rescoring, fine-tuning.

## Expected Assets

- 3 prediction sets (baseline, best hyperparam config, best hyperparam + phrase expansion)
- 1 answer/results doc comparing EA, EA-DV, WER, latency vs t0017 biased baseline
