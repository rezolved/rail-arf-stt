---
spec_version: "2"
task_id: "t0017_parakeet_biasing_buffer_replacement"
status: "draft"
---

# Plan — Parakeet unified vs TDT: Biased Accuracy, Latency, Fine Buffer Sweep

## Objective

Produce a data-backed YES/NO/CONDITIONAL recommendation on replacing the production Parakeet
(`parakeet-tdt-0.6b-v3`) in `brainpowa-realtime-api` with `parakeet-unified-en-0.6b`, and on whether
to change the production streaming buffer size. Three parts:

1. **Model + implementation selection under a biasing requirement.** Rezolve-entity biasing
   ("Rezolve", "brainpowa", "NASDAQ", …) is a hard requirement. Establish that GPU-PB phrase
   boosting is only available in NeMo (the HuggingFace `transformers` Parakeet integration lacks it),
   and confirm GPU-PB applies to both candidate models. Decide which model + implementation proceeds.
2. **Biased head-to-head.** Measure biased entity accuracy (EA, EA-DV) and latency (p50/p95, TTFD)
   for both models on gold-92 with GPU-PB enabled. Biased only.
3. **Fine buffer sweep on the winner.** Sweep buffer intervals 200/300/350/500/750/1000ms; reuse
   t0015 for 500/750/1000ms, run the new 200/300/350ms.

## Approach

Two parts, both on GPU. Freshly re-run everything with GPU-PB — do not reuse t0015 predictions.

- **Part 1 — biased accuracy, both models.** Apply GPU-PB TurboBias to BOTH
  `parakeet-tdt-0.6b-v3` and `parakeet-unified-en-0.6b`, run on gold-92, measure biased accuracy
  (EA, EA-DV, WER). Biasing config mirrors production `parakeet.py`: `alpha=1.0`,
  `context_score=1.0`, `depth_scaling=2.0`, BPE-dropout on, 31-term Rezolve vocab expanded to casing
  variants. Confirm GPU-PB actually loads on `parakeet-unified` (`change_decoding_strategy`
  succeeds; boosting tree built) — if it does not, that model is disqualified and TDT wins by default.
  Pick the **winner by accuracy across all three metrics together** (EA-DV, EA, WER) — not latency.
- **Part 2 — latency + buffer sweep, winner only.** Take the accuracy winner and sweep streaming
  buffer intervals **200/300/350/500/750/1000ms**, measuring latency p50/p95 and TTFD p50/p95 per
  interval (plus WER/EA-DV to confirm quality holds). Only the winner is swept.
- Reuse the t0015 streaming harness: `run_parakeet_buffer_sweep.py --model {tdt,unified}`,
  `constants.py` (GPU-PB params, `INTERVAL_BYTES`), `compute_and_write_metrics.py`, `paths.py`.
  Extend `BUFFER_INTERVALS_MS`/`INTERVAL_BYTES` with 200/300/350ms (200→6400 B, 300→9600 B,
  350→11200 B at 16kHz int16). t0015 numbers are cross-checks only, not inputs.

## Task Requirement Checklist

- **REQ-1** Document, with `file:line` from `brainpowa-realtime-api`, that production biasing is NeMo
  GPU-PB TurboBias and that the `transformers` integration lacks phrase boosting (resolved by
  `docs/parakeet-vocabulary-biasing.md` — implementation = NeMo). Confirm GPU-PB loads and applies on
  BOTH `parakeet-tdt-0.6b-v3` and `parakeet-unified-en-0.6b` (`change_decoding_strategy` succeeds,
  boosting tree built, non-zero phrase count logged). Evidence: implementation-decision section in
  the answer asset + boosting-tree build log for each model. Satisfied by Step 1.
- **REQ-2** Fresh biased predictions for `parakeet-tdt-0.6b-v3` on gold-92, GPU-PB on, production
  biasing config. Evidence: `data/parakeet_tdt/predictions_biased.jsonl`, 93 rows. Satisfied by Step 2.
