---
spec_version: "2"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
date_completed: "2026-08-13"
status: "complete"
---
# Plan: Biasing Pareto Re-Analysis + Biasing-on-Fine-Tune Ablation

## Objective

This task has two independent, self-contained sub-tasks. Both deliberately avoid the two most
expensive levers available to this STT project: training a new model and collecting new held-out
audio.

**Part A (zero compute, local data analysis only).** Re-analyze the two 100-cell hyperparameter
sweeps already collected by prior tasks — `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl`
(model `parakeet-unified-en-0.6b`) and `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`
(model `parakeet-tdt-0.6b-v3`) — to compute the full Pareto frontier over (`brand_exact_rate`
maximized, `neutral_wer` minimized), not just the single max-`brand_exact_rate` cell each prior task
headlined. Locate where the current live-production TDT decoding config
(`context_score=3.0, depth_scaling=0.5, alpha=1.5`) sits relative to that frontier, and issue a
concrete, numerically-justified production-decoding recommendation.

**Part B (one short GPU inference run, no training).** Apply the tuned `malsd_batch` boosting
mechanism (the mechanism from t0023, not the broken `greedy_batch` mechanism from t0021) on top of
the existing fine-tuned checkpoint from t0021
(`/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`), using the boosting config Part A
selects from its own unified-model frontier (not the old t0022 headline cell). Evaluate on the
existing, unmodified 21-clip clean production eval set
(`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/`) and determine whether biasing and
fine-tuning are complementary or redundant.

**Success criteria (done when):**

* Two Pareto-frontier scatter+frontier charts exist (`results/images/pareto_tdt.png`,
  `results/images/pareto_unified.png`), each showing all 100 grid cells, the frontier highlighted,
  and (for TDT) the live-prod point marked.
* A frontier table per model exists, sorted by `neutral_wer` ascending, each row showing
  `brand_exact_rate`, `neutral_wer`, and delta vs. the current live-prod point (TDT only).
* A single, explicit, numerically-stated stance on acceptable `neutral_wer` regression per
  `brand_exact_rate` point gained is used to pick one recommended cell per model, and that stance is
  applied — not asserted — by code, reproducibly.
* The fine-tuned checkpoint has been evaluated with a **working** `malsd_batch` boosting tree (never
  done before this task) on the unmodified 21-clip clean eval set, producing a 21-row predictions
  file with `wer`, `ea_dv`, and per-clip latency.
* A 3-row comparison table (biased-only, fine-tuned-only, fine-tuned+malsd-biased) exists with a
  verdict: complementary or redundant.
* One `predictions` asset and one `answer` asset exist under
  `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/assets/`, matching `task.json`
  `expected_assets` (`predictions: 1`, `answer: 1`).
* `uv run python -u -m arf.scripts.verificators.verify_plan t0024_biasing_pareto_and_ft_biasing_ablation`
  passes with zero errors.

## Task Requirement Checklist

Quoting the operative task text from `task.json` and
`tasks/t0024_biasing_pareto_and_ft_biasing_ablation/task_description.md`:

> **Part A (zero compute):** re-analyze the param sweeps already collected in t0022 and t0023 to
> surface the full `brand_exact_rate` vs `neutral_wer` tradeoff across the grid, not just the single
> max-`brand_exact_rate` cell each prior task headlined. Locate the true Pareto frontier for both
> `parakeet-tdt-0.6b-v3` and `parakeet-unified-en-0.6b`, and check where the current live production
> decoding config actually sits relative to it.
>
> **Part B (one inference run, no training):** apply the existing tuned `malsd_batch` boosting
> config on top of the existing fine-tuned checkpoint from t0021 and evaluate on the existing
> 21-clip clean production eval set — answering whether biasing and fine-tuning are complementary or
> redundant.

Every concrete requirement below is assigned a stable `REQ-*` ID, referenced later in
`## Step by Step`.

**Part A — core deliverables**

* `REQ-1`: Compute the full Pareto frontier (`brand_exact_rate` maximized, `neutral_wer` minimized)
  for `parakeet-tdt-0.6b-v3` over all 100 rows of
  `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`. — Step 2.
* `REQ-2`: Compute the same frontier for `parakeet-unified-en-0.6b` over all 100 rows of
  `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl`. — Step 2.
* `REQ-3`: Plot `neutral_wer` (x) vs `brand_exact_rate` (y) as a scatter of all 100 cells per model,
  frontier highlighted, current live-prod TDT point (`cs=3.0/ds=0.5/α=1.5`) marked explicitly. —
  Step 3.
* `REQ-4`: Locate the live-prod point relative to the TDT frontier: on it, or dominated by which
  cell(s) (equal-or-better on both axes). — Step 2, Step 4.
* `REQ-5`: Write a production recommendation — exact `(context_score, depth_scaling, alpha)` cell —
  with an explicit, stated, numeric stance on how much `neutral_wer` regression is acceptable per
  `brand_exact_rate` point gained. — Step 2, Step 4, Step 14.
* `REQ-6`: Answer: what is the full Pareto frontier for TDT and for unified? — Step 2, Step 4.
* `REQ-7`: Answer: is the current live-prod config on the frontier; if not, which frontier cell(s)
  strictly dominate it? — Step 2, Step 4.
* `REQ-8`: Answer: how much `neutral_wer` does each prior task's "headline" recommendation (TDT
  `cs=3.0/ds=0.5/α=3.0`, unified `cs=2.5/ds=0.5/α=2.5`) actually cost, laid next to the frontier? —
  Step 4.
* `REQ-9`: Answer: does the frontier shape differ qualitatively between the two models (does unified
  reach higher `brand_exact_rate` before `neutral_wer` collapses, or earlier)? — Step 4.
* `REQ-10`: Produce `results/images/pareto_tdt.png` and `results/images/pareto_unified.png`. — Step
  3\.
* `REQ-11`: Produce a frontier table per model, sorted by `neutral_wer` ascending, with
  `brand_exact_rate` and the delta vs. the current live-prod point. — Step 4.

**Part B — core deliverables**

* `REQ-12`: Load the fine-tuned checkpoint
  `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` (from t0021, confirmed present
  via `tasks/t0021_parakeet_finetune_vs_biasing/code/paths.py`). — Step 9, Step 10.
* `REQ-13`: Apply `change_decoding_strategy` with `malsd_batch` and the boosting config
  (`context_score`, `depth_scaling`, `alpha`) that Part A selected from the **unified**-model
  frontier — never default to t0022's old headline cell (`cs=2.5/ds=0.5/α=2.5`) without first
  checking Part A's own frontier answer. — Step 7, Step 9.
