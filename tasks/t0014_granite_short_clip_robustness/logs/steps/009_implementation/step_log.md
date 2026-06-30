---
spec_version: "3"
task_id: "t0014_granite_short_clip_robustness"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-06-30T08:00:00Z"
completed_at: "2026-06-30T14:00:00Z"
---
# Step 9: Implementation

**Task**: t0014_granite_short_clip_robustness\
**Status**: completed\
**Started**: 2026-06-30T08:00:00Z\
**Completed**: 2026-06-30T14:00:00Z\
**Remote machine**: azureuser@llm-t1-nc80 (Azure H100 NVL)

## Summary

All 4 milestones completed. 44 synthetic short clips synthesized, 3 models benchmarked via
`transcribe_stream()` simulation, stratified analysis computed, and answer+prediction assets
created.

## Milestone 1: Dataset Synthesis

- Script: `code/synthesize_clips.py`
- Output: `data/short_clips/` (44 WAV files, 16kHz mono PCM-16)
- Metadata: `data/short_clips_metadata.jsonl`
- 6 duration bins (0.5, 1.0, 1.5, 2.0, 2.5, 3.0 s), 7 clips per bin
- 2 edge cases: synthetic silence and noise from noisiest gold clip
- Ran on remote under `conda activate stt`

## Milestone 2: GPU Inference

All 3 inference scripts ran on Azure H100 NVL via nohup background job. Total wall time ~10 min.

### Whisper large-v3-turbo (HuggingFace Transformers)

- Script: `code/run_whisper_short_clips.py`
- Note: uses HF Transformers, NOT faster-whisper (multi-GPU CUDA ordinal bug on this host)
- Results: 44/44, empty=0%, hallucination=0%, latency p50=0.146s
- Output: `data/short_clip_transcripts_whisper.jsonl`

### Parakeet TDT 0.6b-v3

- Script: `code/run_parakeet_short_clips.py`
- GPU-PB boosting: 66 casing variants, alpha=1.0
- Results: 44/44, empty=27.3% (12/44), hallucination=0%, latency p50=0.032s
- Key: 55.6% empty at 0.5s bin, 57.1% at 1.0s, 42.9% at 1.5s, 0% at 2s+
- Output: `data/short_clip_transcripts_parakeet.jsonl`

### Granite Speech 4.1 2B

- Script: `code/run_granite_short_clips.py`
- Model: `/home/azureuser/granite-model/granite-speech-4.1-2b`, bfloat16
- Results: 44/44, empty=0%, hallucination=0%, latency p50=0.125s
- Output: `data/short_clip_transcripts_granite.jsonl`

## Milestone 3: Analysis

- Script: `code/compute_stratified_analysis.py`
- Output: `results/stratified_analysis.json`
- Gold-92 strata from t0012 predictions (no re-inference)
- BCa bootstrap CIs (B=1000) for gold-92 strata with n>=10
- Charts: `code/generate_charts.py` → `results/images/` (3 PNGs)

Gold-92 aggregate results:

| Model | Entity Acc | WER |
| --- | --- | --- |
| Whisper | 92.3% | 7.7% |
| Parakeet | 65.0% | 16.3% |
| Granite | 94.8% | 7.4% |

- Script: `code/write_metrics_json.py`
- Output: `results/metrics.json` (3 variants × 7 metrics)

## Milestone 4: Answer Asset

- Answer: `assets/answer/granite-vs-parakeet-production-fit/`
- Short answer: **YES, with a minimum clip duration gate of 2.0 s**
- Granite 0% empty rate vs Parakeet 27.3% on short clips
- Granite superior entity accuracy on gold-92 (94.8% vs 65.0%)
- All latencies well under 800ms production constraint

## Prediction Assets

- `assets/predictions/whisper-turbo-short-clips/`
- `assets/predictions/parakeet-tdt-short-clips-biased/` (16/44 single-chunk degenerate)
- `assets/predictions/granite-speech-short-clips-biased/` (all within 4s block-attention window)

## Issues Encountered

1. faster-whisper multi-GPU CUDA error → fixed by using HuggingFace Transformers (same as t0012)
2. tmux not available on remote → fixed by using nohup background job
3. Ruff E501 in docstrings → fixed by wrapping lines
4. Ruff F841 unused variable `n_models` in generate_charts.py → removed
5. Ruff B023 loop-variable closure in write_metrics_json.py → refactored to `resolve_metric()`
   helper outside loop

## Verificators Run

- `verify_task_folder`: PASSED
- `verify_task_metrics`: PASSED
- `verify_plan`: PASSED
- `ruff check`: PASSED (0 errors after fixes)
- `mypy`: PASSED (0 errors, 287 source files)