- **REQ-3** Fresh biased predictions for `parakeet-unified-en-0.6b` on gold-92, GPU-PB on, same
  config. Evidence: `data/parakeet_unified/predictions_biased.jsonl`, 93 rows. Satisfied by Step 2.
- **REQ-4** Head-to-head biased accuracy table: per model, EA, EA-DV, WER (+ empty/hallucination
  counts), computed via `compute_and_write_metrics.py`. Evidence: `results/metrics.json`
  (multi-variant) passes verificators. Satisfied by Step 3.
- **REQ-5** Winner selected by accuracy across all three metrics together (EA-DV, EA, WER);
  selection and rationale recorded. If one model is not strictly better on all three, state the
  tradeoff and pick by EA-DV first (biasing is the point), then EA, then WER. Evidence: winner
  section in `results_detailed.md`. Satisfied by Step 3.
- **REQ-6** Buffer sweep on the winner only at 200/300/350/500/750/1000ms via the extended harness,
  GPU-PB on. Evidence: `data/<winner>/predictions_{200,300,350,500,750,1000}ms.jsonl`, 93 rows each.
  Satisfied by Step 4.
- **REQ-7** Six-interval latency table for the winner: TTFD p50/p95, latency p50/p95 per interval,
  plus WER/EA-DV to confirm quality holds across intervals. Evidence: `results/metrics.json` has 6
  interval variants for the winner. Satisfied by Step 5.
- **REQ-8** Two charts saved to `results/images/` and embedded in `results_detailed.md`: (a) biased
  EA-DV + WER, unified vs TDT (grouped bar); (b) TTFD p50 and latency p50 vs buffer interval for the
  winner across all 6 intervals (line). Satisfied by Step 7.
- **REQ-9** Two prediction assets: `parakeet-tdt-buffer-sweep-biased`,
  `parakeet-unified-buffer-sweep-biased` (each spanning its measured intervals). Each passes
  `verify_predictions_asset.py`. Satisfied by Step 6.
- **REQ-10** Answer asset `parakeet-production-replacement-decision`: implementation decision (NeMo
  required), biased head-to-head, buffer-sweep tradeoff, and a final YES/NO/CONDITIONAL recommendation
  on (a) replacing TDT with unified and (b) changing the production buffer from ~1s. Include the
  brainpowa integration delta (does swapping the checkpoint in `parakeet.py` suffice, or does unified
  need config changes). Passes `verify_answer_asset.py`. Satisfied by Step 8.

## Cost Estimation

Small. Reuses t0015 predictions for 500/750/1000ms (0 GPU cost). New inference = winner (1 model,
likely both) × 3 new intervals × 93 clips. At ~0.25–0.35s latency/clip and more inference passes for
small buffers, ≈ 93×3 re-transcribe streams ≈ well under 1 GPU-hour on H100 NVL. Estimate < $20 GPU
if the t0015 reserved machine (`llm-t1-nc80`) is reused, plus agent/token cost for analysis + write-up.

## Step by Step

1. **biased-accuracy-run (REQ-1/2/3)** — on the GPU server, load both models via NeMo, apply GPU-PB
   (prod config, 31-term vocab + casing), transcribe gold-92 (93 clips) at a single fixed buffer
   (production 1000ms/32kB). Confirm boosting tree builds for each (non-zero phrase count in log).
   Write `data/parakeet_tdt/predictions_biased.jsonl` + `data/parakeet_unified/predictions_biased.jsonl`.
2. **head-to-head (REQ-4/5)** — compute EA, EA-DV, WER (+ empty/hallucination) for both via
   `compute_and_write_metrics.py`; build comparison table; pick winner by all three metrics.
3. **buffer-sweep (REQ-6/7)** — extend `BUFFER_INTERVALS_MS`/`INTERVAL_BYTES` with 200/300/350; run
   `run_parakeet_buffer_sweep.py` for the WINNER at all 6 intervals; measure latency p50/p95 + TTFD.
