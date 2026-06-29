# t0012 — Three-Model Production Streaming Benchmark: Whisper, Parakeet, Granite

## Motivation

t0011 confirmed that Parakeet TDT 0.6b-v3 and Granite Speech 4.1 2B perform identically in streaming
and batch when using the accumulate-then-transcribe pattern. What remains unmeasured is Whisper
turbo — the current production STT model in brainpowa-realtime-api — on the gold-92 benchmark, and
how all three models compare when each runs in its own true production streaming mode. This task
establishes a three-way apples-to-apples comparison where each model is evaluated exactly as it runs
in production.

The key research questions are:

1. What accuracy does Whisper turbo achieve on gold-92 in its production streaming mode (chunked
   re-transcribe with delta extraction)?
2. How does Whisper compare to Parakeet and Granite on entity accuracy, WER, and action-critical
   WER?
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
* Biasing: `initial_prompt` = comma-separated 31 domain vocab terms (same as `stt_initial_prompt` in
  brainpowa config)
* Streaming pattern: every 32 kB of accumulated PCM-16 audio, transcribe full buffer, extract delta
  (new words vs previous interim using word-level longest-common-prefix matching), yield delta;
  final transcribe on complete audio after `None` sentinel
* Latency: wall-clock from first chunk delivered to final transcript returned
* Extra metric: **time-to-first-delta** — wall-clock from first chunk to first non-empty delta yield
  (first partial result)

### Run 2 — Whisper turbo (batch baseline)

Same model and parameters as Run 1 but accumulate all audio, single `transcribe()` call. Provides
the batch baseline for Whisper to quantify the cost of chunked re-transcription.

### Run 3 — Parakeet TDT 0.6b-v3 (streaming, production mode)

Identical to t0011 Parakeet streaming run (accumulate-then-transcribe). Replicated here as a direct
comparison row alongside Whisper. Baselines from t0011 may be copied rather than re-running if the
server environment is unchanged.

* Model: NeMo parakeet-tdt-0.6b-v3 from `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`
* Biasing: GPU-PB phrase boosting, alpha=1.0, 66 casing variants of 31 domain terms
* Pattern: accumulate all 32 kB chunks → reconstruct float32 → single `model.transcribe()`

### Run 4 — Granite Speech 4.1 2B (streaming, production mode)

Identical to t0011 Granite streaming run. Replicated here as a direct comparison row.

* Model: ibm-granite/granite-speech-4.1-2b from
  `/home/azureuser/granite-model/granite-speech-4.1-2b`
* Biasing: keyword prompt injection — `"transcribe the speech to text. Keywords: Rezolve, ..."`
* Pattern: accumulate all 32 kB chunks → reconstruct float32 tensor → single model generate call

## Domain Vocabulary (31 terms)

Rezolve, brainpowa, NASDAQ, Selfridges, Harrods, Walmart, Macy's, Nordstrom, Bloomingdale's,
Sephora, Zara, H&M, Uniqlo, ASOS, Farfetch, NET-A-PORTER, Matches, Mytheresa, Browns, Liberty,
Harvey Nichols, Fenwick, John Lewis, Debenhams, Marks and Spencer, Next, River Island, Topshop,
ASOS, Boohoo, Pretty Little Thing.

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

Estimated cost: Azure H100 NVL reserved instance — effectively $0 incremental for ~20 min GPU time.

## Data Handling

* Audio: gold-92 WAV files from `tasks/t0001_stt_benchmark/` (DVC-tracked). Run `dvc pull` before
  starting.
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

1. **Three-model accuracy comparison** — grouped bar chart, x-axis: model×mode, y-axis: %, panels:
   EA, EA_DV, WER. Answers: which model is most accurate in production streaming mode?
2. **Whisper streaming vs batch delta** — bar chart, x-axis: metric, y-axis: pp delta. Answers: does
   chunked re-transcription hurt Whisper accuracy?
3. **Latency distribution** — grouped bar chart p50/p95/p99 for all four runs. Answers: which model
   is fastest in production mode?
4. **Time-to-first-delta (Whisper)** — histogram of TTFD across 93 clips. Answers: how quickly does
   Whisper produce its first partial result?

## Key Questions

1. Does Whisper turbo match or exceed Granite Speech 4.1 2B on entity accuracy and action-critical
   WER in production streaming mode?
2. Does Whisper's chunked re-transcribe pattern degrade accuracy vs single-pass batch by more than 2
   pp on any metric?
3. Is Whisper's time-to-first-delta under 1 second for ≥90% of clips (one chunk at 32 kB ≈ 1 s)?

## Verification Criteria

* All four runs complete on 93/93 clips (or ≥90/93 with explicit note on failures).
* Parakeet and Granite deltas vs t0011 < 1 pp on all accuracy metrics (environment stability check).
* `metrics.json` written with all registered metrics for all four runs.
* All four charts generated and embedded in `results_detailed.md`.
