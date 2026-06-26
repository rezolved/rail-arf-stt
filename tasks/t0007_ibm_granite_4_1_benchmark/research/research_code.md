---
spec_version: "1"
task_id: "t0007_ibm_granite_4_1_benchmark"
research_stage: "code"
tasks_reviewed: 5
tasks_cited: 4
libraries_found: 0
libraries_relevant: 0
date_completed: "2026-06-25"
status: "complete"
---
# Research Code: Benchmark IBM Granite Speech 4.1 2B on Gold-92

## Task Objective

This task benchmarks IBM Granite Speech 4.1 2B (`ibm-granite/granite-speech-4.1-2b`) against the
gold-92 held-out evaluation set. Two runs are required: (1) batch inference with no keyword biasing,
and (2) batch inference with the 31-term Rezolve domain vocabulary injected via Granite's native
keyword biasing API (shallow fusion at beam-search time). The primary question is whether Granite
keyword-biased can match or exceed the Whisper large-v3 + `initial_prompt` baseline
(`entity_accuracy_domain_vocab` = 94.5%, WER = 8.5%, AC-WER = 2.5%) established by [t0004].
Secondary outputs are a per-segment latency measurement to assess feasibility against the 200 ms p50
target and a qualitative streaming / NAR path assessment. Granite was ranked #1 on the HuggingFace
Open ASR Leaderboard (5.33% mean WER, April 2026) and flagged as the primary benchmark candidate by
[t0005].

* * *

## Library Landscape

The library aggregator reports **zero registered libraries** in this project:

```json
{"library_count": 0, "libraries": []}
```

No cross-task library imports are available. All reusable code must be copied into
`tasks/t0007_ibm_granite_4_1_benchmark/code/`. This is consistent with prior tasks ([t0002],
[t0004]), which also copied evaluation utilities rather than registering libraries.

* * *

## Key Findings

### Dataset Loading and the Cyrillic Anomaly

All benchmark tasks use a consistent pattern for loading gold-92 data [t0002][t0004]. The canonical
entry point is `load_gold92()` in each task's `code/load_dataset.py`, which reads from two JSONL
files:

* `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl` —
  canonical 93-record ground truth index (`clip_id`, `ground_truth`). This file is the reference
  source, **not** `gold_set.jsonl`.
* `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` — used only
  for `accent_group` stratification metadata.

The `load_gold92()` function returns a list of `GoldClip` dataclasses sorted by `clip_id`. Each
`GoldClip` carries: `clip_id`, `reference_text`, `entity_spans` (heuristically inferred via regex),
`accent_group`, and `audio_path`.

Clip `error_en_0005` has a Cyrillic ground truth in `gold_set.jsonl` (known annotation error). Both
[t0002] and [t0004] handle this by excluding the clip from entity accuracy aggregate (via
`np.nanmean`) while including it in WER computation. The constant
`CYRILLIC_ANOMALY_CLIP = "error_en_0005"` is defined in both tasks' `load_dataset.py`.

### Entity Span Inference

Entity spans are not stored explicitly in `ground_truth.jsonl`. Both [t0002] and [t0004] use an
identical heuristic `_infer_entity_spans()` function (161-line `load_dataset.py` in each task) that
applies 22 regex patterns to detect domain entities: brands (`Rezolve AI`, `Rezolve`, `Adobe`,
`Shopify`, `Salesforce`, `Amazon`, `Google`, `Microsoft`), products (`brainpowa`, `Brain Commerce`,
`Shopify Plus`, etc.), and IR terms (`20-F`, `10-K`, `SEO`, `API`, `AI`, `ROI`, `KPI`).

The entity span detection uses `re.IGNORECASE`, so it matches capitalisation variants. Entity
accuracy is computed as all-or-nothing per span: the normalised span text must appear as a substring
in the normalised hypothesis (lowercase + stripped punctuation via `normalise()`).

### Metric Computation Architecture

The metric computation architecture is well-established across [t0002] and [t0004]. The
`SystemMetrics` dataclass and `compute_system_metrics()` function pattern appears in both tasks:

* **`compute_metrics.py`** ([t0002], 735 lines): computes WER, entity accuracy, AC-WER, intent
  preservation, latency p50, all with BCa bootstrap 95% CIs. Uses `jiwer.process_words()` for WER
  and `scipy.stats.bootstrap` with `method="BCa"`, `n_resamples=10_000`, `random_state=42`.
* **`compute_metrics_biased.py`** ([t0004], 722 lines): extends [t0002]'s metric module by adding
  `compute_entity_accuracy_domain_vocab()` and `compute_per_term_accuracy()`. This is the version
  needed for t0007, as `entity_accuracy_domain_vocab` is the primary comparison target.

The `normalise()` helper (lowercase + `str.maketrans("", "", string.punctuation)`) is used
consistently across entity accuracy, WER, and prediction asset generation.

### Domain Vocabulary — 31 Terms

The exact domain vocabulary used for biasing experiments is defined in
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py` (39 lines). The `DOMAIN_VOCAB` list
contains 31 terms:

```python
DOMAIN_VOCAB = ["Rezolve", "Rezolve Ai", "NASDAQ", "brainpowa", "Agentic",
                "Brain Checkout", "Brain Commerce", "Purchase Suite", "GroupBy",
                "Bluedot", "ViSenze", "Smartpay", "Subsquid", "CrownPeak",
                "Hallucinations", "Zero Hallucinations", "Dan Wagner", "Arthur Yao",
                "Richard Burchill", "Crispin Lowery", "Salman Ahmad", "Sauvik Banerjjee",
                "Mark Turner", "Peter Vesco", "Urmee Khan", "Anthony Sharp",
                "David Wright", "Steve Perry", "Derek Smith", "Justin King",
                "Christian Angermayer"]
```

`INITIAL_PROMPT: str = ", ".join(DOMAIN_VOCAB)` is the string used by Whisper's `initial_prompt`.
For Granite's keyword biasing API (shallow fusion), the same 31 terms should be passed as a keyword
list — the exact API parameter names must be confirmed against the HuggingFace model card for
`ibm-granite/granite-speech-4.1-2b`.

### Inference Script Pattern

The inference script pattern from [t0004]'s `run_whisper_biased.py` (178 lines) and
`run_whisper_turbo_biased.py` (180 lines) provides the template:

1. Parse `--limit` CLI flag for validation gate runs (e.g. `--limit 5`)
2. Load model
3. Run 3 warmup clips (throwaway) before recording latencies
4. Iterate clips with `tqdm`, measure `time.perf_counter()` per clip
5. Save `[{"clip_id": ..., "hypothesis": ..., "latency_seconds": ...}]` to JSON
6. Rejection check: raise `RuntimeError` if fewer than 80% of clips succeed
7. Print first 5 results for inspection

For GPU-based Granite inference, the model loading will use HuggingFace Transformers
(`transformers.AutoModelForSpeech2Text` or Granite-specific processor) rather than faster-whisper.
The per-clip latency measurement loop and warmup pattern transfer directly.

### Prediction Asset Schema

Both [t0002] and [t0004] use predictions asset spec v2 with JSONL format. Each JSONL record
contains: `clip_id`, `reference`, `hypothesis`, `accent_group`, `entity_spans_reference`,
`entity_spans_predicted` (list with `found: bool`), `entity_accuracy`, `wer`, `latency_seconds`,
`anomaly_flag`. The `details.json` file declares `spec_version: "2"`, `predictions_id`,
`instance_count: 93`, `dataset_ids: ["stt-benchmark-gold-92"]`, and `metrics_at_creation`.

The `write_prediction_asset()` function in
`tasks/t0004_vocabulary_biasing_experiment/code/write_predictions.py` (499 lines) is the most
complete and up-to-date implementation of this pattern — it handles all three prediction directories
in a single script and includes `description.md` generation.

### Metrics JSON Format

The `metrics.json` format uses explicit variant format as required by the task metrics verificator:

```json
{"variants": [{"variant_id": "...", "label": "...", "dimensions": {"model": "..."}, "metrics": {...}}]}
```

[t0004]'s `compute_metrics_biased.py` writes six metrics per variant: `entity_accuracy_gold92`,
`wer_gold92`, `action_critical_wer_gold92`, `intent_preservation_gold92`, `latency_p50_seconds`,
`entity_accuracy_domain_vocab`.

The `wrong_action_rate_gold92` metric is omitted (requires a confidence-routing policy) — documented
in `analysis_output.json`, not in `metrics.json`.

### Path Management Pattern

Each task defines a `paths.py` with task-specific path constants. The pattern is consistent:
`TASK_ROOT`, `GOLD92_AUDIO`, `GROUND_TRUTH_JSONL`, `GOLD_SET_JSONL`, `DATA_DIR`, `RESULTS_DIR`,
`PREDICTIONS_DIR`. Cross-task references point to the originating task's directory (e.g., [t0004]'s
`paths.py` includes `T0002_WHISPER_TRANSCRIPTS` pointing into t0002's `data/`).

For t0007, the paths.py will need constants for `GRANITE_BATCH_TRANSCRIPTS` and
`GRANITE_BIASED_TRANSCRIPTS` in addition to the standard gold-92 paths.

### t0004 Baseline Numbers (Comparison Target)

From [t0004]'s `results_summary` (definitive, verified):

| Variant | EA gold-92 | EA domain vocab | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| Whisper large-v3 + bias | 46.0% | **94.5%** | 8.5% | **2.5%** | 98.9% | 6.66s |
| Whisper turbo + bias | 43.1% | 87.3% | 8.3% | 5.1% | 96.8% | 5.86s |

These are the primary comparison targets for t0007. The Whisper large-v3 biased predictions are
accessible at
`tasks/t0004_vocabulary_biasing_experiment/assets/predictions/whisper-large-v3-biased/`.

* * *

## Dataset Landscape

The gold-92 dataset ([t0001]) is DVC-tracked at
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/`:

* `audio/` — 93 WAV files (PCM-16 mono, 16 kHz), DVC-managed via `audio.dvc`
* `ground_truth.jsonl` — 93 records with `clip_id` and `ground_truth`
* `gold_set.jsonl` — 93 records with full annotation schema including `source` (accent group)

The dataset contains three source categories: `clean_voices` (~40 clips, 6 named speakers),
`production` (~40 live session captures), `error_cases` (~13 hard cases). The production subset (8
accented English clips from live sessions) is the hardest stratum — Whisper without biasing scored
only 8.8% entity accuracy on it [t0002].

Before running t0007 inference, `dvc pull` must be run to download the audio files if they are not
already present locally.

* * *

## Common Patterns

### BCa Bootstrap CI

All metric files use `scipy.stats.bootstrap` with `method="BCa"`, `n_resamples=10_000`,
`random_state=42`. Both [t0002] and [t0004] implement an identical NaN-guard fallback to percentile
bootstrap if BCa returns NaN. This guard is critical for small strata (production subset, ~8 clips).

### Warmup Clips

Both [t0002] and [t0004] run 3 throwaway warmup clips before recording latencies to warm CPU cache.
For GPU inference (t0007), warmup is still recommended but may need a different mechanism (e.g.,
single dummy forward pass through the model).

### Rejection Criterion

Both inference scripts reject results if fewer than 80% of clips succeed (`RuntimeError` if
`success_count / total < 0.8`). Additionally, both metric scripts reject if any system's WER > 0.6
(likely inference failure). These checks should be carried into t0007.

* * *

## Reusable Code and Assets

### 1. `load_dataset.py` — Gold-92 Dataset Loader

**Source**: `tasks/t0004_vocabulary_biasing_experiment/code/load_dataset.py` (161 lines)

