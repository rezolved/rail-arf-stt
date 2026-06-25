---
spec_version: "3"
task_id: "t0008_moonshine_v2_benchmark"
step_number: 8
step_name: "suggestions"
status: "completed"
started_at: "2026-06-25T10:30:00Z"
completed_at: "2026-06-25T11:00:00Z"
---
## Summary

Generated 3 follow-up suggestions from t0008 results and wrote them to `results/suggestions.json`.
The verificator passed with 0 errors and 0 warnings.

## Context Read

- `task.json` — task index 8, scope: CPU benchmark + shallow-fusion feasibility
- `results/results_summary.md`, `results/results_detailed.md`, `results/metrics.json`
- `results/compare_literature.md`
- `assets/predictions/moonshine-v2-medium-gold92-biasing-assessment/files/shallow_fusion_feasibility.md`
- `task_description.md`
- Step logs for steps 010, 011, 012 (all skipped)
- `project/description.md` (via project context)

## Deduplication

Ran `aggregate_suggestions --uncovered` (23 existing suggestions) and
`aggregate_tasks --detail short` (8 existing tasks). Key exclusions:

- S-0005-04 covers shallow-fusion adapter implementation for Moonshine — not duplicated
- S-0003-07 covers accent stratification of gold-92 — not duplicated
- S-0002-04 covers domain fine-tuning of Whisper — not duplicated

## Suggestions Generated

| ID | Title | Kind | Priority |
| --- | --- | --- | --- |
| S-0008-01 | Benchmark Moonshine ONNX Medium on gold-92 when UsefulSensors ships the ONNX export | experiment | medium |
| S-0008-02 | Moonshine model-size ablation: benchmark tiny, base, and large variants on gold-92 entity accuracy | experiment | medium |
| S-0008-03 | Preprocess Rezolve investor-relations transcript corpus for KenLM domain language model training | dataset | medium |

## Rationale

**S-0008-01**: t0008 measured 233ms warmed p50 using the Transformers backend; the ONNX export (not
yet available for Medium) is estimated to be ~30ms faster per clip, which would meet the 200ms
target. This is a concrete, bounded experiment contingent on UsefulSensors releasing the ONNX model.

**S-0008-02**: The finding that v2 Medium (266M params) achieves identical entity accuracy as base
(38M params) is a significant result. A controlled ablation across all Moonshine variants would
confirm whether the plateau is universal or whether any variant breaks it, informing the value of
S-0005-04 shallow fusion work.

**S-0008-03**: The shallow fusion feasibility report identifies the Rezolve investor-relations
corpus as the prerequisite for KenLM domain LM training (Approach 1 of the feasibility doc).
Preprocessing this corpus unblocks S-0005-04 and future domain adaptation work.

## Verificator Output

```
Verifying: tasks/t0008_moonshine_v2_benchmark/results/suggestions.json
PASSED — no errors or warnings
```
