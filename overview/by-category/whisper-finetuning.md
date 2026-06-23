# Category: Whisper Fine-Tuning

Domain-adapted fine-tuning of Whisper-class ASR models on Rezolve production audio to improve
entity accuracy.

[Back to Dashboard](../README.md)

**Detail pages**: [Papers (3)](../papers/by-category/whisper-finetuning.md) | [Suggestions
(2)](../suggestions/by-category/whisper-finetuning.md) | [Predictions
(5)](../predictions/by-category/whisper-finetuning.md)

---

## Papers (3)

<details>
<summary>📝 <strong>Whisper: Courtside Edition — Multi-Agent LLM Pipeline for
Domain-Specific ASR via Context Generation</strong> — Ron et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2602.18966` |
| **Authors** | Yonathan Ron, Shiri Gilboa, Tammuz Dubnov |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2602.18966` |
| **URL** | https://arxiv.org/abs/2602.18966 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/summary.md) |

Ron et al. demonstrate that Whisper's initial_prompt parameter can be systematically exploited
for domain-specific entity recognition without model retraining. A six-agent LLM pipeline
extracts domain signals from Whisper's preliminary transcript and constructs a compact prompt
that guides the decoder toward rare entity recognition.

The pipeline processes topic classification, NER with fuzzy matching, jargon extraction, and a
decision filter that prevents over-prompting. Evaluation on 421 NBA basketball commentary
segments (dense proper nouns and technical jargon) shows a **17.0% relative WER reduction**
(0.217 → 0.180, p < 0.001), improving **40.1%** of segments while degrading only **7.1%**.

The approach is architecturally straightforward and requires only Whisper API access. The
decision filter is the key practical contribution: it prevents Whisper's 224-token context
window from being filled with low-confidence candidates that degrade performance. Error
analysis confirms that the gains are entity-driven (35% names, 28% jargon).

For Rezolve, this approach is the most immediately deployable: it leverages the existing
Whisper Turbo checkpoint and adds an LLM-based prompt generation step with no model training.
The NBA domain closely parallels ecommerce in entity density and proper noun challenges. The
main engineering work is tuning the fuzzy matching threshold for Rezolve's brand/product
vocabulary and ensuring the multi-agent latency fits within the 800ms p50 budget.

</details>

<details>
<summary>🏤 <strong>WhisperNER: Unified Open Named Entity and Speech
Recognition</strong> — Ayache et al., 2024</summary>

| Field | Value |
|---|---|
| **ID** | `10.1109_ASRU65441.2025.11434797` |
| **Authors** | Gil Ayache, Menachem Pirchi, Aviv Navon, Aviv Shamsian, Gill Hetz, Joseph Keshet |
| **Venue** | 2025 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU) (conference) |
| **DOI** | `10.1109/ASRU65441.2025.11434797` |
| **URL** | https://arxiv.org/abs/2409.08107 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../meta/categories/whisper-finetuning/), [`entity-correction`](../../meta/categories/entity-correction/) |
| **Added by** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../tasks/t0002_baseline_evaluation/assets/paper/10.1109_ASRU65441.2025.11434797/summary.md) |

Ayache et al. propose WhisperNER to solve error propagation in pipeline-based speech-NLP
systems. In standard ASR+NER pipelines, transcription errors in the first stage degrade entity
recognition in the second stage. The paper also identifies a key gap: existing end-to- end
NER-from-speech models support only fixed, closed entity sets, limiting their applicability to
dynamic or domain-specific scenarios where entity vocabularies change over time.

WhisperNER extends Whisper large-v2 by conditioning the decoder on a user-supplied list of
entity type labels at inference time. The model is trained on 350K samples from the NuNER
synthetic dataset augmented with TTS-generated audio, spanning 1.8M unique entity types.
Training incorporates negative entity sampling (~66% negative types per example) and entity
type dropout to reduce hallucination. Only the decoder is updated; the Whisper encoder is
frozen. A scalar logit bias on the entity start token provides inference-time precision-recall
control without retraining.

On zero-shot open-type NER, WhisperNER achieves **53.53 F1** averaged across VoxPopuli-NER,
LibriSpeech-NER, and Fleurs-NER, outperforming the best pipeline baseline (GLiNER at **52.29
F1**) while adding no parameters over Whisper large-v2. Pipeline baselines add 248M-459M NLP
parameters on top of the same Whisper backbone. On supervised fine- tuning, WhisperNER reaches
**81.35 F1** on MIT-Movie at **2.31% WER**, outperforming all baselines on both metrics
simultaneously. The WER cost of NER integration is modest at approximately +0.9 pp on
VoxPopuli.