**What it does**: Loads all 93 gold-92 clips as `GoldClip` dataclasses. Reads ground truth from
`ground_truth.jsonl`, accent groups from `gold_set.jsonl`, infers entity spans via 22 regex
patterns. Handles the Cyrillic anomaly clip (`error_en_0005`) with a warning.

**Reuse method**: **copy into task** (no library registered)

**Key function**:

```python
def load_gold92(
    *,
    ground_truth_path: Path = GROUND_TRUTH_JSONL,
    gold_set_path: Path = GOLD_SET_JSONL,
    audio_dir: Path = GOLD92_AUDIO,
) -> list[GoldClip]:
    ...
```

**Adaptation needed**: Update `paths` import to reference t0007's own `paths.py`. The `GoldClip`
dataclass and `_infer_entity_spans()` logic are unchanged.

### 2. `compute_metrics_biased.py` — Full Metric Computation

**Source**: `tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py` (722 lines)

**What it does**: Computes all six registered metrics (`entity_accuracy_gold92`,
`entity_accuracy_domain_vocab`, `wer_gold92`, `action_critical_wer_gold92`,
`intent_preservation_gold92`, `latency_p50_seconds`) for multiple variants. Includes
`compute_entity_accuracy_domain_vocab()`, `compute_per_term_accuracy()`, BCa CIs, and writes both
`results/metrics.json` and `data/analysis_output.json`.

**Reuse method**: **copy into task**

**Key functions**:

```python
def compute_system_metrics(
    *, variant_id: str, label: str, model_dim: str, clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]], anomaly_clips: set[str], domain_vocab: list[str],
) -> SystemMetrics: ...

def compute_entity_accuracy_domain_vocab(
    *, clips: list[GoldClip], transcripts: dict[str, dict[str, Any]], domain_vocab: list[str],
) -> tuple[float, list[float | None]]: ...

def compute_per_term_accuracy(
    *, clips: list[GoldClip], transcripts_by_variant: dict[str, dict[str, dict[str, Any]]],
    domain_vocab: list[str], variant_ids: list[str],
) -> list[dict[str, Any]]: ...
```

**Adaptation needed**: Update all imports (paths, constants, load_dataset) to reference t0007's own
modules. Remove references to Moonshine and Whisper-specific variant IDs; replace with Granite
variant IDs (`granite-4.1-2b-batch`, `granite-4.1-2b-biased`).

### 3. `constants.py` — Domain Vocabulary

**Source**: `tasks/t0004_vocabulary_biasing_experiment/code/constants.py` (39 lines)

**What it does**: Defines `DOMAIN_VOCAB` (31-term list) and `INITIAL_PROMPT` string. This is the
authoritative source for the biasing vocabulary — the same 31 terms must be used in t0007.

**Reuse method**: **copy into task**

**Adaptation needed**: None for the vocabulary list. `INITIAL_PROMPT` is for Whisper only; for
Granite's keyword biasing API, the implementation must pass `DOMAIN_VOCAB` as a list to the
appropriate Granite processor parameter (to be confirmed against model card).

### 4. `write_predictions.py` — Prediction Asset Writer

**Source**: `tasks/t0004_vocabulary_biasing_experiment/code/write_predictions.py` (499 lines)

**What it does**: Writes complete prediction asset folders (JSONL + `details.json` +
`description.md`) conforming to predictions asset spec v2. Includes `write_prediction_asset()` and
`write_description_md()`.

**Reuse method**: **copy into task**

**Key function**:

```python
def write_prediction_asset(
    *, predictions_id: str, name: str, short_description: str, model_description: str,
    output_dir: Path, clips: list[GoldClip], transcripts: dict[str, dict[str, Any]],
    latency_p50: float, entity_accuracy_gold92: float, wer_gold92: float,
) -> None: ...
```

**Adaptation needed**: Update `created_by_task` to `"t0007_ibm_granite_4_1_benchmark"`,
`date_created` to today, and `categories` to include `stt-evaluation`, `granite-benchmark`. Update
model description strings for Granite 4.1 2B.

### 5. `run_whisper_biased.py` — Inference Script Template

