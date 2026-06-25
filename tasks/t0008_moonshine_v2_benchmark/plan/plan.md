---
spec_version: "2"
task_id: "t0008_moonshine_v2_benchmark"
date_completed: "2026-06-25"
status: "complete"
---
# Plan: Benchmark Moonshine v2 on Gold-92

## Objective

Benchmark Moonshine v2 Medium (CPU-only, OnnxRuntime backend) on the gold-92 benchmark (93 WAV
clips) and assess shallow-fusion biasing feasibility. The task produces one primary prediction
asset: batch-mode transcriptions of all 93 clips with full metric computation (WER, entity accuracy
— overall and domain-vocab, action-critical WER, intent preservation, latency p50, wrong-action
rate). A second asset documents the shallow-fusion feasibility assessment (research + design doc or
prototype, not a second full inference run).

The primary comparator is the t0004 baseline (Whisper large-v3 + initial_prompt):
entity_accuracy_domain_vocab=94.5%, entity_accuracy_gold92=46.0%, wer_gold92=8.5%,
action_critical_wer_gold92=2.5%, intent_preservation_gold92=98.9%, latency_p50_seconds=6.66 s.

**Done when**: all 93 clips transcribed, all 7 registered metrics computed with BCa bootstrap 95%
CIs, shallow-fusion feasibility verdict documented, prediction assets created and verified, and
`uv run python -u -m arf.scripts.verificators.verify_plan t0008_moonshine_v2_benchmark` passes with
zero errors.

## Task Requirement Checklist

**Task name**: Benchmark Moonshine v2 on Gold-92

**short_description** (verbatim):
> Benchmark Moonshine v2 (CPU-only) on gold-92 to validate entity accuracy and latency without GPU
> requirements, comparing entity recall and biasing feasibility vs. Whisper baseline.

**Resolved long description** (operative requirements extracted from `task_description.md`):

* REQ-1 — Run Moonshine v2 Medium (usefulsensors/moonshine, OnnxRuntime CPU) on all 93 gold-92 clips
  in batch mode with no biasing. *Steps 2–4.*
* REQ-2 — Collect per-clip wall-clock latency, distinguishing cold-start (clip 1), warm-up (clips
  2–5), and warmed (clips 6–93). *Steps 3–4.*
* REQ-3 — Compute all 7 registered metrics: `wer_gold92`, `entity_accuracy_gold92`,
  `entity_accuracy_domain_vocab`, `action_critical_wer_gold92`, `intent_preservation_gold92`,
  `latency_p50_seconds`, `wrong_action_rate_gold92`. BCa bootstrap 95% CIs (n=10 000) on all
  accuracy metrics. *Step 5.*
* REQ-4 — Stratify all metrics across three subsets: full set (93 clips), production subset (8
  accented-English clips), and clean-voice subset (85 clips). *Step 5.*
* REQ-5 — Compute custom latency metrics: cold-start, warm-up, and warmed-stage p50/p95/p99. *Step
  5.*
* REQ-6 — Perform shallow-fusion feasibility assessment: document candidate approaches, identify 1–2
  open-source libraries, estimate implementation effort in hours, estimate latency overhead per clip
  (5–30 ms estimated), and produce a feasibility verdict ("viable for production", "needs research",
  or "infeasible within budget"). *Step 6.*
* REQ-7 — Answer 7 numbered key questions from the task description (entity accuracy ≥ 46%?, WER ≤
  8.5%?, AC-WER ≤ 2.5%?, latency p50 ≤ 200 ms after warm-up?, cold-start acceptability?,
  shallow-fusion feasible in < 20 hours?, accented-English entity accuracy vs. Whisper?). *Step 7.*
* REQ-8 — Generate comparison bar charts: entity accuracy (domain vocab), WER, AC-WER vs. Whisper
  baseline; latency distribution (cold-start / warm-up / warmed). *Step 8.*
