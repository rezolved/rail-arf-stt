# Omni-LLM Cascade Streaming STT Benchmark — Parakeet+Qwen3-Omni vs Granite

## Motivation

The brainpowa-realtime-api production pipeline runs an omni-LLM cascade: Parakeet performs fast STT
in ~250–350 ms, while Qwen3-Omni transcribes the same audio with domain hints injected via system
prompt. If Qwen3-Omni finishes within a 0.5 s hard timeout, its transcript is used; otherwise the
pipeline falls back to Parakeet. This design aims to raise domain-entity accuracy (brands, SKUs,
product names) beyond what Parakeet-only achieves (~33% EA-DV), ideally to Granite's level (~97%
EA-DV from t0015), without sacrificing the sub-800 ms p50 latency target.

t0015 established that Granite Speech 4.1 2B achieves ~97% EA-DV in streaming mode, but Parakeet
models remain at ~33% EA-DV despite NeMo contextual biasing. This task answers whether the omni-LLM
cascade can close that gap while staying within production latency constraints, and how the two
Parakeet model variants compare when paired with Qwen3-Omni.

## Pipeline Under Test (Production-Accurate)

Each audio segment is processed by two parallel paths:

1. **Parakeet STT** (NeMo GPU-PB TurboBias, boosting_alpha=1.0, context_score=1.0,
   depth_scaling=2.0, bpe_dropout=True) — produces a transcript in ~250–350 ms.
2. **Qwen3-Omni** (cpatonn/Qwen3-Omni-30B-A3B-Instruct-AWQ-4bit) — transcribes the same audio with
   domain hints injected via system prompt (stt_initial_prompt = Rezolve domain vocab,
   comma-separated). Hard timeout: 0.5 s from segment start.

Decision rule: if Qwen3-Omni finishes within 0.5 s → use Qwen3-Omni transcript; otherwise fall back
to Parakeet transcript. Both paths run concurrently so there is no sequential latency penalty when
Qwen3-Omni wins.

## Models to Benchmark

Three pipeline variants, 9 total run configurations:

**Cascade runs (6 total — 2 Parakeet models × 3 buffer intervals):**

1. **Parakeet-TDT-0.6b-v3 + Qwen3-Omni** at 500 ms buffer interval
2. **Parakeet-TDT-0.6b-v3 + Qwen3-Omni** at 750 ms buffer interval
3. **Parakeet-TDT-0.6b-v3 + Qwen3-Omni** at 1000 ms buffer interval
4. **Parakeet-Unified-en-0.6b + Qwen3-Omni** at 500 ms buffer interval
5. **Parakeet-Unified-en-0.6b + Qwen3-Omni** at 750 ms buffer interval
6. **Parakeet-Unified-en-0.6b + Qwen3-Omni** at 1000 ms buffer interval

**Baseline (reused from t0015, 0 new inference runs):**

7. **Granite Speech 4.1 2B streaming** at 500 ms buffer interval (t0015 prediction files)
8. **Granite Speech 4.1 2B streaming** at 750 ms buffer interval (t0015 prediction files)
9. **Granite Speech 4.1 2B streaming** at 1000 ms buffer interval (t0015 prediction files)

Granite results are loaded directly from t0015 prediction assets — no re-inference required.

## Dataset

**gold-92**: 93 WAV clips (16 kHz mono PCM), Rezolve production investor-relations sessions,
accented English. Same 93 clips used in t0015. References remain unchanged so results are directly
comparable across all tasks.

NEVER train or tune on gold-92 — it is a held-out regression set only.

## Metrics to Collect

The following metrics are computed for every run configuration (all 9 variants):

**Standard project metrics:**

- `wer_gold92` — word error rate vs gold-92 references
- `entity_accuracy_gold92` (EA) — fraction of entity strings correctly transcribed
- `entity_accuracy_domain_vocab` (EA-DV) — entity accuracy restricted to domain vocabulary terms
  (brands, SKUs, product names from the Rezolve domain vocab list from t0015)
- `latency_p50_seconds` — wall-clock p50 latency per clip (including Qwen3-Omni correction when
  used; total cascade latency, not just Parakeet)
- `intent_preservation_gold92` — intent preservation rate
- `action_critical_wer_gold92` — action-critical WER
- `wrong_action_rate_gold92` — wrong action rate

**Cascade-specific additional metrics (per clip, reported in results):**

- `omni_used_rate` — fraction of clips where Qwen3-Omni finished within 0.5 s budget (vs fallback to
  Parakeet). Target: report mean ± std across the 93 clips.
- `omni_latency_p50_seconds` — Qwen3-Omni inference time p50 per clip
- `omni_latency_p95_seconds` — Qwen3-Omni inference time p95 per clip
- `ttfd_seconds` — time to first non-empty transcript from segment start (p50 and p95)

**Efficiency metrics (per cascade run):**

- `efficiency_inference_time_per_item_seconds` — total cascade wall-clock per clip
- `efficiency_inference_cost_per_item_usd` — cost per clip (Qwen3-Omni GPU time on H100 NVL)

## Implementation Approach

### Code Reuse from t0015

