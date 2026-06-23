---
spec_version: "1"
task_id: "t0002_baseline_evaluation"
research_stage: "code"
tasks_reviewed: 1
tasks_cited: 1
libraries_found: 0
libraries_relevant: 0
date_completed: "2026-06-23"
status: "complete"
---

## Task Objective

Establish project baselines by running Deepgram Nova-2 (the current Rezolve production STT
endpoint) and Whisper Large v3 (the leading open-source alternative) on the gold-92 benchmark: 93
annotated WAV clips from Rezolve production voice sessions in the investor-relations and ecommerce
domain with accented English speakers. All five registered project metrics must be computed with BCa
bootstrap 95% confidence intervals (n=10,000 resamples): entity accuracy on action-critical spans
(`entity_accuracy_gold92`), full-transcript WER (`wer_gold92`), action-critical WER
(`action_critical_wer_gold92`), intent preservation (`intent_preservation_gold92`), and end-to-end
latency p50 (`latency_p50_seconds`). A paired BCa bootstrap significance test comparing Whisper
Large v3 vs. Deepgram on `entity_accuracy_gold92` is the primary deliverable. Results are output as
two predictions assets: `predictions/deepgram-nova2-gold92` and
`predictions/whisper-large-v3-gold92`, each containing `predictions.json` and `metadata.json`.

## Library Landscape

The library aggregator returned zero registered libraries in this project. The project is in its
early phases (only one completed task: [t0001]) and no reusable code has been promoted to library
status yet. All cross-task code reuse for this task must therefore use the "copy into task" method.

Key third-party libraries needed for implementation — available as Python packages via `uv add` but
not registered as project libraries:

* **jiwer** — WER, MER, WIL, CER computation; `process_words` provides word-level alignment for
  entity-span WER isolation. Not yet in `pyproject.toml`; must be added.
* **deepgram-sdk** (≥3.0) — Deepgram Nova-2 API client; `listen.v1.media.transcribe_file` is the
  current interface. Not in `pyproject.toml`; must be added.
* **faster-whisper** — CTranslate2-backed Whisper inference; 4× speedup over openai-whisper on GPU.
  Not in `pyproject.toml`; must be added.
* **scipy** (≥1.7) — `scipy.stats.bootstrap` with `method='BCa'` is the project-specified CI
  implementation. Already present in `pyproject.toml` (`scipy>=1.0`).
* **numpy** (≥2.0) — array operations for per-utterance metric vectors. Already present in
  `pyproject.toml`.

No library corrections or replacements are relevant since no libraries exist yet.

## Dataset Landscape

The sole dataset asset is `stt-benchmark-gold-92`, produced by [t0001], located at:

```
tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/
```

**Files in git**:

* `files/gold_set.jsonl` — 93 records; full schema: `clip_id`, `source`, `filename`,
  `ground_truth`, `production` (Deepgram Nova-2 production transcript), `whisper` (Whisper Large v2
  transcript). This file contains existing baseline hypotheses that may be used as a quick sanity
  check but must not substitute for fresh inference.
* `files/ground_truth.jsonl` — 93 records; simplified: `clip_id` and `ground_truth` only. This is
  the canonical reference for all WER and entity accuracy computation.

**Files in DVC** (must be retrieved with `dvc pull`):

* `files/audio/` — 93 WAV files, ~58 MB total (60,210,752 bytes per `audio.dvc`), Azure Blob
  remote `azure://ml-dvc-datasets/datasets/rail-arf-stt`.

**Dataset schema details** (from inspecting `gold_set.jsonl`):

* `clip_id` format: either `{Language}_{Speaker}__{lang}-{Speaker}-q{NN}` (curated clean-voice
  clips) or `{UUID}_turn{N}` (production session clips) or `error_en_{NNNN}` (known-error clips).
* `source` values: `"clean_voices"` (17 clips), `"production"` (~63 clips), `"error_cases"` (~13
  clips). This `source` field is the stratification variable for per-source breakdown tables.
* Audio format: WAV, nominally mono 16 kHz, 2–8 seconds per clip.
* Named speakers: French/NoemieMarciano (6 clips), French/StephaniaCesborn (7 clips),
  German/ErcanKilic (7 clips), Hebrew/FelixTseitlin (5 clips), Korean/JemmaLee (7 clips),
  Russian/OlyaShtalberg (7 clips), plus unattributed production pool and error cases.
* Accent group is inferable from `clip_id` prefix for curated clips; production and error clips do
  not carry explicit speaker labels.

