# Benchmark FunASR SeACo-Paraformer on Gold-92

## Motivation

Task t0005 (STT model survey) identified FunASR SeACo-Paraformer-en as a candidate for
contextual-biasing benchmarking. SeACo-Paraformer is a variant of the Paraformer architecture
with a dedicated contextual biasing module (SeACo — Selective Attention with Contextual Objects),
designed to improve recall of domain-specific vocabulary. The English variant
(`iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020`) was identified as a potential
lower-latency alternative to Granite biased, given Paraformer's CTC-based architecture.

The task was also motivated by suggestion S-0005-02 from task t0005's suggestion generation.

## Goal

Run FunASR SeACo-Paraformer-en on all 93 gold-92 clips in two configurations:

1. **Batch (no biasing)** — standard Paraformer inference without contextual biasing
2. **SeACo biased** — SeACo contextual biasing with Rezolve domain vocabulary

Compute entity accuracy, domain-vocabulary accuracy, WER, action-critical WER, intent
preservation, and latency p50/p95/p99. Compare against Parakeet production (t0009) and
Granite biased (t0007) baselines.

## Success Criteria

- All 93 clips transcribed in both configurations
- metrics.json written with both variants
- Prediction assets registered for DVC tracking
- Results summary and detailed report completed
