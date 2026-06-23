---
spec_version: "3"
task_id: "t0004_vocabulary_biasing_experiment"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-06-23T13:40:00Z"
completed_at: "2026-06-23T15:15:00Z"
---
## Summary

Ran three STT inference experiments on gold-92 (93 clips): Whisper large-v3 with vocabulary biasing,
Whisper turbo with vocabulary biasing, and Moonshine base (no biasing — model does not support
initial_prompt). Computed all registered metrics for all 5 variants (2 baselines from t0002 + 3
new), wrote prediction assets for the 3 new variants, and registered the new
`entity_accuracy_domain_vocab` metric. Key finding: vocabulary biasing via `initial_prompt` raised
domain-vocab entity accuracy from 18% to 87–95% (4–5× improvement).

## Actions Taken

1. Wrote inference scripts: `run_whisper_biased.py` (large-v3), `run_whisper_turbo_biased.py`,
   `run_moonshine_small.py` (uses moonshine/base — no "small" variant exists in
   UsefulSensors/moonshine).
2. Ran Whisper large-v3 biased inference: 93 clips, `initial_prompt` = 31-term domain vocabulary.
   Saved to `data/whisper_large_v3_biased_transcripts.json`.
3. Ran Whisper turbo biased inference: 93 clips. Saved to
   `data/whisper_turbo_biased_transcripts.json`.
4. Added `useful-moonshine-onnx` dependency; ran Moonshine base ONNX inference: 93 clips, p50
   latency 0.07s. Saved to `data/moonshine_base_transcripts.json`.
5. Wrote `compute_metrics_biased.py` computing entity_accuracy, entity_accuracy_domain_vocab, WER,
   action_critical_wer, intent_preservation, latency_p50 with BCa bootstrap CIs (n=10,000, seed=42)
   for all 5 variants. Saved to `results/metrics.json` and `data/analysis_output.json`.
6. Wrote `write_predictions.py` producing 3 prediction assets: `whisper-large-v3-biased`,
   `whisper-turbo-biased`, `moonshine-base-gold92`. All verified (0 errors, 1 warning PR-W014
   acceptable).
7. Registered `meta/metrics/entity_accuracy_domain_vocab/description.json` — metric was not in
   project registry; added to pass `verify_task_metrics`.
8. Passed: mypy (0 issues), ruff (0 errors after auto-fix), all 3 prediction verificators, and
   `verify_task_metrics`.

## Outputs

- `tasks/t0004_vocabulary_biasing_experiment/code/` — 8 Python scripts
- `tasks/t0004_vocabulary_biasing_experiment/data/whisper_large_v3_biased_transcripts.json`
- `tasks/t0004_vocabulary_biasing_experiment/data/whisper_turbo_biased_transcripts.json`
- `tasks/t0004_vocabulary_biasing_experiment/data/moonshine_base_transcripts.json`
- `tasks/t0004_vocabulary_biasing_experiment/data/analysis_output.json`
- `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` — 5 variants
- `tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/`
- `tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/`
- `tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/`
- `meta/metrics/entity_accuracy_domain_vocab/description.json`

## Issues

- Moonshine "small" variant does not exist — UsefulSensors/moonshine only provides "tiny" and
  "base". Used "base" (~60M params) as the closest available model. Documented in code comment.
- `useful-moonshine-onnx` package (correct) vs `moonshine` (computer vision UNet — wrong PyPI name).
  Corrected by removing `moonshine` and installing `useful-moonshine-onnx`.
- `transcripts_by_variant` dict in `compute_metrics_biased.py` initially omitted the
  `moonshine-base` key, causing KeyError in the per-clip analysis section. Fixed by adding the key.
- Inference scripts ran via direct `uv run python` due to Anthropic API 500 error that terminated
  the implementation subagent mid-run. Recovery: reran metrics and predictions scripts manually.
