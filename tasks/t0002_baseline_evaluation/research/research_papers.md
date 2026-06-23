---
spec_version: "1"
task_id: "t0002_baseline_evaluation"
research_stage: "papers"
papers_reviewed: 0
papers_cited: 0
categories_consulted:
  - "stt-evaluation"
  - "commercial-apis"
  - "whisper-finetuning"
  - "entity-correction"
  - "latency-profiling"
  - "audio-datasets"
  - "confidence-routing"
date_completed: "2026-06-23"
status: "partial"
---
# Research — Existing Papers

## Task Objective

This task establishes project baselines by running two STT systems — Deepgram Nova-2 (the current
Rezolve production endpoint) and Whisper Large v3 (the leading open-source alternative) — on the
gold-92 benchmark: 93 annotated WAV clips from Rezolve production voice sessions in the
investor-relations domain with accented English speakers. For each system, all five registered
project metrics must be computed with BCa bootstrap 95% confidence intervals (n=10,000 resamples):
entity accuracy on action-critical spans (`entity_accuracy_gold92`), full-transcript WER
(`wer_gold92`), action-critical WER (`action_critical_wer_gold92`), intent preservation
(`intent_preservation_gold92`), and end-to-end latency p50 (`latency_p50_seconds`). A paired BCa
bootstrap significance test comparing Whisper Large v3 vs. Deepgram on `entity_accuracy_gold92` is
also required. This baseline is the reference point against which every downstream improvement
(entity post-correction, fine-tuning, confidence routing) will be measured.

**Status note**: The project paper corpus is empty at this stage — no papers have been downloaded
via `add-paper` into any task's `assets/paper/` directory. Both the `aggregate_papers` aggregator
(with and without category filters) returned zero results. The key references cited in the task
description — Radford et al. (2023) on the Whisper model and Deepgram Nova-2 documentation — are not
yet registered in the corpus as paper assets. This document is therefore marked `"partial"`. The
dedicated literature review task (`t0003_literature_review_entity_stt`) is planned to ingest the
Whisper paper, relevant evaluation methodology papers, and domain-adaptation literature. Once those
assets exist, a subsequent `research-papers` pass on this task (or the compare-literature step)
should supersede this partial document.

## Category Selection Rationale

All seven registered project categories were consulted via `aggregate_categories` and
`aggregate_papers` (both with and without category filters). The categories and their relevance to
this task are assessed below.

**Included categories** (queried; zero papers found in each):

* `stt-evaluation` — directly covers this task: benchmarking ASR systems on entity accuracy, WER,
  and intent preservation using the gold-92 held-out set. This is the primary category.
* `commercial-apis` — covers Deepgram Nova-2, one of the two systems evaluated. Any papers on
  commercial STT API evaluation methodology or Deepgram-specific benchmarks belong here.
* `whisper-finetuning` — Whisper Large v3 is the second system evaluated. Papers on Whisper
  architecture, training, and out-of-the-box benchmark performance belong here, even though this
  task does not fine-tune.
* `entity-correction` — understanding published entity accuracy baselines is needed to contextualise
  what the gold-92 scores mean and what gaps post-correction tasks should close.
* `latency-profiling` — the task requires measuring `latency_p50_seconds` for both systems. Papers
  on STT inference latency measurement protocols are relevant.
* `audio-datasets` — the gold-92 benchmark is the evaluation set; papers on evaluation dataset
  design and annotation methodology are pertinent for understanding gold-92's representativeness.
* `confidence-routing` — excluded from this task's scope (no routing policy is evaluated here), but
  queried to catch any papers that discuss confidence calibration alongside baseline accuracy
  evaluation.

**Excluded categories** (none, because there are only seven categories and all were checked):

The project has no categories outside the seven listed above. No papers were found in any category.

## Key Findings

### No Papers Are Available in the Project Corpus

The `aggregate_papers` script was run twice — once without any filter (to catch all registered
papers regardless of category) and once filtered to the five most relevant categories
(`stt-evaluation`, `commercial-apis`, `whisper-finetuning`, `entity-correction`,
`latency-profiling`). Both invocations returned `paper_count: 0`. No paper assets exist under any
task's `assets/paper/` directory. All seven project categories were checked; none contained any
registered paper.

