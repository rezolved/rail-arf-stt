# Metrics (7)

## 📊 ratio (3)

<details>
<summary>📊 <strong>Action-Critical WER (gold-92)</strong>
(<code>action_critical_wer_gold92</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `action_critical_wer_gold92` |
| **Unit** | ratio |
| **Value type** | float |
| **Datasets** | — |

Word Error Rate restricted to action-critical token spans in the gold-92 benchmark. Computed
as (S+D+I) / N_critical where N_critical is the total number of reference words in annotated
critical spans.

</details>

<details>
<summary>📊 <strong>Word Error Rate (gold-92)</strong> (<code>wer_gold92</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `wer_gold92` |
| **Unit** | ratio |
| **Value type** | float |
| **Datasets** | — |

Full-transcript Word Error Rate on the gold-92 benchmark. Used primarily to detect general-WER
regression after domain fine-tuning. Computed over all reference words, not restricted to
critical spans.

</details>

<details>
<summary>📊 <strong>Wrong Action Rate (gold-92)</strong>
(<code>wrong_action_rate_gold92</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `wrong_action_rate_gold92` |
| **Unit** | ratio |
| **Value type** | float |
| **Datasets** | — |

Fraction of gold-92 utterances where the routing policy emits a confident action that differs
from the ground-truth action. Measures the false-confidence failure mode; success threshold is
below 2%.

</details>

## ✅ accuracy (3)

<details>
<summary>✅ <strong>Entity Accuracy — Domain Vocabulary</strong>
(<code>entity_accuracy_domain_vocab</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `entity_accuracy_domain_vocab` |
| **Unit** | accuracy |
| **Value type** | float |
| **Datasets** | — |

Entity accuracy computed only over the 31 domain-specific terms (brand names, product names,
person names) from the Rezolve vocabulary list that appear in gold-92 ground truth. A term is
correct if it appears verbatim in the predicted transcript after normalisation.

</details>

<details>
<summary>✅ <strong>Entity Accuracy (gold-92)</strong>
(<code>entity_accuracy_gold92</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `entity_accuracy_gold92` |
| **Unit** | accuracy |
| **Value type** | float |
| **Datasets** | — |

Accuracy on action-critical entity spans (brand names, product lines, SKUs, IR terms) in the
gold-92 benchmark. A span is correct if the predicted text exactly matches the ground-truth
annotation after normalisation.

</details>

<details>
<summary>✅ <strong>Intent Preservation (gold-92)</strong>
(<code>intent_preservation_gold92</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `intent_preservation_gold92` |
| **Unit** | accuracy |
| **Value type** | float |
| **Datasets** | — |

Fraction of utterances in gold-92 where the predicted transcript preserves the ground-truth
intent as judged by the intent classifier. An utterance passes if the downstream action type
and primary slot agree with the reference.

</details>

## ⏱️ seconds (1)

<details>
<summary>⏱️ <strong>Latency p50 (seconds)</strong>
(<code>latency_p50_seconds</code>)</summary>

| Field | Value |
|---|---|
| **Key** | `latency_p50_seconds` |
| **Unit** | seconds |
| **Value type** | float |
| **Datasets** | — |

50th-percentile end-to-end voice-to-action latency in seconds, measured from speech-end
detection through STT decoding, optional post-correction, and routing to the first tool-call
dispatch. Success threshold is under 0.8 s.

</details>
