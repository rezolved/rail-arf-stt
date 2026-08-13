---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
research_stage: "code"
tasks_reviewed: 23
tasks_cited: 6
libraries_found: 0
libraries_relevant: 0
date_completed: "2026-08-13"
status: "complete"
---
## Task Objective

t0024 has two self-contained, zero-training sub-tasks. **Part A** re-analyzes the already-collected
100-cell hyperparameter sweeps from `[t0022]` (`parakeet-unified-en-0.6b`) and `[t0023]`
(`parakeet-tdt-0.6b-v3`) to compute the full `brand_exact_rate`-vs-`neutral_wer` Pareto frontier per
model (both prior tasks reported only the single max-`brand_exact_rate` cell), locate where the live
production decoding config sits relative to that frontier, and recommend production
`context_score`/`depth_scaling`/`alpha` values. Part A must not run any new inference — only read
`tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
`tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`. **Part B** applies the Part-A-selected
`malsd_batch` boosting config on top of the existing fine-tuned checkpoint from `[t0021]`
(`/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`, no training) and transcribes the
same 21-clip clean production eval set from `[t0021]`, to determine whether biasing and fine-tuning
are complementary or redundant. Expected assets: 1 `predictions` asset (21-row JSONL) and 1 `answer`
asset covering both parts. No new fine-tuning, no expansion of the 21-clip clean eval set, and no
new GPU inference for Part A are allowed per `task_description.md`'s constraints.

## Library Landscape

`uv run python -u -m arf.scripts.aggregators.aggregate_libraries --format json --detail short`
returned `"library_count": 0, "libraries": []` — **no libraries are registered in this project**
(`assets/library/` is empty project-wide). Nothing to import via the library mechanism for this
task. All reuse for t0024 must therefore be **copy into task** from prior tasks' `code/`
directories, per the cross-task reuse rule. This matches the pattern seen throughout the project:
even extensively-reused code (the GPU-PB boosting helpers duplicated verbatim across `[t0022]`,
`[t0023]`, and `[t0021]`; the `DOMAIN_VOCAB` list duplicated across `[t0017]`, `[t0021]`, `[t0022]`,
`[t0023]`) has never been promoted to a registered library — every task re-copies and locally
re-defines these helpers rather than importing them.

## Key Findings

### Dependency task status is stale metadata, not a real blocker

`aggregate_tasks --status completed` returns only 17 tasks and omits `[t0021]`, `[t0022]`, and
`[t0023]` entirely (t0021/t0022 have `task.json.status = "not_started"`; t0023 has
`status = "complete"` — singular, not the expected `"completed"` — because it predates the current
`spec_version`/`expected_assets` schema). Direct inspection confirms all three have full, committed
`results/` and `data/` outputs. This exact discrepancy is already documented and worked around in
`tasks/t0024.../logs/steps/002_check-deps/deps_report.json`: the orchestrator's own `check-deps`
step manually bypassed `verify_task_dependencies.py`'s hard gate for this reason and instructs that
other tasks' `task.json` files must never be edited to fix it. This research treats `[t0021]`,
`[t0022]`, `[t0023]` as functionally completed, consistent with that precedent.

### The sweep data schema is a flat 100-row grid per model, directly poolable for Pareto analysis

Both `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
`tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` are newline-delimited JSON, one row per
grid cell, with an **identical schema**:
`{"context_score": float, "depth_scaling": float, "alpha": float, "brand_exact_rate": float, "neutral_wer": float}`
— 100 rows each (5 `context_score` values × 4 `depth_scaling` values × 5 `alpha` values, generated
by `step_param_sweep()` in `tasks/t0022_gpu_pb_diagnostic/code/diagnostic.py` lines 403-462 and
`run_tdt_sweep()` in `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 359-415). No `error`
field is present when the sweep cell succeeded; both sweeps in this project completed cleanly
(verified: 100/100 rows have non-null `brand_exact_rate` and `neutral_wer` in both files).
`brand_exact_rate` is computed over 35 brand clips (Rezolve/brainpowa) and `neutral_wer` over a
fixed 10-clip neutral subset — both subsets of gold-92 `[t0001]`, not the full 93 clips.

### A standalone Pareto-frontier check against these two files reproduces the task's spot-check exactly

Running a minimal Pareto scan (sort by `neutral_wer` ascending, keep only cells whose
`brand_exact_rate` strictly exceeds every lower-`neutral_wer` cell already kept) over
`tdt_sweep.jsonl` gives a 5-cell frontier: `cs=2.5/ds=0.5/α=1.5` (37.1% @ 3.7%),
`cs=2.5/ds=0.5/α=2.0` (48.6% @ 5.7%), `cs=3.0/ds=0.5/α=2.0` (54.3% @ 16.7%), `cs=2.5/ds=0.5/α=2.5`
(57.1% @ 22.4%), `cs=3.0/ds=0.5/α=3.0` (60.0% @ 64.9%). The current live-prod cell
(`cs=3.0/ds=0.5/α=1.5`) evaluates to `brand_exact_rate=0.457, neutral_wer=0.057` — it is **not** on
the frontier, and is dominated by `cs=2.5/ds=0.5/α=2.0` (48.6% at the identical 5.7% neutral WER),
exactly matching the manual spot-check already recorded in `task_description.md`. The
`param_sweep.jsonl` (unified) frontier is also 5 cells: `cs=2.0/ds=0.5/α=1.5` (40.0% @ 2.7%) through
`cs=2.5/ds=0.5/α=2.5` (68.6% @ 27.9%). Both prior tasks' "headline" cells (TDT 60% @ 64.9% WER;
unified 69% @ 27.9% WER) are frontier-Pareto- optimal points but sit at the extreme high-WER end of
a 5-point frontier with three materially cheaper alternatives closer to the knee — confirming
`task_description.md`'s claim that neither prior verdict weighted the `neutral_wer` cost explicitly.
In both models' frontiers, `depth_scaling=0.5` dominates every frontier cell — no frontier point
uses `ds≥1.0` — consistent with `[t0022]`'s own Step-3 finding ("`depth_scaling=0.5` consistently
outperforms `ds≥1.0` for neutral WER").

### GPU-PB boosting-tree helper functions are copy-pasted near-identically across four tasks

`apply_beam_boosting`/`apply_malsd_boost` (malsd_batch + `beam.boosting_tree.*` OmegaConf keys),
`reset_greedy_no_boost`, and `_decode_output`/`transcribe` appear with only cosmetic renaming in
`tasks/t0022_gpu_pb_diagnostic/code/diagnostic.py`,
`tasks/t0023_tdt_vs_unified_biasing/code/run.py`, and (an older `greedy_batch`-only variant,
`apply_boosting`) in `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py`. Critically,
`[t0021]`'s `apply_boosting()` (lines 126-135) only ever configures `greedy_batch` — never
`malsd_batch` — so the fine-tuned checkpoint has never been evaluated with a boosting tree that NeMo
actually applies (`[t0022]`'s Step 2 decoding matrix shows greedy-strategy boosting is silently
ignored: configs (a) and (b) in `results_detailed.md` produce byte-identical brand-EXACT counts).
This is precisely the gap Part B closes, and the fix is mechanical: swap `[t0021]`'s
`apply_boosting()` body for `[t0023]`'s `apply_malsd_boost()` body (which sets
`cfg.strategy = "malsd_batch"` and writes to `beam.boosting_tree.*`, not `greedy.boosting_tree.*`).

### The 21-clip clean eval set and its scoring functions are self-contained and ready to reuse unmodified

`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/manifest.jsonl` (21 rows, fields
`clip_id`/`reference_text`/`audio_filename`) plus `data/clean_eval_audio.dvc`-tracked WAVs are the
exact, unmodified eval set Part B must reuse — `task_description.md` forbids extending it.
`[t0021]`'s `run_clean_eval.py` (`normalise`, `wer`, `entity_accuracy`, `domain_vocab_accuracy`,
`expand_casing_variants`, `run_eval`) is the one scoring implementation that must be matched for
apples-to-apples comparison against the two rows already in `task_description.md`'s comparison table
(biased-only WER=64.4%/EA-DV=0.0%; finetuned-only WER=55.8%/EA-DV=38.1%/latency p50=0.112s). Note
`[t0021]`'s WER uses simple word-overlap via `jiwer.wer()` on lowercased, punctuation-stripped text
— documented in `results_detailed.md` §9 as *not* matching other tasks' `jiwer` normalisation
exactly, a caveat this task's Part B output should preserve for comparability.

## Reusable Code and Assets

All items below are **copy into task** — no registered libraries exist in this project.

* **Source**: `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
  `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` **What it does**: 100-row JSONL
  grids, one row per `(context_score, depth_scaling, alpha)` cell, fields `context_score: float`,
  `depth_scaling: float`, `alpha: float`, `brand_exact_rate: float`, `neutral_wer: float`. This is
  the raw input data for Part A — read directly, no code to copy, just load with `json.loads` per
  line. **Adaptation needed**: none — read-only inputs.

* **Source**: `tasks/t0019_parakeet_biasing_improvement/code/make_charts.py` (139 lines) **What it
  does**: Matplotlib chart-generation pattern used elsewhere in the project —
  `matplotlib.use("Agg")` backend, loads JSONL results with a local `load_jsonl()` helper, saves
  PNGs to `results/images/` at `dpi=150`, uses `fig, ax = plt.subplots(...)` + `fig.tight_layout()`
  \+ `plt.close(fig)`. Directly relevant as the template for Part A's `pareto_tdt.png` /
  `pareto_unified.png` scatter-plus-frontier plots (the project has no shared plotting library).
  **Function signatures**: `load_jsonl(path: Path) -> list[dict]`;
  `plot_hyperparam_heatmap() -> None` (imshow-based grid heatmap with baseline cell highlighted via
  `plt.Rectangle`); `plot_condition_comparison() -> None` (grouped bar chart with per-bar value
  labels). **Reuse method**: copy into task — adapt `plot_hyperparam_heatmap`'s style (axis labels,
  baseline highlight box) into a new scatter+frontier plotting function; the heatmap/bar-chart code
  itself does not directly apply (Part A needs a scatter with frontier line, not a heatmap or bar
  chart). **Line count**: ~30-40 lines of the file's structure (imports, `Agg` backend, save/close
  pattern) are directly reusable; the two `plot_*` function bodies are examples, not verbatim reuse.