The task description identifies two primary external references: Radford et al. (2023) "Robust
Speech Recognition via Large-Scale Weak Supervision" (the Whisper paper, arXiv:2212.04356) and the
Deepgram Nova-2 API documentation. Neither is registered in the corpus. Until these are added via
`add-paper`, no quantitative claims from the published Whisper evaluation (e.g., reported WER on
Common Voice, LibriSpeech, TED-LIUM, or other benchmarks) can be cited with proper provenance. The
dedicated literature review task, `t0003_literature_review_entity_stt`, is planned to ingest the
Whisper paper, relevant STT evaluation methodology papers, and domain-adaptation literature. Until
that task completes and its paper assets are available to the aggregator, this document remains in a
partial state.

**Consequence for this document**: Per the research-papers specification, `papers_cited` must equal
the Paper Index entry count. With zero papers in the corpus and the prohibition on fabricating
citations, this document cannot include a populated Paper Index or inline citations. The status is
`"partial"`.

## Methodology Insights

Based on the task description and project context (without paper citations, as none are available):

* The evaluation must cover all five registered metrics with BCa bootstrap 95% CI (n=10,000
  resamples). Paired BCa on `entity_accuracy_gold92` is the primary significance test between the
  two systems.
* Raw transcription outputs (`deepgram_transcripts.json`, `whisper_transcripts.json`) must be saved
  before metric computation to allow re-scoring without re-running expensive inference.
* Deepgram Nova-2 is called via the cloud API with default settings (no custom vocabulary), so
  network latency contributes to `latency_p50_seconds` for that system.
* Whisper Large v3 is run locally via `openai-whisper`, meaning latency depends on available compute
  (CPU vs. GPU). Latency figures for the two systems will not be directly comparable on equal
  hardware, so the metadata asset must record the inference hardware configuration.
* Gold-92 contains 93 clips (not 92, despite the name), covering the investor-relations domain with
  accented English. Entity spans cover brand names, product lines, SKUs, and IR terms. The
  annotation format must be confirmed from the `t0001_stt_benchmark` dataset asset before writing
  the metric computation code.
* The per-accent-group breakdown required by the task description implies that clip metadata
  includes speaker accent labels — this should be verified against the dataset asset during the
  research-code step.

## Gaps and Limitations

* **No published baselines for comparison**: Without the Whisper paper in the corpus, there are no
  citable WER numbers from published evaluations to compare against the gold-92 results. The
  compare-literature step (step 13) will need to ingest the Whisper paper and Deepgram benchmarks
  before any published-vs-gold-92 comparison is possible.
* **No evaluation methodology papers**: Papers covering BCa bootstrap significance testing for ASR
  evaluation, or papers that define entity accuracy as a metric, are absent. The metric computation
  code must therefore be implemented from first principles without a citable methodological
  reference.
* **No domain-specific STT evaluation papers**: No papers covering STT evaluation on ecommerce or
  investor-relations audio are in the corpus. Whether 93 clips is statistically adequate for the
  chosen CI method is not substantiated by literature.
* **Deepgram not academically documented**: Deepgram Nova-2 is a commercial product with API
  documentation but no peer-reviewed paper in the corpus. Its internal architecture and training
  data are not publicly disclosed, making it impossible to cite any architectural claims.

## Recommendations for This Task

1. **Proceed with implementation without paper citations** — the absence of papers in the corpus
   does not block the evaluation itself. The methodology (BCa bootstrap, paired significance test,
   all five metrics) is fully specified in the task description and can be implemented directly.

2. **Add the Whisper paper to the corpus before the compare-literature step** — use `add-paper` with
   Radford et al. (2023), DOI `10.48550/arXiv.2212.04356`, before step 13. This is the minimum
   needed to compare gold-92 WER against published Whisper Large v3 benchmarks.

3. **Record inference hardware in metadata.json** — since Whisper runs locally, the latency figures
   are hardware-dependent. The metadata asset must capture CPU/GPU model, RAM, and `openai-whisper`
   version so latency results are reproducible and interpretable.

4. **Confirm gold-92 annotation schema before coding metric computation** — specifically, verify
   that entity span annotations include the fields expected by the `entity_accuracy_gold92` metric
   definition, and that accent group labels are present for the per-group breakdown table.

5. **Revisit this document after `t0003_literature_review_entity_stt` completes** — that task is
   planned to ingest the Whisper paper and related STT evaluation literature. A research-papers pass
   on t0002 (or an update to this file) after t0003 completes will fill the gaps identified here and
   convert this document from `"partial"` to `"complete"`.

## Paper Index

No papers are cited in this document. The paper corpus is empty at time of writing. See the Task
Objective section for explanation of partial status.