* REQ-9 — Produce two prediction assets: `moonshine-v2-medium-gold92` (JSONL, run 1) and
  `moonshine-v2-medium-gold92-biasing-assessment` (markdown + optional code, run 2). *Step 9.*
* REQ-10 — Write `results/metrics.json` (explicit variant format, 7 registered metrics for run 1).
  *Step 5.*
* REQ-11 — Report side-by-side comparison vs. Whisper baseline and strategic interpretation: if
  entity accuracy ≥ 46% AND shallow fusion is feasible → Moonshine is viable edge fallback;
  otherwise → recommend follow-up direction. *Step 7.*
* REQ-12 — All 93 clips must be transcribed successfully (no skips except documented failures).
  *Step 3 (rejection criterion).*
* REQ-13 — Track `wrong_action_rate_gold92` (< 2% project threshold). *Step 5.*

## Approach

### Technical approach

**Model and inference**. Moonshine v2 Medium is the `usefulsensors/moonshine` package on
HuggingFace. The correct package is `moonshine-onnx` (PyPI: `useful-moonshine-onnx`), which ships
the ONNX export and OnnxRuntime CPU runtime. The t0004 task already ran Moonshine base (~60 M
params) using `moonshine_onnx.MoonshineOnnxModel` with `model_name="moonshine/base"`. For this task
the target is Moonshine v2 Medium. The usefulsensors/moonshine v2 release (2024-11) renamed
variants; the expected model name is `"moonshine/v2-medium"` — confirm at import time that this name
resolves (see validation gate in Step 3). Audio loading uses `load_audio` from `moonshine_onnx`,
which resamples to 16 kHz mono PCM using librosa.

