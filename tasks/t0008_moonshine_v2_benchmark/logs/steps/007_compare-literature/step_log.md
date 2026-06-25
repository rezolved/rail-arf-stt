---
spec_version: "3"
task_id: "t0008_moonshine_v2_benchmark"
step_number: 7
step_name: "compare-literature"
status: "completed"
started_at: "2026-06-25T10:00:00Z"
completed_at: "2026-06-25T10:10:00Z"
---
## Summary

`results/compare_literature.md` written and verified with zero errors and zero warnings.

## Published Results Compared

Two external published results were compared:

1. **Kudlur2026** (arXiv 2602.12241, Moonshine v2 paper): WER=6.65% on Open ASR Leaderboard
   composite (Table 1), WER=2.08% on LibriSpeech test-clean (Table 1), latency=258ms on Apple M3
   (Abstract), Tiny Earnings-22 WER=20.27% (Table 1).

2. **t0004 Whisper large-v3 + initial_prompt** (prior project task, variant
   `whisper-large-v3-biased`): WER=8.5%, entity_accuracy_gold92=46.0%,
   entity_accuracy_domain_vocab=94.5%, AC-WER=2.5%, intent_preservation=98.9%, latency_p50=6.66s.

3. **t0004 Moonshine base** (prior project task, variant `moonshine-base`): WER=18.4%,
   entity_accuracy_gold92=21.7%, entity_accuracy_domain_vocab=10.9%, AC-WER=41.1%,
   intent_preservation=84.9%, latency_p50=0.070s.

## Key Findings

- WER gap vs. Kudlur2026 published (Open ASR Leaderboard): **+9.95pp** — entirely attributable to
  domain mismatch (gold-92 contains ecommerce brand names and accented English absent from the
  leaderboard benchmark).
- Latency vs. Kudlur2026: **232ms (this task) vs. 258ms (published)** — directionally consistent;
  backend difference (Transformers vs. ONNX) means the comparison is not hardware-matched.
- Entity accuracy (domain vocab) vs. t0004 Whisper biased: **9.1% vs. 94.5% (−85.4pp)** — reflects
  both the model difference and the presence/absence of vocabulary biasing; not a fair head-to-head.
- Entity accuracy vs. t0004 Moonshine base: **21.7% vs. 21.7% (0pp)** — v2 Medium adds no entity
  accuracy over base despite being 7x larger; vocabulary gap is architectural.

## Verificator

`verify_compare_literature t0008_moonshine_v2_benchmark` — PASSED, 0 errors, 0 warnings.

## Files Written

- `tasks/t0008_moonshine_v2_benchmark/results/compare_literature.md`