The streaming simulation code from t0015 (`tasks/t0015_streaming_buffer_interval/`) implements:

- Audio chunking at configurable buffer intervals (500 ms, 750 ms, 1000 ms)
- NeMo GPU-PB TurboBias biasing for Parakeet (with the Rezolve domain vocab keyword list)
- Metric computation harness (WER, EA, EA-DV, intent preservation, latency)

Reuse this code directly; add a parallel Qwen3-Omni runner with the 0.5 s timeout and a cascade
decision function.

### Qwen3-Omni Integration

- Model: `cpatonn/Qwen3-Omni-30B-A3B-Instruct-AWQ-4bit` (AWQ 4-bit quantization)
- System prompt: stt_initial_prompt containing the Rezolve domain vocabulary as a comma-separated
  hint list (same vocab list used for Parakeet biasing in t0015)
- Audio input: same 16 kHz mono PCM segment passed to Parakeet
- Timeout: 0.5 s wall-clock from segment start; enforced with asyncio or threading timeout
- If timeout triggers → use Parakeet transcript; record `omni_used=False` for the clip

### Granite Reuse

Load t0015 prediction files for Granite Speech 4.1 2B at all three buffer intervals. Re-run metric
computation on the loaded predictions to produce a consistent result row for comparison. Do not
re-run Granite inference.

## Compute and Budget

**Machine:** Azure H100 NVL (llm-t1-nc80, same as t0015). Qwen3-Omni-30B AWQ 4-bit requires H100 for
acceptable inference speed — the 0.5 s budget cannot be met on A100 or smaller GPUs.

**Budget estimate:**

- 6 cascade runs × ~$10–12 per run (93 clips × Qwen3-Omni inference on H100 NVL) = **$60–72**
- Granite reuse: $0 marginal cost
- Machine setup/teardown overhead: ~$5–8

**Total estimated budget: $65–80.**

Reserve up to $80. If Qwen3-Omni proves faster than expected (many clips timeout → Parakeet fallback
used), actual cost will be lower.

**Parallelism:** Run all 6 cascade configurations sequentially on a single H100 NVL (Qwen3-Omni
occupies the full GPU). Do not attempt to parallelize cascade runs.

## Key Questions

1. Does Qwen3-Omni correction raise EA-DV from ~33% (Parakeet-only, t0015) to Granite level (~97%)?
   If not, what is the achieved EA-DV?
2. Does the 0.5 s Qwen3-Omni hard timeout hold in practice — what fraction of clips use Omni vs fall
   back to Parakeet?
3. What is the total cascade latency (p50/p95) vs Parakeet-only and Granite from t0015?
4. Does Parakeet-Unified + cascade outperform Parakeet-TDT + cascade on WER and EA-DV?
5. Can the cascade stay under the 800 ms p50 latency target across all buffer intervals?

## Expected Outputs

### Assets

- 1 **answer asset** addressing all 5 key questions above with supporting data

### Prediction files

- `data/predictions_parakeet_tdt_500ms.jsonl` — cascade transcript + decision per clip
- `data/predictions_parakeet_tdt_750ms.jsonl`
- `data/predictions_parakeet_tdt_1000ms.jsonl`
- `data/predictions_parakeet_unified_500ms.jsonl`
- `data/predictions_parakeet_unified_750ms.jsonl`
- `data/predictions_parakeet_unified_1000ms.jsonl`

### Results

- `results/metrics_summary.json` — all metrics for all 9 variants (6 cascade + 3 Granite reused)
- `results/results_detailed.md` — full write-up with tables and charts
- `results/images/ea_dv_by_variant.png` — EA-DV per variant; answers Q1
- `results/images/latency_p50_p95_cascade.png` — p50/p95 latency per variant; answers Q3 and Q5
- `results/images/omni_used_rate_by_interval.png` — omni_used_rate per buffer interval; answers Q2
- `results/images/wer_by_parakeet_variant.png` — WER: TDT vs Unified at each interval; answers Q4

### Tables in results_detailed.md

**Table 1: Core metrics by variant (all 9 rows)**

Columns: variant | buffer_ms | WER | EA | EA-DV | latency_p50 | latency_p95 | intent_pres |
wrong_action_rate

**Table 2: Cascade-specific metrics (6 cascade rows only)**

Columns: variant | buffer_ms | omni_used_rate | omni_latency_p50 | omni_latency_p95 | ttfd_p50

**Table 3: Parakeet-TDT vs Parakeet-Unified delta table**

Columns: buffer_ms | ΔWER | ΔEA | ΔEA-DV | Δlatency_p50 — sign indicates which is better

## Dependencies

- **t0015_streaming_buffer_interval** (required): provides Granite prediction files for reuse;
  domain vocab list for Parakeet biasing and Qwen3-Omni system prompt; streaming simulation code to
  extend with cascade logic.

t0016_streaming_fuzzy_hotword_correction is NOT a dependency — it is not yet completed and its
outputs are not required to run this task.

## Data Handling

- All per-clip prediction files (JSONL) saved to `data/` within the task folder
- Audio files are not duplicated — re-read from t0001_stt_benchmark DVC-tracked audio
- Large prediction files tracked with DVC; `dvc push` before merging PR
