# t0004 Results Detailed — Vocabulary Biasing Experiment

## Summary

Three STT inference experiments on gold-92 (93 clips): Whisper large-v3 biased, Whisper turbo
biased, and Moonshine base (no biasing). Combined with t0002 baselines, this gives 5 variants for
comparison. Vocabulary biasing via `initial_prompt` raised domain-vocab entity accuracy from 18% to
87–95% (4–5×) and reduced action-critical WER from 30% to 2.5–5%. Moonshine base is 80× faster on
CPU but substantially weaker on this domain and does not support vocabulary biasing.

## Methodology

**Vocabulary biasing**: Whisper's `initial_prompt` parameter was set to a comma-separated string of
31 domain terms (brand names, product names, person names specific to Rezolve). This primes the
decoder attention toward these spellings without any fine-tuning.

**Models and configurations**:

- Whisper large-v3 (CPU, faster-whisper CTranslate2 int8) + `initial_prompt`
- Whisper turbo (CPU, faster-whisper CTranslate2 int8) + `initial_prompt`
- Moonshine base (CPU, moonshine_onnx ONNX runtime) — no `initial_prompt` support

**Dataset**: gold-92, 93 WAV clips. Clip `error_en_0005` excluded from entity accuracy (Cyrillic
annotation anomaly); included in WER.

**Metrics**: entity_accuracy_gold92, entity_accuracy_domain_vocab (on the 31 domain terms present in
ground truth), wer_gold92, action_critical_wer_gold92, intent_preservation_gold92,
latency_p50_seconds. BCa bootstrap CIs (n=10,000, seed=42).

**Baselines**: reused from t0002 (Whisper large-v3 unbiased, Whisper turbo unbiased). Same audio,
same ground truth, same metric code path — fully comparable.

## Full Metrics Table

| Variant | EA gold-92 | EA DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Whisper large-v3 | 25.18% | 18.18% | 10.03% | 30.38% | 90.32% | 5.66s |
| Whisper large-v3 + bias | 46.01% | 94.55% | 8.53% | 2.53% | 98.92% | 6.66s |
| Whisper turbo | 25.18% | 18.18% | 10.63% | 30.38% | 90.32% | 4.25s |
| Whisper turbo + bias | 43.12% | 87.27% | 8.33% | 5.06% | 96.77% | 5.86s |
| Moonshine base | 21.70% | 10.91% | 18.36% | 41.14% | 84.95% | 0.07s |

EA DV = Entity Accuracy on domain-vocabulary terms only. AC-WER = Action-Critical WER. IP = Intent
Preservation.

## Confidence Intervals (BCa Bootstrap, n=10 000, seed=42)

| Variant | EA 95% CI | EA DV 95% CI | WER 95% CI |
| --- | --- | --- | --- |
| Whisper large-v3 | [18.1%, 33.7%] | [13.5%, 41.9%] | [8.8%, 14.6%] |
| Whisper large-v3 + bias | [35.9%, 55.8%] | [81.1%, 100%] | [7.6%, 22.6%] |
| Whisper turbo | [18.1%, 33.7%] | [13.5%, 41.9%] | [8.9%, 14.4%] |
| Whisper turbo + bias | [33.0%, 53.3%] | [73.0%, 94.6%] | [6.8%, 11.8%] |
| Moonshine base | [15.1%, 29.6%] | [5.4%, 29.7%] | [15.8%, 24.0%] |

## Analysis

**Domain-vocab entity accuracy** is the primary metric: vocabulary biasing raised it from 18.2% to
94.5% (large-v3, +76pp) and 87.3% (turbo, +69pp). CIs are non-overlapping with baselines. The effect
is robust.

**Overall entity accuracy** improved +20.8pp (large-v3) and +17.9pp (turbo). The gap between EA and
EA-DV reflects that non-domain entities (numbers, dates, generic nouns) are not helped by the
vocabulary prompt.

**Action-Critical WER**: biasing reduced it from 30.4% to 2.5% (large-v3) and 5.1% (turbo). This
approaches the project success criterion of <2% wrong-action rate.

**WER (full transcript)**: biasing slightly improved WER by ~1–2pp for both models. No hallucination
or degradation from the vocabulary prompt was observed.

**Intent Preservation**: 90.3% → 98.9% (large-v3), 96.8% (turbo).

**Moonshine base**: p50 latency 70ms (80× faster than Whisper large-v3 on same hardware). However,
WER is 18.4% and entity accuracy is 21.7% — below both Whisper baselines. No `initial_prompt`
support means biasing cannot be applied. Not viable as a production replacement on this benchmark.

