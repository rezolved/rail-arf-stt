---
spec_version: "2"
task_id: "t0019_parakeet_biasing_improvement"
date_completed: "2026-07-02"
status: "complete"
---

## Objective

Improve NeMo GPU-PB TurboBias biasing quality for `parakeet-unified-en-0.6b` (the winner of
`t0017_parakeet_biasing_buffer_replacement`) on the gold-92 benchmark, beyond the current
biased-baseline `entity_accuracy_domain_vocab` (EA-DV) of 34.8%, without regressing full-transcript
WER or latency beyond the 800ms voice-to-action budget. Done means: three prediction sets exist
(baseline reproduction, best hyperparameter config, best hyperparameter + expanded phrase list),
each scored with the project's registered metrics, and one answer asset states which
biasing-improvement approach (if any) beats the t0017 baseline and by how much, with a
recommendation on whether to ship it to `brainpowa-realtime-api` production.

## Task Requirement Checklist

Verbatim from `task.json` / `task_description.md`:

> **short_description**: Improve GPU-PB biasing quality for parakeet-unified-en-0.6b: hyperparam
> sweep (alpha/context_score/depth_scaling), phonetic/misspelling phrase-list expansion, post-hoc
> stt_replacements fallback for known misses.
>
> **Approaches to test (ranked by expected ROI)**:
> 1. Boosting hyperparam sweep — grid over alpha (1.0-3.0), context_score, depth_scaling on gold-92,
>    biased. Measure EA-DV vs WER (hallucination risk) trade-off.
> 2. Phrase-list expansion with phonetic/misspelling variants — add explicit near-miss forms
>    (e.g. "Resolve", "Rizol" → "Rezolve") to the boosting phrase list, not just casing.
> 3. Post-hoc `stt_replacements` fallback — deterministic post-decode string replacement for terms
>    biasing can't reliably fix.
>
> Deprioritized: per-phrase weighting, beam rescoring, fine-tuning.
>
> **Expected Assets**: 3 prediction sets (baseline, best hyperparam config, best hyperparam +
> phrase expansion); 1 answer/results doc comparing EA, EA-DV, WER, latency vs t0017 biased baseline.

Requirement decomposition:

* **REQ-1**: Reproduce the t0017 biased baseline for `parakeet-unified-en-0.6b` on gold-92 (default
  `alpha=1.0, context_score=1.0, depth_scaling=2.0`, casing-only phrase variants) as the control
  condition. Satisfied by Step 1. Evidence: `assets/predictions/parakeet-unified-baseline-biased/`.
* **REQ-2**: Sweep GPU-PB hyperparameters (`alpha` ∈ {1.0, 1.5, 2.0, 2.5, 3.0}, `depth_scaling` ∈
  {2.0, 3.0, 4.0}, `context_score` held at 1.0 unless alpha sweep shows saturation) on gold-92 and
  identify the config with the best EA-DV without a WER regression >1 absolute point vs baseline.
  Satisfied by Step 2. Evidence: `results/hyperparam_sweep.jsonl`, `results/metrics.json` variant
  `hyperparam-sweep`.
* **REQ-3**: Expand the phrase list with phonetic/misspelling variants for terms with observed
  failures (at minimum "Rezolve" → "Resolve", "Rizol", "Re-zolve"; "brainpowa" → "brain power",
  "brain powa") and re-run gold-92 with the best hyperparameter config from REQ-2. Satisfied by
  Step 3. Evidence: `assets/predictions/parakeet-unified-best-config-phrase-expansion/`.
* **REQ-4**: Evaluate the `stt_replacements` post-hoc fallback approach as a bounded feasibility
  check (not a full production integration) — apply a deterministic string-replacement pass to the
  Step 3 predictions for the same hard-miss terms and measure the EA-DV uplift it could add on top
  of biasing. Satisfied by Step 4. Evidence: `results/posthoc_replacement_check.json`.
* **REQ-5**: Produce 3 predictions assets total (REQ-1 baseline, REQ-2 best-hyperparam run, REQ-3
  best-hyperparam+phrase-expansion run) per `task.json` `expected_assets.predictions: 3`. Satisfied
  by Steps 1, 2, 3.
* **REQ-6**: Produce metrics (WER, EA, EA-DV, latency p50) for all three conditions plus the REQ-4
  feasibility check, compared against the t0017 biased baseline as deltas. Satisfied by Step 5.
