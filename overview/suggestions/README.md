# Research Suggestions Backlog

28 suggestions **23 open** (5 high, 16 medium, 2 low), **5 closed**.

**Browse by view**: By category: [`audio-datasets`](by-category/audio-datasets.md),
[`commercial-apis`](by-category/commercial-apis.md),
[`confidence-routing`](by-category/confidence-routing.md),
[`entity-correction`](by-category/entity-correction.md),
[`latency-profiling`](by-category/latency-profiling.md),
[`stt-evaluation`](by-category/stt-evaluation.md),
[`whisper-finetuning`](by-category/whisper-finetuning.md); [By date
added](by-date-added/README.md)

---

## High Priority

<details>
<summary>📂 <strong>Annotate gold-92 with entity span offsets to enable E-WER and
Slot F1</strong> (S-0003-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-03` |
| **Kind** | dataset |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`audio-datasets`](../../meta/categories/audio-datasets/) |

Add entity-offset markup to gold-92 ground-truth transcripts, tagging brand names, product
names, and SKUs with character-level span annotations. This unblocks computation of E-WER
(required to evaluate RECOVER) and Slot F1 (required to evaluate Zheng2026 selective span
editing). Without entity spans, only substring-match and overall WER can be reported on
gold-92. The annotation should cover all 93 clips and follow a schema compatible with the
Contextual Earnings-22 format (Durmus2026) to enable cross-benchmark comparison. Recommended
task types: audio-dataset-curation.

</details>

<details>
<summary>🔧 <strong>LLM post-correction layer for entity normalization on Whisper
transcripts</strong> (S-0002-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-03` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

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
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2603.16411`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.16411/) |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

Implement the RECOVER pipeline (Kumar2026) on Whisper Turbo: enable beam-width-5 decoding,
collect top-5 hypotheses, and use GPT-4o LLM-Select to choose the most entity-accurate
hypothesis. Measure entity accuracy (substring match), overall WER, and end-to-end latency on
all 93 gold-92 clips. RECOVER reported 33-35% relative E-WER reduction on Earnings-21, the
closest public proxy for ecommerce entities. This is the highest expected gain from a
no-retraining method in the survey. Recommended task types: post-correction-experiment,
stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Run Deepgram Nova-2 baseline on gold-92 to complete REQ-1 and
paired significance test</strong> (S-0002-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`commercial-apis`](../../meta/categories/commercial-apis/) |

The t0002 baseline evaluation could not run Deepgram Nova-2 because DEEPGRAM_API_KEY was
unavailable. This blocked REQ-1, REQ-5 (paired significance test), REQ-9 (Deepgram predictions
asset), and the production comparator column in all results tables. Cost is approximately
$0.09 for 93 clips. A dedicated task should obtain the key from the team vault, run Deepgram
Nova-2 with nova-2 model and default settings on all 93 gold-92 clips, compute all five
registered metrics with BCa CIs, run the paired significance test against whisper-turbo, and
produce the deepgram-nova2-gold92 predictions asset. Recommended task types:
stt-benchmark-run, baseline-evaluation.

</details>

<details>
<summary>🧪 <strong>Vocabulary-biased Whisper inference via STT_INITIAL_PROMPT on
gold-92</strong> (S-0002-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../meta/categories/whisper-finetuning/) |

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
<summary>🧪 <strong>Add Azure Speech Services as a third STT comparison point on
gold-92</strong> (S-0002-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-06` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`commercial-apis`](../../meta/categories/commercial-apis/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

Azure Cognitive Services Speech-to-Text supports custom keyword lists and phrase boosting
natively, making it a strong candidate for domain entity accuracy without fine-tuning. Compare
it against Deepgram Nova-2 and Whisper turbo on gold-92 using all five registered metrics.
Requires AZURE_SPEECH_API_KEY from the team vault. Azure also offers Custom Speech (domain
adaptation) which can be evaluated in a follow-up. Estimated cost: approximately $0.01–$0.05
for 93 clips at standard tier pricing. Recommended task types: stt-benchmark-run,
comparative-analysis.

</details>

<details>
<summary>📊 <strong>Add S2ER (sentence-level semantic error rate) metric to the
project evaluation harness</strong> (S-0003-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-04` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2605.29430`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.29430/) |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`entity-correction`](../../meta/categories/entity-correction/) |

