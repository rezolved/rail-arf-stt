# t0020 — Whisper Production Short-Clip Failure Reproduction

## Motivation

In production (brainpowa-realtime-api), `WhisperSTT` frequently produces empty output or
hallucinations on short audio utterances. The t0014 benchmark showed Whisper with a 0% empty rate on
synthetic short clips, but this result is invalid: t0014 used an accumulate-then-transcribe
simulation (the `STTAdapter` base-class default), not the actual `WhisperSTT.transcribe_stream()`
behavior.

The production `WhisperSTT.transcribe_stream()` (`brainpowa-realtime-api/pipeline/stt/whisper.py`)
does **chunked re-transcribe**: it transcribes the growing audio buffer every
`stream_interval_bytes` (32 kB ≈ 1 second of PCM-16 at 16 kHz) while accumulating chunks. On short
utterances this means the VAD filter receives partial audio at each intermediate pass — causing
`no_speech_prob` to spike, triggering empty output or hallucination before the final chunk arrives.

This task directly reproduces that failure mode using the production code path and characterises the
failure threshold by duration bin.

## Research Questions

1. At what duration does `WhisperSTT.transcribe_stream()` start producing empty output or
   hallucinations via intermediate passes?
2. Does the final pass (on the complete audio) recover correctly even when intermediate passes
   failed?
3. Is the failure caused by VAD misfiring on partial audio, or by the decoder hallucinating on
   incomplete spectrograms?
4. What is the minimum clip duration at which Whisper is reliable in the production streaming
   pattern?

## Scope

### Part 1 — Dataset

Reuse the 44 synthetic short clips from t0014
(`tasks/t0014_granite_short_clip_robustness/data/short_clips/`, duration bins: 0.5 s, 1.0 s, 1.5 s,
2.0 s, 2.5 s, 3.0 s). Synthesise additional clips from gold-92 source audio at longer duration bins:

| Bin | Target count | Source |
| --- | --- | --- |
| 5 s | 7 clips | trimmed gold-92 WAVs |
| 10 s | 7 clips | trimmed gold-92 WAVs |
| 15 s | 7 clips | trimmed gold-92 WAVs |
| 20 s | 7 clips | trimmed gold-92 WAVs |
| 25 s | 7 clips | trimmed gold-92 WAVs |
| 30 s | 7 clips | trimmed gold-92 WAVs |

Total: 44 (reused) + 42 (new) = 86 clips.

Save new clips to `data/short_clips_extended/` as WAV (16 kHz, mono, PCM-16). Save metadata to
`data/short_clips_extended_metadata.jsonl` with the same schema as t0014's
`short_clips_metadata.jsonl` (`clip_id`, `source_clip_id`, `duration_s`, `reference_text`).

### Part 2 — Production Streaming Simulation

Run `WhisperSTT` (faster-whisper `turbo`) on every clip via the actual `transcribe_stream()` code
path, feeding audio as a 32 kB PCM-16 asyncio.Queue exactly as the production WebSocket pipeline
does.

**Model config** (identical to production defaults):

- Model size: `turbo`
- Compute type: `float16`, device: `cuda`
- `beam_size=1`, `vad_filter=True`, `no_speech_threshold=0.6`, `temperature=0.0`
- `initial_prompt`: comma-separated 31 domain vocab terms (same as t0012/t0014)

**ctranslate2 / CUDA note**: On the Azure H100 NVL host (`llm-t1-nc80`), `ctranslate2 4.8.0` with
cuDNN 9 raises `cudaErrorInvalidDevice: invalid device ordinal` when attempting real-audio GPU
inference. Resolution options (try in order):

1. Pin `CUDA_VISIBLE_DEVICES=0` at process level AND use `device_index=None` (not 0) in
   `WhisperModel`.
2. Install `ctranslate2` compiled for cuDNN 9 (check PyPI for `ctranslate2>=4.5` wheels with CUDA
   12.2 + cuDNN 9 support).
3. Fall back to HuggingFace Transformers Whisper with the same chunked re-transcribe loop (same
   weights, comparable VAD — documents the workaround in the correction log).

**Streaming simulation loop** (mirrors `WhisperSTT.transcribe_stream()`):

```python
accumulated = bytearray()
bytes_since_last = 0
intermediates = []

for chunk in audio_chunks:          # 32 kB chunks from queue
    accumulated.extend(chunk)
    bytes_since_last += len(chunk)
    if bytes_since_last >= STREAM_INTERVAL_BYTES:  # 32 kB
        bytes_since_last = 0
        text, nsp = transcribe(bytes(accumulated))  # growing buffer
        intermediates.append({"text": text, "nsp": nsp, "is_empty": not text})

# Final pass on complete audio
final_text, final_nsp = transcribe(bytes(accumulated))
```

Per-clip output (save to `data/transcripts_whisper_production_sim.jsonl`):