For the Rezolve STT project, WhisperNER is the most directly relevant paper in the corpus: it
directly targets the entity accuracy problem by integrating NER into ASR, uses the same
Whisper architecture targeted for fine-tuning in this project, and its open-type prompt
interface allows Rezolve-specific entities to be targeted without retraining. The logit-bias
precision-recall control maps onto the confidence-routing framework. The main open question is
performance on gold-92 (accented English production audio), given the known acoustic mismatch
from synthetic TTS training data. A baseline evaluation of the released WhisperNER model on
gold-92 should be part of t0002_baseline_evaluation.

</details>

<details>
<summary>📝 <strong>Robust Speech Recognition via Large-Scale Weak
Supervision</strong> — Radford et al., 2022</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2212.04356` |
| **Authors** | Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2212.04356` |
| **URL** | https://arxiv.org/abs/2212.04356 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../tasks/t0002_baseline_evaluation/assets/paper/10.48550_arXiv.2212.04356/summary.md) |

Radford et al. present Whisper, a speech recognition system trained on 680,000 hours of weakly
supervised audio-transcript pairs scraped from the internet. The central research question is
whether scaling weak supervision — using noisy but abundant internet data rather than
expensive human-validated corpora — can match or surpass fully supervised approaches while
achieving substantially better real-world robustness. The work is motivated by the observation
that prior state-of-the-art models trained on LibriSpeech are effectively measuring
in-distribution generalization, not the out-of-distribution robustness needed for production
deployment.

The approach uses a standard encoder-decoder Transformer trained end-to-end on 30-second audio
segments with a multitask format: all tasks (transcription, translation, language ID, VAD,
timestamp alignment) are encoded as decoder token sequences, allowing a single model to
replace multiple pipeline stages. Training uses AdamW with linear LR decay for approximately
2-3 passes over the dataset without data augmentation, relying on dataset diversity for
robustness. Five model sizes are released (39M–1.55B parameters). A text normalizer and
long-form decoding heuristics are developed as essential practical components.

The key findings are that Whisper Large V2 achieves **55.2%** average relative error reduction
over the best comparable supervised model on 13 OOD datasets despite similar LibriSpeech
performance, and its transcription quality approaches professional human transcribers on
Kincaid46 (Whisper **8.81%** WER vs. best human service **7.61%**). For translation, Whisper
achieves **29.1 BLEU** on CoVoST2 zero-shot, a new state of the art. A strong data scaling law
is identified: WER halves for every 16× increase in per-language training hours (log-log R² =
0.83 on Fleurs). Multitask and multilingual training provides positive transfer at large model
sizes.

For this project, Whisper Large V2 is the open-source baseline to benchmark against production
Deepgram on gold-92. The paper directly supports the research roadmap: fine-tuning Whisper on
Rezolve production audio is the most direct path to improving entity accuracy on
investor-relations and ecommerce terms. The custom vocabulary prompting mechanism is
immediately actionable for injecting brand names and product entities. The model size family
gives a latency-accuracy trade-off ladder to explore within the 800 ms p50 constraint.

</details>

## Tasks (2)

| # | Task | Status | Completed |
|---|------|--------|-----------|
| 0002 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) | completed | 2026-06-23 10:25 |
| 0003 | [Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) | completed | 2026-06-23 09:25 |

## Answers (0)

No answers in this category.

## Suggestions (2 open, 0 closed)

<details>
<summary>🧪 <strong>Vocabulary-biased Whisper inference via STT_INITIAL_PROMPT on
gold-92</strong> (S-0002-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

Run Whisper turbo on gold-92 with a domain vocabulary prompt injected via STT_INITIAL_PROMPT
(e.g., 'Rezolve, brainpowa, Rezolve AI, Shopify Plus, Salesforce Commerce Cloud, Adobe
Commerce, AI Foundry'). The baseline showed 'Rezolve' is systematically transcribed as 'Hizol'
or 'Resolve' — a pure vocabulary gap. Vocabulary biasing via initial_prompt requires zero
training and zero API cost. Measure entity accuracy on production clips specifically
(baseline: 8.8%) and compare with paired BCa test against the whisper-turbo baseline.
Recommended task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary>🧪 <strong>Domain fine-tuning of Whisper turbo on Rezolve investor-relations
audio</strong> (S-0002-04)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

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
