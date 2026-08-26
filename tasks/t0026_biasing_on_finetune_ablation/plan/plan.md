---
spec_version: "2"
task_id: "t0026_biasing_on_finetune_ablation"
date_completed: "2026-08-26"
status: "complete"
---
# Plan: Biasing on Top of Fine-Tuning — Complementary or Redundant?

## Objective

Run a clean 2x2 ablation of GPU-PB context biasing x `parakeet-unified` fine-tuning on the 91-clip
`clean_eval_v2` holdout set, to answer: **does GPU-PB context biasing still add brand accuracy once
the model has already been fine-tuned on Rezolve domain audio, or do the two techniques recover the
same errors?** This completes Part B of `t0024_biasing_pareto_and_ft_biasing_ablation`, which was
deferred (suggestion `S-0024-01`) because the fine-tuned checkpoint could not be found on any
reachable machine at the time. Both blockers are now resolved: the checkpoint is archived as the DVC
model asset `parakeet-unified-v5` (task `t0024_parakeet_unified_checkpoint_archive`), and a
decontaminated 91-clip holdout (`clean_eval_v2`) exists (task `t0021_parakeet_finetune_vs_biasing`).

Four arms run on the same 91 clips with the same scoring code, in a single GPU session on
`LLM-T1-NC80`:

| Arm | Model | Decoding |
| --- | --- | --- |
| A — base, no bias | `nvidia/parakeet-unified-en-0.6b` (HuggingFace pretrained) | `malsd_batch`, no boosting tree |
| B — base + bias | `nvidia/parakeet-unified-en-0.6b` | `malsd_batch` + GPU-PB, `context_score=3.0, depth_scaling=0.5, alpha=1.5` |
| C — FT, no bias | `parakeet-unified-v5` (DVC checkpoint) | `malsd_batch`, no boosting tree |
| D — FT + bias | `parakeet-unified-v5` (DVC checkpoint) | `malsd_batch` + GPU-PB, `context_score=3.0, depth_scaling=0.5, alpha=1.5` |

Done looks like: 4 `predictions` assets (one per arm) and 1 `answer` asset stating whether biasing
is complementary to fine-tuning (arm D beats both B and C) or redundant (arm D lands within noise of
`max(B, C)`), backed by per-arm `brand_exact_rate`/`neutral_wer`/`overall_wer`/inference-time
metrics, three charts, a paired McNemar significance test for B-vs-D and C-vs-D, and a per-clip
mechanism table showing which lever fixes which clips — all committed under
`tasks/t0026_biasing_on_finetune_ablation/`, all plan verificators and asset verificators passing
with zero errors.

## Task Requirement Checklist

Operative task text (from `task.json` `short_description` and `task_description.md`):

> "2x2 ablation of GPU-PB biasing x parakeet-unified fine-tuning on the 91-clip clean_eval_v2
> holdout. Completes t0024's deferred Part B." … "does GPU-PB context biasing still add brand
> accuracy once the model has already been fine-tuned on Rezolve domain audio, or do the two
> techniques recover the same errors?"

* **REQ-1**: Run all 4 arms (A/B/C/D as defined above) on the same 91 `clean_eval_v2` clips with a
  single shared scoring function, in one GPU session. Satisfied by Steps 4-7 (Milestone 2).
  Evidence: `results/ablation_metrics.json` containing all 4 arms and
  `results/arm_*_predictions.jsonl` with 91 rows each.
* **REQ-2**: All four arms (including the two unbiased ones, A and C) must use `malsd_batch`
  decoding — `greedy_batch` is forbidden for any arm because it silently ignores the boosting tree,
  which would confound decoder-strategy with the biasing effect. Satisfied by Step 5
  (`code/boosting.py`). Evidence: `code/boosting.py` diff shows `apply_malsd_no_boost` and
  `apply_malsd_boost` are the only two decoding-setup functions called by `code/run_ablation.py`.
* **REQ-3**: Arms B and D must use the fixed, already-selected Pareto-frontier biasing cell
  `context_score=3.0, depth_scaling=0.5, alpha=1.5` (60.0% `brand_exact_rate` at 8.7% `neutral_wer`
  on the original sweep), read directly from
  `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` — **not**
  re-swept. Satisfied by Step 4. Evidence: `code/constants.py` hardcodes the cell with a comment
  citing the source file; no sweep loop exists in `code/run_ablation.py`.
* **REQ-4**: Fix `clean_eval_v2/manifest.jsonl`'s absolute macOS `audio_filepath` values
  (`/Users/margotiamanova/Desktop/...`) to resolve on the GPU machine, without committing
  machine-specific paths back to git and without modifying `t0021`'s files. Satisfied by Step 3.
  Evidence: `tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl`
  exists (gitignored), has 91 rows, and every `audio_filepath` resolves to an existing file.
* **REQ-5**: Compute `brand_exact_rate` (overall, `Rezolve`-only, `brainpowa`-only), `neutral_wer`
  (over the 48 non-brand clips), `overall_wer` (all 91 clips), and
  `efficiency_inference_time_per_item_seconds`, per arm, using one shared scoring function so all
  four arms are comparable. Satisfied by Steps 4-7. Evidence: `results/ablation_metrics.json` has
  one object per arm with all five fields populated.
* **REQ-6**: Report `brainpowa` separately from `Rezolve` and treat any `brainpowa` delta as
  anecdotal — only 3 `brainpowa` clips exist, insufficient to resolve a `brainpowa`-specific effect.
  Satisfied by Step 9 and the Rejection Criteria section below. Evidence:
  `results/ablation_metrics.json` breaks `brand_exact_rate` into `overall`/`rezolve`/`brainpowa`
  keys and the answer asset's Limitations section states the n=3 power caveat explicitly.
* **REQ-7**: `results/metrics.json` must be `{}` — every registered project metric except
  `latency_p50_seconds` is defined against gold-92 ground truth (which this task deliberately does
  not use), and `latency_p50_seconds` measures full end-to-end voice-to-action latency, not this
  task's single-clip batch inference timing. Satisfied by Step 8 (deliberate-omission statement) —
  see Phase 1 metrics review below. Evidence: `results/metrics.json` content is literally `{}`,
  confirmed by `verify_task_metrics.py`.
* **REQ-8**: Answer key questions Q1-Q5 from `task_description.md`: (Q1/Q2) is arm D significantly
  above both B and C, or within noise of `max(B, C)`; (Q3) per-clip 2x2 confusion of B-vs-C
  correctness; (Q4) does biasing cost the same `neutral_wer` on the FT model as on the base model;
  (Q5) should `t0025_parakeet_tdt_brand_finetune` proceed as scoped. Satisfied by Steps 6, 7, 9, 10.
  Evidence: the answer asset's `full_answer.md` has one paragraph per question under `## Synthesis`.
* **REQ-9**: Report a paired McNemar test on per-clip brand correctness for the B-vs-D and C-vs-D
  comparisons (not just aggregate percentage-point deltas), because n=43 brand-containing clips is
  too small for aggregate deltas alone to separate signal from noise. Satisfied by Step 7. Evidence:
  `results/mcnemar_results.json` has `b_vs_d` and `c_vs_d` entries with discordant-pair counts and
  p-values.
