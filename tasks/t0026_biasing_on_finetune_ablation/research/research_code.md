---
spec_version: "1"
task_id: "t0026_biasing_on_finetune_ablation"
research_stage: "code"
tasks_reviewed: 13
tasks_cited: 9
libraries_found: 0
libraries_relevant: 0
date_completed: "2026-08-26"
status: "complete"
---
## Task Objective

t0026 runs a clean 2x2 ablation of GPU-PB context biasing x `parakeet-unified` fine-tuning on the
91-clip `clean_eval_v2` holdout: arm A (base model, no bias), arm B (base + bias), arm C (fine-tuned
`parakeet-unified-v5`, no bias), arm D (fine-tuned + bias). All four arms decode with `malsd_batch`
and, for B/D, the frontier-selected biasing cell `context_score=3.0, depth_scaling=0.5, alpha=1.5`
from `t0024` Part A — that cell is held fixed, not re-swept. The task completes the deferred Part B
of `t0024_biasing_pareto_and_ft_biasing_ablation` (verdict never reached because the fine-tuned
checkpoint and its runtime environment could not be located at the time), now unblocked by
`t0024_parakeet_unified_checkpoint_archive`'s DVC-registered `parakeet-unified-v5` model asset and
`t0021`'s new 91-clip decontaminated `clean_eval_v2` set. The question: is context biasing
complementary to fine-tuning (arm D beats both B and C) or redundant (arm D lands within noise of
`max(B, C)`), reported with a paired McNemar test per `task_description.md`'s Key Questions 1-5.

## Library Landscape

`uv run python -u -m arf.scripts.aggregators.aggregate_libraries --format json --detail short`
returns `{"library_count": 0, "libraries": []}` — **zero libraries are registered in this project**.
This confirms, empirically, that `S-0024-05`'s recommendation to promote the repeatedly-duplicated
boosting/scoring helpers (`apply_malsd_boost`, `DOMAIN_VOCAB`, `label_brand`/`brand_in_ref`, `wer`)
to a registered `library` asset has not been acted on by any of the five tasks that have needed this
code since (`t0017`, `t0019`, `t0021`, `t0022`, `t0023`). There is therefore **no import-via-library
path available for this task** — every piece of prior boosting/scoring code identified below must be
copied into `tasks/t0026_biasing_on_finetune_ablation/code/`, per the ARF cross-task reuse rule
(only registered libraries may be imported across task folders; this task should not add a sixth ad
hoc cross-task `code/` import to the four that already exist — see Key Findings below). Whether
*this* task should be the one to finally promote a library is a planning-stage tradeoff (one-time
authoring cost vs. the certainty that a sixth consumer, `t0025_parakeet_tdt_brand_finetune`, is
already queued and would benefit) — flagged in Recommendations, not decided here.

`aggregate_answers --format json --detail short` returns 4 answer assets; the most relevant is
`production-decoding-and-biasing-ft-verdict` (created by
`t0024_biasing_pareto_and_ft_biasing_ablation`) — its `short_answer` field states the Part-B verdict
was "deferred pending human resolution of that data-provenance gap" and gives the exact frontier
cell this task must reuse for the unified model: `context_score=3.0, depth_scaling=0.5, alpha=1.5`
(60.0% `brand_exact_rate` @ 8.7% `neutral_wer`). The other three answers
(`granite-vs-parakeet-production-fit`, `parakeet-unified-vs-tdt-production-fit`,
`parakeet-unified-biasing-improvement`) concern model-family and hyperparameter-improvement
questions already resolved by earlier tasks and are not directly actionable for this ablation, but
the last one documents that GPU-PB hyperparameter tuning beyond the current cell is a proven dead
end (see Key Findings) — reinforcing the task's own constraint not to re-sweep.

## Key Findings

### `malsd_batch` is a hard requirement — `greedy_batch` silently ignores the boosting tree

