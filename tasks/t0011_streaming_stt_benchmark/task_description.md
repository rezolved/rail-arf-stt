# Streaming STT Benchmark — Parakeet TDT 0.6b-v3 vs Granite Speech 4.1 2B (biased)

## Motivation

Production brainpowa-realtime-api does not deliver audio in batch — it streams PCM chunks over a
WebSocket at `stream_interval_bytes = 32000` (~1 s at 16 kHz mono), feeds them into an STT
adapter, and expects a transcription on a None sentinel. Tasks t0007 and t0009 measured both models
in pure-batch mode (full WAV loaded at once). This task answers whether the streaming delivery
pattern changes accuracy or latency relative to those batch baselines, and which model is the
better production fit under realistic conditions.

Key research questions:

1. Does chunked streaming delivery degrade entity accuracy vs. batch for Parakeet (biased)?
2. Does chunked streaming delivery degrade entity accuracy vs. batch for Granite 4.1 2B (biased)?
3. Which model achieves lower latency-to-final-transcript under streaming conditions (p50 / p95)?
4. Does the streaming gap (batch minus streaming entity accuracy) differ between the two models?

## Scope

Two runs on gold-92 (93 WAV clips):

* **Run A — Parakeet TDT 0.6b-v3 (biased, streaming)**: NeMo GPU-PB phrase boosting identical to
  brainpowa production (`stt_initial_prompt` → comma-split → NeMo `boosting_phrases`). Audio fed
  as 32000-byte PCM chunks; model accumulates until None sentinel.
* **Run B — Granite Speech 4.1 2B (biased, streaming)**: keyword prompt injection
  (`"Keywords: kw1, kw2, ..."` prefix) identical to t0007 best variant. Same chunking pattern as
  Run A.

No partial / intermediate transcription required — the streaming simulation tests the latency of the
full-segment accumulate-then-transcribe pattern (same as the production STTAdapter base class
`transcribe_stream()` default implementation).

## Approach

### Streaming Simulation

Read each gold-92 WAV at 16 kHz mono PCM, split into 32000-byte frames (exactly matching
`stt_stream_interval_bytes` from brainpowa config). Deliver frames sequentially with no sleep
(wall-clock simulation of the transport without network jitter). Send a None sentinel after the
last frame to trigger final transcription. Measure:

* `t_first_chunk` — time the first frame is submitted
* `t_transcript` — time the transcript is returned
* `latency = t_transcript - t_first_chunk`

### Biasing configuration

* **Parakeet**: load the canonical keyword list from `tasks/t0009_parakeet_production_baseline/`
  (same entity vocab used in production). Convert to NeMo `boosting_phrases` via comma-split of
  `stt_initial_prompt`.
* **Granite**: use the `"Keywords: ..."` prompt prefix established in t0007 (kw-biased variant,
  which was the best-performing configuration).

### Compute

Single run on the Azure H100 NVL server (`gpu-azure`, alias `azureuser@llm-t1-nc80`). Load only
one model at a time to avoid VRAM contention (Parakeet ~2 GB, Granite BF16 ~4 GB — both fit
sequentially). Estimated wall-clock: 15–20 min per run (93 clips × ~10 s audio × overhead).

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

1. `chart_accuracy_streaming_vs_batch.png` — grouped bar chart, entity accuracy and WER for each
   model × mode (batch vs. streaming); shows whether streaming degrades accuracy.
2. `chart_latency_distribution.png` — p50 / p95 / p99 latency bars for Run A and Run B side by
   side; reference line at 800 ms SLA and 200 ms target.
3. `chart_streaming_delta.png` — delta bars (streaming minus batch) per metric for both models;
   green = no regression, red = regression.

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

* **t0009_parakeet_production_baseline** — provides the production keyword vocabulary and batch
  accuracy baselines for Parakeet TDT 0.6b-v3.
* **t0007_ibm_granite_4_1_benchmark** — provides the batch accuracy baselines and optimal biasing
  configuration for Granite Speech 4.1 2B.

## Verification Criteria

* All 93 gold-92 clips processed in both runs with no errors.
* Streaming entity accuracy for Parakeet within ±3 pp of t0009 batch result (expected near-parity
  since accumulate-then-transcribe is equivalent to batch at segment level).
* Granite streaming entity accuracy within ±3 pp of t0007 kw-biased batch result.
* Latency p50 for both models below 800 ms SLA.
* All charts generated and embedded in `results_detailed.md`.
* `verify_task_file.py` passes with 0 errors.