* **Source**: `tasks/t0023_tdt_vs_unified_biasing/code/run.py`, functions `apply_malsd_boost` (lines
  281-299), `reset_greedy_no_boost` (lines 248-256), `_decode_output`/`transcribe` (lines 158-183)
  **What it does**:
  `apply_malsd_boost(model, phrases, *, alpha, context_score, depth_scaling) -> None` sets
  `model.cfg.decoding` to `strategy="malsd_batch"`, `beam.beam_size=4`, and
  `beam.boosting_tree.{key_phrases_list,context_score,depth_scaling}` / `beam.boosting_tree_alpha`
  via `OmegaConf.update(..., force_add=True)`, then calls `model.change_decoding_strategy(cfg)`.
  This is the exact mechanism Part B needs to apply the Part-A-selected boosting config on top of
  the fine-tuned checkpoint (NeMo's `EncDecHybridRNNTCTCBPEModel`/`ASRModel` share this
  `change_decoding_ strategy` API regardless of which `.nemo` checkpoint is loaded). **Reuse
  method**: copy into task. **Adaptation needed**: none to the boosting-application logic itself;
  the `phrases` list should be built the same way as `build_phrase_list()` (lines 233-240,
  `DOMAIN_VOCAB` + brand variants, casing- expanded) for consistency with the Part A sweep that
  selected the config. **Line count**: ~50 lines total for the three functions.