* **REQ-10**: Reuse `apply_malsd_boost`/brand-scoring/`wer` code rather than copy-pasting a sixth
  time. Resolved as: **copy into this task's own `code/`** (see Approach section for the
  copy-vs-library tradeoff decision). Satisfied by Step 2. Evidence: `code/scoring.py`,
  `code/boosting.py`, `code/constants.py` exist with header comments citing their `t0021`/`t0023`
  source lines.
* **REQ-11**: Produce four `predictions` assets (one per arm, `clean_eval_v2` scope) and one
  `answer` asset carrying the complementary-vs-redundant verdict and production recommendation.
  Satisfied by Steps 8 and 10 (Milestone 4). Evidence: `assets/predictions/<4 ids>/details.json` and
  `assets/answer/<id>/details.json` all pass their respective asset verificators.
* **REQ-12**: Produce 3 charts to `results/images/`, embedded in `results_detailed.md`: (1) grouped
  bar of `brand_exact_rate` by arm x bucket, (2) scatter of `neutral_wer` vs `brand_exact_rate` per
  arm with the unified Pareto frontier overlaid, (3) 2x2 heatmap of per-clip B-vs-C brand
  correctness. Satisfied by Step 9. Evidence: `results/images/chart1_brand_exact_rate.png`,
  `chart2_pareto_scatter.png`, `chart3_bc_confusion_heatmap.png` exist, each > 10,000 bytes.
