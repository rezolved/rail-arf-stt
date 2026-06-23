---
spec_version: "1"
task_id: "t0003_literature_review_entity_stt"
research_stage: "code"
tasks_reviewed: 1
tasks_cited: 1
libraries_found: 0
libraries_relevant: 0
date_completed: "2026-06-23"
status: "complete"
---

# Research Code: Literature Review — Entity-Aware STT for Ecommerce Voice AI

## Task Objective

This task surveys Jan–Jun 2026 publications to identify the most effective techniques for improving
STT accuracy on domain-specific named entities (brand names, product names, SKUs) in an English
ecommerce voice AI context, while remaining compatible with a sub-800 ms voice-to-action latency
constraint. The four technique categories under review are contextual biasing, shallow fusion,
entity-aware ASR, and LLM post-correction. Findings will directly inform the design of follow-on
benchmark and model tasks.

---

## Library Landscape

The library aggregator returned zero registered libraries (`"library_count": 0`). No cross-task
libraries exist in this project at this stage. The project is at an early research phase — t0001
produced a dataset asset and t0003 (this task) is the second completed task. No prior task has
produced a registered library. As a result, there is nothing to import via the library mechanism,
and all code needed for this literature-survey task must be written from scratch or copied from
prior task code. Since t0003 is a pure literature survey (no implementation code required), the
absence of libraries has no impact on execution.

---

## Key Findings

### Gold-92 Dataset: Schema, Entity Types, and Evaluation Contract

The only completed prior task is t0001_stt_benchmark [t0001], which produced the `stt-benchmark-gold-92`
dataset asset. This dataset is the canonical held-out regression set for all STT research in this
project and provides the concrete evaluation contract against which the literature survey's technique
shortlist must be assessed.

**Schema.** The dataset is stored at
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`. Two JSONL files are committed to
git:

* `files/gold_set.jsonl` — 93 records with fields: `clip_id`, `source`, `filename`, `ground_truth`,
  `production` (Deepgram Nova-2 transcript), `whisper` (Whisper Large v2 transcript). File size:
  36 KB.
* `files/ground_truth.jsonl` — 91 records with fields `clip_id` and `ground_truth` only. File size:
  16 KB. (Two clips present in `gold_set.jsonl` lack a `ground_truth.jsonl` entry; this discrepancy
  is flagged for investigation in t0002.)

Audio is stored via DVC (`files/audio.dvc`) pointing to
`azure://ml-dvc-datasets/datasets/rail-arf-stt` (account `mldvcstorerezolve`). Total audio: 93 WAV
files, ~58 MB, mono 16 kHz.

**Entity types.** The dataset does not include explicit entity span annotations (start/end offsets or
entity-type labels). Entity coverage is implicit in the `ground_truth` strings: the corpus spans
ecommerce and investor-relations utterances containing brand names (Rezolve, Salesforce, NASDAQ),
product/integration names (brainpowa), and technical terms. The literature survey should note this
annotation gap: gold-92 supports WER and substring-match entity accuracy, but not span-level F1
unless annotations are augmented in a future task.

**Speaker demographics.** Six named speakers with non-native accents: French (NoemieMarciano),
French/Spanish (StephaniaCesborn), German (ErcanKilic), Hebrew (FelixTseitlin), Korean (JemmaLee),
Russian (OlyaShtalberg), plus an English-native production pool. This accent diversity is important
for the literature survey: techniques that improve entity accuracy on accented speech are more
valuable than those tested only on native-speaker benchmarks.

**Source stratification.** The `source` field separates three provenance categories: `"production"`
(~63 clips), `"clean_voices"` (~17 clips), `"error_cases"` (~13 clips). Error-case clips were
selected precisely because production Deepgram failed on them, making entity accuracy on this
stratum the hardest and most diagnostic sub-benchmark.

### Observed Entity Failure Modes Relevant to Technique Selection

Manual inspection of `gold_set.jsonl` [t0001] documented specific error patterns that directly
constrain which techniques the literature survey should prioritize:

* Deepgram Nova-2 fails on: proper nouns ("Rezolve AI" → "resolve AI", "NASDAQ" → "nas dag",
  "Salesforce" → "sales force").
* Whisper Large v2 shows a different error profile — sometimes more accurate on brand names but
  less consistent on accented speech.
* The two systems exhibit *complementary* errors, suggesting that an ensemble or routing approach
  may outperform either alone.

These patterns map directly to two of the four technique categories in the survey scope:

1. **Contextual biasing** — the current Whisper Turbo pipeline already uses dynamic context
   injection (runtime hotword list). Gold-92 evidence shows this is insufficient for investor-
   relations proper nouns, motivating the search for stronger biasing or post-correction approaches.
2. **LLM post-correction** — the complementary error profiles of Deepgram and Whisper suggest a
   second-pass corrector with entity grounding could close remaining gaps.

### Evaluation Metrics Already Registered

The project has registered six metrics for evaluation against gold-92 (from the dataset description
[t0001]):

* `entity_accuracy_gold92` — primary metric; entity names correct vs. total
* `intent_preservation_gold92`
* `action_critical_wer_gold92`
* `wer_gold92`
* `wrong_action_rate_gold92`
* `latency_p50_seconds` — must stay under 0.800 s p50

Statistical testing requirement: BCa bootstrap with 10 000 resamples on all 93 paired samples
against the production Deepgram baseline. The literature survey should note whether any surveyed
papers use comparable evaluation protocols (entity-level accuracy, bootstrap significance) when
assessing the credibility of their reported gains.

### No Prior Code to Reuse