* **Source**: `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` (292 lines) and
  `code/run_finetuned.py` (225 lines) **What it does**: `run_clean_eval.py` defines the exact
  scoring functions to match for Part B: `normalise(text: str) -> str` (lowercase, strip
  punctuation), `wer(ref: str, hyp: str) -> float` (via `jiwer.wer` on normalised text),
  `domain_vocab_accuracy(ref: str, hyp: str, vocab: list[str]) -> float | None` (fraction of
  in-reference domain terms also found in hypothesis — this is EA-DV),
  `_mono_path`/`transcribe(model, audio_path) -> tuple[str, float]` (stereo-to-mono handling +
  latency timing), and `run_eval(model, clips, *, label, out_path) -> dict` (the per-clip eval loop
  that writes a JSONL and returns aggregate WER/EA-DV). `run_finetuned.py` shows how to load the
  fine-tuned checkpoint: `nemo_asr.models.ASRModel.restore_from(str(checkpoint_path))`. **Reuse
  method**: copy into task. **Adaptation needed**: `run_clean_eval.py`'s `apply_boosting()` (lines
  126-135) must be **replaced** with `[t0023]`'s `apply_malsd_boost` (see above) — the existing
  function only ever sets `greedy_batch`, which `[t0022]` proved ignores the boosting tree entirely.
  Point `FINETUNED_NEMO` (from `tasks/t0021_parakeet_finetune_vs_biasing/code/paths.py` line 21,
  `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`) and `MANIFEST`/
  `CLEAN_EVAL_AUDIO_DIR` at the existing `[t0021]` `data/clean_eval*` paths — do not create new
  ones. **Line count**: ~150 combined lines directly reusable (scoring + eval-loop + checkpoint
  loading); drop the biased-model run-A logic (lines 240-251) since Part B only needs the fine-tuned
  model with boosting added.

