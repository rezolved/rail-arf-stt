---
spec_version: "1"
task_id: "t0007_ibm_granite_4_1_benchmark"
date_completed: "2026-06-25"
---
# Results Summary — IBM Granite Speech 4.1 2B Benchmark on Gold-92

## Summary

IBM Granite Speech 4.1 2B with keyword biasing achieves 40.2% overall entity accuracy and 98.5%
domain-vocabulary entity accuracy on gold-92, matching Whisper's domain-vocab score (94.5%) and
delivering 27× lower latency (248 ms vs. 6.66 s p50). Against the actual production baseline
(Parakeet TDT 0.6b-v3, t0009), Granite biased is +73% better on overall entity accuracy (40.2% vs.
23.2%), +196% better on domain-vocab accuracy (98.5% vs. 33.3%), and −75% better on action-critical
WER (8.2% vs. 33.5%), at the cost of 6.5× higher latency (248 ms vs. 38 ms p50). Keyword biasing is
the decisive factor: unbiased Granite scores only 19.5% entity accuracy, while biasing raises it to
40.2% (+21 pp) and domain-vocab accuracy from 31.9% to 98.5% (+66.6 pp).

## Metrics

**Primary variant: Granite Speech 4.1 2B — keyword biased**

* **entity_accuracy_gold92**: 40.2% (BCa 95% CI: 30.4%–50.0%) vs. Parakeet prod 23.2% (+73%), vs.
  Whisper 46.0% (−5.8 pp)
* **entity_accuracy_domain_vocab**: 98.5% (BCa 95% CI: 88.6%–100%) vs. Parakeet 33.3% (+196%), vs.
  Whisper 94.5% (+4 pp)
* **wer_gold92**: 8.8% (BCa 95% CI: 7.1%–12.6%) vs. Parakeet 15.2% (−42%), vs. Whisper 8.5% (+0.3
  pp)
* **action_critical_wer_gold92**: 8.2% vs. Parakeet 33.5% (−75%), vs. Whisper 2.5% (+5.7 pp)
* **intent_preservation_gold92**: 92.5% vs. Parakeet 87.1% (+5.4 pp), vs. Whisper 98.9% (−6.4 pp)
* **latency_p50_seconds**: 0.248 s vs. Parakeet 0.038 s (6.5× slower), vs. Whisper 6.66 s (27×
  faster)
* **wrong_action_rate_gold92**: 7.5% proxy (1 − intent_preservation) vs. threshold < 2%

**Keyword-biasing gain (biased vs. batch):**

* ΔWER: −3.5 pp
* ΔEntity accuracy: +20.7 pp
* ΔDomain-vocab accuracy: +66.7 pp

## Verification

* All 93 clips transcribed in both batch and biased runs (0 failures)
* BCa bootstrap CIs computed (n=10,000 resamples)
* `ruff check tasks/t0007_ibm_granite_4_1_benchmark/code/` — PASSED
* `mypy -p tasks.t0007_ibm_granite_4_1_benchmark.code` — not run (GPU server env)
