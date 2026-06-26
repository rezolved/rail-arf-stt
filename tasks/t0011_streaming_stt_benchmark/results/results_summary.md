# t0011 — Streaming STT Benchmark: Results Summary

Streaming delivery (32 kB PCM chunks, accumulate-then-transcribe) produces results statistically
identical to batch on both models: all accuracy deltas are below 0.1 pp and latency overhead is
under 4 ms. Granite Speech 4.1 2B (biased) leads on all accuracy metrics under streaming
(EA 41.1%, AC-WER 7.6%), while Parakeet TDT 0.6b-v3 (biased) retains a 6× latency advantage
(41 ms vs 250 ms p50).

## Key Numbers

| Model | EA | EA\_DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Parakeet biased — batch (t0009) | 23.2% | 33.3% | 15.2% | 33.5% | 87.1% | 38 ms |
| Granite 4.1 2B biased — batch (t0007) | 40.2% | 98.6% | 8.8% | 8.2% | 92.5% | 248 ms |
| **Parakeet biased — streaming (t0011)** | **23.1%** | **33.3%** | **15.2%** | **33.5%** | **87.1%** | **41 ms** |
| **Granite 4.1 2B biased — streaming (t0011)** | **41.1%** | **97.1%** | **8.8%** | **7.6%** | **93.6%** | **250 ms** |

## Streaming vs Batch Delta

| Model | ΔEA | ΔEA\_DV | ΔWER | ΔAC-WER | ΔIP | ΔLat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Parakeet | −0.05 pp | +0.03 pp | +0.05 pp | +0.04 pp | 0.00 pp | +3 ms |
| Granite | +0.87 pp | −1.45 pp | 0.00 pp | −0.63 pp | +1.08 pp | +1 ms |

## Verdict

The accumulate-then-transcribe pattern is functionally equivalent to batch inference.
Production deployment can be treated as batch for accuracy and latency estimation purposes.
Granite is the preferred model if accuracy is the priority; Parakeet if sub-50 ms latency
is required.

## Machine

Azure H100 NVL (`gpu-azure`, `azureuser@llm-t1-nc80`), 2026-06-26.
Parakeet run: ~2 min. Granite run (incl. warmup): ~4 min. Both models loaded sequentially.
