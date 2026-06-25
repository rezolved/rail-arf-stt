# Suggestions: `entity-correction`

9 suggestion(s) in category [`entity-correction`](../../../meta/categories/entity-correction/)
**8 open** (2 high, 5 medium, 1 low), **1 closed**.

[Back to all suggestions](../README.md)

---

## High Priority

<details>
<summary>🔧 <strong>LLM post-correction layer for entity normalization on Whisper
transcripts</strong> (S-0002-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-03` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Build a lightweight LLM post-correction pass that takes a Whisper transcript and a domain
entity glossary (Rezolve, brainpowa, product names, IR terms) and corrects entity-span errors
without rewriting the full transcript. The baseline shows entity accuracy of 25.2% overall and
8.8% on production clips — the majority of failures are vocabulary substitutions
(Rezolve→Hizol, Rezolve→Resolve) that a prompted LLM with glossary access could correct
cheaply. Target: measure entity accuracy gain and added latency overhead vs the 800 ms p50
budget. Recommended task types: post-correction-experiment, experiment-run.

</details>

<details>
<summary>🧪 <strong>Prototype RECOVER N-best + LLM-Select on gold-92</strong>
(S-0003-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2603.16411`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.16411/) |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Implement the RECOVER pipeline (Kumar2026) on Whisper Turbo: enable beam-width-5 decoding,
collect top-5 hypotheses, and use GPT-4o LLM-Select to choose the most entity-accurate
hypothesis. Measure entity accuracy (substring match), overall WER, and end-to-end latency on
all 93 gold-92 clips. RECOVER reported 33-35% relative E-WER reduction on Earnings-21, the
closest public proxy for ecommerce entities. This is the highest expected gain from a
no-retraining method in the survey. Recommended task types: post-correction-experiment,
stt-benchmark-run.

</details>

## Medium Priority

<details>
<summary>📊 <strong>Add S2ER (sentence-level semantic error rate) metric to the
project evaluation harness</strong> (S-0003-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-04` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2605.29430`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.29430/) |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`entity-correction`](../../../meta/categories/entity-correction/) |

Register and implement the S2ER metric from Jiang2026 in the project's evaluation harness.
S2ER is an LLM-judged metric that better correlates with wrong-action rate than WER: it
collapsed from 19-28% to under 2% over correction turns while WER changed only marginally.
Adding S2ER alongside WER and entity accuracy provides a direct proxy for the project's target
metric of wrong-action rate below 2%. Implementation: add an LLM judge (GPT-4o) call per
utterance that scores semantic equivalence between reference and hypothesis. Recommended task
types: stt-benchmark-run, write-library.

</details>

<details>
<summary>🧪 <strong>Evaluate fallback strategy if top candidates underperform on
accented English</strong> (S-0005-08)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-08` |
| **Kind** | experiment |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`entity-correction`](../../../meta/categories/entity-correction/) |

Gold-92 is weighted toward investor-relations domain (accented English, financial jargon). The
survey reports that real-world performance on noisy/accented audio degrades 3–7x vs. clean
benchmarks. If Granite and Paraformer achieve <5% WER on LibriSpeech but >15% entity WER on
gold-92 accented clips, design a fallback strategy: (1) ensemble hybrid (fast transducer + LLM
correction), (2) domain fine-tuning Granite/Paraformer on accented audio samples, or (3)
pre-emphasis + speech-enhancement preprocessing before STT. Prototype and benchmark the top 2
fallback approaches on gold-92. Recommended task types: experiment-run,
post-correction-experiment.

</details>

<details>
<summary>🔧 <strong>Implement Novitasari2026 common-word cue injection as a
zero-latency biasing add-on</strong> (S-0003-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-05` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2604.12398`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/) |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

Implement the common-word cue approach from Novitasari2026 as a pre-processing step on top of
Rezolve's existing dynamic context injection. The method maps non-standard brand names and
SKUs to phonetically similar common-word anchors, adding them to the bias list without G2P.
Novitasari2026 reported 16.3% reduction in bias-word errors with zero added latency and no
model retraining, and the method is additive to any existing biasing technique. Evaluate on
gold-92 entity accuracy and confirm zero latency impact. Recommended task types:
post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>🔧 <strong>Implement shallow-fusion contextual biasing adapter for Moonshine
v2</strong> (S-0005-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-04` |
| **Kind** | technique |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Moonshine v2 achieves 5.3% WER with 258ms latency and CPU-only requirements, enabling edge
deployment. However, it lacks native contextual biasing. Implement a post-processing
shallow-fusion adapter that rescores Moonshine's top-3 beam hypotheses against a domain
vocabulary list (Rezolve, brainpowa, product names, SKUs) and selects the hypothesis with
highest entity-overlap score. Estimate +2–5ms latency. Evaluate on gold-92: measure whether
external biasing + Moonshine latency (263ms+) remains under 800ms total voice-to-action
budget, and whether entity accuracy is competitive with Granite. If successful, Moonshine
becomes a viable edge-deployment alternative. Recommended task types:
post-correction-experiment, write-library.

