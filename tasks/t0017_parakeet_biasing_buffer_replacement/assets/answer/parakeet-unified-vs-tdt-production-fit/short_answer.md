---
spec_version: "2"
answer_id: "parakeet-unified-vs-tdt-production-fit"
answered_by_task: "t0017_parakeet_biasing_buffer_replacement"
date_answered: "2026-07-02"
---
## Question

Should brainpowa production Parakeet (parakeet-tdt-0.6b-v3) be replaced by parakeet-unified-en-0.6b, and what streaming buffer size is best?

## Answer

CONDITIONAL — replace within the Parakeet family; reconsider the family entirely if domain-entity
accuracy is the priority. `parakeet-unified-en-0.6b` beats production `parakeet-tdt-0.6b-v3` on
every biased accuracy metric on gold-92 (WER 10.73% vs 15.15%, EA-DV 34.78% vs 33.33%, EA 23.44%
tie, 0 vs 3 empty transcripts), at a modest latency cost (p50 ~0.35s vs ~0.25s, both far under the
800ms voice-to-action budget). Buffer extraction interval has no effect on final-transcript
accuracy; production buffer should be lowered from 1000ms toward ~300ms for faster TTFD with no
accuracy loss (see `results/buffer_interval_realtime.md`). The dominant caveat: even biased,
domain-vocab entity accuracy tops out at 34.8% for either Parakeet model — both still mis-transcribe
"Rezolve" as "Resolve"/"Rizol". If entity accuracy on brand/product terms is the product goal,
Parakeet is the wrong model family — Granite Speech 4.1 2B reaches 97.1% EA-DV on the same
vocabulary (t0012/t0015).

## Sources

* Task: `t0015_streaming_buffer_interval`
* Task: `t0012_whisper_parakeet_granite_streaming`
* Task: `t0009_parakeet_production_baseline`
* URL: https://huggingface.co/nvidia/parakeet-unified-en-0.6b
* URL: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
