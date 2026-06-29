# ✅ Tasks: Completed

13 tasks. ✅ **13 completed**.

[Back to all tasks](../README.md)

---

## ✅ Completed

<details>
<summary>✅ 0013 — <strong>Brainstorm Results — Session 1</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0013_brainstorm_results_1` |
| **Status** | completed |
| **Effective date** | 2026-06-29 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md), [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md), [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md), [`t0006_nemotron_3_5_benchmark`](../../../overview/tasks/task_pages/t0006_nemotron_3_5_benchmark.md), [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md), [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md), [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md), [`t0010_funasr_paraformer_benchmark`](../../../overview/tasks/task_pages/t0010_funasr_paraformer_benchmark.md), [`t0011_streaming_stt_benchmark`](../../../overview/tasks/task_pages/t0011_streaming_stt_benchmark.md), [`t0012_whisper_parakeet_granite_streaming`](../../../overview/tasks/task_pages/t0012_whisper_parakeet_granite_streaming.md) |
| **Expected assets** | — |
| **Source suggestion** | — |
| **Task types** | [`brainstorming`](../../../meta/task_types/brainstorming/) |
| **Start time** | 2026-06-29T00:00:00Z |
| **End time** | 2026-06-29T00:00:00Z |
| **Step progress** | 4/4 |
| **Task page** | [Brainstorm Results — Session 1](../../../overview/tasks/task_pages/t0013_brainstorm_results_1.md) |
| **Task folder** | [`t0013_brainstorm_results_1/`](../../../tasks/t0013_brainstorm_results_1/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0013_brainstorm_results_1/results/results_detailed.md) |

# t0013 — Brainstorm Results: Session 1

## Overview

First brainstorm session for the rail-arf-stt project. Reviewed all 12 completed tasks,
assessed the 24 active suggestions, and decided on one new task and six suggestion rejections.

## Context

All 12 tasks completed. The model landscape is clear: Whisper turbo (42.0% EA) and Granite
Speech 4.1 2B (41.1% EA) lead by a large margin over the current production model Parakeet TDT
0.6b-v3 (23.2% EA). Nemotron, Moonshine, and FunASR Paraformer are eliminated. The strategic
question is whether Granite can replace Parakeet in production — complicated by a known
Whisper failure mode on short audio clips that was the original reason Parakeet was adopted.

## Decisions

1. Create t0014: Granite short-clip robustness validation and production fit assessment.
   Simulates real production streaming (32kB PCM-16 chunk queue via `transcribe_stream()`) on
   synthetic short clips (0.5–2s) and stratified gold-92 analysis. GPU run on Azure H100 NVL.
2. Reject S-0002-01: superseded by t0004.
3. Reject S-0005-04: Moonshine eliminated.
4. Reject S-0005-09: FunASR Paraformer eliminated.
5. Reject S-0008-01: Moonshine eliminated.
6. Reject S-0008-02: Moonshine eliminated.
7. Reject S-0008-03: Moonshine eliminated.

**Results summary:**

> **Results Summary — t0013 Brainstorm Session 1**
>
> **Summary**
>
> First brainstorm session after 12 completed tasks. One new task created (t0014: Granite
> short-clip
> robustness + production fit assessment) and six suggestions rejected for eliminated models
> or
> superseded experiments. The session established that the next priority is validating Granite
> Speech
> 4.1 2B as a production replacement for Parakeet TDT 0.6b-v3, with explicit focus on
> short-clip
> robustness using real production streaming simulation.
>
> **Session Overview**
>
> Date: 2026-06-29. First brainstorm session for the project. Prompted by completion of all 12
> benchmark and research tasks, particularly t0012 which established a three-model production
> streaming comparison. The researcher identified short-clip failures as the original reason
> Whisper
> was replaced by Parakeet in production, and requested a focused validation task.
>
> **Decisions**
>
> 1. **Create t0014** — Granite Short-Clip Robustness Validation + Production Fit Assessment.
>    Uses

</details>

<details>
<summary>✅ 0012 — <strong>Production Streaming Benchmark — Whisper, Parakeet,
Granite on Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0012_whisper_parakeet_granite_streaming` |
| **Status** | completed |
| **Effective date** | 2026-06-29 |
| **Dependencies** | [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md), [`t0011_streaming_stt_benchmark`](../../../overview/tasks/task_pages/t0011_streaming_stt_benchmark.md) |
| **Expected assets** | 6 predictions |
| **Source suggestion** | — |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/), [`experiment-run`](../../../meta/task_types/experiment-run/) |
| **Start time** | 2026-06-26T16:37:03Z |
| **End time** | 2026-06-29T00:00:00Z |
| **Task page** | [Production Streaming Benchmark — Whisper, Parakeet, Granite on Gold-92](../../../overview/tasks/task_pages/t0012_whisper_parakeet_granite_streaming.md) |
| **Task folder** | [`t0012_whisper_parakeet_granite_streaming/`](../../../tasks/t0012_whisper_parakeet_granite_streaming/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0012_whisper_parakeet_granite_streaming/results/results_detailed.md) |

# t0012 — Three-Model Production Streaming Benchmark: Whisper, Parakeet, Granite

## Motivation

t0011 confirmed that Parakeet TDT 0.6b-v3 and Granite Speech 4.1 2B perform identically in
streaming and batch when using the accumulate-then-transcribe pattern. What remains unmeasured
is Whisper turbo — the current production STT model in brainpowa-realtime-api — on the gold-92
benchmark, and how all three models compare when each runs in its own true production
streaming mode. This task establishes a three-way apples-to-apples comparison where each model
is evaluated exactly as it runs in production.

The key research questions are:

1. What accuracy does Whisper turbo achieve on gold-92 in its production streaming mode
   (chunked re-transcribe with delta extraction)?
2. How does Whisper compare to Parakeet and Granite on entity accuracy, WER, and
   action-critical WER?
3. Does Whisper's chunked re-transcribe pattern degrade accuracy vs batch (re-transcribing the
   growing buffer at each chunk introduces more decoding passes)?
4. What is Whisper's time-to-first-delta — the latency from first audio chunk to first partial
   transcript?

## Scope

Three model runs on gold-92 (93 WAV clips, 16 kHz mono), each in its own production mode:

### Run 1 — Whisper turbo (streaming, production mode)

Mirrors `WhisperSTT.transcribe_stream()` in brainpowa-realtime-api exactly:

* Model: `faster-whisper`, model size `turbo`, `float16`, `cuda`
* Parameters: `beam_size=1`, `vad_filter=True`, `temperature=0.0`, `no_speech_threshold=0.6`
* Biasing: `initial_prompt` = comma-separated 31 domain vocab terms (same as
  `stt_initial_prompt` in brainpowa config)
* Streaming pattern: every 32 kB of accumulated PCM-16 audio, transcribe full buffer, extract
  delta (new words vs previous interim using word-level longest-common-prefix matching), yield
  delta; final transcribe on complete audio after `None` sentinel
* Latency: wall-clock from first chunk delivered to final transcript returned
* Extra metric: **time-to-first-delta** — wall-clock from first chunk to first non-empty delta
  yield (first partial result)

### Run 2 — Whisper turbo (batch baseline)

Same model and parameters as Run 1 but accumulate all audio, single `transcribe()` call.
Provides the batch baseline for Whisper to quantify the cost of chunked re-transcription.

### Run 3 — Parakeet TDT 0.6b-v3 (streaming, production mode)

Identical to t0011 Parakeet streaming run (accumulate-then-transcribe). Replicated here as a
direct comparison row alongside Whisper. Baselines from t0011 may be copied rather than
re-running if the server environment is unchanged.

* Model: NeMo parakeet-tdt-0.6b-v3 from `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`
* Biasing: GPU-PB phrase boosting, alpha=1.0, 66 casing variants of 31 domain terms
* Pattern: accumulate all 32 kB chunks → reconstruct float32 → single `model.transcribe()`

### Run 4 — Granite Speech 4.1 2B (streaming, production mode)

Identical to t0011 Granite streaming run. Replicated here as a direct comparison row.

* Model: ibm-granite/granite-speech-4.1-2b from
  `/home/azureuser/granite-model/granite-speech-4.1-2b`
* Biasing: keyword prompt injection — `"transcribe the speech to text. Keywords: Rezolve,
  ..."`
* Pattern: accumulate all 32 kB chunks → reconstruct float32 tensor → single model generate
  call

## Domain Vocabulary (31 terms)

Rezolve, brainpowa, NASDAQ, Selfridges, Harrods, Walmart, Macy's, Nordstrom, Bloomingdale's,
Sephora, Zara, H&M, Uniqlo, ASOS, Farfetch, NET-A-PORTER, Matches, Mytheresa, Browns, Liberty,
Harvey Nichols, Fenwick, John Lewis, Debenhams, Marks and Spencer, Next, River Island,
Topshop, ASOS, Boohoo, Pretty Little Thing.

## Metrics

All seven registered metrics computed for every run:

| Metric | All runs |
| --- | --- |
| Entity Accuracy (gold-92) | ✓ |
| Entity Accuracy — Domain Vocabulary | ✓ |
| Word Error Rate (gold-92) | ✓ |
| Action-Critical WER (gold-92) | ✓ |
| Intent Preservation (gold-92) | ✓ |
| Latency p50 (seconds) | ✓ |
| Wrong Action Rate (gold-92) | ✓ |

Additional metrics (not registered, reported in results):

* Latency p95, p99 (all runs)
* Time-to-first-delta (Run 1 — Whisper streaming only)
* Whisper streaming vs batch delta (Run 1 − Run 2) for all accuracy metrics
* Delta vs t0011 for Parakeet and Granite (Runs 3–4 vs t0011; should be ~0 pp)

## Baselines

* Parakeet batch: t0009 (`entity_accuracy_gold92=0.232`, `wer_gold92=0.152`,
  `action_critical_wer_gold92=0.335`, `latency_p50_seconds=0.038`)
* Parakeet streaming: t0011 (`entity_accuracy_gold92=0.2315`, `latency_p50_seconds=0.041`)
* Granite batch: t0007 (`entity_accuracy_gold92=0.4109`, `wer_gold92=0.0883`,
  `action_critical_wer_gold92=0.0759`, `latency_p50_seconds=0.248`)
* Granite streaming: t0011 (`entity_accuracy_gold92=0.4109`, `latency_p50_seconds=0.250`)
* Whisper batch: established in Run 2 of this task

## Compute and Budget

Machine: Azure H100 NVL (`gpu-azure`, `azureuser@llm-t1-nc80`, conda env `stt`).

| Run | Est. wall-clock | Notes |
| --- | --- | --- |
| Run 1 — Whisper streaming | ~10 min | O(N²) decode passes; 93 clips × avg 6 chunks |
| Run 2 — Whisper batch | ~5 min | Single pass per clip |
| Run 3 — Parakeet streaming | ~2 min | Can reuse t0011 JSONL |
| Run 4 — Granite streaming | ~4 min | Can reuse t0011 JSONL |

Estimated cost: Azure H100 NVL reserved instance — effectively $0 incremental for ~20 min GPU
time.

## Data Handling

* Audio: gold-92 WAV files from `tasks/t0001_stt_benchmark/` (DVC-tracked). Run `dvc pull`
  before starting.
* Intermediate predictions saved to `data/` as JSONL (one line per clip):
  `whisper_streaming_transcripts.jsonl`, `whisper_batch_transcripts.jsonl`,
  `parakeet_streaming_transcripts.jsonl`, `granite_streaming_transcripts.jsonl`
* All predictions use same clip ordering and clip IDs as prior tasks for comparability.

## Assets

Four predictions assets:

1. `whisper-turbo-gold92-streaming` — Whisper turbo production streaming predictions (Run 1)
2. `whisper-turbo-gold92-batch` — Whisper turbo batch predictions (Run 2)
3. `parakeet-tdt-0.6b-v3-gold92-streaming-biased` — Parakeet streaming (Run 3, mirrors t0011)
4. `granite-speech-4.1-2b-gold92-streaming-biased` — Granite streaming (Run 4, mirrors t0011)

## Charts

All charts saved to `results/images/` and embedded in `results_detailed.md`.

1. **Three-model accuracy comparison** — grouped bar chart, x-axis: model×mode, y-axis: %,
   panels: EA, EA_DV, WER. Answers: which model is most accurate in production streaming mode?
2. **Whisper streaming vs batch delta** — bar chart, x-axis: metric, y-axis: pp delta.
   Answers: does chunked re-transcription hurt Whisper accuracy?
3. **Latency distribution** — grouped bar chart p50/p95/p99 for all four runs. Answers: which
   model is fastest in production mode?
