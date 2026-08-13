---
spec_version: "3"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
step_number: 6
step_name: "research-code"
status: "completed"
started_at: "2026-08-13T07:35:51Z"
completed_at: "2026-08-13T07:42:12Z"
---
## Summary

Reviewed t0021's `run_finetuned.py` / `run_clean_eval.py` (`apply_boosting`, scoring functions) and
t0022/t0023's sweep code, then wrote `research/research_code.md` and the compressed
`research/research_summary.md` so Part A's frontier analysis and Part B's inference run reuse the
exact same scoring method and reference the correct checkpoint/config paths.

## Actions Taken

1. Spawned a subagent to execute the `/research-code` skill. It surveyed the library aggregator (0
   libraries registered project-wide), the task aggregator, and 6 relevant prior tasks (`t0001`,
   `t0017`, `t0019`, `t0021`, `t0022`, `t0023`), then wrote
   `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_code.md`. The subagent
   independently recomputed the Pareto frontier from both sweep JSONLs and confirmed the manual
   spot-check in `task_description.md` exactly (current-prod TDT point dominated by
   `cs=2.5/ds=0.5/α=2.0`).
2. Ran
   `uv run python -u -m arf.scripts.verificators.verify_research_code t0024_biasing_pareto_and_ft_biasing_ablation`
   via `run_with_logs.py` — PASSED, zero errors or warnings.
3. Independently re-verified (outside the subagent) the specific claims this step exists to confirm:
   `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
   `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` each have exactly 100 rows with the
   schema `{context_score, depth_scaling, alpha, brand_exact_rate, neutral_wer}`; the current-prod
   TDT cell (`cs=3.0/ds=0.5/α=1.5`) in `tdt_sweep.jsonl` reads
   `brand_exact_rate=0.457, neutral_wer=0.057`, matching `task_description.md` exactly;
   `t0021/code/paths.py` confirms
   `FINETUNED_NEMO = /mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`; `t0021`'s
   `apply_boosting()` (lines 126-135 of `run_clean_eval.py`) only ever sets
   `strategy = "greedy_batch"` and writes to `greedy.boosting_tree.*`, never `malsd_batch`;
   `t0023`'s `apply_malsd_boost()` (lines 281-299 of `code/run.py`) is the correct `malsd_batch` +
   `beam.boosting_tree.*` implementation Part B must copy in. Could not independently re-verify the
   live production `brainpowa-realtime-api/src/brainpowa_realtime_api/config.py` decoding-default
   values cited in `task_description.md` — that repo is not cloned into this sandbox/worktree; the
   values are taken as given from the task description's stated prior verification.
4. Spawned a second subagent to execute the `/research-summarize` skill, producing
   `research/research_summary.md` (93 lines, 7.6 KB — within the 200-line/8KB budget) as the compact
   research artifact for the planning and implementation subagents.

## Outputs

* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_code.md`
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_summary.md`
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/logs/commands/003_20260813T074039Z_uv-run-python.*`
  (verificator run log)

## Issues

No issues encountered. One verification gap noted: the live production
`brainpowa-realtime-api/config.py` values cited in `task_description.md` could not be independently
re-read from this sandbox (repo not present here); downstream steps should treat those specific
numbers as unverified-in-this-worktree if precision matters, though they are not load-bearing for
either Part A (uses the sweep JSONLs, not the config file) or Part B (uses the frontier point, not
the literal current-prod value).
