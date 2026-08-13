# Task t0024 — Biasing Pareto Re-Analysis + Biasing-on-Fine-Tune Ablation

## Objective

Two self-contained sub-tasks that both deliberately avoid the two most expensive levers available to
this project right now — training a new model and collecting new held-out audio:

1. **Part A (zero compute):** re-analyze the param sweeps already collected in
   [[t0022_gpu_pb_diagnostic]] and [[t0023_tdt_vs_unified_biasing]] to surface the full
   `brand_exact_rate` vs `neutral_wer` tradeoff across the grid, not just the single
   max-`brand_exact_rate` cell each prior task headlined. Locate the true Pareto frontier for both
   `parakeet-tdt-0.6b-v3` and `parakeet-unified-en-0.6b`, and check where the current live
   production decoding config actually sits relative to it.
2. **Part B (one inference run, no training):** apply the existing tuned `malsd_batch` boosting
   config on top of the existing fine-tuned checkpoint from [[t0021_parakeet_finetune_vs_biasing]]
   and evaluate on the existing 21-clip clean production eval set — answering whether biasing and
   fine-tuning are complementary or redundant.

## Background

**Part A.** [[t0022_gpu_pb_diagnostic]] and [[t0023_tdt_vs_unified_biasing]] each ran a full 5×5×4
grid (`context_score` ∈ {1.0, 1.5, 2.0, 2.5, 3.0} × `alpha` ∈ {1.0, 1.5, 2.0, 2.5, 3.0} ×
`depth_scaling` ∈ {0.5, 1.0, 1.5, 2.0}, 100 cells) on gold-92's 35 brand clips + 10 neutral clips —
for `parakeet-unified-en-0.6b` (t0022) and `parakeet-tdt-0.6b-v3` (t0023) respectively. Both tasks
are inference-only against gold-92 (no training touches it), so there is no train/test contamination
concern anywhere in Part A.

Both tasks' `results_summary.md` / `comparison.md` reported only the single cell that maximized
`brand_exact_rate`, without systematically reporting how `neutral_wer` degrades across the grid. A
manual spot-check during this project's planning already found:

- The current live production defaults (confirmed in
  `brainpowa-realtime-api/src/brainpowa_realtime_api/config.py`:
  `parakeet_decoding_strategy = "malsd_batch"`, `parakeet_context_score = 3.0`,
  `parakeet_depth_scaling = 0.5`, `parakeet_boosting_alpha = 1.5`, deployed via `platform-fluxcd`
  `clusters/upper/spd-aks-primary-rail-up-westeurope-01/.../brainpowa-realtime-api.yaml`, no env
  override) sit at `brand_exact_rate=45.7%`, `neutral_wer=5.7%` on the TDT sweep
  (`tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`).
- That point is **dominated**: `context_score=2.5, depth_scaling=0.5, alpha=2.0` gives
  `brand_exact_rate=48.6%` at the *same* `neutral_wer=5.7%` — a strictly better operating point,
  already sitting in already-collected data.
- The "headline" numbers previously cited as the recommendation (TDT 60% at `cs=3.0/ds=0.5/α=3.0`,
  unified 69% at `cs=2.5/ds=0.5/α=2.5`) come at `neutral_wer` of 64.9% and 27.9% respectively — i.e.
  roughly every second (TDT) or every fourth (unified) non-brand word gets mangled. Neither prior
  task's verdict section weighted this cost explicitly.

This task formalizes that spot-check into a rigorous, complete analysis and a concrete
recommendation on production decoding defaults.

**Part B.** [[t0021_parakeet_finetune_vs_biasing]] found fine-tuning (`EA-DV=38%` on 21 clean clips)
far outperforms biasing alone (`EA-DV=0%` on the same clips) for `parakeet-unified-en-0.6b`. But the
fine-tuned model in that task was evaluated with NeMo's default decoding config — no
`change_decoding_strategy` call anywhere in
`tasks/t0021_parakeet_finetune_vs_biasing/code/run_finetuned.py` — so no boosting tree was ever
applied on top of the fine-tuned checkpoint. `run_clean_eval.py`'s `apply_boosting()` only touches
the non-fine-tuned model, and uses the old, since-superseded `greedy_batch` + `alpha=1.0` config
from t0015/t0017, not the `malsd_batch` + tuned-params fix from t0022/t0023. The combination
"fine-tune + malsd_batch + tuned boosting" has never been run. The fine-tuned model already fails
specifically on short clips and on "brainpowa" (t0021 §4) — exactly the failure modes a decode-time
boost might plausibly help with, since the model has never been shown a boosting tree at all.

## Constraints (both parts)

- No new model fine-tuning of any kind (TDT fine-tuning is tracked separately, out of scope here).
- No expansion of the 21-clip clean eval set
  (`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/`) — reuse it exactly as collected. Do
  not source additional production clips.
