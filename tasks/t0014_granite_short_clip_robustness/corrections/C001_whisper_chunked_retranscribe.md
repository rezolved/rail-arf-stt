# C001 — Whisper chunked re-transcribe correction

**Date:** 2026-07-03
**Severity:** High — invalidates all Whisper short-clip empty_rate / hallucination_rate results

## Bug

`code/run_whisper_short_clips.py` used `simulate_streaming_accumulate()` which accumulates all
audio then calls HuggingFace Whisper once. This is the base class `STTAdapter.transcribe_stream()`
accumulate-then-transcribe pattern, NOT the production `WhisperSTT.transcribe_stream()` behavior.

Production Whisper (`brainpowa-realtime-api/pipeline/stt/whisper.py`) does **chunked
re-transcribe**: transcribes the growing buffer every `stream_interval_bytes` (32kB ≈ 1s) while
accumulating. On short clips this triggers VAD on partial audio → empty output or hallucination.

Additionally, the benchmark used HuggingFace Transformers (`openai/whisper-large-v3-turbo`) instead
of faster-whisper, which is what production uses. The no_speech_prob behavior differs.

## Impact

- `empty_rate` for Whisper was 0% for all duration bins — this is wrong. Production empty_rate on
  sub-3s clips is the primary failure mode that caused Whisper's removal.
- `hallucination_rate` is partially correct (VAD hallucinations still trigger on full-audio HF
  Whisper) but the intermediate-transcription hallucination path was not exercised.
- The Granite and Parakeet results are **not affected** — their streaming simulation was correct
  (Granite uses accumulate-then-transcribe; Parakeet chunked re-transcribe was simulated correctly).

## Fix

Replace `run_whisper_short_clips.py` with `code/run_whisper_short_clips_v2.py` which:

1. Uses faster-whisper (`WhisperModel`, same as production)
2. Implements real chunked re-transcribe: transcribes growing buffer every `CHUNK_SIZE_BYTES`
3. Records `intermediate_empty_count` and `intermediate_hallucination_count` per clip
4. Marks `is_empty=True` if the FINAL transcription is empty (consistent with how production
   pipeline consumes the stream — a clip with only intermediate empties may still recover)
5. Adds `any_intermediate_empty` flag for the failure mode where early chunks cause empty
   intermediate results (even if final is non-empty)

## Files changed

- `code/run_whisper_short_clips_v2.py` — corrected script (run this instead of v1)
- `data/short_clip_transcripts_whisper_v2.jsonl` — corrected output (replaces v1 after re-run)
- After re-run: update `results/stratified_analysis.json`, `results/metrics.json`, charts, and
  `results/results_detailed.md` Whisper rows.

## Re-run instructions

On Azure H100 NVL (`azureuser@llm-t1-nc80`, conda env `stt`):

```bash
cd ~/rail-arf-stt
git pull
python -u tasks/t0014_granite_short_clip_robustness/code/run_whisper_short_clips_v2.py
```

Then copy output and re-run analysis:

```bash
cp data/short_clip_transcripts_whisper_v2.jsonl \
   tasks/t0014_granite_short_clip_robustness/data/short_clip_transcripts_whisper.jsonl
python -u tasks/t0014_granite_short_clip_robustness/code/compute_stratified_analysis.py
python -u tasks/t0014_granite_short_clip_robustness/code/generate_charts.py
python -u tasks/t0014_granite_short_clip_robustness/code/write_metrics_json.py
```