* `REQ-14`: Copy/adapt t0023's `apply_malsd_boost()`
  (`tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines ~281-299 — sets `strategy="malsd_batch"`,
  writes `beam.boosting_tree.*` and `beam.boosting_tree_alpha`). Do **not** reuse t0021's
  `apply_boosting()` in `run_clean_eval.py` as written — it only ever sets
  `strategy="greedy_batch"`, which NeMo silently ignores for the boosting tree (proven in t0022's
  decoding matrix: `greedy_batch` + boosting-tree config is byte-identical to no-boost). — Step 7.
* `REQ-15`: Transcribe the same 21 clips as
  `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/manifest.jsonl`. — Step 9, Step 10.
* `REQ-16`: Compute `wer`, `ea_dv`, and per-clip latency using the same scoring approach as
  `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` (`normalise`, `wer`,
  `domain_vocab_accuracy` — copied in, not imported cross-task). — Step 6, Step 9.
* `REQ-17`: Produce a 3-row comparison table: Biased-only (t0021, copied, WER 64.4% / EA-DV 0.0%),
  Fine-tuned-only (t0021, copied, WER 55.8% / EA-DV 38.1%, latency p50 — see `REQ-25` for a
  provenance correction to the quoted 0.112s figure), and Fine-tuned+`malsd_batch`-biasing (new,
  this task). — Step 11.
* `REQ-18`: Answer: does biasing on top of the fine-tuned checkpoint improve EA-DV beyond 38.1%,
  particularly on short clips and "brainpowa" clips (t0021 §4 failure modes)? — Step 11, Step 14.
* `REQ-19`: Answer: does adding the boosting tree regress WER or latency relative to
  fine-tuned-only? — Step 11, Step 14.
* `REQ-20`: Answer: is the combination complementary (better than either alone) or redundant (no
  improvement over fine-tuning alone)? — Step 11, Step 14.
* `REQ-21`: Produce a `predictions` asset: 21-row JSONL of fine-tuned + biased transcripts. — Step
  13\.
* `REQ-22`: Produce an `answer` asset covering both parts' recommendation/verdict (task.json
  `expected_assets.answer = 1`, so this plan uses **one shared** answer asset — task_description.md
  explicitly permits "one shared answer asset or two"; one is chosen to match `expected_assets`
  exactly). — Step 14.

**Constraints (both parts, non-negotiable)**

* `REQ-23`: No new model fine-tuning of any kind anywhere in this task (TDT fine-tuning is tracked
  separately). — Enforced throughout; no step trains anything.
* `REQ-24`: No expansion or modification of the 21-clip clean eval set — reuse
  `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/` exactly as-is, no additional
  production clips. — Step 9, Step 10 read this directory read-only.
* `REQ-25`: Part A must not run any new inference. If a question cannot be answered from the two
  existing sweep JSONLs, document it as a limitation instead of launching a new sweep. — Step 2,
  Step 4 (also surfaces the separate, unprompted finding that the task-text-quoted "0.112s" latency
  figure for fine-tuned-only is actually t0021's gold-92 latency, not clean-21 latency — corrected
  in Step 11 by recomputing directly from t0021's existing raw per-clip data, still zero new
  inference).
* `REQ-26`: All reused code is copied into
  `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/`, never imported from another task's
  `code/` directory (no registered libraries exist in `assets/library/` to import from either). —
  Steps 1, 5, 6, 7.
* `REQ-27`: Quality-first priority — latency is recorded as a side metric on every relevant run
  (Part B p50 latency; Part A notes WER/`neutral_wer`) but never gates which frontier cell or config
  is recommended. — Step 2 (frontier selection algorithm only ever compares `neutral_wer` vs.
  `brand_exact_rate`), Step 11, Step 14.

## Approach

**Part A — pure-Python Pareto scan + Matplotlib scatter.** No GPU, no NeMo dependency. Both sweep
files (`tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` and
`tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl`) are confirmed (verified directly
against the files during planning) to be 100-row JSONL with an identical flat schema —
`{context_score, depth_scaling, alpha, brand_exact_rate, neutral_wer}` — no `error` fields, all
100/100 rows valid in both files, directly poolable with no cleaning. `code/pareto.py` computes the
**true** Pareto frontier as the set of non-dominated points: a row is on the frontier iff no other
row has both `neutral_wer` ≤ its `neutral_wer` and `brand_exact_rate` ≥ its `brand_exact_rate`, with
at least one strict inequality. This is a real O(n²) pairwise non-domination check over 100 rows
(100² = 10,000 comparisons, trivial cost) — **not** a "sort by `neutral_wer`, keep points where
`brand_exact_rate` strictly increases" single-pass scan. That naive scan was tried by hand during
planning and, because both sweeps contain multiple rows sharing the same `neutral_wer` value, it can
retain a **dominated** point ahead of a same-`neutral_wer`, higher-`brand_exact_rate` row that
appears later in the file's original (non-frontier-relevant) ordering. Re-deriving with the correct
non-domination check during planning gives a clean 5-cell frontier for both models, matching the
independent counts already recorded in `research/research_summary.md`:

* **TDT frontier (5 cells, ascending `neutral_wer`)**: `cs=2.5/ds=0.5/α=1.5` (37.1% @ 3.7%),
  `cs=2.5/ds=0.5/α=2.0` (48.6% @ 5.7%), `cs=3.0/ds=0.5/α=2.0` (54.3% @ 16.7%), `cs=2.5/ds=0.5/α=2.5`
  (57.1% @ 22.4%), `cs=3.0/ds=0.5/α=3.0` (60.0% @ 64.9%).
* **Unified frontier (5 cells, ascending `neutral_wer`)**: `cs=2.0/ds=0.5/α=1.5` (40.0% @ 2.7%),
  `cs=2.5/ds=0.5/α=1.5` (48.6% @ 4.4%), `cs=1.5/ds=0.5/α=2.5` (51.4% @ 7.7%), `cs=3.0/ds=0.5/α=1.5`
  (60.0% @ 8.7%), `cs=2.5/ds=0.5/α=2.5` (68.6% @ 27.9%).
* Both prior tasks' "headline" cells (TDT `cs=3.0/ds=0.5/α=3.0`, unified `cs=2.5/ds=0.5/α=2.5`) are
  technically Pareto-optimal (they are the last/highest-`neutral_wer` frontier cell in each list
  above) but sit at the extreme, expensive tail — this directly answers `REQ-8`.
* The current live-prod TDT point (`cs=3.0/ds=0.5/α=1.5` → `brand_exact_rate=45.7%`,
  `neutral_wer=5.7%`, read directly from `tdt_sweep.jsonl` and confirmed identical to
  `task_description.md`'s cited value) is **not** on the frontier: `cs=2.5/ds=0.5/α=2.0` gives
  `brand_exact_rate=48.6%` at the identical `neutral_wer=5.7%` — a strict, zero-extra-cost
  improvement. This directly answers `REQ-4`/`REQ-7`.

**Explicit acceptable-regression stance (`REQ-5`, `REQ-27`).** The stance is: *starting from a
baseline point, walk the frontier in ascending `neutral_wer` order and accept a candidate frontier
cell only if the marginal ratio `Δneutral_wer / Δbrand_exact_rate`, measured against the
**last-accepted** point (not necessarily the immediately-preceding frontier row), is ≤ 1.0 — i.e.,
never pay more than 1 percentage point of extra `neutral_wer` for less than 1 percentage point of
`brand_exact_rate` gain.* A threshold of exactly 1.0 is used because it is a symmetric, unweighted
trade (neither metric is treated as intrinsically more important, both being 0-100% quantities),
consistent with `REQ-27`'s "quality first, no metric gates the other with an arbitrary weighting"
framing, and — verified by hand during planning on both sweeps' actual numbers — this threshold
falls in a clean gap between accepted and rejected candidates rather than landing arbitrarily
mid-continuum, so it is not reverse-engineered to hit a preferred answer:

* **TDT**, baseline = current live-prod point (`45.7%@5.7%`, since this is literally the config
  being reconsidered): `cs=2.5/ds=0.5/α=2.0` is accepted at ratio `0/2.9 = 0.0` (zero extra
  `neutral_wer`, strict `brand_exact_rate` gain). The next candidate, `cs=3.0/ds=0.5/α=2.0`, has
  ratio `(16.7-5.7)/(54.3-48.6) ≈ 1.93` against the newly-accepted baseline — rejected. All further
  candidates have ratio > 1.93 against that baseline and are also rejected. **Recommended TDT
  production cell: `context_score=2.5, depth_scaling=0.5, alpha=2.0`**
  (`brand_exact_rate=48.6%, neutral_wer=5.7%`).
* **Unified**, baseline = the lowest-`neutral_wer` frontier cell (there is no "current prod" anchor
  for unified — it is not deployed): `cs=2.5/ds=0.5/α=1.5` accepted at ratio
  `(4.4-2.7)/(48.6-40.0) ≈ 0.198`. `cs=1.5/ds=0.5/α=2.5` is rejected at ratio
  `(7.7-4.4)/(51.4-48.6) ≈ 1.18` against that baseline. `cs=3.0/ds=0.5/α=1.5` is then evaluated
  **against the same last-accepted baseline** (`48.6%@4.4%`, skipping the rejected candidate) at
  ratio `(8.7-4.4)/(60.0-48.6) ≈ 0.377` — accepted. `cs=2.5/ds=0.5/α=2.5` is rejected at ratio
  `(27.9-8.7)/(68.6-60.0) ≈ 2.23` against the new baseline. **Recommended unified cell:
  `context_score=3.0, depth_scaling=0.5, alpha=1.5`** (`brand_exact_rate=60.0%, neutral_wer=8.7%`,
  on the pre-fine-tune biasing-only sweep). This is the exact cell Part B uses for its boosting
  config (`REQ-13`) — it is numerically coincidental that these parameter values match the current
  TDT live-prod config's numbers; they are a different model's frontier selection and this plan
  calls that coincidence out explicitly so it is not mistaken for a bug.

`code/pareto.py` must implement this algorithm and reproduce these numbers from the raw JSONL files,
not hardcode them — the numbers above are the expected output, used as a correctness check in
`## Verification Criteria`, not a substitute for running the code.

**Part B — copy t0021's eval harness, swap the boosting function.** Copy `run_clean_eval.py`'s
scoring functions (`normalise`, `wer`, `domain_vocab_accuracy` at lines 55-84) and model/transcribe
helpers (`_ensure_transcribe_cfg`, `_mono_path`, `transcribe` at lines 92-123) verbatim into this
task's `code/`. Point path constants at t0021's existing data in place — do **not** copy the WAV
files or manifest (`REQ-24`); read them from
`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval/` directly. Replace t0021's
`apply_boosting()` (which only ever sets `strategy="greedy_batch"`) with t0023's
`apply_malsd_boost()` body (`strategy="malsd_batch"`, `beam.beam_size=4`, `beam.boosting_tree.*`,
`beam.boosting_tree_alpha`) — this is the exact, mechanical fix identified during research: the
fine-tuned checkpoint has never actually been evaluated with a working boosting tree because
`greedy_batch` + boosting-tree config is proven byte-identical to no-boost in t0022's decoding
matrix (0/35 brand-exact both ways).

**Alternatives considered:**

* *Re-run a new, finer-grained sweep instead of re-analyzing the existing 100-cell grids.* Rejected
  — explicitly forbidden by `REQ-25` (Part A must not run new inference), and wasteful: two full
  100-cell grids already exist and are large enough to derive a clean 5-cell frontier per model.
* *Evaluate the fine-tuned+biased combination on gold-92 instead of the 21-clip clean set, to get a
  larger n.* Rejected — gold-92 is contaminated for this specific fine-tuned checkpoint (all 93
  clips had speed-perturbed versions in the finetune training data; research found gold-92 EA-DV for
  the fine-tuned model is inflated ~55pp vs. the clean-21 EA-DV, 93.18% vs. 38.1%). Using gold-92
  here would produce an invalid complementary-vs-redundant verdict. `REQ-24` forbids it explicitly
  anyway.
* *Default Part B's boosting config to t0022's old headline cell (`cs=2.5/ds=0.5/α=2.5`, 68.6%@27.9%
  WER).* Rejected — explicitly forbidden by `REQ-13`; that cell is the extreme, high-`neutral_wer`
  tail of the unified frontier, not what Part A's own stance selects (`cs=3.0/ds=0.5/α=1.5`,
  60.0%@8.7%).