4. **Time-to-first-delta (Whisper)** — histogram of TTFD across 93 clips. Answers: how quickly
   does Whisper produce its first partial result?

## Key Questions

1. Does Whisper turbo match or exceed Granite Speech 4.1 2B on entity accuracy and
   action-critical WER in production streaming mode?
2. Does Whisper's chunked re-transcribe pattern degrade accuracy vs single-pass batch by more
   than 2 pp on any metric?
3. Is Whisper's time-to-first-delta under 1 second for ≥90% of clips (one chunk at 32 kB ≈ 1
   s)?

## Verification Criteria

* All four runs complete on 93/93 clips (or ≥90/93 with explicit note on failures).
* Parakeet and Granite deltas vs t0011 < 1 pp on all accuracy metrics (environment stability
  check).
* `metrics.json` written with all registered metrics for all four runs.
* All four charts generated and embedded in `results_detailed.md`.

</details>

<details>
<summary>✅ 0011 — <strong>Streaming STT Benchmark — Parakeet TDT 0.6b-v3 vs Granite
Speech 4.1 2B (biased)</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0011_streaming_stt_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-26 |
| **Dependencies** | [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md), [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | `S-0005-05` |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/), [`experiment-run`](../../../meta/task_types/experiment-run/) |
| **Start time** | 2026-06-26T09:00:00Z |
| **End time** | 2026-06-26T13:30:00Z |
| **Step progress** | 3/3 |
| **Task page** | [Streaming STT Benchmark — Parakeet TDT 0.6b-v3 vs Granite Speech 4.1 2B (biased)](../../../overview/tasks/task_pages/t0011_streaming_stt_benchmark.md) |
| **Task folder** | [`t0011_streaming_stt_benchmark/`](../../../tasks/t0011_streaming_stt_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0011_streaming_stt_benchmark/results/results_detailed.md) |

# Streaming STT Benchmark — Parakeet TDT 0.6b-v3 vs Granite Speech 4.1 2B (biased)

## Motivation

Production brainpowa-realtime-api does not deliver audio in batch — it streams PCM chunks over
a WebSocket at `stream_interval_bytes = 32000` (~1 s at 16 kHz mono), feeds them into an STT
adapter, and expects a transcription on a None sentinel. Tasks t0007 and t0009 measured both
models in pure-batch mode (full WAV loaded at once). This task answers whether the streaming
delivery pattern changes accuracy or latency relative to those batch baselines, and which
model is the better production fit under realistic conditions.

Key research questions:

1. Does chunked streaming delivery degrade entity accuracy vs. batch for Parakeet (biased)?
2. Does chunked streaming delivery degrade entity accuracy vs. batch for Granite 4.1 2B
   (biased)?
3. Which model achieves lower latency-to-final-transcript under streaming conditions (p50 /
   p95)?
4. Does the streaming gap (batch minus streaming entity accuracy) differ between the two
   models?

## Scope

Two runs on gold-92 (93 WAV clips):

* **Run A — Parakeet TDT 0.6b-v3 (biased, streaming)**: NeMo GPU-PB phrase boosting identical
  to brainpowa production (`stt_initial_prompt` → comma-split → NeMo `boosting_phrases`).
  Audio fed as 32000-byte PCM chunks; model accumulates until None sentinel.
* **Run B — Granite Speech 4.1 2B (biased, streaming)**: keyword prompt injection (`"Keywords:
  kw1, kw2, ..."` prefix) identical to t0007 best variant. Same chunking pattern as Run A.

No partial / intermediate transcription required — the streaming simulation tests the latency
of the full-segment accumulate-then-transcribe pattern (same as the production STTAdapter base
class `transcribe_stream()` default implementation).

## Approach

### Streaming Simulation

Read each gold-92 WAV at 16 kHz mono PCM, split into 32000-byte frames (exactly matching
`stt_stream_interval_bytes` from brainpowa config). Deliver frames sequentially with no sleep
(wall-clock simulation of the transport without network jitter). Send a None sentinel after
the last frame to trigger final transcription. Measure:

* `t_first_chunk` — time the first frame is submitted
* `t_transcript` — time the transcript is returned
* `latency = t_transcript - t_first_chunk`

### Biasing configuration

* **Parakeet**: load the canonical keyword list from
  `tasks/t0009_parakeet_production_baseline/` (same entity vocab used in production). Convert
  to NeMo `boosting_phrases` via comma-split of `stt_initial_prompt`.
* **Granite**: use the `"Keywords: ..."` prompt prefix established in t0007 (kw-biased
  variant, which was the best-performing configuration).

### Compute

Single run on the Azure H100 NVL server (`gpu-azure`, alias `azureuser@llm-t1-nc80`). Load
only one model at a time to avoid VRAM contention (Parakeet ~2 GB, Granite BF16 ~4 GB — both
fit sequentially). Estimated wall-clock: 15–20 min per run (93 clips × ~10 s audio ×
overhead).

### Budget

* Azure H100 NVL: ~$3/hr × 1 hr = ~$3 total
* No external API calls

## Runs

| Run | Model | Biasing | Mode |
| --- | --- | --- | --- |
| A | Parakeet TDT 0.6b-v3 | GPU-PB phrase boosting | streaming (32 kB chunks) |
| B | Granite Speech 4.1 2B | keyword prompt injection | streaming (32 kB chunks) |

Both runs use the same gold-92 clips and keyword vocabulary to ensure comparability.

## Metrics

Compute all registered project metrics for every run:

* `entity_accuracy_gold92`
* `entity_accuracy_domain_vocab`
* `wer_gold92`
* `action_critical_wer_gold92`
* `intent_preservation_gold92`
* `latency_p50_seconds`
* `wrong_action_rate_gold92`

Additionally compute `latency_p95_seconds` and `latency_p99_seconds` for latency distribution
analysis (not registered metrics, reported in results tables only).

Efficiency metrics:

* `efficiency_inference_time_per_item_seconds` — mean transcript latency per clip
* `efficiency_inference_cost_per_item_usd` — H100 hourly rate ÷ clips per hour

## Comparison Baselines

| Baseline | Source | Notes |
| --- | --- | --- |
| Parakeet TDT 0.6b-v3 batch (biased) | t0009 | Same keyword vocab, batch mode |
| Granite Speech 4.1 2B kw-biased batch | t0007 | Same keyword list, batch mode |

Report streaming vs. batch delta for each metric as `Δ = streaming − batch`.

## Expected Outputs

### Charts (saved to `results/images/`)

1. `chart_accuracy_streaming_vs_batch.png` — grouped bar chart, entity accuracy and WER for
   each model × mode (batch vs. streaming); shows whether streaming degrades accuracy.
2. `chart_latency_distribution.png` — p50 / p95 / p99 latency bars for Run A and Run B side by
   side; reference line at 800 ms SLA and 200 ms target.
3. `chart_streaming_delta.png` — delta bars (streaming minus batch) per metric for both
   models; green = no regression, red = regression.

All charts embedded in `results/results_detailed.md`.

### Tables

* Per-run metric table (rows = metrics, columns = Run A / Run B / batch baselines / deltas)
* Per-clip latency table (clip name, Run A latency ms, Run B latency ms) for reproducibility

## Data Handling

* Intermediate chunked PCM data is generated on-the-fly from gold-92 WAVs — no new data files
  written to disk.
* Per-clip transcript predictions saved to `data/predictions_streaming_parakeet.jsonl` and
  `data/predictions_streaming_granite.jsonl` (DVC-tracked).
* Per-clip latency log saved to `data/latency_log.jsonl` (DVC-tracked).

## Dependencies

* **t0009_parakeet_production_baseline** — provides the production keyword vocabulary and
  batch accuracy baselines for Parakeet TDT 0.6b-v3.
* **t0007_ibm_granite_4_1_benchmark** — provides the batch accuracy baselines and optimal
  biasing configuration for Granite Speech 4.1 2B.

## Verification Criteria

* All 93 gold-92 clips processed in both runs with no errors.
* Streaming entity accuracy for Parakeet within ±3 pp of t0009 batch result (expected
  near-parity since accumulate-then-transcribe is equivalent to batch at segment level).
* Granite streaming entity accuracy within ±3 pp of t0007 kw-biased batch result.
* Latency p50 for both models below 800 ms SLA.
* All charts generated and embedded in `results_detailed.md`.
* `verify_task_file.py` passes with 0 errors.

**Results summary:**

> **t0011 — Streaming STT Benchmark: Results Summary**
>
> Streaming delivery (32 kB PCM chunks, accumulate-then-transcribe) produces results
> statistically
> identical to batch on both models: all accuracy deltas are below 0.1 pp and latency overhead
> is
> under 4 ms. Granite Speech 4.1 2B (biased) leads on all accuracy metrics under streaming
> (EA 41.1%, AC-WER 7.6%), while Parakeet TDT 0.6b-v3 (biased) retains a 6× latency advantage
> (41 ms vs 250 ms p50).
>
> **Key Numbers**
>
> | Model | EA | EA\_DV | WER | AC-WER | IP | Lat p50 |
> | --- | --- | --- | --- | --- | --- | --- |
> | Parakeet biased — batch (t0009) | 23.2% | 33.3% | 15.2% | 33.5% | 87.1% | 38 ms |
> | Granite 4.1 2B biased — batch (t0007) | 40.2% | 98.6% | 8.8% | 8.2% | 92.5% | 248 ms |
> | **Parakeet biased — streaming (t0011)** | **23.1%** | **33.3%** | **15.2%** | **33.5%** | **87.1%** | **41 ms** |
> | **Granite 4.1 2B biased — streaming (t0011)** | **41.1%** | **97.1%** | **8.8%** | **7.6%** | **93.6%** | **250 ms** |
>
> **Streaming vs Batch Delta**
>
> | Model | ΔEA | ΔEA\_DV | ΔWER | ΔAC-WER | ΔIP | ΔLat p50 |

</details>

<details>
<summary>✅ 0010 — <strong>Benchmark FunASR SeACo-Paraformer on Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0010_funasr_paraformer_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-25 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0007_ibm_granite_4_1_benchmark`](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md), [`t0009_parakeet_production_baseline`](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | `S-0005-02` |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Start time** | 2026-06-25T00:00:00Z |
| **End time** | 2026-06-25T20:00:00Z |
| **Step progress** | 3/3 |
| **Task page** | [Benchmark FunASR SeACo-Paraformer on Gold-92](../../../overview/tasks/task_pages/t0010_funasr_paraformer_benchmark.md) |
| **Task folder** | [`t0010_funasr_paraformer_benchmark/`](../../../tasks/t0010_funasr_paraformer_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0010_funasr_paraformer_benchmark/results/results_detailed.md) |

# Benchmark FunASR SeACo-Paraformer on Gold-92

## Motivation

Task t0005 (STT model survey) identified FunASR SeACo-Paraformer-en as a candidate for
contextual-biasing benchmarking. SeACo-Paraformer is a variant of the Paraformer architecture
with a dedicated contextual biasing module (SeACo — Selective Attention with Contextual
Objects), designed to improve recall of domain-specific vocabulary. The English variant
(`iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020`) was identified as a potential
lower-latency alternative to Granite biased, given Paraformer's CTC-based architecture.

The task was also motivated by suggestion S-0005-02 from task t0005's suggestion generation.

## Goal

Run FunASR SeACo-Paraformer-en on all 93 gold-92 clips in two configurations:

1. **Batch (no biasing)** — standard Paraformer inference without contextual biasing
2. **SeACo biased** — SeACo contextual biasing with Rezolve domain vocabulary

Compute entity accuracy, domain-vocabulary accuracy, WER, action-critical WER, intent
preservation, and latency p50/p95/p99. Compare against Parakeet production (t0009) and Granite
biased (t0007) baselines.

## Success Criteria

- All 93 clips transcribed in both configurations
- metrics.json written with both variants
- Prediction assets registered for DVC tracking
- Results summary and detailed report completed

**Results summary:**

> ---
> spec_version: "1"
> task_id: "t0010_funasr_paraformer_benchmark"
> date_completed: "2026-06-25"
> ---
> **Results Summary — FunASR SeACo-Paraformer Benchmark on Gold-92**
>
> **Summary**
>
> FunASR SeACo-Paraformer-en (iic/speech_seaco_paraformer_asr_nat-en-16k-common-vocab10020)
> was
> benchmarked on all 93 gold-92 clips in batch and contextual-biased modes. The model produces
> near-random English-sounding tokens when given Rezolve's investor-relations English speech:
> WER=122.7% (batch), WER=122.2% (biased). WER exceeding 100% indicates the model's hypotheses
> contain more word errors than reference words — effectively complete transcription failure.
> Entity accuracy is 2.2% in both variants, and domain-vocabulary accuracy is 0.0%. SeACo
> contextual biasing has zero effect on any accuracy metric.
>
> The root cause is that Paraformer was trained primarily on Mandarin Chinese speech data.
> The "en" variant's English capability is severely limited and cannot handle Rezolve's
> English voice-commerce speech. This model is not suitable for any English STT application

</details>

<details>
<summary>✅ 0009 — <strong>Parakeet TDT 0.6b-v3 Production Baseline on
Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0009_parakeet_production_baseline` |
| **Status** | completed |
| **Effective date** | 2026-06-25 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | — |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Start time** | 2026-06-25T00:00:00Z |
| **End time** | 2026-06-25T06:00:00Z |
| **Step progress** | 3/3 |
| **Task page** | [Parakeet TDT 0.6b-v3 Production Baseline on Gold-92](../../../overview/tasks/task_pages/t0009_parakeet_production_baseline.md) |
| **Task folder** | [`t0009_parakeet_production_baseline/`](../../../tasks/t0009_parakeet_production_baseline/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0009_parakeet_production_baseline/results/results_detailed.md) |

