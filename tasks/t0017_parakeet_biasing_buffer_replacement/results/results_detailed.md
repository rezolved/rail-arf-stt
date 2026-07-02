# t0017 — Parakeet unified vs TDT: Biased Accuracy, Latency & Buffer Sweep

**Question:** should brainpowa's production Parakeet (`parakeet-tdt-0.6b-v3`) be replaced by
`parakeet-unified-en-0.6b`, and what streaming buffer size is best?

**Answer:** `parakeet-unified-en-0.6b` wins on **every** biased accuracy metric and is the more
reliable model — a strict upgrade within the Parakeet family. Keep the buffer at **1000ms**.
Caveat: domain-entity accuracy stays low (~35%) for both — biasing barely helps Parakeet.

---

## 1. Summary

| | WER ↓ | Entity Acc ↑ | EA domain-vocab ↑ | empty ↓ | halluc ↓ | latency p50 | TTFD p50 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| parakeet-tdt-0.6b-v3 (prod) | 15.25% | 22.81% | 33.33% | 3 | 0 | 0.239s | 0.033s |
| **parakeet-unified-en-0.6b** ⭐ | **11.03%** | **23.44%** | **34.78%** | **0** | 0 | 0.335s | 0.037s |
| **delta (unified − tdt)** | **−4.22pp** | **+0.63pp** | **+1.45pp** | **−3** | 0 | +0.096s | +0.004s |

Winner selected by accuracy across all three metrics together (WER, EA, EA-DV) — unified is strictly
better on all three, plus eliminates all 3 empty transcripts. Latency numbers are at the production
1000ms buffer.

---

## 2. Methodology

- **Dataset:** gold-92 (93 production WAV clips, ≥3.07s, 16kHz mono PCM-16). Held-out; never tuned on.
- **Biasing:** NeMo GPU-PB TurboBias, production config — `alpha=1.0`, `context_score=1.0`,
  `depth_scaling=2.0`, `use_bpe_dropout=True`, 31-term Rezolve vocab expanded to 66 casing variants.
  Boosting tree confirmed built on **both** models (66 phrases, alpha 1.0) — see `logs/run.log`.
- **Streaming:** production accumulate-then-retranscribe pattern (32kB chunks, re-transcribe every N
  ms), mirroring brainpowa `ParakeetSTT.transcribe_stream` incl. `_extract_delta`.
- **All accuracy is biased** (GPU-PB on). Unbiased runs were out of scope.
- **Machine:** Azure H100 NVL (`llm-t1-nc80`), NeMo 3.1.0, conda env `stt`. Both models from HF cache.
- **Latency caveat:** the sweep feeds audio instantly, so `latency`/`TTFD` measure **compute** time
  (relative cost per model), not real-time perceived latency (which adds real-time buffer fill). Valid
  for model-vs-model comparison and interval trends; end-to-end perceived latency would be higher.

---

## 3. Biased accuracy — unified wins on all metrics

![Biased accuracy: tdt vs unified](images/accuracy_comparison.png)

unified cuts WER by 4.2pp (15.3%→11.0%) and edges ahead on both entity metrics. The gain is largest
on WER — unified produces cleaner overall transcripts.

## 4. Reliability — unified has zero empty outputs

![Empty outputs](images/reliability_comparison.png)

TDT returned **3 empty transcripts** on gold-92; unified returned **0**. Empty output on short
utterances is the exact failure mode that disqualified Whisper from production — unified is safer here.
Neither model hallucinated.

## 5. Buffer sweep on the winner (unified)

![Winner latency by interval](images/winner_latency_by_interval.png)

| interval | WER | EA-DV | latency p50 | latency p95 | TTFD p50 |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 200ms | 11.03% | 34.78% | 0.373s | 0.644s | 0.037s |
| 300ms | 11.03% | 34.78% | 0.359s | 0.641s | 0.037s |
| 350ms | 11.03% | 34.78% | 0.359s | 0.634s | 0.037s |
| 500ms | 11.03% | 34.78% | 0.357s | 0.646s | 0.037s |
| 750ms | 11.03% | 34.78% | 0.345s | 0.605s | 0.037s |
| **1000ms** | 11.03% | 34.78% | **0.335s** | **0.587s** | 0.037s |