Register and implement the S2ER metric from Jiang2026 in the project's evaluation harness.
S2ER is an LLM-judged metric that better correlates with wrong-action rate than WER: it
collapsed from 19-28% to under 2% over correction turns while WER changed only marginally.
Adding S2ER alongside WER and entity accuracy provides a direct proxy for the project's target
metric of wrong-action rate below 2%. Implementation: add an LLM judge (GPT-4o) call per
utterance that scores semantic equivalence between reference and hypothesis. Recommended task
types: stt-benchmark-run, write-library.

</details>

<details>
<summary>🧪 <strong>Benchmark Moonshine ONNX Medium on gold-92 when UsefulSensors
ships the ONNX export</strong> (S-0008-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`latency-profiling`](../../meta/categories/latency-profiling/) |

t0008 used the HuggingFace Transformers CPU backend because moonshine_onnx does not include a
Medium variant. The ONNX export is expected to be ~30ms faster per clip, which would bring
warmed p50 from 233ms to ~200ms and potentially meet the project latency target. Once
UsefulSensors ships an ONNX Medium model, run it on all 93 gold-92 clips using the same
inference harness as t0008 and compare latency p50/p95/p99 and entity accuracy. Recommended
task types: stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Compare Granite/Paraformer against Deepgram Nova-2 and Azure
Speech on gold-92</strong> (S-0005-07)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-07` |
| **Kind** | experiment |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`commercial-apis`](../../meta/categories/commercial-apis/) |

The survey did not include closed-API baselines (Deepgram Nova-2, Azure Speech Services). Both
support contextual biasing and have lower latency than Whisper. Run a comparative benchmark to
establish whether open-source candidates (Granite, Paraformer) can match or exceed the
accuracy and latency of production-quality closed APIs. This context is critical for
production decision-making if open-source candidates fall short. Azure Speech and Deepgram API
costs are approximately $0.01–$0.10 for 93 clips. Recommended task types: stt-benchmark-run,
comparative-analysis.

</details>

<details>
<summary>🧪 <strong>Domain fine-tuning of Whisper turbo on Rezolve investor-relations
audio</strong> (S-0002-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-04` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`whisper-finetuning`](../../meta/categories/whisper-finetuning/), [`audio-datasets`](../../meta/categories/audio-datasets/) |

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
<summary>🧪 <strong>Evaluate fallback strategy if top candidates underperform on
accented English</strong> (S-0005-08)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-08` |
| **Kind** | experiment |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`entity-correction`](../../meta/categories/entity-correction/) |

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
<summary>📂 <strong>Expand gold-92 benchmark with more production clips and fix
annotation inconsistencies</strong> (S-0002-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-05` |
| **Kind** | dataset |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`audio-datasets`](../../meta/categories/audio-datasets/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

Three findings motivate benchmark expansion: (1) the 34-clip production subset scores only
8.8% entity accuracy but drives all business-critical decisions; a larger production sample
would tighten BCa confidence intervals and reduce the risk of outlier clips dominating
results; (2) at least three clips (Examples 10, 13, 14) show verbatim transcript matches
scoring 0 entity accuracy due to annotation normalisation mismatches — the annotation schema
needs an audit; (3) clip error_en_0005 has Cyrillic ground truth indicating upstream data
quality issues. The expanded benchmark should also apply blockwise bootstrap by speaker for
the clean_voices subset as recommended by Liu2020. Recommended task types:
audio-dataset-curation, data-analysis.

</details>

<details>
<summary>📊 <strong>Implement intent classification metric to replace span-presence
proxy</strong> (S-0002-07)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-07` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`confidence-routing`](../../meta/categories/confidence-routing/) |

The current intent_preservation_gold92 metric uses a span-presence heuristic that is
over-estimated: 'Resolve' satisfies 'Rezolve' after normalisation, inflating the 90.3% figure.
A proper intent classifier should distinguish entity substitution that changes action target
(e.g., wrong company name) from substitution that preserves action type (e.g., generic query
intent). This is needed to make intent_preservation_gold92 meaningful for the
confidence-routing policy (wrong_action_rate_gold92 goal: <2%). Implement as a lightweight
rule-based or LLM-based classifier and re-evaluate on gold-92. Recommended task types:
write-library, experiment-run.

</details>

<details>
<summary>🔧 <strong>Implement Novitasari2026 common-word cue injection as a
zero-latency biasing add-on</strong> (S-0003-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-05` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2604.12398`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/) |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`latency-profiling`](../../meta/categories/latency-profiling/) |

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
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

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
<summary>📊 <strong>Measure end-to-end latency of RECOVER and Ron2026 pipelines on
Rezolve infrastructure</strong> (S-0003-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-06` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../meta/categories/latency-profiling/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

The survey found that latency estimates for both RECOVER (~+100-200ms) and Ron2026 (~550-650ms
total) are extrapolations from known Whisper Turbo inference speed and GPT-4o API latency, not
empirical measurements. Before confirming either method fits the 800ms p50 budget, measure
actual pipeline latency on Rezolve's production infrastructure at p50 and p95. This is a
prerequisite for any production deployment decision. If GPT-4o API latency exceeds the budget,
evaluate a local 7B model substitute for the LLM-Select step. Recommended task types:
latency-profiling, experiment-run.

</details>

<details>
<summary>🧪 <strong>Moonshine model-size ablation: benchmark tiny, base, and large
variants on gold-92 entity accuracy</strong> (S-0008-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`latency-profiling`](../../meta/categories/latency-profiling/) |

t0008 found that Moonshine v2 Medium (266M params) achieves exactly the same
entity_accuracy_gold92 (21.7%) and entity_accuracy_domain_vocab (9.1%) as the base model (38M
params) from t0004. This contradicts the assumption that a larger model would improve entity
recall. A controlled ablation across all published Moonshine variants (tiny, base,
streaming-medium, and any large variant) would confirm whether the entity accuracy plateau is
a training-distribution gap or a tokenizer/decoder limit, and would determine the optimal
model size for latency/accuracy trade-off before investing in S-0005-04 shallow fusion work.
Recommended task types: stt-benchmark-run, comparative-analysis.

</details>

<details>
<summary>📂 <strong>Preprocess Rezolve investor-relations transcript corpus for KenLM
domain language model training</strong> (S-0008-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-03` |
| **Kind** | dataset |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`audio-datasets`](../../meta/categories/audio-datasets/), [`entity-correction`](../../meta/categories/entity-correction/) |

The t0008 shallow fusion feasibility assessment (Approach 1) identified that implementing
log-linear N-best rescoring for Moonshine requires a domain LM trained on Rezolve
investor-relations text. The corpus exists (annual reports, investor presentations, brainpowa
session transcripts) but is noted as not yet preprocessed. Curate and clean this corpus into a
plaintext format suitable for KenLM trigram training, covering at minimum the 31-term domain
vocabulary and surrounding IR context. Estimated size: 50k–500k tokens. This unblocks both the
Moonshine shallow fusion task (S-0005-04) and any future domain adaptation work. Recommended
task types: audio-dataset-curation.

</details>

<details>
<summary>📊 <strong>Quantify entity accuracy gain vs. integration effort for Granite
vs. Paraformer</strong> (S-0005-09)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-09` |
| **Kind** | evaluation |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

After benchmarking both Granite and Paraformer on gold-92 (suggestions S-0005-01, S-0005-02),
create a cost-benefit matrix: entity accuracy gain (%) vs. integration complexity (days),
latency under load (ms), and VRAM (GB). Use this to make a final production selection. If
Granite delivers +12% entity accuracy with 2-day integration and Paraformer delivers +10% with
4-day integration, the decision favors Granite. This task synthesizes the experimental
findings into a decision frame for the team. Recommended task types: comparative-analysis,
data-analysis.

</details>

<details>
<summary>📊 <strong>Stratify gold-92 evaluation by speaker accent to quantify
accent-induced entity errors</strong> (S-0003-07)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-07` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2603.25727`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/) |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`audio-datasets`](../../meta/categories/audio-datasets/) |

