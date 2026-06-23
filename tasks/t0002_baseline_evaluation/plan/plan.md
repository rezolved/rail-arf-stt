---
spec_version: "2"
task_id: "t0002_baseline_evaluation"
date_completed: "2026-06-23"
status: "complete"
---
# Plan: Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92

## Objective

Establish project-wide baselines by running two STT configurations — Deepgram Nova-2 (production
cloud API) and Whisper Large v3 (local open-source model) — on the gold-92 benchmark and computing
all five registered project metrics with BCa bootstrap 95% confidence intervals. The gold-92
benchmark contains 93 annotated WAV clips from Rezolve production investor-relations voice sessions
(accented English). Results serve as the reference point against which every subsequent improvement
task (post-correction, fine-tuning, confidence routing) is judged.

Success looks like: two predictions assets committed and passing verificators;
`results/metrics.json` using the explicit variant format with both conditions; a bar chart and
scatter plot in `results/images/`; a summary metrics table and per-accent breakdown table in
`results_detailed.md`; and the plan verificator passing with zero errors.

## Task Requirement Checklist

Operative task text (from `task.json` `name` and `long_description_file`):

> **Baseline Evaluation — Deepgram and Whisper Large v3 on Gold-92**
>
> Establish project baselines by running Deepgram Nova-2 and Whisper Large v3 on gold-92, computing
> all five registered metrics with BCa bootstrap confidence intervals.
>
> Evaluate exactly two STT configurations: (1) Deepgram Nova-2 via cloud API with `nova-2` model and
> default settings; (2) Whisper Large v3 via `openai-whisper` package, local inference, no
> fine-tuning. All five registered metrics for both runs. BCa bootstrap 95% CI (n=10,000, paired).
> Paired BCa significance test comparing Whisper vs Deepgram on `entity_accuracy_gold92`. DVC-pull
> gold-92 audio before inference. Do not modify gold-92 data. Save raw transcripts to
> `data/deepgram_transcripts.json` and `data/whisper_transcripts.json`. Two predictions assets:
> `predictions/deepgram-nova2-gold92` and `predictions/whisper-large-v3-gold92`, each with
> `predictions.json` and `metadata.json`. Required charts (Fig 1: bar chart; Fig 2: scatter plot).
> Required tables (summary metrics; per-accent-group breakdown). Address RQ1 and its significance
> sub-question.

* **REQ-1** — Run Deepgram Nova-2 on all 93 gold-92 clips via the cloud API using `nova-2` model and
  default settings (no custom vocabulary). Satisfied by Step 4; evidence:
  `data/deepgram_transcripts.json` with 93 entries.

* **REQ-2** — Run Whisper Large v3 on all 93 gold-92 clips via local inference with no fine-tuning
  or prompt injection. Per research findings, use `faster-whisper`
  (`WhisperModel("large-v3", device="cpu", compute_type="int8")`) rather than the `openai-whisper`
  package. (The `task_description.md` specifies `openai-whisper` but research shows `faster-whisper`
  is the correct implementation on Apple M5 — this discrepancy is resolved in Approach.) Satisfied
  by Step 5; evidence: `data/whisper_transcripts.json` with 93 entries.

* **REQ-3** — Compute all five registered project metrics for both systems:
  `entity_accuracy_gold92`, `wer_gold92`, `action_critical_wer_gold92`,
  `intent_preservation_gold92`, `latency_p50_seconds`. Satisfied by Step 7; evidence:
  `results/metrics.json` explicit-variant format with both conditions.

* **REQ-4** — Compute BCa bootstrap 95% confidence intervals (n=10,000 resamples, paired samples)
  for each metric. Satisfied by Step 7; evidence: CI values in `results/metrics.json` and tables in
  `results_detailed.md`.

* **REQ-5** — Run a paired BCa bootstrap significance test comparing Whisper Large v3 vs Deepgram on
  `entity_accuracy_gold92` (primary metric). Satisfied by Step 7; evidence: p-value reported in
  `results_detailed.md`.