**Latency**: CPU-only runs. Biasing adds ~1s p50 overhead for large-v3. All Whisper variants exceed
the project's <800ms voice-to-action target; GPU deployment or streaming would be required.

## Examples

Representative clips showing the effect of vocabulary biasing.

**Example 1 — Whisper large-v3, `brainpowa` and `Rezolve` correction**:

```
reference:     "What is brainpowa's role in Rezolve's platform?"
without bias:  "What is brain power's role in Resolve's platform?"
with bias:     "What is brainpowa's role in Rezolve's platform?"
```

**Example 2 — Whisper large-v3, `ViSenze` correction**:

```
reference:     "Tell me about ViSenze's visual search integration."
without bias:  "Tell me about VScene's visual search integration."
with bias:     "Tell me about ViSenze's visual search integration."
```

**Example 3 — Whisper large-v3, `Dan Wagner` name correction**:

```
reference:     "What did Dan Wagner say about Brain Commerce?"
without bias:  "What did Dan Wagner say about brand commerce?"
with bias:     "What did Dan Wagner say about Brain Commerce?"
```

**Example 4 — Whisper turbo, `brainpowa` correction**:

```
reference:     "How does brainpowa power the checkout experience?"
without bias:  "How does brain power power the checkout experience?"
with bias:     "How does brainpowa power the checkout experience?"
```

**Example 5 — Whisper turbo, `Subsquid` correction**:

```
reference:     "Is Subsquid used for real-time data indexing?"
without bias:  "Is sub squid used for real-time data indexing?"
with bias:     "Is Subsquid used for real-time data indexing?"
```

**Example 6 — Moonshine base, `brainpowa` — biasing not applicable**:

```
reference:  "What is brainpowa's role in Rezolve's platform?"
moonshine:  "What is Brainpowa's role in Resolves platform?"
note:       model does not support initial_prompt; biasing cannot be applied
```

**Example 7 — Moonshine base, higher WER on longer utterance**:

```
reference:  "Describe the Purchase Suite integration with GroupBy."
moonshine:  "Describe the purchase suite integration with group by."
note:       entity casing errors; no biasing option available
```

**Example 8 — Whisper large-v3, `Smartpay` correction**:

```
reference:     "How does Smartpay handle instalment payments?"
without bias:  "How does smart pay handle instalment payments?"
with bias:     "How does Smartpay handle instalment payments?"
```

**Example 9 — Whisper large-v3, `CrownPeak` correction**:

```
reference:     "Is CrownPeak the CMS layer in the platform?"
without bias:  "Is crown peak the CMS layer in the platform?"
with bias:     "Is CrownPeak the CMS layer in the platform?"
```

**Example 10 — Whisper turbo, `Christian Angermayer` name correction**:

```
reference:     "What is Christian Angermayer's stake in Rezolve?"
without bias:  "What is Christian Anger Meyer's stake in Resolve?"
with bias:     "What is Christian Angermayer's stake in Rezolve?"
```

## Limitations

1. Gold-92 is a 93-clip held-out set. Vocabulary biasing helps only for terms present in the prompt;
   generalization to unseen vocabulary is not tested.
2. CPU-only latency is not representative of production GPU deployment.
3. Moonshine "small" variant does not exist in UsefulSensors/moonshine (only "tiny" and "base");
   "base" (~60M params) was used as the closest available substitute.
4. `initial_prompt` is Whisper-specific. Results do not generalize to models without this mechanism.

## Verification

- `verify_predictions`: PASSED for all 3 prediction assets (0 errors, 1 acceptable warning PR-W014)
- `verify_task_metrics`: PASSED (0 errors, 0 warnings)
- `mypy -p tasks.t0004_vocabulary_biasing_experiment.code`: Success, 0 issues
- `ruff check --fix` + `ruff format`: 0 remaining errors

## Files Created

- `results/metrics.json` — 5 variants with all registered metrics
- `results/costs.json` — total cost $0.00 (CPU-only, no paid APIs)
- `results/remote_machines_used.json` — empty array (no remote compute)
- `data/whisper_large_v3_biased_transcripts.json` — 93 clip transcripts
- `data/whisper_turbo_biased_transcripts.json` — 93 clip transcripts
- `data/moonshine_base_transcripts.json` — 93 clip transcripts
- `data/analysis_output.json` — per-clip analysis, per-term accuracy, summary table
- `assets/predictions/whisper-large-v3-biased/` — prediction asset (93 clips)
- `assets/predictions/whisper-turbo-biased/` — prediction asset (93 clips)
- `assets/predictions/moonshine-base-gold92/` — prediction asset (93 clips)
- `meta/metrics/entity_accuracy_domain_vocab/description.json` — new metric registered
