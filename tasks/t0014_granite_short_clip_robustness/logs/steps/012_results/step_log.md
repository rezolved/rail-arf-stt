---
spec_version: "3"
task_id: "t0014_granite_short_clip_robustness"
step_number: 12
step_name: "results"
status: "completed"
started_at: "2026-06-30T07:38:28Z"
completed_at: "2026-06-30T07:55:00Z"
---
## Summary

Wrote `results_summary.md` and `results_detailed.md` covering all task results for the Granite
short-clip robustness validation. Read `stratified_analysis.json` and `metrics.json` to verify all
numbers before writing; all quoted metrics match JSON sources exactly. The detailed results include
12 concrete examples from prediction JSONLs, covering random, best, worst, boundary, and contrastive
example categories. Task requirement coverage section addresses all REQ-1 through REQ-13 items from
the plan with status, direct answer, and evidence path.

Key finding: Granite achieves 0% empty output rate on all 44 short clips vs Parakeet's 27.3%;
production recommendation is CONDITIONAL YES with a 2.0 s minimum clip gate.

## Actions Taken

1. Read `arf/skills/execute-task/SKILL.md` (Part B results step) and
   `arf/specifications/task_results_specification.md` for format requirements.
2. Read `results/stratified_analysis.json` and `results/metrics.json` to collect exact numbers.
3. Read prediction JSONLs from all 3 prediction assets (44 rows each) to extract concrete examples.
4. Read `plan/plan.md` to get all REQ-1 through REQ-13 items for task requirement coverage.
5. Wrote `results/results_summary.md` with Summary, Metrics (8 bullet points with numbers), and
   Verification sections.
6. Wrote `results/results_detailed.md` (spec_version: "2") with all mandatory sections plus Metrics
   Tables, Comparison vs Baselines, Visualizations (3 embedded charts), Analysis, Examples (12
   examples), Limitations, and Task Requirement Coverage.
7. Cross-checked all numbers in markdown against JSON sources — confirmed identical.
8. Ran `verify_task_results t0014_granite_short_clip_robustness` — passed with 0 errors.
9. Updated `checkpoint.md` with step 12 history and next step (14 suggestions).
10. Ran flowmark on all modified `.md` files.
11. Committed all step work.

## Outputs

- `results/results_summary.md` — headline metrics and verificator status
- `results/results_detailed.md` — full results with 12 examples and REQ-1–REQ-13 coverage
- `logs/steps/012_results/step_log.md` — this file

## Issues

RM-E001 from `verify_machines_destroyed`: the Azure H100 NVL reserved instance (`llm-t1-nc80`) was
not destroyed after the task. This is expected — it is a shared team infrastructure resource with no
per-minute billing. Cost remains $0. This is documented in `results_detailed.md` under Limitations
and is not an error for this task.