**Key findings from t0004 (used here)**. Moonshine base (no biasing) produced:
entity_accuracy_gold92=21.7%, entity_accuracy_domain_vocab=10.9%, wer_gold92=18.4%,
action_critical_wer_gold92=41.1%, intent_preservation_gold92=84.9%, latency_p50=0.07 s. Moonshine v2
Medium is a newer, larger variant (reported 5.3% WER on LibriSpeech, vs. base's higher error rate),
so we expect materially better WER and entity accuracy. The entity_accuracy threshold to beat is
46.0% (Whisper large-v3 biased, overall gold-92).

**Dataset and paths**. Gold-92 audio lives at
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/<clip_id>.wav`. Ground
truth is at
`tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl` (canonical
reference — use this, NOT gold_set.jsonl, for text comparison). Accent groups and production-subset
membership are in `gold_set.jsonl` (same directory).

**Metric computation**. All metric functions already exist in
`tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py`: `normalise`, `bca_ci`,
`compute_per_clip_entity_accuracy`, `compute_wer_batch`, `compute_action_critical_wer`,
`compute_intent_preservation`, `compute_latency_p50`, `compute_entity_accuracy_domain_vocab`,
`build_production_entity_accuracy`. These will be imported directly (the module is importable as a
project package). The domain vocabulary (31 terms) is in
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py` as `DOMAIN_VOCAB`.

**wrong_action_rate_gold92**. This metric is not computed in t0004. The project defines it as the
fraction of utterances where the routing policy emits a confident action that differs from the
ground-truth action. For this benchmarking task (no routing layer), a proxy approximation is used:
wrong_action_rate = 1 − intent_preservation (i.e., any utterance where no entity span is recovered =
"wrong action"). This proxy is consistent with how t0004 computed intent preservation and is the
most defensible approach without a full downstream routing layer. Document the proxy definition
explicitly in results_detailed.md.

**Latency staging**. The inference loop assigns each clip to a latency stage: cold-start = clip
index 0, warm-up = clip indices 1–4, warmed = clip indices 5–92. Per-stage p50/p95/p99 are computed
separately. The registered metric `latency_p50_seconds` uses the median across all 93 clips
(consistent with t0004 measurement).

**metrics.json format**. Because this task produces a single inference run (run 1), the legacy flat
format is appropriate. Run 2 is a qualitative assessment and produces no registered metrics.

**Shallow-fusion assessment**. This is a research + writing task, not a full inference run.
Approaches to document: (1) log-linear model (add log-prob from an n-gram LM over the biasing
vocabulary), (2) lattice rescoring with kaldi-native-io or k2, (3) forced-first-pass bias list
injection into the ONNX decoder. Candidate libraries: `pyctcdecode` (CTC beam-search with hotword
boosting), `k2` / `icefall` (lattice rescoring). Effort estimate should include: model modification
hours, integration + testing hours, and validation hours.

**Code to copy and adapt**. Copy:
* `tasks/t0004_vocabulary_biasing_experiment/code/run_moonshine_small.py` → `code/run_inference.py`
  (change model name to `"moonshine/v2-medium"`, add latency staging, expand output schema)
* `tasks/t0004_vocabulary_biasing_experiment/code/load_dataset.py` → import directly (no copy needed
  — it's a project package)
* `tasks/t0004_vocabulary_biasing_experiment/code/constants.py` → import directly
* `tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py` → import directly

### Alternatives considered

**Alternative 1: Run Moonshine v2 Tiny or Small instead of Medium.** Rejected because the task
description specifies Medium (~4.7 M params) as the target. Tiny/Small would give better latency but
lower accuracy, making the comparison to Whisper less fair.

**Alternative 2: Copy all metric code instead of importing from t0004.** Rejected. The t0004 code is
a project package (importable). Copying it would create maintenance divergence. Importing directly
is cleaner and ensures consistent metric computation with t0004.

**Alternative 3: Run the shallow-fusion assessment as a separate full inference run with a prototype
adapter.** Rejected per task scope. The task description explicitly says "this run assesses
feasibility and estimates integration effort" — a full second inference run is out of scope. A
design doc + prototype or library evaluation is sufficient.

### Task type

Task type: `stt-benchmark-run` (confirmed in `task.json`). Per the Planning Guidelines for this
type: model and configuration are fully specified below; API cost for 93 local clips is $0; primary
comparison target is t0004 (Whisper large-v3 + initial_prompt); `metrics.json` will use the 7
registered project metrics; per-clip predictions will be saved to the predictions asset `files/`
subdirectory and tracked by DVC.

## Cost Estimation

* Moonshine v2 Medium inference on 93 clips (OnnxRuntime CPU, local machine): **$0.00** — no cloud
  compute, no paid APIs.
* DVC push to Azure Blob Storage (`azure://ml-dvc-datasets/datasets/rail-arf-stt`): **$0.00** —
  within free-tier storage thresholds for this project.
* Shallow-fusion research (library review, design doc): **$0.00** — time-only, no paid services.

**Total estimated cost: $0.00.** Well within the per-task default limit of $100.00 and the project
total budget of $2,000.00.

## Step by Step

### Milestone 1: Setup and validation

1. **Pull data and verify environment.** Run `dvc pull` from the repo root to ensure all gold-92
   audio files are present locally. Then confirm the count:
   ```
   ls tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/*.wav | wc -l
   ```
   Expected: 93 files. If fewer, the DVC pull failed — do not proceed. Also verify `moonshine_onnx`
   is importable:
   ```
   uv run python -c "from moonshine_onnx import MoonshineOnnxModel; print('ok')"
   ```
   If the package is missing, add `useful-moonshine-onnx` to `pyproject.toml` under
   `[project.dependencies]` and run `uv sync`. Satisfies REQ-1 (setup).

2. **Confirm model name for v2 Medium.** Run:
   ```
   uv run python -c "
   from moonshine_onnx import MoonshineOnnxModel
   m = MoonshineOnnxModel(model_name='moonshine/v2-medium')
   print('loaded ok')
   "
   ```
   If this fails with a model-not-found error, try `"moonshine/v2"`, `"moonshine/medium"`, or check
   the usefulsensors/moonshine HuggingFace repo for the exact model identifier. The plan uses
   `"moonshine/v2-medium"` but the exact string must be validated before the full run. Document the
   confirmed name in `code/paths.py`. Satisfies REQ-1 (model identification).

### Milestone 2: Batch inference (Run 1)

3. **[CRITICAL] Write and run `code/run_inference.py`.** Create
   `tasks/t0008_moonshine_v2_benchmark/code/run_inference.py` by adapting
   `tasks/t0004_vocabulary_biasing_experiment/code/run_moonshine_small.py` with these changes:

   * Change `MODEL_NAME = "moonshine/base"` to the confirmed v2 Medium model name.
   * Add latency staging constants: `COLD_START_INDEX = 0`, `WARMUP_INDICES = set(range(1, 5))`,
     `WARMED_START = 5`.
   * In the output dict per clip, add a `"latency_stage"` field: `"cold_start"` for index 0,
     `"warmup"` for indices 1–4, `"warmed"` for indices 5–92.
   * Output path: `tasks/t0008_moonshine_v2_benchmark/data/moonshine_v2_medium_transcripts.json`
     (same format as t0004: list of dicts with `clip_id`, `hypothesis`, `latency_seconds`,
     `latency_stage`).
   * Add a `--limit N` CLI argument (using `argparse`) to cap the number of clips for validation.
   * Write a progress line every 10 clips (already in t0004 code — keep it).

   **Validation gate (run before full 93-clip run):**
   * Run `uv run python -u tasks/t0008_moonshine_v2_benchmark/code/run_inference.py --limit 10`
   * After completion, read 5 individual output records manually and confirm: (a) `hypothesis` field
     is non-empty English text (not garbled), (b) `latency_seconds` is between 0.01 s and 5.0 s per
     clip, (c) `clip_id` matches the audio filename.
   * Trivial baseline: a random-string transcriber would produce entity_accuracy ≈ 0%. If the first
     10 clips produce entity accuracy at or below 0% (all empty/garbled output), **STOP** and debug
     the model loading path — do not proceed to the full 93-clip run.
   * If validation passes: run
     `uv run python -u tasks/t0008_moonshine_v2_benchmark/code/run_inference.py` (no --limit) for
     the full 93-clip run.

   Satisfies REQ-1, REQ-2, REQ-12.

### Milestone 3: Metric computation

4. **Write `code/paths.py`.** Create `tasks/t0008_moonshine_v2_benchmark/code/paths.py` with path
   constants:
   ```python
   from pathlib import Path
   TASK_ROOT = Path("tasks/t0008_moonshine_v2_benchmark")
   DATA_DIR = TASK_ROOT / "data"
   RESULTS_DIR = TASK_ROOT / "results"
   MOONSHINE_V2_TRANSCRIPTS = DATA_DIR / "moonshine_v2_medium_transcripts.json"
   METRICS_JSON = RESULTS_DIR / "metrics.json"
   ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
   PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"
   GOLD92_AUDIO = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio"
   )
   GROUND_TRUTH_JSONL = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
   )
   GOLD_SET_JSONL = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
   )
   ```

5. **[CRITICAL] Write and run `code/compute_metrics.py`.** Create
   `tasks/t0008_moonshine_v2_benchmark/code/compute_metrics.py`. This script:

   * Imports from t0004 (project packages — importable as-is):
     ```python
     from tasks.t0004_vocabulary_biasing_experiment.code.compute_metrics_biased import (
         normalise, bca_ci, compute_per_clip_entity_accuracy, compute_wer_batch,
         compute_action_critical_wer, compute_intent_preservation,
         compute_latency_p50, compute_entity_accuracy_domain_vocab,
         build_production_entity_accuracy, CYRILLIC_ANOMALY_CLIP,
     )
     from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import load_gold92
     from tasks.t0004_vocabulary_biasing_experiment.code.constants import DOMAIN_VOCAB
     ```
   * Loads transcripts from `MOONSHINE_V2_TRANSCRIPTS` (list of dicts, keyed by clip_id).
   * Calls each metric function for the single variant `"moonshine-v2-medium"`.
   * Computes `wrong_action_rate_gold92` as `1.0 - intent_preservation_aggregate` (proxy).
   * Computes per-stage latency (cold_start, warmup, warmed): filter transcript records by
     `latency_stage`, compute p50/p95/p99 for each group using `np.percentile`.
   * Stratifies entity_accuracy, WER, AC-WER, intent_preservation across full set, production subset
     (accent_group == "production", 8 clips), and clean-voice subset (85 clips).
   * Writes `results/metrics.json` using the **legacy flat format** (single variant):
     ```json
     {
       "wer_gold92": <float>,
       "entity_accuracy_gold92": <float>,
       "entity_accuracy_domain_vocab": <float>,
       "action_critical_wer_gold92": <float>,
       "intent_preservation_gold92": <float>,
       "latency_p50_seconds": <float>,
       "wrong_action_rate_gold92": <float>
     }
     ```
   * Writes `data/analysis_output.json` with full breakdown: per-clip scores, per-stage latency,
     stratified metrics, BCa CI bounds, and production-subset accuracy.
   * Prints a summary table to stdout.

   Run: `uv run python -u tasks/t0008_moonshine_v2_benchmark/code/compute_metrics.py`

   Expected output: summary table with 7 metric values; `results/metrics.json` written. Satisfies
   REQ-3, REQ-4, REQ-5, REQ-10, REQ-13.

### Milestone 4: Shallow-fusion assessment (Run 2)

6. **Write `code/shallow_fusion_assessment.md`.** Create
   `tasks/t0008_moonshine_v2_benchmark/code/shallow_fusion_assessment.md` (or produce directly as
   the predictions asset description). This document must cover:

   * 3 candidate shallow-fusion approaches, each with:
     - Method name and reference (e.g., "log-linear model", "CTC beam-search hotword boosting",
       "lattice rescoring")
     - Integration point in the Moonshine OnnxRuntime pipeline
     - Applicable open-source library (e.g., `pyctcdecode`, `k2`, custom PyTorch layer)
     - Estimated implementation effort in hours
     - Estimated latency overhead per clip (target: 5–30 ms)
   * Recommended approach with justification.
   * Feasibility verdict: one of "viable for production", "needs research", or "infeasible within
     budget".
   * Effort estimate: total hours to integrate the recommended approach.

   Satisfies REQ-6.

### Milestone 5: Charts

7. **Write and run `code/generate_charts.py`.** Create
   `tasks/t0008_moonshine_v2_benchmark/code/generate_charts.py` to produce 4 charts saved to
   `results/images/`. Each chart uses `matplotlib`. Required charts:

   * `entity_accuracy_domain_vocab_comparison.png` — bar chart: Moonshine v2 Medium (no bias) vs.
     Whisper large-v3 + initial_prompt (94.5%). Include BCa CI error bars.
   * `wer_comparison.png` — bar chart: Moonshine v2 vs. Whisper baseline (8.5%).
   * `action_critical_wer_comparison.png` — bar chart: Moonshine v2 vs. Whisper (2.5%).
   * `latency_distribution.png` — histogram or violin plot with three groups: cold-start (1 clip),
     warm-up (clips 2–5), warmed (clips 6–93). Include p50 marker line per group.

   All charts must have axis labels, titles, and legends. Run:
   `uv run python -u tasks/t0008_moonshine_v2_benchmark/code/generate_charts.py`

   Satisfies REQ-8.

8. **Produce key-question answer document.** Write
   `tasks/t0008_moonshine_v2_benchmark/data/key_question_answers.md` with answers to the 7 numbered
   key questions from the task description. For each question, state YES/NO/UNCERTAIN with the
   measured value. Example: "Q1: entity_accuracy_domain_vocab = X.X% — [BELOW / MEETS] the 46.0%
   Whisper overall baseline." Include the strategic interpretation (edge-deployment fallback viable
   or not). The orchestrator's results step will incorporate these answers into the results
   documents. Satisfies REQ-7, REQ-11.

### Milestone 6: Prediction assets

9. **Create prediction asset `moonshine-v2-medium-gold92`.** Create folder structure:
   ```
   tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92/
   ├── details.json
   ├── description.md
   └── files/
       └── predictions-gold92.jsonl
   ```

   `predictions-gold92.jsonl`: one JSON object per line with fields: `clip_id` (string),
   `ground_truth` (string), `prediction` (string), `wer_local` (float), `entity_accuracy_local`
   (float or null), `latency_ms` (float), `latency_stage` (string: "cold_start" | "warmup" |
   "warmed").

   `details.json` must include:
   * `spec_version: "2"`, `predictions_id: "moonshine-v2-medium-gold92"`
   * `model_id: null` (no separate model asset), `model_description`: describe Moonshine v2 Medium
     (usefulsensors/moonshine v2, OnnxRuntime CPU, ~4.7M params)
   * `dataset_ids: ["stt-benchmark-gold-92"]`
   * `prediction_format: "jsonl"`, `prediction_schema`: describe the 7 fields
   * `instance_count: 93`, `categories: ["stt-evaluation"]`
   * `created_by_task: "t0008_moonshine_v2_benchmark"`, `date_created: <today>`

   `description.md` must include YAML frontmatter and sections: `## Metadata`, `## Overview`,
   `## Model`, `## Data`, `## Prediction Format`, `## Metrics`, `## Main Ideas`, `## Summary`.

   Track prediction file with DVC:
   `dvc add tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92/files/predictions-gold92.jsonl`

   Satisfies REQ-9.

10. **Create prediction asset `moonshine-v2-medium-gold92-biasing-assessment`.** Create:
    ```
    tasks/t0008_moonshine_v2_benchmark/assets/predictions/
        moonshine-v2-medium-gold92-biasing-assessment/
    ├── details.json
    ├── description.md
    └── files/
        └── shallow_fusion_feasibility.md
    ```

    `shallow_fusion_feasibility.md`: the full shallow-fusion feasibility assessment from Step 6.
    `details.json`: `spec_version: "2"`,
    `predictions_id: "moonshine-v2-medium-gold92-biasing-assessment"`, `model_id: null`,
    `model_description`: "Moonshine v2 Medium — shallow fusion feasibility assessment (no inference
    run)", `dataset_ids: ["stt-benchmark-gold-92"]`, `prediction_format: "jsonl"`,
    `prediction_schema`: "Assessment document only — no per-clip predictions",
    `instance_count: null`, `categories: ["stt-evaluation"]`,
    `created_by_task: "t0008_moonshine_v2_benchmark"`, `date_created: <today>`.

    Satisfies REQ-9.