* **REQ-13**: Produce a main results table (arms A-D x `brand_exact_rate` overall/Rezolve/brainpowa,
  `neutral_wer`, `overall_wer`, inference time), a paired-test table (B-vs-D and C-vs-D x discordant
  counts, McNemar statistic, p-value), and a clip-level appendix (clips fixed by exactly one lever,
  with reference and all four hypotheses). Satisfied by Step 9 (implementation work ends here per
  the Forbidden list below — the orchestrator's `results` step renders these tables into
  `results_detailed.md` from the JSON files this plan's steps produce).
* **REQ-14**: Pin GPU execution to `LLM-T1-NC80`, `CUDA_VISIBLE_DEVICES=1` explicitly in every
  command (not the default), never write durable output to `/mnt`, `dvc pull` the checkpoint into
  the task folder, and `dvc push` anything worth keeping before teardown. Satisfied by the Remote
  Machines section and Step 1. Evidence: `results/remote_machines_used.json` records
  `LLM-T1-NC80`/GPU 1; `code/paths.py` has no `/mnt` write path; DVC status is clean after
  `dvc push`.
* **REQ-15**: Sequence GPU access with `t0025_parakeet_tdt_brand_finetune` — the two cannot run GPU
  work concurrently on `LLM-T1-NC80` today (`acquire()` refuses a VM it finds already `Running`).
  This task must run, then fully teardown, before `t0025` acquires the box. Satisfied by the Remote
  Machines section (this is an execution-order constraint enforced by the orchestrator's
  `setup-machines`/`teardown` steps, not a step inside this plan's own Step by Step).

## Approach

### Grounding findings from research

* `malsd_batch` is mandatory for every arm, including the unbiased ones. `t0022_gpu_pb_diagnostic`
  proved `greedy_batch` + GPU-PB gives 0% brand EXACT identically to no boosting at all — the
  boosting tree is not consulted under that decoding strategy. Pairing "no bias" with `greedy_batch`
  would confound the decoder-strategy change with the biasing effect this task exists to measure.
* Biasing alone does not generalize off its own tuning set: `t0021_parakeet_finetune_vs_biasing`
  measured 0.0% entity accuracy for GPU-PB biasing on 21 unseen clips vs 34.8% on gold-92 (the set
  its hyperparameters were tuned against). Fine-tuning held up better on the same 21 clips (38.1%
  with no boosting at all). This is the direct motivation for the ablation — whether biasing still
  helps once fine-tuning has already moved the model, on a holdout set that overlaps neither the
  biasing tuning set nor the fine-tuning training data.
* Arm D (fine-tuned checkpoint + `malsd_batch` boosting via `restore_from()`) has never been run by
  any prior task. `t0021`'s finetuned eval called `.transcribe()` with pure NeMo defaults, no
  decoding-strategy change at all. `t0024` Part B was scoped for exactly this combination but never
  executed — $14.06 was spent on GPU provisioning with the checkpoint and its `stt` conda env
  unreachable, zero results. This makes arm D the one genuinely novel code path in this task and the
  primary implementation risk (see Risks & Fallbacks).
* The biasing hyperparameter cell (`context_score=3.0, depth_scaling=0.5, alpha=1.5`) is already
  selected by `t0024` Part A's Pareto-frontier analysis and must not be re-swept —
  `t0019_parakeet_biasing_improvement`'s sweep independently confirms this cell is near a local
  optimum (far-from-default values wreck `neutral_wer` by 20-27 absolute points).
* Two incompatible entity-accuracy metrics exist in this project: `t0021`'s `domain_vocab_accuracy`
  (loose substring match) and `t0022`/`t0023`'s `brand_exact_rate` family (`label_brand` returning
  `EXACT`/`PHONETIC`/`GARBAGE` via word-boundary-anchored regex). This task requires
  `brand_exact_rate` per `task_description.md`'s Metrics section — the `t0022`/`t0023` scoring
  apparatus is the one to copy, not `t0021`'s.
* `clean_eval_v2/manifest.jsonl` stores absolute macOS paths from the annotator's laptop
  (`/Users/margotiamanova/Desktop/REZOLVE AI/rail-arf-stt/...`), confirmed present by direct read of
  the file. Every `audio_filepath` must be rewritten to resolve on the GPU machine before any
  inference, or every arm fails to load audio.
* Task-status bookkeeping in this project has shown false negatives twice
  (`t0024_parakeet_unified_checkpoint_archive`, `t0019_parakeet_biasing_improvement`) — assets on
  disk are the source of truth, not `task.json` `status` fields, if any dependency check looks
  suspiciously empty.

### Copy-vs-library decision (REQ-10)

`task_description.md` explicitly raises two options for reusing `apply_malsd_boost`, `DOMAIN_VOCAB`,
and the clean-eval scoring functions: import them, or — "if the import path is genuinely unworkable
across task folders" — promote them to a registered `library` asset per `S-0024-05` and have this
task be the first consumer. Research (`research_code.md`) confirms `aggregate_libraries` currently
returns 0 registered libraries project-wide, and that four existing cross-task imports (`t0019`,
`t0022`, `t0023` importing `DOMAIN_VOCAB` from `t0017`'s `code/` package) already violate the
project's own rule that only registered `library` assets — not raw `code/` packages — may be
imported across task folders.

**Decision: copy the helpers into this task's own `code/` directory; do not promote a library in
this task.** Reasoning: `task.json`'s `expected_assets` for this task is
`{"predictions": 4, "answer": 1}` — it does not provision a `library` deliverable, and authoring one
(folder structure, `details.json`, a description document with mandatory sections per
`meta/asset_types/library/specification.md`) is realistic added scope this task was not sized for.
Copying ~130 lines of already-reviewed, already-correct code (per research: no adaptation needed for
`apply_malsd_boost`, `label_brand`, `brand_in_ref`, `wer`, `build_phrase_list`; minor adaptation
only for `load_audio`/`transcribe`) is the smaller, lower-risk change, and it follows the exact
pattern `task.json`'s cross-task import rule already requires. **Alternative considered and
rejected**: promoting a library now, since `t0025_parakeet_tdt_brand_finetune` is already queued as
a further consumer and would benefit — rejected for this task because it changes `task.json`'s scope
unilaterally and is better decided once, deliberately, rather than as a side effect of this
ablation. This tradeoff is flagged as a strong candidate for `results/suggestions.json` at the end
of this task (not resolved here) — a future task should scaffold `boosting_scoring_lib` as a
registered library with `apply_malsd_boost`, `apply_malsd_no_boost`, the brand-scoring family, and
`wer`, so the sixth and seventh consumers (this task now, `t0025` next) do not each duplicate the
same ~130 lines a further time.

### Manifest-fix approach (REQ-4)

Rather than editing `t0021`'s `data/clean_eval_v2/manifest.jsonl` in place (which would modify files
outside this task's own folder and risks committing machine-specific paths if done carelessly), this
task reads `t0021`'s manifest as input and writes a corrected copy to its own
`tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl`, gitignored like
every other task's `data/` directory in this project (see `tasks/t0021_.../data/.gitignore` for
precedent). Each `audio_filepath` is rewritten from the annotator's absolute macOS path to
`REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/audio" / <basename>`,
resolved fresh on whichever machine runs the script. `t0021`'s original file, and its DVC-tracked
audio, are never modified.

### Task types

`task.json` already lists `task_types: ["experiment-run", "answer-question"]`, confirmed as the
correct match: this task varies two independent variables (biasing on/off, fine-tuning on/off) and
reports the interaction as the deliverable, and its final output is an `answer` asset resolving a
specific question. No `task_types` update is needed. Guidance followed from
`meta/task_types/experiment-run/instruction.md`: use `run_with_logs` for script execution, save all
raw per-clip outputs (not just aggregates) for diagnostic traceability, generate at least 2 charts
(this plan produces 3), treat below-baseline results as a pipeline bug not a finding, and inspect
individual outputs after every validation run before scaling up. Guidance followed from
`meta/task_types/answer-question/instruction.md`: one answer asset for the single question, written
only after the ablation's evidence is stable, direct/decisive style with no inline citations in the
short answer, and explicit statement of the `brainpowa` n=3 power limitation as an evidence-quality
caveat rather than papering over it.

### Alternative approaches considered

* **Re-sweep the biasing hyperparameters on the fine-tuned checkpoint** instead of reusing the fixed
  cell — rejected per `task_description.md`'s explicit instruction ("Re-tuning it on the FT
  checkpoint would confound the ablation and burn GPU hours") and `t0019`'s independent confirmation
  that re-tuning near this cell finds nothing new.
* **Evaluate on gold-92 instead of `clean_eval_v2`** — rejected because `train_v5` (the fine-tuning
  data) contains 60 of gold-92's 93 clips by exact `clip_id`; any figure on gold-92 for
  `parakeet-unified-v5` is inflated by training contamination. `clean_eval_v2` is the decontaminated
  set built specifically to fix this.
* **Use `t0021`'s `domain_vocab_accuracy` metric** instead of `brand_exact_rate` — rejected because
  `task_description.md`'s Metrics section names `brand_exact_rate` explicitly, and the two metrics
  are not comparable (fractional substring match vs. strict EXACT/PHONETIC/GARBAGE classification).
* **Run two separate GPU sessions (base model, then fine-tuned model)** instead of one session
  covering all 4 arms — rejected: both models are 0.6B parameters and fit comfortably in one
  session's GPU memory, and a single session avoids double VM-start/dvc-pull overhead, keeping this
  well under the ~2 GPU-hour estimate.

## Cost Estimation

* **Remote compute (Azure ML, `LLM-T1-NC80`, GPU 1, H100 NVL)**: ~2 GPU-hours at $13.96/hr ≈
  **$28**. Basis: 4 arms x 91 clips of batch inference on a 0.6B parameter model is well under an
  hour of pure GPU compute; wall clock is dominated by VM start, `dvc pull` of the checkpoint (2.47
  GB) and audio (11.5 MB), and `stt` conda env verification, all one-time per session. This matches
  `t0017_parakeet_biasing_buffer_replacement`'s $13.40/hour rate precedent and is far below
  `t0015_streaming_buffer_interval`'s $287.58/20.6-GPU-hour run (that task ran a much larger sweep).
* **API calls**: **$0**. No paid LLM or external API calls — the base model is pulled from
  HuggingFace (`nvidia/parakeet-unified-en-0.6b`, no cost), and the fine-tuned checkpoint is pulled
  from the project's own DVC remote (Azure Blob storage, already-provisioned).
* **Claude Code orchestration**: ~$3, based on `t0002_baseline_evaluation`'s $2.50 precedent for a
  comparably-scoped task (moderate step count, no massive log volumes to process).
* **Total estimated cost: ~$31.** Compared against `project/budget.json`: total project budget is
  $2000, per-task default limit is $100 (this task has no `task_budget_limit_usd` override in
  `task.json`, so the $100 default applies) — $31 is 31% of the per-task limit. Aggregate project
  spend before this task is $325.08 (16.25% of budget, $1674.92 remaining before the $2000 stop
  threshold and $1274.92 remaining before the 80%/$1600 warn threshold). This task's estimated $31
  leaves the project comfortably under both thresholds.

## Step by Step

### Milestone 1: Manifest fix and code scaffolding (no GPU required, runs locally)

1. **[CRITICAL] Create `code/paths.py`.** Define path constants: `REPO_ROOT` (via
   `Path(__file__).parents[3]`), `TASK_DIR`, `DATA_DIR`, `RESULTS_DIR`,
   `T0021_MANIFEST = REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/manifest.jsonl"`,
   `T0021_AUDIO_DIR = REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/audio"`,
   `FIXED_MANIFEST = DATA_DIR / "clean_eval_v2_manifest_fixed.jsonl"`,
   `FT_CHECKPOINT = REPO_ROOT / "tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo"`,
   `PARETO_UNIFIED_JSON = REPO_ROOT / "tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json"`.
   No inputs beyond `__file__`; output is the module itself. Satisfies REQ-4, REQ-14.

2. **[CRITICAL] Copy scoring/boosting/constants code into this task's `code/` directory.** Copy,
   verbatim except for noted adaptations, from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` and
   `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` — do not import cross-task (see
   Approach section decision).

   * `code/constants.py`: copy `DOMAIN_VOCAB` verbatim from
     `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` (31 terms). Also copy
     `TARGET_BRANDS`, `BRAND_VARIANTS`, `PHONETIC_PATTERNS`, `EXACT_PATTERNS`, `TERM_FILTER` from
     `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 85-97, no adaptation. Add the frontier
     cell as a named constant:
     `SELECTED_CELL = {"context_score": 3.0, "depth_scaling": 0.5, "alpha": 1.5}` with a comment
     citing `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` as the
     source (read at runtime in Step 4 to confirm the constant matches, not re-derived).
   * `code/scoring.py`: copy `label_brand` (lines 186-191), `brand_in_ref` (lines 194-200), `wer`
     (lines 203-218), `_expand_casing_variants` (lines 221-230), and `build_phrase_list` (lines
     233-240) verbatim from `tasks/t0023_tdt_vs_unified_biasing/code/run.py`. Import
     `DOMAIN_VOCAB`/`BRAND_VARIANTS` from this task's own `code/constants.py` (Step 2's first
     bullet), not from `t0023`.
   * `code/boosting.py`: copy `apply_malsd_boost` verbatim from
     `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 281-299 (sets `strategy="malsd_batch"`,
     `beam.beam_size=4`, and the three boosting-tree OmegaConf keys). Add one new function,
     `apply_malsd_no_boost(model: Any) -> None`, modeled on `reset_greedy_no_boost`
     (`tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 248-256) but targeting `malsd_batch`
     instead of `greedy_batch`: set `cfg.strategy = "malsd_batch"` and `beam.beam_size = 4` via the
     same `OmegaConf`/`open_dict` pattern, **without** setting any `beam.boosting_tree.*` keys —
     this is the "no bias" arm's decoding config (REQ-2: `malsd_batch` for all arms, but only B/D
     get a boosting tree). This function does not exist in any prior task; it is a ~10-line new
     function, not a copy.
   * `code/audio_io.py`: copy `load_audio` (lines 145-155), `_decode_output` (lines 158-172), and
     `transcribe` (lines 175-183) from `tasks/t0023_tdt_vs_unified_biasing/code/run.py`. Adaptation:
     `clean_eval_v2` audio is already 16kHz (per `t0021`'s DVC recording), so the `soxr.resample`
     branch inside `load_audio` should be unreachable in practice — keep it as a guard, do not
     remove it.

   Expected output: `code/constants.py`, `code/scoring.py`, `code/boosting.py`, `code/audio_io.py`
   exist;
   `uv run python -c "from tasks.t0026_biasing_on_finetune_ablation.code import constants, scoring, boosting, audio_io"`
   imports cleanly with no errors. Satisfies REQ-2, REQ-3, REQ-10.

3. **[CRITICAL] Fix the manifest paths.** Create `code/fix_manifest.py`. Read every line of
   `paths.T0021_MANIFEST` (JSON per line: `clip_id`, `audio_filepath`, `text`, `source`). For each
   row, replace `audio_filepath` with
   `str(paths.T0021_AUDIO_DIR / Path(original_audio_filepath).name)` — i.e., keep the same filename,
   point at this repo's actual `t0021` audio directory instead of the annotator's macOS path. Write
   the corrected 91 rows to `paths.FIXED_MANIFEST`
   (`tasks/t0026_biasing_on_finetune_ablation/data/clean_eval_v2_manifest_fixed.jsonl`). Add
   `tasks/t0026_biasing_on_finetune_ablation/data/.gitignore` containing `*.jsonl` so the fixed
   manifest (which contains a machine-resolved absolute path once written) is never committed — do
   not commit machine-specific paths back, per `task_description.md`. After writing, assert every
   row's `audio_filepath` resolves to an existing file:
   `assert all(Path(r["audio_filepath"]).exists() for r in rows)` and `assert len(rows) == 91`; exit
   non-zero with a clear message if either assertion fails. Run via
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0026_biasing_on_finetune_ablation -- python -u tasks/t0026_biasing_on_finetune_ablation/code/fix_manifest.py`.
   Expected output: script prints `Fixed manifest: 91/91 rows resolve to existing files` and exits
   0\. This step can run locally before GPU acquisition (no NeMo import needed) — do it before Step
   8 (`setup-machines`) so the manifest is ready the moment the GPU box is up. Satisfies REQ-4.

### Milestone 2: Ablation run script (runs on `LLM-T1-NC80`, GPU 1, conda env `stt`)

4. **[CRITICAL] Write `code/run_ablation.py`.** CLI via `argparse`: `--limit N` (default `None`,
   caps clips per arm for validation runs), `--arms` (default `"A,B,C,D"`, comma-separated subset
   for smoke testing), `--checkpoint` (default `str(paths.FT_CHECKPOINT)`). Logic:

   * Load `paths.FIXED_MANIFEST` (91 rows from Step 3), apply `--limit` if set.
   * Read `paths.PARETO_UNIFIED_JSON`, assert
     `data["selected_cell"] == {"context_score": 3.0, "depth_scaling": 0.5, "alpha": 1.5, "brand_exact_rate": 0.6, "neutral_wer": 0.087}`
     (fail loudly if `t0024`'s file ever changes underneath this task — this task must not silently
     drift from the frontier-selected cell).
   * For each requested arm, load the model once: A/B use
     `nemo.collections.asr.models.ASRModel.from_pretrained("nvidia/parakeet-unified-en-0.6b")`; C/D
     use `nemo.collections.asr.models.ASRModel.restore_from(str(args.checkpoint))` — same call
     `t0021/code/run_finetuned.py` used (confirmed at that file's `restore_from` call site). Set
     `CUDA_VISIBLE_DEVICES=1` in the shell environment before running the script (per REQ-14 — do
     not rely on any default).
   * Apply decoding config: A/C call `boosting.apply_malsd_no_boost(model)`; B/D call
     `boosting.apply_malsd_boost(model, scoring.build_phrase_list(), alpha=1.5, context_score=3.0, depth_scaling=0.5)`.
   * Transcribe with `audio_io.transcribe(model, clips)`, timing each arm's total transcription wall
     time with `time.perf_counter()` around the call and dividing by clip count for
     `efficiency_inference_time_per_item_seconds`.
   * Score each clip: `brand = scoring.brand_in_ref(ref)`; if not `None`,
     `label = scoring.label_brand(hyp, brand)` (else the clip is neutral);
     `w = scoring.wer(ref, hyp)`. Track `successful_requests` (clip transcribed without exception)
     vs `total_requests` (91) per arm for the Rejection Criteria check.
   * Write per-clip records to `results/arm_<a|b|c|d>_predictions.jsonl` — one JSON object per line:
     `{clip_id, ref, hyp, brand (or null), label (EXACT/PHONETIC/GARBAGE/null), wer, latency_seconds, source}`.
   * Aggregate into `results/ablation_metrics.json`: one key per arm (`"A"`, `"B"`, `"C"`, `"D"`),
     each an object with `brand_exact_rate: {overall, rezolve, brainpowa}` (fraction of
     brand-containing clips labeled `EXACT`, computed separately for the `Rezolve`-only and
     `brainpowa`-only subsets), `neutral_wer` (mean `wer` over clips with `brand is None`, 48
     clips), `overall_wer` (mean `wer` over all clips), `avg_inference_time_per_item_seconds`,
     `n_clips`, `n_brand_clips`, `n_neutral_clips`, `successful_requests`, `total_requests`.

   Inputs: `paths.FIXED_MANIFEST`, `paths.FT_CHECKPOINT` (DVC-pulled in Step 8),
   `paths.PARETO_UNIFIED_JSON`. Outputs: `results/arm_{a,b,c,d}_predictions.jsonl`,
   `results/ablation_metrics.json`. Libraries: `nemo.collections.asr.models.ASRModel` (project's
   `stt` conda env, NeMo 3.1.0), `omegaconf` (already used inside `code/boosting.py`), this task's
   own `code/constants.py`, `code/scoring.py`, `code/boosting.py`, `code/audio_io.py`,
   `code/paths.py`. Satisfies REQ-1, REQ-5, REQ-6.

5. **Validation gate 1 — 2-clip smoke test across all 4 arms.** Run
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0026_biasing_on_finetune_ablation -- python -u tasks/t0026_biasing_on_finetune_ablation/code/run_ablation.py --limit 2 --arms A,B,C,D`.
   This is the primary check on arm D (fine-tuned checkpoint + `malsd_batch` boosting via
   `restore_from()`), the one code path no prior task has exercised. **Failure condition**: if the
   script raises an exception for any arm (especially arm D — e.g., an OmegaConf key mismatch
   between `restore_from()`'s config structure and `from_pretrained()`'s), STOP and debug before
   proceeding — read the full traceback, compare `model.cfg.decoding` structure between an
   `A`-arm-loaded model and a `C`-arm-loaded model before and after `change_decoding_strategy()` is
   called, and fix `code/boosting.py` before any further runs. **Baseline check**: for every arm
   that completes, `overall_wer` on this 2-clip run must be below `1.0` (100% WER — i.e., not every
   single word wrong). A `wer >= 0.9` on any arm indicates a broken pipeline (wrong sample rate,
   empty audio, model not loaded) — this is the trivial "completely wrong transcription" ceiling,
   not a real result; STOP and debug rather than proceeding. **Individual-output inspection**: read
   all 8 produced hypotheses (2 clips x 4 arms) from the per-arm `results/arm_*_predictions.jsonl`
   files and manually confirm each hypothesis is a plausible English transcript of its reference
   text (not empty, not gibberish, not a repeated token).

6. **Validation gate 2 — 20-clip validation run across all 4 arms.** Run the same command with
   `--limit 20`. **Failure condition**: same `overall_wer >= 0.9` threshold per arm as Step 5.
   **Individual-output inspection**: read 5 individual predictions per arm (20 total) from
   `results/arm_*_predictions.jsonl` and verify: the audio clip was correctly matched to its
   reference text (via `clip_id`), the hypothesis is reasonable given the reference, and — for clips
   where `brand is not None` — the `label` field (`EXACT`/`PHONETIC`/`GARBAGE`) is scored correctly
   by manually checking whether the exact brand string appears in the hypothesis. Expected output:
   arm B and arm D (biased arms) show visibly higher `brand_exact_rate` than arm A on this 20-clip
   subset, consistent with the historical 60% brand_exact_rate at this cell — if biasing shows zero
   effect on both B and D at this scale, treat it as a possible pipeline bug (boosting tree not
   wired through) before scaling up, per the project's own precedent (`t0022`'s `greedy_batch` bug
   looked exactly like this).

