# t0017 Results Summary — Parakeet unified vs TDT (biased) + buffer sweep

**Headline:** `parakeet-unified-en-0.6b` beats production `parakeet-tdt-0.6b-v3` on **every** biased
accuracy metric on gold-92 (WER 11.0% vs 15.3%, EA-DV 34.8% vs 33.3%, EA 23.4% vs 22.8%, 0 empty vs
3 empty), at a modest latency cost (p50 ~0.34s vs ~0.24s, both far under the 800ms voice-to-action
budget). TTFD is effectively equal (~37ms vs ~33ms). Winner by quality: **parakeet-unified**.

Buffer sweep on the winner (unified) across 200/300/350/500/750/1000ms: **accuracy is fully
invariant to interval** (identical final transcript); latency decreases slightly with larger
intervals (0.373s @200ms → 0.335s @1000ms, ~10%); TTFD flat at 37ms.

**Caveat (dominant finding):** biasing barely helps the Parakeet family. Even biased, the winner's
domain-vocab entity accuracy is only 34.8% — both models transcribe "Rezolve" as "Resolve"/"Rizol".
GPU-PB is active (66 phrase variants, alpha 1.0, confirmed on both models) but its ceiling on TDT/
unified is low, consistent with t0009 (+1.4pp). If domain-entity accuracy is the product goal,
neither Parakeet is the answer (Granite = 97.1% EA-DV).

## Recommendation

**CONDITIONAL replace.** Within the Parakeet family, swap production `parakeet-tdt-0.6b-v3` →
`parakeet-unified-en-0.6b`: strictly better quality (incl. 0 empty on short utterances — the failure
mode that dropped Whisper), TTFD unchanged, latency still ≈0.34s ≪ 800ms. Keep the buffer at
**1000ms / 32000 bytes** (lowest latency, quality invariant; smaller buffers only add partial-update
cadence at a latency cost). But if domain entity accuracy (Rezolve/brainpowa/SKU) is the priority,
Parakeet is the wrong family — move to Granite.