* **REQ-7**: Produce 1 answer asset stating which approach(es) improved biasing quality, by how
  much, and a ship/no-ship recommendation for production `brainpowa-realtime-api`. Satisfied by
  Step 6, per `task.json` `expected_assets.answer: 1`.
* **REQ-8**: Explicitly deprioritize per-phrase weighting, beam rescoring, and fine-tuning — do not
  implement them in this task; note them as future work in the answer asset (Step 6).

Ambiguity handling: the task text does not give an exact hyperparameter grid resolution. This plan
fixes a specific grid (5 alpha values × 3 depth_scaling values = up to 15 runs, pruned adaptively,
see Step 2) as a concrete, boundable interpretation of "hyperparam sweep."

## Approach

**Grounding in prior findings (t0017, no new research step run for this task — task was scoped
directly from t0017's dependency results per orchestrator instruction to skip unneeded stages):**
t0017 (`tasks/t0017_parakeet_biasing_buffer_replacement/results/results_summary.md`) established
that `parakeet-unified-en-0.6b`, biased with NeMo GPU-PB TurboBias at default hyperparameters
(`alpha=1.0`, `context_score=1.0`, `depth_scaling=2.0`, `use_bpe_dropout=True`), scores WER 11.0%,
EA 23.4%, EA-DV 34.8% on gold-92, and still mis-transcribes "Rezolve" as "Resolve"/"Rizol". The
31-term Rezolve domain vocabulary and casing-expansion logic live in
`tasks/t0017_parakeet_biasing_buffer_replacement/code/constants.py` (`DOMAIN_VOCAB`) and
`code/run_parakeet_buffer_sweep.py` (`expand_casing_variants`, `apply_boosting`). The boosting
config is applied via `OmegaConf.update` on `model.cfg.decoding.greedy.boosting_tree.*` before
`model.change_decoding_strategy(cfg)` — this is the exact mechanism this task's Step 2 hyperparameter
sweep will vary.

**Approach for this task**: reuse the t0017 harness wholesale (copy `code/` into `t0019/code/`,
repoint imports) and add three new entry points on top of it:

1. A baseline reproduction run (unified model only, default hyperparameters, casing-only phrases)
   to establish this task's own control condition (do not simply cite t0017's numbers — the harness
   changed slightly after t0017 due to a casing-variant bug fix, so REQ-1 reproduces fresh to keep
   comparisons apples-to-apples within this task).
2. A hyperparameter grid sweep over `alpha` and `depth_scaling` (REQ-2), reusing `apply_boosting`
   with different constant values per run instead of the fixed t0017 constants.
3. A phrase-list expansion (REQ-3) that adds phonetic/misspelling variants to `DOMAIN_VOCAB` for the
   worst-performing terms, re-run with the winning hyperparameter config from step 2.
4. A cheap post-hoc string-replacement feasibility check (REQ-4) — not a new model run, just a
   regex/string substitution pass over the Step 3 transcripts for known hard misses, to see whether
   it adds accuracy without needing further model changes.