**Source**: `tasks/t0004_vocabulary_biasing_experiment/code/run_whisper_biased.py` (178 lines)

**What it does**: Template for clip-by-clip inference with tqdm progress, warmup loop, per-clip
latency measurement, `--limit` CLI flag, 80% success rejection criterion, and JSON output.

**Reuse method**: **copy into task** (as `run_granite_batch.py` and `run_granite_biased.py`)

**Adaptation needed**: Replace `faster_whisper.WhisperModel` with HuggingFace Transformers Granite
model/processor. Replace `model.transcribe(str(audio_path), language="en", initial_prompt=...)` with
Granite's inference API. For keyword biasing, add the domain vocab list to the Granite processor
call. The per-clip timing, warmup, rejection criterion, and JSON output structure remain identical.

### 6. Gold-92 Dataset (DVC Asset)

**Source**: `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`

**What it does**: 93 WAV clips (PCM-16 mono, 16 kHz) plus annotation JSONL files.

**Reuse method**: Referenced by path — not copied. Requires `dvc pull` before inference.

**Audio path**:
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/{clip_id}.wav`

* * *

## Lessons Learned

### Entity Accuracy Jumps with Biasing — But Results Vary by Model

[t0004]'s key finding: `initial_prompt` biasing raised domain-vocab entity accuracy from 18.2% to
94.5% (large-v3) — a 5× improvement — with no WER degradation (WER actually improved slightly from
10.0% to 8.5%). However, Moonshine base (no biasing support) scored only 10.9% domain-vocab entity
accuracy, and AC-WER of 41.1% vs. 2.5% for biased large-v3. Model architecture matters: a faster
model without biasing is far weaker on domain entities.

### Production Subset Is the Hardest Stratum

Without biasing, both Whisper models scored only 8.8% entity accuracy on production clips [t0002].
With biasing [t0004], the production subset entity accuracy was not explicitly reported but the
aggregate improved significantly. For t0007, reporting stratified results on the production subset
(8 accented English clips) is mandatory per the task description.

### CPU Latency Is Incompatible with 800 ms Budget

Whisper large-v3 with biasing ran at 6.66 s p50 on CPU [t0004]. Moonshine achieved 70 ms p50 but at
much lower accuracy. For Granite (batch-only, NAR), GPU inference (A100/H100) is required to hit the
≤200 ms p50 per-segment target. The 80 ms improvement from Moonshine was achieved at severe entity
accuracy cost, confirming that speed/accuracy tradeoffs are steep.

### `ground_truth.jsonl` Is the Canonical Reference

[t0002] discovered that `gold_set.jsonl` has normalisation inconsistencies and should not be used as
the reference for metric computation. The canonical file is `ground_truth.jsonl`. Both tasks
document this prominently in their `load_dataset.py` docstrings.

### BCa NaN Guard Is Necessary

[t0002] and [t0004] both implement a NaN fallback in `bca_ci()`. On small strata (production subset,
~8 clips), BCa can return NaN due to insufficient resampling diversity. The percentile fallback
prevents crash but should be flagged in output.

### Rejection Criteria Prevent Silent Failures

[t0004] introduced an 80% success threshold on inference (raise `RuntimeError` on failure) and a WER
\> 0.6 check at metric computation time. These prevented silent propagation of empty transcripts
into metric computation.

### Per-Term Domain Vocabulary Breakdown Is High-Value

[t0004]'s `compute_per_term_accuracy()` function produces a per-term breakdown showing which of the
31 domain terms were still misrecognised after biasing. This is directly useful for diagnosing
Granite's biasing effectiveness and should be included in t0007 results.

* * *

## Recommendations for This Task

1. **Copy four files from [t0004]** as the foundation: `load_dataset.py`,
   `compute_metrics_biased.py`, `constants.py`, and `write_predictions.py`. These are the most
   complete and verified versions of the evaluation harness. Update all imports to reference t0007's
   own modules.

2. **Create two new inference scripts** (`run_granite_batch.py` and `run_granite_biased.py`) using
   [t0004]'s `run_whisper_biased.py` (178 lines) as the template. Replace only the model loading and
   transcription call; keep the warmup loop, tqdm, per-clip timing, `--limit` flag, and 80%
   rejection criterion.

3. **Use GPU inference** (A100 or H100). CPU latency for Granite will not come close to 200 ms p50.
   The task description estimates $3–8 USD for ~1 hour A100 time.

4. **Confirm the Granite keyword biasing API** before writing `run_granite_biased.py`. The
   `ibm-granite/granite-speech-4.1-2b` model card must be consulted (or `research_internet.md`
   reviewed) to identify the exact processor/model parameter for passing keyword lists. The
   `DOMAIN_VOCAB` list from [t0004]'s `constants.py` is the vocabulary to use.

5. **Produce both `granite-4.1-2b-gold92-batch` and `granite-4.1-2b-gold92-keyword-biased`
   prediction assets** per the task specification (2 expected). Use [t0004]'s
   `write_prediction_asset()` pattern for full spec v2 compliance.

6. **Report per-term domain vocab accuracy** using `compute_per_term_accuracy()` from [t0004]. This
   directly answers whether Granite's keyword biasing lifts specific terms.

7. **Stratify results** by full set (93 clips), production subset (8 accented clips), and
   clean-voice subset. Use the `accent_group` field from `GoldClip` (loaded from `gold_set.jsonl`).

8. **Include the Cyrillic anomaly handling** unchanged: exclude `error_en_0005` from entity accuracy
   aggregate via `np.nanmean`, include it in WER. The constant `CYRILLIC_ANOMALY_CLIP` should be
   copied from [t0004].

9. **Do not re-run t0004 inference**. The Whisper large-v3 biased baseline numbers (94.5% domain
   vocab accuracy) come from `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` and
   should be loaded for side-by-side comparison tables.

10. **Document streaming/NAR assessment** as a qualitative section in `results_detailed.md`. No
    separate benchmark run is needed, but the assessment must confirm whether a streaming decode
    path or NAR variant of Granite 4.1 is available and what latency implications it has for
    `transcribe_stream` compatibility.

* * *

## Task Index

### [t0001]

* **Task ID**: t0001_stt_benchmark
* **Name**: STT Benchmark — Gold-92 Dataset Ingestion
* **Status**: completed
* **Relevance**: Provides the gold-92 evaluation dataset (93 WAV clips, `ground_truth.jsonl`,
  `gold_set.jsonl`) that t0007 runs inference on. Must be DVC-pulled before any inference.

### [t0002]

* **Task ID**: t0002_baseline_evaluation
* **Name**: Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92
* **Status**: completed
* **Relevance**: Established the evaluation harness (metric computation, BCa CI, entity span
  inference, predictions asset format) that all subsequent benchmark tasks reuse. Key finding:
  Whisper without biasing scores 25.2% entity accuracy and 30.4% AC-WER on gold-92.

### [t0004]

* **Task ID**: t0004_vocabulary_biasing_experiment
* **Name**: Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy
* **Status**: completed
* **Relevance**: Direct dependency. Provides the Whisper large-v3 + initial_prompt comparison
  baseline (94.5% domain vocab accuracy, 2.5% AC-WER), the 31-term domain vocabulary list, the
  extended metric harness with `entity_accuracy_domain_vocab`, and the inference/prediction asset
  code that t0007 will copy and adapt.

### [t0005]

* **Task ID**: t0005_stt_model_survey_brainpowa
* **Name**: STT Model Survey: Open-Source Candidates for the brainpowa Pipeline
* **Status**: completed
* **Relevance**: Ranked IBM Granite Speech 4.1 2B as #1 benchmark candidate based on HuggingFace
  Open ASR Leaderboard position (5.33% WER), native keyword biasing mechanism, and estimated 100–200
  ms TTFT. Identified the model as primary next-step for gold-92 benchmarking, directly motivating
  t0007.