**Task types.** `task.json`'s `task_types` field is empty. This plan recommends four types (the
orchestrator or a human should update `task.json` accordingly, per `plan_specification.md`):
`comparative-analysis` (Part A frontier comparison across configs; Part B's 3-row FT/biasing
comparison — both compared strictly under identical evaluation data per the type's "fair comparison"
guideline), `data-analysis` (Part A's methodology: chart generation to `results/images/`, structured
intermediate JSON, per-subset breakdowns), `experiment-run` (Part B's GPU inference run, predictions
asset, validation gate before full scale), and `answer-question` (both parts culminate in one shared
answer asset with a direct, evidence-cited recommendation). The `comparative-analysis` guideline to
"generate a bar chart comparing the primary metric" and "produce Pareto frontier charts for
multi-dimensional trade-offs" directly shapes Steps 2-3. The `experiment-run` guideline's mandatory
validation gate ("baseline, `--limit`, failure condition, individual-output inspection") directly
shapes Step 12. The `answer-question` guideline's "state the exact evidence sources, no hedging in
the short answer" shapes Step 14.

## Cost Estimation

* **Part A: $0.** Pure local Python (`json`, `matplotlib`) on two already-on-disk JSONL files. No
  API calls, no remote compute. `project/budget.json` lists `azure_ml` as the only paid service this
  task touches, and Part A does not use it.
* **Part B: one short GPU run on the shared Azure ML H100 pool** (`project/azure_vm.json`,
  NC80-class, 2×H100, `$13.96/hr` per VM). Estimated wall-clock: checkpoint load (~2-5 min) +
  `dvc pull` of `clean_eval_audio` if not already cached (~1-2 min, small — 21 short WAV clips) +
  5-clip validation run (~1 min) + 21-clip full run (~2-3 min, batch-of-1 inference, clips are a few
  seconds each) + environment/SSH setup overhead (~10-15 min). Total padded estimate: **1.5 hours**
  wall-clock ⇒ **≈$21**, rounded up to a **$30 cap** for this task to leave margin for retries after
  a validation-gate failure. `project/budget.json`'s `per_task_default_limit` is `$100`; $30 is well
  under it (≈30%).
* **Total task cost estimate: ≈$21-30**, all in Part B GPU time. No LLM/API costs anywhere in this
  task (no `anthropic_api`/`openai_api` usage — this is pure ASR inference and local analysis).

## Step by Step

### Milestone 1 — Part A: Pareto Frontier Computation and Charts (local, no GPU) [CRITICAL]

1. **Create `code/paths.py`.** Define path constants: `REPO_ROOT` (four parents up from this file),
   `TASK_DIR`, `RESULTS_DIR = TASK_DIR / "results"`, `IMAGES_DIR = RESULTS_DIR / "images"`, and
   read-only references into the dependency tasks —
   `T0022_SWEEP = REPO_ROOT / "tasks" / "t0022_gpu_pb_diagnostic" / "results" / "param_sweep.jsonl"`,
   `T0023_SWEEP = REPO_ROOT / "tasks" / "t0023_tdt_vs_unified_biasing" / "results" / "tdt_sweep.jsonl"`,
   `T0021_MANIFEST = REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval" / "manifest.jsonl"`,
   `T0021_AUDIO_DIR = REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval_audio"`,
   `T0021_FINETUNED_NEMO = Path("/mnt/finetune-checkpoints/parakeet-unified- finetuned-best.nemo")`
   (matches `tasks/t0021_parakeet_finetune_vs_biasing/code/paths.py` `FINETUNED_NEMO`),
   `T0021_CLEAN_BIASED = REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval_biased.jsonl"`,
   `T0021_CLEAN_FINETUNED = REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval_finetuned.jsonl"`.
   No data files are copied — every dependency path is read in place, satisfying `REQ-26`. Expected
   output: module imports cleanly with
   `python -c "from tasks.t0024_biasing_pareto_and_ft_biasing_ablation.code import paths"`.
   Satisfies `REQ-26` (path centralization prerequisite for later steps).

2. **Create `code/pareto.py`.** Implement:
   * `load_sweep(path: Path) -> list[dict]` — read JSONL line by line with `json.loads`.
   * `pareto_frontier(rows: list[dict]) -> list[dict]` — the true non-dominated-point filter
     described in `## Approach`: for each row, it is on the frontier iff no other row has
     `neutral_wer <= row.neutral_wer` and `brand_exact_rate >= row.brand_exact_rate` with at least
     one strict inequality. Return the frontier sorted by `neutral_wer` ascending. **Do not**
     implement this as a single-pass "sort then keep monotonically increasing `brand_exact_rate`"
     scan — as documented in `## Approach`, that construction can retain dominated points when two
     rows share the same `neutral_wer` value, which both sweeps do.
   * `select_frontier_cell(frontier: list[dict], baseline: dict, *, ratio_threshold: float = 1.0) -> dict`
     — implements the stance from `## Approach`: starting from `baseline`, scan the frontier
     ascending by `neutral_wer`; for each candidate compute
     `ratio = (candidate.neutral_wer - accepted.neutral_wer) / (candidate.brand_exact_rate - accepted.brand_exact_rate)`
     against the current accepted point (initially `baseline`); if `ratio <= ratio_threshold`,
     accept the candidate as the new baseline; continue through the whole frontier list regardless
     of a rejection (do not stop scanning at the first rejected candidate). Return the final
     accepted point.
   * `main()` — loads both sweeps via `paths.T0022_SWEEP`/`paths.T0023_SWEEP`, asserts
     `len(rows) == 100` for each (hard-stop with a clear error if not — `REQ-25`'s "must not run new
     inference" implies these files are the sole source of truth and must not have silently changed
     shape), computes each frontier, locates the live-prod TDT point in `tdt_sweep.jsonl`
     (`context_score==3.0, depth_scaling==0.5, alpha==1.5`), determines whether it is in the TDT
     frontier list and which frontier cell(s) dominate it if not (cell(s) with
     `neutral_wer <= live_prod.neutral_wer and brand_exact_rate >= live_prod.brand_exact_rate`), and
     computes `select_frontier_cell` for both models (TDT baseline = the live-prod point itself;
     unified baseline = `unified_frontier[0]`, the lowest-`neutral_wer` frontier cell, since unified
     has no deployed "current prod" reference).
   * Write `results/pareto_tdt.json`:
     `{"model": "parakeet-tdt-0.6b-v3", "source_file": "tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl", "n_rows": 100, "frontier": [...5 cells, ascending neutral_wer...], "live_prod_point": {"context_score": 3.0, "depth_scaling": 0.5, "alpha": 1.5, "brand_exact_rate": 0.457, "neutral_wer": 0.057}, "live_prod_on_frontier": false, "live_prod_dominated_by": [...frontier cell(s)...], "selected_cell": {...}, "selection_stance": "marginal delta_neutral_wer / delta_brand_exact_rate <= 1.0 against the last-accepted point, scanning the frontier ascending by neutral_wer, TDT baseline = current live-prod point"}`.
   * Write `results/pareto_unified.json` with the same shape but no `live_prod_*` keys (unified is
     not deployed) and `"selection_stance"` noting the baseline is the lowest-`neutral_wer` frontier
     cell. Run:
     `uv run python -m arf.scripts.utils.run_with_logs --task-id t0024_biasing_pareto_and_ft_biasing_ablation -- uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/pareto.py`.
     **Expected output** (derived by hand from the raw files during planning — use as a correctness
     check, not a hardcoded substitute): TDT frontier has exactly 5 cells; unified frontier has
     exactly 5 cells; TDT `live_prod_on_frontier` is `false`, dominated by `cs=2.5/ds=0.5/α=2.0`;
     TDT `selected_cell` is `cs=2.5/ds=0.5/α=2.0` (`brand_exact_rate=0.486, neutral_wer=0.057`);
     unified `selected_cell` is `cs=3.0/ds=0.5/α=1.5` (`brand_exact_rate=0.600, neutral_wer=0.087`).
     If the freshly computed output differs from these numbers, trust the code's fresh computation
     over this plan's numbers only after first checking `pareto_frontier`'s comparison directions
     and `select_frontier_cell`'s ratio-against-last-accepted logic for a sign/off-by-one bug (see
     `## Risks & Fallbacks`, Risk 4) — the input files are static and were independently read during
     planning, so a real, correctly implemented run should reproduce these exact numbers. Satisfies
     `REQ-1`, `REQ-2`, `REQ-4`, `REQ-5`, `REQ-6`, `REQ-7`, `REQ-25`.