**Important data quality note**: `ground_truth.jsonl` contains a slightly different normalisation
than `gold_set.jsonl` for some clips (e.g., "Brain Commerce" vs. "Brain Commerce" capitalisations,
trailing punctuation differences). Always use `ground_truth.jsonl` as the reference; do not derive
references from `gold_set.jsonl`'s `ground_truth` field.

## Key Findings

### Dataset Is Ready; Audio Requires DVC Pull

The gold-92 dataset was fully ingested by [t0001]. JSONL annotation files are committed to git and
immediately accessible. The 93 WAV audio files are DVC-tracked and require `dvc pull` to
materialise at `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/`. The
DVC pointer file (`audio.dvc`) records md5 `0ee9d110f56cb9db9e25f814d10bed16.dir`, 93 files,
60,210,752 bytes total — this can be used to verify successful pull.

No code for loading or processing the dataset was produced by [t0001], as that task was purely a
data ingestion task with no computation. All loading, inference, and metric computation code must be
written from scratch in `tasks/t0002_baseline_evaluation/code/`.

### Existing Hypotheses in gold_set.jsonl Are Not Adequate Baselines

The `gold_set.jsonl` file contains `production` (Deepgram Nova-2) and `whisper` (Whisper Large
**v2**, not v3) hypotheses pre-populated from the original benchmark curation. These cannot be used
as the task's prediction outputs because:

1. The `production` column contains Nova-2 transcripts captured at various timestamps during Rezolve
   production sessions — not a controlled re-run with consistent API settings, timing measurement,
   or format parameters (`smart_format`, `punctuate`).
2. The `whisper` column is Whisper Large **v2**, not v3. The task requires v3 inference.
3. Latency data is entirely absent from `gold_set.jsonl` — all latency must be measured freshly.

The existing hypotheses are useful as sanity-check references during development (expected to
roughly agree with fresh Nova-2 inference) but must not substitute for fresh runs.

### Entity Failure Patterns Are Observable from gold_set.jsonl

Inspection of `gold_set.jsonl` reveals systematic entity transcription failures that the task's
metrics must capture:

* **"Rezolve AI" → "resolve AI"** or "Hezos": Whisper misidentifies the brand name on accented
  audio; production Nova-2 is inconsistent (correct on clean-voice clips, wrong on production clips
  like `da47fc8f` turn2 where it produces "CEO of Hezos").
* **"brainpowa" → "brain power" or "brain powr"**: both systems hallucinate the product name on
  accented speech (`error_en_0020`).
* **"Shopify Plus", "Salesforce Commerce Cloud", "Adobe"**: both systems handle multi-word platform
  names well on clean-voice clips but Whisper incorrectly segments "Salesforce, Commerce Cloud" with
  a comma for German and Hebrew speakers.
* **"20-F" → "20f"**: Whisper drops the hyphen in form designators, which matters for IR entity
  accuracy.
* **Production clips show hallucinated prefix insertion**: Nova-2 on `error_en_0009` adds "And I've
  heard about Rezolve Ai and your product for e-commerce." before the actual utterance — a severe
  hallucination not present in the reference. These cases inflate Deepgram WER in production clips.

These patterns confirm that entity accuracy on action-critical spans will diverge substantially from
full-transcript WER, justifying the separate `entity_accuracy_gold92` and
`action_critical_wer_gold92` metrics.

### BCa Bootstrap Implementation Is Straightforward with scipy