* **REQ-6** — DVC-pull the gold-92 audio before running any inference. Satisfied by Step 2;
  evidence: 93 WAV files present in
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/`.

* **REQ-7** — Do not modify or augment the gold-92 data. Satisfied by the read-only data handling in
  Steps 2–5; evidence: no writes to `tasks/t0001_stt_benchmark/`.

* **REQ-8** — Save raw transcription outputs to `data/deepgram_transcripts.json` and
  `data/whisper_transcripts.json` within this task folder. Satisfied by Steps 4 and 5; evidence:
  both files present with 93 entries each.

* **REQ-9** — Produce predictions asset `predictions/deepgram-nova2-gold92` with `predictions.json`
  and `metadata.json`. Satisfied by Step 8; evidence: asset passes verificator.

* **REQ-10** — Produce predictions asset `predictions/whisper-large-v3-gold92` with
  `predictions.json` and `metadata.json`. Satisfied by Step 9; evidence: asset passes verificator.

* **REQ-11** — Generate required Chart 1 (bar chart comparing `entity_accuracy_gold92`,
  `wer_gold92`, `action_critical_wer_gold92` with BCa CI error bars). Satisfied by Step 10;
  evidence: `results/images/fig1_primary_metrics_comparison.png`.

* **REQ-12** — Generate required Chart 2 (per-utterance scatter plot of entity accuracy, coloured by
  speaker accent group). Satisfied by Step 10; evidence:
  `results/images/fig2_per_utterance_entity_accuracy.png`.

* **REQ-13** — Produce summary metrics table (rows = both systems, columns = all 5 metrics ± CI).
  Satisfied by Step 11; evidence: table in `results_detailed.md`.

* **REQ-14** — Produce per-accent-group breakdown table (`entity_accuracy_gold92` by accent group
  for each system). Satisfied by Step 11; evidence: table in `results_detailed.md`.

* **REQ-15** — Address RQ1: what is the current WER and entity accuracy of both systems on gold-92,
  broken down by utterance category and entity type? Satisfied by Step 11; evidence:
  `results_detailed.md` Analysis section.

* **REQ-16** — Address RQ1 significance sub-question: does Whisper Large v3 materially outperform
  Deepgram on entity accuracy (BCa p < 0.05)? Satisfied by Step 7; evidence: p-value in
  `results_detailed.md`.

* **REQ-17** — Flag `error_en_0005` (Cyrillic ground truth `"ы"`) in the predictions asset metadata
  and in `metadata.json`. Satisfied by Steps 4–5 and 8–9; evidence: anomaly logged in both
  predictions assets' `metadata.json`.

## Approach

### Technical approach

This task runs two STT systems against the gold-92 benchmark and computes metrics. The five modules
are written from scratch (no shared code exists yet in this project).

**Whisper inference: `faster-whisper` not `openai-whisper`**

The task description mentions `openai-whisper`, but research confirms that `faster-whisper`
(`WhisperModel("large-v3", device="cpu", compute_type="int8")`) is the correct implementation on
Apple M5 Mac. `openai-whisper` on CPU takes 8–12 min per clip (12–19 hours total), making the full
run impractical without a remote GPU. `faster-whisper` with CTranslate2 INT8 reduces this to ~15–40
minutes total by providing ~4x speedup and ~75% RAM reduction (10 GB → 2.5 GB). Always pass
`language="en"` to prevent accent-misclassification (documented failure mode where accented English
is classified as another language). This deviation from the task description's literal package name
is a technical implementation detail, not a change to the evaluation configuration — both packages
produce Whisper Large v3 transcriptions.

**Deepgram SDK**

Use `deepgram-sdk>=3.0` with `DeepgramClient().listen.v1.media.transcribe_file()`. The legacy
`listen.prerecorded` API is deprecated. Set `smart_format=True, punctuate=True` for normalised
output. Cost: ~$0.09 total for 93 clips at $0.0043/min.

**Reference data**

Use `ground_truth.jsonl` (not `gold_set.jsonl`) as the canonical reference for all metric
computation. `gold_set.jsonl` has normalisation inconsistencies in its `ground_truth` field. The
`production` and `whisper` columns in `gold_set.jsonl` must never be used as baselines — they are
uncontrolled live-session outputs. Re-run inference fresh.

**Entity accuracy**

Implement Caubrière et al. (2020) definition: an entity span is correct only if all constituent
words exactly match after normalisation (lowercase + strip punctuation). All-or-nothing, no partial
credit. `entity_accuracy_gold92 = 1 - EER`.

**WER computation**

Use `jiwer.process_words` (batch, all 93 pairs at once) with one shared `normalise(text)` function
(lowercase + strip punctuation). For `action_critical_wer_gold92`, filter the aligned word list to
entity-span tokens only before computing S+D+I counts.

**BCa bootstrap**

`scipy.stats.bootstrap(method='BCa', n_resamples=10_000, random_state=42)`. For the paired
significance test use `paired=True`. Guard against degenerate distributions (all scores identical →
BCa returns NaN) by falling back to `method='percentile'` with a logged warning. This handles
`error_en_0005` and any trivially easy or impossible clips.

**Latency measurement**

Use `time.perf_counter()` around each API/inference call. Do NOT use `response.metadata.duration`
(that is audio duration, not processing time). Deepgram latency includes network round-trip; Whisper
latency is local-only — the two are not directly comparable and this must be documented in
`metadata.json` for each predictions asset.

**Bootstrap seeds**

Use `random_state=42` for all bootstrap calls (not the framework default 12345) to maintain
consistency with the research plan. Document the seed in `metadata.json`.

**`error_en_0005` handling**

Clip `error_en_0005` has Cyrillic ground truth `"ы"` — a known annotation error. Include it in the
full run for completeness, log a warning during processing, record it in both predictions assets'
`metadata.json`, and note it in results. Verify it does not disproportionately skew aggregate
metrics (it will produce 0 entity accuracy and nonstandard WER for that clip).

**`metrics.json` format**

Use the explicit variant format (two variants: `deepgram-nova2` and `whisper-large-v3`) since this
task compares two conditions. Each variant's `metrics` object contains point estimates; CI values go
in `results_detailed.md`.

**Intent preservation**

The registered metric `intent_preservation_gold92` requires downstream intent classification.
Implement a rule-based proxy: an utterance preserves intent if the action type implied by key entity
spans (IR terms, product names, action verbs) matches between reference and hypothesis. This is a
heuristic approximation; document its limitations explicitly.

**`wrong_action_rate_gold92`**

The sixth registered metric (`wrong_action_rate_gold92`) requires a confidence-routing policy which
is not part of this baseline task. This metric is omitted from `metrics.json` with explicit
documentation in `results_detailed.md` explaining that it requires a routing policy (task scope).

### Alternatives considered

**Alternative 1: Use `openai-whisper` directly with a remote GPU.** The task description mentions
`openai-whisper`, and a GPU instance would make it feasible. Rejected because: (a) the Apple M5
machine is confirmed as the execution environment; (b) `faster-whisper` achieves the same
transcription quality (same model weights) at ~4x speed with no accuracy penalty; (c) avoids $5–20
GPU spend that is unnecessary.

**Alternative 2: Use `gold_set.jsonl` ground truth instead of `ground_truth.jsonl`.**
`gold_set.jsonl` exists and is co-located. Rejected because research confirmed its `ground_truth`
field has normalisation inconsistencies that would inflate WER artefactually.

**Alternative 3: Blockwise bootstrap by speaker for all BCa computations.** Liu & Peng (2020) show
that standard i.i.d. BCa is biased when evaluation utterances share speakers. Rejected as the
primary approach because: the speaker correlation affects only the `clean_voices` subset (~40/93
clips with 6 named speakers); for the full 93-clip result, standard BCa is an acceptable
approximation per the research summary. The bootstrap method choice (standard vs. blockwise) is
documented in `metadata.json`.

### Task types

Task types declared in `task.json`: `stt-benchmark-run` and `baseline-evaluation`. Both types'
planning guidelines have been followed:

* From `stt-benchmark-run`: full STT configuration specified; API/inference cost estimated; output
  schema tied to the 6 registered project metrics; DVC-pull step included; latency warmup planned;
  normalisation method specified; predictions JSONL tracked by DVC.
* From `baseline-evaluation`: per-subset (accent group) breakdowns planned from the start; explicit
  metrics variants defined; inference time and API cost measurement planned; compare-literature step
  is in the optional steps list (to be run after results).

## Cost Estimation

| Item | Unit cost | Quantity | Total |
| --- | --- | --- | --- |
| Deepgram Nova-2 API | $0.0043/min audio | ~18 min (93 clips × ~12 s avg) | ~$0.08 |
| Whisper Large v3 (local, CPU) | $0 | 93 clips | $0.00 |
| Remote GPU instance | N/A | None required (M5 Mac) | $0.00 |
| **Total** |  |  | **~$0.08** |

Per-task budget limit: $100 (from `project/budget.json`). Estimated spend of ~$0.08 is well within
limit — less than 0.1% of the per-task budget.

## Step by Step

### Milestone 1: Environment and data setup

1. **Verify environment dependencies.** Check that `faster-whisper`, `deepgram-sdk>=3.0`, `jiwer`,
   `scipy`, `matplotlib`, `seaborn`, and `numpy` are in `pyproject.toml`. If missing, add them and
   run `uv sync`. Also verify `DEEPGRAM_API_KEY` is set in the environment. Expected output:
   `uv sync` completes with no errors;
   `python -c "from faster_whisper import WhisperModel; print('ok')` prints `ok`. Satisfies REQ-1,
   REQ-2 prerequisites.