3. **Create `code/make_charts.py`.** Copy the structural pattern from
   `tasks/t0019_parakeet_biasing_improvement/code/make_charts.py`: `matplotlib.use("Agg")` before
   importing `pyplot`, save figures to `IMAGES_DIR` at `dpi=150`. Read `results/pareto_tdt.json` and
   `results/pareto_unified.json` (written by Step 2). For each model, produce one PNG:
   * Scatter all rows from the source sweep JSONL (re-read via `paths.T0022_SWEEP`/
     `paths.T0023_SWEEP`) as small gray/muted points, x-axis = `neutral_wer` (as a percentage,
     0-100), y-axis = `brand_exact_rate` (as a percentage, 0-100).
   * Overlay the frontier cells connected by a line, in a distinct color (e.g., a saturated accent
     color), with markers.
   * For TDT only, mark the live-prod point with a distinct marker shape/color and a text label
     (e.g., `"live prod"`).
   * Title: `"Parakeet TDT 0.6B v3 — brand_exact_rate vs neutral_wer (t0023 sweep)"` /
     `"Parakeet Unified EN 0.6B — brand_exact_rate vs neutral_wer (t0022 sweep)"`. Axis labels:
     `"neutral_wer (%)"`, `"brand_exact_rate (%)"`. Legend distinguishing "all cells", "frontier",
     and (TDT only) "live prod".
   * Save to `results/images/pareto_tdt.png` and `results/images/pareto_unified.png`. Run:
     `uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py`.
     Expected output: both PNG files exist and are non-trivial in size (each > 10 KB — a
     blank/failed plot is typically under a few KB). Satisfies `REQ-3`, `REQ-10`.