# Parakeet TDT 0.6b-v3 Production Baseline on Gold-92

## Motivation

Parakeet TDT 0.6b-v3 (NVIDIA) is the current production STT model deployed in brainpowa's
voice-commerce pipeline. Tasks t0006–t0010 all compare their benchmarked models against this
production system, making it essential to have directly comparable metrics computed with the
same evaluation harness.

Prior tasks (t0001–t0005) used Whisper large-v3 as the reference baseline. This task
establishes a second, more operationally relevant baseline using the actual production model,
so that benchmark results are interpretable in terms of real-world improvement potential.

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

**Results summary:**

> ---
> spec_version: "1"
> task_id: "t0009_parakeet_production_baseline"
> date_completed: "2026-06-25"
> ---
> **Results Summary — Parakeet TDT 0.6b-v3 Production Baseline on Gold-92**
>
> **Summary**
>
> Parakeet TDT 0.6b-v3 (NVIDIA, current Rezolve production model) was benchmarked on all 93
> gold-92 clips in unbiased and production-config (biased) modes. The production config
> achieves
> entity accuracy=23.2%, domain-vocabulary accuracy=33.3%, WER=15.2%, and action-critical
> WER=33.5% at p50 latency=38 ms. Keyword biasing in the production config provides negligible
> benefit over unbiased: ΔEA=−0.2 pp, ΔEA_DV=+1.4 pp, ΔWER=+0.1 pp.
>
> This baseline establishes the current production floor. All subsequent benchmark tasks
> (t0006–t0010) report their metrics relative to this result. The key finding is that the
> production model has very low entity accuracy (23.2%) and very high action-critical WER
> (33.5%),
> confirming significant headroom for improvement.
>

</details>

<details>
<summary>✅ 0008 — <strong>Benchmark Moonshine v2 on Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0008_moonshine_v2_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-25 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | — |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Start time** | 2026-06-25T08:30:15Z |
| **End time** | 2026-06-25T09:55:00Z |
| **Step progress** | 9/15 |
| **Key metrics** | ⚠️ Action-Critical WER (gold-92): **0.341772**, 📖 Entity Accuracy — Domain Vocabulary: **0.090909**, 🎯 Entity Accuracy (gold-92): **0.217029**, ✅ Intent Preservation (gold-92): **0.870968**, ⚡ Latency p50 (seconds): **0.2321**, 🚫 Wrong Action Rate (gold-92): **0.129032** |
| **Task page** | [Benchmark Moonshine v2 on Gold-92](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Task folder** | [`t0008_moonshine_v2_benchmark/`](../../../tasks/t0008_moonshine_v2_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0008_moonshine_v2_benchmark/results/results_detailed.md) |

# Benchmark Moonshine v2 on Gold-92

## Motivation

Task t0005 (STT model survey) ranked **Moonshine v2** as an **edge-deployment candidate** —
the only **CPU-only open-source STT model** in the survey:

- **No GPU required**: runs on CPU via OnnxRuntime; eliminates cloud infrastructure overhead
- **Ultra-low latency**: 50–258 ms per clip (Tiny/Small/Medium variants), well under 800 ms
  budget
- **Small model size**: 6× fewer parameters than Whisper large-v3; efficient memory footprint
- **5.3% WER**: competitive with Whisper turbo on general English; VoxPopuli (accented) WER
  not published
- **MIT license**: permissive, fully open-weight

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5%
domain entity accuracy** on gold-92 through vocabulary biasing. Moonshine's key limitation is
the **absence of native contextual biasing**. Instead, Moonshine must use external
shallow-fusion adapters (not yet implemented) to boost entity recall. This task establishes
Moonshine's baseline entity accuracy **without biasing** and assesses the integration
feasibility of an external biasing layer.

**Strategic value**: If entity accuracy without biasing is ≥ 46% (Whisper overall baseline)
and a shallow-fusion biasing adapter can be prototyped, Moonshine becomes a viable
**edge-deployment fallback** — low latency, no cloud GPU, minimal infrastructure. This is
especially valuable for devices with limited GPU access or offline deployment scenarios.

## Research Question

**What is Moonshine v2's entity accuracy and latency on gold-92 without native biasing, and is
an external shallow-fusion biasing layer feasible for improving entity recall toward the
Whisper baseline (94.5% domain vocab)?**

Secondary questions:

- How does Moonshine's WER compare to Whisper turbo on gold-92?
- What is Moonshine's action-critical WER (AC-WER) vs. the Whisper baseline (2.5%)?
- Can Moonshine achieve ≤ 200 ms p50 latency on local CPU (warm-up included)?
- Is Moonshine's latency degradation from cold-start to warmed-up inference acceptable for
  real-time voice commerce?

## Scope

### Runs

1. **Moonshine v2 Medium — Batch Mode (No Biasing)**
   - Model: `usefulsensors/moonshine` via HuggingFace (Medium variant, ~4.7M params)
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: default batch inference, OnnxRuntime CPU backend
   - Metrics: WER, entity accuracy (overall + domain vocab), intent preservation,
     action-critical WER, latency p50/p95/p99 (including cold-start warmup)

2. **Moonshine v2 Medium — Shallow Fusion (External Biasing Assessment)**
   - Model: same as above
   - Biasing vocabulary: identical 31 terms from t0004
   - Biasing method: external shallow-fusion adapter (NOT yet implemented; this run assesses
     feasibility and estimates integration effort)
   - Metrics: same as run 1 + feasibility verdict (can shallow fusion be integrated in
     reasonable time?)

### Comparators

**t0004 Baseline (Whisper large-v3 + initial_prompt):**

| Metric | Value |
| --- | --- |
| Entity accuracy (domain vocab) | 94.5% |
| Entity accuracy (overall) | 46.0% |
| WER | 8.5% |
| AC-WER | 2.5% |
| Intent preservation | 98.9% |
| Latency p50 | 6.66 s |

### Registered Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:

- Overall (93 clips)
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining 85 clips)

**Per run:**

- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds`
- `wrong_action_rate_gold92`

**Custom metrics:**

- Cold-start latency (first clip)
- Warm-up warmup latency (clips 2–5)
- Warmed latency (clips 6–93)
- Production subset entity accuracy (accented English, 8 clips)

### Shallow Fusion Feasibility Assessment

This is a qualitative research + prototyping subtask, not a separate benchmark run:

- Document shallow-fusion implementation approaches (speech-to-speech fusion, lattice
  rescoring, log-linear model, etc.)
- Identify 1–2 candidate open-source shallow-fusion libraries (e.g., `fuse-viterbi`,
  `kaldi-native-io`, custom PyTorch layer)
- Estimate implementation effort in hours
- Estimate latency overhead per clip (5–30 ms estimated)
- Write feasibility verdict: "viable for production", "needs research", or "infeasible within
  budget"

## Approach

### Setup

1. Install `moonshine-vad`, `onnxruntime`, `librosa` (CPU inference path)
2. Load gold-92 clips and ground-truth transcripts from t0001
3. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison
4. Prepare the 31-term domain vocabulary from t0004 for the biasing assessment

### Implementation Steps

1. **Run 1 (no biasing):** iterate over 93 gold-92 clips, run Moonshine batch transcription on
   CPU, collect predictions + per-clip wall-clock latency (track cold-start vs. warm-up
   separately)

2. **Run 2 (shallow fusion assessment):** research shallow-fusion libraries, write a
   shallow-fusion adapter prototype (or detailed design doc if time-constrained), estimate
   latency overhead and implementation effort, produce a feasibility report

3. **Metric computation:** WER (normalized Levenshtein), entity accuracy (substring match),
   domain vocab accuracy, AC-WER, intent preservation, latency p50/p95/p99; BCa bootstrap 95%
   confidence intervals on all accuracy metrics

4. **Stratification:** report all metrics on full set, production subset (8 accented clips),
   clean-voice subset

5. **Shallow fusion report:** document the feasibility verdict and effort estimate for
   downstream follow-up tasks

### Compute

**CPU:** Any modern multi-core CPU (Moonshine is OnnxRuntime CPU-native; no GPU required)\
**Budget estimate:** $0 (local compute only)

## Output Specification

### Prediction Assets (1–2 total)

1. `moonshine-v2-medium-gold92` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local,
     latency_ms}`
   - Format: JSONL

2. `moonshine-v2-medium-gold92-biasing-assessment` — shallow fusion prototype or design doc
   - Format: markdown + optional code snippets

### Results Files

- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  latency feasibility, shallow fusion verdict)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification,
  cold-start vs. warm-up analysis, shallow fusion feasibility report
- `results/metrics.json` — registered metrics (run 1 only; run 2 is assessment, not metrics)
- `results/costs.json` — `{"total_cost_usd": 0, "breakdown": {}}`
- `results/images/` — comparison bar charts:
  - Entity accuracy (domain vocab): Moonshine vs. Whisper baseline
  - WER: same comparison
  - AC-WER: same comparison
  - Latency distribution: cold-start, warm-up, warmed (histogram or violin plot)

### Key Questions (numbered, falsifiable)

1. **Entity accuracy (domain vocab) without biasing:** Does Moonshine ≥ 46% (Whisper overall
   baseline)?
   - Hypothesis: UNCERTAIN — Moonshine WER is competitive (5.3%), but entity accuracy without
     biasing may lag

2. **WER:** Is Moonshine ≤ 8.5% (Whisper baseline)?
   - Hypothesis: YES — 5.3% reported WER is below Whisper; gold-92 may be slightly higher

3. **Action-critical WER:** Does Moonshine AC-WER ≤ 2.5% (Whisper baseline)?
   - Hypothesis: UNCERTAIN — depends on entity-heavy vs. generic token distribution

4. **Latency:** Is Moonshine p50 ≤ 200 ms on local CPU after warm-up?
   - Hypothesis: YES — Medium variant ~80–150 ms reported; gold-92 segment lengths and local
     CPU speed TBD

5. **Cold-start latency:** Is first-clip latency acceptable for real-time UX?
   - Hypothesis: UNCERTAIN — cold-start may be 500+ ms; production would need pre-warming or
     caching

6. **Shallow fusion feasibility:** Can a shallow-fusion biasing adapter be integrated in <20
   hours of effort?
   - Hypothesis: YES — log-linear fusion or lattice rescoring are well-established;
     open-source tools exist

7. **Accented English (production subset):** Does Moonshine entity accuracy > Whisper on 8
   production clips?
   - Hypothesis: UNCERTAIN — no VoxPopuli (accented) WER data for Moonshine

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, entity
  annotations). Required before any inference can run.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results and the 31-term biasing
  vocabulary. Provides the comparison baseline and domain vocabulary for the shallow fusion
  assessment.

## Expected Assets

- `predictions` asset (count: 1–2) — Moonshine predictions on gold-92 (+ optional shallow
  fusion design/prototype)

## Budget

- **Estimated:** $0 (local CPU compute only)
- No cloud GPU, no paid inference APIs
- Shallow fusion research time budgeted within the task (estimate <3 hours for assessment)

## Success Criteria

1. All 93 clips transcribed successfully on local CPU
2. All registered metrics computed with valid BCa bootstrap confidence intervals
3. Entity accuracy (domain vocab) measured and compared to t0004 baseline (46.0% overall
   target)
4. Latency p50/p95/p99 measured with cold-start/warm-up breakdown
5. WER and AC-WER measured and compared to Whisper baseline
6. Shallow fusion assessment documented with feasibility verdict and effort estimate
7. Predictions asset created and verified
8. Results document includes side-by-side comparison vs. Whisper baseline and interpretation:
   - If entity accuracy ≥ 46% AND shallow fusion is feasible: Moonshine is viable edge
     fallback
   - If entity accuracy < 46% OR shallow fusion is not feasible: recommend follow-up direction
     or alternative (Paraformer, Granite with GPU)

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set, NEVER tune on)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline (WER,
  entity accuracy, 31-term domain vocabulary); defines comparison target and biasing
  vocabulary