`t0022_gpu_pb_diagnostic`'s decoding matrix (`results/summary.md`) found `greedy_batch` + GPU-PB
produces **0% brand EXACT** identically to `greedy_batch` with no boosting at all — the boosting
tree is simply not consulted by that decoding strategy. Switching to `malsd_batch` (beam-based,
boosting tree wired through `beam.boosting_tree.*`) raised brand EXACT to 60% (21/35) with the tuned
cell [t0022]. `t0023_tdt_vs_unified_biasing` reproduced the same greedy-vs-malsd_batch gap on the
TDT model [t0023]. This is exactly why `task_description.md` mandates `malsd_batch` for **all four
arms**, including the two unbiased ones (A, C) — pairing "no bias" with `greedy_batch` would
confound the decoder-strategy change with the biasing effect. This project convention is directly
traceable to `t0022`'s diagnostic, not an arbitrary choice.

### Biasing catastrophically fails to generalize off its tuning set — fine-tuning does not

`t0021_parakeet_finetune_vs_biasing`'s clean-eval results are the single most load-bearing prior
finding for this task: on 21 unseen production clips (no train/gold-92 overlap), GPU-PB biasing
alone scored **EA-DV = 0.0%** — it never once produced "Rezolve" or "brainpowa" correctly, despite
scoring 34.8% EA-DV on gold-92 with the same config [t0021]. The fine-tuned checkpoint, run with
**no boosting at all** (`run_finetuned.py` never calls `model.change_decoding_strategy()`), scored
EA-DV = 38.1% on the same 21 clips [t0021]. This is the direct motivation for t0026's Q1/Q2:
biasing's apparent 34.8% gold-92 number looks like it may be an artifact of gold-92 itself (all 93
clips are the sweep-tuning set the biasing hyperparameters were selected against in
`t0022`/`t0023`), while fine-tuning's gain held up out-of-sample. Whether biasing *on top of* the
fine-tuned model still adds anything on `clean_eval_v2` (91 clips, a superset built from the same 21
clean clips plus 74 new `quepasa_prod` clips per `task_description.md`) is exactly the open question
this task answers.

### Fine-tuned + biased has never been run — t0021's finetuned eval used the wrong (or no) decoding

config

`t0021`'s `run_finetuned.py` restores `parakeet-unified-finetuned-best.nemo` via
`nemo_asr.models.ASRModel.restore_from()` and immediately calls `.transcribe()` with no decoding
strategy change — pure NeMo defaults, no boosting tree at all [t0021]. Its sibling
`run_clean_eval.py` does call `apply_boosting()` on the **base** (non-fine-tuned) model, but with
the stale `t0015`/`t0017` defaults (`alpha=1.0, context_score=1.0, depth_scaling=2.0`, strategy
forced to `greedy_batch`) — the config `t0022` later proved ineffective, not the `malsd_batch` +
`context_score=3.0/depth_scaling=0.5/ alpha=1.5` cell this task must use [t0021].
`t0024_biasing_pareto_and_ft_biasing_ablation`'s Part B was scoped to close exactly this gap
(fine-tuned checkpoint + tuned `malsd_batch` boosting) but never executed — `results_summary.md`
states "0 of 9 planned Part-B requirements... deferred, not attempted, after $14.06 of GPU
provisioning found neither the checkpoint nor its runtime environment reachable" [t0024-pareto]. So
arm D of this task is, concretely, the first time anyone applies a boosting tree to a restored
fine-tuned checkpoint in this project — see Recommendations for the implementation implication.

### The Pareto cell selection is already computed — do not re-derive it

