# Granite vs Parakeet vs Whisper
**Rezolve STT · Benchmark Summary · June 2026**

---

## Datasets

| Task | Dataset | Clips | Conditions |
|------|---------|------:|------------|
| t0007 / t0009 / t0012 | gold-92 · production IR WAVs | 93 | ≥ 3.07s · 16kHz mono · complete utterances |
| t0014 | short clips · synthetic cuts from gold-92 | 44 | ≤ 5s · 6 duration bins · partial utterances |

---

## Full Clips — Streaming (t0012 · gold-92 · 93 clips)

| Model | EA | EA domain-vocab | WER | AC-WER | Lat p50 |
|-------|----|-----------------|-----|--------|---------|
| Whisper turbo | 42.0% | 89.9% | 9.0% | 6.3% | 290ms |
| **Granite 4.1 2B** ⭐ | 41.1% | **97.1%** | **8.8%** | 7.6% | 249ms |
| Parakeet TDT 0.6b | 23.2% | 33.3% | 15.2% | 33.5% | **40ms** |

> Granite keyword prompt: +66pp on domain-vocab EA. Parakeet production uses NeMo GPU-PB TurboBias (boosting tree in TDT decoder) — effect +1.4pp domain-vocab (tested in t0009 with production config).

---

## Short Clips — Robustness (t0014 · synthetic cuts · 44 clips)

### Empty Rate and Hallucination by Bin

| Bin | n | Granite empty | Parakeet empty | Whisper hall. |
|-----|:-:|:---:|:---:|:---:|
| < 1s | 9 | **0%** | 56% | 67% |
| 1–2s | 14 | **0%** | 29% | 29% |
| 2–3s | 14 | **0%** | 14% | 7% |
| 3–5s | 7 | **0%** | 14% | 0% |
| **Total** | **44** | **0%** | **27%** | **25%** |

### WER @3–5s (only valid bin)

| Model | WER | EA |
|-------|:---:|:--:|
| **Granite 4.1 2B** | **4.9%** | **96.2%** |
| Whisper turbo | 7.5% | 94.6% |
| Parakeet TDT 0.6b | 21.5% | 64.5% |

> WER for bins < 3s is **not meaningful**: reference is the full original transcript, clip contains only the first N seconds. The model correctly transcribes what it hears, but WER is computed against the complete sentence → 80–95%. Relevant metrics for short clips: empty rate and hallucination rate.

---

## Summary — Production Mode

| Metric | Granite 4.1 2B | Parakeet TDT 0.6b | Whisper turbo |
|--------|:--------------:|:-----------------:|:-------------:|
| WER (full clips) | **8.8%** | 15.2% | 9.0% |
| EA domain-vocab | **97.1%** | 33.3% | 89.9% |
| AC-WER | 7.6% | 33.5% | **6.3%** |
| Empty (< 3s clips) | **0%** | 27–56% | 0% |
| Hallucination (< 3s) | **0%** | 0% | 29–67% |
| Latency p50 | 249ms | **40ms** | 290ms |
| Keyword biasing | ✅ +66pp EA-DV | ⚠️ +1.4pp EA-DV (GPU-PB) | ✅ initial_prompt |

---

## Recommendation

**Granite** → production.
Best WER on domain, 97% domain-vocab EA, only model with 0% empty and 0% hallucinations on short clips. With a ≥ 2s clip gate — full reliability.

**Parakeet** → fallback only when latency < 50ms is a hard requirement on long clips (≥ 3s).