- **t0005_stt_model_survey_brainpowa** — identified Moonshine v2 as edge-deployment candidate;
  documented CPU-only latency, WER, and biasing limitations
- **t0006_nemotron_3_5_benchmark** — parallel benchmark of Nemotron 3.5 (streaming native);
  results from t0006 + t0008 together should form the "streaming-capable fast" + "CPU-only
  low-cost" leg of the candidacy evaluation
- **t0007_ibm_granite_4_1_benchmark** — parallel benchmark of Granite 4.1 (highest WER);
  results from all three (t0006, t0007, t0008) form a comprehensive 3-way comparison
- **brainpowa-realtime-api** integration target — Moonshine findings will inform STTAdapter
  brick implementation (OnnxRuntime CPU backend + optional shallow-fusion adapter)

**Results summary:**

> ---
> spec_version: "1"
> task_id: "t0008_moonshine_v2_benchmark"
> date_completed: "2026-06-25"
> ---
> **Results Summary — Moonshine v2 Benchmark on Gold-92**
>
> **Summary**
>
> Moonshine v2 Medium (UsefulSensors/moonshine-streaming-medium, 266M params, CPU) was
> benchmarked on
> all 93 gold-92 clips. It achieves WER=16.6% and entity accuracy (domain vocab) of 9.1%, both
> significantly worse than the Whisper large-v3 baseline (8.5% WER, 94.5% domain-vocab entity
> accuracy). Warmed latency p50 of 233ms is close to the 200ms target but does not meet it;
> cold-start
> latency is 1.33s. Moonshine is not production-ready for Rezolve's voice commerce use case
> without
> vocabulary biasing, but shallow-fusion is feasible (~15–25 hours effort, verdict: "needs
> research").
>
> **Metrics**
>
> - **wer_gold92**: 16.6% (BCa 95% CI: 14.8%–22.6%) vs. Whisper baseline 8.5% — 2x worse
> - **entity_accuracy_gold92**: 21.7% (BCa 95% CI: 15.0%–29.5%) vs. Whisper 46.0% — 24pp below

</details>

<details>
<summary>✅ 0007 — <strong>Benchmark IBM Granite Speech 4.1 2B on Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0007_ibm_granite_4_1_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-25 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | `S-0005-01` |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Start time** | 2026-06-25T07:29:50Z |
| **Step progress** | 3/3 |
| **Task page** | [Benchmark IBM Granite Speech 4.1 2B on Gold-92](../../../overview/tasks/task_pages/t0007_ibm_granite_4_1_benchmark.md) |
| **Task folder** | [`t0007_ibm_granite_4_1_benchmark/`](../../../tasks/t0007_ibm_granite_4_1_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0007_ibm_granite_4_1_benchmark/results/results_detailed.md) |

# Benchmark IBM Granite Speech 4.1 2B on Gold-92

## Motivation

Task t0005 (STT model survey) ranked **IBM Granite Speech 4.1 2B** as the **#1 primary
benchmark candidate** from a field of 20+ open-source STT models:

- Ranks **#1 on the Hugging Face Open ASR Leaderboard** (5.33% mean WER, April 2026)
- Native **keyword biasing** with published F1 metrics — shallow-fusion mechanism for domain
  vocabulary injection (brands, product names, SKUs)
- Estimated **100–200 ms TTFT** in batch mode — within the 800 ms voice-to-action budget for
  short-segment inference
- **Apache 2.0** license; self-hostable via HuggingFace Transformers; ~6–8 GB VRAM

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5%
domain entity accuracy** and **2.5% action-critical WER** on gold-92 using prompt-injection
biasing alone. Granite's native keyword biasing and best-in-class WER position it as a
credible candidate to exceed that entity accuracy with lower overall WER.

**Key caveat:** Granite 4.1 is batch-only by default (non-autoregressive decoder, no native
streaming path). A non-autoregressive (NAR) variant exists and may achieve sub-100 ms latency
on short segments. Streaming capability must be assessed during implementation; if Granite
requires full-segment buffering before decoding, it cannot satisfy the brainpowa
`transcribe_stream` interface without a buffering shim and will be disqualified for the
primary streaming path (though still valuable as a batch/fallback transcriber).

This task validates Granite's entity accuracy and latency on gold-92 and determines whether it
is viable as a production STTAdapter brick replacement or a high-accuracy batch-mode fallback.

## Research Question

**Can IBM Granite Speech 4.1 2B, with native keyword biasing, match or exceed Whisper large-v3
+ initial_prompt entity accuracy (94.5% domain vocab) while achieving ≤ 200 ms p50 per-segment
latency in batch mode on the gold-92 investor-relations domain?**

Secondary questions:

- What is Granite's action-critical WER (AC-WER) vs. the Whisper baseline (2.5%)?
- Does Granite's keyword biasing outperform Whisper's initial_prompt biasing on accented
  English clips (production subset, 8 clips)?
- Is Granite viable for `transcribe_stream` — does a streaming or low-latency incremental path
  exist?

## Scope

### Runs

1. **Granite 4.1 2B — Batch Mode, No Biasing**
   - Model: `ibm-granite/granite-speech-4.1-2b` via HuggingFace Transformers
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: default batch inference, no keyword list
   - Metrics: WER, entity accuracy (overall + domain vocab), intent preservation,
     action-critical WER, latency p50

2. **Granite 4.1 2B — Batch Mode with Keyword Biasing**
   - Model: same as above
   - Keyword vocabulary: identical 31 terms from t0004 (Rezolve, brainpowa, Shopify Plus,
     Adobe Commerce, Salesforce Commerce Cloud, AI Foundry, E-commerce, conversational AI,
     product recommendation, voice AI, ASR, NLU, entity recognition, intent detection, product
     catalog, SKU, brand name, model number, price point, inventory, fulfillment, customer
     service, support, shopping assistant, voice assistant, smart speaker, multi-modal,
     omnichannel, cross-channel, real-time, low-latency)
   - Biasing mechanism: native Granite keyword biasing API (shallow fusion at beam-search
     time)
   - Metrics: same as batch + keyword-biasing gain (Δ entity accuracy, Δ WER vs. no-biasing
     run)

### Comparator

**t0004 Baseline (Whisper large-v3 + initial_prompt):**

| Metric | Value |
| --- | --- |
| Entity accuracy (domain vocab) | 94.5% |
| Entity accuracy (overall) | 46.0% |
| WER | 8.5% |
| AC-WER | 2.5% |
| Intent preservation | 98.9% |
| Latency p50 | 6.66 s |

### Registered Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:

- Overall (93 clips)
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining 85 clips)

**Per run:**

- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds`
- `wrong_action_rate_gold92`

**Custom metrics:**

- Keyword-biasing gain: Δ entity accuracy (biased vs. unbiased)
- Keyword-biasing gain: Δ WER (biased vs. unbiased)
- Production subset entity accuracy (accented English, 8 clips)
- Latency feasibility: is p50 < 200 ms per segment achievable?

### Streaming Assessment

As part of run 1 setup, document:

- Whether the HuggingFace Granite API exposes a streaming decode path
- Whether a NAR (non-autoregressive) model variant is available and what its latency profile
  is
- Whether a buffering shim could wrap Granite for `transcribe_stream` compatibility at
  acceptable latency overhead

This assessment is qualitative; it does not require a separate benchmark run.

## Approach

### Setup

1. Install `transformers` + `torch` (HuggingFace Transformers inference path)
2. Load `ibm-granite/granite-speech-4.1-2b` weights (~6–8 GB VRAM; A100 or H100 recommended)
3. Load gold-92 clips and ground-truth transcripts from t0001
4. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison

### Implementation Steps

1. **Baseline inference (no biasing):** iterate over 93 gold-92 clips, run Granite batch
   transcription, collect predictions + per-clip wall-clock latency
2. **Keyword-biased inference:** same 93 clips with 31-term domain vocabulary active via
   Granite keyword biasing API; collect predictions + latency
3. **Metric computation:** WER (normalized Levenshtein), entity accuracy (substring match on
   annotated entity spans), domain vocab accuracy, AC-WER, intent preservation, latency
   p50/p95/p99; BCa bootstrap 95% confidence intervals on all accuracy metrics
4. **Stratification:** report all metrics on full set, production subset (8 accented clips),
   clean-voice subset
5. **Streaming assessment:** document streaming / NAR path availability (see Scope above)

### Compute

**GPU:** A100 or H100 (6–8 GB VRAM; 93 clips ≈ seconds of inference)\ **Budget estimate:**
$3–8 USD

| Component | Cost |
| --- | --- |
| A100 GPU time, ~1 hour setup | $1–2 |
| 2 inference runs × ~30 s each | negligible |
| Metric computation + charting | ~5 min |
| **Total** | **$3–8** |

## Output Specification

### Prediction Assets (2 total)

1. `granite-4.1-2b-gold92-batch` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local,
     latency_ms}`
   - Format: CSV or JSONL

2. `granite-4.1-2b-gold92-keyword-biased` — batch mode with keyword biasing
   - Same schema

### Results Files

- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  keyword-biasing gain, latency feasibility verdict)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification by
  subset, streaming assessment, limitations
- `results/metrics.json` — registered metrics per variant
- `results/images/` — comparison bar charts:
  - Entity accuracy (domain vocab): Granite no-bias vs. Granite biased vs. Whisper baseline
  - WER: same three configurations
  - AC-WER: same three configurations
  - Latency p50: Granite batch vs. Whisper batch (and Nemotron streaming when t0006 completes)

### Key Questions (numbered, falsifiable)

1. **Entity accuracy (domain vocab):** Does Granite keyword-biased ≥ 94.5% (Whisper baseline)?
   - Hypothesis: YES — #1 WER + native keyword biasing should match or exceed initial_prompt
     biasing

2. **Overall entity accuracy:** Does Granite keyword-biased ≥ 46.0% (Whisper baseline)?
   - Hypothesis: YES — lower WER should generalize to higher overall entity recall

3. **Keyword-biasing gain:** Does keyword biasing improve entity accuracy over no-biasing run?
   - Hypothesis: YES — native shallow fusion mechanism should lift domain vocab precision

4. **Action-critical WER:** Does Granite keyword-biased AC-WER ≤ 2.5% (Whisper baseline)?
   - Hypothesis: YES — best-in-class WER + entity-focused biasing should reduce action errors

5. **Latency feasibility:** Is Granite p50 ≤ 200 ms per segment?
   - Hypothesis: UNCERTAIN — 100–200 ms TTFT reported in t0005 survey; actual wall-clock on
     gold-92 segment lengths must be measured; NAR variant may be needed to hit target

6. **Accented English (production subset):** Does Granite keyword-biased entity accuracy >
   Whisper on 8 production clips?
   - Hypothesis: UNCERTAIN — Granite WER advantage may not hold for accented speech without
     accented-English fine-tuning data

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, entity
  annotations). Required before any inference can run.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results (WER, entity accuracy,
  intent preservation, 31-term biasing vocabulary). Provides the comparison baseline and the
  exact keyword list to use for run 2.

## Expected Assets

- `predictions` asset (count: 2) — batch and keyword-biased Granite 4.1 2B predictions on
  gold-92

## Budget

- **Estimated:** $3–8 USD
- GPU: A100 or H100 (~1 hour including setup); inference itself is negligible
- No paid data or external APIs

## Success Criteria

1. All 93 clips transcribed in both runs (no-biasing and keyword-biased)
2. All registered metrics computed with valid BCa bootstrap confidence intervals
3. Entity accuracy (domain vocab) measured and compared to t0004 baseline (94.5%)
4. Keyword-biasing gain quantified (Δ entity accuracy and Δ WER)
5. Latency p50 measured and feasibility vs. 200 ms target assessed
6. Streaming / NAR path assessed and documented
7. Predictions assets created and verified
8. Results document includes side-by-side comparison vs. Whisper baseline and interpretation:
   - If entity accuracy ≥ 94.5%: confirms Granite as viable production candidate
   - If entity accuracy < 94.5%: identifies gap and recommends fine-tuning direction or
     fallback
   - If latency > 200 ms: documents batch-only limitation and recommends NAR variant or
     buffering shim

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set, NEVER tune on)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline (WER,
  entity accuracy, 31-term domain vocabulary); defines comparison target
- **t0005_stt_model_survey_brainpowa** — identified Granite 4.1 2B as #1 benchmark candidate;
  documented keyword biasing mechanism, WER, VRAM footprint, and integration path