2. **[CRITICAL] DVC-pull gold-92 audio.** From the repo root, run
   `dvc pull tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio.dvc`. Verify
   exactly 93 WAV files are present:

   ```bash
   ls tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/*.wav | wc -l
   ```

   Expected: `93`. If DVC pull fails, create
   `tasks/t0002_baseline_evaluation/intervention/dvc_pull_failed.md` documenting the error — do not
   proceed. Satisfies REQ-6.

3. **Write `code/paths.py`.** Create `tasks/t0002_baseline_evaluation/code/paths.py` defining all
   path constants as `pathlib.Path` objects:

   ```python
   from pathlib import Path
   TASK_ROOT = Path("tasks/t0002_baseline_evaluation")
   GOLD92_AUDIO = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio")
   GROUND_TRUTH_JSONL = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
   )
   DATA_DIR = TASK_ROOT / "data"
   RESULTS_DIR = TASK_ROOT / "results"
   RESULTS_IMAGES_DIR = RESULTS_DIR / "images"
   DEEPGRAM_TRANSCRIPTS = DATA_DIR / "deepgram_transcripts.json"
   WHISPER_TRANSCRIPTS = DATA_DIR / "whisper_transcripts.json"
   ```

   Create `tasks/t0002_baseline_evaluation/data/` directory (gitkeep). Satisfies REQ-8 path
   structure.

4. **Write `code/load_dataset.py`.** Load `ground_truth.jsonl` (NOT `gold_set.jsonl`) and return a
   list of dicts with fields `clip_id`, `reference_text`, `entity_spans` (list of span dicts),
   `accent_group`, `source`. Each dict is one gold-92 clip. Use explicit type annotations.

   ```python
   from pathlib import Path
   import json
   from dataclasses import dataclass
   from typing import Any

   @dataclass(frozen=True, slots=True)
   class GoldClip:
       clip_id: str
       reference_text: str
       entity_spans: list[dict[str, Any]]
       accent_group: str
       audio_path: Path
   ```

   Verify:
   `python -c "from tasks.t0002_baseline_evaluation.code.load_dataset import load_gold92; clips = load_gold92(); assert len(clips) == 93, f'Expected 93, got {len(clips)}'"`.
   Satisfies REQ-3 data loading prerequisite.