**Alternatives considered and rejected** (per task_description.md "Deprioritized" list and this
plan's own judgment):
* *Per-phrase weighting* — NeMo GPU-PB `context_score` is applied globally per model call in the
  current harness; per-phrase weights would need a config format NeMo's boosting tree does not
  expose through the simple `key_phrases_list` interface used here (it takes a flat phrase list, not
  a phrase→weight map in this NeMo version). Rejected for this task: higher implementation risk,
  uncertain API support, no prior validation. Left as future work in the answer asset.
* *Beam rescoring* — would require switching `cfg.strategy` from `greedy_batch` to a beam strategy,
  which t0017's research flagged as untested with GPU-PB on this model version and adds decode-time
  cost. Rejected: out of scope, higher risk, not requested as a priority approach.
* *Fine-tuning* — explicitly deprioritized in the task text as the most expensive, least-proven-ROI
  option. Rejected: no GPU fine-tuning budget allocated in this plan's Cost Estimation.

**Recommended task types**: `task.json` already declares `stt-benchmark-run` and `experiment-run`.
Both apply. From `meta/task_types/stt-benchmark-run/instruction.md`: transcribe all 93 gold-92 clips
per condition (never subsample), compute the six registered project metrics, save per-clip
predictions to JSONL tracked for reuse, run a warm-up before timing latency. From
`meta/task_types/experiment-run/instruction.md`: this is a multi-condition comparison (baseline vs
hyperparameter configs vs phrase expansion), so `results/metrics.json` must use the **explicit
multi-variant format** (one variant per condition), fixed seeds are not applicable (Parakeet
`greedy_batch` decoding is deterministic, no sampling), and per-instance predictions must be saved
as `predictions` assets. Charts: at least 2 (EA-DV vs alpha/depth_scaling heatmap or line chart;
grouped bar chart comparing WER/EA/EA-DV/latency across the 4 conditions: t0017 baseline reproduced,
best hyperparam, best hyperparam+phrase expansion, +post-hoc replacement).

## Cost Estimation

**$0 in external API/cloud spend.** All inference runs on the existing reserved GPU server
(`ssh gpu-azure`, 2×H100 NVL, already running per `t0017-progress` memory note — no new machine
provisioning cost). Both `nvidia/parakeet-unified-en-0.6b` weights are already cached in HF cache on
that machine from t0017. No paid API calls (no LLM judge, no Deepgram calls) are part of this task —
all metrics (WER, EA, EA-DV, latency) are computed locally with `jiwer` and regex matching, reusing
t0017's `compute_and_write_metrics.py` logic. Total estimated compute time is well under the
project's `per_task_default_limit: $100.0` from `project/budget.json` (the limit is a token/agent
time budget proxy, not GPU rental cost, since the machine is a standing reserved resource — no
incremental $ cost is incurred by running more inference passes on it). Project `total_budget` is
$2000.0; this task consumes $0 of that pool.

## Step by Step

**Milestone A — Setup and baseline reproduction**

1. **[CRITICAL] Copy and adapt the t0017 harness.** Copy
   `tasks/t0017_parakeet_biasing_buffer_replacement/code/constants.py`,
   `code/paths.py`, `code/hallucination_detector.py`, `code/run_parakeet_buffer_sweep.py`, and
   `code/compute_and_write_metrics.py` into `tasks/t0019_parakeet_biasing_improvement/code/`.
   Update all `tasks.t0017_parakeet_biasing_buffer_replacement.code.*` import paths to
   `tasks.t0019_parakeet_biasing_improvement.code.*`. In the new `code/paths.py`, keep
   `GOLD92_AUDIO_DIR`/`GOLD92_GROUND_TRUTH` pointing at `t0001_stt_benchmark` (relative path via
   `TASK_DIR.parent`, unchanged pattern) and `BOH_PATTERNS_CSV` pointing at
   `t0014_granite_short_clip_robustness` (unchanged). Drop the TDT model dict entries and buffer
   interval sweep logic (`BUFFER_INTERVALS_MS`, `INTERVAL_BYTES`) from `constants.py` — this task
   fixes the buffer at the t0017-recommended production interval (1000ms / 32000 bytes, single
   interval, not a sweep) since buffer tuning is out of scope here. Satisfies REQ-1 setup.
   Expected output: `code/` directory with 5 files, no `t0017` string remaining in any import line
   (verify with `grep -rn t0017_parakeet_biasing_buffer_replacement code/`, expect zero matches).