- **t0006_nemotron_3_5_benchmark** — parallel benchmark of Nemotron 3.5 (streaming native);
  Granite results should be compared with Nemotron results when both complete
- **S-0005-01** — source suggestion: "Benchmark IBM Granite Speech 4.1 2B on gold-92 for
  entity accuracy and latency"
- **brainpowa-realtime-api** integration target — Granite findings will inform STTAdapter
  brick implementation (HuggingFace Transformers backend + async wrapper)

**Results summary:**

> ---
> spec_version: "1"
> task_id: "t0007_ibm_granite_4_1_benchmark"
> date_completed: "2026-06-25"
> ---
> **Results Summary — IBM Granite Speech 4.1 2B Benchmark on Gold-92**
>
> **Summary**
>
> IBM Granite Speech 4.1 2B with keyword biasing achieves 40.2% overall entity accuracy and
> 98.5%
> domain-vocabulary entity accuracy on gold-92, matching Whisper's domain-vocab score (94.5%)
> and
> delivering 27× lower latency (248 ms vs. 6.66 s p50). Against the actual production baseline
> (Parakeet TDT 0.6b-v3, t0009), Granite biased is +73% better on overall entity accuracy
> (40.2% vs.
> 23.2%), +196% better on domain-vocab accuracy (98.5% vs. 33.3%), and −75% better on
> action-critical
> WER (8.2% vs. 33.5%), at the cost of 6.5× higher latency (248 ms vs. 38 ms p50). Keyword
> biasing is
> the decisive factor: unbiased Granite scores only 19.5% entity accuracy, while biasing
> raises it to
> 40.2% (+21 pp) and domain-vocab accuracy from 31.9% to 98.5% (+66.6 pp).
>
> **Metrics**
>

</details>

<details>
<summary>✅ 0006 — <strong>Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0006_nemotron_3_5_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-25 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md), [`t0004_vocabulary_biasing_experiment`](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | — |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Start time** | 2026-06-25T06:00:00Z |
| **End time** | 2026-06-25T12:00:00Z |
| **Step progress** | 3/3 |
| **Task page** | [Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92](../../../overview/tasks/task_pages/t0006_nemotron_3_5_benchmark.md) |
| **Task folder** | [`t0006_nemotron_3_5_benchmark/`](../../../tasks/t0006_nemotron_3_5_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0006_nemotron_3_5_benchmark/results/results_detailed.md) |

# Benchmark NVIDIA Nemotron 3.5 ASR on Gold-92

## Motivation

Task t0005 (STT model survey) identified NVIDIA Nemotron 3.5 ASR (June 2026) as a **TIER 1
primary benchmark candidate** — the only streaming-native STT model meeting all brainpowa
STTAdapter constraints:
- Native streaming with configurable chunks (80ms–1.12s), achieving <800ms p50 voice-to-action
  latency
- Published word-boosting mechanism for domain vocabulary (brands, products, SKUs)
- Self-hostable with Python async interface (NeMo + NVIDIA Riva NIM)
- 6.93% WER (batch), 7.91% WER (streaming, 1.12s chunks), 7.69% on accented English
  (VoxPopuli)

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5%
domain entity accuracy** and **2.5% action-critical WER** on gold-92 through vocabulary
biasing alone — without any model-level entity-aware mechanisms. Nemotron offers native word
boosting + domain fine-tuning recipes, positioning it as a credible candidate to **exceed or
match Whisper's entity accuracy while maintaining streaming real-time constraints** (critical
for voice commerce UX).

This task validates that hypothesis on the gold-92 held-out benchmark.

## Research Question

**Can NVIDIA Nemotron 3.5 ASR, with native word boosting, match or exceed Whisper large-v3 +
initial_prompt entity accuracy (94.5% domain vocab) while maintaining <800ms p50 latency in
streaming mode on the gold-92 investor-relations domain?**

Secondary questions:
- What is the accuracy degradation from batch to streaming (1.12s chunks) on Nemotron?
- Is Nemotron's action-critical WER (AC-WER) ≤ 5.1% (Whisper baseline)?
- Does word-boosted Nemotron outperform Whisper on accented English clips (production subset)?

## Scope

### Runs

1. **Nemotron 3.5 ASR — Batch Mode (Baseline)**
   - Model: `nvidia/nemotron-3.5-asr-streaming-0.6b` via NeMo
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: batch inference, no biasing, greedy search
   - Metric: WER, entity accuracy (overall, domain vocab), intent preservation, latency (N/A
     for batch)

2. **Nemotron 3.5 ASR — Streaming with Word Boosting**
   - Model: same as above, streaming mode
   - Chunk size: 1.12s (matches publish RTF benchmarks)
   - Word boosting vocabulary: identical 31 terms from t0004 (Rezolve, brainpowa, Shopify
     Plus, Adobe Commerce, Salesforce Commerce Cloud, AI Foundry, E-commerce, conversational
     AI, product recommendation, voice AI, ASR, NLU, entity recognition, intent detection,
     product catalog, SKU, brand name, model number, price point, inventory, fulfillment,
     customer service, support, shopping assistant, voice assistant, smart speaker,
     multi-modal, omnichannel, cross-channel, real-time, low-latency)
   - Metric: same as batch + latency p50/p95/p99 (ms), streaming degradation vs batch (Δ WER,
     Δ entity accuracy)

### Comparator

**t0004 Baseline (Whisper large-v3 + initial_prompt):**
- Entity accuracy (domain vocab): 94.5%
- Entity accuracy (overall): 46.0%
- WER: 8.5%
- AC-WER: 2.5%
- Intent preservation: 98.9%
- Latency: 6.66s (non-streaming)

### Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:
- Overall
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining)

**Registered metrics to compute:**
- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds` (streaming run only)

**Custom metrics for this task:**
- Streaming degradation: Δ WER (batch vs streaming)
- Streaming degradation: Δ entity accuracy (batch vs streaming)
- Production subset entity accuracy (accented English)
- Word-boosting gain: entity accuracy (boosted vs non-boosted)

## Approach

### Setup

1. Install NVIDIA NeMo + nemotron-3.5-asr-streaming-0.6b weights (HF Model Hub)
2. Load gold-92 clips and ground-truth transcripts from t0001
3. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison

### Implementation Steps (Batch Mode)

1. **Baseline inference (no biasing):**
   - Iterate over 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Run Nemotron batch transcription
   - Collect predictions + latency measurements

2. **Word-boosted inference:**
   - Same 93 clips with word-boosting vocabulary active (NeMo word_list parameter)
   - Collect predictions + latency

3. **Metric computation:**
   - WER (normalized Levenshtein distance, 0–100%)
   - Entity accuracy: substring match (is each entity from ground truth present in
     prediction?)
   - Domain vocab accuracy: entity accuracy on the 31-term boosting vocabulary only
   - Action-critical WER: WER on action-bearing tokens (entity spans, intents)
   - Intent preservation: does the predicted intent match the ground truth? (using same proxy
     as t0004)
   - Latency: wall-clock time per clip (ms)

4. **Stratification:**
   - Compute all metrics on: full set, production subset (8 accented clips), clean-voice
     subset
   - Report means + 95% binomial confidence intervals (BCa bootstrap as in t0002/t0004)

### Compute

**GPU:** H100 or A100 (Nemotron RTF = 258.9x on H100; 93 clips ~ 10–15 seconds wall time per
run) **Budget estimate:** $5–10 (2–3 hours H100 time, including setup + metric computation)

### Output Specification

**Predictions Assets (2 total):**

1. `nemotron-3.5-asr-gold92-batch` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local,
     latency_ms}`
   - Format: CSV or JSONL

2. `nemotron-3.5-asr-gold92-word-boosted` — streaming mode with word boosting
   - Same schema

**Results Files:**
- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  streaming degradation)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification by
  subset, limitations
- `results/metrics.json` — registered metrics per variant
- `results/images/` — comparison bar charts (entity accuracy, WER, AC-WER vs. t0004 baseline)

**Key Questions (numbered, falsifiable):**

1. **Entity accuracy (domain vocab):** Does Nemotron word-boosted ≥ 94.5% (Whisper baseline)?
   - Hypothesis: YES — Nemotron native word boosting should be comparable to or exceed
     initial_prompt biasing

2. **Overall entity accuracy:** Does Nemotron word-boosted ≥ 46.0% (Whisper baseline)?
   - Hypothesis: YES — native biasing mechanism should generalize

3. **Streaming degradation:** Is Δ WER (batch→streaming) < 2%?
   - Hypothesis: YES — published benchmarks show 0.98% degradation on speech; domain may be
     similar

4. **Action-critical WER:** Does Nemotron word-boosted AC-WER ≤ 5.1% (Whisper baseline)?
   - Hypothesis: YES — entity-focused biasing should benefit action-bearing tokens

5. **Accented English (production subset):** Does Nemotron word-boosted entity accuracy >
   Whisper on 8 production clips?
   - Hypothesis: UNCERTAIN — Nemotron VoxPopuli WER (7.69%) slightly above Whisper VoxPopuli
     baseline; domain boosting may tip the balance

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, annotations).
  This task must complete successfully before benchmarking can start.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results for comparison (WER,
  entity accuracy, intent preservation). Provides the metric definitions and baseline numbers.

## Expected Assets

- `predictions` asset (count: 2) — batch + word-boosted Nemotron predictions on gold-92

## Budget

- **Estimated:** $5–10 USD
- **Breakdown:**
  - H100 GPU time: ~2 hours @ $3–5/hr = $6–10
  - Inference: ~100ms/clip × 93 clips × 2 variants = ~20 seconds
  - Metric computation + charting: ~5 minutes
- **Assumption:** Cost varies with cloud provider (AWS, GCP, NVIDIA DGX); local GPU available
  (no cost) acceptable.

## Success Criteria

1. ✅ All 93 clips transcribed in both batch and streaming modes
2. ✅ All registered metrics computed with valid confidence intervals
3. ✅ Entity accuracy (domain vocab) measured and compared to t0004 baseline (94.5%)
4. ✅ Streaming degradation quantified (Δ WER batch→streaming)
5. ✅ Predictions assets created and verified
6. ✅ Results document includes side-by-side comparison vs. Whisper baseline + interpretation
   of findings
7. ✅ If entity accuracy ≥ 94.5%, task confirms Nemotron as viable production candidate; if <
   94.5%, task identifies entity-accuracy gap and recommends fine-tuning direction or fallback
   strategy

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline results
  (WER, entity accuracy, intent preservation, latency)
- **t0005_stt_model_survey_brainpowa** — identified Nemotron 3.5 as TIER 1 primary candidate;
  correction file added Nemotron findings with streaming latency constraints and word-boosting
  documentation
- **brainpowa-realtime-api** integration target — Nemotron findings will inform STTAdapter
  brick implementation (NeMo backend + async wrapper)

**Results summary:**

> ---
> spec_version: "1"
> task_id: "t0006_nemotron_3_5_benchmark"
> date_completed: "2026-06-25"
> ---
> **Results Summary — NVIDIA Nemotron 3.5 ASR Benchmark on Gold-92**
>
> **Summary**
>
> NVIDIA Nemotron 3.5 ASR was benchmarked on all 93 gold-92 clips in two configurations: batch
> (no biasing) and streaming with word boosting. Batch WER=17.6% is 2× worse than the Whisper
> large-v3 baseline (8.5%), and batch entity accuracy=24.7% is 21 pp below Whisper (46.0%).
> Word
> boosting actively degrades performance relative to batch: ΔEA=−6.0 pp, ΔWER=+2.3 pp,
> ΔEA_DV=−5.5 pp. Latency p50=0.72s is within the 800 ms voice-to-action budget but does not
> offer a meaningful advantage over Granite biased (248 ms).
>
> Nemotron 3.5 is not recommended for Rezolve production. Word boosting is the primary failure
> mode — the mechanism degrades rather than improves domain-vocabulary accuracy, suggesting
> the
> word-boosting API does not behave as documented for this domain. Without an effective
> biasing
> mechanism, the model cannot meet Rezolve's entity accuracy requirements.

</details>

