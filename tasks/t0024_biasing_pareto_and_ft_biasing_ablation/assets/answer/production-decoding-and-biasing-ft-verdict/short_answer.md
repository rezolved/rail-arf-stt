---
spec_version: "2"
answer_id: "production-decoding-and-biasing-ft-verdict"
answered_by_task: "t0024_biasing_pareto_and_ft_biasing_ablation"
date_answered: "2026-08-13"
---
## Question

Given the full Pareto frontier over brand_exact_rate vs neutral_wer for parakeet-tdt-0.6b-v3 and
parakeet-unified-en-0.6b, what production decoding defaults should brainpowa-realtime-api use, and —
evaluated on the 21-clip clean production set — are GPU-PB biasing and fine-tuning of
parakeet-unified-en-0.6b complementary or redundant?

## Answer

Ship `context_score=2.5, depth_scaling=0.5, alpha=2.0` as the production TDT decoding config: it
strictly dominates the current live-prod cell (`context_score=3.0, depth_scaling=0.5, alpha=1.5`),
gaining 2.9 percentage points of brand_exact_rate at zero extra neutral_wer cost. For
parakeet-unified-en-0.6b (not currently deployed), the frontier-selected cell under the same
ratio-threshold stance is `context_score=3.0, depth_scaling=0.5, alpha=1.5` (60.0% brand_exact_rate
at 8.7% neutral_wer). Whether biasing and fine-tuning are complementary or redundant is not answered
this round: the t0021 fine-tuned checkpoint and its `stt` conda environment could not be located on
any reachable machine, so the planned inference run never executed and this verdict is deferred
pending human resolution of that data-provenance gap.

## Sources

* Task: `t0021_parakeet_finetune_vs_biasing`
* Task: `t0022_gpu_pb_diagnostic`
* Task: `t0023_tdt_vs_unified_biasing`
* Task: `t0024_biasing_pareto_and_ft_biasing_ablation`