4. **results + assets (REQ-8/9/10)** — merge into `metrics.json`; 2 charts (accuracy bars;
   latency/TTFD vs interval); 2 prediction assets; answer asset with YES/NO/CONDITIONAL on replacing
   prod Parakeet + optimal buffer.
5. **reporting** — verificators, machine-usage log, set task completed.

Skip separate biased-vs-unbiased runs (unbiased out of scope); GPU-PB build log is proof enough that
biasing is active.

Research/planning sub-steps (research-papers, research-internet, research-code) are skipped: the
harness, models, and design are established in t0009/t0012/t0015.

## Remote Machines

Azure H100 NVL (`llm-t1-nc80`, reserved from t0015) if still live; otherwise one H100/A100 node.
Both checkpoints already cached there from t0015. GPU smoke gate before inference.

## Assets Needed

- gold-92 audio + `ground_truth.jsonl` (DVC).
- t0015 biased prediction JSONLs for both parakeet models (DVC).
- 31-term Rezolve domain vocab list (from t0012/t0015).
- t0015 code: `run_parakeet_buffer_sweep.py`, `constants.py`, `paths.py`,
  `compute_and_write_metrics.py`.

## Expected Assets

- `predictions`: 2 (`parakeet-tdt-buffer-sweep-biased`, `parakeet-unified-buffer-sweep-biased`).
- `answers`: 1 (`parakeet-production-replacement-decision`).

## Time Estimation

~0.5 day: reuse + fine sweep inference (1–2h), metrics + charts (1h), answer + reporting (1–2h).

## Risks & Fallbacks

- **Unified may not accept GPU-PB.** If `change_decoding_strategy` for GPU-PB fails on
  `parakeet-unified-en-0.6b`, that is the answer to REQ-1: unified cannot be biased → keep TDT;
  record the failure and stop the head-to-head early.
- **Small buffers raise latency, not lower it.** t0015 showed larger intervals slightly *reduce*
  latency (fewer passes). 200/300ms may increase compute/latency; the payoff is TTFD/partial cadence
  for realtime UX. Report both — do not assume smaller is better.
- **Sub-1s buffers below the 32kB chunk.** 200/300/350ms buffers are smaller than the 32kB (~1s)
  WebSocket chunk; ensure `INTERVAL_BYTES` drives re-transcription independent of chunk size, matching
  how `transcribe_stream()` accumulates. Fallback: feed smaller synthetic chunks if the harness
  couples the two.
- **Parakeet biasing barely moves the needle.** t0009 measured GPU-PB TurboBias at only **+1.4pp**
  domain-vocab EA on TDT (31.9%→33.3%), with overall EA −0.2pp and WER +0.1pp — vs Whisper
  `initial_prompt` +76pp and Granite keyword +66pp. So even biased, Parakeet EA-DV is ~33–35% (t0015).
  The likely honest outcome is "keep TDT; do not expect biasing gains from unified; if entity
  accuracy is the goal, Parakeet is the wrong family (Granite wins at 97.1%)." Document this negative
  result with the same rigor as a positive, and make it explicit in the answer asset.
- **gold-92 contamination.** Never tune on gold-92. Reuse only; no threshold fitting on it.

## Verification Criteria

- `results/metrics.json` passes `verify_task_metrics` and `verify_task_results`; multi-variant
  format; ≥6 interval variants for the winner + both models' head-to-head variants.
- 2 prediction assets pass `verify_predictions_asset.py`; each interval file has 93 rows.
- Answer asset passes `verify_answer_asset.py` with an explicit YES/NO/CONDITIONAL recommendation and
  the brainpowa integration delta.
- All charts saved to `results/images/` and embedded in `results_detailed.md`.
- REQ-1..REQ-10 each map to a satisfying step in `## Task Requirement Coverage` in results.
