# t0026 — Biasing on Top of Fine-Tuning: Complementary or Redundant?

## Objective

Answer one question with a clean 2x2 ablation: **does GPU-PB context biasing still add brand
accuracy once the model has already been fine-tuned on Rezolve domain audio, or do the two
techniques recover the same errors?**

This completes **Part B of `t0024_biasing_pareto_and_ft_biasing_ablation`**, which was deferred
mid-task (suggestion `S-0024-01`) because the fine-tuned checkpoint could not be found on any
reachable machine. Both blockers are now gone:

* The checkpoint was located and archived to DVC by `t0024_parakeet_unified_checkpoint_archive` as
  the registered model asset `parakeet-unified-v5`.
* A larger decontaminated holdout, `clean_eval_v2` (91 clips), was added to
  `t0021_parakeet_finetune_vs_biasing` — replacing the n=21 set whose statistical power `S-0024-07`
  flagged as inadequate.

## Motivation

The project's headline goal is beating production Deepgram on entity accuracy for brand and product
terms. Two independent levers now exist, and their costs are very different:

| Lever | Cost | Evidence |
| --- | --- | --- |
| GPU-PB context biasing (`malsd_batch`) | inference-time only, config change | t0022/t0023/t0024 |
| Domain fine-tuning | GPU training run + checkpoint lifecycle | t0021 |

If they are **complementary**, production should ship both and the two prior workstreams stack. If
they are **redundant**, the project can drop whichever is more expensive to operate — and the answer
determines whether the queued `t0025_parakeet_tdt_brand_finetune` fine-tune is worth running at all
on top of a biased decoder. No task so far has measured the interaction; every prior result varies
one lever with the other held fixed.

## Runs

Four arms, all on the same 91 clips, same scoring code, single GPU session:

| Arm | Model | Decoding |
| --- | --- | --- |
| A — base, no bias | `nvidia/parakeet-unified-en-0.6b` | `malsd_batch`, no boosting tree |
| B — base + bias | `nvidia/parakeet-unified-en-0.6b` | `malsd_batch` + GPU-PB, `context_score=3.0`, `depth_scaling=0.5`, `alpha=1.5` |
| C — FT, no bias | `parakeet-unified-v5` (DVC) | `malsd_batch`, no boosting tree |
| D — FT + bias | `parakeet-unified-v5` (DVC) | `malsd_batch` + GPU-PB, `context_score=3.0`, `depth_scaling=0.5`, `alpha=1.5` |

The biasing cell is **not** re-swept. `context_score=3.0 / depth_scaling=0.5 / alpha=1.5` is the
unified-model Pareto-frontier cell selected by t0024 Part A (60.0% `brand_exact_rate` at 8.7%
`neutral_wer`, see
`tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json`). Re-tuning it on
the FT checkpoint would confound the ablation and burn GPU hours; if arm D underperforms arm B, note
it as a follow-up rather than tuning inside this task.

All four arms use `malsd_batch` including the unbiased ones — t0022 established that `greedy_batch`
gives 0% brand EXACT, so pairing "no bias" with `greedy_batch` would measure the decoder change, not
the biasing.

## Eval set

`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/` — 91 clips, DVC-tracked audio
(`audio.dvc`), manifest at `manifest.jsonl`.

* 74 clips `source: quepasa_prod`, 17 clips `source: clean_eval_21`
* 43 clips contain a brand term: 40 `Rezolve` mentions, 3 `brainpowa` mentions
* 48 neutral clips carry the WER-cost side of the tradeoff

Decontamination was done in `t0021` (commit `c17327a` removed 8 clips found in `train_v5`), so this
set is disjoint from the `parakeet-unified-v5` fine-tuning data. **gold-92 must not be used here** —
`train_v5` contains 60 of gold-92's 93 clips by exact `clip_id`, so any figure on it for a
`train_v5`-derived checkpoint is inflated. The uncontaminated remainder is no substitute either: all
33 of those clips are `source: clean_voices`, meaning every `production` clip and every
`error_cases` clip is inside the training data, and only 8 of the 33 carry a brand term.

