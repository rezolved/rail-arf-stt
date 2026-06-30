# Suggestions: `whisper-finetuning`

3 suggestion(s) in category
[`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) **3 open** (1 high, 2
medium).

[Back to all suggestions](../README.md)

---

## High Priority

<details>
<summary>🧪 <strong>Vocabulary-biased Whisper inference via STT_INITIAL_PROMPT on
gold-92</strong> (S-0002-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |

Run Whisper turbo on gold-92 with a domain vocabulary prompt injected via STT_INITIAL_PROMPT
(e.g., 'Rezolve, brainpowa, Rezolve AI, Shopify Plus, Salesforce Commerce Cloud, Adobe
Commerce, AI Foundry'). The baseline showed 'Rezolve' is systematically transcribed as 'Hizol'
or 'Resolve' — a pure vocabulary gap. Vocabulary biasing via initial_prompt requires zero
training and zero API cost. Measure entity accuracy on production clips specifically
(baseline: 8.8%) and compare with paired BCa test against the whisper-turbo baseline.
Recommended task types: stt-benchmark-run, experiment-run.

</details>

## Medium Priority

<details>
<summary>🧪 <strong>Domain fine-tuning of Whisper turbo on Rezolve investor-relations
audio</strong> (S-0002-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-04` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/), [`audio-datasets`](../../../meta/categories/audio-datasets/) |

Fine-tune Whisper turbo on Rezolve-domain audio (investor-relations sessions, brand names,
product terms) to close the vocabulary gap revealed by the baseline. Both large-v3 and turbo
achieved identical entity accuracy (25.2%), confirming model size is not the bottleneck —
training data distribution is. The WhisperNER supervised fine-tuning comparison showed 81.35
F1 on a domain-specific corpus vs our 25.2%, indicating large headroom. A fine-tuning task
should collect or synthesize domain audio+transcript pairs, run LoRA or full fine-tune on
turbo (pragmatic: 25% lower latency than large-v3 with no accuracy loss), and evaluate on
gold-92 production clips (baseline: 8.8%). Recommended task types: whisper-finetuning-run,
experiment-run.

</details>

<details>
<summary>📊 <strong>Improve Whisper hallucination detection for sub-1 s clips by
refining the BoH reference-word check</strong> (S-0014-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0014-04` |
| **Kind** | evaluation |
| **Date added** | 2026-06-30 |
| **Source task** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |

t0014 found Whisper returns 'Thank you.' on silence and Korean-accented sub-1 s clips —
patterns that match BoH top-30 but were not flagged as hallucinations because the
reference-word overlap check was satisfied by partial gold-92 transcripts. Refining
hallucination detection to use only the actual audio duration's expected spoken content (not
the full clip transcript) would improve precision. This would also yield a cleaner
hallucination rate for comparing Whisper and Granite in production monitoring. Recommended
task types: experiment-run.

</details>