7. **[CRITICAL] Full run — all 91 clips, all 4 arms.** Run
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0026_biasing_on_finetune_ablation -- python -u tasks/t0026_biasing_on_finetune_ablation/code/run_ablation.py --arms A,B,C,D`
   (no `--limit`). Expected output: `results/ablation_metrics.json` has 4 arm entries, each with
   `n_clips: 91`, `n_brand_clips: 43`, `n_neutral_clips: 48`, `total_requests: 91`. Satisfies REQ-1,
   REQ-3, REQ-5, REQ-6.

   Then write `code/mcnemar_test.py`. For the B-vs-D and C-vs-D comparisons, build paired
   correct/incorrect vectors over the 43 brand-containing clips (correct = `label == "EXACT"`),
   matched by `clip_id` across the two arms' `results/arm_*_predictions.jsonl` files. Count
   discordant pairs: `b_count` = clips correct in the first arm but not the second, `c_count` =
   clips correct in the second arm but not the first. Compute the exact McNemar test via
   `scipy.stats.binomtest(min(b_count, c_count), b_count + c_count, p=0.5, alternative="two-sided")`
   — `scipy` is already a project dependency (`pyproject.toml`); do not add `statsmodels`. If
   `b_count + c_count == 0` (no discordant pairs), record `p_value: 1.0` with a note that the test
   is uninformative (both arms agree on every brand clip). Write `results/mcnemar_results.json`:
   `{"b_vs_d": {"b": ..., "c": ..., "n_discordant": ..., "p_value": ...}, "c_vs_d": {...}}`. Run via
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0026_biasing_on_finetune_ablation -- python -u tasks/t0026_biasing_on_finetune_ablation/code/mcnemar_test.py`.
   Satisfies REQ-9.

