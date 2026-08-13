---
spec_version: "2"
answer_id: "production-decoding-and-biasing-ft-verdict"
answered_by_task: "t0024_biasing_pareto_and_ft_biasing_ablation"
date_answered: "2026-08-13"
confidence: "high"
---
## Question

Given the full Pareto frontier over brand_exact_rate vs neutral_wer for parakeet-tdt-0.6b-v3 and
parakeet-unified-en-0.6b, what production decoding defaults should brainpowa-realtime-api use, and —
evaluated on the 21-clip clean production set — are GPU-PB biasing and fine-tuning of
parakeet-unified-en-0.6b complementary or redundant?

## Short Answer

Ship `context_score=2.5, depth_scaling=0.5, alpha=2.0` as the production TDT decoding config: it
strictly dominates the current live-prod cell (`context_score=3.0, depth_scaling=0.5, alpha=1.5`),
gaining 2.9 percentage points of brand_exact_rate at zero extra neutral_wer cost. For
parakeet-unified-en-0.6b (not currently deployed), the frontier-selected cell under the same
ratio-threshold stance is `context_score=3.0, depth_scaling=0.5, alpha=1.5` (60.0% brand_exact_rate
at 8.7% neutral_wer). Whether biasing and fine-tuning are complementary or redundant is not answered
this round: the t0021 fine-tuned checkpoint and its `stt` conda environment could not be located on
any reachable machine, so the planned inference run never executed and this verdict is deferred
pending human resolution of that data-provenance gap.

## Research Process

This task (t0024) has two independent, self-contained sub-tasks. **Part A** re-analyzes the two
100-cell hyperparameter sweeps already collected by t0022 (`parakeet-unified-en-0.6b`,
`results/param_sweep.jsonl`) and t0023 (`parakeet-tdt-0.6b-v3`, `results/tdt_sweep.jsonl`) to
compute the true Pareto frontier over (`brand_exact_rate` maximized, `neutral_wer` minimized) for
each model, locate the live-prod TDT config relative to its frontier, and select one recommended
cell per model under an explicit, code-enforced marginal-ratio stance. **Part B** was planned to
apply t0023's `malsd_batch` boosting mechanism on top of t0021's fine-tuned checkpoint and evaluate
on the 21-clip clean production set, to determine whether biasing and fine-tuning are complementary
or redundant.

Step 8 (`setup-machines`) of this task provisioned and fully verified a GPU VM (`FT-MC`: SSH, 2x
H100 NVL, CUDA 12.2, repo synced), but neither the t0021 fine-tuned checkpoint
(`/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`) nor the `stt` conda environment
it requires exist on that VM or on any other reachable machine in the project's pool — the VM that
originally ran t0021's fine-tuning is no longer in the Azure pool, and the checkpoint is not
DVC-tracked or otherwise backed up in this repo. This is documented in full in
`tasks/t0024_biasing_pareto_and_ft_biasing_ablation/intervention/checkpoint_not_found.md`. The
project maintainer was consulted directly and decided: defer Part B entirely, proceed with Part A
only in this implementation round. `task.json`'s `expected_assets` was updated from
`{"predictions": 1, "answer": 1}` to `{"answer": 1}` to reflect this user-approved scope reduction —
Part B's `predictions` asset will not be produced until a future task/step resumes it with a located
checkpoint.

## Evidence from Papers

The `papers` method was not used. This task re-analyzes internal sweep data collected by prior
project tasks (t0021, t0022, t0023), not published literature — the Pareto-frontier algorithm and
the marginal-ratio selection stance are this task's own methodology, not derived from any paper
asset in `assets/paper/`.

## Evidence from Internet Sources

The `internet` method was not used — this task operates entirely on local sweep data already
collected by t0022/t0023 and, for the deferred Part B, t0021's existing checkpoint/eval-set
references.

## Evidence from Code or Experiments

Part A's evidence comes entirely from `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/`:

* `code/pareto.py` implements `pareto_frontier()` as a true non-dominated-point filter (O(n²)
  pairwise comparison over the 100 rows in each sweep, not a "sort by neutral_wer, keep increasing
  brand_exact_rate" single-pass scan, which can silently retain a dominated point when two rows
  share the same `neutral_wer` — both sweeps do). Running it produced:
  * **TDT frontier** (5 cells, from `tdt_sweep.jsonl`'s 100 rows): `cs=2.5/ds=0.5/α=1.5`
    (37.1%@3.7%), `cs=2.5/ds=0.5/α=2.0` (48.6%@5.7%), `cs=3.0/ds=0.5/α=2.0` (54.3%@16.7%),
    `cs=2.5/ds=0.5/α=2.5` (57.1%@22.4%), `cs=3.0/ds=0.5/α=3.0` (60.0%@64.9%). The current live-prod
    point (`cs=3.0/ds=0.5/α=1.5`, 45.7%@5.7%) is **not** on this frontier — it is dominated by
    `cs=2.5/ds=0.5/α=2.0`, which achieves higher `brand_exact_rate` at the identical `neutral_wer`.
  * **Unified frontier** (5 cells, from `param_sweep.jsonl`'s 100 rows): `cs=2.0/ds=0.5/α=1.5`
    (40.0%@2.7%), `cs=2.5/ds=0.5/α=1.5` (48.6%@4.4%), `cs=1.5/ds=0.5/α=2.5` (51.4%@7.7%),
    `cs=3.0/ds=0.5/α=1.5` (60.0%@8.7%), `cs=2.5/ds=0.5/α=2.5` (68.6%@27.9%).
  * `select_frontier_cell()` implements the stance: walking each frontier ascending by
    `neutral_wer`, accept a candidate as the new baseline only if it strictly increases
    `brand_exact_rate` over the current baseline AND the marginal ratio
    `Δneutral_wer / Δbrand_exact_rate` (against the current baseline, not necessarily the
    immediately-preceding row) is `<= 1.0`. Applied to TDT (baseline = live-prod point), this
    selects `cs=2.5/ds=0.5/α=2.0` (ratio `0/2.9 = 0.0` against live-prod; the next candidate
    `cs=3.0/ds=0.5/α=2.0` is rejected at ratio `≈1.93`). Applied to unified (baseline = its own
    lowest-`neutral_wer` frontier cell, since unified is not deployed), this selects
    `cs=3.0/ds=0.5/α=1.5` (accepted at ratio `≈0.377` against the last-accepted `48.6%@4.4%` point,
    after rejecting `cs=1.5/ds=0.5/α=2.5` at ratio `≈1.18`).
  * These numbers were independently re-derived by hand during planning (`plan/plan.md ## Approach`)
    and match the code's fresh computation exactly — confirmed by direct inspection of
    `results/pareto_tdt.json` and `results/pareto_unified.json` after running `code/pareto.py`, not
    merely trusted from a clean exit code.
  * Both prior tasks' "headline" cells (TDT `cs=3.0/ds=0.5/α=3.0`; unified `cs=2.5/ds=0.5/α=2.5`)
    are technically Pareto-optimal — the last row in each frontier list above — but sit at the
    extreme tail (`64.9%` and `27.9%` `neutral_wer` respectively, roughly 11x and 3x the selected
    cells' `neutral_wer`).
* `code/make_charts.py` produced `results/images/pareto_tdt.png` and
  `results/images/pareto_unified.png`, scatter-plotting all 100 cells per model with the frontier
  overlaid and (TDT only) the live-prod point marked; both files exist and are well over 10 KB.
* `results/frontier_tables.md` contains the full per-model frontier tables, the headline-cell-cost
  and frontier-shape-comparison prose, and a limitations note (the frontier is scoped to the
  35-brand/10-neutral clip subset of gold-92 that t0022/t0023 swept over, and t0022's raw sweep
  contains `neutral_wer` values above 100% at extreme dominated settings — a real ASR insertion
  phenomenon, not a computation bug).

Part B produced no evidence this round: no GPU inference ran, `results/clean_eval_ft_biased.jsonl`
was never created, and no `predictions` asset exists. `tasks/t0021_parakeet_finetune_vs_biasing`'s
own prior results remain the last available data point for biasing-only (WER 64.4%, EA-DV 0.0%) and
fine-tuning-only (WER 55.8%, EA-DV 38.1%) on the clean-21 set, but the third condition needed to
answer complementary-vs-redundant (fine-tuning + working `malsd_batch` biasing together) has never
been measured, because t0021's own boosting code only ever configured the broken `greedy_batch`
strategy (confirmed in this task's step 6 research).

## Synthesis

Part A's frontier re-analysis is a clean, self-contained, zero-compute correction to production
decoding defaults: the current live-prod TDT config is provably dominated by a frontier cell that
costs nothing extra in `neutral_wer`, so `brainpowa-realtime-api`'s decoding defaults should change
from `context_score=3.0, depth_scaling=0.5, alpha=1.5` to
`context_score=2.5, depth_scaling=0.5, alpha=2.0`. For the not-yet-deployed unified model,
`context_score=3.0, depth_scaling=0.5, alpha=1.5` is the frontier-selected cell under the identical
stance, and would be the boosting config for any future biasing-plus-fine-tuning run.

The second half of the original question — whether biasing and fine-tuning are complementary or
redundant — cannot be synthesized from existing evidence without fabrication. t0021's biasing-only
and fine-tuning-only numbers on clean-21 are known, but the fine-tuned+biased combination has never
actually been evaluated with a working boosting mechanism (t0021's own attempt used the broken
`greedy_batch` path), and this task's own attempt to run that evaluation was blocked by a genuine
data-provenance gap: the checkpoint and its runtime environment are not reachable on any machine in
the project's current pool. Guessing at a verdict here would misrepresent evidence that does not
exist. This question remains open and is explicitly deferred, not silently dropped — `task.json`'s
`expected_assets` was updated to reflect that only Part A's deliverables ship this round.

## Limitations

* **Part A scope**: the frontier is derived entirely from the 35-brand-clip / 10-neutral-clip subset
  of gold-92 that t0022's and t0023's 100-cell sweeps were run over. It is not a re-derivation on a
  larger sample, and this task ran no new inference to check the Pareto analysis against a different
  clip subset, per this task's constraint against launching new inference for Part A.
* **Part B is entirely unanswered this round**: the complementary-vs-redundant verdict requires a
  human to either locate the t0021 fine-tuned checkpoint (check whether the VM that trained it was
  renamed rather than deleted, or check for an export/backup) or accept it must be regenerated. See
  `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/intervention/checkpoint_not_found.md` for the
  full search record (filesystem search, conda env inventory, DVC-tracking check, and the separate
  stale-pool-config and DVC-auth findings it surfaced). Until that gap is resolved, no `predictions`
  asset or 3-row comparison table exists for this task, and this answer's coverage of the original
  question is partial by design, not by omission.

## Sources

* Task: [t0021 — Parakeet fine-tune vs. biasing][t0021]
* Task: [t0022 — GPU-PB diagnostic sweep][t0022]
* Task: [t0023 — TDT vs. unified biasing sweep][t0023]
* Task:
  [t0024 — this task, Pareto re-analysis (Part A) and deferred biasing-on-fine-tune ablation (Part B)][t0024]

[t0021]: ../../../t0021_parakeet_finetune_vs_biasing/
[t0022]: ../../../t0022_gpu_pb_diagnostic/
[t0023]: ../../../t0023_tdt_vs_unified_biasing/
[t0024]: ../../../t0024_biasing_pareto_and_ft_biasing_ablation/