t0001 is a data-ingestion task that produced no code (`code/` directory absent). Its research file
(`tasks/t0001_stt_benchmark/research/research_code.md`) contains only placeholder text ("No code
research required for dataset ingestion"). The current task is a pure literature survey requiring
no implementation code, so the absence of reusable code from t0001 has no impact on execution.

---

## Dataset Landscape

| Dataset ID | Task | Location | Format | Size | Status |
|---|---|---|---|---|---|
| `stt-benchmark-gold-92` | t0001_stt_benchmark | `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/` | JSONL + DVC audio | 93 clips, ~58 MB | DVC-tracked |

**Access.** Audio requires `dvc pull` with the Azure connection string from the team vault
(`.dvc/config.local`). JSONL annotation files are committed to git and available without DVC.

**Usage constraint.** Gold-92 is held-out only. It must never be used for training, fine-tuning,
validation loss monitoring, or few-shot example selection. Its sole permitted use is regression
evaluation.

**Bearing on the literature survey.** When assessing surveyed papers, the literature reviewer
should flag whether techniques can be evaluated on gold-92 as-is (entity substring match on
`ground_truth.jsonl`) or whether they require span-level entity annotations (not yet present).
Techniques that require entity-annotated training data are of lower immediate utility unless a
separate annotated training set is available.

---

## Reusable Code and Assets

### Dataset Asset: stt-benchmark-gold-92

* **Source:** t0001_stt_benchmark —
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` (36 KB,
  93 records) and `files/ground_truth.jsonl` (16 KB, 91 records).
* **What it does:** Provides the ground-truth transcripts, existing Deepgram and Whisper hypotheses,
  clip provenance labels, and audio pointers needed for all downstream STT evaluation.
* **Reuse method:** These are data files, not code. Load them directly by path — no import needed.
  The evaluation protocol (BCa bootstrap, 10 000 resamples, 93 paired samples) is documented in the
  dataset description but not yet implemented in any code module; implementation is deferred to
  t0002_baseline_evaluation.
* **Adaptation needed for t0003:** None. This is a literature survey — no code runs against the
  dataset. However, the annotation schema (fields, entity types, speaker stratification) informs
  the survey's inclusion/exclusion criteria and the "Comparison Against Whisper Turbo + Dynamic
  Context Injection" section.

There is no registered library code or task code to import or copy for this task.

---

## Lessons Learned

**t0001: DVC-first data management works cleanly for audio.** The pattern of committing JSONL
annotations to git and audio to DVC (via Azure Blob) kept the git repository lightweight while
making the full dataset reproducible. Future evaluation tasks should follow the same pattern: small
metadata files in git, large binary files via `dvc add` + `dvc push`.

**t0001: Annotation completeness gaps should be flagged early.** The two-record discrepancy between
`gold_set.jsonl` (93) and `ground_truth.jsonl` (91) was noted but not resolved in t0001; it is
deferred to t0002. For the literature survey, this is not a blocker, but it is a reminder that
annotation QA should be a dedicated step in any future dataset task.

**t0001: Entity types are implicit, not explicit.** The gold-92 schema has no entity span
annotations (type labels, offsets). This limits evaluation to WER and substring-match entity
accuracy. Techniques that require span-level entity annotations (e.g., entity-conditioned decoding
with typed spans) cannot be evaluated on gold-92 in its current form. The literature survey should
explicitly note this limitation when ranking the shortlist for follow-on prototyping.

**No implementation pitfalls from prior tasks** — t0001 was a straightforward data-ingestion task
with no code, so there are no debugging insights or performance edge cases to transfer.

---

## Recommendations for This Task

1. **Use gold-92 annotation schema as the survey's evaluation filter.** When assessing each
   surveyed paper, check whether its claimed entity accuracy gains were measured with metrics
   compatible with what gold-92 supports: WER, entity substring match, or entity recall/precision
   on named spans. Papers measured only on internal ecommerce datasets without disclosed metrics
   should be flagged as lower-confidence.

2. **Prioritize techniques that do not require span-level entity training annotations.** Gold-92 has
   no entity span labels. Contextual biasing and LLM post-correction approaches that operate on
   word-level or phrase-level hypotheses without requiring typed entity spans are more immediately
   prototypable on this benchmark.

3. **Flag accent robustness as a first-class criterion.** The gold-92 speaker pool (six non-native
   accents) makes accent robustness directly relevant. Papers that evaluate only on native-English
   benchmarks should be noted as lower-priority unless their technique is accent-agnostic by design.

4. **Note the complementary error profiles** of Deepgram Nova-2 and Whisper Large v2 observed in
   [t0001] as motivation for the LLM post-correction and shallow fusion categories: if the two
   systems make different errors on the same entities, a post-correction layer or a fusion
   architecture could recover accuracy that neither system achieves alone.

5. **Adopt the `source` stratification for future reporting.** The `error_cases` stratum (~13
   clips selected because production Deepgram failed) is the hardest sub-benchmark. The shortlist
   of techniques should be assessed against this stratum in addition to the full 93-clip set in any
   follow-on evaluation task.

6. **No libraries to import; no code to copy.** The project has zero registered libraries. The
   literature survey requires no implementation code. Research output is a synthesis document plus
   paper assets; no scripts need to be written for this task.

---

## Task Index

### [t0001]

* **Task ID**: t0001_stt_benchmark
* **Name**: STT Benchmark — Gold-92 Dataset Ingestion
* **Status**: completed
* **Relevance**: t0001 produced the `stt-benchmark-gold-92` dataset — the canonical held-out
  evaluation set for all STT research in this project. Its annotation schema (fields, entity types,
  speaker demographics), entity failure observations (Deepgram vs. Whisper error profiles), and
  registered evaluation metrics directly define the evaluation contract that the literature survey's
  technique shortlist must satisfy.
