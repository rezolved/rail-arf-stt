---
spec_version: "3"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
step_number: 12
step_name: "results"
status: "completed"
started_at: "2026-08-13T11:13:07Z"
completed_at: "2026-08-13T11:16:31Z"
---
## Summary

Wrote `results/results_summary.md`, `results/results_detailed.md`, `results/costs.json`, and
`results/remote_machines_used.json` for this task's completed Part A (Pareto-frontier re-analysis)
and deferred Part B (fine-tuned + biasing ablation), and re-verified `results/metrics.json` (already
`{}` from step 9). Both PNGs are embedded with descriptions. The `## Task Requirement Coverage`
section quotes `task.json`/`task_description.md` verbatim and marks all 27 `REQ-*` items from
`plan/plan.md`: Part A (`REQ-1`-`REQ-11`) Done, Part B (`REQ-12`-`REQ-21`) Not done with pointers to
`intervention/checkpoint_not_found.md`, shared/constraint REQs (`REQ-22`-`REQ-27`) Done or Partial
with an honest explanation for each partial.

## Actions Taken

1. Read `checkpoint.md` in full plus `intervention/checkpoint_not_found.md`, `task.json`,
   `task_description.md`, step 9's outputs (`results/frontier_tables.md`, `results/pareto_tdt.json`,
   `results/pareto_unified.json`, `results/metrics.json`, both chart PNGs, the `answer` asset), and
   `logs/steps/008_setup-machines/machine_log.json` (real FT-MC cost figures: 1.0075 hrs, $14.06).
2. Read `arf/skills/execute-task/SKILL.md`'s `results` step instructions (Phase 5) and
   `arf/specifications/task_results_specification.md` in full for the mandatory section lists, the
   metrics cross-check requirement, the chart-embedding requirement, and the
   `## Task Requirement Coverage` requirements.
3. Read `plan/plan.md`'s `## Task Requirement Checklist` (`REQ-1` through `REQ-27`) to build the
   coverage table.
4. Confirmed no registered project metric (`entity_accuracy_gold92`, `wer_gold92`,
   `latency_p50_seconds`, etc. — all scoped to the full 92-clip gold-92 benchmark) applies to Part
   A's re-analysis of a 45-clip sweep subset; left `results/metrics.json` as `{}`.
5. Wrote `results/remote_machines_used.json` (one entry, `FT-MC`, sourced directly from
   `machine_log.json`) and `results/costs.json` (`total_cost_usd: 14.06`, honest `note` documenting
   this as a Part B sunk cost, not a Part A cost).
6. Wrote `results/results_summary.md` and `results/results_detailed.md`, including the required
   "Plan assumption check" prominently under `## Analysis` (the plan assumed Part B was a routine,
   low-risk run with the checkpoint "confirmed present"; that assumption was contradicted by a
   provenance failure the plan's risk table never anticipated).
7. Ran `uv run flowmark --inplace --nobackup` on both new markdown files; caught and fixed a
   self-introduced unbalanced-backtick bug in the first `flowmark` pass (a stray extra backtick in
   one sentence caused the formatter to merge subsequent text into a runaway inline-code span,
   stripping spacing) by rewriting that sentence cleanly, then re-ran `flowmark` clean.
8. Ran `verify_task_results.py` and `verify_task_metrics.py` (both wrapped in `run_with_logs.py`) —
   both **PASSED** with 0 errors, 0 warnings.

## Outputs

- `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/results_summary.md`
- `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/results_detailed.md`
- `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/costs.json`
- `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/remote_machines_used.json`

## Issues

One self-introduced markdown formatting bug (unbalanced backticks causing `flowmark` to mangle a
paragraph's spacing) was found and fixed before committing — see Actions Taken item 7. No other
issues encountered.