**Known power limit, state it in the results rather than papering over it**: with only 3 `brainpowa`
clips, this task cannot resolve a `brainpowa`-specific effect. The `parakeet-unified-v5` model card
records 0/3 `brainpowa` on the old clean set. Report `brainpowa` separately from `Rezolve` and treat
any `brainpowa` delta as anecdotal.

## Prerequisite: fix the manifest paths

`clean_eval_v2/manifest.jsonl` currently stores `audio_filepath` as absolute paths from the
annotator's laptop (`/Users/margotiamanova/Desktop/...`). Rewrite them relative to the repo root as
step one, on the machine, before any inference — otherwise every arm fails to load audio. Do not
commit machine-specific absolute paths back.

## Metrics

Per arm, computed by one shared scoring function so all four are comparable:

* `brand_exact_rate` — fraction of brand mentions transcribed verbatim after normalisation, split
  three ways: overall, `Rezolve` only, `brainpowa` only
* `neutral_wer` — WER over the 48 neutral clips (the cost side of the tradeoff)
* `overall_wer` — WER over all 91 clips
* `efficiency_inference_time_per_item_seconds` — per arm, to confirm GPU-PB's decoding overhead is
  acceptable for the <800 ms p50 voice-to-action budget

**Registered project metrics: N/A.** Every registered metric in `meta/metrics/` except
`latency_p50_seconds` is defined against gold-92 ground truth, which this task deliberately does not
use. `results/metrics.json` will be `{}`, as in t0024. Latency here is single-clip batch inference,
not end-to-end voice-to-action, so it does not satisfy `latency_p50_seconds` either.

## Key questions

1. Is arm D's `brand_exact_rate` significantly above **both** arm B and arm C? (complementary)
2. Or does arm D land within noise of `max(B, C)`? (redundant — the two levers fix the same clips)
3. Which clips does each lever fix that the other does not? Produce the per-clip 2x2 confusion of
   correct/incorrect between arms B and C — this is the actual mechanism evidence, not the
   aggregate.
4. What does biasing cost arm D in `neutral_wer` relative to arm C, and is that cost the same as the
   `B - A` cost on the base model? (Does fine-tuning make biasing cheaper or more damaging?)
5. Given the answer, should `t0025_parakeet_tdt_brand_finetune` proceed as scoped?

Report a McNemar test on the paired per-clip brand-correctness for the B-vs-D and C-vs-D comparisons
— with n=43 brand clips, aggregate percentage-point differences alone will not separate signal from
noise.

## Code reuse

Do **not** copy-paste the helpers a sixth time — `S-0024-05` documents that `apply_beam_boosting` /
`apply_malsd_boost`, `DOMAIN_VOCAB`, and the `normalise` / `wer` / `domain_vocab_accuracy` scoring
functions have been duplicated across t0017, t0019, t0021, t0022, and t0023 already, which is how
the `malsd_batch`-vs-`greedy_batch` bug failed to propagate between copies. Sources for this task:

* `tasks/t0023_tdt_vs_unified_biasing/code/run.py:281` — `apply_malsd_boost`
* `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py` — `DOMAIN_VOCAB`
* `tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py` — clean-eval scoring

Import them, or if the import path is genuinely unworkable across task folders, promote them to a
registered library asset as `S-0024-05` recommends and have this task be the first consumer.

## Assets

Four `predictions` assets, one per arm (`clean-eval-v2` scope), plus one `answer` asset carrying the
complementary-vs-redundant verdict and its production recommendation.

## Compute and budget

* **Machine: `LLM-T1-NC80`, GPU 1 — `CUDA_VISIBLE_DEVICES=1`.** Not a suggestion; pin it. This is
  the only box in `project/azure_vm.json` and the only one carrying the `stt` conda env (NeMo
  3.1.0), the HF model cache, and `/mnt/finetune-checkpoints/`. It has 2xH100 NVL and 880 GB RAM, so
  this task shares it with `t0025`, which is pinned to `CUDA_VISIBLE_DEVICES=0`. Both are 0.6B
  models — one training run plus one inference sweep fit comfortably. Set the variable explicitly in
  every command; do not rely on the default, or the two tasks will collide on GPU 0.