- Part A must not run any new inference. If an analysis question cannot be answered from
  `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
  `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`, note it as a limitation rather than
  launching a new sweep.

## Part A — Pareto Frontier Re-Analysis

### What to run

Pure data analysis, no GPU:

1. Load `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` (unified, 100 rows) and
   `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` (TDT, 100 rows).
2. For each model, compute the Pareto frontier over (`brand_exact_rate` maximized, `neutral_wer`
   minimized) across all 100 grid cells.
3. Plot `neutral_wer` (x) vs `brand_exact_rate` (y) as a scatter of all 100 cells per model, with
   the Pareto frontier highlighted and the current live production point (TDT,
   `cs=3.0/ds=0.5/α=1.5`) marked explicitly.
4. Locate where the current live production point falls relative to the frontier: on it, or
   dominated by which cell(s).
5. Write a recommendation: which `(context_score, depth_scaling, alpha)` cell should production use,
   given an explicit stance on how much `neutral_wer` regression is acceptable per
   `brand_exact_rate` point gained (state the stance — e.g. "prefer the frontier point with the
   least `neutral_wer` increase over current prod that still improves `brand_exact_rate`").

### Key questions

1. What is the full Pareto frontier (brand_exact_rate vs neutral_wer) for TDT and for unified?
2. Is the current live production config on the frontier? If not, which frontier cell strictly
   dominates it (equal or better on both axes)?
3. How much `neutral_wer` does each prior task's "headline" recommendation actually cost, laid next
   to the frontier?
4. Does the frontier change qualitatively between the two models (e.g. does unified reach higher
   brand_exact_rate before neutral_wer collapses, or does it collapse earlier)?

### Expected outputs

- `results/images/pareto_tdt.png`, `results/images/pareto_unified.png` — scatter + frontier plots
  per model, embedded in `results_detailed.md`.
- A table per model: frontier cells only, sorted by `neutral_wer` ascending, with `brand_exact_rate`
  and the delta vs the current live production point.
- One `answer` asset: recommendation on whether/how to update the production decoding defaults in
  `brainpowa-realtime-api/src/brainpowa_realtime_api/config.py`, referencing the exact
  `context_score`/`depth_scaling`/`alpha` to change to and why.

## Part B — Biasing on Top of the Existing Fine-Tuned Checkpoint

### What to run

One inference run on `gpu-azure`, reusing the existing checkpoint — no training:

1. Load the checkpoint from [[t0021_parakeet_finetune_vs_biasing]]:
   `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`.
2. Apply `change_decoding_strategy` with `malsd_batch` and the boosting config selected from Part A
   (the frontier point recommended for unified — do not default to the old t0022 headline point
   without checking Part A's answer first).
3. Transcribe the same 21 clips as
   `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/manifest.jsonl`.
4. Compute `wer`, `ea_dv`, and per-clip latency, using the same scoring method as
   `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` / `run_finetuned.py` so the
   three-way comparison is apples-to-apples.

### Eval set

The existing 21-clip clean set only — `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/`.
Do not modify or extend it.

### Comparison

Produce a single table with all three conditions on the same 21 clips (biased-only and
finetuned-only rows are copied from t0021's existing results, not re-run):

| Config | WER | EA-DV | Latency p50 |
| --- | --- | --- | --- |
| Biased only (no FT) — t0021 | 64.4% | 0.0% | — |
| Fine-tuned only (no biasing) — t0021 | 55.8% | 38.1% | 0.112s |
| **Fine-tuned + malsd_batch biasing (new)** | ? | ? | ? |

### Key questions

1. Does biasing on top of the fine-tuned checkpoint improve EA-DV beyond 38.1%, particularly on the
   short clips and the "brainpowa" clips t0021 identified as failure modes (t0021 §4)?
2. Does adding the boosting tree regress WER or latency relative to fine-tuned-only?
3. Is the combination complementary (better than either alone) or redundant (no improvement over
   fine-tuning alone, suggesting the fine-tuned model's failures are not boostable)?

### Expected outputs

- 1 `predictions` asset: 21-row JSONL, fine-tuned + biased transcripts on the clean eval set.
- Updated `answer` asset (shared with Part A, or a second one): verdict on whether biasing and
  fine-tuning are complementary, and an updated production recommendation if so.

## Limitations

- Both parts are explicitly scoped away from the two things that would most reduce uncertainty (more
  clean eval data, a from-scratch TDT fine-tune) — conclusions from Part B in particular should be
  read as directional given n=21, consistent with the caveats already logged in
  [[t0021_parakeet_finetune_vs_biasing]].
- Part A's Pareto frontier is only as good as the existing 35-brand-clip / 10-neutral-clip subset of
  gold-92 used by the t0022/t0023 sweeps — it does not re-derive the frontier on a larger sample.
