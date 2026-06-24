# Project Dashboard

<p align="center">
  <a href="papers/"><img src="https://img.shields.io/badge/Papers-19-4169E1" alt="Papers"></a>
  <a href="datasets/"><img src="https://img.shields.io/badge/Datasets-1-2E8B57" alt="Datasets"></a>
  <a href="models/"><img src="https://img.shields.io/badge/Models-0-FF8C00" alt="Models"></a>
  <a href="predictions/"><img src="https://img.shields.io/badge/Predictions-5-9370DB" alt="Predictions"></a>
  <a href="libraries/"><img src="https://img.shields.io/badge/Libraries-0-20B2AA" alt="Libraries"></a>
  <a href="answers/"><img src="https://img.shields.io/badge/Answers-0-CD853F" alt="Answers"></a>
</p>

<p align="center">
  <a href="news/"><img src="https://img.shields.io/badge/News-0-FF6347" alt="News"></a>
  <a href="tasks/"><img src="https://img.shields.io/badge/Tasks-5-4682B4" alt="Tasks"></a>
  <a href="suggestions/"><img src="https://img.shields.io/badge/Suggestions-25-DAA520" alt="Suggestions"></a>
  <a href="llm-context/"><img src="https://img.shields.io/badge/LLM%20Contexts-8-8B4513" alt="LLM Contexts"></a>
  <a href="metrics/"><img src="https://img.shields.io/badge/Metrics-7-708090" alt="Metrics"></a>
  <a href="metrics-results/"><img src="https://img.shields.io/badge/Results-9-DC143C" alt="Results"></a>
  <a href="task-types/"><img src="https://img.shields.io/badge/Task%20Types-21-708090" alt="Task%20Types"></a>
</p>

🏷️ **Categories**: [audio-datasets](by-category/audio-datasets.md) |
[commercial-apis](by-category/commercial-apis.md) |
[confidence-routing](by-category/confidence-routing.md) |
[entity-correction](by-category/entity-correction.md) |
[latency-profiling](by-category/latency-profiling.md) |
[stt-evaluation](by-category/stt-evaluation.md) |
[whisper-finetuning](by-category/whisper-finetuning.md)

**[LLM Contexts](llm-context/README.md)**: [overview](llm-context/project-overview.xml) (3K) |
[full](llm-context/full.xml) (24K) | [roadmap](llm-context/roadmap.xml) (8K) |
[results](llm-context/results-deep-dive.xml) (19K) |
[assets](llm-context/literature-and-assets.xml) (8K)

*Last updated: 2026-06-24 11:08 UTC*

* **Budget**: **$2** spent of $2000
* **Remaining**: **$1998**
* **Usage**: `░░░░░░░░░░░░░░░░░░░░` 0.1%

---

## [Daily News (0)](news/)

No daily news yet.

---

## [In Progress (0)](tasks/by-status/in_progress.md)

No tasks in progress.

---

## [Ready to Start (0)](tasks/by-status/not_started.md)

No tasks ready to start.

---

## [Blocked Tasks (0)](tasks/)

No blocked tasks.

---

## [Recently Completed (5 total)](tasks/by-status/completed.md)

| # | Task | Results | Completed |
|---|------|---------|-----------|
| 0005 | [STT Model Survey: Open-Source Candidates for the brainpowa Pipeline](../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) | [`results`](../tasks/t0005_stt_model_survey_brainpowa/results/results_detailed.md) | 2026-06-24 11:06 |
| 0004 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | [`results`](../tasks/t0004_vocabulary_biasing_experiment/results/results_detailed.md) | 2026-06-23 15:30 |
| 0002 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | [`results`](../tasks/t0002_baseline_evaluation/results/results_detailed.md) | 2026-06-23 10:25 |
| 0003 | [Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)](../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) | [`results`](../tasks/t0003_literature_review_entity_stt/results/results_detailed.md) | 2026-06-23 09:25 |
| 0001 | [STT Benchmark — Gold-92 Dataset Ingestion](../overview/tasks/task_pages/t0001_stt_benchmark.md) | [`results`](../tasks/t0001_stt_benchmark/results/results_detailed.md) | 2026-06-22 00:00 |