### Milestone 3: Charts and analysis outputs (can run locally, no GPU needed, after Step 7's outputs exist)

8. **Write `code/make_charts.py`** with three chart functions, saved to `results/images/` as PNG at
   `dpi=150` via `matplotlib` with `matplotlib.use("Agg")` (no display needed):

   * `plot_brand_exact_rate_bar(metrics: dict, out_path: Path) -> None` — adapt `generate_chart_b`
     from `tasks/t0014_granite_short_clip_robustness/code/generate_charts.py` lines 114-171
     (grouped-bar-with-`yerr`-error-bars pattern). Swap its duration-stratum x-axis for 3 buckets
     (`overall`, `Rezolve`, `brainpowa`) and its 2-model bar offset for a 4-arm (`A`/`B`/`C`/`D`)
     offset using `bar_width = 0.2`. No CI error bars are available for this ablation's small
     `brainpowa` bucket (n=3) — omit `yerr` rather than fabricate a confidence interval on 3 points;
     state this omission in a code comment. Save to `results/images/chart1_brand_exact_rate.png`.
     Answers Q1/Q2.
   * `plot_arms_vs_frontier(metrics: dict, frontier: list[dict], out_path: Path) -> None` — adapt
     `plot_pareto_chart` from
     `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py` lines 39-99. Keep the
     frontier-line-overlay logic (lines 61-69 of that file) reading `frontier` from
     `paths.PARETO_UNIFIED_JSON`. Replace the "all cells" gray scatter (lines 51-60 of that file,
     which plotted a 100-cell sweep) with 4 labeled points, one per arm, plotted at
     `(neutral_wer, brand_exact_rate["overall"])`, colored/labeled by arm. Save to
     `results/images/chart2_pareto_scatter.png`. Answers Q4.
   * `plot_bc_confusion_heatmap(predictions_b: list[dict], predictions_c: list[dict], out_path: Path) -> None`
     — new function, no prior-task precedent (research confirmed this). Build a 2x2 count matrix
     over the 43 brand-containing clips: rows = arm B correct/incorrect (`label == "EXACT"`),
     columns = arm C correct/incorrect, matched by `clip_id`. Render with
     `matplotlib.pyplot.imshow`, annotate each cell with its count via `ax.text`, label axes "Arm B"
     / "Arm C", title "Per-clip brand correctness: B vs C (n=43 brand clips)". Save to
     `results/images/chart3_bc_confusion_heatmap.png`. Keep under 50 lines. Answers Q3.

   Run via
   `uv run python -m arf.scripts.utils.run_with_logs --task-id t0026_biasing_on_finetune_ablation -- python -u tasks/t0026_biasing_on_finetune_ablation/code/make_charts.py`.
   Expected output: all three PNG files exist, each > 10,000 bytes. Satisfies REQ-12.

9. **Write `results/clip_level_appendix.json`.** From the full-run per-clip files (Step 7), select
   every brand-containing clip (43 total) where exactly one of B or C is `EXACT` and the other is
   not (the "fixed by exactly one lever" set per `task_description.md`). For each such clip, record
   `{clip_id, ref, hyp_a, hyp_b, hyp_c, hyp_d, label_a, label_b, label_c, label_d}` (all four arms'
   hypotheses and labels, so the mechanism is inspectable). Satisfies REQ-13 (the data source for
   the clip-level appendix table; the orchestrator's own `results` step, not part of this plan's
   implementation work, later renders this JSON into the final results report — per the rule that
   implementation work ends at metric computation and chart generation).

