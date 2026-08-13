---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
updated_at: "2026-08-13T07:10:00Z"
completed_steps: 1
next_step_number: 2
next_step_id: "check-deps"
---
# Task Objective

Re-analyze existing t0022/t0023 biasing sweeps for the brand-accuracy/WER tradeoff, then test
biasing on top of the existing t0021 fine-tuned checkpoint.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0024_biasing_pareto_and_ft_biasing_ablation` created from `main` at `ad69aea`.
Worktree at `real-repos/rail-arf-stt-worktrees/t0024_biasing_pareto_and_ft_biasing_ablation`. Full
15-step plan written to `step_tracker.json` (research-papers, research-internet, creative-thinking,
compare-literature skipped — see step_tracker.json descriptions for why). Environment needed local
git identity, git-lfs, and pre-commit hook fixes (all resolved, logged in
`logs/steps/001_create-branch/branch_info.txt`).

* * *

## Cross-Step Decisions

- **Push access**: the default `GH_TOKEN` (vgorovoy) cannot push to `rezolved/rail-arf-stt` (403
  despite API-reported `push:true` — token scope gap, not a role gap). The coordinator configured
  `git remote set-url --push origin` with a working PAT (`rez-auto-research-write`, confirmed
  identity `vgorovoy` but different underlying token/scope) for this repo only (push URL only, fetch
  untouched). This is already in place in `.git/config`, shared by all worktrees — no further action
  needed by later steps, but if a step-executor hits a 403 on `git push`, this is the first thing to
  check (the override may need reapplying if `.git/config` was reset).
- **Dependency metadata caveat**: `t0021_parakeet_finetune_vs_biasing` and `t0022_gpu_pb_diagnostic`
  task.json both show `"status": "not_started"` despite having complete results committed on `main`.
  `t0023_tdt_vs_unified_biasing` task.json uses a legacy pre-spec schema unresolvable by
  `aggregate_tasks.py --ids`. This is a pre-existing data-quality issue in the repo, not something
  to fix here (never modify other tasks' folders). The actual files this task needs
  (`t0022/results/param_sweep.jsonl`, `t0023/results/tdt_sweep.jsonl`, `t0021/data/clean_eval/`, and
  the external checkpoint path referenced in t0021's `results_detailed.md`) are all present and
  readable by direct inspection regardless of the metadata staleness. `check-deps` (step 2) should
  verify functional availability of these files directly rather than treating a strict-metadata
  verificator failure as a hard blocker.

* * *

## Next Step Notes

Step 1 completed successfully. Proceed to step 2 (`check-deps`): verify the three dependency tasks'
functional outputs are present per the Cross-Step Decisions note above, and write `deps_report.json`
reflecting the real situation (files present and usable) rather than a fabricated clean pass if the
metadata verificator flags the status/schema issues.
