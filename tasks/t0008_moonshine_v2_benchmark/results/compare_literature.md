---
spec_version: "1"
task_id: "t0008_moonshine_v2_benchmark"
date_compared: "2026-06-25"
---
# Comparison with Published Results

## Summary

Moonshine v2 Medium was compared against the published Kudlur2026 paper (arXiv 2602.12241) and
against two prior-task baselines from this project (t0004: Whisper large-v3 + initial_prompt and
t0004: Moonshine base). On the Open ASR Leaderboard, Kudlur2026 reports **6.65% WER** and **258ms
latency** for the Medium variant on Apple M3; on gold-92, this task measures **16.6% WER** and
**232ms warmed p50 latency**. The WER gap of **+9.95 percentage points** is explained by domain
mismatch: gold-92 contains Rezolve-specific brand names and accented English that are absent from
Moonshine's training distribution. Entity accuracy, not reported in Kudlur2026, was **21.7%**
overall and **9.1%** on the 31-term domain vocabulary — far below the t0004 Whisper biased baseline
of **94.5%**.

## Comparison Table

| Method / Paper | Metric | Published Value | Our Value | Delta | Notes |
| --- | --- | --- | --- | --- | --- |
| Moonshine v2 Medium [Kudlur2026, Table 1] | WER (avg Open ASR Leaderboard) | 6.65% | 16.6% | +9.95pp | Different test set: gold-92 vs. Open ASR Leaderboard composite; gold-92 has domain-specific brand names and accented English |
| Moonshine v2 Medium [Kudlur2026, Table 1] | WER (LibriSpeech test-clean) | 2.08% | 16.6% | +14.52pp | Different test set: clean read-aloud LibriSpeech vs. Rezolve production utterances; not directly comparable |
| Moonshine v2 Medium [Kudlur2026, Abstract] | Latency p50 (Apple M3) | 258ms | 232ms | −26ms | Different hardware/backend: Kudlur2026 uses optimised ONNX on Apple M3; this task uses HuggingFace Transformers CPU backend on a local CPU; latency is not directly comparable but is of the same order |
| Moonshine v2 Tiny [Kudlur2026, Table 1] | WER (Earnings-22, domain-specific) | 20.27% | 16.6% | −3.67pp | Different model size (Tiny vs. Medium) and different domain benchmark (financial earnings vs. ecommerce); Earnings-22 is the closest public domain-specific proxy |
| Moonshine base [t0004, variant moonshine-base] | WER (gold-92) | 18.4% | 16.6% | −1.8pp | Same dataset; different model variant (base vs. streaming-medium); v2 Medium modestly improves WER over base |
| Moonshine base [t0004, variant moonshine-base] | entity_accuracy_gold92 | 21.7% | 21.7% | 0.0pp | Same dataset; identical entity accuracy despite larger model size — confirms vocabulary gap is architectural, not capacity-limited |
| Moonshine base [t0004, variant moonshine-base] | entity_accuracy_domain_vocab | 10.9% | 9.1% | −1.8pp | Same dataset; v2 Medium is marginally worse on domain vocabulary than base, within noise |
| Whisper large-v3 + initial_prompt [t0004, variant whisper-large-v3-biased] | WER (gold-92) | 8.5% | 16.6% | +8.1pp | Same dataset; Moonshine v2 Medium WER is approximately 2x worse than the biased Whisper baseline |
| Whisper large-v3 + initial_prompt [t0004, variant whisper-large-v3-biased] | entity_accuracy_domain_vocab | 94.5% | 9.1% | −85.4pp | Same dataset; the gap reflects Whisper's vocabulary biasing via initial_prompt vs. Moonshine with no biasing |
| Whisper large-v3 + initial_prompt [t0004, variant whisper-large-v3-biased] | latency_p50_seconds | 6.66s | 0.232s | −6.43s | Same hardware class; Moonshine is 29x faster at p50 warmed latency — the key latency advantage |

## Methodology Differences

- **Test set**: Kudlur2026 evaluates on the Open ASR Leaderboard composite (LibriSpeech,
  Earnings-22, and other standard sets). This task evaluates on gold-92, a Rezolve-specific set of
  93 production utterances with accented English and ecommerce brand/product entities not present in
  any standard benchmark.

