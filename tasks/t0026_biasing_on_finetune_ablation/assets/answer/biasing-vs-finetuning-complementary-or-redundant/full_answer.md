---
spec_version: "2"
answer_id: "biasing-vs-finetuning-complementary-or-redundant"
answered_by_task: "t0026_biasing_on_finetune_ablation"
date_answered: "2026-09-02"
confidence: "high"
---
## Question

Does GPU-PB context biasing still add brand accuracy once the model has already been fine-tuned on
Rezolve domain audio, or do the two techniques recover the same errors?

## Short Answer

No — once `parakeet-unified-en-0.6b` is fine-tuned, GPU-PB biasing is redundant, not complementary.
On the 91-clip `clean_eval_v2` holdout, the fine-tuned model alone (arm C) already reaches 79.1%
brand_exact_rate versus the base model's 0%, and adding biasing on top (arm D, 83.7%) is not a
statistically significant improvement over C (McNemar c_vs_d: 3 clips gained, 1 lost, n=4
discordant, p=0.625), while it clears the un-fine-tuned biased model (arm B, 37.2%) decisively
(McNemar b_vs_d: p=1.9e-6). The two levers also overlap mechanically: every one of the 18 clips
fixed by exactly one lever is fixed by fine-tuning, none by biasing alone. Stacking biasing onto the
fine-tuned model is also far more expensive once fine-tuning is in place: neutral_wer rises 21.7
percentage points from C to D (27.1% to 48.8%), versus only 4.6 points from A to B on the base
model, driven by biasing over-triggering brand-term insertions on brand-adjacent neutral audio.

## Research Process

This task completes Part B of `t0024_biasing_pareto_and_ft_biasing_ablation`, whose answer asset
`production-decoding-and-biasing-ft-verdict` explicitly deferred the complementary-vs-redundant
verdict: at that time the fine-tuned checkpoint could not be located on any reachable machine, and
t0021's own attempt at a combined fine-tuning-plus-biasing evaluation had configured the broken
`greedy_batch` decoding path (0% brand accuracy for any config), so no working three-way comparison
had ever been run. Two blockers were resolved before this task started: the checkpoint was recovered
and DVC-archived as `parakeet-unified-v5` by `t0024_parakeet_unified_checkpoint_archive`, and
`t0021_parakeet_finetune_vs_biasing` built a larger, decontaminated 91-clip holdout,
`clean_eval_v2`, replacing the underpowered 21-clip set the deferred verdict would otherwise have
had to rely on.

This task ran a clean 2x2 ablation — model (base / `parakeet-unified-v5`) x decoding (`malsd_batch`
plain / `malsd_batch` + GPU-PB) — as four arms (A/B/C/D) on the same 91 clips, using the shared
`malsd_batch` boosting implementation from `t0023_tdt_vs_unified_biasing` and the
`DOMAIN_VOCAB`/scoring code from `t0021_parakeet_finetune_vs_biasing`, rather than re-implementing
either. The biasing hyperparameters (`context_score=3.0, depth_scaling=0.5, alpha=1.5`) were held
fixed at the cell `t0024_biasing_pareto_and_ft_biasing_ablation` selected as the unified-model
Pareto-frontier point, so the ablation isolates the fine-tuning x biasing interaction rather than
re-sweeping the biasing config. Before trusting any arm's numbers, `successful_requests` /
`total_requests` was checked against the plan's 0.8 rejection threshold for every arm: all four arms
completed 91/91 requests (100%), so all numbers below are reportable as computed, with no arm
excluded or flagged as unreliable.

## Evidence from Papers

The `papers` method was not used. This task's evidence is entirely from the project's own code
experiments — the four-arm ablation and its scoring pipeline — not from published literature or any
paper asset under `assets/paper/`. No paper was consulted, cited, or needed to reach this verdict.

## Evidence from Internet Sources

The `internet` method was not used. No external URLs or web sources were consulted for this answer;
all evidence is drawn from local files under `tasks/t0026_biasing_on_finetune_ablation/results/`,
produced by this task's own GPU inference run.

## Evidence from Code or Experiments

