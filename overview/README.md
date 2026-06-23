# Project Dashboard

<p align="center">
  <a href="papers/"><img src="https://img.shields.io/badge/Papers-15-4169E1" alt="Papers"></a>
  <a href="datasets/"><img src="https://img.shields.io/badge/Datasets-1-2E8B57" alt="Datasets"></a>
  <a href="models/"><img src="https://img.shields.io/badge/Models-0-FF8C00" alt="Models"></a>
  <a href="predictions/"><img src="https://img.shields.io/badge/Predictions-0-9370DB" alt="Predictions"></a>
  <a href="libraries/"><img src="https://img.shields.io/badge/Libraries-0-20B2AA" alt="Libraries"></a>
  <a href="answers/"><img src="https://img.shields.io/badge/Answers-0-CD853F" alt="Answers"></a>
</p>

<p align="center">
  <a href="news/"><img src="https://img.shields.io/badge/News-0-FF6347" alt="News"></a>
  <a href="tasks/"><img src="https://img.shields.io/badge/Tasks-3-4682B4" alt="Tasks"></a>
  <a href="suggestions/"><img src="https://img.shields.io/badge/Suggestions-8-DAA520" alt="Suggestions"></a>
  <a href="llm-context/"><img src="https://img.shields.io/badge/LLM%20Contexts-8-8B4513" alt="LLM Contexts"></a>
  <a href="metrics/"><img src="https://img.shields.io/badge/Metrics-6-708090" alt="Metrics"></a>
  <a href="metrics-results/"><img src="https://img.shields.io/badge/Results-3-DC143C" alt="Results"></a>
  <a href="task-types/"><img src="https://img.shields.io/badge/Task%20Types-21-708090" alt="Task%20Types"></a>
</p>

🏷️ **Categories**: [audio-datasets](by-category/audio-datasets.md) |
[commercial-apis](by-category/commercial-apis.md) |
[confidence-routing](by-category/confidence-routing.md) |
[entity-correction](by-category/entity-correction.md) |
[latency-profiling](by-category/latency-profiling.md) |
[stt-evaluation](by-category/stt-evaluation.md) |
[whisper-finetuning](by-category/whisper-finetuning.md)

**[LLM Contexts](llm-context/README.md)**: [overview](llm-context/project-overview.xml) (2K) |
[full](llm-context/full.xml) (13K) | [roadmap](llm-context/roadmap.xml) (5K) |
[results](llm-context/results-deep-dive.xml) (7K) |
[assets](llm-context/literature-and-assets.xml) (6K)

*Last updated: 2026-06-23 10:13 UTC*

* **Budget**: **$0** spent of $2000
* **Remaining**: **$2000**
* **Usage**: `░░░░░░░░░░░░░░░░░░░░` 0.0%

---

## [Daily News (0)](news/)

No daily news yet.

---

## [In Progress (1)](tasks/by-status/in_progress.md)

| # | Task | Started |
|---|------|---------|
| 0002 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | 2026-06-23 08:04 |

---

## [Ready to Start (0)](tasks/by-status/not_started.md)

No tasks ready to start.

---

## [Blocked Tasks (0)](tasks/)

No blocked tasks.

---

## [Recently Completed (2 total)](tasks/by-status/completed.md)

| # | Task | Results | Completed |
|---|------|---------|-----------|
| 0003 | [Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) | [`results`](../tasks/t0003_literature_review_entity_stt/results/results_detailed.md) | 2026-06-23 09:25 |
| 0001 | [STT Benchmark — Gold-92 Dataset Ingestion](../overview/tasks/task_pages/t0001_stt_benchmark.md) | [`results`](../tasks/t0001_stt_benchmark/results/results_detailed.md) | 2026-06-22 00:00 |

---

## [Recent Suggestions (8 open)](suggestions/)

