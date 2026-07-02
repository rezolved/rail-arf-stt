# Task t0017 — Parakeet unified vs TDT: Biased Accuracy, Latency, Fine Buffer Sweep

## Goal

Decide whether the production Parakeet in `brainpowa-realtime-api`
(`nvidia/parakeet-tdt-0.6b-v3`, NeMo, GPU-PB TurboBias, ~1s streaming buffer) should be replaced by
`parakeet-unified-en-0.6b`.

## Background

Production STT (`src/brainpowa_realtime_api/pipeline/stt/parakeet.py`) loads
`parakeet-tdt-0.6b-v3` via NeMo `ASRModel.from_pretrained()`, biases Rezolve-domain phrases with
GPU-PB TurboBias (boosting tree in the TDT decoder; `alpha=1.0`, `context_score=1.0`,
`depth_scaling=2.0`, BPE-dropout on), and streams by re-transcribing an accumulating buffer every
32000 bytes (~1s at 16kHz mono PCM-16).

Two Parakeet candidates are on the table: `parakeet-unified-en-0.6b` (streaming-capable) and
`parakeet-tdt-0.6b-v3` (current production). t0015 already benchmarked both, biased, on gold-92 at
500/750/1000ms buffers: WER unified 9.53% vs TDT ~15.2%; EA-DV unified 34.8% vs TDT 33.3%; TTFD p50
TDT 32ms vs unified 37ms; latency p50 TDT ~250ms vs unified ~350ms. Quality was invariant to buffer
interval; larger intervals slightly reduced latency.

## Research Questions

1. **Implementation for biasing.** Does biasing Rezolve-type entities require NeMo? Confirm that the
   HuggingFace `transformers` Parakeet integration cannot do GPU-PB phrase boosting, and that NeMo
   GPU-PB works on both `parakeet-tdt-0.6b-v3` and `parakeet-unified-en-0.6b`. Output: which model +
   implementation to carry forward.
2. **Biased head-to-head.** With GPU-PB biasing enabled (Rezolve 31-term domain vocab), how do the
   two models compare on **biased** entity accuracy (EA, EA-DV) and latency (p50/p95, TTFD) on
   gold-92? Biased only — unbiased runs are out of scope.
3. **Fine buffer sweep on the winner.** How do TTFD, latency p50/p95, WER, and EA-DV vary across
   streaming buffer intervals **200, 300, 350, 500, 750, 1000ms**? Reuse t0015 for 500/750/1000ms;
   run the new 200/300/350ms intervals. Below the production 32kB (~1s) chunk, does going smaller
   buy responsiveness (lower TTFD / faster partials) at an acceptable latency and quality cost?
4. **Replace or not.** Given the above, replace `parakeet-tdt-0.6b-v3` with
   `parakeet-unified-en-0.6b` in production, keep TDT, or change the buffer size only?

## Dataset

gold-92 (93 WAV clips, ≥3.07s, 16kHz mono PCM-16). Biasing keyword list: the 31-term Rezolve domain
vocab used in t0012/t0014/t0015. gold-92 is a held-out regression set — never tune on it.

## Constraint

All inference simulates the production streaming path (accumulate PCM-16 bytes in 32kB chunks,
re-transcribe every N ms), matching `transcribe_stream()` in brainpowa-realtime-api. Biasing config
must match production defaults so the decision transfers.