11. **DVC push.** After all files are written and verified locally, run `dvc push` to upload the
    prediction JSONL file to Azure Blob Storage. This is required before merging so teammates can
    reproduce the run.

### Milestone 7: Verification

12. **Run all verificators.**
    ```bash
    uv run python -u -m arf.scripts.verificators.verify_plan t0008_moonshine_v2_benchmark
    uv run python -u -m arf.scripts.verificators.verify_predictions \
        tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92
    uv run python -u -m arf.scripts.verificators.verify_predictions \
        tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92-biasing-assessment
    uv run python -u -m arf.scripts.verificators.verify_task_complete t0008_moonshine_v2_benchmark
    uv run ruff check --fix tasks/t0008_moonshine_v2_benchmark/code/ && \
        uv run ruff format tasks/t0008_moonshine_v2_benchmark/code/
    uv run mypy tasks/t0008_moonshine_v2_benchmark/
    ```
    Fix all errors before merging. Satisfies REQ-3 (metric integrity), REQ-9 (asset structure).

## Remote Machines

None required. Moonshine v2 Medium runs entirely on CPU via OnnxRuntime. No GPU, no cloud instance.
Inference on 93 clips is expected to complete in under 30 minutes on any modern multi-core laptop or
server.

## Assets Needed

* **Gold-92 benchmark dataset** — `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`
  (93 WAV clips, `ground_truth.jsonl`, `gold_set.jsonl`). Available via `dvc pull`. Source: task
  t0001_stt_benchmark.