### Milestone 4: Assets

10. **[CRITICAL] Create 4 `predictions` assets**, one per arm, under
    `assets/predictions/<predictions_id>/` following `meta/asset_types/predictions/specification.md`
    (v2, with `description_path` set explicitly): `parakeet-unified-base-nobias-clean-eval-v2`,
    `parakeet-unified-base-bias-clean-eval-v2`, `parakeet-unified-ft-nobias-clean-eval-v2`,
    `parakeet-unified-ft-bias-clean-eval-v2` (arms A/B/C/D respectively — slugs satisfy the
    `^[a-z0-9]+([.\-][a-z0-9]+)*$` naming rule). Each folder gets:

    * `details.json`: `model_id: null` for A/B (`model_description`:
      `"nvidia/parakeet-unified-en-0.6b, HuggingFace pretrained checkpoint, no local model asset"`),
      `model_id: "parakeet-unified-v5"` for C/D (`model_description` citing the DVC checkpoint at
      `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/`);
      `dataset_ids: []` for all four, since `t0021` (the source of `clean_eval_v2`) has no
      registered `dataset` asset — state this explicitly in `description.md`'s `## Data` section and
      cite the raw path `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/` instead;
      `prediction_format: "jsonl"`; `instance_count: 91`; `metrics_at_creation` populated from the
      matching arm's entry in `results/ablation_metrics.json`; `files` pointing at
      `files/predictions-clean-eval-v2.jsonl` (a copy of the arm's `results/arm_*_predictions.jsonl`
      from Step 4/7).
    * `description.md`: all 8 mandatory sections per the specification (`## Metadata`, `## Overview`
      > = 80 words, `## Model`, `## Data`, `## Prediction Format`, `## Metrics`, `## Main Ideas` >=
      > 3 bullets, `## Summary` >= 100 words), written after Step 7's full-run numbers are final.

    Satisfies REQ-11.

11. **[CRITICAL] Create 1 `answer` asset** under `assets/answer/<answer_id>/` (suggested id:
    `biasing-vs-finetuning-complementary-or-redundant`), following
    `meta/asset_types/answer/specification.md` (v2). `question`: "Does GPU-PB context biasing still
    add brand accuracy once parakeet-unified has already been fine-tuned on Rezolve domain audio, or
    do biasing and fine-tuning recover the same errors?" `answer_methods: ["code-experiment"]`.
    `source_task_ids: ["t0021_parakeet_finetune_vs_biasing", "t0022_gpu_pb_diagnostic", "t0023_tdt_vs_unified_biasing", "t0024_biasing_pareto_and_ft_biasing_ablation", "t0024_parakeet_unified_checkpoint_archive"]`.
    `confidence`: `"high"` if the McNemar p-values for both B-vs-D and C-vs-D are decisive (either
    clearly significant or clearly not, at p < 0.05 / p > 0.3 respectively) and the 91-clip
    `successful_requests/total_requests` ratio is >= 0.8 for all 4 arms (see Rejection Criteria);
    otherwise `"medium"`, with the reason stated in `## Limitations`. Write `short_answer.md`
    beginning with "Yes" (complementary), "No" (redundant), or "The evidence is insufficient to
    answer definitively" (if Rejection Criteria trigger or McNemar p-values are ambiguous, e.g. 0.05
    < p < 0.3 for both comparisons) — decided from Step 7's actual numbers, not pre-determined by
    this plan. Write `full_answer.md` with all 8 mandatory sections, addressing Q1-Q5 explicitly
    under `## Synthesis` and the `brainpowa` n=3 power limit under `## Limitations`. Satisfies
    REQ-8, REQ-11.

### Metrics measurement summary (registered project metrics, Phase 1 review)

Every one of the 7 registered project metrics in
`tasks/t0026_biasing_on_finetune_ablation/ctx/metrics.json` was reviewed for applicability:

* `action_critical_wer_gold92`, `entity_accuracy_domain_vocab`, `entity_accuracy_gold92`,
  `intent_preservation_gold92`, `wer_gold92`, `wrong_action_rate_gold92` — all six are defined
  against gold-92 ground truth. This task deliberately does not evaluate on gold-92 (60 of its 93
  clips are inside `train_v5`, the fine-tuning data — any figure would be contaminated). **Not
  applicable; deliberately omitted.**
* `latency_p50_seconds` — defined as end-to-end voice-to-action latency (speech-end detection
  through STT decoding, optional post-correction, and routing to the first tool-call dispatch). This
  task measures single-clip batch inference time only (`efficiency_inference_time_per_item_seconds`,
  a distinct, task-specific measurement written to `results/ablation_metrics.json`, not
  `results/metrics.json`), not the full pipeline `latency_p50_seconds` scope. **Not applicable;
  deliberately omitted.**

`results/metrics.json` is therefore `{}`, matching `t0024`'s precedent for the same reason.
Satisfies REQ-7.

## Remote Machines

**Required.** GPU: `LLM-T1-NC80` (Azure ML compute, workspace `brainpowa-northeurope`, resource
group `rezolve-AI`), 2x H100 NVL, 880 GB RAM — the only VM in `project/azure_vm.json`'s pool. Pin
`CUDA_VISIBLE_DEVICES=1` explicitly in every command run on this box (GPU 1; GPU 0 is reserved for
`t0025_parakeet_tdt_brand_finetune`'s training run) — do not rely on any default device selection.
Use the `stt` conda environment (NeMo 3.1.0) already present on this box; do not create a new
environment. Estimated runtime: ~2 GPU-hours total, including VM start, the mandatory HostName
refresh (Azure reassigns the public IP on every start — see `docs/northeurope_pool_runbook.md` Step
3), `dvc pull` of the checkpoint (2.47 GB) and audio (11.5 MB), `stt` env verification, and the
actual inference (well under 1 hour of GPU time for 4 arms x 91 clips on a 0.6B model).

**Coordination requirement**: `LLM-T1-NC80` carries `requires_coordination_if_running: true` in
`project/azure_vm.json` — humans (finetuning team members) SSH in directly without taking an ARF
lock, so `acquire()` refuses this VM if it is found already `Running` rather than assuming it is
free, and this is the only entry in the pool (no fallback). Per `task_description.md`'s explicit
instruction: **run this task's GPU work before `t0025_parakeet_tdt_brand_finetune`, and do not
expect the two to run concurrently under the current tooling.** `t0025`'s `task.json` currently
shows `status: "not_started"` with no `checkpoint.md` yet, confirming it has not started GPU work —
there is no live conflict today, but this task's `setup-machines` step must acquire, this task's
`teardown` step must fully release/deallocate the VM, and only then should `t0025`'s
`setup-machines` step attempt to acquire. `t0025`'s CPU-only prerequisite work (building
`val_v6.jsonl`) can proceed in parallel with this task holding the GPU. Never write durable output
to `/mnt` on this box (it is ephemeral local disk, wiped on every stop/start — this is how the
original `t0021` checkpoint copy was lost); `dvc pull` the checkpoint into
`tasks/t0026_biasing_on_finetune_ablation/`'s own space (it is already DVC-tracked under
`t0024_parakeet_unified_checkpoint_archive`'s asset folder, so `dvc pull` resolves it there — no
need to copy it elsewhere), and `dvc push` any new artifacts worth keeping (the per-arm predictions
JSONL files, if large) before teardown.