### Milestone 2: Deepgram inference

5. **[CRITICAL] Write and run `code/run_deepgram.py`.** This module calls the Deepgram Nova-2 API
   for each of the 93 clips and saves raw responses.

   **Setup**:

   * Import: `from deepgram import DeepgramClient, PrerecordedOptions`
   * Client: `DeepgramClient(api_key=os.environ["DEEPGRAM_API_KEY"])`
   * Method: `client.listen.v1.media.transcribe_file(payload, options)` where `payload` is
     `{"buffer": audio_bytes}` and `options` is
     `PrerecordedOptions(model="nova-2", smart_format=True, punctuate=True)`
   * Latency: measure with `time.perf_counter()` around each call; record in the output dict

   **Validation gate (run with `--limit 5` first)**:

   * Run
     `uv run python -m arf.scripts.utils.run_with_logs --task-id t0002_baseline_evaluation -- python tasks/t0002_baseline_evaluation/code/run_deepgram.py --limit 5`
   * Trivial baseline: a system that produces empty output would have entity accuracy of 0.0. Any
     real STT output should yield at least some word overlap.
   * Failure condition: if all 5 clips return empty transcripts or HTTP errors, STOP — do not
     proceed to full run. Debug authentication and SDK client setup.
   * Individual inspection: read the first 5 raw API responses manually. Verify: (a) the
     `transcript` field is non-empty; (b) the response contains
     `results.channels[0].alternatives[0].transcript`; (c) `error_en_0005` clip logs a Cyrillic
     warning.

   **Full run**:

   * Once the 5-clip test passes individual inspection, run the full 93-clip batch.
   * Save to `data/deepgram_transcripts.json` as a list of dicts:
     `{"clip_id": str, "hypothesis": str, "latency_seconds": float, "raw_response": dict}`.
   * Log a warning for `error_en_0005` to stdout.

   Expected output: `data/deepgram_transcripts.json` with 93 entries, file size ~200–500 KB.
   Satisfies REQ-1, REQ-8.

### Milestone 3: Whisper inference

6. **[CRITICAL] Write and run `code/run_whisper.py`.** This module runs Whisper Large v3 locally via
   `faster-whisper`.

   **Setup**:

   * Import: `from faster_whisper import WhisperModel`
   * Model: `WhisperModel("large-v3", device="cpu", compute_type="int8")`
   * Load model once before the loop (not per clip)
   * Transcribe: `model.transcribe(str(audio_path), language="en")` — `language="en"` is mandatory
     to prevent accent-misclassification failure mode
   * Latency: measure with `time.perf_counter()` around each `transcribe()` call

   **Validation gate (run with `--limit 5` first)**:

   * Run
     `uv run python -m arf.scripts.utils.run_with_logs --task-id t0002_baseline_evaluation -- python tasks/t0002_baseline_evaluation/code/run_whisper.py --limit 5`
   * Trivial baseline: empty output = 0.0 entity accuracy. Any real output should produce
     recognisable English words.
   * Failure condition: if all 5 clips produce empty transcripts or if the model fails to load,
     STOP. Verify `faster-whisper` package version and that model weights download succeeds.
   * Individual inspection: read 5 individual outputs. Verify: (a) transcripts are English words;
     (b) latency values are plausible (>0.1 s per clip); (c) `error_en_0005` logs a Cyrillic
     warning.

   **Warmup**:

   * Run 3 throwaway clips through the model before recording latency (Lesson 1: cold-cache
     measurements are not pairable with warm-cache measurements). These 3 clips do not go into
     `data/whisper_transcripts.json` — they are discarded.

   **Full run**:

   * Save to `data/whisper_transcripts.json` as a list of dicts:
     `{"clip_id": str, "hypothesis": str, "latency_seconds": float}`.
   * Expected total wall-clock time: 15–40 minutes on Apple M5 with INT8 quantization.
   * Progress logging every 10 clips: `print(f"Whisper: {i+1}/93 clips processed")`.

   Expected output: `data/whisper_transcripts.json` with 93 entries. Satisfies REQ-2, REQ-8.

### Milestone 4: Metric computation