2. **[CRITICAL] Write `code/run_baseline.py`.** New script, single entry point, no CLI model choice
   (unified only). Reuses `expand_casing_variants`, `apply_boosting`, `load_audio_float32`,
   `transcribe_buffer`, `load_gold92_clips` copied/adapted from Step 1's
   `run_parakeet_buffer_sweep.py` (single-buffer, non-streaming variant: transcribe the full clip in
   one `model.transcribe()` call at 1000ms-equivalent single-shot, since buffer-interval TTFD
   behavior is out of scope — only final transcript quality and single-shot latency matter here).
   Apply `apply_boosting` with the unchanged defaults from `constants.py`
   (`PARAKEET_BOOSTING_ALPHA=1.0`, `PARAKEET_CONTEXT_SCORE=1.0`, `PARAKEET_DEPTH_SCALING=2.0`) and
   `expand_casing_variants(DOMAIN_VOCAB)` phrases (66 variants, matching t0017's fixed
   casing-expansion logic — confirm `expand_casing_variants` uses `phrase.title()` for the
   capitalized variant, not `phrase[:1].upper() + phrase[1:]`; the latter was a known bug fixed in
   t0017 on 2026-07-02, re-verify it is not reintroduced when copying). Run on all 93 gold-92 clips
   first with `--limit 10` to validate: expected EA-DV in the 25-45% range (t0017 baseline was
   34.8%); if result is 0% or the harness crashes, stop and inspect 5 individual predictions before
   the full run. Then run full 93 clips. Write predictions JSONL to
   `data/baseline/predictions.jsonl`. Satisfies REQ-1.
   Expected output: `data/baseline/predictions.jsonl` with 93 lines (or ≥80% success rate per
   `MIN_SUCCESS_RATE=0.80`, else raise `RuntimeError` per t0017's rejection pattern).

**Milestone B — Hyperparameter sweep**

3. **Write `code/run_hyperparam_sweep.py`.** Grid: `alpha` ∈ [1.0, 1.5, 2.0, 2.5, 3.0],
   `depth_scaling` ∈ [2.0, 3.0, 4.0], `context_score` fixed at 1.0 (15 combinations). To bound GPU
   time, run the full 15-combination grid on a **fixed subsample of 20 clips** (deterministic:
   first 20 clips by `clip_id` sort order from `load_gold92_clips`) to find the top-2 candidate
   configs by EA-DV, then re-run only those top-2 configs on the full 93 clips to select the single
   winner. State this subsampling explicitly in the script's logged output and in
   `results/hyperparam_sweep.jsonl` metadata (per the
   `stt-benchmark-run` instruction's "never subsample unless the task plan explicitly approves it" —
   this plan explicitly approves subsampling for the screening phase only; the final reported numbers
   for the winning config always come from the full 93-clip run). For each of the 15
   screening configs, call `apply_boosting` with that config's `alpha`/`depth_scaling`, transcribe
   the 20-clip subsample, compute EA-DV inline (reuse normalisation/entity-matching logic from
   `code/compute_and_write_metrics.py`). Write `results/hyperparam_sweep.jsonl` (one row per config:
   `alpha`, `depth_scaling`, `context_score`, `ea_dv_20clip`, `wer_20clip`). [CRITICAL] Then run the
   top-2 configs by 20-clip EA-DV on the full 93 clips, write predictions to
   `data/hyperparam_top2/{config_slug}/predictions.jsonl`. Select the winner: highest full-93 EA-DV
   among the top-2, with a WER regression cap — the winner must not exceed baseline WER (from Step
   2) by more than 1.0 absolute percentage point; if both top-2 candidates violate the cap, fall
   back to the baseline config as the "winner" and note this explicitly in the answer asset (Step
   6) as a null result for the hyperparameter-sweep approach. Copy the winning full-93 predictions
   file to `data/best_hyperparam/predictions.jsonl`. Satisfies REQ-2.
   Expected output: `results/hyperparam_sweep.jsonl` (15 rows), `data/hyperparam_top2/` (2
   subfolders), `data/best_hyperparam/predictions.jsonl` (93 lines).

**Milestone C — Phrase-list expansion**

4. **Write `code/phrase_expansion.py` and re-run with best config.** Define
   `EXPANDED_DOMAIN_VOCAB_VARIANTS: dict[str, list[str]]` mapping each `DOMAIN_VOCAB` term that
   appears as a wrong-entity in Step 2/3 baseline predictions to a list of phonetic/misspelling
   near-miss forms. Minimum required entries (from t0017's observed failures): `"Rezolve"` →
   `["Resolve", "Rizol", "Re-zolve", "Rezolv"]`, `"Rezolve Ai"` → `["Resolve AI", "Rizol AI"]`,
   `"brainpowa"` → `["brain power", "brain powa", "Brain Powa"]`. Before finalizing this list,
   inspect the Step 2 baseline `data/baseline/predictions.jsonl` transcripts for the other 28
   domain-vocab terms and add any additional observed near-miss forms found by grepping predicted
   transcripts around each term's expected position in the reference text. Extend
   `expand_casing_variants` output with these additional literal strings (dedup against existing
   variants) before calling `apply_boosting`. Re-run the full 93 clips using the winning
   hyperparameter config from Step 3 plus this expanded phrase list. Write predictions to
   `data/best_hyperparam_phrase_expansion/predictions.jsonl`. Satisfies REQ-3.
   Expected output: `data/best_hyperparam_phrase_expansion/predictions.jsonl` (93 lines), and the
   expanded phrase list documented as a Python literal in `code/phrase_expansion.py` for
   reproducibility.

**Milestone D — Post-hoc replacement feasibility check**

5. **Write `code/posthoc_replacement_check.py`.** Not a model run — a pure post-processing pass.
   For each of the near-miss forms defined in Step 4's `EXPANDED_DOMAIN_VOCAB_VARIANTS`, apply a
   case-insensitive whole-word string replacement (near-miss → canonical term) to the Step 4
   transcripts (`data/best_hyperparam_phrase_expansion/predictions.jsonl`), producing a hypothetical
   "biasing + post-hoc" transcript set in memory (do not overwrite Step 4's file — write to
   `data/posthoc_check/predictions.jsonl`). Recompute EA-DV and WER on this post-hoc set and compare
   against Step 4's un-replaced numbers. This estimates the theoretical ceiling of the
   `stt_replacements` approach without wiring it into the actual `brainpowa-realtime-api` service
   (out of scope for this research task — REQ-4 asks for a feasibility measurement only). Write
   `results/posthoc_replacement_check.json` with keys `ea_dv_before`, `ea_dv_after`, `wer_before`,
   `wer_after`, `n_replacements_applied`. Satisfies REQ-4.
   Expected output: `results/posthoc_replacement_check.json` with `ea_dv_after >= ea_dv_before` (a
   replacement pass should never hurt EA-DV since it is targeted at known-wrong terms only; if it
   does regress, inspect for over-matching false positives before reporting).

**Milestone E — Metrics, charts, and assets**

6. **Compute metrics for all conditions.** Adapt `code/compute_and_write_metrics.py` to score four
   conditions: `baseline` (Step 2), `best-hyperparam` (Step 3), `best-hyperparam-phrase-expansion`
   (Step 4), and `posthoc-check` (Step 5, informational only, not a separate predictions asset).
   For each, compute `wer_gold92`, `entity_accuracy_gold92`, `entity_accuracy_domain_vocab`, and
   `latency_p50_seconds` (measure wall-clock per-clip transcription time in Steps 2/3/4, warm up
   with 3 throwaway clips first per the `stt-benchmark-run` Common Pitfalls guidance).
   `intent_preservation_gold92`, `action_critical_wer_gold92`, and `wrong_action_rate_gold92`
   require the downstream intent classifier / routing policy from `brainpowa-realtime-api`, which
   this task does not invoke — omit these three metrics explicitly and note in code comments /
   script output that they require the full routing pipeline, out of scope for a biasing-only
   experiment. Write `results/metrics.json` using the **explicit multi-variant format**
   (one variant object per condition: `baseline`, `best-hyperparam`, `best-hyperparam-phrase-
   expansion`) per `arf/specifications/metrics_specification.md`. Generate at least 2 charts with
   matplotlib, saved to `results/images/`: (a) `hyperparam_sweep_heatmap.png` — EA-DV (20-clip
   screening) as a heatmap over the alpha × depth_scaling grid from Step 3; (b)
   `condition_comparison.png` — grouped bar chart of WER/EA/EA-DV across the 4 conditions
   (t0017-reported baseline for reference + this task's 3 conditions). Satisfies REQ-6.
   Expected output: `results/metrics.json` (multi-variant), 2 PNG files in `results/images/`.

7. **Create predictions assets.** Create three `assets/predictions/<id>/` folders per
   `meta/asset_types/predictions/specification.md`: `parakeet-unified-biasing-baseline` (Step 2
   output), `parakeet-unified-biasing-best-hyperparam` (Step 3 output),
   `parakeet-unified-biasing-best-hyperparam-phrase-expansion` (Step 4 output). Each folder gets
   `details.json`, `description.md`, and `files/predictions.jsonl` (copy from the corresponding
   `data/` path). Satisfies REQ-5.
   Expected output: 3 folders under `assets/predictions/`, each with the 3 required files present.

8. **Create the answer asset.** Create `assets/answer/parakeet-unified-biasing-improvement/` per
   `meta/asset_types/answer/specification.md` with `details.json`, `short_answer.md`,
   `full_answer.md`. `short_answer.md` states: which of the 3 tested approaches (hyperparameter
   tuning, phrase expansion, post-hoc replacement) produced the largest EA-DV improvement over the
   34.8% t0017 baseline (or this task's freshly reproduced baseline from Step 2 if it differs), the
   exact delta, and a ship/no-ship call for `brainpowa-realtime-api` production. `full_answer.md`
   includes the full comparison table (4 conditions × 4 metrics), the hyperparameter sweep heatmap
   embedded via `![description](../../../results/images/hyperparam_sweep_heatmap.png)`-style
   relative reference or a copy under the answer folder, and explicitly lists the 3 deprioritized
   approaches (per-phrase weighting, beam rescoring, fine-tuning) as future work with one sentence
   each on why they were not attempted (per REQ-8). Satisfies REQ-7, REQ-8.
   Expected output: `assets/answer/parakeet-unified-biasing-improvement/` with all 3 required files.

## Remote Machines

GPU required for all NeMo `ASRModel.transcribe()` calls (matches t0017 and t0009 precedent — NeMo
GPU-PB is confirmed working only on GPU in this project's prior tasks). Use the existing reserved
machine: ssh alias `gpu-azure` (2×H100 NVL), remote path `/home/azureuser/rail-arf-stt`, conda env
`stt` (NeMo 3.1.0), per `t0017-progress` memory — this machine was left running specifically because
it is reserved and kept alive. Do not provision a new machine. Sync code with `rsync`, run scripts
over `ssh`, sync `data/` and `results/` back afterward. `parakeet-unified-en-0.6b` weights are
already in the remote HF cache from t0017 — no re-download needed. Estimated GPU time: ~90 minutes
total (Step 2 full run ~15 min, Step 3 screening 15 configs × 20 clips ~20 min + top-2 full runs
~30 min, Step 4 full run ~15 min, Step 5 is CPU-only post-processing).

## Assets Needed

* Gold-92 audio + ground truth: `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`
  (dependency chain via t0017's paths, not a direct `task.json` dependency of t0019 — access via
  the same relative-path convention as t0017's `code/paths.py`).
* BoH hallucination patterns CSV: `tasks/t0014_granite_short_clip_robustness/data/boh_patterns.csv`
  (same reuse pattern as t0017).
* t0017 results for baseline comparison: `tasks/t0017_parakeet_biasing_buffer_replacement/results/
  results_summary.md` and `results/metrics.json` (dependency `t0017_parakeet_biasing_buffer_
  replacement`, declared in `task.json`).
* NeMo model weights `nvidia/parakeet-unified-en-0.6b`: already cached in HF cache on `gpu-azure`
  from t0017's run, no new download.

## Expected Assets

* `predictions` asset `parakeet-unified-biasing-baseline` — 93-clip biased baseline reproduction,
  default GPU-PB hyperparameters.
* `predictions` asset `parakeet-unified-biasing-best-hyperparam` — 93-clip run with the winning
  alpha/depth_scaling from the Step 3 sweep.
* `predictions` asset `parakeet-unified-biasing-best-hyperparam-phrase-expansion` — 93-clip run with
  winning hyperparameters plus the expanded phonetic/misspelling phrase list from Step 4.
* `answer` asset `parakeet-unified-biasing-improvement` — states which approach(es) improved
  biasing quality, by how much (EA-DV delta vs t0017 baseline), and a ship/no-ship recommendation.

These match `task.json` `expected_assets: {"predictions": 3, "answer": 1}`.

## Time Estimation

* Setup/harness copy (Step 1): 15 minutes.
* Baseline reproduction (Step 2): 30 minutes (15 min GPU + validation/inspection).
* Hyperparameter sweep (Step 3): 60 minutes (20 min screening + 30 min top-2 full runs + analysis).
* Phrase expansion (Step 4): 30 minutes (transcript inspection + 15 min GPU run).
* Post-hoc check (Step 5): 15 minutes (CPU-only, no model calls).
* Metrics, charts, assets, answer (Steps 6-8): 45 minutes.
* **Total: ~3.25 hours**, dominated by GPU inference time on the already-running `gpu-azure` machine.

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hyperparameter sweep finds no config beats baseline EA-DV (GPU-PB ceiling is structural, not tuning-limited, per t0017's finding that biasing "barely helps") | Medium | Core deliverable (REQ-2) becomes a null result | Report it as a null result explicitly (not hidden) — this is a valid, useful finding per `LESSONS.md` "document negative results with the same rigor." Fall back to baseline config as the carried-forward "winner" for Step 4. |
| Phrase-expansion near-miss list over-fires and boosts wrong tokens elsewhere in the transcript (known GPU-PB failure mode: short/common phrases over-trigger, noted in t0017's referenced NeMo issues) | Medium | WER regression on non-domain-vocab words | Check full-transcript WER (not just EA-DV) after Step 4; if WER regresses more than 1 absolute point vs Step 3, drop the offending near-miss variant and re-run only that config, documenting the removed variant. |
| `gpu-azure` machine reservation lapses or is reclaimed mid-task | Low | Blocks all GPU steps | Machine is confirmed reserved/kept-alive per project policy (see `t0017-progress` memory); if unavailable, create an intervention file noting the blocker and escalate rather than silently switching to CPU (NeMo GPU-PB was only validated on GPU in this project). |
| Success rate on any condition drops below the 80% `MIN_SUCCESS_RATE` threshold (audio load failures, transcription exceptions) | Low | That condition's results are unusable | Reuse t0017's existing `RuntimeError` rejection guard in `run_buffer_sweep`-derived code; per the project's Rejection Criteria default rule, any condition with `successful/total < 0.8` is reported as null, not as a real measurement. |

## Verification Criteria

* Run `ls tasks/t0019_parakeet_biasing_improvement/assets/predictions/` and confirm exactly 3
  subfolders exist: `parakeet-unified-biasing-baseline`, `parakeet-unified-biasing-best-hyperparam`,
  `parakeet-unified-biasing-best-hyperparam-phrase-expansion`, each containing `details.json`,
  `description.md`, and a non-empty `files/predictions.jsonl` with 93 lines (or documented rejection
  if below the 80% success threshold): `wc -l tasks/t0019_parakeet_biasing_improvement/assets/
  predictions/*/files/predictions.jsonl`.
* Run `ls tasks/t0019_parakeet_biasing_improvement/assets/answer/parakeet-unified-biasing-
  improvement/` and confirm `details.json`, `short_answer.md`, `full_answer.md` all exist and
  `full_answer.md` contains all 8 `REQ-*` IDs (`grep -c 'REQ-' tasks/t0019_parakeet_biasing_
  improvement/assets/answer/parakeet-unified-biasing-improvement/full_answer.md` returns ≥ 8, one
  mention per requirement minimum).
* Run `uv run python -m json.tool tasks/t0019_parakeet_biasing_improvement/results/metrics.json`
  and confirm it parses as valid JSON with 3 named variants (`baseline`, `best-hyperparam`,
  `best-hyperparam-phrase-expansion`), each containing `wer_gold92`, `entity_accuracy_gold92`,
  `entity_accuracy_domain_vocab`, and `latency_p50_seconds` keys.
* Run `ls tasks/t0019_parakeet_biasing_improvement/results/images/` and confirm at least 2 `.png`
  files exist (`hyperparam_sweep_heatmap.png`, `condition_comparison.png`).
* Run `uv run python -u -m arf.scripts.verificators.verify_plan t0019_parakeet_biasing_improvement`
  (already run during planning, re-run after any plan edits) and confirm zero errors.
* Confirm requirement coverage: every `REQ-1` through `REQ-8` above is cited by at least one Step by
  Step item (manual cross-check against this document — all 8 appear in the numbered steps above).

## Rejection Criteria

Per `LESSONS.md` Lesson 3 (pre-register failure-rate rejection), any of the following make a
condition's numbers **null**, not reportable, regardless of what they show:

* Any of the 4 conditions (baseline, best-hyperparam, best-hyperparam-phrase-expansion, posthoc
  check) has `successful_clips / total_clips < 0.8` (the project-wide `MIN_SUCCESS_RATE` from
  `constants.py`).
* The hyperparameter sweep's 20-clip screening subsample was not drawn deterministically (same
  clip IDs across all 15 configs) — if the subsample varies per config, the screening comparison is
  invalid and must be re-run with a fixed subsample.
* GPU-PB boosting fails to apply (raises an exception in `apply_boosting`) for any condition — that
  condition is not "unbiased Parakeet," it is a broken run, and must be fixed or excluded, not
  reported as a biasing result.
* The post-hoc replacement check (Step 5) is reported as evidence for or against shipping
  `stt_replacements` to production — it is explicitly a feasibility ceiling estimate only, computed
  outside the real `brainpowa-realtime-api` pipeline, and must be labeled as such in the answer
  asset, not presented as a validated production measurement.
