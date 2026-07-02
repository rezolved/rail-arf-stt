# t0017 Results Summary — Parakeet unified vs TDT (biased) + buffer sweep

## Summary

`parakeet-unified-en-0.6b` beats production `parakeet-tdt-0.6b-v3` on **every** biased accuracy
metric on gold-92 (WER 10.7% vs 15.2%, EA-DV 34.8% vs 33.3%, EA 23.4% vs 23.4%, 0 empty vs 3 empty),
at a modest latency cost (p50 ~0.35s vs ~0.25s, both far under the 800ms voice-to-action budget).
TTFD is effectively equal (~37ms vs ~33ms). Winner by quality: **parakeet-unified**.

Buffer sweep on the winner (unified) across 200/300/350/500/750/1000ms: **accuracy is fully
invariant to interval** (identical final transcript); latency decreases slightly with larger
intervals (0.391s @200ms → 0.353s @1000ms, ~10%); TTFD flat at 37-38ms.

**Caveat (dominant finding):** biasing barely helps the Parakeet family. Even biased, the winner's
domain-vocab entity accuracy is only 34.8% — both models transcribe "Rezolve" as "Resolve"/"Rizol".
GPU-PB is active (72 phrase variants — original/lowercase/title-case, alpha 1.0, confirmed on both
models) but its ceiling on TDT/unified is low, consistent with t0009 (+1.4pp). If domain-entity
accuracy is the product goal, neither Parakeet is the answer (Granite = 97.1% EA-DV).

## Metrics

* WER (gold-92): unified 10.73% vs tdt 15.15% (−4.42pp)
* Entity accuracy (gold-92): unified 23.44% vs tdt 23.44% (tie)
* EA-DV (domain vocab): unified 34.78% vs tdt 33.33% (+1.45pp)
* Empty transcripts: unified 0/93 vs tdt 3/93
* Latency p50 @1000ms buffer: unified 0.353s vs tdt 0.253s
* TTFD p50: unified 0.037s vs tdt 0.033s

## Verification

`uv run python -m arf.scripts.verificators.verify_task_metrics t0017_parakeet_biasing_buffer_replacement`
passes with no errors. All 558 prediction records per model (93 clips × 6 intervals) were
regenerated end-to-end after the casing-variant biasing bug fix and re-scored with
`code/compute_and_write_metrics.py`; `results/metrics.json` reflects the corrected numbers reported
here.

## Recommendation

**CONDITIONAL replace.** Within the Parakeet family, swap production `parakeet-tdt-0.6b-v3` →
`parakeet-unified-en-0.6b`: strictly better quality (incl. 0 empty on short utterances — the failure
mode that dropped Whisper), TTFD unchanged, latency still ≈0.35s ≪ 800ms. Keep the buffer at
**1000ms / 32000 bytes** (lowest latency, quality invariant; smaller buffers only add partial-update
cadence at a latency cost). But if domain entity accuracy (Rezolve/brainpowa/SKU) is the priority,
Parakeet is the wrong family — move to Granite.
