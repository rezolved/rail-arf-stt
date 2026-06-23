# Suggestions: `stt-evaluation`

13 suggestion(s) in category [`stt-evaluation`](../../../meta/categories/stt-evaluation/) **12
open** (5 high, 6 medium, 1 low), **1 closed**.

[Back to all suggestions](../README.md)

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
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`audio-datasets`](../../../meta/categories/audio-datasets/) |

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

<details>
<summary>🧪 <strong>Run Deepgram Nova-2 baseline on gold-92 to complete REQ-1 and
paired significance test</strong> (S-0002-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`commercial-apis`](../../../meta/categories/commercial-apis/) |

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
<summary>🧪 <strong>Add Azure Speech Services as a third STT comparison point on
gold-92</strong> (S-0002-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-06` |
| **Kind** | experiment |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`commercial-apis`](../../../meta/categories/commercial-apis/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

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
<summary>📂 <strong>Expand gold-92 benchmark with more production clips and fix
annotation inconsistencies</strong> (S-0002-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0002-05` |
| **Kind** | dataset |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`audio-datasets`](../../../meta/categories/audio-datasets/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

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
| **Source task** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`confidence-routing`](../../../meta/categories/confidence-routing/) |

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
<summary>📊 <strong>Measure end-to-end latency of RECOVER and Ron2026 pipelines on
Rezolve infrastructure</strong> (S-0003-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-06` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

The survey found that latency estimates for both RECOVER (~+100-200ms) and Ron2026 (~550-650ms
total) are extrapolations from known Whisper Turbo inference speed and GPT-4o API latency, not
empirical measurements. Before confirming either method fits the 800ms p50 budget, measure
actual pipeline latency on Rezolve's production infrastructure at p50 and p95. This is a
prerequisite for any production deployment decision. If GPT-4o API latency exceeds the budget,
evaluate a local 7B model substitute for the LLM-Select step. Recommended task types:
latency-profiling, experiment-run.

</details>

<details>
<summary>📊 <strong>Stratify gold-92 evaluation by speaker accent to quantify
accent-induced entity errors</strong> (S-0003-07)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-07` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2603.25727`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/) |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`audio-datasets`](../../../meta/categories/audio-datasets/) |

WildASR (Tay2026) confirmed that model robustness does not transfer across accent conditions
and that ASR systems hallucinate plausible but unspoken content under degraded inputs. Gold-92
contains six non-native English speaker clips, making accent-induced entity errors a direct
project risk. Stratify all gold-92 evaluation results by speaker accent group and compare
entity accuracy between native and non-native speakers. If accent is the primary driver of
entity errors rather than lexical ambiguity, post-correction methods (RECOVER, Ron2026) will
have limited effect and ASR-stage improvements should be prioritized instead. Recommended task
types: data-analysis, stt-benchmark-run.

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