<details>
<summary>🧪 <strong>Prototype RECOVER N-best + LLM-Select on gold-92</strong>
(S-0003-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Implement the RECOVER pipeline (Kumar2026) on Whisper Turbo: enable beam-width-5 decoding,
collect top-5 hypotheses, and use GPT-4o LLM-Select to choose the most entity-accurate
hypothesis. Measure entity accuracy (substring match), overall WER, and end-to-end latency on
all 93 gold-92 clips. RECOVER reported 33-35% relative E-WER reduction on Earnings-21, the
closest public proxy for ecommerce entities. This is the highest expected gain from a
no-retraining method in the survey. Recommended task types: post-correction-experiment,
stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Prototype Ron2026 initial_prompt multi-agent pipeline on
gold-92</strong> (S-0003-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Implement the six-agent LLM pipeline from Ron2026 against Whisper Turbo on gold-92. The
pipeline processes a first-pass transcript to extract topic labels, named entities, and domain
jargon, assembles a context prompt (224 tokens max), and feeds it into a second Whisper
decoding pass via the initial_prompt parameter. Seed the NER agent with Rezolve's
brand/product catalog. Measure entity accuracy and latency on all 93 clips. Ron2026 reported
17% relative WER reduction on entity-dense NBA commentary with zero model retraining.
Recommended task types: post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>📂 <strong>Annotate gold-92 with entity span offsets to enable E-WER and
Slot F1</strong> (S-0003-03)</summary>

**Kind**: dataset | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Add entity-offset markup to gold-92 ground-truth transcripts, tagging brand names, product
names, and SKUs with character-level span annotations. This unblocks computation of E-WER
(required to evaluate RECOVER) and Slot F1 (required to evaluate Zheng2026 selective span
editing). Without entity spans, only substring-match and overall WER can be reported on
gold-92. The annotation should cover all 93 clips and follow a schema compatible with the
Contextual Earnings-22 format (Durmus2026) to enable cross-benchmark comparison. Recommended
task types: audio-dataset-curation.

</details>

<details>
<summary>📊 <strong>Add S2ER (sentence-level semantic error rate) metric to the
project evaluation harness</strong> (S-0003-04)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Register and implement the S2ER metric from Jiang2026 in the project's evaluation harness.
S2ER is an LLM-judged metric that better correlates with wrong-action rate than WER: it
collapsed from 19-28% to under 2% over correction turns while WER changed only marginally.
Adding S2ER alongside WER and entity accuracy provides a direct proxy for the project's target
metric of wrong-action rate below 2%. Implementation: add an LLM judge (GPT-4o) call per
utterance that scores semantic equivalence between reference and hypothesis. Recommended task
types: stt-benchmark-run, write-library.

</details>

<details>
<summary>🔧 <strong>Implement Novitasari2026 common-word cue injection as a
zero-latency biasing add-on</strong> (S-0003-05)</summary>

**Kind**: technique | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Implement the common-word cue approach from Novitasari2026 as a pre-processing step on top of
Rezolve's existing dynamic context injection. The method maps non-standard brand names and
SKUs to phonetically similar common-word anchors, adding them to the bias list without G2P.
Novitasari2026 reported 16.3% reduction in bias-word errors with zero added latency and no
model retraining, and the method is additive to any existing biasing technique. Evaluate on
gold-92 entity accuracy and confirm zero latency impact. Recommended task types:
post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>📊 <strong>Measure end-to-end latency of RECOVER and Ron2026 pipelines on
Rezolve infrastructure</strong> (S-0003-06)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

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

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

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
<summary>🔧 <strong>Monitor LOGIC (Wang2026) arXiv reappearance for constant-time
logit-space biasing</strong> (S-0003-08)</summary>

**Kind**: technique | **Priority**: low | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

The LOGIC paper (Wang2026, logit-space entity biasing with constant-time complexity, 9%
relative Entity WER reduction) was withdrawn from arXiv in February 2026 for institutional
approval compliance. It cannot be implemented until it reappears at a conference venue. Set up
monitoring for LOGIC reappearance at Interspeech 2026 or ICASSP 2026 proceedings. Once
republished, LOGIC's constant-time biasing approach directly addresses context window
saturation at catalog scale (10,000+ entries) without the retrieval infrastructure required by
BR-ASR. Recommended task types: internet-research.

</details>

---

## [High Priority Suggestions (3)](suggestions/)

<details>
<summary>🧪 <strong>Prototype RECOVER N-best + LLM-Select on gold-92</strong>
(S-0003-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Implement the RECOVER pipeline (Kumar2026) on Whisper Turbo: enable beam-width-5 decoding,
collect top-5 hypotheses, and use GPT-4o LLM-Select to choose the most entity-accurate
hypothesis. Measure entity accuracy (substring match), overall WER, and end-to-end latency on
all 93 gold-92 clips. RECOVER reported 33-35% relative E-WER reduction on Earnings-21, the
closest public proxy for ecommerce entities. This is the highest expected gain from a
no-retraining method in the survey. Recommended task types: post-correction-experiment,
stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Prototype Ron2026 initial_prompt multi-agent pipeline on
gold-92</strong> (S-0003-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Implement the six-agent LLM pipeline from Ron2026 against Whisper Turbo on gold-92. The
pipeline processes a first-pass transcript to extract topic labels, named entities, and domain
jargon, assembles a context prompt (224 tokens max), and feeds it into a second Whisper
decoding pass via the initial_prompt parameter. Seed the NER agent with Rezolve's
brand/product catalog. Measure entity accuracy and latency on all 93 clips. Ron2026 reported
17% relative WER reduction on entity-dense NBA commentary with zero model retraining.
Recommended task types: post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>📂 <strong>Annotate gold-92 with entity span offsets to enable E-WER and
Slot F1</strong> (S-0003-03)</summary>

**Kind**: dataset | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../tasks/t0003_literature_review_entity_stt/)

Add entity-offset markup to gold-92 ground-truth transcripts, tagging brand names, product
names, and SKUs with character-level span annotations. This unblocks computation of E-WER
(required to evaluate RECOVER) and Slot F1 (required to evaluate Zheng2026 selective span
editing). Without entity spans, only substring-match and overall WER can be reported on
gold-92. The annotation should cover all 93 clips and follow a schema compatible with the
Contextual Earnings-22 format (Durmus2026) to enable cross-benchmark comparison. Recommended
task types: audio-dataset-curation.

</details>

---

## [Recent Answers (0 total)](answers/)

No answers yet.

---

## [Latest Papers (15 total)](papers/)

<details>
<summary>🏤 <strong>Towards Robust Dysarthric Speech Recognition: LLM-Agent Post-ASR
Correction Beyond WER</strong> — Zheng et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.21347` |
| **Authors** | Xiuwen Zheng, Sixun Dong, Bornali Phukon, Mark Hasegawa-Johnson, Chang D. Yoo |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2601.21347` |
| **URL** | https://arxiv.org/abs/2601.21347 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.21347/summary.md) |

Zheng et al. address the disconnect between WER and actual downstream accuracy for ASR
post-correction. Standard WER counts all token substitutions equally, regardless of whether
the error affects a function word or a business-critical entity name. The paper frames
post-correction as a selective editing task rather than a full rewrite, motivated by the
observation that LLM hallucination replaces rare domain terms with plausible but wrong
alternatives.

The Judge-Editor architecture takes k=5 ASR hypotheses and uses span-level agreement as a
proxy for transcription confidence. High-agreement spans are preserved unchanged;
low-agreement spans are rewritten by an LLM guided by structured prompts. The SAP-Hypo5
benchmark, introduced alongside the method, provides a reproducible evaluation environment
with five hypotheses per utterance and multi-metric scoring.

Key results: **14.51% WER reduction**, **+7.59 pp MENLI**, and **+7.66 pp Slot Micro F1** on
difficult samples. The selective editing mechanism reduces hallucinations by ~30% compared to
unconstrained LLM rewriting, practically important when rare entities must be preserved.

For Rezolve's voice commerce pipeline, the takeaways are: (a) Slot Micro F1 on brand/product
spans is a better proxy for wrong-action rate than WER; (b) an N-best post-correction agent
using multiple ASR hypotheses is a viable low-latency add-on avoiding model retraining; and
(c) domain fine-tuning on ecommerce entity examples would materially improve entity correction
accuracy.

</details>

<details>
<summary>📝 <strong>TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust
Automatic Speech Recognition</strong> — Wang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.27808` |
| **Authors** | Xinyu Wang, Ziyu Zhao, Ke Bai, Silin Meng, Dongming Shen, Xiao-Wen Chang, Yixuan He |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.27808` |
| **URL** | https://arxiv.org/abs/2605.27808 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`latency-profiling`](../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.27808/summary.md) |

TARQ diagnoses and fixes a structural flaw in data-aware post-training quantization for ASR:
standard calibration metrics inherit the Zipfian token-frequency distribution of the
calibration corpus, assigning only ~6.9% of trace mass to rare tokens (names, numerals, domain
terms) that represent a disproportionate share of recognition risk in entity-sensitive
applications. The research question is whether this metric-level imbalance — not solver
quality — is the root cause of rare-word degradation under W4G128 quantization of modern ASR
models.

TARQ addresses this through RAREBAL, a closed-form per-Linear-layer trace equalization that
reweights the calibration metric to give equal mass to common and rare token groups, computed
from a single scalar derived from activation second moments already accumulated during PTQ. A
propagation-aware residual correction ensures the sequential layer sweep remains aligned with
the rebalanced metric. Both components require no entity labels, no additional data, and no
extra calibration pass, making TARQ a drop-in enhancement to any GPTQ-family solver.

Across 8 backbones and 6 datasets, TARQ achieves rank-1 mean plain WER on all backbones and
rank-1 mean rare-WER on 6 of 8, with a cross-corpus stability swing of just 0.63 pp vs 2.51 pp
for GPTQ. Entity-rich benchmarks (ProfASR, ContextASR-Speech-En) confirm transfer without
entity supervision. Deployment profiling shows 1.06x–2.18x GPU speedup and 33%–67% VRAM
reduction, with Whisper-large-v3 reaching CPU real time (RTF 0.87 at 8 threads).

For Rezolve's voice commerce pipeline, TARQ offers a practical path to compressed ASR without
sacrificing brand name and SKU recognition quality. The identified limitation — failure on
isolated rare proper nouns lacking phonetic context — directly motivates the entity-correction
research track in this project, confirming that inference-time contextual biasing or
vocabulary injection must complement quantization-time fixes. The paper's rare-WER metric also
provides a precise template for enriching the gold-92 benchmark evaluation beyond aggregate
WER.

</details>

<details>
<summary>📝 <strong>Beyond Prompting: Efficient and Robust Contextual Biasing for
Speech LLMs via Logit-Space Integration (LOGIC)</strong> — Wang, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.15397` |
| **Authors** | Peidong Wang |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2601.15397` |
| **URL** | https://arxiv.org/abs/2601.15397 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`latency-profiling`](../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.15397/summary.md) |

LOGIC (Logit-Space Integration for Contextual Biasing) addresses the inability of Speech LLMs
to reliably recognise domain-specific entities — brand names, contact names, product
identifiers — without the scalability failures of prompting or the hallucination failures of
generative error correction. The paper motivates the problem by demonstrating that prompting
collapses with as few as 460 entities (exhibiting "list-vomiting" output) and that GEC
introduces hallucinated entities based on textual similarity rather than acoustic evidence.
LOGIC is proposed as a decoding-layer alternative that injects entity bias directly into the
logit distribution at each auto-regressive step using a subword-aware prefix tree, achieving
O(1) complexity with respect to entity list size.

The method constructs a Token-Level Trie from the entity phrase list using Multi-Path
Tokenization to handle SentencePiece's context-dependent subword segmentation, then applies a
sparse logit bonus at each decoding step for tokens that extend a valid Trie path. Immediate
Prefix Boosting (IPB) fires the bias from the very first token of any entity to maximise
recall for short entries, while Retroactive Score Rectification (RSR) penalises hypotheses
that accumulate partial-match bonuses but diverge before completing the entity string. The
CUDA implementation uses a sparse kernel with O(D) per-step complexity, deployed as a vLLM
LogitsProcessor with zero-copy GPU state.

Experiments using Phi-4-Mini across 11 multilingual locales on an internal Microsoft Person
Name test suite show **9% average relative EWER improvement** in a conservative configuration
and **17%** in an aggressive configuration, with average FAR increase of just **+0.30%** and
RTF overhead of only **+2.8%** on A100 GPUs. French (**19%**), German (**14%**), and Mexican
Spanish (**17%**) see the strongest improvements. The method generalises to logographic
languages (zh-CN **9%**, ja-JP **6%**) despite the added complexity of context-sensitive
subword tokenization.

For the Rezolve STT project, LOGIC is directly actionable as a production-grade entity-biasing
layer for any Speech LLM (Phi-4, GPT-4o Audio) used as a replacement for or complement to
Deepgram. Its near-zero latency overhead is compatible with the 800 ms p50 voice-to-action
budget, and RSR's hallucination suppression is critical for ecommerce where false entity
insertions cause incorrect purchase actions. The key validation gap is whether the EWER
improvements on Person Names transfer to Rezolve's entity types (brand names, product lines,
investor-relations terms), which have different phonetic distributions and may require
independent tuning of the biasing bonus λ per entity category.

</details>

<details>
<summary>📝 <strong>Contextual Biasing for Streaming ASR via CTC-based Word
Spotting</strong> — Tsai et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.18222` |
| **Authors** | Kai-Chen Tsai, Tien-Hong Lo, Yun-Ting Sun, Berlin Chen |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.18222` |
| **URL** | https://arxiv.org/abs/2605.18222 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`latency-profiling`](../meta/categories/latency-profiling/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.18222/summary.md) |

Tsai et al. adapt CTC-based word spotting to streaming ASR by maintaining trie search state
across audio chunks. The core contribution is that keyword paths are not discarded at chunk
boundaries but preserved in a stateful token passing buffer, allowing detections that straddle
chunk boundaries. An incremental commitment threshold controls how long ambiguous segments are
held before being emitted.

The approach is model-agnostic: it operates on CTC posteriors, not encoder activations, making
it applicable without any retraining. The streaming window is 160ms per chunk, consistent with
practical streaming ASR deployment constraints.

Results demonstrate reduced WER and improved keyword F-score compared to streaming CTC without
biasing; specific absolute numbers are not reported in the abstract. Latency overhead is
bounded and configurable via the commitment threshold β.

For Rezolve's pipeline, the most attractive property is zero training cost: the stateful
CTC-WS can be applied directly to Whisper Turbo's CTC head without modifying model weights.
The 160ms chunk size matches typical streaming deployment, and the commitment mechanism can be
tuned to stay within the 800ms p50 latency budget. The absence of absolute metric values in
the paper's available metadata is a gap; full-paper validation is needed before concluding on
entity F-score gains.

</details>

<details>
<summary>📝 <strong>Back to Basics: Revisiting ASR in the Age of Voice
Agents</strong> — Tay et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.25727` |
| **Authors** | Geeyang Tay, Wentao Ma, Jaewon Lee, Yuzhi Tang, Daniel Lee, Weisu Yin, Dongming Shen, Silin Meng, Yi Zhu, Mu Li, Alex Smola |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2603.25727` |
| **URL** | https://arxiv.org/abs/2603.25727 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../meta/categories/stt-evaluation/), [`latency-profiling`](../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/summary.md) |

Tay et al. (2026) challenge the assumption that ASR is a solved problem by demonstrating that
modern systems achieving sub-5% WER on standard benchmarks fail severely and unpredictably
under real-world voice agent conditions. The paper's motivation is direct: voice agents do not
passively transcribe speech but use transcripts to trigger downstream tool calls and execute
actions. Under out-of-distribution conditions, hallucinated or garbled transcripts cause
silent action failures — exactly the problem Rezolve faces with its production Deepgram
deployment on accented investor-relations audio. The paper introduces WildASR, a multilingual
diagnostic benchmark (EN/ZH/JA/KO) constructed entirely from real human speech.

The benchmark decomposes OOD robustness into 11 conditions across three axes: environmental
degradation (reverberation, far-field, phone codec, noise gap, clipping), demographic shift
(children, older adults, accented speakers), and linguistic diversity (short utterances,
truncated audio, code-switching). Seven systems — Whisper Large V3, GPT-4o Transcribe, Gemini
2.5/3 Pro, Qwen2-Audio, Deepgram Nova 2, ElevenLabs Scribe V1 — are evaluated under a unified
protocol. Three diagnostic tools supplement raw metrics: a P90 Elbow detector, a prompt
sensitivity profiler (10 paraphrased instructions), and integration of Hallucination Error
Rate to catch semantic fabrications that WER misses.

The headline results are stark. Noise gaps cause **+67.7% WER** for English conversational
speech and **+121% CER** for Korean. No model achieves below **18.2% WER** on English child
speech. Deepgram Nova 2 on Chinese code-switching produces 33.7% lexical error but **68.4%
semantic hallucination rate**. Prompt phrasing alone induces up to **σ = 46.1%** performance
swing for Chinese. Robustness does not transfer across languages: a model robust to
reverberation in English may catastrophically fail in Japanese under the same perturbation.
Synthetic TTS-based evaluation underestimates real failure rates by 5.9× compared to authentic
child speech.

For this project, the paper delivers three concrete takeaways. First, the gold-92 evaluation
harness must stratify by utterance condition type and adopt HER alongside WER and entity
accuracy — aggregate WER alone will miss the hallucination risk that production Deepgram
carries. Second, Deepgram Nova 2 and Whisper Large V3 both show condition-specific failure
modes that mean their gold-92 rankings may not reflect their behavior on domain-specific OOD
inputs like accented investor-relations vocabulary. Third, the paper validates Rezolve's
methodological choice to use real production audio for gold-92 rather than TTS-synthesized
data, and confirms that short terse commands — a common voice commerce pattern — are a
high-risk category that merits dedicated coverage in the benchmark design.

</details>

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
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/), [`whisper-finetuning`](../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/summary.md) |

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
<summary>🏤 <strong>RLBR: Reinforcement Learning with Biasing Rewards for Contextual
Speech Large Language Models</strong> — Ren et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.13409` |
| **Authors** | Bo Ren, Ruchao Fan, Yelong Shen, Weizhu Chen, Jinyu Li |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2601.13409` |
| **URL** | https://arxiv.org/abs/2601.13409 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.13409/summary.md) |

Ren et al. address the SFT misalignment for contextual biasing: standard supervised
fine-tuning gives equal gradient weight to common function words and rare domain entities,
even though the entire value of contextual biasing lies in the rare entity accuracy. RLBR
corrects this by using a RL reward function that multiplies the reward for correct bias word
transcription by alpha=5, focusing the policy gradient where it matters.

The GRPO-based RL training generates 8 hypothesis samples per utterance and scores them with
the bias-word-preferred reward. A reference-aware augmentation prevents mode collapse by
ensuring the exploration space covers the correct entity handling paths.

Results on LibriSpeech: B-WER of **0.59%/2.11%** at 100 bias words, **1.09%/3.24%** at 500
words, and **1.36%/4.04%** at 1000 words (test-clean/test-other). These represent
state-of-the-art biased WERs among methods published in Jan-Jun 2026 for English ASR.

For Rezolve, RLBR requires fine-tuning the production ASR model (Whisper Turbo or equivalent)
on ecommerce entity data — a higher-investment approach than post-processing methods. The
reward shaping principle is directly transferable: any RL-based ASR fine-tuning for ecommerce
should weight brand/product/SKU tokens at alpha=5×. The reference-aware exploration mechanism
addresses a practical training stability concern that would arise when fine-tuning on a small
(~1000 utterance) ecommerce entity dataset.

</details>

<details>
<summary>🏤 <strong>Towards Deep Contextual Reasoning from Broad Descriptions for ASR
with Speech-LLM via Metadata-Driven Reasoning Chains</strong> — Poncelet
& hamme, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2606.10838` |
| **Authors** | Jakob Poncelet, Hugo Van hamme |
| **Venue** | Interspeech 2026 (conference) |
| **DOI** | `10.48550/arXiv.2606.10838` |
| **URL** | https://arxiv.org/abs/2606.10838 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2606.10838/summary.md) |

Poncelet and Van hamme train a speech-LLM to reason from broad contextual descriptions using
chain-of-thought fine-tuning. The motivation is that keyword lists cannot capture the semantic
richness of context available in real applications (video metadata, session context). The
training data is constructed automatically: GPT-4o generates reasoning chain explanations
pairing ASR errors with video metadata, creating 400 hours of reasoning-augmented training
data.

The model is fine-tuned to produce initial transcript, reasoning, and corrected output. Four
speech-LLM architectures are tested on the M3AV YouTube test set. Results: overall WER
improves from **9.4% to 9.3%**, rare word WER from **24.0% to 23.1%**, named entity WER from
**23.9% to 23.3%** — modest but consistent improvements across all architectures.

The improvements are smaller in absolute terms than keyword-biasing methods but complement
them: reasoning over context semantics catches entity corrections that keyword matching misses
(e.g., inferring a brand from product category context rather than requiring the exact brand
name in the bias list).

For Rezolve, the session metadata pipeline is particularly relevant: product categories,
search queries, and cart contents provide natural broad-description context for ecommerce
voice sessions. The automated training data construction from session logs and production
transcripts could be applied to the gold-92 domain without human annotation overhead.

</details>

<details>
<summary>🏤 <strong>Contextual Biasing for ASR in Speech LLM with Common Word Cues
and Bias Word Position Prediction</strong> — Novitasari et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2604.12398` |
| **Authors** | Sashi Novitasari, Takashi Fukuda, Gakuto Kurata, George Saon |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2604.12398` |
| **URL** | https://arxiv.org/abs/2604.12398 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/summary.md) |

Novitasari et al. address the G2P dependency problem in phoneme-assisted contextual biasing
for speech LLMs. The practical motivation is that brand names, model numbers, and domain
jargon often have phonetically irregular spellings not covered by general-purpose G2P systems,
causing phoneme-assisted biasing to fail silently.

The solution uses common words with phonetically overlapping substrings as acoustic proxies
for rare bias targets, extracted from the speech LLM's encoder. An additional position
prediction objective jointly trains the model to locate where in the output sequence a bias
word will appear, improving recall and spatial attention.

Key result: **16.3% relative reduction** in bias word recognition errors on both in-domain and
out-of-domain evaluation, with no regression on non-bias words. The position prediction head
adds a further **+2.1pp** recall improvement beyond the cue method alone.

For Rezolve's Whisper Turbo + dynamic context injection pipeline, this paper is directly
relevant: the G2P-free approach matches the constraint that product names and SKUs resist
standard phonemization. The position prediction objective is applicable as a fine-tuning
modification. The gain (16.3%) is notable but smaller than retrieval-based methods like CLAR,
suggesting it would be most valuable as a complementary addition to a retrieval layer.

</details>

<details>
<summary>🏤 <strong>RECOVER: Robust Entity Correction via Agentic Orchestration of
Hypothesis Variants for Evidence-based Recovery</strong> — Kumar &
Sachdeva, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.16411` |
| **Authors** | Abhishek Kumar, Aashraya Sachdeva |
| **Venue** | Interspeech 2026 (conference) |
| **DOI** | `10.48550/arXiv.2603.16411` |
| **URL** | https://arxiv.org/abs/2603.16411 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../meta/categories/entity-correction/), [`stt-evaluation`](../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.16411/summary.md) |

Kumar and Sachdeva address the entity recovery gap in LLM post-correction by exploiting the
N-best hypothesis diversity from beam search. The core finding is that the 1-best hypothesis
frequently omits rare entities that appear in hypotheses ranked 2-5, and that collecting this
diversity significantly improves entity recovery when a smart selection strategy is applied.

RECOVER evaluates four hypothesis selection strategies from trivial (1-Best) to LLM-based
(LLM-Select with GPT-4o), measuring entity-phrase WER (E-WER) and recall on five diverse
English domains. LLM-Select is the most robust strategy, achieving the best or near-best E-WER
on 4 of 5 datasets.

Key results: **8-46% relative E-WER reductions** and **up to +22pp entity recall** across
datasets. Earnings-21 (closest to Rezolve's entity-rich domain) sees **33-35% relative** E-WER
reduction. ROVER Ensemble degrades on noisy domains — LLM-based selection is required for
reliable cross-domain performance.

For Rezolve, RECOVER's multi-hypothesis approach is immediately applicable to the production
Whisper Turbo pipeline: collecting beam search top-5 is free, and the LLM-Select + correction
approach adds a post-processing layer with no model retraining. The main obstacle is latency:
GPT-4o adds 200-500ms per utterance. A distilled local corrector (7B class) would be needed to
meet the 800ms p50 target.

</details>

*5 more papers → [papers](papers/)*

---

## [Latest Datasets (1 total)](datasets/)

| Name | Size | Source | Added |
|------|------|--------|-------|
| [STT Benchmark Gold-92](../tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/description.md) | 93 WAV clips (~58 MB total audio). Speakers include accented English (French, German, Hebrew, Korean, Russian, Spanish native languages) plus English-native Rezolve IR session recordings. | [1](../overview/tasks/task_pages/t0001_stt_benchmark.md) | 2026-06-22 |

---

## [Latest Models (0 total)](models/)

No models yet.

---

## [Latest Predictions (0 total)](predictions/)

No predictions yet.

---

## [Latest Libraries (0 total)](libraries/)

No libraries yet.

---

## [Cost Leaders (0 tasks with spend)](costs/)

No tasks with non-zero spend.