* **31-term domain vocabulary** — `tasks/t0004_vocabulary_biasing_experiment/code/constants.py`,
  `DOMAIN_VOCAB` list. Used for entity_accuracy_domain_vocab computation and shallow-fusion
  vocabulary reference. Source: task t0004_vocabulary_biasing_experiment.
* **Metric computation code** — importable from
  `tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py` and
  `tasks/t0004_vocabulary_biasing_experiment/code/load_dataset.py`. No copy needed.
* **Moonshine OnnxRuntime package** — `useful-moonshine-onnx` (PyPI). Must be in `pyproject.toml`
  dependencies; run `uv sync` if not already installed.
* **t0004 baseline comparison values** (hardcoded into charts and results):
  entity_accuracy_domain_vocab=94.5%, entity_accuracy_gold92=46.0%, wer_gold92=8.5%,
  action_critical_wer_gold92=2.5%, intent_preservation_gold92=98.9%, latency_p50_seconds=6.66 s.

## Expected Assets

* **Predictions asset 1**: `moonshine-v2-medium-gold92` — per-clip JSONL predictions from Moonshine
  v2 Medium batch inference on all 93 gold-92 clips. Stored at
  `tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92/`. Schema:
  `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local, latency_ms, latency_stage}`.
  DVC-tracked.