**Accuracy is fully invariant to buffer interval** (identical final transcript). The latency numbers
above measure compute-only cost (audio fed instantly, not real-time paced) and are valid for
model-vs-model comparison but not for perceived latency. In real-time-paced measurement TTFD scales
linearly with the interval (≈ interval + 16ms), so **smaller buffer = faster first partial word**.
→ **Lower the production buffer from 1000ms toward ~300ms**: TTFD drops from ~1.0s → ~0.32s
(3× more responsive), accuracy and finalization latency (~55ms) are unchanged. The only cost is more
GPU re-transcribe passes per session. Choose 200–350ms for best UX if GPU headroom allows; 500ms
as a compute-saving compromise. See `results/buffer_interval_realtime.md` for the full real-time
measurement.

## 6. Latency vs production budget

![Latency comparison @1000ms](images/latency_comparison.png)

unified costs +96ms compute latency vs tdt (0.335s vs 0.239s) but both sit far under the 800ms
voice-to-action budget. TTFD is effectively equal (37ms vs 33ms). The latency cost of switching is
acceptable.

---

## 7. The dominant caveat — biasing barely helps Parakeet

Even biased, the winner's domain-vocab entity accuracy is only **34.8%**. Both models mis-transcribe
the flagship term: TDT writes "Rizol AI", unified writes "Resolve AI" — never "Rezolve". GPU-PB is
active and correctly configured, but its ceiling on the Parakeet TDT/unified decoders is low,
consistent with t0009's measured **+1.4pp** biasing gain. For comparison, Granite Speech 4.1 2B
reaches **97.1%** EA-DV on the same vocab (t0012/t0015).

So unified is the better *Parakeet*, but Parakeet is a weak choice if domain-entity accuracy is the
product goal.

---

## 8. Recommendation

**CONDITIONAL — replace within Parakeet; reconsider the family for entity accuracy.**

1. **If staying on Parakeet:** replace `parakeet-tdt-0.6b-v3` → `parakeet-unified-en-0.6b`.
   Strictly better quality (WER −4.2pp, EA-DV +1.5pp), 3→0 empty outputs, TTFD unchanged, latency
   still ~0.34s ≪ 800ms. Integration is a one-line checkpoint swap: set
   `PARAKEET_MODEL=nvidia/parakeet-unified-en-0.6b` (GPU-PB config, streaming path, and
   `stt_initial_prompt` biasing channel are unchanged — confirmed GPU-PB loads on unified).
2. **Buffer:** lower from **1000ms → ~300ms**. TTFD drops 3× (1.0s → 0.32s), accuracy unchanged,
   no backpressure. Trade-off: more GPU passes per session. Use 200–350ms for best UX; 500ms if
   GPU capacity is constrained.
3. **If domain-entity accuracy (Rezolve/brainpowa/SKU) is the priority:** Parakeet is the wrong
   family. Move to Granite Speech 4.1 2B (97.1% EA-DV) — see t0012/t0014/t0015.

---

## 9. Files created

- Predictions: `data/parakeet_tdt/predictions_{200,300,350,500,750,1000}ms.jsonl`,
  `data/parakeet_unified/predictions_{...}ms.jsonl` (93 rows each, biased).
- Metrics: `results/metrics.json` (12 variants).
- Charts: `results/images/{accuracy_comparison,reliability_comparison,winner_latency_by_interval,latency_comparison}.png`.
- Run log (GPU-PB build proof): `logs/run.log`.

## 10. Task Requirement Coverage

- REQ-1 (biasing impl = NeMo; GPU-PB on both) — §2, `logs/run.log` (66 phrases each). ✓
- REQ-2/3 (fresh biased predictions both models) — §9, 93 rows each. ✓
- REQ-4 (head-to-head metrics) — §1, `results/metrics.json`. ✓
- REQ-5 (winner by all three metrics) — §1, §3. ✓
- REQ-6/7 (winner buffer sweep 200–1000ms, latency) — §5. ✓
- REQ-8 (bar charts embedded) — §3–6. ✓
- REQ-10 (YES/NO/CONDITIONAL recommendation + integration delta) — §8. ✓
