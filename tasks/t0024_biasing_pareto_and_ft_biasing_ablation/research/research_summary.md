# Research Summary — t0024_biasing_pareto_and_ft_biasing_ablation

## Key Findings (top 10 insights directly actionable for this task)

1. No registered libraries exist in this project (`assets/library/` empty). All reuse is
   copy-into-task from prior tasks' `code/` directories.
2. `param_sweep.jsonl` (t0022, unified, 100 rows) and `tdt_sweep.jsonl` (t0023, TDT, 100 rows) share
   an identical flat schema: `{context_score, depth_scaling, alpha, brand_exact_rate, neutral_wer}`.
   No `error` fields — all 100/100 rows valid in both files. Directly poolable for the Pareto scan
   with no cleaning needed.
3. A verified Pareto scan (sort by `neutral_wer` ascending, keep cells with strictly-improving
   `brand_exact_rate`) gives a **5-cell TDT frontier**: `cs=2.5/ds=0.5/α=1.5` (37.1%@3.7%),
   `cs=2.5/ds=0.5/α=2.0` (48.6%@5.7%), `cs=3.0/ds=0.5/α=2.0` (54.3%@16.7%), `cs=2.5/ds=0.5/α=2.5`
   (57.1%@22.4%), `cs=3.0/ds=0.5/α=3.0` (60.0%@64.9%). Unified frontier is also 5 cells,
   `cs=2.0/ds=0.5/α=1.5` (40.0%@2.7%) through `cs=2.5/ds=0.5/α=2.5` (68.6%@27.9%).
4. Current live-prod TDT config (`cs=3.0/ds=0.5/α=1.5` → 45.7%@5.7%) is **not** on the frontier —
   strictly dominated by `cs=2.5/ds=0.5/α=2.0` (48.6% at the identical 5.7% neutral_wer). Confirms
   the manual spot-check in `task_description.md` exactly.
5. In both models' frontiers, `depth_scaling=0.5` dominates every frontier cell — no frontier point
   ever uses `ds≥1.0`, consistent with t0022's own finding.
6. Both prior tasks' "headline" max-brand_exact_rate cells (TDT 60%@64.9% WER; unified 69%@27.9%
   WER) are technically Pareto-optimal but sit at the extreme high-WER tail with 3-4 materially
   cheaper frontier alternatives closer to the knee — neither prior verdict weighed this cost.
7. Greedy-strategy boosting is a **silent no-op**: t0022's decoding-matrix experiment proved
   `greedy_batch` + boosting-tree config is byte-identical to `greedy_batch` with no boost (0/35
   brand-exact both). Only `malsd_batch` actually applies the boosting tree.
8. t0021's `run_clean_eval.py::apply_boosting()` (lines 126-135) only ever sets `greedy_batch` —
   never `malsd_batch` — so the fine-tuned checkpoint has *never* been evaluated with a working
   boosting tree. This is the exact gap Part B closes; fix is mechanical: swap that function body
   for t0023's `apply_malsd_boost()` (sets `strategy="malsd_batch"`, writes `beam.boosting_tree.*`).
9. Gold-92 is contaminated for t0021's fine-tuned checkpoint (all 93 clips had speed-perturbed
   versions in finetune training data) — gold-92 EA-DV (93.18%) is inflated ~55pp vs. clean-21 EA-DV
   (38.1%). Part B must use only the 21-clip clean eval set, exactly as `task_description.md`
   mandates.
10. t0021's WER metric uses `jiwer.wer()` on lowercased/punctuation-stripped text, documented as
    *not* matching other tasks' jiwer normalisation exactly — preserve this caveat in Part B's
    writeup for apples-to-apples comparability with the two existing rows (Biased-only 64.4%/0.0%;
    FT-only 55.8%/38.1%/0.112s p50).

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: Pure-Python Pareto scan + Matplotlib scatter (Part A)

No GPU/NeMo dependency. Read both JSONL files directly with `json.loads` per line, compute the
frontier with a ~15-line function (sort by `neutral_wer` ascending, keep strictly-improving
`brand_exact_rate`), and plot with `matplotlib.use("Agg")` following t0019's `make_charts.py`
pattern (scatter of all 100 cells, frontier highlighted/connected, prod point marked distinctly,
saved to `results/images/*.png` at dpi=150).