The `scipy.stats.bootstrap` function (available in the project's current `scipy>=1.0` dependency)
supports BCa natively via `method='BCa'`. For this task with 93 paired samples, the pattern is:

```python
from scipy import stats
import numpy as np

boot = stats.bootstrap(
    (per_utterance_scores,), np.mean,
    n_resamples=10_000, method='BCa', random_state=42
)
ci_low, ci_high = boot.confidence_interval
```

For the paired Whisper-vs-Deepgram significance test on `entity_accuracy_gold92`:

```python
def paired_diff(x, y, axis):
    return np.mean(x - y, axis=axis)

boot = stats.bootstrap(
    (whisper_entity_scores, deepgram_entity_scores),
    paired_diff, n_resamples=10_000, method='BCa', paired=True, random_state=42
)
```

A CI excluding zero constitutes significance at α=0.05. Edge case: if all scores are identical,
BCa returns NaN — add a fallback to `method='percentile'` with a logged warning.

### Speaker Correlation Requires Bootstrap Method Choice

The gold-92 dataset has multiple clips from the same named speaker (e.g., 6–7 clips per
German/French/Korean/Hebrew/Russian speaker). Standard i.i.d. BCa assumes clip independence. Liu &
Peng (2020) demonstrate this is biased for speaker-correlated ASR evaluation sets. For the curated
clean-voice portion (~40 clips from 6 named speakers), blockwise bootstrap with speaker-grouped
blocks is more statistically sound. The `source` and `clip_id` fields provide the grouping
information.

Practically, this means the implementation should support both modes and document the choice in
`metadata.json`. For the primary reported result (all 93 clips), standard BCa is a reasonable
approximation given the mixed production/clean-voice composition. A supplementary blockwise result
on the clean-voice subset is advisable.

### WER Normalisation Must Be Consistent

The `ground_truth.jsonl` transcripts include capitalised entity names ("Rezolve AI", "Brain
Commerce", "Shopify Plus"), punctuation, and mixed-case strings. WER computation with `jiwer`
requires consistent normalisation of both reference and hypothesis before comparison:

```python
from jiwer import wer, process_words
import re

def normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # strip punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text

wer_score = wer(
    [normalise(ref) for ref in references],
    [normalise(hyp) for hyp in hypotheses]
)
```

For `entity_accuracy_gold92`, exact case-insensitive match after normalisation is required per the
metric definition: "A span is correct if the predicted text exactly matches the ground-truth
annotation after normalisation."

### No Shared Evaluation Code Exists Yet — All Must Be Written

Because [t0001] produced no code (data ingestion only), this task must implement all of the
following from scratch in `tasks/t0002_baseline_evaluation/code/`:

1. `load_dataset.py` — load `gold_set.jsonl` and `ground_truth.jsonl`, build clip records, resolve
   audio file paths.
2. `run_deepgram.py` — batch Deepgram Nova-2 transcription with timing, retry logic, raw output
   serialisation to `data/deepgram_transcripts.json`.
3. `run_whisper.py` — Whisper Large v3 transcription via `faster-whisper`, with `language="en"`,
   per-clip timing, raw output serialisation to `data/whisper_transcripts.json`.
4. `compute_metrics.py` — WER, action-critical WER, entity accuracy (span-level exact match), intent
   preservation, latency p50; BCa bootstrap CI for each metric; paired significance test.
5. `generate_predictions_asset.py` — write `predictions.json` and `metadata.json` for each of the
   two predictions assets.

## Reusable Code and Assets

### Gold-92 Dataset Files

**Source**: `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/` (produced by
[t0001])

**What it provides**:

* `gold_set.jsonl` (93 lines, ~24 KB): full annotation records including `clip_id`, `source`,
  `filename`, `ground_truth`, `production` hypothesis, `whisper` (v2) hypothesis.
* `ground_truth.jsonl` (93 lines, ~6 KB): simplified `clip_id` + `ground_truth` for reference
  lookup.
* `audio/` (93 WAV files, ~58 MB, DVC-tracked): the audio inputs for inference.

**Reuse method**: reference in place — no copying needed. Load from the canonical path:

```python
DATASET_ROOT = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files")
GOLD_SET = DATASET_ROOT / "gold_set.jsonl"
GROUND_TRUTH = DATASET_ROOT / "ground_truth.jsonl"
AUDIO_DIR = DATASET_ROOT / "audio"
```

**Adaptation needed**: none — paths are stable since [t0001] is completed. The DVC audio directory
must be materialised with `dvc pull` before any inference script runs.

### No Library or Task Code to Copy

There are zero registered libraries in this project and [t0001] produced no Python code. All
evaluation scripts must be written fresh. The implementation subagent should use the code structure
recommendations in the Key Findings section above.

## Lessons Learned

### From t0001: Dataset Ingestion Pitfalls

* The DVC pointer was committed but `dvc push` had a dependency on the Azure connection string being
  configured in `.dvc/config.local`. Any agent running this task must verify `dvc pull` succeeds
  before attempting inference. If pull fails, the audio files will be absent and inference will
  throw file-not-found errors rather than API errors.
* The `ground_truth.jsonl` line count per the plan's verification criteria was stated as 91 lines,
  but the actual file has 93 records (one per clip). This discrepancy in the plan's verification
  criteria should not be used to validate the dataset — count actual lines in the file.
* The `error_en_0005` clip has a ground_truth of `"ы"` (a single Cyrillic character), which is
  almost certainly an annotation error (the audio likely contains a short non-speech sound or
  whispered/barely-audible utterance). This clip will skew WER calculations — consider flagging and
  possibly excluding from reported metrics, or note it explicitly in results.

### Production vs. Clean-Voice Clip Behaviour

Manual inspection of `gold_set.jsonl` reveals that the `production` (Deepgram) column is accurate
on clean-voice clips but shows hallucination and prefix-insertion artefacts on production session
clips. For example, Nova-2 generates full marketing sentences ("How does Rezolve transform…") where
the reference is only a short interjection ("ы"). This suggests the production transcripts in
`gold_set.jsonl` were captured from a live Rezolve demo session where the LLM context may have
contaminated or the mic picked up ambient audio. Fresh Deepgram API calls on the raw WAV files
should not reproduce these hallucinations, but the discrepancy should be verified.

### Entity Names Are Case-Sensitive in gold_set.jsonl

Ground-truth transcripts use specific capitalisation: "Rezolve AI", "Brain Commerce", "brainpowa"
(always lowercase), "Shopify Plus", "Salesforce Commerce Cloud", "NASDAQ". Normalisation for WER
must lowercase both reference and hypothesis. Entity accuracy must be computed on normalised
lowercase forms to avoid penalising Whisper for returning "rezolve ai" vs. "Rezolve AI".

## Recommendations for This Task

1. **Run `dvc pull` first** — before any inference, run
   `dvc pull tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio.dvc`
   and verify exactly 93 WAV files are present. Fail loudly if the count is wrong.

2. **Load from `ground_truth.jsonl` for references, `gold_set.jsonl` for metadata** — use
   `ground_truth.jsonl` as the authoritative reference source; use `gold_set.jsonl` for `source`
   stratification and sanity-checking only. Never use `gold_set.jsonl`'s `production` or `whisper`
   columns as the baseline hypotheses — re-run inference.

3. **Implement normalisation once and share it** — define a single `normalise(text: str) -> str`
   function in `compute_metrics.py` that lowercases and strips punctuation; call it for both
   references and hypotheses in WER and entity accuracy computation. Inconsistent normalisation is
   the most common source of inflated or deflated WER numbers.

4. **Flag `error_en_0005`** — this clip has ground_truth `"ы"` (a single Cyrillic character). Log a
   warning, include it in the full 93-clip run for completeness, but add a note in `metadata.json`
   explaining the anomalous reference. Check whether it skews aggregate metrics.

5. **Use `faster-whisper` not `openai-whisper`** — add `faster-whisper` as a dependency, load with
   `WhisperModel("large-v3", device="cpu", compute_type="int8")` for CPU or `device="cuda",
   compute_type="float16"` for GPU. Always pass `language="en"` to prevent accent
   misclassification. Record package version in `metadata.json`.

6. **Use `deepgram-sdk>=3.0`** — add as a dependency; use
   `DeepgramClient().listen.v1.media.transcribe_file()` with `smart_format=True` and
   `punctuate=True`. Measure per-clip latency with `time.perf_counter()` around the API call; do
   not rely on `response.metadata.duration` which reports audio duration, not processing time.

7. **Implement BCa with a degenerate fallback** — use `scipy.stats.bootstrap(method='BCa',
   n_resamples=10_000, random_state=42)`. If `confidence_interval.low` is NaN, fall back to
   `method='percentile'` and log a warning in `metadata.json`.

8. **Document blockwise bootstrap decision** — inspect the clip_id prefixes to determine whether
   the clean-voice subset has enough clips per speaker for blockwise bootstrap. Record the decision
   (standard BCa vs. blockwise) in `metadata.json` with a brief rationale.

9. **Preserve raw outputs before metric computation** — write `data/deepgram_transcripts.json` and
   `data/whisper_transcripts.json` (as specified in `task_description.md`) before computing any
   metrics. This enables re-running the metric computation without re-running expensive inference.

10. **Use the `source` field for per-source breakdown** — the results tables must include a
    per-accent-group / per-source breakdown. Use `gold_set.jsonl`'s `source` field (`clean_voices`,
    `production`, `error_cases`) and the `clip_id` prefix (for named speaker accent groups) to
    stratify results.

## Task Index

### [t0001]

* **Task ID**: t0001_stt_benchmark
* **Name**: STT Benchmark — Gold-92 Dataset Ingestion
* **Status**: completed
* **Relevance**: The sole dependency for this task. Produced the gold-92 dataset asset
  (`stt-benchmark-gold-92`) containing 93 annotated WAV clips with ground-truth transcripts. The
  dataset files (`gold_set.jsonl`, `ground_truth.jsonl`, DVC-tracked `audio/`) are the inputs for
  all Deepgram and Whisper inference in this task. Produced no code; all evaluation scripts must be
  written from scratch.
