---
spec_version: "1"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
---
# Pareto Frontier Tables — Part A

Raw intermediate artifact produced by `code/pareto.py` (data) and hand-assembled here from
`results/pareto_tdt.json` / `results/pareto_unified.json`. This is not the orchestrator-managed
detailed results writeup — that is produced by a later `results` step.

## TDT frontier (`parakeet-tdt-0.6b-v3`, source: t0023's `tdt_sweep.jsonl`, 100 rows)

Sorted ascending by `neutral_wer`. Deltas are vs. the current live-prod point
(`context_score=3.0, depth_scaling=0.5, alpha=1.5`, `brand_exact_rate=45.7%`, `neutral_wer=5.7%`).

| context_score | depth_scaling | alpha | brand_exact_rate | neutral_wer | Δneutral_wer vs live-prod | Δbrand_exact_rate vs live-prod |
| --- | --- | --- | --- | --- | --- | --- |
| 2.5 | 0.5 | 1.5 | 37.1% | 3.7% | -2.0pp | -8.6pp |
| 2.5 | 0.5 | 2.0 | 48.6% | 5.7% | 0.0pp | +2.9pp |
| 3.0 | 0.5 | 2.0 | 54.3% | 16.7% | +11.0pp | +8.6pp |
| 2.5 | 0.5 | 2.5 | 57.1% | 22.4% | +16.7pp | +11.4pp |
| 3.0 | 0.5 | 3.0 | 60.0% | 64.9% | +59.2pp | +14.3pp |

The live-prod point (`45.7%@5.7%`) is **not** on the frontier: it is dominated by
`context_score=2.5, depth_scaling=0.5, alpha=2.0` (`48.6%@5.7%`) — a strict, zero-extra-cost
`brand_exact_rate` improvement at the identical `neutral_wer`.

**Selected production cell (this task's stance, see below):
`context_score=2.5, depth_scaling=0.5, alpha=2.0`** (`brand_exact_rate=48.6%, neutral_wer=5.7%`).

## Unified frontier (`parakeet-unified-en-0.6b`, source: t0022's `param_sweep.jsonl`, 100 rows)

Sorted ascending by `neutral_wer`. Unified is not deployed in production, so there is no live-prod
anchor and no delta columns.

| context_score | depth_scaling | alpha | brand_exact_rate | neutral_wer |
| --- | --- | --- | --- | --- |
| 2.0 | 0.5 | 1.5 | 40.0% | 2.7% |
| 2.5 | 0.5 | 1.5 | 48.6% | 4.4% |
| 1.5 | 0.5 | 2.5 | 51.4% | 7.7% |
| 3.0 | 0.5 | 1.5 | 60.0% | 8.7% |
| 2.5 | 0.5 | 2.5 | 68.6% | 27.9% |

**Selected cell (this task's stance, see below): `context_score=3.0, depth_scaling=0.5, alpha=1.5`**
(`brand_exact_rate=60.0%, neutral_wer=8.7%`). This is the exact cell Part B (deferred, see
`intervention/checkpoint_not_found.md`) would use for its boosting config — it is numerically
coincidental that these parameter values match the current TDT live-prod config's numbers; they are
a different model's frontier selection.

## Selection stance

Starting from a baseline, walk each model's frontier in ascending `neutral_wer` order. Accept a
candidate frontier cell as the new baseline only if it both (a) strictly increases
`brand_exact_rate` over the current baseline, and (b) its marginal ratio
`Δneutral_wer / Δbrand_exact_rate`, measured against the current baseline (not necessarily the
immediately-preceding frontier row), is `<= 1.0` — never pay more than 1 percentage point of extra
`neutral_wer` for less than 1 percentage point of `brand_exact_rate` gained. TDT's baseline is the
current live-prod point (the config being reconsidered); unified's baseline is its own
lowest-`neutral_wer` frontier cell (no deployed reference exists). The scan continues through the
whole frontier regardless of a rejection. This threshold is implemented and enforced by
`code/pareto.py`'s `select_frontier_cell()`, not merely asserted here.

## Headline cell cost

Both prior tasks' "headline" cells (TDT `context_score=3.0/depth_scaling=0.5/alpha=3.0`; unified
`context_score=2.5/depth_scaling=0.5/alpha=2.5`) are technically Pareto-optimal — each is literally
the last (highest-`neutral_wer`) row in its frontier table above — but they sit at the extreme,
expensive tail: `64.9%` `neutral_wer` for TDT (roughly 11x the `5.7%` of this task's selected TDT
cell) and `27.9%` `neutral_wer` for unified (roughly 3x the `8.7%` of this task's selected unified
cell). The cheaper frontier alternatives closer to the "knee" deliver most of the `brand_exact_rate`
gain at a fraction of the `neutral_wer` cost.

## Frontier shape comparison

Unified reaches a higher selected `brand_exact_rate` (`60.0%`) than TDT's selected cell (`48.6%`),
and does so at a lower `neutral_wer` (`8.7%` vs. TDT's own frontier "knee" of `5.7%` for a lower
`48.6%` rate — TDT does not reach `60.0%` `brand_exact_rate` until `64.9%` `neutral_wer`, its most
expensive frontier cell). In other words, unified's frontier climbs to a higher `brand_exact_rate`
much faster (its `neutral_wer` "knee" around `4-9%` already buys `40-60%` `brand_exact_rate`) than
TDT's frontier, which needs `16-65%` `neutral_wer` to reach comparable `brand_exact_rate` levels
above `50%`. Read directly from the `selected_cell` and full `frontier` lists in
`results/pareto_tdt.json` / `results/pareto_unified.json`.

## Limitations

This frontier is only as good as the 35-brand-clip / 10-neutral-clip subset of gold-92 that
t0022/t0023 swept over (100 hyperparameter cells each, but the same fixed clip subset underlies
every cell) — it is not a re-derivation on a larger sample, and no new inference was run to check
this Pareto analysis against a different subset (`REQ-25`: Part A must not run new inference).
Separately, t0022's raw sweep contains `neutral_wer` values well above `100%` (up to `1511%`) at
extreme, dominated hyperparameter settings — a real ASR phenomenon (insertions can push word error
rate arbitrarily high), not a bug in this analysis; those points are visible as the long right-hand
tail in `results/images/pareto_unified.png` and never appear on the frontier.
