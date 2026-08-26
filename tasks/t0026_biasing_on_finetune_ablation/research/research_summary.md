# Research Summary — t0026_biasing_on_finetune_ablation

## Key Findings (top 10 insights directly actionable for this task)

1. `greedy_batch` silently ignores GPU-PB's boosting tree (0% brand EXACT regardless of config) —
   `malsd_batch` is mandatory for **all four arms**, including the unbiased A/C, to avoid
   confounding decoder-strategy with the biasing effect [t0022, t0023].
2. Biasing catastrophically fails to generalize: `t0021` measured EA-DV = 0.0% on 21 unseen clips vs
   34.8% on gold-92 (its own tuning set). Fine-tuning held up better: 38.1% unseen vs 93.2%
   contaminated gold-92. This motivates the whole ablation question [t0021].
3. Arm D (fine-tuned + biased) has never been run by any prior task. `t0021`'s finetuned eval used
   no decoding-strategy change at all; `t0024` Part B was scoped for exactly this but never executed
   (checkpoint/env unreachable, $14.06 burned for zero results) [t0021, t0024-pareto].
4. The biasing hyperparameter cell is already selected — do not re-sweep. Use
   `context_score=3.0, depth_scaling=0.5, alpha=1.5` (60.0% brand_exact_rate @ 8.7% neutral_wer)
   from `t0024`'s `results/pareto_unified.json` for arms B and D [t0024-pareto].
5. Two incompatible entity metrics exist: `t0021` uses loose `domain_vocab_accuracy` (substring
   match); `t0022`/`t0023` use strict `label_brand`/`brand_exact_rate` (regex, EXACT/PHONETIC/
   GARBAGE). `task_description.md` requires `brand_exact_rate` — reuse `t0022`/`t0023`'s family, not
   `t0021`'s.
6. No registered libraries exist in this project (`aggregate_libraries` returns 0). All reusable
   code must be **copied** into `tasks/t0026.../code/`, never imported cross-task — four prior tasks
   (`t0019`, `t0022`, `t0023` importing from `t0017`) already violate this rule; do not add a
   fifth/sixth.
7. Pull `parakeet-unified-v5` via DVC from `t0024_parakeet_unified_checkpoint_archive`'s model asset
   — do **not** use the old ephemeral `/mnt/finetune-checkpoints/...` path that caused the original
   `t0024` Part B blocker.
8. `clean_eval_v2/manifest.jsonl` contains absolute macOS paths
   (`/Users/margotiamanova/Desktop/...`) that must be rewritten relative to repo root before
   inference, without committing machine-specific paths back.
9. Task-status bookkeeping cannot be trusted: both `t0024_parakeet_unified_checkpoint_archive` and
   `t0019_parakeet_biasing_improvement` show `status` fields that contradict fully-populated
   `results/`/`code/` on disk. Verify assets on disk, not `task.json`, if any aggregator query
   returns suspiciously empty.
10. No McNemar precedent exists in this project (only `t0002`'s BCa bootstrap for continuous
    metrics). Implement fresh via `scipy.stats.binomtest(k, n, p=0.5)` on discordant pairs — `scipy`
    is already a dependency; do not add `statsmodels`.

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: Copy-and-adapt the t0022/t0023 boosting+scoring stack

Copy `apply_malsd_boost`, `label_brand`/`brand_in_ref`/`EXACT_PATTERNS`, `wer`, `build_phrase_list`,
and audio/transcribe helpers from `t0023_tdt_vs_unified_biasing/code/run.py` into this task's own
`code/`. This is the exact `brand_exact_rate`/`neutral_wer` metric family the task requires, and the
`apply_malsd_boost` signature applies unchanged to both `from_pretrained` (arm B) and `restore_from`
(arm D) models.

### Approach 2: Reuse precomputed Pareto data, not Pareto code

Read `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` directly as a
cross-task **data** read (allowed; only `code/` imports are restricted) for the selected cell and
the frontier array for chart 2's reference line — do not re-run `pareto.py`.

### Approach 3: Adapt existing chart code for 2 of 3 output charts

Adapt `t0024`'s `plot_pareto_chart` (frontier-overlay logic) for chart 2, and `t0014`'s
`generate_chart_b` (grouped bars + CI error bars) for chart 1 (brand_exact_rate by arm x bucket).
Chart 3 (2x2 per-clip correctness heatmap) has no precedent — implement fresh with
`matplotlib.pyplot.imshow`, small (<50 lines).

## Reusable Code / Assets

* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:281-299` — `apply_malsd_boost()`, ~19 lines, no
  adaptation needed.
* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:76-97,186-200` — brand-labeling constants +
  `label_brand`/`brand_in_ref`, ~35 lines, no adaptation.
* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:203-218` — dependency-free `wer()`, ~16 lines.
* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:221-240` — `build_phrase_list()`, ~20 lines.
* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:145-183` — `load_audio`/`transcribe`, ~40 lines,
  minor adaptation (resample should be a no-op but keep as guard).
* `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` — `DOMAIN_VOCAB` (31 terms), copy
  verbatim, do not import.
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` — precomputed
  frontier + selected cell; read as data, not code.
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py:39-99` —
  `plot_pareto_chart`, ~60 lines to adapt (4-arm points instead of 100-cell scatter).
* `tasks/t0014_granite_short_clip_robustness/code/generate_charts.py:114-171` — `generate_chart_b`,
  ~55 lines to adapt (brand-bucket x-axis, 4-arm offset).
* `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo`
  — DVC-tracked checkpoint for arms C/D; `dvc pull` then `ASRModel.restore_from()`.
* Not reusable: `tasks/t0002_baseline_evaluation/code/compute_metrics.py:353-410` —
  `compute_paired_significance` is a BCa bootstrap on continuous metrics, not McNemar on paired
  binary outcomes; reference only.

## Key Papers (top 5, with finding most relevant to this task)

(not generated — step skipped)

## Risks Flagged in Research

* Arm D (fine-tuned checkpoint + `malsd_batch` boosting via `restore_from()`) is an untested code
  combination — the single genuinely novel path in this task. Smoke-test with a `--limit 2` dry run
  before the full 91-clip x 4-arm sweep.
* `clean_eval_v2/manifest.jsonl` has absolute macOS paths that will break inference until rewritten
  relative to repo root.
* Re-sweeping the biasing hyperparameters is explicitly forbidden and would also likely be wasted
  effort — `t0019`'s sweep shows the cell is near a local optimum (far-from-default values wreck
  `neutral_wer` by 20-27pp).
* `t0021` has no `assets/` directory — its clean-21 biased/finetuned numbers are not available via
  the predictions/answer aggregators; must cite raw files (`data/clean_eval_comparison.json`, etc.)
  directly if compared against.
* Whether to finally promote the boosting/scoring helpers to a registered `library` (per
  `S-0024-05`, with `t0025` queued as a further consumer) is a real tradeoff to surface in
  `plan/plan.md`, not to resolve unilaterally in this task.

## Full Detail Available In

* `tasks/t0026_biasing_on_finetune_ablation/research/research_papers.md` — (not generated — step
  skipped)
* `tasks/t0026_biasing_on_finetune_ablation/research/research_internet.md` — (not generated — step
  skipped)
* `tasks/t0026_biasing_on_finetune_ablation/research/research_code.md` — 9 code references (13 prior
  tasks reviewed)
