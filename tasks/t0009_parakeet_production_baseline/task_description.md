# Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Motivation

Parakeet TDT 0.6b-v3 (NVIDIA) is the current production STT model deployed in brainpowa's
voice-commerce pipeline. Tasks t0006–t0010 all compare their benchmarked models against this
production system, making it essential to have directly comparable metrics computed with the
same evaluation harness.

Prior tasks (t0001–t0005) used Whisper large-v3 as the reference baseline. This task establishes
a second, more operationally relevant baseline using the actual production model, so that
benchmark results are interpretable in terms of real-world improvement potential.

## Goal

Run Parakeet TDT 0.6b-v3 on all 93 gold-92 clips in two configurations:

1. **Unbiased** — standard inference, no keyword injection
2. **Biased (production config)** — with the keyword biasing configuration currently deployed
   in production

Compute entity accuracy, domain-vocabulary accuracy, WER, action-critical WER, intent
preservation, and latency p50/p95/p99 using the same evaluation harness as all other benchmark
tasks.

## Success Criteria

- All 93 clips transcribed in both configurations
- metrics.json written with both variants
- Prediction assets registered for DVC tracking
- Results summary and detailed report completed