- `clip_id`, `duration_s`, `transcript` (final pass text)
- `is_empty` — final pass empty
- `is_hallucination` — BoH detector on final pass
- `any_intermediate_empty` — any intermediate pass empty (primary production failure mode)
- `any_intermediate_hallucination` — any intermediate pass hallucination
- `intermediate_count` — number of intermediate passes fired
- `intermediates` — list of `{bytes, text, is_empty, is_hallucination, no_speech_prob}`
- `final_no_speech_prob`, `latency_seconds`, `ttfd_seconds`

### Part 3 — Stratified Analysis

Compute per duration bin:

| Metric | All bins |
| --- | --- |
| `empty_rate` (final pass) | ✓ |
| `intermediate_empty_rate` (any intermediate empty) | ✓ |
| `hallucination_rate` (final pass) | ✓ |
| `intermediate_hallucination_rate` | ✓ |
| Latency p50 (seconds) | ✓ |

For bins with reference transcripts (all bins have them via gold-92 ground truth):

| Metric | All bins |
| --- | --- |
| `entity_accuracy_gold92` | ✓ |
| `wer_gold92` | ✓ |
| `action_critical_wer_gold92` | ✓ |
| `intent_preservation_gold92` | ✓ |
| `wrong_action_rate_gold92` | ✓ |
| `entity_accuracy_domain_vocab` | ✓ |
| `latency_p50_seconds` | ✓ |

### Part 4 — Answer Asset

Answer ID: `whisper-production-short-clip-failure-profile`

Question: "At what clip duration does WhisperSTT.transcribe_stream() become reliable in the
production streaming pattern, and what is the failure mechanism?"

Evidence to cover:

- `intermediate_empty_rate` and `intermediate_hallucination_rate` per duration bin (primary failure
  signal)
- `final_empty_rate` per bin (does final pass recover?)
- `no_speech_prob` distributions for intermediate vs final passes
- Whether failure is VAD-driven (high `no_speech_prob`) or decoder hallucination (non-empty but
  wrong)
- Explicit duration threshold recommendation: "use Whisper only for clips > X seconds in the
  production streaming pattern"
- Cross-reference with t0014's false 0% empty rate — explain the discrepancy

## Metrics

All seven registered project metrics computed on clips with reference transcripts:

| Metric | Run |
| --- | --- |
| `entity_accuracy_gold92` | Whisper production sim |
| `entity_accuracy_domain_vocab` | Whisper production sim |
| `wer_gold92` | Whisper production sim |
| `action_critical_wer_gold92` | Whisper production sim |
| `intent_preservation_gold92` | Whisper production sim |
| `latency_p50_seconds` | Whisper production sim |
| `wrong_action_rate_gold92` | Whisper production sim |

Additional metrics per duration bin:

- `empty_rate` (final pass)
- `intermediate_empty_rate`
- `hallucination_rate` (final pass)
- `intermediate_hallucination_rate`

## Charts

All saved to `results/images/` and embedded in `results_detailed.md`.

1. **Intermediate vs final empty rate by duration bin** — line chart, x-axis: duration bin, y-axis:
   rate (%), two lines: `intermediate_empty_rate` and `final_empty_rate`. Answers: does the final
   pass recover from intermediate failures?
2. **Failure rate by duration bin** — grouped bar chart, x-axis: duration bin, y-axis: rate (%),
   bars: `intermediate_empty_rate`, `intermediate_hallucination_rate`, `final_empty_rate`. Answers:
   at what duration does production Whisper become reliable?
3. **no\_speech\_prob distribution** — box-plot per duration bin, separate series for intermediate
   passes vs final pass. Answers: is failure VAD-driven?

## Baselines

Compare against t0014 Whisper results (false 0% empty rate) to quantify the measurement gap.

## Assets

1. `whisper-short-clips-production-sim` (predictions) — per-clip JSONL with all streaming
   intermediate data
2. `whisper-production-short-clip-failure-profile` (answer) — duration threshold analysis and
   failure mechanism characterisation

## Compute and Budget

| Run | Est. wall-clock | Notes |
| --- | --- | --- |
| Part 1 — dataset synthesis | 10 min | CPU, local or remote |
| Part 2 — Whisper inference (86 clips) | 20 min | GPU, H100 NVL |
| Part 3–4 — analysis + answer | 20 min | CPU |

Total GPU time: ~20 min. Cost: $0 (reserved instance).

Machine: Azure H100 NVL (`gpu-azure`, `azureuser@llm-t1-nc80`, conda env `stt`).

## Data Handling

- t0014 short clips: `tasks/t0014_granite_short_clip_robustness/data/short_clips/` (DVC-tracked).
  Run `dvc pull` before starting.
- Gold-92 source audio: `tasks/t0001_stt_benchmark/` (DVC-tracked). Run `dvc pull` before starting.
- New extended clips saved to `data/short_clips_extended/` and DVC-tracked.

## Verification Criteria

- 86 total clips processed (44 reused + 42 new).
- `WhisperSTT.transcribe_stream()` or accurate simulation used — NOT direct `model.transcribe()`.
- `intermediate_empty_rate` reported per duration bin.
- Duration threshold recommendation stated explicitly in answer asset.
- All seven registered metrics computed.
- Three charts generated and embedded in `results_detailed.md`.
- t0014 discrepancy explained in answer asset.