* **Predictions asset 2**: `moonshine-v2-medium-gold92-biasing-assessment` — shallow-fusion
  feasibility assessment document (markdown + optional code snippets). Stored at
  `tasks/t0008_moonshine_v2_benchmark/assets/predictions/ moonshine-v2-medium-gold92-biasing-assessment/`.
  Not DVC-tracked (markdown only).

Both assets match `expected_assets: {predictions: 2}` in `task.json`.

## Time Estimation

* **Milestone 1 (setup, validation)**: ~20 min
* **Milestone 2 (batch inference, 93 clips)**: ~10–30 min (CPU; ~100–500 ms/clip for v2 Medium)
* **Milestone 3 (metric computation)**: ~20 min (code + run)
* **Milestone 4 (shallow-fusion assessment)**: ~90 min (research + writing)
* **Milestone 5 (charts)**: ~30 min
* **Milestone 6 (prediction assets)**: ~30 min
* **Milestone 7 (verification + fixes)**: ~20 min

**Total estimated wall-clock time**: ~3.5–4 hours.

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Moonshine v2 Medium model name differs from `"moonshine/v2-medium"` | Medium | Blocks inference | Validate in Step 2; check HuggingFace usefulsensors/moonshine README for exact string |
| `useful-moonshine-onnx` not installed or pinned to old version without v2 | Medium | Blocks inference | Add to pyproject.toml; run `uv sync`; check package changelog for v2 support |
| DVC pull fails (Azure credentials missing in `.dvc/config.local`) | Medium | Blocks inference | Follow `docs/dvc-data-workflow.md`; copy `.dvc/config.local.example` and fill connection string |
| Per-clip latency for v2 Medium much higher than 200 ms target (e.g., 800 ms+ on slow machine) | Low | Results not what expected; latency hypothesis fails | Document actual measured p50; still meets REQ-2/5; latency answer will be NO for that hypothesis |
| BCa bootstrap NaN for domain-vocab metric (few clips with domain terms) | Low | CI invalid | Use fallback to percentile bootstrap (already implemented in t0004 `bca_ci`) |
| Cyrillic anomaly clip (error_en_0005) causes compute_entity_accuracy to fail | Low | Partial metric failure | Exclude from entity accuracy via np.nanmean (t0004 pattern already handles this) |
| Shallow-fusion library `pyctcdecode` incompatible with Moonshine ONNX | Medium | Assessment verdict may change | Document as "needs research"; use it as architectural reference only, not a tested prototype |
| More than 20% of clips fail to transcribe (rejection criterion) | Very Low | Results are null | Do not report any metrics; create intervention file; investigate audio format or model bug |

