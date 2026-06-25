---
spec_version: "1"
predictions_id: moonshine-v2-medium-gold92-biasing-assessment
task: t0008_moonshine_v2_benchmark
date_created: "2026-06-25"
model: UsefulSensors/moonshine-streaming-medium
dataset: stt-benchmark-gold-92
instance_count: null
---
## Metadata

- **Model:** UsefulSensors/moonshine-streaming-medium
- **Task:** t0008_moonshine_v2_benchmark
- **Type:** Feasibility assessment (no per-clip predictions)
- **Date:** 2026-06-25

## Overview

This asset documents a feasibility assessment for adding shallow-fusion vocabulary biasing to
Moonshine v2 Medium. The assessment was motivated by the model's low domain-vocabulary entity
accuracy (9.1%) compared to Whisper with vocabulary biasing (94.5%). No inference was run for this
asset; it is an architectural analysis only.

## Model

- **HuggingFace ID:** UsefulSensors/moonshine-streaming-medium
- **Architecture:** Sliding-window Transformer encoder-decoder (not CTC)
- **Key constraint:** No `initial_prompt` support; no built-in hotword boosting

## Data

References the gold-92 benchmark and Rezolve domain vocabulary (31 terms) from
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py`.

## Prediction Format

Assessment document only. See `files/shallow_fusion_feasibility.md` for the full analysis.

## Metrics

Not applicable (no inference run for this asset).

## Main Ideas

- Moonshine v2 Medium uses an encoder-decoder architecture that blocks the easiest shallow-fusion
  path (CTC hotword boosting via pyctcdecode)
- Log-linear N-best rescoring (KenLM domain LM) is the recommended approach: ~3-5 days effort,
  +50-80ms latency overhead per clip
- Feasibility verdict: "needs research" — the approach is architecturally viable but 85pp entity
  accuracy gap vs Whisper biased is unlikely to close fully from shallow fusion alone
- Hybrid routing (Moonshine for latency-critical queries, Whisper for entity-critical) may offer the
  best production trade-off

## Summary

Three shallow-fusion approaches were assessed:

1. **Log-linear N-best rescoring** (recommended): Rescore top-4 beams with a KenLM domain LM.
   Effort: 3-5 days. Latency overhead: +50-80ms.
2. **pyctcdecode CTC hotword boosting**: Requires CTC-head surgery or an official CTC variant.
   Blocked by encoder-decoder architecture.
3. **Lattice rescoring**: Similar to approach 1 but with full lattice; higher complexity for
   marginal gain.

**Verdict:** Viable for production (with effort), but the entity accuracy gap vs. Whisper is large.
A hybrid routing strategy (Moonshine for latency-critical, Whisper for entity-critical) may be
optimal.