* **Source**: `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` (`DOMAIN_VOCAB`, 31
  terms) and `code/paths.py` (`CLEAN_EVAL_DIR`, `CLEAN_EVAL_AUDIO_DIR`, `MANIFEST`,
  `FINETUNED_NEMO`) **What it does**: the Rezolve domain-vocabulary list (identical copy also lives
  in `[t0017]`, `[t0022]`, `[t0023]`) and the path constants pointing at the 21-clip clean eval set
  and checkpoint. **Reuse method**: copy into task. **Adaptation needed**: `paths.py`'s
  `TASK_DIR = Path(__file__).parents[1]` pattern must be re-pointed at `t0024`'s own directory, but
  `GOLD92_*`/`CLEAN_EVAL_*`/`FINETUNED_NEMO` should still resolve to the **t0021** task folder
  (`TASK_DIR.parent / "t0021_parakeet_finetune_vs_biasing" / "data" / ...`) since the constraint is
  to reuse that data exactly, not copy it. **Line count**: ~40 lines combined.

* **Source**:
  `tasks/t0019_parakeet_biasing_improvement/assets/answer/parakeet-unified-biasing- improvement/{short_answer.md,full_answer.md,details.json}`
  and
  `assets/predictions/parakeet-unified-biasing-best-hyperparam/{description.md,details.json, files/predictions.jsonl}`
  **What it does**: concrete templates for the `answer` (spec_version "2": `answer_id`, `question`,
  `short_title`, `short_answer_path`, `full_answer_path`, `categories`, `answer_methods`,
  `source_task_ids`, `confidence`) and `predictions` (spec_version "2": `predictions_id`, `name`,
  `dataset_ids`, `prediction_format`, `prediction_schema`, `instance_count`, `metrics_at_creation`,
  `files`) asset JSON schemas t0024's expected 1 `predictions` + 1 `answer` asset must follow.
  **Reuse method**: copy into task as a structural template (fill in t0024-specific content).
  **Adaptation needed**: full content rewrite; only the JSON key structure is reused.

## Lessons Learned

* **Greedy-strategy boosting is a silent no-op** — `[t0022]`'s decoding-matrix experiment
  (`results_detailed.md` Step 2) proved configs (a) `greedy, no boost` and (b) `greedy + GPU-PB`
  produce byte-identical brand-EXACT counts (0/35 both); only `malsd_batch` makes the boosting tree
  affect output. `[t0021]`'s `run_clean_eval.py` never made this switch, which is the entire premise
  of Part B and the reason its biased-only clip result was EA-DV=0.0%.
