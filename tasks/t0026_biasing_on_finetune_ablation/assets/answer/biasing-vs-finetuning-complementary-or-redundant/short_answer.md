---
spec_version: "2"
answer_id: "biasing-vs-finetuning-complementary-or-redundant"
answered_by_task: "t0026_biasing_on_finetune_ablation"
date_answered: "2026-09-02"
---
## Question

Does GPU-PB context biasing still add brand accuracy once the model has already been fine-tuned on
Rezolve domain audio, or do the two techniques recover the same errors?

## Answer

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

## Sources

* Task: `t0021_parakeet_finetune_vs_biasing`
* Task: `t0022_gpu_pb_diagnostic`
* Task: `t0023_tdt_vs_unified_biasing`
* Task: `t0024_biasing_pareto_and_ft_biasing_ablation`
* Task: `t0024_parakeet_unified_checkpoint_archive`