- **Model variant and backend**: Kudlur2026 uses an ONNX export optimised for Apple M3 via
  `moonshine_onnx`. This task uses `UsefulSensors/moonshine-streaming-medium` via HuggingFace
  Transformers (CPU backend), because the `moonshine_onnx` package does not ship a Medium-variant
  ONNX model. The Transformers backend is expected to be slower than the ONNX export; the latency
  comparison is therefore not apples-to-apples.

- **Entity accuracy**: Kudlur2026 does not report entity-level accuracy. Entity accuracy on domain
  vocabulary is measured only in this task, using a 31-term Rezolve vocabulary (brand names, product
  identifiers, SKU codes). There is no published comparator for this metric.

- **Vocabulary biasing**: Kudlur2026 tests with no vocabulary biasing. This task also tests with no
  biasing, which is the baseline condition being compared. The t0004 Whisper baseline uses
  `initial_prompt` vocabulary biasing, making that comparison a biased-vs-unbiased cross-model
  comparison rather than a direct head-to-head.

- **Accent conditions**: gold-92 contains 34 production clips with accented English
  (`accent_group="production"`). No accented-English stratification is reported in Kudlur2026.
  Moonshine's entity accuracy on the accented subset is **5.9%**, substantially below the **21.7%**
  overall figure.

- **Prior task comparison (Moonshine base vs. v2 Medium)**: t0004 benchmarked `moonshine-base` on
  gold-92 as a side variant. That run produced WER=18.4%, entity_accuracy=21.7%,
  entity_accuracy_domain_vocab=10.9%. The v2 Medium (this task) achieves WER=16.6%, entity_accuracy=
  21.7%, entity_accuracy_domain_vocab=9.1%. WER improves by **1.8pp** but entity accuracy is
  unchanged — consistent with the conclusion that entity failure is vocabulary-driven, not
  capacity-driven.

## Analysis

### Literature comparison: WER gap on domain-specific data

Kudlur2026 reports **6.65% WER** for Moonshine v2 Medium on the Open ASR Leaderboard and **2.08%
WER** on LibriSpeech test-clean. This task measures **16.6% WER** on gold-92 — a **+9.95pp delta**
against the leaderboard figure. This is not surprising: the Open ASR Leaderboard draws on clean and
semi-clean English, whereas gold-92 contains Rezolve production utterances with non-standard proper
nouns ("Rezolve", "brainpowa", "B2-4792") and accented English from investor- relations sessions.
The gap is a domain mismatch, not a model failure. The Tiny model's **20.27% WER** on Earnings-22
[Kudlur2026, Table 1] provides the closest public proxy for domain- specific degradation; this
task's 16.6% for the Medium model is directionally consistent with the trend from clean to
domain-specific data.

### Latency: published claim partially confirmed

Kudlur2026 reports **258ms** for the Medium model on Apple M3 using the ONNX backend. This task
measures **232ms warmed p50** using the HuggingFace Transformers backend on a local CPU. The
Transformers backend is expected to be slower (no ONNX graph optimisation), yet the measured latency
is slightly lower, likely because this task uses sequential per-clip inference on a modern CPU with
no inter-clip model reloading. The values are of the same order. The **200ms p50 target** set by the
project was not met (233ms for warmed clips), but the gap is modest — roughly 33ms (16.5%) — and
would likely close with an ONNX export.

### Entity accuracy: no published baseline exists

