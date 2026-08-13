---
spec_version: "2"
answer_id: "parakeet-unified-vs-tdt-production-fit"
answered_by_task: "t0017_parakeet_biasing_buffer_replacement"
date_answered: "2026-07-02"
confidence: "high"
---
## Question

Should brainpowa production Parakeet (parakeet-tdt-0.6b-v3) be replaced by parakeet-unified-en-0.6b,
and what streaming buffer size is best?

## Short Answer

CONDITIONAL — replace within the Parakeet family; reconsider the family entirely if domain-entity
accuracy is the priority. `parakeet-unified-en-0.6b` beats production `parakeet-tdt-0.6b-v3` on
every biased accuracy metric on gold-92 (WER 10.73% vs 15.15%, EA-DV 34.78% vs 33.33%, EA 23.44%
tie, 0 vs 3 empty transcripts). Buffer interval has no effect on accuracy; lower the production
buffer from 1000ms toward ~300ms for faster TTFD at no accuracy cost.

## Research Process

This answer was produced by a code experiment, reusing and extending the t0015 streaming buffer
harness. No new literature or internet research was performed for this task; it builds directly on
research already completed in t0009, t0012, and t0015.

1. **Setup:** Both candidate checkpoints (`nvidia/parakeet-tdt-0.6b-v3`,
   `nvidia/parakeet-unified-en-0.6b`) loaded via NeMo on an Azure H100 NVL GPU. GPU-PB TurboBias
   phrase boosting applied with Rezolve's 31-term domain vocabulary (alpha=1.0, context_score=1.0,
   depth_scaling=2.0, bpe_dropout=True), matching brainpowa production config.

2. **Compute-only sweep:** Simulated the production accumulate-then-retranscribe streaming pattern
   (32kB PCM chunks, re-transcribe every N ms) for both models across an extended interval grid
   (200/300/350/500/750/1000ms) on all 93 gold-92 clips, recording WER, entity accuracy (overall and
   domain-vocab), empty/hallucination counts, TTFD, and latency per clip.

3. **Bug found + fixed mid-task:** the casing-variant expansion used to widen the biasing phrase
   list (`expand_casing_variants()`) only capitalized the first character of the whole phrase
   (`phrase[:1].upper() + phrase[1:]`) instead of each word, so multi-word domain terms ("Salesforce
   Commerce Cloud", "Adobe Commerce", "Shopify Plus") never got a real title-case biasing variant —
   only their already-title original and an all-lowercase form. Fixed to `phrase.title()` (72
   effective phrase variants, up from a smaller effective set) in both this task's code and the
   shared t0015 harness it was copied from. The sweep was rerun with the fix; numbers moved slightly
   (WER improved ~0.1–0.3pp for both models) but the conclusion — unified wins — did not change.
   t0015's own results were not rerun (out of scope for this task).

4. **Real-time-paced validation:** A separate real-time-paced run (feeding audio at real speed
   rather than instantly) showed TTFD scales linearly with buffer interval (≈ interval + 16ms),
   correcting an artifact of the compute-only sweep where latency appeared nearly flat across
   intervals. See `results/buffer_interval_realtime.md`.

## Evidence from Papers

No new paper review was performed for this task. Model architecture claims (TDT decoder, unified
streaming decoder) rely on the NeMo/Parakeet documentation reviewed in t0012's literature pass.

## Evidence from Internet Sources

No new internet research was performed for this task. Model card details for both checkpoints were
confirmed against their HuggingFace pages (see Sources).

## Evidence from Code or Experiments

All findings come from a code experiment (`code/run_parakeet_buffer_sweep.py`,
`code/compute_and_write_metrics.py`) run on gold-92 (93 held-out production clips). 558 prediction
records per model (93 clips × 6 intervals) are on disk under `assets/predictions/`. Full metrics are
in `results/metrics.json` and `results/results_detailed.md`.

## Synthesis

`parakeet-unified-en-0.6b` wins on WER (10.73% vs 15.15%, −4.42pp), EA-DV (34.78% vs 33.33%,
+1.45pp), and reliability (0 vs 3 empty transcripts), while EA (overall entity accuracy) ties at
23.44%. Latency cost is +100ms compute (0.353s vs 0.253s p50 at 1000ms buffer), both far under the
800ms voice-to-action budget; TTFD is effectively equal (37ms vs 33ms). Buffer interval does not
affect final-transcript accuracy for either model; a real-time-paced run shows TTFD scales with
interval, so lowering the production buffer from 1000ms toward ~300ms gives ~3x faster TTFD at no
accuracy cost (more GPU passes per session is the trade-off). The dominant caveat: even with GPU-PB
TurboBias active and correctly configured on both models, domain-vocab entity accuracy tops out at
34.8% — both models mis-transcribe "Rezolve" as "Resolve" or "Rizol", never the correct spelling,
consistent with t0009's measured +1.4pp biasing gain for Parakeet and far below Granite Speech 4.1
2B's 97.1% EA-DV on the same vocabulary (t0012/t0015).

## Limitations

Biased accuracy only — unbiased runs were out of scope. Latency in the primary sweep is compute-only
(audio fed instantly, not real-time paced); the separate real-time-paced run
(`results/buffer_interval_realtime.md`) corrects for perceived latency but was not repeated with the
casing-variant fix. t0015's own results were not rerun after fixing the same casing bug there, so
t0015's published numbers may be marginally stale in the same direction as t0017's were.

## Recommendation

1. **If staying on Parakeet:** replace `parakeet-tdt-0.6b-v3` → `parakeet-unified-en-0.6b`. Strictly
   better quality, 3→0 empty outputs, latency still ≪800ms. One-line checkpoint swap
   (`PARAKEET_MODEL=nvidia/parakeet-unified-en-0.6b`); GPU-PB config and streaming path unchanged.
2. **Buffer:** lower from 1000ms toward ~300ms. TTFD improves ~3x, accuracy unchanged, no
   backpressure. Trade-off is more GPU passes per session.
3. **If domain-entity accuracy (Rezolve/brainpowa/SKU) is the priority:** Parakeet is the wrong
   model family — move to Granite Speech 4.1 2B (97.1% EA-DV). See t0012/t0014/t0015.

## Sources

* Task: `t0015_streaming_buffer_interval`
* Task: `t0012_whisper_parakeet_granite_streaming`
* Task: `t0009_parakeet_production_baseline`
* URL: https://huggingface.co/nvidia/parakeet-unified-en-0.6b
* URL: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