<details>
<summary>✅ 0005 — <strong>STT Model Survey: Open-Source Candidates for the brainpowa
Pipeline</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0005_stt_model_survey_brainpowa` |
| **Status** | completed |
| **Effective date** | 2026-06-24 |
| **Dependencies** | — |
| **Expected assets** | — |
| **Source suggestion** | — |
| **Task types** | [`internet-research`](../../../meta/task_types/internet-research/) |
| **Start time** | 2026-06-24T10:48:13Z |
| **End time** | 2026-06-24T11:06:19Z |
| **Step progress** | 7/15 |
| **Task page** | [STT Model Survey: Open-Source Candidates for the brainpowa Pipeline](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Task folder** | [`t0005_stt_model_survey_brainpowa/`](../../../tasks/t0005_stt_model_survey_brainpowa/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0005_stt_model_survey_brainpowa/results/results_detailed.md) |

# STT Model Survey: Open-Source Candidates for the brainpowa Pipeline

## Motivation

Rezolve's voice-commerce assistant runs on the `brainpowa-realtime-api`, an OpenAI-compatible
realtime server with a pluggable STT brick. Production today uses Whisper Turbo (via
faster-whisper) with runtime context injection; the pipeline also ships Azure Speech and
NVIDIA Parakeet (`parakeet-tdt-0.6b-v3` via NeMo, the current default, which unlocks GPU
phrase-boosting / contextual biasing) plus omni-LLM transcriber modes (Qwen3-Omni).

The gold-92 benchmark (`t0001_stt_benchmark`) confirmed that the dominant failure mode is
**entity accuracy** — brand names, product names, and SKUs are mangled or dropped, pushing the
wrong-action rate above the 2% target. `t0003_literature_review_entity_stt` surveyed
*techniques* (contextual biasing, shallow fusion, entity-aware ASR, LLM post-correction) and
`t0004_vocabulary_biasing_experiment` tested initial-prompt biasing on Whisper. Those tasks
answered "what methods help"; they did **not** answer "which concrete, integratable model
should we run."

This task closes that gap: a structured survey of **open-source / open-weight STT models**
that could be dropped into the brainpowa STT brick as a candidate to improve entity accuracy
over the current production baseline. GPU-requiring models are explicitly in scope —
self-hosting on GPU is acceptable.

## Research Question

Which open-source / open-weight STT models (released or actively maintained, including recent
2025–2026 releases) are the best candidates to integrate as a brainpowa STT brick to improve
**entity accuracy** over the current production baseline under an **800 ms p50
voice-to-action** latency budget — weighed on contextual-biasing support, streaming
capability, GPU footprint, license, and English / accented-English accuracy?

This is **not** a generic "best STT models" listicle. Every candidate must be assessed against
our concrete integration interface and product constraints below. A model that tops a WER
leaderboard but cannot do contextual biasing or stream is a weaker fit than a slightly-worse
model that can.

## Constraints (the bar every candidate is measured against)

### Integration interface

The brainpowa STT brick is defined by the `STTAdapter` Protocol
(`src/brainpowa_realtime_api/pipeline/stt/base.py`):

* `async transcribe(pcm16_mono_bytes, *, options, session_id) -> TranscriptionResult(text,
  no_speech_prob, segment_count)` — mandatory.
* `async transcribe_stream(audio_queue) -> AsyncGenerator[(delta, result)]` — optional, for
  **true incremental** recognition. The default base implementation buffers the whole segment
  and calls `transcribe` once; only override-capable models give low-latency streaming UX.
* Input is **raw PCM-16 mono** at the configured sample rate. Must run as a self-hosted Python
  service brick (importable inference, not a closed cloud-only API).
* Existing providers for comparison: faster-whisper (`whisper turbo`), Azure Speech, and
  `nvidia/parakeet-tdt-0.6b-v3` via `nemo_toolkit[asr]`. Use these as the integration-effort
  and accuracy reference points.

### Product constraints

* Primary goal: improve entity accuracy (brands, products, SKUs) and intent preservation over
  the current production STT baseline.
* Latency: **< 800 ms p50** voice-to-action. STT is one stage of that budget, so per-segment
  STT latency / real-time-factor matters a lot.
* Language: **English, accented** (investor-relations domain in gold-92).
* Must support **contextual biasing / hotwords / initial_prompt** for domain vocabulary, and
  ideally streaming/incremental decoding for low latency.
* Open weights strongly preferred; permissive license (Apache-2.0 / MIT / CC-BY) is a plus,
  copyleft or non-commercial is a minus to flag.

## Scope

### Candidates to evaluate (not exhaustive)

* **NVIDIA Parakeet / Canary family** — Parakeet TDT/RNNT/CTC variants, Canary, FastConformer.
  Already partly integrated; establish the upgrade ceiling within this family.
* **Whisper variants** — large-v3, turbo, distil-whisper, whisper.cpp, WhisperX.
* **Moonshine** — fast English-focused streaming ASR.
* **Kyutai / Moshi STT** — streaming speech-to-text.
* **FunASR family** — Paraformer, SenseVoice.
* **Conformer / FastConformer** CTC/transducer baselines.
* **wav2vec2 / MMS**.
* **IBM Granite Speech**.
* **Microsoft Phi-4-multimodal** (audio).
* **Qwen-Omni / Qwen-Audio** (already referenced by the omni transcriber path).
* **Any newer 2025–2026 open ASR releases** surfaced during search.

### Per-candidate dimensions to record

For every shortlisted model, capture (mark "unknown / not reported" rather than guessing):

1. Model family, sizes available, parameter count.
2. License + weights availability (HF repo / GitHub), and any commercial-use restriction.
3. Streaming vs batch; native incremental decoding support (maps to `transcribe_stream`).
4. Contextual biasing / hotword / initial-prompt / phrase-boost support and the mechanism.
5. GPU / VRAM footprint and reported latency or real-time-factor (RTF) at a stated
   batch/segment size.
6. Reported WER (English + accented if available) and any **entity / keyword-recall** numbers.
7. Integration effort into the `STTAdapter` brick (existing Python inference path? NeMo / HF /
   ctranslate2? PCM-16 mono input handling?).
8. Fit verdict vs the current parakeet / whisper / Azure providers.

### Inclusions

* Open-source / open-weight models with self-hostable inference.
* GPU-requiring models (acceptable; record the footprint).
* English or multilingual-with-English-results models.

### Exclusions

* Closed cloud-only APIs with no downloadable weights (Azure, Google, AssemblyAI, etc.) —
  except as **named comparison baselines**, not candidates.
* Pure TTS / diarization / VAD-only systems.
* Models with no English results and no path to English use.

## Approach

Follow the `internet-research` task type guidelines.

### Search strategy

Define queries before searching; log every query + result count in `research/search_log.md`.
Cover at least these angles:

* Open ASR leaderboards — Hugging Face Open ASR Leaderboard, Papers-with-Code ASR/WER,
  Artificial Analysis speech-to-text.
* "contextual biasing" / "hotword" / "keyword boosting" + each model family.
* "streaming ASR" / "low latency" / "RTF" + each model family.
* 2025–2026 release announcements (NVIDIA, Kyutai, Useful Sensors/Moonshine, Alibaba FunASR,
  IBM, Microsoft, Qwen).
* GitHub repos + model cards for license, input format, and inference API.

**Sources**: official model cards / GitHub repos / docs (authoritative for license, API,
footprint); HF Open ASR Leaderboard (WER); arXiv (architecture + entity/biasing results);
independent benchmarks (cross-check, never sole source).

### Process

* Broad landscape pass first, then narrow per candidate.
* Record every URL immediately with date accessed, source org, and a one-line contribution
  note.
* Cross-reference accuracy/latency claims across ≥2 independent sources; flag single-source
  claims.
* Write `research/research_internet.md` incrementally, structured **by dimension/candidate**,
  not by search.

### Stopping criterion

Stop when the candidate set covers the families above plus any newer releases found, each
scored on all eight dimensions, and ≥3 candidates are ranked with enough evidence to justify a
follow-on benchmark task. Do not expand into technique re-surveys already covered by `t0003`.

## Expected Outputs

* `research/research_internet.md` — the survey, containing:
  * A **comparison table** (rows = candidate models, columns = the eight per-candidate
    dimensions).
  * A ranked **shortlist** (top 3–5) of candidates by fit to the brainpowa brick +
    entity-accuracy / latency goals, each with a one-paragraph rationale and source URLs.
  * An explicit comparison of the shortlist against the currently-integrated parakeet /
    whisper / Azure providers.
  * A short "recommended next experiment" note pointing at which 1–2 candidates merit a
    gold-92 benchmark run.
* `research/search_log.md` — every query and result count.

No model assets, datasets, or paper assets are required (`expected_assets: {}`). No model
training or paid compute beyond LLM / search usage; budget is low.

## Cross-References

* `t0001_stt_benchmark` — gold-92 held-out regression set; defines the entity-accuracy metric
  the candidates must eventually beat. **Never tune on gold-92.**
* `t0003_literature_review_entity_stt` — technique survey; this task supplies the concrete
  models that implement those techniques. Do not re-survey techniques.
* `t0004_vocabulary_biasing_experiment` — established initial-prompt biasing baseline on
  Whisper; informs the contextual-biasing dimension.
* Integration target: `brainpowa-realtime-api` STT brick
  (`src/brainpowa_realtime_api/pipeline/stt/`).

Dependencies are intentionally empty: this is internet research that can start without any
other task's concrete file output. The prior tasks above are motivation and context, not
blocking inputs.

**Results summary:**

> **Results Summary: STT Model Survey for brainpowa Pipeline**
>
> **Summary**
>
> Comprehensive internet research identified and ranked 20+ open-source/open-weight STT models
> suitable for integration as a brainpowa STTAdapter brick candidate. Top 3 shortlist: **IBM
> Granite
> 4.1 2B** (highest entity accuracy + latency fit), **FunASR Paraformer** (best
> entity-specific
> metrics), **Moonshine v2** (fastest, CPU-only). Research revealed entity-biasing capability
> gaps in
> standard Whisper/Canary and positioned Granite + Paraformer as primary next-step
> benchmarking
> candidates for gold-92 evaluation against current Whisper turbo + initial_prompt baseline.
>
> **Metrics**
>
> - **Models surveyed**: 20+ (15 detailed, 5 excluded with rationale)
> - **Search queries executed**: 13 structured queries with 50+ consulted sources
> - **Top candidates shortlisted**: 3 (Granite, Paraformer, Moonshine)
> - **Verified citations**: 20 sources with complete metadata, 4 papers identified for
>   download
> - **Entity-accuracy candidates**: 2 with native biasing (Granite, Paraformer)
> - **Latency-optimized candidates**: 2 under 800ms (Moonshine <300ms, Granite ~150ms)
>

</details>

<details>
<summary>✅ 0004 — <strong>Vocabulary Biasing Experiment — initial_prompt Impact
on Gold-92 Entity Accuracy</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0004_vocabulary_biasing_experiment` |
| **Status** | completed |
| **Effective date** | 2026-06-23 |
| **Dependencies** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Expected assets** | 3 predictions |
| **Source suggestion** | `S-0003-02` |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/), [`experiment-run`](../../../meta/task_types/experiment-run/), [`comparative-analysis`](../../../meta/task_types/comparative-analysis/) |
| **Start time** | 2026-06-23T13:39:58Z |
| **End time** | 2026-06-23T15:30:00Z |
| **Step progress** | 7/15 |
| **Key metrics** | ⚠️ Action-Critical WER (gold-92): **0.025316**, 📖 Entity Accuracy — Domain Vocabulary: **0.945455**, 🎯 Entity Accuracy (gold-92): **0.460145**, ✅ Intent Preservation (gold-92): **0.989247**, ⚡ Latency p50 (seconds): **0.0697** |
| **Task page** | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../../../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) |
| **Task folder** | [`t0004_vocabulary_biasing_experiment/`](../../../tasks/t0004_vocabulary_biasing_experiment/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0004_vocabulary_biasing_experiment/results/results_detailed.md) |

# Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy

## Motivation