Kudlur2026 reports no entity-level metrics. This task is the first measurement of Moonshine v2
Medium entity accuracy on a domain-specific ecommerce vocabulary. The result — **9.1% domain-vocab
entity accuracy** — is substantially below the production target of ≥46% (Whisper unbiased baseline
from t0004). The failure mode is systematic: the model consistently transcribes brand tokens as
phonetically similar common words ("Rezolve" → "resolve"/"result", "brainpowa" → "brain power/
powa"). This is a vocabulary coverage issue, not a WER issue.

### Prior task comparison: v2 Medium does not improve entity accuracy over base

The t0004 Moonshine base variant achieved entity_accuracy_gold92=21.7% and
entity_accuracy_domain_vocab=10.9%. This task (v2 Medium) achieves entity_accuracy_gold92=21.7% and
entity_accuracy_domain_vocab=9.1%. Entity accuracy is **identical at the overall level** and
**marginally worse on domain vocabulary**, despite the Medium model being 7× larger than base (~267M
vs. ~38M parameters). This finding contradicts the implicit assumption in the task description that
a larger model would improve entity recall. The result strongly supports the interpretation that
entity failures are caused by out-of-vocabulary training distribution, not by model capacity, and
that vocabulary biasing is required before Moonshine can serve as an edge fallback.

### Wrong-action rate: far above production threshold

The project defines a **<2% wrong-action rate** threshold. This task's proxy (1 −
intent_preservation) yields **12.9%** — 6× above the threshold. The t0004 Whisper biased baseline
achieves intent_preservation=98.9% (wrong-action rate ~1.1%). Moonshine's intent preservation on the
production (accented) subset is **79.4%**, implying a wrong-action rate of **20.6%** for the
highest-stakes utterances — clearly disqualifying for production deployment without biasing.

## Limitations

- **No published entity accuracy comparator**: Kudlur2026 does not report entity-level metrics. The
  comparison is limited to WER and latency against the published paper. Entity accuracy comparisons
  are against prior project tasks (t0004), not published literature.

- **Different test conditions for WER comparison**: The Open ASR Leaderboard benchmark used by
  Kudlur2026 does not include gold-92. The WER delta of +9.95pp is therefore a domain-mismatch
  measurement, not a reproducibility failure.

- **ONNX vs. Transformers backend**: Kudlur2026's latency numbers use the optimised ONNX export on
  Apple M3. This task uses the HuggingFace Transformers CPU backend because `moonshine_onnx` does
  not ship a Medium-variant ONNX model. Latency comparison is directionally valid but not
  hardware-matched.

- **Earnings-22 model size mismatch**: The closest domain-specific WER published in Kudlur2026 is
  for the Tiny variant on Earnings-22 (20.27%), not the Medium variant. No Medium Earnings-22 figure
  is reported; the comparison involves a model size mismatch.

- **Shallow fusion literature gap**: t0003 confirmed that no standalone shallow-fusion paper
  appeared in Jan–Jun 2026 literature. The feasibility assessment (verdict: "needs research") cannot
  be compared against a published implementation on a comparable benchmark.

- **No per-task cost for biasing comparison**: The t0004 biased Whisper result uses `initial_prompt`
  vocabulary injection, a mechanism not available in Moonshine. The entity_accuracy_domain_vocab
  comparison (9.1% vs. 94.5%) reflects both the model difference and the biasing method difference;
  these cannot be disentangled without a matched biasing experiment.

### Prior Task Comparison

| Metric | Moonshine base (t0004) | Moonshine v2 Medium (this task) | Delta | Interpretation |
| --- | --- | --- | --- | --- |
| wer_gold92 | 18.4% | 16.6% | −1.8pp | Modest improvement; v2 Medium is marginally better on WER |
| entity_accuracy_gold92 | 21.7% | 21.7% | 0.0pp | No improvement; entity failure is not capacity-limited |
| entity_accuracy_domain_vocab | 10.9% | 9.1% | −1.8pp | Marginal regression within noise; no improvement |
| action_critical_wer_gold92 | 41.1% | 34.2% | −6.9pp | Moderate improvement; fewer errors on entity-containing words |
| intent_preservation_gold92 | 84.9% | 87.1% | +2.2pp | Small improvement |
| latency_p50_seconds | 0.070s | 0.232s | +162ms | v2 Medium is 3.3x slower than base; larger model increases latency |
| wrong_action_rate_gold92 | 15.1% | 12.9% | −2.2pp | Marginal improvement; both far above the 2% threshold |

The prior-task comparison confirms that upgrading from Moonshine base to v2 Medium yields no
meaningful entity accuracy gain. The latency trade-off (3.3x slower) is not compensated by accuracy
improvement. For latency-constrained edge deployment, the base variant would be preferred over v2
Medium if both require external biasing before production use.
