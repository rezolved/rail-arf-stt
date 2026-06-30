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

## Actions Taken

1. Synthesized 44 short clips across 6 duration bins (0.5–3.0 s, 7 clips/bin + 2 edge cases) via
   `code/synthesize_clips.py` on Azure H100 NVL; clips stored in `data/short_clips/` as 16kHz mono
   PCM-16 WAV files with metadata in `data/short_clips_metadata.jsonl`.
2. Ran Whisper large-v3-turbo inference via `code/run_whisper_short_clips.py` (HF Transformers, not
   faster-whisper due to multi-GPU CUDA ordinal bug); 44/44 outputs, empty=0%, p50=0.146s.
3. Ran Parakeet TDT 0.6b-v3 inference via `code/run_parakeet_short_clips.py` with GPU-PB boosting
   (66 casing variants, alpha=1.0); 44/44 outputs, empty=27.3% (12/44), p50=0.032s.
4. Ran Granite Speech 4.1 2B inference via `code/run_granite_short_clips.py` (bfloat16, local model
   path); 44/44 outputs, empty=0%, p50=0.125s.
5. Computed stratified analysis via `code/compute_stratified_analysis.py`: empty/hallucination rates
   per duration bin, BCa bootstrap CIs (B=1000) for gold-92 strata with n≥10, gold-92 aggregate
   EA/WER from t0012 predictions (no re-inference).
6. Generated 3 charts via `code/generate_charts.py` → `results/images/`.
7. Wrote `results/metrics.json` (3 variants × 7 metrics) via `code/write_metrics_json.py`.
8. Created answer asset `assets/answer/granite-vs-parakeet-production-fit/` with YES+2.0s-gate
   recommendation.
9. Created 3 prediction assets: `whisper-turbo-short-clips`, `parakeet-tdt-short-clips-biased`,
   `granite-speech-short-clips-biased`.

## Outputs

- `data/short_clips/` — 44 WAV files (16kHz mono PCM-16)
- `data/short_clips_metadata.jsonl` — clip metadata
- `data/short_clip_transcripts_whisper.jsonl` — Whisper transcripts
- `data/short_clip_transcripts_parakeet.jsonl` — Parakeet transcripts
- `data/short_clip_transcripts_granite.jsonl` — Granite transcripts
- `results/stratified_analysis.json` — stratified metrics with BCa CIs
- `results/metrics.json` — 3 variants × 7 registered metrics
- `results/images/` — 3 charts (PNG)
- `assets/answer/granite-vs-parakeet-production-fit/` — answer asset
- `assets/predictions/whisper-turbo-short-clips/` — prediction asset
- `assets/predictions/parakeet-tdt-short-clips-biased/` — prediction asset
- `assets/predictions/granite-speech-short-clips-biased/` — prediction asset

## Issues

1. faster-whisper multi-GPU CUDA ordinal error — fixed by using HuggingFace Transformers (same
   approach as t0012).
2. tmux not available on remote machine — fixed by using nohup background job.
3. Ruff E501 line-length violations in docstrings — fixed by wrapping lines.
4. Ruff F841 unused variable `n_models` in `generate_charts.py` — removed.
5. Ruff B023 loop-variable closure in `write_metrics_json.py` — refactored to `resolve_metric()`
   helper outside loop.