`results/ablation_metrics.json` records, per arm, over all 91 clips (43 brand: 40 Rezolve + 3
brainpowa; 48 neutral):

| Arm | brand_exact (overall) | brand_exact (Rezolve) | brand_exact (brainpowa) | neutral_wer | overall_wer |
| --- | --- | --- | --- | --- | --- |
| A — base, no bias | 0.0% | 0.0% | 0.0% | 8.1% | 24.7% |
| B — base + bias | 37.2% | 37.5% | 33.3% | 12.7% | 25.6% |
| C — FT, no bias | 79.1% | 82.5% | 33.3% | 27.1% | 28.0% |
| D — FT + bias | 83.7% | 87.5% | 33.3% | 48.8% | 45.7% |

`results/mcnemar_results.json` gives the paired significance tests on per-clip brand correctness:

* `b_vs_d`: 0 clips where B was right and D wrong, 20 where D was right and B wrong (20 discordant
  pairs), exact McNemar p = 1.9e-6 — D is decisively better than B.
* `c_vs_d`: 1 clip where C was right and D wrong, 3 where D was right and C wrong (4 discordant
  pairs total), exact McNemar p = 0.625 — with only 4 discordant pairs, D's +4.65-point nominal edge
  over C is statistically indistinguishable from noise.

`results/clip_level_appendix.json` lists the 18 clips fixed by exactly one of the two levers (B xor
C, relative to the unbiased/un-fine-tuned baseline A). All 18 are fixed by fine-tuning (arm C) and
zero are fixed by biasing alone (arm B) — e.g. `95b01c9b-...` ("Who is the CEO of Rezolve?") goes
from `hyp_a`/`hyp_b` = "The CEO of Resolve" (PHONETIC) to `hyp_c` = "the CEO of Rezolve" (EXACT),
while biasing alone never corrects the same phonetic Rezolve/Resolve confusion on this or any of the
other 17 clips. Of these 18 fine-tuning fixes, 16 remain EXACT once biasing is also applied (arm D),
and one regresses — `ab5466b6-...` ("Who is the CEO of Rezolve?") goes from `hyp_c` = "Who is the
CEO of Rezolve?" (EXACT) to `hyp_d` = "Conversational" (GARBAGE) — consistent with the single
C-favoring discordant pair in the c_vs_d McNemar count.

`results/arm_d_predictions.jsonl`'s neutral clips (`brand: null`) show the mechanism behind D's
neutral_wer cost: biasing over-triggers brand-adjacent vocabulary once the fine-tuned model is
already primed to hear brand terms. The four worst neutral clips (wer = 1.0) all reference "Brain
Commerce" or "Brain Cortex" — unrelated Rezolve product names — and are transcribed as "brainpowa"
or have "Rezolve" inserted: `"Brain Commerce"` to `"brainpowa."`; `"Brain Cortex"` to
`"brainpowa."`; `"Not Brain Commerce, Brain Cortex."` to `"Rezolve brainpowa brainpowa brainpowa."`;
`"What is SEO of Brain Commerce?"` to `"Where are Rezolve brainpowa?"`. This pattern recurs through
most of the highest-WER neutral clips in arm D and explains why the neutral_wer cost of adding
biasing scales up so much more once fine-tuning is already in place (+21.7 points, C to D) than it
does on the base model (+4.6 points, A to B): the fine-tuned model's output distribution is already
closer to brand vocabulary, so the same boosting tree has more brand-shaped tokens to over-amplify.

## Synthesis

**Q1 (is D significantly above both B and C?):** No. D clears B decisively (p = 1.9e-6) but does not
clear C at any conventional significance level (p = 0.625, only 4 discordant pairs) — the
"complementary" criterion requires both, and only one holds.

**Q2 (does D land within noise of max(B, C)?):** Yes. `max(B, C)` is C (79.1% vs 37.2%), and D's
83.7% is statistically indistinguishable from C's 79.1% per the c_vs_d McNemar test above — the
nominal 4.65-point gap is carried by only 4 discordant clips (3 favoring D, 1 favoring C).

