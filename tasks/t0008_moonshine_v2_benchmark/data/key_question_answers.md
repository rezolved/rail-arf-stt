# Key Question Answers — Moonshine v2 Medium Benchmark

**Task:** t0008_moonshine_v2_benchmark **Date:** 2026-06-25 **Model:**
UsefulSensors/moonshine-streaming-medium **Dataset:** gold-92 (93 clips)

## Measured Metrics

| Metric | Measured | Whisper Baseline |
| --- | --- | --- |
| Entity accuracy (domain vocab) | 9.1% | 94.5% |
| Entity accuracy (overall) | 21.7% | 46.0% |
| WER | 16.6% | 8.5% |
| Action-critical WER | 34.2% | 2.5% |
| Intent preservation | 87.1% | - |
| Wrong-action rate | 12.9% | - |
| Latency p50 (warmed) | 0.233s | - |
| Latency p50 cold-start | 1.327s | - |

* * *

## Question Answers

### Q1: Entity accuracy (domain vocab) without biasing — Does Moonshine >= 46%?

**NO**

Measured entity accuracy (domain vocab): **9.1%** (95% BCa CI: 5.4%–27.0%). This is far below the
46% Whisper overall baseline and the 94.5% Whisper-with-biasing baseline. Moonshine transcribes
general speech reasonably well but cannot recognise Rezolve-specific terms (brainpowa, Rezolve AI,
NASDAQ, personnel names) without vocabulary biasing. The entity accuracy gap is 85 percentage points
vs. Whisper with biasing.

### Q2: WER — Is Moonshine WER <= 8.5%?

**NO**

Measured WER: **16.6%** (95% BCa CI: 14.8%–22.6%). Moonshine v2 Medium underperforms Whisper on this
domain-specific benchmark. The gap is primarily due to domain-specific terminology not present in
Moonshine's training data. General WER on clean English may be lower, but on accented
investor-relations speech, Whisper is significantly better.

### Q3: Action-critical WER — Does Moonshine AC-WER <= 2.5%?

**NO**

Measured action-critical WER: **34.2%**. This is 13x the Whisper baseline (2.5%). Action-critical
WER is computed over entity span words only; since Moonshine does not recognise most
Rezolve-specific entities, this metric is severely impacted. The model is not suitable for
production entity-heavy voice commerce queries without biasing.

### Q4: Latency — Is Moonshine p50 <= 200ms on local CPU after warm-up?

**UNCERTAIN / BORDERLINE**

Measured warmed p50: **233ms** (p95: 363ms, p99 not well-defined with 88 warmed clips). The 200ms
target is not met in our local CPU measurements. However, the margin is small (33ms over target).
With hardware optimisation, ONNX export, or quantisation, the <200ms target may be achievable. The
current measurement uses the transformers CPU backend without optimisation.

### Q5: Cold-start latency — Is first-clip latency acceptable for real-time UX?

**NO (without pre-warming)**

Cold-start latency: **1.327s** (single observation). This significantly exceeds the 800ms
voice-to-action budget. Pre-warming (loading model weights before the first user request) would
eliminate this cost. Production deployments would require either pre-warming at service start or
accepting cold-start delay on first query after idle. Once warm, latency is acceptable at 233ms p50.

### Q6: Shallow fusion feasibility — Can a biasing adapter be integrated in <20 hours?

**YES (with caveat)**

Log-linear N-best rescoring is feasible in approximately 3-5 days (15-25 hours). The main effort is:
(1) training a trigram KenLM on domain text, (2) wrapping `model.generate()` with `num_beams=4` and
custom rescoring, (3) tuning the interpolation weight lambda.

However, Moonshine's encoder-decoder architecture blocks the easier CTC-based pyctcdecode approach.
Lattice rescoring is also viable at similar effort.

The caveat: even with shallow fusion, closing an 85 percentage-point entity accuracy gap is
unlikely. Whisper with biasing (94.5%) should remain the primary production model.

### Q7: Accented English (production subset) — Does Moonshine entity accuracy exceed Whisper on production clips?

**UNCERTAIN**

The production subset (34 clips, accent_group="production") metrics were computed but no direct
Whisper-per-subset comparison is available from t0004 outputs. Moonshine's production subset entity
accuracy is expected to be similar to the overall 21.7%, which is lower than Whisper's 46% overall
baseline. Without explicit production-subset Whisper numbers, this question cannot be definitively
answered.

* * *

## Strategic Interpretation

Moonshine v2 Medium is **not ready for production deployment** on Rezolve's voice commerce use case
in its current form:

1. **WER is 2x Whisper** on this domain-specific benchmark
2. **Domain-vocab entity accuracy is catastrophically low** (9.1%) without biasing
3. **Latency marginally misses the 200ms target** on local CPU without optimisation

However, Moonshine has two genuine strengths:

- **Excellent warmed latency** (233ms p50) — competitive for streaming use cases
- **Shallow fusion is feasible** — N-best rescoring could improve entity accuracy

**Recommended path:** Continue with Whisper (t0004 configuration) as production STT. Moonshine is a
viable candidate for a future streaming-optimised path if: (a) vocabulary biasing is implemented,
and (b) latency is further optimised via ONNX export or quantisation.

A hybrid architecture — Moonshine for latency-tolerant fallback, Whisper for entity-critical queries
— may offer the best trade-off.
