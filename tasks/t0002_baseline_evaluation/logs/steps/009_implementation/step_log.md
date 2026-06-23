---
spec_version: "3"
task_id: "t0002_baseline_evaluation"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-06-23T08:36:14Z"
completed_at: "2026-06-23T09:15:00Z"
---
## Summary

Ran Whisper Large v3 on all 93 gold-92 clips via faster-whisper (CTranslate2 INT8, CPU, M5 Mac).
Scope narrowed to Whisper-only by user direction (no Deepgram API key available). Computed WER,
entity accuracy, action-critical WER, intent preservation, and latency p50 with BCa bootstrap CIs.
Entity accuracy is low (25.2%) confirming the domain-specific entity challenge that motivates this
project.

## Actions Taken

1. Installed faster-whisper, deepgram-sdk, jiwer, matplotlib, scipy, tqdm dependencies in
   pyproject.toml.
2. Located gold-92 audio at `/Users/margotiamanova/Desktop/gold_dataset_stt/audio/` (DVC pull
   unavailable — Azure config.local not configured) and symlinked to task audio path.
3. Validated 5-clip sample: English output confirmed, plausible transcriptions, latency ~5-6s/clip.
4. Ran full Whisper Large v3 inference on 93 clips: 100% success, ~9 minutes on M5.
5. Computed all five metrics with BCa bootstrap (n=10,000, seed=42, blockwise by source group).
6. Created predictions asset `whisper-large-v3-gold92` (93 records, verificator passed).
7. Generated results/metrics.json (explicit variant format) and two charts.
8. Removed Deepgram placeholder asset per user scope change (Whisper-only baseline).
9. Updated task.json expected_assets from 2 to 1 predictions asset.

## Outputs

* `tasks/t0002_baseline_evaluation/code/` — 8 Python modules (load_dataset, run_whisper,
  run_deepgram, compute_metrics, generate_predictions_asset, generate_analysis_output,
  generate_charts, paths)
* `tasks/t0002_baseline_evaluation/data/whisper_transcripts.json` — 93 raw transcripts
* `tasks/t0002_baseline_evaluation/data/analysis_output.json` — BCa CIs and accent breakdown
* `tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/` — predictions asset
* `tasks/t0002_baseline_evaluation/results/metrics.json` — entity_accuracy=0.2518, wer=0.1003,
  action_critical_wer=0.3038, intent_preservation=0.9032, latency_p50=5.66s
* `tasks/t0002_baseline_evaluation/results/images/fig1_primary_metrics_comparison.png`
* `tasks/t0002_baseline_evaluation/results/images/fig2_per_utterance_entity_accuracy.png`

## Issues

Deepgram Nova-2 run skipped by user decision (no API key). Task narrowed to Whisper-only baseline.
DVC pull not available (Azure config.local missing) — audio sourced locally from
`/Users/margotiamanova/Desktop/gold_dataset_stt/audio/`.