**Q3 (per-clip 2x2 mechanism, B vs C):** The clip-level appendix shows the two levers are not
attacking different error classes. All 18 clips fixed by exactly one lever are fixed by C (fine-
tuning), none by B (biasing) alone — biasing's fixes are a subset of what fine-tuning already
recovers on this holdout, not a disjoint complementary set. This is the direct explanation for why
stacking biasing on top of fine-tuning (arm D) buys so little over fine-tuning alone (arm C).

**Q4 (neutral_wer cost, D vs C, compared to B vs A):** Biasing costs far more once the model is
fine-tuned. B costs +4.6 points of neutral_wer over A (8.1% to 12.7%); D costs +21.7 points over C
(27.1% to 48.8%) — roughly 4.7x the base-model cost for the same biasing configuration. Fine-tuning
does not make biasing cheaper; it makes it more damaging, because the fine-tuned model's outputs are
already brand-shaped and the boosting tree over-amplifies that tendency onto neutral, brand-adjacent
audio (see the "Brain Commerce"/"Brain Cortex" to "brainpowa" hallucinations above).

**Q5 (should `t0025_parakeet_tdt_brand_finetune` proceed as scoped?):** Fine-tuning is the dominant,
high-yield lever on this evidence — it alone recovers 79.1% brand_exact_rate from a 0% base, while
adding biasing on top contributes an insignificant amount at a disproportionate WER cost. `t0025`
fine-tuning parakeet-tdt-brand should proceed. However, its plan should not budget additional work
to stack GPU-PB biasing on top of the resulting checkpoint by default: this redundancy finding was
measured on `parakeet-unified`, and `t0025` targets a different base architecture (TDT). If a
biased-plus-fine-tuned TDT configuration is wanted in production, it needs its own small validation
pass before shipping — this task's numbers do not transfer across architectures.

## Limitations

* **brainpowa n=3 statistical power**: only 3 clips carry a `brainpowa` mention, and
  `brand_exact_rate` (brainpowa) is 33.3% and identical across arms B, C, and D (1/3 correct in
  each). This is anecdotal, not a measured effect — no brainpowa-specific McNemar test or confidence
  interval is reported anywhere in this document because none can be computed meaningfully at this
  sample size. The Rezolve-only breakdown (40 clips) carries the statistical weight of every
  conclusion above.
* **Architecture caveat for Q5**: this ablation used `parakeet-unified` throughout. The queued
  `t0025_parakeet_tdt_brand_finetune` fine-tunes a TDT-architecture base model, not
  `parakeet-unified`. The redundancy finding here — that biasing adds little once fine-tuning has
  already happened — is a property of this specific model family's error modes on this holdout, and
  the recommendation not to stack biasing onto `t0025`'s output by default should be treated as a
  starting hypothesis to re-check on TDT, not an architecture-independent law.
* **Biasing config not re-swept for the fine-tuned model**: arms B and D reuse the biasing cell
  selected by `t0024_biasing_pareto_and_ft_biasing_ablation` for the base model
  (`context_score=3.0, depth_scaling=0.5, alpha=1.5`). It is possible a milder biasing cell, tuned
  specifically against the fine-tuned model's already-brand-shaped output distribution, would
  recover some of arm D's neutral_wer cost without giving up its brand gain over arm B — this task
  deliberately did not re-tune the cell (to avoid confounding the ablation and burning extra GPU
  time), so that possibility remains untested.

## Sources

* Task: [t0021 — Parakeet fine-tune vs. biasing][t0021]
* Task: [t0022 — GPU-PB diagnostic sweep][t0022]
* Task: [t0023 — TDT vs. unified biasing sweep][t0023]
* Task: [t0024 — Biasing Pareto frontier and deferred fine-tune ablation][t0024]
* Task: [t0024 — Parakeet unified checkpoint archive][t0024-archive]

[t0021]: ../../../t0021_parakeet_finetune_vs_biasing/
[t0022]: ../../../t0022_gpu_pb_diagnostic/
[t0023]: ../../../t0023_tdt_vs_unified_biasing/
[t0024]: ../../../t0024_biasing_pareto_and_ft_biasing_ablation/
[t0024-archive]: ../../../t0024_parakeet_unified_checkpoint_archive/