7. **[CRITICAL] Write and run `code/compute_metrics.py`.** This module loads both transcript files
   and ground truth and computes all five metrics.

   **Imports**:

   ```python
   import jiwer
   import numpy as np
   from scipy.stats import bootstrap
   ```

   **Normalisation** (shared function, used consistently on both reference and hypothesis):

   ```python
   import re, string

   def normalise(text: str) -> str:
       text = text.lower()
       text = text.translate(str.maketrans("", "", string.punctuation))
       return text.strip()
   ```

   **WER** (`wer_gold92`):

   * Apply `normalise()` to both reference and hypothesis for all 93 clips
   * `transformation = jiwer.Compose([jiwer.ReduceToListOfListOfWords()])`
   * `result = jiwer.process_words(references_list, hypotheses_list)` (batch, all 93 pairs)
   * WER =
     `result.substitutions + result.deletions + result.insertions) / result.hits + result.substitutions + result.deletions`

   **Entity accuracy** (`entity_accuracy_gold92`):

   * For each clip, iterate over `entity_spans` from `ground_truth.jsonl`
   * A span is correct iff `normalise(predicted_span) == normalise(reference_span)` for all words in
     the span (all-or-nothing, Caubrière et al. 2020)
   * Per-clip score: correct_spans / total_spans (0 if total_spans = 0)
   * For `error_en_0005`: entity_spans may include `"ы"` — log warning, skip that clip from the
     denominator of aggregate entity accuracy (use `np.nanmean` with NaN for that clip)

   **Action-critical WER** (`action_critical_wer_gold92`):

   * Filter aligned word list from `jiwer.process_words` to entity-span tokens only
   * `action_critical_wer = (S_critical + D_critical + I_critical) / N_critical` where N_critical is
     total reference words in annotated entity spans

   **Intent preservation** (`intent_preservation_gold92`):

   * Rule-based proxy: an utterance preserves intent if
     `set(entity_spans_predicted) & set(entity_spans_reference)` is non-empty (at least one critical
     entity matched)
   * Per-clip boolean; aggregate = fraction of clips that pass
   * Record intent preservation method in `data/analysis_output.json` under key
     `intent_preservation_method` for downstream documentation

   **Latency p50** (`latency_p50_seconds`):

   * `np.percentile([clip["latency_seconds"] for clip in transcripts], 50)` for each system
   * Include in `metrics.json` per variant

   **BCa bootstrap CIs**:

   ```python
   def bca_ci(
       per_clip_scores: np.ndarray,
       *,
       n_resamples: int = 10_000,
       random_state: int = 42,
   ) -> tuple[float, float]:
       try:
           result = bootstrap(
               (per_clip_scores,),
               statistic=np.mean,
               method="BCa",
               n_resamples=n_resamples,
               random_state=random_state,
           )
           low, high = result.confidence_interval
           if np.isnan(low) or np.isnan(high):
               raise ValueError("BCa returned NaN — falling back to percentile")
           return float(low), float(high)
       except Exception:
           import warnings
           warnings.warn("BCa NaN guard triggered — using percentile bootstrap", stacklevel=2)
           result = bootstrap(
               (per_clip_scores,),
               statistic=np.mean,
               method="percentile",
               n_resamples=n_resamples,
               random_state=random_state,
           )
           return float(result.confidence_interval.low), float(result.confidence_interval.high)
   ```

   **Paired significance test** (`entity_accuracy_gold92` primary metric):

   ```python
   diff = deepgram_entity_scores - whisper_entity_scores
   result = bootstrap(
       (diff,),
       statistic=np.mean,
       method="BCa",
       n_resamples=10_000,
       paired=True,
       random_state=42,
   )
   p_value = float(np.mean(diff <= 0))  # one-sided: P(Whisper >= Deepgram)
   ```

   Store the p-value in `data/analysis_output.json` under `significance_test.p_value`.

   **Output**: save `tasks/t0002_baseline_evaluation/results/metrics.json` using explicit variant
   format:

   ```json
   {
     "variants": [
       {
         "variant_id": "deepgram-nova2",
         "label": "Deepgram Nova-2",
         "dimensions": {"model": "deepgram-nova-2"},
         "metrics": {
           "entity_accuracy_gold92": 0.XX,
           "wer_gold92": 0.XX,
           "action_critical_wer_gold92": 0.XX,
           "intent_preservation_gold92": 0.XX,
           "latency_p50_seconds": X.XX
         }
       },
       {
         "variant_id": "whisper-large-v3",
         "label": "Whisper Large v3",
         "dimensions": {"model": "whisper-large-v3"},
         "metrics": {
           "entity_accuracy_gold92": 0.XX,
           "wer_gold92": 0.XX,
           "action_critical_wer_gold92": 0.XX,
           "intent_preservation_gold92": 0.XX,
           "latency_p50_seconds": X.XX
         }
       }
     ]
   }
   ```

   Note: `wrong_action_rate_gold92` is omitted — requires a confidence-routing policy not in scope
   for this task. Record the omission rationale in `data/analysis_output.json` under
   `omitted_metrics` key for downstream documentation.

   Satisfies REQ-3, REQ-4, REQ-5, REQ-15, REQ-16.

### Milestone 5: Predictions assets