</details>

<details>
<summary>📂 <strong>Preprocess Rezolve investor-relations transcript corpus for KenLM
domain language model training</strong> (S-0008-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-03` |
| **Kind** | dataset |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`audio-datasets`](../../../meta/categories/audio-datasets/), [`entity-correction`](../../../meta/categories/entity-correction/) |

The t0008 shallow fusion feasibility assessment (Approach 1) identified that implementing
log-linear N-best rescoring for Moonshine requires a domain LM trained on Rezolve
investor-relations text. The corpus exists (annual reports, investor presentations, brainpowa
session transcripts) but is noted as not yet preprocessed. Curate and clean this corpus into a
plaintext format suitable for KenLM trigram training, covering at minimum the 31-term domain
vocabulary and surrounding IR context. Estimated size: 50k–500k tokens. This unblocks both the
Moonshine shallow fusion task (S-0005-04) and any future domain adaptation work. Recommended
task types: audio-dataset-curation.

</details>

## Low Priority

<details>
<summary>🔧 <strong>Monitor LOGIC (Wang2026) arXiv reappearance for constant-time
logit-space biasing</strong> (S-0003-08)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-08` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2601.15397`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.15397/) |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

The LOGIC paper (Wang2026, logit-space entity biasing with constant-time complexity, 9%
relative Entity WER reduction) was withdrawn from arXiv in February 2026 for institutional
approval compliance. It cannot be implemented until it reappears at a conference venue. Set up
monitoring for LOGIC reappearance at Interspeech 2026 or ICASSP 2026 proceedings. Once
republished, LOGIC's constant-time biasing approach directly addresses context window
saturation at catalog scale (10,000+ entries) without the retrieval infrastructure required by
BR-ASR. Recommended task types: internet-research.

</details>

## Closed

<details>
<summary>✅ <s>Prototype Ron2026 initial_prompt multi-agent pipeline on gold-92</s> —
covered by <a
href="../../../tasks/t0004_vocabulary_biasing_experiment/"><code>t0004_vocabulary_biasing_experiment</code></a>
(S-0003-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2602.18966`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/) |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Implement the six-agent LLM pipeline from Ron2026 against Whisper Turbo on gold-92. The
pipeline processes a first-pass transcript to extract topic labels, named entities, and domain
jargon, assembles a context prompt (224 tokens max), and feeds it into a second Whisper
decoding pass via the initial_prompt parameter. Seed the NER agent with Rezolve's
brand/product catalog. Measure entity accuracy and latency on all 93 clips. Ron2026 reported
17% relative WER reduction on entity-dense NBA commentary with zero model retraining.
Recommended task types: post-correction-experiment, stt-benchmark-run.

</details>