`t0024_biasing_pareto_and_ft_biasing_ablation`'s Part A computed the true non-dominated-point
frontier over the existing 100-cell sweeps from `t0022` (unified) and `t0023` (TDT) via
`pareto_frontier()` and `select_frontier_cell()` (`code/pareto.py:98-151`), and wrote the selected
unified cell — `context_score=3.0, depth_scaling=0.5, alpha=1.5` at 60.0% `brand_exact_rate` / 8.7%
`neutral_wer` — to `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json`,
along with the full non-dominated `frontier` array needed to draw the reference line for this task's
output chart 2 (`neutral_wer` vs `brand_exact_rate` scatter with the unified Pareto frontier
overlaid) [t0024-pareto]. `task_description.md` explicitly forbids re-sweeping this cell ("not
re-swept... Re-tuning it on the FT checkpoint would confound the ablation and burn GPU hours"), and
`t0019_parakeet_biasing_improvement` independently confirms hyperparameter re-tuning is a proven
dead end: near-default sweep values move nothing, far-from-default values wreck `neutral_wer` by
20-27 absolute points from over-boosting [t0019]. This task should load `pareto_unified.json`
directly rather than importing or re-running `pareto.py`.

### Boosting/scoring helpers are duplicated across five tasks, and the duplication has already caused

a real bug

`task_description.md` cites this directly: "`apply_beam_boosting` / `apply_malsd_boost`,
`DOMAIN_VOCAB`, and the `normalise`/`wer`/`domain_vocab_accuracy` scoring functions have been
duplicated across t0017, t0019, t0021, t0022, and t0023 already, which is how the
`malsd_batch`-vs-`greedy_batch` bug failed to propagate between copies." This is verifiable in the
code: `t0022_gpu_pb_diagnostic/code/diagnostic.py` defines `apply_beam_boosting()`
(`diagnostic.py:234-249`) with the identical body to `t0023_tdt_vs_unified_biasing/code/run.py`'s
`apply_malsd_boost()` (`run.py:281-299`) — same OmegaConf calls, different function name, no shared
source [t0022][t0023]. Separately, `DOMAIN_VOCAB` is byte-identical between
`t0017_parakeet_biasing_buffer_replacement/code/constants.py` and
`t0021_parakeet_finetune_vs_biasing/code/constants.py` (verified via `diff`), yet `t0021` keeps its
own copy while `t0022`, `t0023`, and `t0019` instead `import` directly from `t0017`'s `code/` module
(`from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import DOMAIN_VOCAB` — present
in `t0022/code/diagnostic.py:65-67`, `t0023/code/run.py:64-67`, and three files in `t0019/code/`)
[t0017][t0022][t0023][t0019]. **These four cross-task `code/` imports already violate the ARF rule
that only registered `library` assets may be imported across task folders** — they work today only
because `t0017`'s module happens to be importable Python, not because it is a sanctioned reuse path.
This task must not extend that pattern to a fifth or sixth import; the correct move is to copy the
needed functions into `tasks/t0026_biasing_on_finetune_ablation/code/`.

### Two incompatible entity-accuracy metrics exist in the codebase — use the `brand_exact_rate` family,

not `domain_vocab_accuracy`

`t0021`'s scoring (`code/run_clean_eval.py`, `code/run_finetuned.py`) uses `domain_vocab_accuracy()`
— a **fractional** score: `matched_terms / present_terms` per clip, where "matched" means the
normalized term string appears anywhere in the normalized hypothesis (loose substring match, not
exact) [t0021]. `t0022`/`t0023`'s scoring instead uses a strict per-brand classifier —
`label_brand()` returns `EXACT`/`PHONETIC`/`GARBAGE` via compiled regex patterns (`EXACT_PATTERNS`,
word-boundary anchored), and `brand_exact_rate` is the fraction of brand-containing clips labeled
`EXACT` [t0022][t0023]. These are not the same metric and are not directly comparable: `t0021`'s
clean-eval EA-DV=38.1% and `t0022`/`t0023`'s brand_exact_rate=60.0% describe different scoring
functions on different clip sets. `task_description.md`'s Metrics section names `brand_exact_rate`
explicitly — this task must reuse the `t0022`/`t0023` scoring family (`label_brand`, `brand_in_ref`,
`EXACT_PATTERNS`), not `t0021`'s `domain_vocab_accuracy`, even though `t0021` is the closest prior
task by subject matter.

### Status-field false negatives are common in this project — verify assets on disk, not just

`task.json`

Both direct dependencies of this task have shown this failure mode. `checkpoint.md` step 2 already
documents `t0024_parakeet_unified_checkpoint_archive` being stuck at `status: not_started` despite
its model asset being fully merged to `main` — corrected via a metadata-only commit on `main`
(`e755ef4`) [t0024-archive]. Independently, `t0019_parakeet_biasing_improvement/task.json` also
reports `status: "not_started"`, yet its `code/` directory contains 7 populated scripts and its
`results/` directory contains 6 populated result files (`hyperparam_sweep.jsonl`,
`hyperparam_top2_full93.json`, `phrase_expansion_full93.json`, `posthoc_replacement_check.json`,
plus an `images/` folder), and the answer aggregator serves a fully-formed, high-confidence answer
asset (`parakeet-unified-biasing-improvement`) attributed to it [t0019]. This is not relevant to
this task's own dependency chain (t0019 is not a t0026 dependency), but it is a second independent
confirmation of the same false-negative pattern noted for
`t0024_parakeet_unified_checkpoint_archive` — worth keeping in mind if any other aggregator query in
this task's planning/implementation stages returns a suspiciously-empty result for a task that
"should" have output.

## Reusable Code and Assets

All items below are **copy into task** (no registered libraries exist — see Library Landscape).

* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py:281-299` —
  `apply_malsd_boost(model, phrases, *, alpha, context_score, depth_scaling) -> None`. Sets
  `strategy="malsd_batch"`, `beam.beam_size=4`, and the three boosting-tree OmegaConf keys via
  `model.change_decoding_strategy`. **Adaptation**: none needed for arms B and D — same call
  signature applies whether `model` was loaded via `from_pretrained` (arm B) or `restore_from` (arm
  D, untested combination — see Key Findings). ~19 lines.
* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py:76-97, 186-200` — `TARGET_BRANDS`,
  `BRAND_VARIANTS`, `PHONETIC_PATTERNS`, `EXACT_PATTERNS`, `TERM_FILTER`,
  `label_brand(hyp, brand) -> str`, `brand_in_ref(ref) -> str | None`. This is the exact
  `brand_exact_rate` scoring apparatus `task_description.md` requires (EXACT/PHONETIC/GARBAGE
  classification per brand mention). **Adaptation**: none — Rezolve/brainpowa patterns are
  project-wide constants. ~35 lines.
* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py:203-218` —
  `wer(ref: str, hyp: str) -> float`, a dependency-free word-level Levenshtein WER (regex tokenizer
  `[a-z0-9']+`, no `jiwer` needed). Used for `neutral_wer`. **Adaptation**: none. ~16 lines.
* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py:221-240` — `_expand_casing_variants`,
  `build_phrase_list() -> list[str]` (merges `DOMAIN_VOCAB` + `BRAND_VARIANTS`, expands casing).
  Builds the `key_phrases_list` passed into `apply_malsd_boost`. **Adaptation**: none. ~20 lines.
* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py:145-183` —
  `load_audio(path) -> np.ndarray` (mono conversion + `soxr` resample to 16kHz),
  `transcribe(model, clips) -> list[str]`, `_decode_output`. **Adaptation**: minor — `clean_eval_v2`
  clips are already 16kHz per `t0021`'s DVC audio, so the resample branch should be a no-op but keep
  it as a guard. ~40 lines.
* **Source**: `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` —
  `DOMAIN_VOCAB: list[str]` (31 terms, byte-identical to `t0017`'s copy). **Adaptation**: none, copy
  verbatim. ~35 lines. Do **not** import this cross-task (see Key Findings on the existing rule
  violation) — copy it fresh.
* **Source**: `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` — the
  precomputed `ParetoReport` (frontier array + `selected_cell` =
  `context_score=3.0, depth_scaling=0.5, alpha=1.5`, `brand_exact_rate=0.6`, `neutral_wer=0.087`).
  **Reuse method**: read the JSON file directly as a cross-task **data** read (not a code import —
  reading another task's `results/` output is not the restricted path; only importing from another
  task's `code/` package is). Use `frontier` for chart 2's reference-line overlay and
  `selected_cell` for the arm B/D hyperparameters, instead of re-deriving via `code/pareto.py`.
* **Source**: `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py:39-99` —
  `plot_pareto_chart(*, sweep_path, report_path, out_path, title, show_live_prod)`. Matplotlib
  scatter (all cells, gray) + frontier line (red) + optional starred reference point, `Agg` backend.
  **Reuse method**: copy into task and adapt — this task's chart 2 plots 4 arm points (not a
  100-cell sweep) against the same frontier-line data source; the frontier-overlay logic (lines
  61-69) is directly reusable, the "all cells" scatter (lines 51-60) should be replaced with the 4
  arm points. ~60 lines to adapt.
* **Source**: `tasks/t0014_granite_short_clip_robustness/code/generate_charts.py:114-171` —
  `generate_chart_b`, a grouped bar chart with per-group offset bars, CI error bars via
  `yerr=[lo, hi]`, and `ax.legend()`/`ax.set_xticklabels()` idioms. **Reuse method**: copy into task
  and adapt for this task's output chart 1 (arm A/B/C/D grouped by brand bucket:
  overall/Rezolve/brainpowa) — swap the duration-stratum x-axis for the brand-bucket x-axis and the
  2-model bar offset for a 4-arm offset. ~55 lines to adapt.
* **Source**:
  `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo`
  (DVC-tracked, `dvc pull` required). **Reuse method**: pull via DVC (model asset, not code) — this
  is the fine-tuned checkpoint for arms C/D. Load with
  `nemo.collections.asr.models.ASRModel.restore_from(str(path))`, same call `t0021`'s
  `run_finetuned.py` used. **Do not** use the old `/mnt/finetune-checkpoints/...` path from
  `t0021`'s `code/paths.py` — that is ephemeral local disk on the pool VM and is exactly what caused
  the original `t0024` Part B blocker (checkpoint not found on any reachable machine).
* **Not reusable, reference only**:
  `tasks/t0002_baseline_evaluation/code/compute_metrics.py:353-410` —
  `compute_paired_significance()`, a paired BCa bootstrap significance test. This is the only
  existing paired-significance-testing code in the project, but it is a bootstrap test on continuous
  metrics, not a McNemar test on paired binary outcomes — `task_description.md` explicitly asks for
  McNemar on per-clip brand correctness. No prior task implements McNemar; see Recommendations.

## Lessons Learned

`t0022`'s diagnostic proved GPU-PB is silently inert under `greedy_batch` (0% brand EXACT with or
without a boosting tree) and only becomes effective under `malsd_batch` — a decoding-strategy
requirement now baked into `task_description.md` for all four of this task's arms [t0022]. `t0019`'s
hyperparameter sweep independently confirmed the current cell is near a local optimum: values far
from `context_score=3.0/depth_scaling=0.5/alpha=1.5` wreck `neutral_wer` by 20-27 absolute points,
so re-sweeping on the fine-tuned checkpoint would very likely just rediscover the same instability
without new information — reinforcing `task_description.md`'s explicit instruction not to re-tune
[t0019]. `t0021`'s clean-eval run is the strongest evidence in this project that GPU-PB biasing
overfits its own tuning set: 34.8% EA-DV on gold-92 (the set the sweep was tuned against) collapsed
to 0.0% EA-DV on 21 unseen production clips, while fine-tuning held up better (93.2% contaminated
gold-92 vs 38.1% unseen) [t0021]. `t0024` Part B's total failure — $14.06 spent with zero results
because the checkpoint and its `stt` conda environment were unreachable from the acquired machine —
is the direct reason `task_description.md` now mandates pulling the checkpoint via the
DVC-registered model asset rather than a machine-local path, and is why
`t0024_parakeet_unified_checkpoint_archive` exists as a prerequisite at all
[t0024-pareto][t0024-archive]. Two separate `task.json` status-field false negatives
(`t0024_parakeet_unified_checkpoint_archive`, `t0019_parakeet_biasing_improvement`) show this
project's bookkeeping cannot always be trusted at face value; assets on disk are the source of truth
[t0024-archive][t0019].

## Recommendations for This Task

1. **Copy, do not import, the scoring/boosting helpers** from
   `tasks/t0023_tdt_vs_unified_biasing/ code/run.py` (`apply_malsd_boost`, brand-labeling
   constants/functions, `wer`, phrase-list builders, audio/transcribe helpers) into this task's own
   `code/` directory. This is the `brand_exact_rate` / `neutral_wer` metric family
   `task_description.md` requires — not `t0021`'s `domain_vocab_accuracy`, which is a different,
   looser metric.
2. **Do not re-run the Pareto sweep.** Load `context_score=3.0, depth_scaling=0.5, alpha=1.5` and
   the `frontier` array straight from
   `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/ results/pareto_unified.json` for arms B/D's
   biasing config and for chart 2's frontier reference line, per `task_description.md`'s explicit
   constraint against re-tuning.
3. **Pull `parakeet-unified-v5` via DVC**, not a machine-local `/mnt` path — `dvc pull` the model
   asset at
   `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/`.
   Restore with `ASRModel.restore_from()` exactly as `t0021/code/run_finetuned.py` did, then apply
   `apply_malsd_boost()` to the restored model for arm D — this exact combination (fine-tuned
   checkpoint + explicit `malsd_batch` decoding-strategy change) has never been exercised by any
   prior task in this project and is the one genuinely novel code path here; treat it as the primary
   implementation risk and smoke-test it first (`--limit 2`-style dry run) before the full 91-clip x
   4-arm sweep.
4. **Fix `clean_eval_v2/manifest.jsonl`'s absolute macOS paths**
   (`/Users/margotiamanova/Desktop/...`, confirmed present in the file) before any inference —
   rewrite `audio_filepath` relative to the repo root and do not commit the machine-specific paths
   back, per `task_description.md`'s prerequisite step.
5. **Reuse chart-building patterns rather than writing from scratch**: adapt
   `t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py`'s `plot_pareto_chart` for
   output chart 2 (scatter + frontier), and
   `t0014_granite_short_clip_robustness/code/generate_charts.py`'s `generate_chart_b`
   grouped-bar-with-error-bars pattern for output chart 1 (brand_exact_rate by arm x bucket). The
   2x2 per-clip correctness heatmap (output chart 3) has no prior-task precedent in this project —
   implement it fresh with `matplotlib.pyplot.imshow` over a 2x2 count matrix; it is small (well
   under 50 lines) and does not warrant searching further.
6. **Implement McNemar fresh** — no prior task in this project has paired binary-outcome
   significance testing. `scipy` is already a project dependency (`pyproject.toml:45`,
   `scipy>=1.0`); `statsmodels` (which has `statsmodels.stats.contingency_tables.mcnemar`) is not
   installed. The exact McNemar test is a one-liner over the discordant-pair count via
   `scipy.stats.binomtest(k, n, p=0.5)` — do not add `statsmodels` as a new dependency for this; the
   ladder stops at stdlib/already-installed here.
7. **Do not extend the existing cross-task `code/` import pattern.** `t0019`, `t0022`, and `t0023`
   already import `DOMAIN_VOCAB` directly from `t0017`'s `code/` package, which violates the ARF
   cross-task reuse rule (only registered `library` assets may cross task boundaries). This task
   should copy `DOMAIN_VOCAB` fresh rather than adding a fifth/sixth such import. Whether to finally
   promote a shared library per `S-0024-05` — given `t0025_parakeet_tdt_brand_finetune` is already
   queued as a further consumer — is a real tradeoff worth surfacing explicitly in `plan/plan.md`,
   but is a planning decision, not something to resolve unilaterally here.
8. **Gap to flag for planning**: `t0021` has no `assets/` directory at all — its predictions and
   comparison outputs live as plain files under `data/`, not as registered `predictions`/`answer`
   assets. This task cannot pull `t0021`'s biased-only or finetuned-only numbers via the
   predictions/ answer aggregators; any comparison to `t0021`'s clean-21 subset numbers must cite
   the raw JSONL/JSON files directly (`data/clean_eval_comparison.json`,
   `data/clean_eval_biased.jsonl`, `data/clean_eval_finetuned.jsonl`).

## Task Index

### [t0017]

* **Task ID**: `t0017_parakeet_biasing_buffer_replacement`
* **Name**: Parakeet unified vs TDT — biased accuracy, latency, fine buffer sweep
* **Status**: completed
* **Relevance**: Original source of `DOMAIN_VOCAB` (`code/constants.py`), imported cross-task by
  three later tasks; established `parakeet-unified-en-0.6b` as the model family this task fine-tunes
  and biases.

### [t0019]

* **Task ID**: `t0019_parakeet_biasing_improvement`
* **Name**: Parakeet-unified biasing improvement
* **Status**: not_started (bookkeeping false negative — code and results exist and appear complete)
* **Relevance**: Confirms GPU-PB hyperparameter re-tuning beyond the current cell is a dead end
  (near-default = no effect, far-from-default = 20-27pp WER regression) — supports this task's
  constraint against re-sweeping the biasing cell.

### [t0021]

* **Task ID**: `t0021_parakeet_finetune_vs_biasing`
* **Name**: Parakeet fine-tune vs biasing — parakeet-unified on gold-92
* **Status**: completed
* **Relevance**: Direct dependency. Supplies `clean_eval_v2` (91 clips, superset built from this
  task's 21-clip clean set), the original `DOMAIN_VOCAB` copy, and the only prior
  fine-tuned-vs-biased comparison (finding biasing fails to generalize off-distribution while
  fine-tuning partially does).

### [t0022]

* **Task ID**: `t0022_gpu_pb_diagnostic`
* **Name**: GPU-PB biasing diagnostic — parakeet-unified brand recognition failure
* **Status**: completed
* **Relevance**: Established `malsd_batch` as required for GPU-PB to have any effect, and produced
  the 100-cell hyperparameter sweep that `t0024` Part A's Pareto frontier (reused by this task) is
  built from. Source of the `brand_exact_rate`/`label_brand` scoring family this task must reuse.

### [t0023]

* **Task ID**: `t0023_tdt_vs_unified_biasing`
* **Name**: TDT vs Unified — GPU-PB biasing comparison on gold-92
* **Status**: completed (legacy pre-`spec_version` `task.json`, invisible to the task/dependency
  aggregators per `S-0024-06` — read directly from `tasks/t0023_tdt_vs_unified_biasing/`)
* **Relevance**: Primary source of the reusable `apply_malsd_boost`, brand-labeling, WER, and
  phrase-list-building code this task copies into its own `code/` directory.

### [t0024-pareto]

* **Task ID**: `t0024_biasing_pareto_and_ft_biasing_ablation`
* **Name**: Biasing Pareto Re-Analysis + Biasing-on-Fine-Tune Ablation
* **Status**: completed (Part A only; Part B deferred — this is the task t0026 completes)
* **Relevance**: Direct dependency. Supplies the precomputed, frontier-selected biasing cell
  (`context_score=3.0, depth_scaling=0.5, alpha=1.5`) this task holds fixed, plus the reusable
  `pareto_frontier`/chart-plotting code and the exact reason (`checkpoint` + env unreachable) this
  task's Part B must not repeat.

### [t0024-archive]

* **Task ID**: `t0024_parakeet_unified_checkpoint_archive`
* **Name**: parakeet-unified-v5 checkpoint — DVC archive and model asset registration
* **Status**: completed (task.json status was a bookkeeping false negative, corrected on `main` per
  `checkpoint.md` step 2)
* **Relevance**: Direct dependency. Supplies the `parakeet-unified-v5` model asset (DVC-tracked
  `.nemo` checkpoint) that arms C and D of this task fine-tune-evaluate — the exact checkpoint whose
  absence caused `t0024` Part A/B's original blocker.

### [t0002]

* **Task ID**: `t0002_baseline_evaluation`
* **Name**: Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92
* **Status**: completed
* **Relevance**: Only prior paired-significance-testing precedent in the project
  (`compute_paired_significance`, BCa bootstrap) — confirms no McNemar precedent exists, so this
  task's paired McNemar test on per-clip brand correctness must be implemented fresh.

### [t0014]

* **Task ID**: `t0014_granite_short_clip_robustness`
* **Name**: Granite Short-Clip Robustness
* **Status**: completed
* **Relevance**: Source of a reusable grouped-bar-chart-with-error-bars pattern
  (`generate_chart_b`), directly adaptable for this task's output chart 1 (`brand_exact_rate` by arm
  x brand bucket).