## Verification Criteria

* **All 93 clips transcribed**:
  `python -c "import json; d=json.load(open('tasks/t0008_moonshine_v2_benchmark/data/moonshine_v2_medium_transcripts.json')); print(len(d))"`
  — expected output: `93`.
* **All 7 registered metrics present in metrics.json**:
  `python -c "import json; m=json.load(open('tasks/t0008_moonshine_v2_benchmark/results/metrics.json')); print(sorted(m.keys()))"`
  — expected output contains all 7 keys: `action_critical_wer_gold92`,
  `entity_accuracy_domain_vocab`, `entity_accuracy_gold92`, `intent_preservation_gold92`,
  `latency_p50_seconds`, `wer_gold92`, `wrong_action_rate_gold92`.
* **Prediction asset verificator passes**:
  `uv run python -u -m arf.scripts.verificators.verify_predictions tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92`
  — expected: 0 errors.
* **Prediction asset 2 verificator passes**:
  `uv run python -u -m arf.scripts.verificators.verify_predictions tasks/t0008_moonshine_v2_benchmark/assets/predictions/moonshine-v2-medium-gold92-biasing-assessment`
  — expected: 0 errors.
* **Plan verificator passes**:
  `uv run python -u -m arf.scripts.verificators.verify_plan t0008_moonshine_v2_benchmark` —
  expected: 0 errors.