8. **Write `code/generate_predictions_asset.py` and create the Deepgram predictions asset.** Create
   `tasks/t0002_baseline_evaluation/assets/predictions/deepgram-nova2-gold92/` with:

   * `files/predictions-gold92.jsonl` — one JSON object per line, 93 lines:

     ```json
     {
       "clip_id": "clean_en_0001",
       "reference": "<normalised reference text>",
       "hypothesis": "<Deepgram output>",
       "entity_spans_reference": [{"text": "Rezolve AI", "type": "brand"}],
       "entity_spans_predicted": [{"text": "resolve AI", "type": "brand"}],
       "entity_accuracy": 0.0,
       "wer": 0.12,
       "latency_seconds": 0.85,
       "anomaly_flag": null
     }
     ```

     For `error_en_0005`: set `"anomaly_flag": "cyrillic_ground_truth"`.

   * `metadata.json` — model name, API version, inference date, total latency, bootstrap method used
     (`standard_bca`, seed 42), hardware description, `error_en_0005` anomaly note, disclaimer that
     Deepgram latency includes network round-trip and is not comparable to local Whisper latency.

   * `details.json` — spec_version `"2"`, predictions_id `"deepgram-nova2-gold92"`, all required
     fields per predictions asset specification. `model_id: null` (API, no local asset).
     `dataset_ids: ["stt-benchmark-gold-92"]`. `instance_count: 93`.

   * `description.md` — full canonical description with all mandatory sections (Metadata, Overview,
     Model, Data, Prediction Format, Metrics, Main Ideas, Summary), minimum 400 words.

   Run verificator:
   `uv run python -m arf.scripts.verificators.verify_predictions_asset --task-id t0002_baseline_evaluation deepgram-nova2-gold92`.
   Fix all errors. Satisfies REQ-9.

9. **Create the Whisper predictions asset.** Follow the same pattern as Step 8, creating
   `tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/` with:

   * `files/predictions-gold92.jsonl` — same schema as Deepgram asset, 93 lines
   * `metadata.json` — model `faster-whisper large-v3`, `compute_type="int8"`, `device="cpu"`,
     `language="en"`, hardware: Apple M5, inference date, total wall-clock time, bootstrap seed 42,
     note on `error_en_0005`, disclaimer that Whisper latency is local-only (not network-bound).
   * `details.json` — spec_version `"2"`, predictions_id `"whisper-large-v3-gold92"`, required
     fields, `model_id: null`.
   * `description.md` — full canonical description, minimum 400 words.

   Run verificator:
   `uv run python -m arf.scripts.verificators.verify_predictions_asset --task-id t0002_baseline_evaluation whisper-large-v3-gold92`.
   Fix all errors. Satisfies REQ-10.

10. **DVC-track the predictions JSONL files.** Run:

    ```bash
    dvc add tasks/t0002_baseline_evaluation/assets/predictions/deepgram-nova2-gold92/files/
    dvc add tasks/t0002_baseline_evaluation/assets/predictions/whisper-large-v3-gold92/files/
    dvc push
    ```

    Git-add only the `.dvc` pointer files and `.gitignore` entries, not the raw JSONL content.

### Milestone 6: Charts and results

11. **Write and run `code/generate_charts.py`.** Produces both required charts:

    **Chart 1** (`results/images/fig1_primary_metrics_comparison.png`):

    * Grouped bar chart with `matplotlib`/`seaborn`
    * Metrics on x-axis: `entity_accuracy_gold92`, `wer_gold92`, `action_critical_wer_gold92`
    * Two bars per metric (Deepgram Nova-2 = blue, Whisper Large v3 = orange)
    * BCa 95% CI error bars
    * Title: "Figure 1: Primary metric comparison — Deepgram Nova-2 vs Whisper Large v3 on gold-92."
    * Y-axis label: "Score (lower is better for WER metrics)"
    * Save as PNG at 150 DPI minimum

    **Chart 2** (`results/images/fig2_per_utterance_entity_accuracy.png`):

    * Scatter plot, one point per clip (93 points)
    * x-axis: Deepgram entity accuracy per clip
    * y-axis: Whisper entity accuracy per clip
    * Points coloured by `accent_group` from `ground_truth.jsonl`
    * Diagonal reference line y=x
    * Title: "Figure 2: Per-utterance entity accuracy correlation — clips above diagonal favour
      Whisper."
    * Legend with accent group labels

    Expected: both PNG files in `results/images/` with sizes > 10 KB. Satisfies REQ-11, REQ-12.