* **Hyperparameter sweeps near the default are a null result; far from it, they wreck WER** —
  `[t0019]`'s narrow-grid sweep found *zero* EA-DV movement across 18 near-default configs, while
  wide-grid far-from-default configs regressed WER by 20-27 absolute points. This project's own
  prior finding directly supports Part A's premise that the "headline" max-`brand_exact_rate` cells
  (`neutral_wer` 64.9%/27.9%) are far past a reasonable operating point, and that a frontier
  analysis — not a single best-cell pick — is the right lens. `[t0019]`'s `full_answer.md` is also a
  template for how this project writes up sweep-vs-null-result findings with a pre-registered
  rejection rule (WER cap), worth mirroring in t0024's answer asset.
* **Fine-tuning and biasing solve different failure classes, per `[t0021]`** — TurboBias (greedy,
  unboosted-in-practice) never recovers "Rezolve"/"brainpowa" on 21 unseen production clips
  (EA-DV=0.0%); fine-tuning recovers 38.1% but still fails on short clips and 100% of "brainpowa"
  clips specifically (`results_detailed.md` §4). Since fine-tuning was never combined with a
  correctly-applied (`malsd_batch`) boosting tree, it remains untested whether boosting closes any
  of that residual gap — this is the open question Part B answers.
* **Gold-92 is contaminated for `[t0021]`'s fine-tuned checkpoint** — all 93 gold-92 clips had
  speed- perturbed versions in the finetune training data, so `[t0021]`'s gold-92 EA-DV (93.18%) is
  inflated by ~55pp versus the clean 21-clip EA-DV (38.1%). Part B must use the 21-clip clean set
  exclusively (as `task_description.md` already mandates) — gold-92 would silently overstate any
  biasing gain on the fine-tuned model.
* **A pure post-decode string-replacement channel already exists and dramatically outperforms both
  boosting and fine-tuning alone** — `[t0019]`'s `stt_replacements` finding (EA-DV 34.8%→95.7%) is
  out of scope for t0024 (which is specifically a biasing-vs-fine-tuning question) but is directly
  relevant context for the answer asset's production recommendation: even if Part B shows biasing +
  fine-tuning are complementary, `[t0019]`'s post-hoc replacement pass remains the higher-EA-DV,
  lower -effort production option and should be mentioned as the load-bearing comparison point.

## Recommendations for This Task

1. **Part A**: implement the Pareto scan as a pure-Python script reading the two existing JSONL
   files — no NeMo/GPU dependency, no new task-specific helper needed beyond a ~15-line frontier
   function (sort by `neutral_wer`, keep strictly-improving `brand_exact_rate`). The verified
   frontier above (5 cells per model) can be used directly to sanity-check the implementation's
   output. Copy the Matplotlib `Agg`-backend + `results/images/` save pattern from `[t0019]`'s
   `make_charts.py` for `pareto_tdt.png`/`pareto_unified.png`; build a scatter of all 100 cells with
   the frontier cells connected/highlighted and the current-prod cell (`cs=3.0/ds=0.5/α=1.5` for
   TDT) marked distinctly.
2. **Part B**: copy `[t0021]`'s `run_clean_eval.py` and `constants.py`/`paths.py` into t0024's
   `code/`, replace the `apply_boosting()` body with `[t0023]`'s `apply_malsd_boost()` (malsd_batch
   \+ `beam.boosting_tree.*`), parameterize `context_score`/`depth_scaling`/`alpha` from Part A's
   answer for the unified model (do not hardcode `[t0022]`'s single "headline" cell — the frontier
   point Part A recommends may differ), and run only the fine-tuned-plus-boosting condition (the
   biased- only and finetuned-only rows are already given in `task_description.md`'s comparison
   table, copied from `[t0021]`, and must not be re-run per the task's
   no-new-inference-on-gold-92-adjacent-data spirit — though Part B explicitly is the one new
   inference run allowed).