WildASR (Tay2026) confirmed that model robustness does not transfer across accent conditions
and that ASR systems hallucinate plausible but unspoken content under degraded inputs. Gold-92
contains six non-native English speaker clips, making accent-induced entity errors a direct
project risk. Stratify all gold-92 evaluation results by speaker accent group and compare
entity accuracy between native and non-native speakers. If accent is the primary driver of
entity errors rather than lexical ambiguity, post-correction methods (RECOVER, Ron2026) will
have limited effect and ASR-stage improvements should be prioritized instead. Recommended task
types: data-analysis, stt-benchmark-run.

</details>

<details>
<summary>📊 <strong>Test entity-biasing mechanisms at scale (1,000+ entity
vocabulary)</strong> (S-0005-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-06` |
| **Kind** | evaluation |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`latency-profiling`](../../meta/categories/latency-profiling/) |

The survey reports contextual biasing results on 50–1,800 entity lists. Rezolve's product
catalog scales to 10,000+ SKUs. Test whether Granite 4.1 keyword biasing and Paraformer
deep-biasing maintain performance (latency, entity accuracy) when biasing context grows from
1,800 to 10,000 entities. Measure latency scaling curve and F1 degradation if any. If latency
exceeds budget at production scale, design a retrieval-based filtering pre-pass (e.g.,
retrieve top-100 entities relevant to the speaker/context before biasing) to cap the active
biasing vocabulary. Recommended task types: experiment-run, data-analysis.

</details>

## Low Priority

<details>
<summary>🔧 <strong>Implement quantized variants of Granite/Paraformer for edge and
latency optimization</strong> (S-0005-10)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-10` |
| **Kind** | technique |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../meta/categories/latency-profiling/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

If benchmarking shows that Granite or Paraformer meet accuracy targets but exceed VRAM or
latency budgets at scale, implement quantized (int8/float16) variants using ONNX, TensorRT, or
vLLM to reduce model size and improve inference speed. Moonshine already ships as a
245M-parameter model optimized for edge; quantization could reduce Granite (2B) and Paraformer
(varies) to similar footprints. Measure quantization impact on entity accuracy and latency. If
quantization preserves accuracy within 1–2% while halving latency, quantized variants become
the recommended production deployment. Recommended task types: experiment-run, build-model.

</details>

<details>
<summary>🔧 <strong>Monitor LOGIC (Wang2026) arXiv reappearance for constant-time
logit-space biasing</strong> (S-0003-08)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-08` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2601.15397`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.15397/) |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

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
<summary>✅ <s>Benchmark FunASR Paraformer with contextual biasing on gold-92</s> —
covered by <a
href="../../tasks/t0010_funasr_paraformer_benchmark/"><code>t0010_funasr_paraformer_benchmark</code></a>
(S-0005-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

FunASR Paraformer (SenseVoice/SeACo variant) achieves 1.8% Entity WER (EWER) with
shallow-fusion contextual biasing on ~1,800 entities, and Apache 2.0 license. As the secondary
candidate from the survey, benchmark it on gold-92 to validate entity accuracy and measure
latency under concurrent load. Test both shallow-fusion (low-latency) and deep-biasing
variants if available. If TTFT <200ms achievable and entity accuracy competitive with Granite,
Paraformer becomes a strong alternative. Also measure integration complexity vs. Granite to
inform production selection. Recommended task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary>✅ <s>Benchmark IBM Granite Speech 4.1 2B on gold-92 for entity accuracy and
latency</s> — covered by <a
href="../../tasks/t0007_ibm_granite_4_1_benchmark/"><code>t0007_ibm_granite_4_1_benchmark</code></a>
(S-0005-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

IBM Granite Speech 4.1 2B ranks #1 on the Open ASR Leaderboard (5.33% WER) and includes native
keyword biasing with published F1 metrics. Run a controlled benchmark on gold-92 against the
current Whisper turbo + initial_prompt baseline. Measure entity accuracy (substring match),
overall WER, keyword recall (F1), and end-to-end latency on both p50 and p95 percentiles. If
entity accuracy improves >10% and latency remains <800ms p50, Granite becomes the recommended
primary candidate for production integration. If entity biasing falls short, test variant
configurations (e.g., larger biasing context window). Recommended task types:
stt-benchmark-run, experiment-run.

</details>

<details>
<summary>✅ <s>Integrate IBM Granite Speech 4.1 into brainpowa STTAdapter brick
(async wrapper)</s> — covered by <a
href="../../tasks/t0014_granite_short_clip_robustness/"><code>t0014_granite_short_clip_robustness</code></a>
(S-0005-03)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-03` |
| **Kind** | technique |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

Create a production-ready Python async wrapper for IBM Granite Speech 4.1 that implements the
STTAdapter Protocol (async transcribe, optional async transcribe_stream, PCM-16 mono input
handling). Start from the Hugging Face Transformers API and reference Granite's
keyword-biasing generate() kwargs. Test end-to-end with Rezolve's context injection
infrastructure and validate that biasing context can be programmatically updated per session.
Integration effort estimated at 2–3 days. Deliverable: new brick class in
`src/brainpowa_realtime_api/pipeline/stt/granite_adapter.py` with unit tests and latency
profiling. Recommended task types: infrastructure-setup, write-library.

</details>

<details>
<summary>✅ <s>Profile Granite 4.1, Paraformer, and Whisper latency under concurrent
request load</s> — covered by <a
href="../../tasks/t0011_streaming_stt_benchmark/"><code>t0011_streaming_stt_benchmark</code></a>
(S-0005-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-05` |
| **Kind** | evaluation |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../meta/categories/latency-profiling/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

The survey reports single-request latencies; production voice-to-action pipelines receive
concurrent requests. Profile all three candidates (Granite, Paraformer, Whisper turbo) on
Rezolve's production infrastructure under 10, 50, and 100 concurrent sessions. Measure TTFT
(time-to-first-token), total latency, p50/p95/p99 percentiles, and VRAM utilization at each
concurrency level. This determines whether Granite/Paraformer can sustain the latency budget
under realistic load, and whether GPU memory becomes the bottleneck. If latency degrades
significantly at >10 concurrent sessions, batch-processing or model quantization strategies
become necessary. Recommended task types: experiment-run, data-analysis.

</details>

<details>
<summary>✅ <s>Prototype Ron2026 initial_prompt multi-agent pipeline on gold-92</s> —
covered by <a
href="../../tasks/t0004_vocabulary_biasing_experiment/"><code>t0004_vocabulary_biasing_experiment</code></a>
(S-0003-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2602.18966`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/) |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |

Implement the six-agent LLM pipeline from Ron2026 against Whisper Turbo on gold-92. The
pipeline processes a first-pass transcript to extract topic labels, named entities, and domain
jargon, assembles a context prompt (224 tokens max), and feeds it into a second Whisper
decoding pass via the initial_prompt parameter. Seed the NER agent with Rezolve's
brand/product catalog. Measure entity accuracy and latency on all 93 clips. Ron2026 reported
17% relative WER reduction on entity-dense NBA commentary with zero model retraining.
Recommended task types: post-correction-experiment, stt-benchmark-run.

</details>