## Assets Needed

* **Model asset** `parakeet-unified-v5` from `t0024_parakeet_unified_checkpoint_archive` (dependency
  task) — DVC-tracked `.nemo` checkpoint at
  `tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo`.
  Hard dependency for arms C and D; `dvc pull` before Step 4.
* **Data** `clean_eval_v2` (91-clip manifest + DVC-tracked audio) from
  `tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/` (dependency task, not a registered
  `dataset` asset — see Step 10's note). `dvc pull` the `audio.dvc` pointer in that directory before
  Step 3.
* **Data** `pareto_unified.json` from
  `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json` (dependency task)
  — read directly as a cross-task data file (not a code import — only `code/` imports are
  restricted), for the selected biasing cell and the frontier array.
* **Code (copied, not imported)** from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` (not a
  `task.json` dependency — its legacy pre-`spec_version` schema is invisible to the dependency
  checker per `S-0024-06`; read directly) and
  `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` (dependency task) — see Step 2 for
  exact line ranges.
* **External model**: `nvidia/parakeet-unified-en-0.6b` from HuggingFace, pulled fresh via
  `ASRModel.from_pretrained()` on the GPU machine (already cached in the `stt` env's HF cache on
  `LLM-T1-NC80` per `project/azure_vm.json`'s notes — no download expected, but not guaranteed).

## Expected Assets

* `predictions` (4x): `parakeet-unified-base-nobias-clean-eval-v2`,
  `parakeet-unified-base-bias-clean-eval-v2`, `parakeet-unified-ft-nobias-clean-eval-v2`,
  `parakeet-unified-ft-bias-clean-eval-v2` — per-clip transcription output for arms A/B/C/D
  respectively on the 91-clip `clean_eval_v2` holdout, matching `task.json`
  `expected_assets.predictions: 4`.
* `answer` (1x): `biasing-vs-finetuning-complementary-or-redundant` — the complementary-vs-redundant
  verdict and production recommendation for `t0025`, matching `task.json`
  `expected_assets.answer: 1`.

## Time Estimation

* Research (already done, prior steps): 0h (this plan resumes at implementation).
* Milestone 1 (manifest fix + code scaffolding, local, no GPU): ~45 min.
* `setup-machines` step (VM acquire, HostName refresh, `dvc pull` checkpoint + audio, `stt` env
  verify): ~30-45 min (orchestrator-managed step, not part of this plan's Step by Step, but counted
  in overall task wall clock).
* Milestone 2 (ablation script, smoke test, 20-clip validation, full 91-clip run, McNemar test): ~90
  min, dominated by model load time (2 models x 2 decoding configs = up to 4 model loads) and the
  full 4-arm x 91-clip transcription pass.
* Milestone 3 (charts, clip-level appendix): ~25 min, local, no GPU needed once Step 7's JSONL/JSON
  outputs exist (can run on the GPU box or downloaded locally).
* Milestone 4 (predictions + answer assets, description documents): ~30 min.
* `teardown` step: ~10 min (orchestrator-managed).
* **Total estimated wall clock: ~3.5-4 hours**, of which ~1.5-2 hours is GPU-billed time (matching
  the ~2 GPU-hour, ~$28 cost estimate).

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Arm D (`restore_from()` + `apply_malsd_boost` `malsd_batch` decoding-strategy change) is an untested code combination and may raise an exception (e.g., the restored checkpoint's `model.cfg.decoding` structure differs from the `from_pretrained` model's, breaking the `OmegaConf` key paths `apply_malsd_boost` assumes) | Medium | High — arm D is this task's single novel, CRITICAL contribution; without it the ablation cannot answer Q1/Q2 | Validation gate 1 (Step 5) smoke-tests exactly this combination with `--limit 2` before any full-scale run. If it fails after debugging (structural incompatibility, not a typo), this is a CRITICAL step blocker: write `intervention/arm_d_blocked.md` describing the exact failure, rather than silently dropping arm D or substituting a different decoding call for arm D only (which would break REQ-2's requirement that all arms use the identical `malsd_batch` boosting mechanism). |
| `LLM-T1-NC80` is found already `Running` when `setup-machines` attempts `acquire()` (a human finetuning-team member, or a stray un-torn-down session) | Medium — this is shared, non-dedicated compute per `project/azure_vm.json`'s notes | Medium — blocks all GPU work until resolved, but is recoverable, not data-destructive | `acquire()` writes `pool_busy.md` and stops rather than silently claiming the box; check `#finetuning` Slack (or ask directly) per `docs/northeurope_pool_runbook.md` before retrying `setup-machines`. Do not force-start or bypass the coordination check. |
| The manifest-fix script (Step 3) silently mis-resolves paths — e.g., a filename collision or a clip present in the manifest but missing from the DVC-pulled `audio/` directory | Low-Medium | High — garbage or missing predictions for affected clips, undetected if not checked | Step 3's own assertion (`len(rows) == 91` and every `audio_filepath.exists()`) fails loudly before any inference starts; this is a pre-inference gate, not a post-hoc discovery. |
| `dvc pull` of the 2.47 GB fine-tuned checkpoint fails or times out on the GPU box (network flakiness, DVC remote misconfiguration) | Low-Medium | Medium — delays arms C/D, though arms A/B could still complete | Verify `dvc status`/`dvc pull` succeeds and the pulled file's md5 matches `parakeet-unified-finetuned-best.nemo.dvc` before Step 4 begins; retry with backoff; this is the exact failure mode that blocked the original `t0024` Part B, so treat any DVC pull failure as a known, expected risk to check for explicitly rather than assume success. |
| GPU cost overrun from an un-torn-down or idle-left VM session | Low — $28 estimate is far under the $100 per-task limit, and `H100` billing is per-hour not per-idle-minute at a rate that would blow the budget quickly | Low-Medium — wasted budget, not task failure | `teardown` step (orchestrator-managed, step 10 in `step_tracker.json`) runs immediately after Step 9's outputs are downloaded/`dvc push`ed; do not leave the session running between Milestone 2 and Milestone 3/4 work (Milestones 3-4 do not need the GPU). |
| Only 3 `brainpowa` clips exist in `clean_eval_v2`, making any `brainpowa`-specific claim (aggregate or McNemar) statistically meaningless | High (pre-registered, known in advance) | Low-Medium if handled correctly, High if misreported as a confident finding | Report `brainpowa` counts descriptively only (Step 4's `brand_exact_rate.brainpowa` field, Step 8's chart with no fabricated error bars); do not run a `brainpowa`-only McNemar test (Step 7 only computes McNemar over all 43 brand clips); state the n=3 power limit explicitly in the answer asset's `## Limitations` section (Step 11) and in the Rejection Criteria below. |

## Verification Criteria

* Run `uv run python -u -m arf.scripts.verificators.verify_plan t0026_biasing_on_finetune_ablation`
  — expect **zero errors** (this plan document itself).
* Run
  `python3 -c "import json; d=json.load(open('tasks/t0026_biasing_on_finetune_ablation/results/ablation_metrics.json')); assert set(d.keys())=={'A','B','C','D'}; assert all(d[a]['n_clips']==91 and d[a]['n_brand_clips']==43 and d[a]['n_neutral_clips']==48 for a in d)"`
  — expect no `AssertionError` (all 4 arms present, correct clip counts, confirming REQ-1 and
  REQ-5).
* Run
  `wc -l tasks/t0026_biasing_on_finetune_ablation/results/arm_a_predictions.jsonl tasks/t0026_biasing_on_finetune_ablation/results/arm_b_predictions.jsonl tasks/t0026_biasing_on_finetune_ablation/results/arm_c_predictions.jsonl tasks/t0026_biasing_on_finetune_ablation/results/arm_d_predictions.jsonl`
  — expect exactly `91` for each file.
* Run
  `uv run python -m meta.asset_types.predictions.verificator parakeet-unified-base-nobias-clean-eval-v2 --task-id t0026_biasing_on_finetune_ablation`
  (and the same command for the other 3 predictions IDs from Step 10) — expect exit code 0, all
  checks passed, confirming REQ-11's predictions half.
* Run
  `uv run python -m meta.asset_types.answer.verificator biasing-vs-finetuning-complementary-or-redundant --task-id t0026_biasing_on_finetune_ablation`
  — expect exit code 0, all checks passed, confirming REQ-8 and REQ-11's answer half.
* Run
  `uv run python -u -m arf.scripts.verificators.verify_task_metrics t0026_biasing_on_finetune_ablation`
  — expect zero errors, and manually confirm `results/metrics.json` content is exactly `{}` (REQ-7).
* Run
  `ls -la tasks/t0026_biasing_on_finetune_ablation/results/images/chart1_brand_exact_rate.png tasks/t0026_biasing_on_finetune_ablation/results/images/chart2_pareto_scatter.png tasks/t0026_biasing_on_finetune_ablation/results/images/chart3_bc_confusion_heatmap.png`
  — expect all three files to exist with size greater than 10,000 bytes each (REQ-12).
* Run
  `python3 -c "import json; d=json.load(open('tasks/t0026_biasing_on_finetune_ablation/results/mcnemar_results.json')); assert 'b_vs_d' in d and 'c_vs_d' in d and 'p_value' in d['b_vs_d'] and 'p_value' in d['c_vs_d']"`
  — expect no `AssertionError` (REQ-9).
* Run
  `uv run ruff check tasks/t0026_biasing_on_finetune_ablation/code/ && uv run ruff format --check tasks/t0026_biasing_on_finetune_ablation/code/`
  — expect 0 issues.
* Run `uv run mypy tasks/t0026_biasing_on_finetune_ablation/code/` — expect 0 errors.
* Run
  `python3 -c "import re, pathlib; txt = pathlib.Path('tasks/t0026_biasing_on_finetune_ablation/plan/plan.md').read_text(); reqs = sorted(set(re.findall(r'REQ-\d+', txt))); print(reqs); assert len(reqs) == 15 and all(txt.count(r) >= 2 for r in reqs)"`
  — expect all 15 `REQ-*` IDs printed and each appearing at least twice (once in the checklist, once
  in a step or section that satisfies it) — confirms full requirement-coverage traceability.

## Rejection Criteria

Pre-registered before running, per `LESSONS.md` Lesson 3 ("Pre-register a failure-rate rejection
threshold before running"), so these conditions cannot be retroactively loosened once results are
known:

* **Default failure-rate rule**: for any arm, if `successful_requests / total_requests < 0.8` (i.e.,
  fewer than 80% of the 91 clips transcribe without exception), that arm's condition is declared
  **null** and excluded from the answer's `brand_exact_rate`/`neutral_wer`/McNemar comparisons,
  regardless of any measured numbers on the successfully-transcribed subset. Report the failure rate
  and the reason (if known) in `## Limitations` rather than silently dropping the arm from the
  report.
* **Manifest integrity gate**: if the manifest-fix assertion in Step 3 (`len(rows) == 91` and every
  `audio_filepath` resolves to an existing file) fails and is not fixed before Step 4 begins, the
  entire ablation is null — do not compute or report metrics against a manifest with unresolved or
  missing audio paths, even for a subset of arms.
* **`brainpowa` statistical-claim exclusion**: with only 3 `brainpowa` clips (a pre-registered,
  known-in-advance power limit stated in `task_description.md`), no McNemar test or confidence
  interval is computed for the `brainpowa` subset specifically (Step 7 computes McNemar only over
  all 43 brand clips combined). Any `brainpowa`-specific number reported is descriptive only (raw
  counts, e.g. "1 of 3 correct"), never presented as a statistically tested finding.
* **GPU-coordination blocker**: if `LLM-T1-NC80` cannot be acquired within a reasonable number of
  coordinated retries (per the Risks & Fallbacks row above) because it remains `Running` under
  someone else's use, this is a **blocked-task escalation**, not a null result — write an
  intervention file rather than substituting CPU-only inference (NeMo `malsd_batch` beam decoding on
  CPU for a 0.6B model across 4 arms x 91 clips would be far slower and is not validated by any
  prior task in this project) or synthetic/cached data.

## Additional Sections

### Architecture

```text
tasks/t0021_.../data/clean_eval_v2/manifest.jsonl (absolute macOS paths)
        │  Step 3: code/fix_manifest.py
        ▼
tasks/t0026_.../data/clean_eval_v2_manifest_fixed.jsonl (gitignored, repo-relative)
        │
        ▼
Step 4-7: code/run_ablation.py  ──uses──▶ code/constants.py, code/scoring.py,
        │         │                       code/boosting.py, code/audio_io.py
        │         │
        │         ├─ Arm A: from_pretrained(unified) + apply_malsd_no_boost
        │         ├─ Arm B: from_pretrained(unified) + apply_malsd_boost(cell)
        │         ├─ Arm C: restore_from(parakeet-unified-v5) + apply_malsd_no_boost
        │         └─ Arm D: restore_from(parakeet-unified-v5) + apply_malsd_boost(cell)
        │
        ▼
results/arm_{a,b,c,d}_predictions.jsonl, results/ablation_metrics.json
        │
        ├─ Step 7: code/mcnemar_test.py ──▶ results/mcnemar_results.json
        ├─ Step 8: code/make_charts.py ──▶ results/images/chart{1,2,3}.png
        ├─ Step 9: results/clip_level_appendix.json
        │
        ▼
Step 10: assets/predictions/<4 ids>/     Step 11: assets/answer/<id>/
```

### Dependencies on Other Tasks

* `t0024_parakeet_unified_checkpoint_archive` (hard dependency, `task.json` `status` field is a
  known false negative — verified merged to `main` in `checkpoint.md` step 2, commit `e755ef4`):
  supplies the `parakeet-unified-v5` checkpoint arms C/D require.
* `t0021_parakeet_finetune_vs_biasing` (dependency): supplies `clean_eval_v2`'s manifest and audio,
  and `DOMAIN_VOCAB`.
* `t0024_biasing_pareto_and_ft_biasing_ablation` (dependency): supplies the frontier-selected
  biasing cell this task holds fixed, and is the task whose Part B this completes.
* `t0023_tdt_vs_unified_biasing` (not a `task.json` dependency — legacy pre-`spec_version` schema
  invisible to the dependency checker per `S-0024-06`): source of the `apply_malsd_boost`/scoring
  code copied in Step 2.