### Approach 2: Copy t0021 eval harness + swap boosting function (Part B)

Copy `run_clean_eval.py`, `constants.py`, `paths.py` from t0021's `code/` into t0024's `code/`.
Replace `apply_boosting()` with t0023's `apply_malsd_boost()` body. Point `FINETUNED_NEMO`/
`MANIFEST`/`CLEAN_EVAL_AUDIO_DIR` at t0021's existing paths (do not copy the data — reuse in place).
Parameterize `context_score`/`depth_scaling`/`alpha` from Part A's selected unified-model frontier
point (do not hardcode t0022's old headline cell).

### Approach 3: Asset templates from t0019/t0017

Use t0019's `assets/answer/{short_answer.md,full_answer.md,details.json}` and
`assets/predictions/{description.md,details.json,files/predictions.jsonl}` as the literal structural
template for t0024's expected 1 `predictions` + 1 `answer` asset (spec_version "2" schemas) —
content is fully task-specific but the JSON key structure is reusable as-is.

## Reusable Code / Assets

* `tasks/t0022_gpu_pb_diagnostic/results/param_sweep.jsonl` — 100-row unified sweep grid (read-only
  input, Part A).
* `tasks/t0023_tdt_vs_unified_biasing/results/tdt_sweep.jsonl` — 100-row TDT sweep grid (read-only
  input, Part A).
* `tasks/t0019_parakeet_biasing_improvement/code/make_charts.py` — Matplotlib `Agg`-backend +
  `results/images/` save pattern; template for `pareto_tdt.png`/`pareto_unified.png`.
* `tasks/t0023_tdt_vs_unified_biasing/code/run.py` (`apply_malsd_boost` L281-299,
  `reset_greedy_no_boost` L248-256, `_decode_output`/`transcribe` L158-183) — the malsd_batch
  boosting mechanism Part B needs; ~50 lines.
* `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` (292 lines) and
  `code/run_finetuned.py` (225 lines) — scoring functions (`normalise`, `wer`,
  `domain_vocab_accuracy`, `transcribe`, `run_eval`) and checkpoint-loading pattern
  (`ASRModel.restore_from`); ~150 lines directly reusable, drop the biased-only run-A logic.
* `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` (`DOMAIN_VOCAB`, 31 terms) and
  `code/paths.py` (`CLEAN_EVAL_DIR`, `MANIFEST`, `FINETUNED_NEMO`) — re-point `TASK_DIR` to t0024
  but resolve data paths into t0021's folder, do not copy data.
* `tasks/t0019_parakeet_biasing_improvement/assets/answer/` and `assets/predictions/` — JSON schema
  templates for t0024's expected assets.

## Key Papers (top 5, with finding most relevant to this task)

(not applicable — no papers research step run for this task; see Full Detail Available In)

## Risks Flagged in Research

* Dependency tasks' `task.json.status` is stale (t0021/t0022 show `not_started`, t0023 shows legacy
  `"complete"` not `"completed"`), but this is a known/documented metadata bug, already bypassed by
  the orchestrator's `check-deps` step for this task — do not edit other tasks' `task.json` to fix
  it.
* Both Part A frontiers are only as good as the underlying 35-brand/10-neutral clip subset of
  gold-92 used by the sweeps — not a re-derivation on a larger sample.
* Part B is n=21, directional only; gold-92 is contaminated for the fine-tuned checkpoint so must
  not be used for Part B evaluation under any circumstance.
* t0021's WER normalisation differs from other tasks' jiwer usage — flag this when presenting the
  three-way comparison table so readers don't over-interpret cross-metric precision.
* A pure post-decode string-replacement channel (t0019's `stt_replacements`, EA-DV 34.8%→95.7%) is
  out of scope for t0024 but should be mentioned in the answer asset as the higher-EA-DV,
  lower-effort production alternative for context.

## Full Detail Available In

* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_papers.md` — (not generated
  — step skipped)
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_internet.md` — (not
  generated — step skipped)
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/research/research_code.md` — 23 tasks
  reviewed, 6 cited
