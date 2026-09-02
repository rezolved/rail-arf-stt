---
spec_version: "3"
task_id: "t0026_biasing_on_finetune_ablation"
step_number: 12
step_name: "results"
status: "completed"
started_at: "2026-09-02T15:05:31Z"
completed_at: "2026-09-02T15:20:00Z"
---
## Summary

Wrote `results/results_summary.md` and `results/results_detailed.md` (spec_version "2") synthesizing
the 4-arm ablation already computed in step 9 (`results/ablation_metrics.json`,
`results/mcnemar_results.json`, `results/clip_level_appendix.json`) into the mandatory results-step
deliverables, cross-checked every quoted number against the underlying JSON, and verified
`results/metrics.json`, `results/costs.json`, and `results/remote_machines_used.json` (the latter
two already correct from step 10 teardown, left unmodified).

## Actions Taken

1. Re-read `tasks/t0026_biasing_on_finetune_ablation/task.json`, `plan/plan.md`'s
   `## Task Requirement Checklist` (15 `REQ-*` items), `task_description.md`'s Q1-Q5, and the full
   `assets/answer/biasing-vs-finetuning-complementary-or-redundant/full_answer.md` before writing
   any results file, per the step spec's mandatory pre-write review.
2. Wrote `results/results_summary.md` with `## Summary`, `## Metrics` (7 bullets, each a specific
   number sourced from `results/ablation_metrics.json` / `results/mcnemar_results.json` /
   `results/clip_level_appendix.json`), and `## Verification`.
3. Wrote `results/results_detailed.md` with all 6 mandatory `spec_version: "2"` sections
   (`## Summary`, `## Methodology`, `## Verification`, `## Limitations`, `## Files Created`,
   `## Task Requirement Coverage` as the final section) plus the recommended `## Analysis` (with the
   required plan-assumption check), `## Visualizations` (all 3 charts embedded with descriptions),
   and the experiment-task-mandatory `## Examples` section (12 concrete input/output examples across
   contrastive, best-case, worst-case, boundary, and random categories, all in fenced code blocks
   copied verbatim from the committed JSONL/JSON files).
4. Performed the metrics cross-check: every number quoted in both markdown files was read directly
   from `results/ablation_metrics.json`, `results/mcnemar_results.json`, or
   `results/clip_level_appendix.json` — no re-derivation or rounding beyond the JSON's own
   precision.
5. Verified `results/costs.json` (`total_cost_usd: $14.37`, `azure-ml-2xh100` breakdown) and
   `results/remote_machines_used.json` (one `LLM-T1-NC80` entry, 1.029 hrs) against
   `logs/steps/008_setup-machines/machine_log.json` and `logs/steps/010_teardown/` — both consistent
   with the real teardown output from step 10; left unmodified, not overwritten.
6. Ran `uv run flowmark --inplace --nobackup` on both new markdown files.
7. Ran `verify_task_metrics` and `verify_task_results` via `run_with_logs` — both **PASSED** with 0
   errors, 0 warnings.

## Outputs

* `results/results_summary.md`
* `results/results_detailed.md`
* `logs/commands/*_verify-task-metrics.*`, `logs/commands/*_verify-task-results.*`

## Issues

No issues encountered. `results/metrics.json`, `results/costs.json`, and
`results/remote_machines_used.json` all already existed from prior steps (implementation and
teardown) and needed no changes — verified consistent rather than regenerated.