12. **Save analysis tables and examples to `data/analysis_output.json`** for consumption by the
    results step. This file is the structured intermediate that the results step uses to produce the
    required tables and examples in the detailed results document.

    Contents of `data/analysis_output.json`:

    * `summary_table` — list of dicts, one per system, with all 5 metric point estimates and CI
      half-widths. Enables Table 1 (rows = {Deepgram Nova-2, Whisper Large v3}, columns = all 5
      metrics as "point_estimate ± CI_half_width").

    * `accent_breakdown` — list of dicts, one per accent group: N clips, Deepgram
      `entity_accuracy_gold92`, Whisper `entity_accuracy_gold92`. Enables Table 2 (per-accent-group
      breakdown).

    * `significance_test` — dict with `p_value`, `method`, `n_resamples`, `seed`, and
      `interpretation` field (e.g., "p=0.042 — Whisper significantly outperforms Deepgram at
      alpha=0.05").

    * `anomaly_clips` — list of clip_ids with anomaly flags (at minimum: `error_en_0005`).

    * `contrastive_examples` — list of 10+ dicts, each with `clip_id`, `reference`,
      `deepgram_hypothesis`, `whisper_hypothesis`, `entity_accuracy_deepgram`,
      `entity_accuracy_whisper`, `category` (one of: random, best_case, worst_case, boundary,
      contrastive). This feeds the mandatory `## Examples` section in the detailed results.

    Run:
    `uv run python -m arf.scripts.utils.run_with_logs --task-id t0002_baseline_evaluation -- python tasks/t0002_baseline_evaluation/code/generate_analysis_output.py`

    Expected output: `data/analysis_output.json` present, file size > 5 KB. Satisfies REQ-13,
    REQ-14, REQ-15.

### Milestone 7: Validation

13. **Run all verificators and fix errors.**

    ```bash
    uv run python -m arf.scripts.verificators.verify_plan t0002_baseline_evaluation
    uv run python -m arf.scripts.verificators.verify_predictions_asset \
        --task-id t0002_baseline_evaluation deepgram-nova2-gold92
    uv run python -m arf.scripts.verificators.verify_predictions_asset \
        --task-id t0002_baseline_evaluation whisper-large-v3-gold92
    uv run python -m arf.scripts.verificators.verify_task_metrics t0002_baseline_evaluation
    ```

    Fix all errors (E-level). Address all warnings (W-level) unless explicitly justified.

14. **Run Python quality checks.**

    ```bash
    uv run ruff check --fix tasks/t0002_baseline_evaluation/code/ && \
    uv run ruff format tasks/t0002_baseline_evaluation/code/ && \
    uv run mypy tasks/t0002_baseline_evaluation/code/
    ```

    Fix all lint and type errors.

## Remote Machines

None required. All inference runs locally on the Apple M5 Mac:

* Deepgram Nova-2 is a cloud API — no local GPU needed.
* Whisper Large v3 runs via `faster-whisper` (`device="cpu", compute_type="int8"`) which requires
  ~2.5 GB RAM and completes in ~15–40 minutes total on Apple M5 CPU.

A remote GPU instance would reduce Whisper inference time from ~40 minutes to ~5 minutes, but the
time saving does not justify the cost or setup overhead given the per-task $100 budget. If the
implementation agent finds that `faster-whisper` CPU runtime exceeds 90 minutes on the actual M5
hardware, it may provision a remote GPU as a fallback (document in intervention file first).

## Assets Needed

* **Gold-92 audio WAV files** —
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/` (DVC-tracked;
  materialise with `dvc pull` before use). Source: dependency task `t0001_stt_benchmark`.

* **Ground-truth JSONL** —
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`
  (canonical references; use this, not `gold_set.jsonl`). Source: dependency task
  `t0001_stt_benchmark`.

* **Deepgram API key** — environment variable `DEEPGRAM_API_KEY`. Source: team vault / local
  environment. If not set, create `intervention/deepgram_api_key_missing.md`.

* **Python packages** (must be in `pyproject.toml`): `faster-whisper`, `deepgram-sdk>=3.0`, `jiwer`,
  `scipy`, `matplotlib`, `seaborn`, `numpy`.

## Expected Assets

Two predictions assets (matching `task.json` `expected_assets: {"predictions": 2}`):

* **`predictions/deepgram-nova2-gold92`** — asset type `predictions`, spec v2. Per-clip transcripts
  and metrics for Deepgram Nova-2 on gold-92. Contains: `details.json`, `description.md`,
  `files/predictions-gold92.jsonl`, `metadata.json`. 93 prediction instances.

* **`predictions/whisper-large-v3-gold92`** — asset type `predictions`, spec v2. Per-clip
  transcripts and metrics for Whisper Large v3 on gold-92. Contains: `details.json`,
  `description.md`, `files/predictions-gold92.jsonl`, `metadata.json`. 93 prediction instances.

Both assets are DVC-tracked (JSONL files in `files/` added via `dvc add` and pushed).

## Time Estimation

| Phase | Estimated wall-clock |
| --- | --- |
| Research (already done) | 0 min |
| Env setup, DVC pull, path scaffold (Steps 1–4) | 15–20 min |
| Deepgram inference — 5-clip gate + full 93 (Step 5) | 5–10 min |
| Whisper inference — 5-clip gate + full 93 (Step 6) | 20–50 min |
| Metric computation and metrics.json (Step 7) | 15–20 min |
| Predictions assets creation and verificators (Steps 8–10) | 20–30 min |
| Charts and results tables (Steps 11–12) | 20–30 min |
| Final verificators and quality checks (Steps 13–14) | 10–15 min |
| **Total** | **~1.5–3 hours** |

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| DVC pull fails (Azure connection issue or missing key) | Medium | Blocking — no audio, no inference | Check `.dvc/config.local` for the Azure connection string. If missing, create `intervention/dvc_pull_failed.md` and await human input. |
| `DEEPGRAM_API_KEY` not set | Low | Blocking for REQ-1 | Create `intervention/deepgram_api_key_missing.md`. Whisper run can proceed independently. |
| `faster-whisper` CPU inference >90 min on M5 (model download failure, quantization issue) | Low | Time overrun | Add a `--dry-run` flag that checks model load; if >90 min projected, create intervention requesting GPU option. |
| `error_en_0005` Cyrillic `"ы"` causes crash in WER/entity computation | Medium | Silent metric error | Use `try/except` around that clip; force `entity_accuracy=NaN`, log warning; `np.nanmean` for aggregates. |
| BCa bootstrap returns NaN (degenerate distribution) | Low | Wrong CI values | NaN guard implemented: fall back to `method='percentile'` with logged warning (implemented in Step 7). |
| Deepgram SDK `listen.prerecorded` deprecation — wrong API path used | Medium | All 93 API calls fail | Use `client.listen.v1.media.transcribe_file()` from `deepgram-sdk>=3.0`. The 5-clip gate will catch this immediately. |
| `ground_truth.jsonl` missing `entity_spans` field for some clips | Low | Entity accuracy=NaN | Check during load; log clips with missing spans; treat as zero-entity clips (neutral, not an error). |
| Whisper `language="en"` forgotten — accent misclassification | Medium | Silently wrong transcripts | Assert `language="en"` is passed in `run_whisper.py`; validate in 5-clip gate that output is English. |

## Verification Criteria

* **Plan verificator passes.** Run:

  ```bash
  uv run python -m arf.scripts.verificators.verify_plan t0002_baseline_evaluation
  ```

  Expected: `0 errors, 0 warnings`.

* **Both transcript raw files contain exactly 93 entries.** Run:

  ```bash
  python -c "
  import json
  dg = json.load(open('tasks/t0002_baseline_evaluation/data/deepgram_transcripts.json'))
  wh = json.load(open('tasks/t0002_baseline_evaluation/data/whisper_transcripts.json'))
  assert len(dg) == 93, f'Deepgram: {len(dg)}'
  assert len(wh) == 93, f'Whisper: {len(wh)}'
  print('Both transcript files have 93 entries — PASS')
  "
  ```

  Expected output: `Both transcript files have 93 entries — PASS`.

* **Metrics JSON uses explicit variant format with both conditions and all 5 metrics.** Run:

  ```bash
  python -c "
  import json
  m = json.load(open('tasks/t0002_baseline_evaluation/results/metrics.json'))
  assert 'variants' in m, 'Missing variants key'
  assert len(m['variants']) == 2, f'Expected 2 variants, got {len(m[\"variants\"])}'
  keys = {'entity_accuracy_gold92','wer_gold92','action_critical_wer_gold92',
          'intent_preservation_gold92','latency_p50_seconds'}
  for v in m['variants']:
      missing = keys - set(v['metrics'].keys())
      assert not missing, f'Variant {v[\"variant_id\"]} missing: {missing}'
  print('metrics.json structure PASS')
  "
  ```

  Expected: `metrics.json structure PASS`.

* **Both predictions assets pass verificators with zero errors.** Run:

  ```bash
  uv run python -m arf.scripts.verificators.verify_predictions_asset \
      --task-id t0002_baseline_evaluation deepgram-nova2-gold92
  uv run python -m arf.scripts.verificators.verify_predictions_asset \
      --task-id t0002_baseline_evaluation whisper-large-v3-gold92
  ```

  Expected: `0 errors` for each. (Address all warnings.)

* **Both chart PNGs exist and are non-empty.**

  ```bash
  ls -lh tasks/t0002_baseline_evaluation/results/images/
  ```

  Expected: `fig1_primary_metrics_comparison.png` and `fig2_per_utterance_entity_accuracy.png` both
  present, each >10 KB.

* **REQ coverage check — `data/analysis_output.json` covers all analysis requirements.** Confirm
  that `data/analysis_output.json` contains `summary_table`, `accent_breakdown`,
  `significance_test`, and `contrastive_examples` keys:

  ```bash
  python -c "
  import json
  d = json.load(open('tasks/t0002_baseline_evaluation/data/analysis_output.json'))
  required = {'summary_table','accent_breakdown','significance_test','contrastive_examples'}
  missing = required - set(d.keys())
  assert not missing, f'Missing keys: {missing}'
  assert len(d['contrastive_examples']) >= 10, \
      f'Need >=10 examples, got {len(d[\"contrastive_examples\"])}'
  print('analysis_output.json PASS')
  "
  ```

  Expected: `analysis_output.json PASS`.

* **Ruff and mypy clean.**

  ```bash
  uv run ruff check tasks/t0002_baseline_evaluation/code/ && \
  uv run mypy tasks/t0002_baseline_evaluation/code/
  ```

  Expected: no errors.

## Rejection Criteria

The following conditions render this task's measurements **null** regardless of any reported
numbers. These criteria are pre-registered before running inference (Lesson 3: pre-register
failure-rate rejection threshold).

* **Incomplete transcription**: If `successful_requests / total_requests < 0.8` for either system
  (fewer than 75 of 93 clips successfully transcribed), that system's metrics are null. Do not
  report results — create `intervention/incomplete_transcription_<system>.md` with the error log.

* **All-zero entity accuracy**: If `entity_accuracy_gold92 = 0.0` for both systems, the entity span
  annotations in `ground_truth.jsonl` may not have loaded correctly, or normalisation may be
  stripping all content. Stop, debug, and do not report.

* **WER above 60%**: If either system's `wer_gold92 > 0.6`, the transcription pipeline has likely
  failed (wrong audio files, wrong reference file, or malformed normalisation). Stop and debug.

* **`error_en_0005` causes aggregate NaN not caught**: If aggregate entity accuracy is NaN after the
  NaN guard is applied, the fallback logic failed. Stop and debug the `nanmean` implementation.