4. **Write `results/frontier_tables.md`.** A raw, intermediate markdown artifact — not the
   orchestrator-managed detailed-results writeup produced by a later `results` step — containing:
   * Two tables (one per model), each row = one frontier cell from `results/pareto_tdt.json` /
     `results/pareto_unified.json`, columns: `context_score`, `depth_scaling`, `alpha`,
     `brand_exact_rate`, `neutral_wer`, and (TDT only) `Δneutral_wer vs live-prod`,
     `Δbrand_exact_rate vs live-prod`. Sorted ascending `neutral_wer`. This directly satisfies
     `REQ-11`.
   * A short "headline cell cost" paragraph answering `REQ-8`: state that both prior tasks' headline
     cells are technically Pareto-optimal (they are literally the last row in each frontier table
     above) but sit at `64.9%` (TDT) and `27.9%` (unified) `neutral_wer` — 11x and 3x higher
     `neutral_wer` respectively than each model's selected cell from Step 2 — with the cheaper
     frontier alternatives closer to the "knee" delivering most of the `brand_exact_rate` gain at a
     fraction of the `neutral_wer` cost.
   * A short "frontier shape comparison" paragraph answering `REQ-9`: compare where each frontier's
     `neutral_wer` "knee" sits (from the `select_frontier_cell` output in Step 2's JSON files) —
     state explicitly whether unified reaches its selected `brand_exact_rate` (60.0%) at a lower
     `neutral_wer` (8.7%) than TDT needs to reach a comparable `brand_exact_rate` gain, or the
     opposite, based on the actual computed numbers (do not guess — read the two JSON files'
     `selected_cell` and full `frontier` lists produced by Step 2).
   * A short "limitations" paragraph stating `REQ-25`'s scope limit explicitly: this frontier is
     only as good as the 35-brand-clip / 10-neutral-clip subset of gold-92 that t0022/t0023 swept
     over — it is not a re-derivation on a larger sample, and no new inference was run to check this
     Pareto analysis against a different subset. Satisfies `REQ-6`, `REQ-8`, `REQ-9`, `REQ-11`.

**Milestone 1 checkpoint**: `results/pareto_tdt.json`, `results/pareto_unified.json`,
`results/images/pareto_tdt.png`, `results/images/pareto_unified.png`, and
`results/frontier_tables.md` all exist and are internally consistent (chart frontier points match
the JSON `frontier` lists). Part A is fully verifiable without any GPU access at this point.

### Milestone 2 — Part B: Fine-Tuned + `malsd_batch`-Biased Inference on Clean-21 [CRITICAL]

5. **Create `code/constants.py`.** Copy `DOMAIN_VOCAB` (the 31-term Rezolve domain vocabulary list)
   verbatim from `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py`. This is the same list
   t0021 used for its `EA-DV` (entity-accuracy domain-vocabulary) metric on both the biased-only and
   fine-tuned-only clean-21 runs — reusing it verbatim keeps the new row apples-to-apples with the
   two copied rows, per `REQ-16`. Satisfies `REQ-16`, `REQ-26`.

6. **Create `code/scoring.py`.** Copy verbatim from
   `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py`: `normalise()` (lines 55-58,
   lowercase + strip punctuation), `wer()` (lines 61-66, `jiwer.wer` on normalised text — note in a
   module docstring that this WER definition is documented in `research/research_summary.md` finding
   10 as *not* matching other tasks' `jiwer` normalisation exactly; this caveat must be repeated in
   the final comparison writeup so the 3-row table's WER numbers are not over-interpreted against
   other tasks' WER figures), and `domain_vocab_accuracy()` (lines 77-84, fraction of in-reference
   `DOMAIN_VOCAB` terms that also appear in the normalised hypothesis). Also copy
   `expand_casing_variants()` (lines 138-146, expands each vocab phrase to
   `{as-given, lower, Capitalized}` for boosting-tree phrase lists). Satisfies `REQ-16`, `REQ-26`.

7. **Create `code/run_ft_biased_eval.py`.** This is the main Part B script:
   * Import `DOMAIN_VOCAB` from `code.constants`, `normalise`/`wer`/`domain_vocab_accuracy`/
     `expand_casing_variants` from `code.scoring`, path constants from `code.paths`.
   * Copy `_ensure_transcribe_cfg()`, `_mono_path()`, and `transcribe()` (mono-conversion + per-clip
     wall-clock timing via `time.perf_counter()`) verbatim from
     `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` lines 92-123.
   * Copy `apply_malsd_boost(model, phrases, *, alpha, context_score, depth_scaling)` verbatim from
     `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 281-299: deep-copies
     `model.cfg.decoding`, sets `cfg.strategy = "malsd_batch"`, and via
     `OmegaConf.update(..., force_add=True)` sets `beam.beam_size = 4`,
     `beam.boosting_tree.key_phrases_list`, `beam.boosting_tree.context_score`,
     `beam.boosting_tree.depth_scaling`, `beam.boosting_tree_alpha`, then calls
     `model.change_decoding_strategy(cfg)`. **Do not** copy t0021's `apply_boosting()` (only ever
     sets `greedy_batch`) or t0023's `apply_greedy_boost()` (same broken mechanism) — this is the
     exact bug this task fixes, per `REQ-14`.
   * At import time, load `results/pareto_unified.json` (written by Step 2) and read
     `selected_cell.context_score`, `selected_cell.depth_scaling`, `selected_cell.alpha` into module
     constants `BOOSTING_CONTEXT_SCORE`, `BOOSTING_DEPTH_SCALING`, `BOOSTING_ALPHA`. Assert the file
     exists and has a `selected_cell` key; raise a clear `FileNotFoundError`/`KeyError` with a
     message pointing back to Step 2 if not — Part B must not proceed with a hardcoded fallback
     config if Part A's output is missing (`REQ-13`). Print the loaded config values at startup so
     the run log is a durable record of which cell was actually used.
   * `main()`: parse `--limit` (int, default `None`) and `--checkpoint` (`Path`, default
     `paths.T0021_FINETUNED_NEMO`) CLI args. Load clips from `paths.T0021_MANIFEST` (apply `--limit`
     by slicing). Load the model via `nemo_asr.models.ASRModel.restore_from(str(args.checkpoint))`
     (same pattern as `run_clean_eval.py` line 259), call `.eval()`. Build
     `phrases = expand_casing_variants(DOMAIN_VOCAB)` and call
     `apply_malsd_boost(model, phrases, alpha=BOOSTING_ALPHA, context_score=BOOSTING_CONTEXT_SCORE, depth_scaling=BOOSTING_DEPTH_SCALING)`
     once before the transcription loop (the boosting config is static across all clips — unlike
     t0021's `run_clean_eval.py`, which compared two separate model runs, this script runs one model
     configuration end to end).
   * Adapt `run_eval()` from `run_clean_eval.py` lines 154-212: for each clip, read audio from
     `paths.T0021_AUDIO_DIR / clip["audio_filename"]`, transcribe, compute `wer`, `ea_dv` (via
     `domain_vocab_accuracy`), and `latency_seconds`. Write one JSON record per line to
     `results/clean_eval_ft_biased.jsonl` with the identical schema to t0021's
     `data/clean_eval_finetuned.jsonl` (`clip_id`, `reference_text`, `transcript`, `wer`, `ea_dv`,
     `latency_seconds`, `duration_s`) so downstream comparison code can treat all three JSONL files
     uniformly. Print aggregate `WER`/`EA-DV`/latency-p50 to stdout at the end. Satisfies `REQ-12`,
     `REQ-13`, `REQ-14`, `REQ-15`, `REQ-16`, `REQ-26`.

8. **Provision the GPU machine and sync data (setup-machines step, referenced here for context — the
   actual acquisition happens in the orchestrator's separate `setup-machines` step per this plan's
   `## Remote Machines` section).** Once the machine is `ready`: `rsync` or `git clone` this repo
   (branch `task/t0024_biasing_pareto_and_ft_biasing_ablation`) onto the VM so
   `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/` and its dependency paths under
   `tasks/t0021_parakeet_finetune_vs_biasing/`, `tasks/t0022_gpu_pb_diagnostic/`,
   `tasks/t0023_tdt_vs_unified_biasing/` resolve identically to the local checkout. On the VM,
   inside the conda env `stt` (matches t0021/t0022/t0023's documented environment: NeMo 3.1.0, CUDA
   12.2), run `dvc pull tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_audio` (per
   `docs/dvc-data-workflow.md` and this repo's `CLAUDE.md`: "After `git pull`, always run `dvc pull`
   to sync data" — the 21 WAV clips are DVC-tracked, confirmed via
   `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_audio.dvc`, not committed as raw
   bytes). Verify: `ls tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_audio/*.wav | wc -l`
   must print `21`. Verify the checkpoint is present:
   `ls -la /mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` must succeed (this is a
   VM-local mount per t0021's `code/paths.py`, not something to copy from the git repo). This step
   supports `REQ-12`, `REQ-15`, `REQ-24` (confirms the eval set is used exactly as-is, nothing
   added).

9. **[CRITICAL, validation gate] Run the 5-clip smoke test on the GPU VM.** Baseline to compare
   against: t0021's fine-tuned-only (no boosting) run achieved `EA-DV = 38.1%` aggregate across all
   21 clips and correctly transcribed "Rezolve"/"Rezolve Ai" in 8 of 21 clips (t0021 §4). For a
   5-clip subset the exact aggregate is not reproducible, so the sanity floor is structural, not
   numeric: Run:
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0024_biasing_pareto_and_ft_biasing_ablation -- uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/run_ft_biased_eval.py --limit 5`.
   **Failure condition — halt and debug if any of these hold**: (a) the script errors out or
   crashes; (b) all 5 transcripts are empty strings; (c) the printed decoding-strategy confirmation
   does not show `"malsd_batch"` (if it silently shows `"greedy_batch"`, the boosting-tree swap from
   Step 7 did not take effect — this is exactly the bug this task exists to fix, so it must not
   silently recur). If any failure condition holds, **do not proceed to the full run** — inspect
   `model.cfg.decoding.strategy` immediately after `apply_malsd_boost()` is called, and check for a
   NeMo version mismatch between the fine-tuned checkpoint (t0021 environment: NeMo 3.1.0) and the
   VM environment. **Individual-output inspection (mandatory)**: read all 5 records written to
   `results/clean_eval_ft_biased.jsonl` (or the equivalent `--limit 5` output). For each, confirm
   the `transcript` field is a plausible, non-garbage transcription of `reference_text` (not empty,
   not repeated tokens), and spot-check whether any of the 5 reference texts contain a
   `DOMAIN_VOCAB` term (e.g., "Rezolve") and, if so, whether the hypothesis correctly reproduces it
   — compare qualitatively against t0021 §4's documented pattern (fine-tuned-only got "Rezolve"
   right in 8/21 cases; biasing on top should not make this worse). Satisfies the mandatory
   validation-gate requirement for this expensive GPU operation; supports `REQ-12`-`REQ-16`.

10. **[CRITICAL] Run the full 21-clip evaluation on the GPU VM.** Only after Step 9 passes its
    failure-condition check. Run:
    `uv run python -m arf.scripts.utils.run_with_logs --task-id t0024_biasing_pareto_and_ft_biasing_ablation -- uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/run_ft_biased_eval.py`.
    Expected output: `results/clean_eval_ft_biased.jsonl` with exactly 21 rows; stdout prints
    aggregate WER, EA-DV, and p50 latency. **Rejection gate** (see `## Rejection Criteria`): if
    fewer than 17 of the 21 clips produce a successful (non-exception) transcription, the resulting
    condition must be reported as null, not as a real measurement. `rsync` or `scp`
    `results/clean_eval_ft_biased.jsonl` back to the local checkout (or write directly to a path
    mounted/synced back) before tearing down the VM. Satisfies `REQ-12`, `REQ-13`, `REQ-14`,
    `REQ-15`, `REQ-16`.

**Milestone 2 checkpoint**: `results/clean_eval_ft_biased.jsonl` exists locally with 21 rows, each
with non-null `wer`, `ea_dv` (where a domain term is present in the reference), and
`latency_seconds`. The GPU VM has been torn down (handled by the orchestrator's separate `teardown`
step, not part of this plan's Step by Step).

### Milestone 3 — Comparison, Metrics, and Asset Creation (local, no GPU)

11. **Create `code/build_comparison.py`.** Assemble the 3-row comparison table (`REQ-17`):
    * Row 1 (biased-only, t0021, copied — not re-run): `WER = 64.4%`, `EA-DV = 0.0%`, latency `null`
      (t0021 never recorded per-clip latency for the biased-only clean-21 run — its Set B table has
      no latency column). Copy these two numbers literally from t0021's existing detailed writeup at
      `tasks/t0021_parakeet_finetune_vs_biasing/results/` (the file documenting the Set A/Set B eval
      tables), lines 37-38 (the "Set B — clean production clips" table).
    * Row 2 (fine-tuned-only, t0021, copied — not re-run): `WER = 55.8%`, `EA-DV = 38.1%`, copied
      from the same table. For latency, **do not** use the `0.112s` figure quoted in
      `task_description.md`'s comparison table — that number is t0021's **gold-92 (Set A)** latency
      (same t0021 writeup, line 30, the "Set A — gold-92" table), not the clean-21 (Set B) latency,
      which that table never reports. Instead, compute the correct clean-21 fine-tuned-only p50
      latency directly from the 21 raw `latency_seconds` values already present in t0021's existing
      `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_finetuned.jsonl` (read via
      `paths.T0021_CLEAN_FINETUNED`) — this is reading, not re-running, so it remains inside
      `REQ-25`'s "no new inference" boundary. The correct value (verified by hand during planning)
      is `p50 ≈ 0.0536s`. Report both numbers in the write-up with their provenance (`0.112s`
      labeled "task-description-quoted, gold-92, not clean-21" and `0.0536s` labeled "computed from
      t0021's existing clean-21 per-clip latencies") so the correction is auditable, not silently
      applied.
    * Row 3 (fine-tuned + `malsd_batch`-biased, new, this task): read
      `results/clean_eval_ft_biased.jsonl` (Step 10's output), compute aggregate `WER` (mean of
      per-clip `wer` where the reference is non-empty), `EA-DV` (mean of per-clip `ea_dv` where a
      domain term is present in the reference, matching t0021's `run_eval()` aggregation exactly),
      and `latency p50` (median of the 21 `latency_seconds` values).
    * Write `results/comparison_table.md` (the 3-row markdown table plus the row-2
      latency-provenance note) and `results/comparison.json` (structured:
      `{"biased_only": {...}, "finetuned_only": {...}, "finetuned_plus_malsd_biased": {...}}`, each
      with `wer`, `ea_dv`, `latency_p50_seconds` or `null`).
    * Print a short WER-normalisation caveat (from Step 6: `jiwer.wer` on lowercased/punctuation-
      stripped text, not identical to other tasks' `jiwer` usage) alongside the table so it is not
      over-interpreted against other tasks' WER numbers.
    * Answer `REQ-18` (does biasing improve EA-DV beyond 38.1%, especially on short clips /
      "brainpowa" clips?), `REQ-19` (does it regress WER/latency vs. fine-tuned-only?), and `REQ-20`
      (complementary or redundant?) directly from the row-3-vs-row-2 delta, cross-referencing the
      per-clip records in `results/clean_eval_ft_biased.jsonl` for the specific short-clip and
      "brainpowa" clips t0021 §4 named as failure modes (grep `reference_text` for `"brainpowa"` and
      for clips under ~2 words to identify them). Write these three answers into
      `results/comparison_table.md` as a short prose section beneath the table. Run:
      `uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/build_comparison.py`.
      Expected output: `results/comparison_table.md` and `results/comparison.json` exist; the 3rd
      row's numbers are non-null. Satisfies `REQ-17`, `REQ-18`, `REQ-19`, `REQ-20`, `REQ-25`,
      `REQ-27`.

12. **Write `results/metrics.json`** using the **explicit multi-variant format** (three comparable
    conditions being compared, per the `comparative-analysis`/`experiment-run` type guidance to use
    explicit variants whenever more than one condition is reported):
    ```json
    {
      "variants": [
        {
          "variant_id": "biased-only-t0021",
          "label": "Biased only (no fine-tune) — t0021, copied",
          "dimensions": {"model": "parakeet-unified-en-0.6b", "fine_tuned": false,
                          "biasing_strategy": "greedy_batch_turbobias", "source_task": "t0021"},
          "metrics": {"entity_accuracy_domain_vocab": 0.0}
        },
        {
          "variant_id": "finetuned-only-t0021",
          "label": "Fine-tuned only (no biasing) — t0021, copied",
          "dimensions": {"model": "parakeet-unified-en-0.6b", "fine_tuned": true,
                          "biasing_strategy": "none", "source_task": "t0021"},
          "metrics": {"entity_accuracy_domain_vocab": 0.381, "latency_p50_seconds": 0.0536}
        },
        {
          "variant_id": "finetuned-plus-malsd-biased-t0024",
          "label": "Fine-tuned + malsd_batch biasing — t0024, new",
          "dimensions": {"model": "parakeet-unified-en-0.6b", "fine_tuned": true,
                          "biasing_strategy": "malsd_batch", "source_task": "t0024"},
          "metrics": {"entity_accuracy_domain_vocab": "<computed in Step 11>",
                       "latency_p50_seconds": "<computed in Step 11>"}
        }
      ]
    }
    ```
    Fill the two `"<computed in Step 11>"` placeholders with the real values from
    `results/comparison.json` before writing the file — placeholders must never appear in the final
    committed file. **Deliberately omit `wer_gold92` from all three variants**: none of the three
    conditions was evaluated on the gold-92 benchmark (all three use the clean-21 set per `REQ-24`),
    and `wer_gold92`'s registered definition (`meta/metrics/wer_gold92`) is explicitly scoped to
    "the gold-92 benchmark" — forcing clean-21 WER numbers under that key would misrepresent the
    metric's dataset scope for any cross-task dashboard/leaderboard consumer. The three WER numbers
    (64.4%, 55.8%, and the new row's WER) remain fully reported, just in
    `results/comparison_table.md` and `results/comparison.json` as task-specific data rather than a
    registered project metric. Also state explicitly (do not just omit silently) that
    `action_critical_wer_gold92`, `entity_accuracy_gold92`, `intent_preservation_gold92`, and
    `wrong_action_rate_gold92` are inapplicable to this task for the same reason (no fresh gold-92
    evaluation happens in either part — Part A only re-reads existing sweep results, Part B
    evaluates on clean-21 only). Verify with:
    `uv run python -m arf.scripts.verificators.verify_task_metrics t0024_biasing_pareto_and_ft_biasing_ablation`.
    Satisfies the metrics-measurement requirement for every applicable registered metric
    (`entity_accuracy_domain_vocab`, `latency_p50_seconds`), with the
    `wer_gold92`/gold-92-scoped-metric omissions stated as deliberate.

13. **Create the `predictions` asset** `assets/predictions/parakeet-finetuned-malsd-biased-clean21/`
    (folder name matches the `predictions` ID regex `^[a-z0-9]+([.\-][a-z0-9]+)*$`), per
    `meta/asset_types/predictions/specification.md`:
    * `details.json`: `spec_version: "2"`,
      `predictions_id: "parakeet-finetuned-malsd-biased-clean21"`,
      `name: "Parakeet fine-tuned + malsd_batch biasing on clean-21"`, `short_description` (1-2
      sentences: fine-tuned unified checkpoint + tuned malsd_batch boosting, evaluated on the
      21-clip clean production set), `description_path: "description.md"`, `model_id: null` (no
      `model` asset exists for the t0021 checkpoint in this project), `model_description` (free
      text: `parakeet-unified-en-0.6b`, encoder frozen, 8.9M trainable decoder-head params,
      fine-tuned per t0021, checkpoint
      `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo`, decoded with
      `strategy=malsd_batch`, `beam_size=4`, boosting config
      `context_score=3.0/depth_scaling=0.5/alpha=1.5` selected by this task's Part A frontier
      analysis), `dataset_ids: []` (the clean-21 set has no registered `dataset` asset — t0021 never
      created one; state this explicitly rather than fabricating an ID),
      `prediction_format: "jsonl"`, `prediction_schema` (describe the 7 fields: `clip_id`,
      `reference_text`, `transcript`, `wer`, `ea_dv`, `latency_seconds`, `duration_s`),
      `instance_count: 21`, `metrics_at_creation` (the aggregate WER/EA-DV/latency-p50 from Step
      11),
      `files: [{"path": "files/predictions.jsonl", "description": "21-row per-clip fine-tuned + malsd_batch-biased transcripts on t0021's clean production eval set", "format": "jsonl"}]`,
      `categories: ["entity-correction", "stt-evaluation", "latency-profiling"]` (all three exist in
      `meta/categories/`), `created_by_task: "t0024_biasing_pareto_and_ft_biasing_ablation"`,
      `date_created: "2026-08-13"`.
    * `files/predictions.jsonl`: copy of `results/clean_eval_ft_biased.jsonl`.
    * `description.md`: all mandatory sections (`## Metadata`, `## Overview` [≥80 words],
      `## Model`, `## Data`, `## Prediction Format`, `## Metrics`, `## Main Ideas` [≥3 bullets],
      `## Summary` [≥100 words]) per `meta/asset_types/predictions/specification.md`. Verify:
      `uv run python -m meta.asset_types.predictions.verificator parakeet-finetuned-malsd-biased-clean21 --task-id t0024_biasing_pareto_and_ft_biasing_ablation`.
      Satisfies `REQ-21`.

14. **Create the shared `answer` asset** `assets/answer/production-decoding-and-biasing-ft-verdict/`
    (folder name derived as a slug from the question), per
    `meta/asset_types/answer/specification.md`. This is the **one** shared answer asset covering
    both parts (`REQ-22`), matching `task.json` `expected_assets.answer = 1`:
    * `details.json`: `spec_version: "2"`,
      `answer_id: "production-decoding-and-biasing-ft-verdict"`,
      `question: "Given the full Pareto frontier over brand_exact_rate vs neutral_wer for parakeet-tdt-0.6b-v3 and parakeet-unified-en-0.6b, what production decoding defaults should brainpowa-realtime-api use, and — evaluated on the 21-clip clean production set — are GPU-PB biasing and fine-tuning of parakeet-unified-en-0.6b complementary or redundant?"`,
      `short_title: "Production decoding defaults + biasing-vs- fine-tuning verdict"`,
      `short_answer_path: "short_answer.md"`, `full_answer_path: "full_answer.md"`,
      `categories: ["entity-correction", "stt-evaluation", "latency-profiling"]`,
      `answer_methods: ["code-experiment"]`, `source_paper_ids: []`, `source_urls: []`,
      `source_task_ids: ["t0021_parakeet_finetune_vs_biasing", "t0022_gpu_pb_diagnostic", "t0023_tdt_vs_unified_biasing", "t0024_biasing_pareto_and_ft_biasing_ablation"]`,
      `confidence: "medium"` (Part A's frontier answer is high-confidence — n=100 grid cells per
      model, deterministic re-analysis; Part B's complementary/redundant verdict is directional-only
      per `REQ-25`'s n=21 caveat, so the combined answer's overall confidence is medium, not high —
      state this split explicitly in the full answer rather than picking one number silently),
      `created_by_task: "t0024_biasing_pareto_and_ft_biasing_ablation"`,
      `date_created: "2026-08-13"`.
    * `short_answer.md`: `## Question` (verbatim), `## Answer` (2-5 sentences, direct, no hedging,
      no inline citations — state the recommended TDT production cell
      (`context_score=2.5, depth_scaling=0.5, alpha=2.0`, from Step 2/4) and the complementary-or-
      redundant verdict (from Step 11) as two direct sentences), `## Sources` (bullet list of the 4
      `source_task_ids`).
    * `full_answer.md`: all mandatory sections (`## Question`, `## Short Answer`,
      `## Research Process`, `## Evidence from Papers` [state "papers method not used"],
      `## Evidence from Internet Sources` [state "internet method not used"],
      `## Evidence from Code or Experiments`
      [summarize Steps 1-13: the Pareto scan code, chart outputs, the fine-tuned+biased GPU run, and the comparison table — with concrete numbers],
      `## Synthesis`
      [combine both parts' findings into one recommendation — e.g., ship the TDT config change to `brainpowa-realtime-api/src/ brainpowa_realtime_api/config.py` (state the exact `context_score`/`depth_scaling`/`alpha` to change to, per `REQ-5`), and state whether fine-tuning + malsd_batch biasing should also be pursued in production for the unified model given the complementary/redundant verdict],
      `## Limitations`
      [restate `REQ-25`'s two documented limitations: the frontier is scoped to t0022/t0023's 35-brand/10-neutral clip subset, not a larger re-derivation; Part B is n=21, directional only, consistent with t0021's own caveats],
      `## Sources`
      [with markdown reference link definitions per the spec, one per source task pointing at that task's folder]).
      Verify:
      `uv run python -m meta.asset_types.answer.verificator production-decoding-and-biasing-ft-verdict --task-id t0024_biasing_pareto_and_ft_biasing_ablation`.
      Satisfies `REQ-5`, `REQ-18`, `REQ-19`, `REQ-20`, `REQ-22`.

**Milestone 3 checkpoint (task complete)**: `results/metrics.json`,
`assets/predictions/parakeet-finetuned-malsd-biased-clean21/`, and
`assets/answer/production-decoding-and-biasing-ft-verdict/` all exist and pass their respective
verificators.

## Remote Machines

**Part B requires one GPU machine; Part A requires none.**

* `gpu_class: H100`
* `provider: azure_ml` (explicit — the Azure ML pool and Vast/Nebius can both serve `H100`, so an
  explicit provider is mandatory per `arf/specifications/remote_machines_specification.md`; this
  task uses the project's existing shared pool, consistent with t0021/t0022/t0023's prior GPU runs)
* **Pool**: `project/azure_vm.json` — 2×H100 (NC80-class) VMs, priority order `FT-NC80-v3` →
  `FT-NC80-v1` → `FT-NC80-v2` → `FT-MC`, each `$13.96/hr`. Shared with the finetuning team —
  coordinate via `#finetuning`/`#rail-arf-serving` Slack before claiming, per
  `arf/skills/setup-remote-machine/SKILL.md`.
* **Provisioning**:
  `uv run python -m arf.scripts.utils.azure_ml_vm acquire t0024_biasing_pareto_and_ft_biasing_ablation`
  (wrapped in `run_with_logs.py` per the skill's Critical Rule 1), handled by the orchestrator's
  separate `setup-machines` step (step 8 in `step_tracker.json`), not by this plan's Step by Step.
* **Estimated runtime**: well under 1 hour of actual GPU wall-clock (checkpoint load + `dvc pull` +
  5-clip validation + 21-clip full run), padded to 1.5 hours to account for SSH/environment setup
  overhead. See `## Cost Estimation`.
* **Teardown**:
  `uv run python -m arf.scripts.utils.azure_ml_vm teardown t0024_biasing_pareto_and_ft_biasing_ablation`
  immediately after Step 10 completes and results are synced back locally — handled by the
  orchestrator's separate `teardown` step (step 10 in `step_tracker.json`), not by this plan's Step
  by Step. Do not pass `--keep-running` — no approval for that has been given.

## Assets Needed

* **From t0022** (`t0022_gpu_pb_diagnostic`): `results/param_sweep.jsonl` — 100-row unified-model
  sweep grid, read-only input for Part A (Step 2).
* **From t0023** (`t0023_tdt_vs_unified_biasing`): `results/tdt_sweep.jsonl` — 100-row TDT-model
  sweep grid, read-only input for Part A (Step 2). `code/run.py`'s `apply_malsd_boost()` function
  (lines ~281-299) — code to copy, not import, into Step 7.
* **From t0021** (`t0021_parakeet_finetune_vs_biasing`): the fine-tuned checkpoint
  `/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` (VM-local mount, not a git/DVC
  asset); `data/clean_eval/manifest.jsonl` and `data/clean_eval_audio/` (DVC-tracked, 21 WAV clips)
  — read-only, exactly as-is, per `REQ-24`; `data/clean_eval_biased.jsonl` and
  `data/clean_eval_finetuned.jsonl` — existing per-clip results to copy numbers from (Step 11);
  `results/results_detailed.md` — source of the two copied comparison-table rows;
  `code/run_clean_eval.py`'s scoring functions and `code/constants.py`'s `DOMAIN_VOCAB` — code to
  copy, not import, into Steps 5-6.
* **From t0019** (`t0019_parakeet_biasing_improvement`): `code/make_charts.py` — structural chart
  pattern to copy into Step 3. `assets/answer/` and `assets/predictions/` folders — literal JSON-key
  structural templates for Steps 13-14.
* No external URLs, papers, or new datasets are needed. No registered `library` assets exist in this
  project (`assets/library/` is empty) to import from.

## Expected Assets

Matching `task.json` `expected_assets` (`predictions: 1`, `answer: 1`):

* **`predictions` asset** — `assets/predictions/parakeet-finetuned-malsd-biased-clean21/`: 21-row
  JSONL of fine-tuned + `malsd_batch`-biased transcripts on the clean-21 eval set, with per-clip
  `wer`, `ea_dv`, and `latency_seconds`. Produced by Step 13.
* **`answer` asset** — `assets/answer/production-decoding-and-biasing-ft-verdict/`: one shared
  answer covering (a) the exact `(context_score, depth_scaling, alpha)` cell recommended for
  `brainpowa-realtime-api`'s production TDT decoding config, with the numeric stance that justifies
  it, and (b) the complementary-vs-redundant verdict for biasing on top of the fine-tuned unified
  checkpoint. Produced by Step 14.

## Time Estimation

* **Research** (already done, prior to this plan): steps 1-6 of `step_tracker.json`, complete.
* **Milestone 1 (Part A implementation)**: ~45-60 minutes — writing and running `code/paths.py`,
  `code/pareto.py`, `code/make_charts.py`, `results/frontier_tables.md`. Local, no GPU wait time.
* **Milestone 2 (Part B implementation, including GPU wall-clock)**: ~1.5-2 hours — writing
  `code/constants.py`/`code/scoring.py`/`code/run_ft_biased_eval.py` locally (~30-40 min), GPU
  machine acquisition + sync + `dvc pull` (~15-20 min), validation-gate run + inspection (~10 min),
  full run (~5-10 min), teardown (~5 min).
* **Milestone 3 (comparison, metrics, assets)**: ~45-60 minutes — `code/build_comparison.py`,
  `results/metrics.json`, the predictions asset, and the answer asset (the fullest write, given the
  mandatory-sections list).
* **Total implementation estimate**: ~3-3.5 hours wall-clock plus the ~1.5 hour GPU rental window
  already counted inside Milestone 2.

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| `apply_malsd_boost()` (`strategy="malsd_batch"`, `beam.beam_size=4`) is incompatible with the fine-tuned checkpoint's decoder config (t0023 only validated it on the non-fine-tuned model; t0021's fine-tune only touched decoder heads, encoder frozen) — `change_decoding_strategy` could raise or silently no-op on this checkpoint. | Medium | High — blocks Part B entirely | The Step 9 validation gate (5-clip run) surfaces this immediately before any full-scale GPU time is spent. If it fails, inspect `model.cfg.decoding.strategy` right after the call and compare the fine-tuned checkpoint's decoder architecture against the non-fine-tuned `parakeet-unified-en-0.6b` used in t0022/t0023. If genuinely incompatible after investigation, write an intervention file documenting the blocker — do not silently fall back to `greedy_batch` (the exact broken config `REQ-14` forbids reusing). |
| The shared Azure ML H100 pool (`project/azure_vm.json`) is occupied by the finetuning team when this task needs it. | Medium | Medium — delay, not a hard block | `setup-remote-machine`'s priority-ordered pool (`FT-NC80-v3` → `FT-NC80-v1` → `FT-NC80-v2` → `FT-MC`) gives 4 fallback VMs; coordinate via `#finetuning`/`#rail-arf-serving` Slack before claiming, per the skill. This task's GPU need is short (<1 hr), so it should be schedulable within a normal work session even with contention. |
| `clean_eval_audio` is DVC-tracked and not yet pulled on a fresh VM — `transcribe()` fails with file-not-found on all 21 clips. | Medium | Medium — wastes GPU time if hit mid-run instead of pre-run | Step 8 runs `dvc pull tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_audio` and verifies `ls .../clean_eval_audio/*.wav \| wc -l` equals 21 **before** Step 9's validation-gate run, not after a failure. |
| `pareto_frontier()`/`select_frontier_cell()` in `code/pareto.py` is implemented with a naive sort-and-scan instead of a true non-dominated-point check, silently keeping a dominated point ahead of a same-`neutral_wer`, higher-`brand_exact_rate` row (both sweeps contain `neutral_wer` ties). This is a real mistake made and caught by hand during planning, not a hypothetical. | Low-Medium | High — a wrong frontier flows into both the production recommendation (`REQ-5`) and Part B's boosting config (`REQ-13`), meaning a GPU run could be spent on the wrong config | Step 2 mandates the O(n²) pairwise non-domination check explicitly and states the exact 5-cell-per-model expected frontier composition (see `## Approach`) as a correctness check. Before proceeding to Step 7, verify `len(frontier) == 5` for both `results/pareto_tdt.json` and `results/pareto_unified.json` — a different count signals the check needs re-inspection. |
| The task-description-quoted fine-tuned-only latency (`0.112s`) is actually t0021's gold-92 (Set A) latency, not the clean-21 (Set B) latency the 3-row comparison table needs — confirmed during planning by reading `results_detailed.md` lines 27-39 and recomputing from the raw per-clip data (`p50 ≈ 0.0536s` on clean-21). | Certain (already confirmed) | Medium — using `0.112s` in the comparison table would make the new fine-tuned+biased row's latency delta misleading against a same-dataset baseline | Step 11 mandates recomputing the clean-21 p50 directly from t0021's existing `data/clean_eval_finetuned.jsonl` per-clip `latency_seconds` field rather than trusting the task-description figure, and documents both numbers with provenance so the correction is auditable. |

## Verification Criteria

* Run
  `uv run python -u -m arf.scripts.verificators.verify_plan t0024_biasing_pareto_and_ft_biasing_ablation`
  — expect **zero errors** (this plan document itself).
* Run `uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/pareto.py` then
  check:
  `python3 -c "import json; d=json.load(open('tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_tdt.json')); assert len(d['frontier'])==5 and d['live_prod_on_frontier'] is False"`
  — expect no `AssertionError` (TDT frontier has exactly 5 cells, live-prod point confirmed off the
  frontier). Repeat the length check for `results/pareto_unified.json`.
* Run
  `ls -la tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/images/pareto_tdt.png tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/images/pareto_unified.png`
  — expect both files to exist with size greater than 10,000 bytes each.
* Run `wc -l tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/clean_eval_ft_biased.jsonl`
  — expect exactly `21`.
* Run
  `uv run python -m meta.asset_types.predictions.verificator parakeet-finetuned-malsd-biased-clean21 --task-id t0024_biasing_pareto_and_ft_biasing_ablation`
  — expect exit code 0, all checks passed.
* Run
  `uv run python -m meta.asset_types.answer.verificator production-decoding-and-biasing-ft-verdict --task-id t0024_biasing_pareto_and_ft_biasing_ablation`
  — expect exit code 0, all checks passed.
* Run
  `uv run python -m arf.scripts.verificators.verify_task_metrics t0024_biasing_pareto_and_ft_biasing_ablation`
  — expect zero errors, and manually confirm `results/metrics.json` contains only
  `entity_accuracy_domain_vocab` and `latency_p50_seconds` keys (no `wer_gold92` or other
  gold-92-scoped keys, per the deliberate-omission reasoning in Step 12).
* **Requirement coverage check**: run
  `grep -o "REQ-[0-9]*" tasks/t0024_biasing_pareto_and_ft_biasing_ablation/plan/plan.md | sort -u -V`
  and manually confirm all `REQ-1` through `REQ-27` appear at least once outside the
  `## Task Requirement Checklist` section itself (i.e., each is referenced by at least one Step by
  Step step) — every requirement in this plan's checklist is mapped to an implementation step, with
  no orphaned `REQ-*` IDs.

## Rejection Criteria

Pre-registered before any GPU run, so these cannot be loosened after seeing results:

* **Part B, default benchmark rule**: if fewer than `17` of the `21` clips (`17/21 ≈ 0.81 ≥ 0.8`)
  produce a successful transcription (no exception raised during `transcribe()`), the "fine-tuned +
  `malsd_batch`-biasing" condition is **null** — report it as an infrastructure failure, not as a
  real WER/EA-DV/latency measurement, regardless of what the successful subset's numbers show. This
  follows the project default: `successful_requests / total_requests < 0.8` ⇒ null (see `LESSONS.md`
  Lesson 3).
* **Part B, validation-gate rule**: if the Step 9 5-clip validation run shows the decoding strategy
  is not `"malsd_batch"` after `apply_malsd_boost()` is called, or all 5 transcripts are empty, the
  pipeline is broken, not merely under-performing — the task must halt and debug before any
  full-scale numbers from Step 10 can be treated as valid. A full 21-clip run executed despite this
  failure condition produces a **null** result regardless of its aggregate numbers.
* **Part B, config-provenance rule**: if `code/run_ft_biased_eval.py` cannot load a `selected_cell`
  from `results/pareto_unified.json` (Step 2's output missing or malformed), Part B must not proceed
  with a hardcoded fallback boosting config (e.g., silently reverting to t0022's old headline cell).
  Any run executed under a fallback config not sourced from Part A's own frontier answer is **null**
  for the purposes of answering `REQ-13`/`REQ-20` — it would not test what the task asks.
* **Part A**: if either `param_sweep.jsonl` or `tdt_sweep.jsonl` does not contain exactly 100 valid
  rows at read time (contradicting the file counts confirmed during planning), the frontier
  computation for that model is **null** until the discrepancy is investigated — do not silently
  proceed on a truncated or corrupted file and report a frontier as if it were the full grid.