3. **Do not invest in further GPU-PB hyperparameter search beyond selecting a frontier point** —
   both `[t0019]` (null result near default) and this task's own frontier computation (only 5-10% of
   the 100-cell grid is ever Pareto-optimal) confirm the grid is already exhaustively characterized;
   Part A is an analysis task over existing data, not a new search.
4. Both eval subsets are small (35/10 brand/neutral clips for Part A's underlying sweeps; 21 clips
   for Part B) — carry forward `[t0021]`'s explicit "directional, not definitive" framing in the
   answer asset rather than presenting point estimates as statistically conclusive, consistent with
   `task_description.md`'s own Limitations section.
5. Use `[t0019]`'s and `[t0017]`'s `assets/answer/` and `assets/predictions/` JSON structures as the
   literal template for t0024's expected 1 `predictions` + 1 `answer` asset — no new schema design
   needed.

## Task Index

### [t0001]

* **Task ID**: `t0001_stt_benchmark`
* **Name**: STT Benchmark — Gold-92 Dataset Ingestion
* **Status**: completed
* **Relevance**: Source of the gold-92 dataset (`ground_truth.jsonl`, `audio/`) underlying the 35
  brand + 10 neutral clip subsets used by both `[t0022]`'s and `[t0023]`'s sweeps that Part A
  re-analyzes.

### [t0017]

* **Task ID**: `t0017_parakeet_biasing_buffer_replacement`
* **Name**: Parakeet unified vs TDT — biased accuracy, latency, fine buffer sweep
* **Status**: completed
* **Relevance**: Source of `DOMAIN_VOCAB` (`code/constants.py`) reused verbatim by `[t0021]`,
  `[t0022]`, and `[t0023]`; established the `alpha=1.0/context_score=1.0/depth_scaling=2.0` baseline
  boosting config that `[t0021]`'s biased-only run and `[t0022]`/`[t0023]`'s baseline cells build
  on.

### [t0019]

* **Task ID**: `t0019_parakeet_biasing_improvement`
* **Name**: Parakeet-unified biasing improvement
* **Status**: not_started (stale metadata; results/assets present — see Key Findings)
* **Relevance**: Prior null-result hyperparameter sweep (supports Part A's premise that the grid is
  already well-characterized) and template for this project's `answer`/`predictions` asset schemas
  and Matplotlib chart-generation pattern (`code/make_charts.py`).

### [t0021]

* **Task ID**: `t0021_parakeet_finetune_vs_biasing`
* **Name**: Parakeet fine-tune vs biasing — parakeet-unified on gold-92
* **Status**: not_started (stale metadata; results/data present — see Key Findings)
* **Relevance**: Direct task.json dependency. Source of the fine-tuned checkpoint, the 21-clip clean
  eval set, and the scoring/eval-loop code (`run_clean_eval.py`, `run_finetuned.py`) Part B must
  reuse and extend with correctly-applied `malsd_batch` boosting.

### [t0022]

* **Task ID**: `t0022_gpu_pb_diagnostic`
* **Name**: GPU-PB biasing diagnostic — parakeet-unified brand recognition failure
* **Status**: not_started (stale metadata; results present — see Key Findings)
* **Relevance**: Direct task.json dependency. Source of `param_sweep.jsonl` (the unified-model 100-
  cell grid Part A re-analyzes) and the `apply_beam_boosting`/decoding-strategy helper functions.

### [t0023]

* **Task ID**: `t0023_tdt_vs_unified_biasing`
* **Name**: TDT vs Unified — GPU-PB Biasing Comparison
* **Status**: complete (legacy schema; treated as completed — see Key Findings)
* **Relevance**: Direct task.json dependency. Source of `tdt_sweep.jsonl` (the TDT-model 100-cell
  grid Part A re-analyzes) and `apply_malsd_boost`, the exact function Part B needs to correctly
  apply boosting on top of `[t0021]`'s fine-tuned checkpoint.