---

## [Key Metrics Leaderboard](metrics-results/)

### ⚠️ Action-Critical WER (gold-92)

| # | Task | Variant | Value |
|---|------|---------|-------|
| 1 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 + vocab bias | **0.025316** |
| 2 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo + vocab bias | **0.050633** |
| 3 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper Large v3 | **0.303797** |
| 4 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper turbo | **0.303797** |
| 5 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 (baseline) | **0.303797** |
| 6 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo (baseline) | **0.303797** |
| 7 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Moonshine base (no biasing — model doesn't support initial_prompt) | **0.411392** |

### 📖 Entity Accuracy — Domain Vocabulary

| # | Task | Variant | Value |
|---|------|---------|-------|
| 1 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 + vocab bias | **0.945455** |
| 2 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo + vocab bias | **0.872727** |
| 3 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 (baseline) | **0.181818** |
| 4 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo (baseline) | **0.181818** |
| 5 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Moonshine base (no biasing — model doesn't support initial_prompt) | **0.109091** |

### 🎯 Entity Accuracy (gold-92)

| # | Task | Variant | Value |
|---|------|---------|-------|
| 1 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 + vocab bias | **0.460145** |
| 2 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo + vocab bias | **0.431159** |
| 3 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper Large v3 | **0.251812** |
| 4 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper turbo | **0.251812** |
| 5 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 (baseline) | **0.251812** |
| 6 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo (baseline) | **0.251812** |
| 7 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Moonshine base (no biasing — model doesn't support initial_prompt) | **0.217029** |

### ✅ Intent Preservation (gold-92)

| # | Task | Variant | Value |
|---|------|---------|-------|
| 1 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 + vocab bias | **0.989247** |
| 2 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo + vocab bias | **0.967742** |
| 3 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper Large v3 | **0.903226** |
| 4 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper turbo | **0.903226** |
| 5 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 (baseline) | **0.903226** |
| 6 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo (baseline) | **0.903226** |
| 7 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Moonshine base (no biasing — model doesn't support initial_prompt) | **0.849462** |

### ⚡ Latency p50 (seconds)

| # | Task | Variant | Value |
|---|------|---------|-------|
| 1 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Moonshine base (no biasing — model doesn't support initial_prompt) | **0.0697** |
| 2 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper turbo | **4.2501** |
| 3 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo (baseline) | **4.2501** |
| 4 | [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | Whisper Large v3 | **5.6598** |
| 5 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 (baseline) | **5.6598** |
| 6 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper turbo + vocab bias | **5.8598** |
| 7 | [Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | Whisper Large v3 + vocab bias | **6.6621** |

---

## [Recent Suggestions (24 open)](suggestions/)

<details>
<summary>🧪 <strong>Benchmark IBM Granite Speech 4.1 2B on gold-92 for entity
accuracy and latency</strong> (S-0005-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>🧪 <strong>Benchmark FunASR Paraformer with contextual biasing on
gold-92</strong> (S-0005-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

FunASR Paraformer (SenseVoice/SeACo variant) achieves 1.8% Entity WER (EWER) with
shallow-fusion contextual biasing on ~1,800 entities, and Apache 2.0 license. As the secondary
candidate from the survey, benchmark it on gold-92 to validate entity accuracy and measure
latency under concurrent load. Test both shallow-fusion (low-latency) and deep-biasing
variants if available. If TTFT <200ms achievable and entity accuracy competitive with Granite,
Paraformer becomes a strong alternative. Also measure integration complexity vs. Granite to
inform production selection. Recommended task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary>🔧 <strong>Integrate IBM Granite Speech 4.1 into brainpowa STTAdapter brick
(async wrapper)</strong> (S-0005-03)</summary>

**Kind**: technique | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>🔧 <strong>Implement shallow-fusion contextual biasing adapter for Moonshine
v2</strong> (S-0005-04)</summary>

**Kind**: technique | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>📊 <strong>Profile Granite 4.1, Paraformer, and Whisper latency under
concurrent request load</strong> (S-0005-05)</summary>

**Kind**: evaluation | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>📊 <strong>Test entity-biasing mechanisms at scale (1,000+ entity
vocabulary)</strong> (S-0005-06)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

The survey reports contextual biasing results on 50–1,800 entity lists. Rezolve's product
catalog scales to 10,000+ SKUs. Test whether Granite 4.1 keyword biasing and Paraformer
deep-biasing maintain performance (latency, entity accuracy) when biasing context grows from
1,800 to 10,000 entities. Measure latency scaling curve and F1 degradation if any. If latency
exceeds budget at production scale, design a retrieval-based filtering pre-pass (e.g.,
retrieve top-100 entities relevant to the speaker/context before biasing) to cap the active
biasing vocabulary. Recommended task types: experiment-run, data-analysis.

</details>

<details>
<summary>🧪 <strong>Compare Granite/Paraformer against Deepgram Nova-2 and Azure
Speech on gold-92</strong> (S-0005-07)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

The survey did not include closed-API baselines (Deepgram Nova-2, Azure Speech Services). Both
support contextual biasing and have lower latency than Whisper. Run a comparative benchmark to
establish whether open-source candidates (Granite, Paraformer) can match or exceed the
accuracy and latency of production-quality closed APIs. This context is critical for
production decision-making if open-source candidates fall short. Azure Speech and Deepgram API
costs are approximately $0.01–$0.10 for 93 clips. Recommended task types: stt-benchmark-run,
comparative-analysis.

</details>

<details>
<summary>🧪 <strong>Evaluate fallback strategy if top candidates underperform on
accented English</strong> (S-0005-08)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>📊 <strong>Quantify entity accuracy gain vs. integration effort for Granite
vs. Paraformer</strong> (S-0005-09)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

After benchmarking both Granite and Paraformer on gold-92 (suggestions S-0005-01, S-0005-02),
create a cost-benefit matrix: entity accuracy gain (%) vs. integration complexity (days),
latency under load (ms), and VRAM (GB). Use this to make a final production selection. If
Granite delivers +12% entity accuracy with 2-day integration and Paraformer delivers +10% with
4-day integration, the decision favors Granite. This task synthesizes the experimental
findings into a decision frame for the team. Recommended task types: comparative-analysis,
data-analysis.

</details>

<details>
<summary>🔧 <strong>Implement quantized variants of Granite/Paraformer for edge and
latency optimization</strong> (S-0005-10)</summary>

**Kind**: technique | **Priority**: low | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

If benchmarking shows that Granite or Paraformer meet accuracy targets but exceed VRAM or
latency budgets at scale, implement quantized (int8/float16) variants using ONNX, TensorRT, or
vLLM to reduce model size and improve inference speed. Moonshine already ships as a
245M-parameter model optimized for edge; quantization could reduce Granite (2B) and Paraformer
(varies) to similar footprints. Measure quantization impact on entity accuracy and latency. If
quantization preserves accuracy within 1–2% while halving latency, quantized variants become
the recommended production deployment. Recommended task types: experiment-run, build-model.

</details>

*14 more open suggestions → [open suggestions](suggestions/)*

---

## [High Priority Suggestions (9)](suggestions/)

<details>
<summary>🧪 <strong>Benchmark IBM Granite Speech 4.1 2B on gold-92 for entity
accuracy and latency</strong> (S-0005-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>🧪 <strong>Benchmark FunASR Paraformer with contextual biasing on
gold-92</strong> (S-0005-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

FunASR Paraformer (SenseVoice/SeACo variant) achieves 1.8% Entity WER (EWER) with
shallow-fusion contextual biasing on ~1,800 entities, and Apache 2.0 license. As the secondary
candidate from the survey, benchmark it on gold-92 to validate entity accuracy and measure
latency under concurrent load. Test both shallow-fusion (low-latency) and deep-biasing
variants if available. If TTFT <200ms achievable and entity accuracy competitive with Granite,
Paraformer becomes a strong alternative. Also measure integration complexity vs. Granite to
inform production selection. Recommended task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary>🔧 <strong>Integrate IBM Granite Speech 4.1 into brainpowa STTAdapter brick
(async wrapper)</strong> (S-0005-03)</summary>

**Kind**: technique | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>📊 <strong>Profile Granite 4.1, Paraformer, and Whisper latency under
concurrent request load</strong> (S-0005-05)</summary>

**Kind**: evaluation | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../tasks/t0005_stt_model_survey_brainpowa/)

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
<summary>🧪 <strong>Vocabulary-biased Whisper inference via STT_INITIAL_PROMPT on
gold-92</strong> (S-0002-01)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../tasks/t0002_baseline_evaluation/)

Run Whisper turbo on gold-92 with a domain vocabulary prompt injected via STT_INITIAL_PROMPT
(e.g., 'Rezolve, brainpowa, Rezolve AI, Shopify Plus, Salesforce Commerce Cloud, Adobe
Commerce, AI Foundry'). The baseline showed 'Rezolve' is systematically transcribed as 'Hizol'
or 'Resolve' — a pure vocabulary gap. Vocabulary biasing via initial_prompt requires zero
training and zero API cost. Measure entity accuracy on production clips specifically
(baseline: 8.8%) and compare with paired BCa test against the whisper-turbo baseline.
Recommended task types: stt-benchmark-run, experiment-run.

</details>

<details>
<summary>🧪 <strong>Run Deepgram Nova-2 baseline on gold-92 to complete REQ-1 and
paired significance test</strong> (S-0002-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../tasks/t0002_baseline_evaluation/)

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
<summary>🔧 <strong>LLM post-correction layer for entity normalization on Whisper
transcripts</strong> (S-0002-03)</summary>

**Kind**: technique | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../tasks/t0002_baseline_evaluation/)

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

## [Latest Papers (19 total)](papers/)

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
| **Categories** | [`stt-evaluation`](../meta/categories/stt-evaluation/), [`whisper-finetuning`](../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0002_baseline_evaluation`](../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../tasks/t0002_baseline_evaluation/assets/paper/10.48550_arXiv.2212.04356/summary.md) |

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

*9 more papers → [papers](papers/)*

---

## [Latest Datasets (1 total)](datasets/)

| Name | Size | Source | Added |
|------|------|--------|-------|
| [STT Benchmark Gold-92](../tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/description.md) | 93 WAV clips (~58 MB total audio). Speakers include accented English (French, German, Hebrew, Korean, Russian, Spanish native languages) plus English-native Rezolve IR session recordings. | [1](../overview/tasks/task_pages/t0001_stt_benchmark.md) | 2026-06-22 |

---

## [Latest Models (0 total)](models/)

No models yet.

---

## [Latest Predictions (5 total)](predictions/)

| Name | Source | Created |
|------|--------|---------|
| [Whisper turbo on Gold-92](../tasks/t0002_baseline_evaluation/assets/predictions/whisper-turbo-gold92/description.md) | [2](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | 2026-06-23 |
| [Whisper Turbo + Vocabulary Bias on Gold-92](../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-turbo-biased/description.md) | [4](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | 2026-06-23 |
| [Whisper Large v3 on Gold-92](../tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/description.md) | [2](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | 2026-06-23 |
| [Whisper Large v3 + Vocabulary Bias on Gold-92](../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/description.md) | [4](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | 2026-06-23 |
| [Moonshine Base on Gold-92 (no vocabulary biasing)](../tasks/t0004_vocabulary_biasing_experiment/assets/predictions/moonshine-base-gold92/description.md) | [4](../overview/tasks/task_pages/t0004_vocabulary_biasing_experiment.md) | 2026-06-23 |

---

## [Latest Libraries (0 total)](libraries/)

No libraries yet.

---

## [Cost Leaders (1 tasks with spend)](costs/)

| Task | Cost | Date |
|------|------|------|
| [Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92](../overview/tasks/task_pages/t0002_baseline_evaluation.md) | [`$2.50`](../tasks/t0002_baseline_evaluation/results/costs.json) | 2026-06-23 10:25 |
