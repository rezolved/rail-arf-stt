---
spec_version: "2"
predictions_id: "whisper-large-v3-biased"
documented_by_task: "t0004_vocabulary_biasing_experiment"
date_documented: "2026-06-23"
---
# Whisper Large v3 + Vocabulary Bias on Gold-92

## Metadata

* **Name**: Whisper Large v3 + Vocabulary Bias on Gold-92
* **Model**: Whisper Large v3 (~1.5B parameters, faster-whisper INT8)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of Whisper Large v3 (~1.5B parameters, faster-whisper INT8) on the gold-92
benchmark, using vocabulary biasing via Whisper's `initial_prompt` parameter. The experiment is
part of task t0004 which ablates the effect of a 31-term domain vocabulary injected as initial
context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production investor-relations
voice sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases). The vocabulary prompt includes key brand names (Rezolve, brainpowa), product
lines (Brain Commerce, Brain Checkout), partner names (GroupBy, Bluedot, ViSenze), and people
names (Dan Wagner, Arthur Yao, etc.) that appear in the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for this
clip is a normal English sentence; this clip is included in WER computation but excluded from the
aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 (~1.5B parameters, faster-whisper INT8) run locally via `faster-whisper` (CTranslate2 INT8 quantization, CPU
inference, language='en') on Apple M5 Mac. The key difference from the t0002 baseline is the
addition of `initial_prompt` set to the 31-term domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation without
any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn from
three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}],
  "entity_spans_predicted": [{"text": "Rezolve AI", "type": "brand", "found": true}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | 0.4601 |
| wer_gold92 | 0.0853 |
| latency_p50_seconds | 6.66s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that requires
  no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people names
  that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact of
  vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to hallucinate
  terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term vocabulary
covers the key entities in the Rezolve IR domain that appear most frequently in production voice
sessions.

The headline finding (available in `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`)
shows the effect size of vocabulary biasing on entity_accuracy_gold92 and
entity_accuracy_domain_vocab relative to the t0002 baselines. Even small improvements in entity
accuracy are meaningful for
the voice commerce use case, where downstream intent routing depends critically on correct entity
recognition.