t0002_baseline_evaluation established a sobering finding: Whisper large-v3 and Whisper turbo
both score **25.2% entity accuracy overall** and only **8.8% on production clips** (real
investor-relations call recordings). Crucially, this gap is model-size invariant — scaling
from turbo to large-v3 yields no entity accuracy gain. The bottleneck is that domain terms
(brand names, product names, people's names) are absent from Whisper's training distribution.

In production (brainpowa-realtime-api), the codebase already uses `STT_INITIAL_PROMPT` as a
vocabulary hint, populated by `get_voice_utterance_transcription_prompt()`. This function
returns a comma-separated list of 31 domain terms. However, the actual impact of this biasing
strategy on entity recognition has never been quantified against a held-out benchmark.

This task closes that gap by running a controlled ablation: identical evaluation conditions as
t0002, with the only variable being the presence or absence of the 31-term `initial_prompt`.
The results will tell us whether the production biasing is effective and by how much, and will
identify which domain terms remain problematic even after biasing.

## Domain Vocabulary List

The exact 31 terms used in production (verbatim from
`get_voice_utterance_transcription_prompt()`):

> Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
> GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations, Dan
> Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee, Mark Turner,
> Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith, Justin King,
> Christian Angermayer

This string is passed verbatim as the `initial_prompt` parameter to faster-whisper's
`transcribe()` call.

## Runs

Four runs in total. Two baselines are **reused from t0002** (no re-inference needed — load
predictions from t0002's assets directly):

| Run | Model | initial_prompt | Source |
| --- | --- | --- | --- |
| R1 | Whisper large-v3 | None (no biasing) | Reuse t0002 predictions |
| R2 | Whisper large-v3 | 31-term domain vocab | New inference (this task) |
| R3 | Whisper turbo | None (no biasing) | Reuse t0002 predictions |
| R4 | Whisper turbo | 31-term domain vocab | New inference (this task) |

New inference (R2 and R4) uses the same setup as t0002: faster-whisper int8 on CPU (Apple M5),
beam size 5, language "en", no other parameters changed from t0002.

## Metrics

All six registered project metrics are computed for every run:

| Metric key | Description |
| --- | --- |
| `entity_accuracy_gold92` | Entity accuracy across all 93 clips (primary comparison) |
| `entity_accuracy_production` | Entity accuracy on the 34 production-accent clips only |
| `entity_accuracy_domain_vocab` | Entity accuracy over the 31 domain terms appearing in gold-92 ground truth (primary for this task) |
| `wer_gold92` | Word error rate across all 93 clips |
| `latency_p50_seconds` | p50 inference latency (new inference runs only; baselines carry t0002 values) |
| `intent_preservation_gold92` | Intent preservation across all 93 clips |

All metrics reported with BCa bootstrap 95% CIs (n=10,000, seed=42). The
`entity_accuracy_domain_vocab` subset metric is the primary metric for this task because it
directly measures whether biasing helps with the 31 terms that were injected.

**Note**: `entity_accuracy_production` is not a registered project metric. Report it as a
derived sub-metric within results but do not register it separately. The registered metrics
listed above are sufficient for cross-task comparability.

## Compute

No GPU required. Runs on CPU (Apple M5 Pro/Max), faster-whisper int8. Each new inference run
(R2, R4) takes approximately the same wall-clock time as a full t0002 inference pass (~15–25
minutes per model). Total estimated compute: under 1 hour.

Budget: $0 (CPU-only, no cloud resources).

## Key Questions

1. Does `initial_prompt` with the 31-term domain vocabulary improve entity accuracy on domain
   terms? By how much (absolute and relative)?
2. Which of the 31 domain terms are still misrecognised after biasing (term-level breakdown)?
3. Does biasing cause any WER regression on non-domain utterances (hallucination or drift)?
4. Is the entity accuracy improvement larger on production-accent clips (34 clips) than on
   clean-voice clips?
5. Is the biasing effect consistent across both model sizes (large-v3 vs turbo), or does one
   model benefit more?

## Expected Assets

Two new prediction assets produced by this task:

- `predictions/whisper-large-v3-biased` — transcript predictions for all 93 gold-92 clips from
  Whisper large-v3 with domain `initial_prompt`
- `predictions/whisper-turbo-biased` — transcript predictions for all 93 gold-92 clips from
  Whisper turbo with domain `initial_prompt`

The two no-biasing baselines (R1, R3) are referenced from t0002 assets, not regenerated.

## Dependencies

Depends on **t0002_baseline_evaluation** for:

1. The no-biasing prediction assets for Whisper large-v3 and turbo (reused directly, no
   re-inference)
2. The evaluation harness code and metric computation scripts developed in t0002
3. The gold-92 dataset split definitions and clip-level metadata (production vs non-production
   stratification)

## Results Structure

Results will be reported in `results/results_detailed.md` with:

- A summary comparison table: all four runs × all six metrics with CIs
- A per-term breakdown table: for each of the 31 domain terms that appear in gold-92 ground
  truth, show recognition rate before and after biasing (both model sizes)
- A stratified comparison: production-accent clips vs clean-voice clips, biased vs unbiased
- A WER regression check: histogram or table of WER per clip, biased vs unbiased, flagging any
  clips where biasing increased WER by more than 5%

All charts saved to `results/images/` and embedded in `results_detailed.md`.

## Source

This task was motivated by suggestion **S-0003-02** ("Prototype Ron2026 initial_prompt
multi-agent pipeline on gold-92"). The current task implements the simpler ablation first —
quantifying the single-prompt biasing baseline — before moving to the multi-agent pipeline
described in the suggestion.

**Results summary:**

> **t0004 Results Summary — Vocabulary Biasing Experiment**
>
> **Summary**
>
> Injecting a 31-term domain vocabulary via Whisper's `initial_prompt` parameter produces a
> **4–5×
> improvement in domain-entity accuracy** (18% → 87–95%) with no WER degradation.
> Action-Critical WER
> dropped from 30% to 2.5% (large-v3 biased), approaching the project success criterion of <2%
> wrong-action rate. Moonshine base is 80× faster (p50 70ms) but significantly weaker on this
> domain.
>
> **Metrics**
>
> - **entity_accuracy_domain_vocab**: 18.2% → 94.5% (large-v3 biased), 87.3% (turbo biased) —
>   4–5×
> improvement; 10.9% for Moonshine base (weaker)
> - **entity_accuracy_gold92**: 25.2% → 46.0% (large-v3 biased), 43.1% (turbo biased); 21.7%
>   Moonshine
> base
> - **wer_gold92**: 10.0% → 8.5% (large-v3 biased), 10.6% → 8.3% (turbo biased); 18.4%
>   Moonshine base
> — biasing does not hurt WER
> - **action_critical_wer_gold92**: 30.4% → 2.5% (large-v3 biased), 5.1% (turbo biased); 41.1%
> Moonshine base
> - **intent_preservation_gold92**: 90.3% → 98.9% (large-v3 biased), 96.8% (turbo biased);
>   84.9%

</details>

<details>
<summary>✅ 0003 — <strong>Literature Review: Entity-Aware STT for Ecommerce Voice
AI (Jan–Jun 2026)</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0003_literature_review_entity_stt` |
| **Status** | completed |
| **Effective date** | 2026-06-23 |
| **Dependencies** | — |
| **Expected assets** | 10 paper |
| **Source suggestion** | — |
| **Task types** | [`literature-survey`](../../../meta/task_types/literature-survey/) |
| **Start time** | 2026-06-23T08:06:23Z |
| **End time** | 2026-06-23T09:25:00Z |
| **Step progress** | 11/15 |
| **Task page** | [Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Task folder** | [`t0003_literature_review_entity_stt/`](../../../tasks/t0003_literature_review_entity_stt/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0003_literature_review_entity_stt/results/results_detailed.md) |

# Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)

## Motivation

Rezolve's voice commerce assistant currently uses Whisper Turbo with dynamic context injection
(a runtime hotword list passed to the decoder) as its production STT pipeline. The primary
bottleneck, confirmed by the gold-92 benchmark (`t0001_stt_benchmark`), is entity accuracy:
brand names, product names, and SKUs are frequently mangled or dropped, leading to
wrong-action rates that exceed the 2% target.

Before investing engineering effort in a new approach, this task surveys the most recent
published literature (January–June 2026) to identify which techniques offer the best
entity-accuracy gains in the ecommerce domain while remaining compatible with the project's
800 ms p50 latency constraint. The findings will directly inform the design of follow-on
benchmark and model tasks.

## Research Question

What are the most effective techniques published between January and June 2026 for improving
STT accuracy on domain-specific named entities (brand names, product names, SKUs), and which
of these are compatible with a sub-800 ms voice-to-action latency requirement in an English
ecommerce voice AI context?

## Scope

### Techniques to cover

1. **Contextual biasing** — runtime entity lists fed to the decoder (prefix trees, WFST
   rescoring, shallow biasing networks). This is the approach used in our current Whisper
   Turbo pipeline; the survey must identify state-of-the-art alternatives and their reported
   gains over this baseline.
2. **Shallow fusion** — interpolating ASR decoder scores with a domain language model at
   inference time. Focus on low-latency variants compatible with streaming ASR.
3. **Entity-aware ASR** — model architectures that embed entity knowledge during training or
   fine-tuning (named entity embeddings, entity-conditioned decoding, span-level objectives).
4. **LLM post-correction** — using a language model as a second-pass corrector of the ASR
   hypothesis, with or without entity grounding. Emphasis on latency-efficient approaches
   (speculative decoding, distilled correctors, prompt-based).

### Inclusions

- Papers published or posted between January 1 and June 30, 2026.
- English-language ASR or multilingual ASR with English results reported.
- Ecommerce, voice assistant, or general conversational domain.
- Any evaluation on named entity recognition accuracy, entity WER, or brand/product recall.

### Exclusions

- Papers published before 2026 (background reading only; do not add as task paper assets
  unless they are essential baselines cited by 2026 papers).
- Purely offline batch transcription systems with no latency data.
- Non-English-only systems with no English results.

## Approach

### Search strategy

Query the following databases using at least the keyword combinations listed below. Record
every query and its result count in `results/search_log.md`.

**Databases**: arXiv (cs.CL, cs.SD, eess.AS), Semantic Scholar, ACL Anthology, Interspeech
2026 proceedings (if published), ICASSP 2026 proceedings.

**Keyword combinations** (run all six):

1. `contextual biasing ASR named entity 2026`
2. `entity-aware speech recognition ecommerce 2026`
3. `shallow fusion ASR latency 2026`
4. `LLM post-correction ASR named entity 2026`
5. `domain-specific ASR brand product 2026`
6. `Whisper fine-tuning named entity ecommerce 2026`

### Paper selection

- Target: a minimum of 8 and a maximum of 15 papers added as paper assets.
- Prioritize papers that report: (a) entity-level accuracy or entity WER, (b) latency
  measurements or inference cost, and (c) ecommerce or voice assistant domain results.
- Papers that do not report latency data are still in scope if they address entity accuracy
  directly — note the omission explicitly in the synthesis.

### Asset creation

Use `/add-paper` for each selected paper to create a paper asset under
`assets/paper/<paper_id>/`. Use `/download_paper` to obtain PDF files where available. For
each paper, read the full text before writing the summary. Mark abstract-only summaries
explicitly in the paper asset when a PDF is unavailable.

## Comparison Against Current Approach

The synthesis document must include a dedicated section titled **"Comparison Against Whisper
Turbo + Dynamic Context Injection"** that addresses:

1. Which surveyed techniques report gains on entities over a runtime hotword-biasing baseline?
2. Which techniques are latency-compatible (sub-800 ms p50 for a ~5-second utterance) based on
   reported numbers or reasonable extrapolation?
3. Which techniques are practically implementable without full model retraining (i.e., can be
   applied to our existing Whisper Turbo checkpoint)?
4. For each viable candidate: what is the estimated entity accuracy uplift vs. the hotword
   baseline?

This comparison should yield a ranked shortlist of at most 3 techniques to prototype in
follow-on tasks.

## Expected Outputs

### Paper assets

- 8–15 paper assets under `assets/paper/`, each passing `verify_paper_asset.py` with no
  errors.
- Each paper summary states: technique category, claimed entity-accuracy gain, latency impact,
  and domain.

### Synthesis document (`results/results_summary.md`)

Organized as follows:

1. **Methodology** — search queries, databases, inclusion/exclusion criteria, total papers
   reviewed vs. selected.
2. **Findings by technique category** — one subsection per category (contextual biasing,
   shallow fusion, entity-aware ASR, LLM post-correction), summarizing the 2–4 most relevant
   papers and the consensus finding for each category.
3. **Comparison Against Whisper Turbo + Dynamic Context Injection** — see above.
4. **Shortlist for prototyping** — the top 1–3 techniques ranked by expected entity accuracy
   gain while respecting the <800 ms latency constraint.
5. **Gaps and uncertainties** — what the surveyed literature does not cover, and what
   assumptions underlie the shortlist ranking.

### Search log (`results/search_log.md`)

Records every query run, the database, the date, the result count, and the number of papers
selected from that query.

## Key Questions

1. Does contextual biasing (the technique underlying our current dynamic context injection)
   remain the dominant approach in Jan–Jun 2026 literature, or have newer methods superseded
   it?
2. Which post-correction approach offers the best entity accuracy gain with the lowest added
   latency?
3. Is shallow fusion still competitive with end-to-end entity-aware ASR architectures for
   ecommerce domains?
4. Are there ecommerce-specific benchmarks published in this period that could complement
   gold-92 for ongoing evaluation?

## Dependencies

No task dependencies. This is a pure literature survey and can start immediately. The gold-92
benchmark dataset (`t0001_stt_benchmark`) provides domain context but is not a runtime input
to this task.

## Budget and Compute

This task requires no GPU compute. Costs are limited to:

- LLM API calls for paper summarization: estimated $2–5 total.
- Web search and paper download: no direct cost.

No remote machine setup is needed.

**Results summary:**

> ---
> task_id: "t0003_literature_review_entity_stt"
> date: "2026-06-23"
> ---
> **Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)**
>
> **Summary**
>
> Systematic literature review of Jan–Jun 2026 publications on entity-aware STT. **15 paper
> assets**
> were created covering contextual biasing, entity-aware ASR architectures, and LLM
> post-correction.
> The top no-retraining candidates for prototyping on gold-92 are **RECOVER** (33–35% relative
> E-WER
> reduction, Earnings-21) and **Ron2026** (17% relative WER reduction via Whisper
> `initial_prompt`).
> Shallow fusion has effectively no 2026 literature — documented as a gap, not a search
> failure.
>
> **Metrics**
>
> * **Paper assets created**: **15** (all passing `verify_paper_asset.py`, 0 errors)
> * **Databases searched**: **9** (arXiv, Semantic Scholar, ACL Anthology, ICASSP 2026,
>   Interspeech
> 2026, Papers With Code, AssemblyAI, Emergent Mind, Google web search)
> * **Search queries run**: **14** (6 required keyword combinations + 8 gap-filling queries)

</details>

<details>
<summary>✅ 0002 — <strong>Baseline Evaluation — Deepgram and Whisper Large v3 on
Gold-92</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0002_baseline_evaluation` |
| **Status** | completed |
| **Effective date** | 2026-06-23 |
| **Dependencies** | [`t0001_stt_benchmark`](../../../overview/tasks/task_pages/t0001_stt_benchmark.md) |
| **Expected assets** | 2 predictions |
| **Source suggestion** | — |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/), [`baseline-evaluation`](../../../meta/task_types/baseline-evaluation/) |
| **Start time** | 2026-06-23T08:04:26Z |
| **End time** | 2026-06-23T10:25:00Z |
| **Step progress** | 13/15 |
| **Key metrics** | ⚠️ Action-Critical WER (gold-92): **0.303797**, 🎯 Entity Accuracy (gold-92): **0.251812**, ✅ Intent Preservation (gold-92): **0.903226**, ⚡ Latency p50 (seconds): **4.2501** |
| **Task page** | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Task folder** | [`t0002_baseline_evaluation/`](../../../tasks/t0002_baseline_evaluation/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0002_baseline_evaluation/results/results_detailed.md) |

# Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92

## Motivation

Before pursuing entity-aware post-correction or fine-tuning, the project needs a reliable
reference point for all five registered metrics on both the production STT system and the
leading open-source alternative. This task produces the baseline results against which every
subsequent improvement is judged. Without this baseline, no downstream task can claim a
statistically significant improvement.

The gold-92 benchmark (`stt-benchmark-gold-92`, produced by `t0001_stt_benchmark`) contains 93
annotated WAV clips from Rezolve production voice sessions across the investor-relations
domain, with accented English speakers. It is the held-out evaluation set for all tasks in
this project.

## Runs

This task evaluates exactly two STT configurations:

1. **Deepgram Nova-2** — the current Rezolve production STT endpoint. Called via the Deepgram
   cloud API with the `nova-2` model and default settings (no custom vocabulary). This is the
   production baseline the project is trying to beat.

2. **Whisper Large v3** — the state-of-the-art open-source STT model from OpenAI. Run via the
   `openai-whisper` Python package (local inference, CPU or GPU). No fine-tuning or prompt
   injection; pure out-of-the-box transcription. This provides the open-source ceiling before
   any domain adaptation.

No other STT systems or model variants are evaluated in this task.

## Metrics

All five registered project metrics must be computed for both runs:

* `entity_accuracy_gold92` — accuracy on action-critical entity spans (brand names, product
  lines, SKUs, IR terms) after normalisation. Primary success metric.
* `wer_gold92` — full-transcript WER over all reference words.
* `action_critical_wer_gold92` — WER restricted to action-critical token spans only.
* `intent_preservation_gold92` — fraction of utterances where predicted transcript preserves
  the ground-truth intent (action type + primary slot agreement).
* `latency_p50_seconds` — p50 end-to-end latency from speech-end to transcription complete.

For each metric, compute BCa bootstrap 95% confidence intervals (n=10,000 resamples, paired
samples). Run a paired BCa bootstrap significance test comparing Whisper Large v3 vs Deepgram
on `entity_accuracy_gold92` (the primary metric).

## Data Handling

* DVC-pull the gold-92 audio from `tasks/t0001_stt_benchmark/` before running any inference.
* Ground-truth transcripts and entity annotations are in the same DVC-tracked folder.
* Do not modify or augment the gold-92 data — it is a held-out regression set.
* Save raw transcription outputs (pre-metric-computation) to `data/` within this task for
  reproducibility:
  * `data/deepgram_transcripts.json` — raw Deepgram API responses for all 93 clips
  * `data/whisper_transcripts.json` — raw Whisper outputs for all 93 clips

## Compute and Budget

* **Deepgram Nova-2**: API call cost is approximately $0.0043/minute of audio. Gold-92 is
  roughly 15–20 minutes total, so ~$0.09. Negligible.
* **Whisper Large v3**: local inference on CPU takes ~8–12 min/clip × 93 clips ≈ 12–19 hours.
  Use a GPU instance if available (A100/H100: ~2–5 minutes total). Prefer a GPU if wall-clock
  time matters; the per-task budget is $100.
* Total budget estimate: $5–$20 (GPU instance) + ~$0.09 (Deepgram API). Well within limit.

If GPU is used, include `setup-machines` and `teardown` steps.

## Output Assets

Two predictions assets, one per STT system:

* `predictions/deepgram-nova2-gold92` — raw transcripts + per-utterance metrics for Deepgram
* `predictions/whisper-large-v3-gold92` — raw transcripts + per-utterance metrics for Whisper

Each predictions asset includes:

* `predictions.json` — one entry per clip: `clip_id`, `hypothesis`, `reference`,
  `entity_spans_predicted`, `entity_spans_reference`, per-utterance metric values
* `metadata.json` — model name, API version or package version, inference date, total latency

## Charts and Tables

**Required charts** (save to `results/images/`, embed in `results_detailed.md`):

1. Bar chart comparing `entity_accuracy_gold92`, `wer_gold92`, and
   `action_critical_wer_gold92` for both systems side-by-side, with BCa 95% CI error bars.
   Caption: "Figure 1: Primary metric comparison — Deepgram Nova-2 vs Whisper Large v3 on
   gold-92."
2. Per-utterance scatter plot of entity accuracy (x = Deepgram, y = Whisper), one point per
   clip, coloured by speaker accent group. Caption: "Figure 2: Per-utterance entity accuracy
   correlation — clips above diagonal favour Whisper."

**Required tables** (in `results_detailed.md`):

1. Summary metrics table: rows = {Deepgram Nova-2, Whisper Large v3}, columns = all 5 metrics
   (point estimate ± 95% CI).
2. Per-accent-group breakdown: rows = accent groups, columns = `entity_accuracy_gold92` for
   each system.

## Key Research Questions Addressed

1. What is the current WER and entity accuracy of Deepgram (production) and Whisper Large v3
   on the gold-92 benchmark, broken down by utterance category and entity type? *(RQ1)*
2. Does Whisper Large v3 materially outperform Deepgram on entity accuracy with statistical
   significance (BCa p < 0.05)? *(Sub-question of RQ1)*

## Dependencies

* `t0001_stt_benchmark` — provides the gold-92 DVC-tracked audio and ground-truth annotations.
  This task cannot start without the dataset being available via `dvc pull`.

## Cross-References

* Project description: "What is the current WER and entity accuracy of Deepgram (production)
  and Whisper Large v3 on the gold-92 benchmark?" (RQ1)
* Deepgram Nova-2 documentation — current production STT endpoint
* Radford et al. (2023) — Whisper model paper

**Results summary:**

> **Results Summary: Baseline Evaluation — Deepgram and Whisper on Gold-92**
>
> **Summary**
>
> Whisper turbo and Whisper large-v3 were benchmarked on the gold-92 STT dataset (93 clips
> from
> Rezolve investor-relations production sessions). Both models produced **identical entity
> accuracy of
> 25.2%** with matching BCa 95% CIs, ruling out model size as the bottleneck. The
> production-session
> subset scored only **8.8% entity accuracy**, exposing a severe gap between lab conditions
> and real
> deployment. Deepgram Nova-2 could not be run due to a missing API key; the Whisper results
> stand as
> the open-source baseline. The primary implication is that vocabulary biasing — not a larger
> model —
> is the highest-ROI next step.
>
> **Metrics**
>
> - **Entity accuracy (gold-92, both models)**: **25.2%** (95% BCa CI: 18.1%–33.7%)
> - **WER — Whisper large-v3**: **10.0%** (95% BCa CI: 8.8%–14.6%)
> - **WER — Whisper turbo**: **10.6%** (95% BCa CI: 8.9%–14.4%)
> - **Action-critical WER (both models)**: **30.4%** — 3× higher than general WER, confirming
>   domain
> entities are the failure locus
> - **Intent preservation (both models)**: **90.3%** (95% BCa CI: 82.8%–95.7%) — likely
>   over-estimated

</details>

<details>
<summary>✅ 0001 — <strong>STT Benchmark — Gold-92 Dataset Ingestion</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0001_stt_benchmark` |
| **Status** | completed |
| **Effective date** | 2026-06-22 |
| **Dependencies** | — |
| **Expected assets** | 1 dataset |
| **Source suggestion** | — |
| **Task types** | [`audio-dataset-curation`](../../../meta/task_types/audio-dataset-curation/) |
| **Start time** | 2026-06-22T00:00:00Z |
| **End time** | 2026-06-22T00:00:00Z |
| **Step progress** | 6/6 |
| **Task page** | [STT Benchmark — Gold-92 Dataset Ingestion](../../../overview/tasks/task_pages/t0001_stt_benchmark.md) |
| **Task folder** | [`t0001_stt_benchmark/`](../../../tasks/t0001_stt_benchmark/) |
| **Detailed report** | [results_detailed.md](../../../tasks/t0001_stt_benchmark/results/results_detailed.md) |

# STT Benchmark — Gold-92 Dataset Ingestion

## Objective

Ingest the gold-92 held-out STT benchmark dataset from Rezolve production voice sessions into
the ARF task structure, version the audio files with DVC, and register the dataset asset so
all future evaluation tasks can depend on it.

## Background

The gold-92 dataset was curated from Rezolve production brainpowa-realtime-api sessions. It
contains 93 WAV clips annotated with manually verified ground-truth transcripts plus existing
Deepgram Nova-2 and Whisper Large v2 hypotheses. Speakers include accented English (French,
German, Hebrew, Korean, Russian, Spanish native languages) and English-native Rezolve
investor-relations recordings.

This dataset is the primary held-out regression set for all STT experiments in this project.
It must never be used for training or fine-tuning — only for evaluation.

## What Was Done

- Copied 93 WAV clips from the local benchmark directory
  (`tmp/stt-research/bencmark-92/gold_combined/`) into
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/`.
- Created `gold_set.jsonl` (93 records) with full annotation schema: clip_id, source,
  filename, ground_truth, production (Deepgram), whisper.
- Created `ground_truth.jsonl` (93 records) with simplified clip_id + ground_truth index.
- Tracked the `audio/` directory with DVC (`dvc add`) pointing to the Azure Blob remote
  `azure://ml-dvc-datasets/datasets/rail-arf-stt`.
- Committed the `.dvc` pointer file to git; actual audio bytes go through `dvc push`.

## Constraints

- Gold-92 is **held-out only**. Never split into train or validation. Never fine-tune on it.
- Audio files are DVC-managed — do not commit raw WAV bytes to git.
- The `audio.dvc` pointer must be kept up to date if audio files change.

**Results summary:**

> **Results Summary: t0001_stt_benchmark**
>
> **Outcome**
>
> Gold-92 STT benchmark dataset successfully ingested and registered. 93 WAV clips with
> ground-truth annotations are now version-controlled: JSONL files in git, audio in DVC
> (Azure Blob Storage at `azure://ml-dvc-datasets/datasets/rail-arf-stt`).
>
> **Assets Produced**
>
> * Dataset asset `stt-benchmark-gold-92` with 93 clips, 2 JSONL annotation files, and
>   DVC-tracked
> audio directory.
>
> **Baseline Observations (from gold_set.jsonl)**
>
> * Production (Deepgram) transcripts are present for all 93 clips.
> * Whisper Large v2 transcripts are present for all 93 clips.
> * Formal WER and entity accuracy evaluation is deferred to `t0002_baseline_evaluation`.
>
> **Next Steps**

</details>