* **All 4 chart files exist**: `ls tasks/t0008_moonshine_v2_benchmark/results/images/` — expected:
  `entity_accuracy_domain_vocab_comparison.png`, `wer_comparison.png`,
  `action_critical_wer_comparison.png`, `latency_distribution.png`.
* **REQ coverage in results**:
  `grep -c "REQ-" tasks/t0008_moonshine_v2_benchmark/results/results_detailed.md` — expected: ≥ 13
  (one entry per REQ-1 through REQ-13).
* **Ruff and mypy clean**:
  `uv run ruff check tasks/t0008_moonshine_v2_benchmark/code/ && uv run mypy tasks/t0008_moonshine_v2_benchmark/`
  — expected: 0 errors.

## Rejection Criteria

These conditions invalidate the benchmark results and require an intervention file rather than
reported metrics. Pre-registered before execution (per Lesson 3 in LESSONS.md) to prevent
retroactive loosening.

* **Transcription failure rate ≥ 20%**: if `successful_transcriptions / 93 < 0.8`, all metrics are
  **null** regardless of measured values. Likely cause: model loading failure or audio format
  mismatch. Action: create `intervention/transcription_failure.md` documenting the error.
* **WER > 60% for any variant**: indicates a broken pipeline (wrong model, wrong audio, wrong
  normalisation). All metrics are **null**. This threshold is consistent with t0004's rejection
  check.
* **Latency p50 > 30 seconds**: indicates the OnnxRuntime inference path is not CPU-native or the
  machine is severely resource-constrained. Latency metrics are **null** (other metrics may still be
  reported if transcription quality is acceptable).
* **entity_accuracy_domain_vocab = 0.0 exactly**: indicates the domain vocabulary is not being
  evaluated correctly (e.g., normalisation bug, wrong transcript file path). Metrics are **null**
  pending investigation, even if WER appears reasonable.