* See `docs/northeurope_pool_runbook.md` for the SSH alias and the **mandatory HostName refresh
  after every start** — Azure reassigns the public IP, and a stale alias fails as
  `failure_phase="ssh_connect"`.
* **Never write durable output to `/mnt`** on any pool box — it is the ephemeral local disk and is
  wiped on every stop/start. This is how the t0021 checkpoint was lost. `dvc pull` the checkpoint
  into the task folder, and `dvc push` anything worth keeping before teardown.
* Historical note, do not re-litigate: `FT-MC` was removed from the pool on 2026-08-26 after its
  single use (t0024) failed on a missing `stt` env — $14.06, zero results.
* **Work**: 4 arms x 91 clips of batch inference on a 0.6B model. Well under an hour of GPU time;
  the wall clock is dominated by VM start, `dvc pull` of the checkpoint plus audio, and env setup.
* **Estimate**: ~2 GPU-hours. Running alongside `t0025` on the same box costs nothing extra — the VM
  bills at one $13.96/hr rate whether one GPU is busy or both — so budget this task at **$0** when
  it shares the box, and ~$28 when it runs alone.
* **This task may run concurrently with `t0025`.** `LLM-T1-NC80` declares `max_concurrent_tasks: 2`,
  and `acquire` now joins a `Running` VM that already carries an ARF lock instead of refusing it (PR
  #25). Whichever task starts the box first, the other joins it. At teardown, the task that did
  **not** start the VM must pass `--joined-running-vm` so the shared window is not billed twice;
  check `started_vm` in this task's acquire output to know which one you are.
* **Start this task first anyway**: `t0025` cannot begin until its `val_v6.jsonl` is built, which is
  CPU-only work that can proceed while this task already holds the GPU.
* No second machine — four short arms on one GPU beats a second VM acquisition.

## Outputs

Charts (all to `results/images/`, embedded in `results_detailed.md`):

1. Grouped bar chart — `brand_exact_rate` by arm (A/B/C/D), one group per brand term bucket (overall
   / `Rezolve` / `brainpowa`). Answers Q1/Q2: does D clear both B and C?
2. Scatter — x: `neutral_wer`, y: `brand_exact_rate`, one point per arm, with t0024's unified Pareto
   frontier drawn as the reference line. Answers Q4: where do the FT arms sit relative to the
   biasing-only frontier?
3. 2x2 heatmap — per-clip brand correctness, arm B (correct/incorrect) x arm C (correct/incorrect),
   cell values = clip counts. Answers Q3: the overlap of what each lever fixes.

Tables:

* Main results table — rows: arms A–D; columns: `brand_exact_rate` (overall / Rezolve / brainpowa),
  `neutral_wer`, `overall_wer`, inference time per item.
* Paired-test table — rows: B-vs-D and C-vs-D; columns: discordant pair counts, McNemar statistic,
  p-value.
* Clip-level appendix — the clips fixed by exactly one lever, with reference and all four
  hypotheses, so the mechanism is inspectable rather than inferred from aggregates.

## Dependencies

* `t0024_parakeet_unified_checkpoint_archive` — supplies the `parakeet-unified-v5` checkpoint as a
  DVC-tracked model asset. Hard dependency: without it there is nothing to fine-tune-test.
* `t0021_parakeet_finetune_vs_biasing` — supplies `clean_eval_v2`, the `DOMAIN_VOCAB` list, and the
  clean-eval scoring code.
* `t0024_biasing_pareto_and_ft_biasing_ablation` — supplies the frontier-selected biasing cell this
  task holds fixed, and is the task whose Part B this completes.

`t0023_tdt_vs_unified_biasing` is not listed as a dependency despite supplying `apply_malsd_boost`,
because its `task.json` uses a legacy pre-`spec_version` schema that the dependency checker and
aggregators cannot read (`S-0024-06`). Read its code directly. Note that
`t0024_parakeet_unified_checkpoint_archive` also still carries `status: not_started` despite its
assets being merged to `main`, so `verify_task_dependencies.py` may false-negative here — check the
merged assets on disk before treating that as a real block.
