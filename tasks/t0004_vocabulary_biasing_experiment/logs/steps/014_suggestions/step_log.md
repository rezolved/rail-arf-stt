---
spec_version: "3"
task_id: "t0004_vocabulary_biasing_experiment"
step_number: 14
step_name: "suggestions"
status: "completed"
started_at: "2026-06-23T14:48:12Z"
completed_at: "2026-06-23T15:25:00Z"
---
## Summary

Wrote 7 suggestions (S-0004-01 through S-0004-07) covering GPU latency benchmarking, vocabulary
expansion, Whisper fine-tuning, Moonshine fine-tuning, confidence-based routing, streaming
inference, and benchmark expansion. All suggestions are grounded in the t0004 findings. Passed
`verify_suggestions` with 0 errors, 0 warnings.

## Actions Taken

1. Wrote `results/suggestions.json` with 7 suggestions derived from t0004 findings.
2. Fixed SG-E008: changed suggestion kind `data` to `dataset`.
3. Fixed SG-W006: replaced non-existent category `latency-optimisation` with `latency-profiling`
   (matches registered category in meta/categories/).
4. Ran `verify_suggestions` — passed with 0 errors, 0 warnings.

## Outputs

- `tasks/t0004_vocabulary_biasing_experiment/results/suggestions.json` — 7 suggestions

## Issues

No issues encountered after fixes.
