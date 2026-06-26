---
spec_version: "2"
task_id: "t0007_ibm_granite_4_1_benchmark"
date_completed: "2026-06-25"
status: "complete"
---
# Plan: Benchmark IBM Granite Speech 4.1 2B on Gold-92

## Objective

Benchmark IBM Granite Speech 4.1 2B (`ibm-granite/granite-speech-4.1-2b`) on the gold-92 evaluation
set (93 investor-relations audio clips) to determine whether it matches or exceeds the current
Whisper large-v3 + `initial_prompt` production baseline from task t0004. The baseline scores are:
`entity_accuracy_domain_vocab` = 94.5%, WER = 8.5%, AC-WER = 2.5%, intent preservation = 98.9%,
latency p50 = 6.66 s (CPU).

Two inference runs are required: (1) Granite batch mode with no biasing, and (2) Granite batch mode
with the 31-term Rezolve domain vocabulary activated via Granite's native keyword biasing API. All 7
registered project metrics are measured for each run, stratified by overall / production subset (8
accented clips) / clean-voice subset (85 clips). A qualitative streaming/NAR path assessment is
produced as part of run 1 setup.

**Done** means: both prediction assets created and verified, all metrics computed with BCa bootstrap
95% CIs, comparison tables vs. Whisper baseline in `results/`, and a latency feasibility verdict for
the 200 ms per-segment p50 target.

## Task Requirement Checklist

> **Task name**: Benchmark IBM Granite Speech 4.1 2B on Gold-92
>
> **Short description**: Benchmark IBM Granite Speech 4.1 2B with keyword biasing on gold-92 to
> validate entity accuracy and latency vs. Whisper large-v3 + initial_prompt baseline.
>
> **From task_description.md — Scope / Runs:**
>
> Run 1 — Granite 4.1 2B batch mode, no biasing: all 93 gold-92 clips, default batch inference. Run
> 2 — Granite 4.1 2B batch mode with keyword biasing: same 93 clips, 31-term domain vocab via native
> Granite keyword biasing API. Comparator: Whisper large-v3 + initial_prompt from t0004.
>
> **Registered metrics (per run, per stratum):** `wer_gold92`, `entity_accuracy_gold92`,
> `entity_accuracy_domain_vocab`, `action_critical_wer_gold92`, `intent_preservation_gold92`,
> `latency_p50_seconds`, `wrong_action_rate_gold92`. Custom metrics: keyword-biasing gain (Δ entity
> accuracy, Δ WER), production subset entity accuracy, latency feasibility verdict.
>
> **Streaming assessment** (qualitative, no separate run): HuggingFace API streaming path existence,
> NAR variant availability and latency, buffering shim viability.
>
> **Success criteria**: All 93 clips transcribed in both runs; all registered metrics computed with
> BCa CIs; entity accuracy domain vocab measured vs. 94.5% baseline; biasing gain quantified;
> latency p50 measured vs. 200 ms target; streaming/NAR path assessed; prediction assets created and
> verified; results include interpretation for each outcome case.

* REQ-1: Transcribe all 93 gold-92 clips with Granite 4.1 2B in batch mode, no keyword biasing.
  Evidence: `data/granite_batch_transcripts.json` with 93 entries. Steps 4–5 satisfy this.

* REQ-2: Transcribe all 93 gold-92 clips with Granite 4.1 2B in batch mode, with the 31-term Rezolve
  domain vocabulary activated via native Granite keyword biasing API. Evidence:
  `data/granite_biased_transcripts.json` with 93 entries. Step 6 satisfies this.

* REQ-3: Compute all 7 registered project metrics (`wer_gold92`, `entity_accuracy_gold92`,
  `entity_accuracy_domain_vocab`, `action_critical_wer_gold92`, `intent_preservation_gold92`,
  `latency_p50_seconds`, `wrong_action_rate_gold92`) for both runs with BCa bootstrap 95% CIs (n=10
  000 resamples). Report per stratum: overall, production subset (8 clips), clean-voice subset (85
  clips). Evidence: `results/metrics.json` with explicit multi-variant format. Step 9 satisfies
  this.

* REQ-4: Compute keyword-biasing gain: Δ entity accuracy (run 2 − run 1) and Δ WER (run 2 − run 1).
  Evidence: recorded in `results/metrics.json` and comparison table in results. Step 9 satisfies
  this.

* REQ-5: Measure latency p50 per segment on GPU and issue a feasibility verdict: is p50 ≤ 200 ms?
  Evidence: `latency_p50_seconds` in `results/metrics.json` and verdict in `results_summary.md`.
  Steps 5–6 (timing) and step 9 (verdict) satisfy this.

* REQ-6: Assess streaming/NAR path availability (qualitative): HuggingFace API streaming decode
  path, NAR variant and latency, buffering shim viability. Evidence: `data/streaming_assessment.md`
  written during run 1 setup. Step 3 satisfies this.

* REQ-7: Compare Granite keyword-biased results vs. Whisper large-v3 + initial_prompt baseline
  (t0004) on the six key questions (entity accuracy domain vocab ≥ 94.5%, overall entity accuracy ≥
  46.0%, biasing gain > 0, AC-WER ≤ 2.5%, latency ≤ 200 ms p50, production subset entity accuracy
  vs. Whisper on 8 accented clips). Evidence: comparison table in `results/results_detailed.md`.
  Step 10 satisfies this.

* REQ-8: Produce per-term domain vocabulary breakdown via `compute_per_term_accuracy()` to identify
  which of the 31 terms Granite's biasing still misses. Evidence: per-term table in
  `results/results_detailed.md`. Step 9 satisfies this.

* REQ-9: Create two predictions assets conforming to predictions spec v2:
  `granite-4.1-2b-gold92-batch` and `granite-4.1-2b-gold92-keyword-biased`. Evidence: both asset
  folders pass `verify_task_complete`. Step 11 satisfies this.

* REQ-10: Generate comparison bar charts (entity accuracy domain vocab, WER, AC-WER, latency p50)
  showing Granite no-bias vs. Granite biased vs. Whisper baseline. Save to `results/images/`. Step
  10 satisfies this.

* REQ-11: Run BCa bootstrap significance test (n=10 000 resamples, paired) vs. the Whisper
  large-v3-biased variant for entity accuracy and intent preservation. Record p-values. Step 9
  satisfies this.

## Approach

**Chosen approach: copy-and-adapt from t0004 (Approach 1).**

Task t0004 (`vocabulary_biasing_experiment`) produced a fully verified evaluation harness for
gold-92: `load_dataset.py` (GoldClip dataclasses, Cyrillic anomaly handling, 22-regex entity span
inference), `compute_metrics_biased.py` (all 6 project metrics, BCa CIs, paired significance test,
`compute_per_term_accuracy()`), `constants.py` (authoritative 31-term `DOMAIN_VOCAB`), and
`write_predictions.py` (predictions asset spec v2). Copying these verbatim and adapting only import
paths and variant IDs minimises inconsistency risk with established metric definitions.

Two new inference scripts are created from scratch (`run_granite_batch.py` and
`run_granite_biased.py`) using `run_whisper_biased.py` as the structural template (warmup, tqdm,
per-clip timing, `--limit`, 80% rejection criterion). The only new complexity vs. t0004 is the
Granite model loading API and the keyword biasing parameter — which is the top implementation
unknown (see Risks).

The 31-term domain vocabulary is copied verbatim from
`tasks/t0004_vocabulary_biasing_experiment/code/constants.py`. The terms are: Rezolve, Rezolve Ai,
NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite, GroupBy, Bluedot,
ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations, Dan Wagner, Arthur Yao,
Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee, Mark Turner, Peter Vesco, Urmee
Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith, Justin King, Christian Angermayer (31
terms).

**Cyrillic anomaly**: clip `error_en_0005` has a Cyrillic ground truth (`ы`) in `gold_set.jsonl`. As
in t0004, exclude it from entity accuracy aggregate via `np.nanmean`, include in WER.

**BCa NaN guard**: The production stratum has only 8 clips, near-minimum for BCa. The fallback to
percentile bootstrap (copied from t0004's `compute_metrics_biased.py`) is mandatory.

**Keyword biasing API**: IBM Granite Speech 4.1 2B uses HuggingFace Transformers. Before writing
`run_granite_biased.py`, the implementation agent must confirm the exact processor or model
parameter for passing keyword lists by checking the model card at
`https://huggingface.co/ibm-granite/granite-speech-4.1-2b`. The t0005 survey identified native
shallow-fusion keyword biasing as available but did not confirm the exact API parameter name. If the
parameter cannot be confirmed, create an intervention file — do not silently run unbiased inference
and call it biased.

**metrics.json format**: Use the explicit multi-variant format (as in t0004) with three variants:
`granite-4.1-2b-batch` (no biasing), `granite-4.1-2b-biased` (keyword biasing), and
`whisper-large-v3-biased` (t0004 baseline loaded from
`tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` for the comparison table only — do
not re-measure Whisper). Task type is `stt-benchmark-run`. The Planning Guidelines for this type
specify: full-model-configuration SUT, cost estimate for 93 clips, comparison vs. production
baseline, BCa significance test, per-clip predictions saved via DVC.

**Alternatives considered:**

* *t0002 harness minimal adaptation*: the t0002 `compute_metrics.py` (735 lines) lacks
  `entity_accuracy_domain_vocab` and `compute_per_term_accuracy()`. Adding these from scratch
  introduces inconsistency risk. Rejected in favour of t0004's already-complete version.
* *Fresh implementation*: highest risk of metric definition drift (normalisation, BCa parameters,
  Cyrillic handling). Rejected — no benefit over copying t0004.

## Cost Estimation

| Component | Estimated Cost |
| --- | --- |
| A100 80 GB GPU rental (~1 hour, Lambda/RunPod) | $1.50–$2.00 |
| Model download (ibm-granite/granite-speech-4.1-2b, ~5 GB) | $0.00 (HuggingFace free) |
| Inference run 1 (93 clips, ~30 s total on A100) | negligible |
| Inference run 2 (93 clips with biasing, ~30 s total on A100) | negligible |
| Metric computation + charting (~5 min CPU) | $0.00 |
| **Total estimated** | **$3–8 USD** |

Project budget: $2,000 total, $1,997.50 remaining (per user-provided budget summary). Per-task
default limit is $100 (from `project/budget.json`). This task is well within budget.

## Step by Step

### Milestone 1: Environment and data setup

1. **Run `dvc pull` to ensure gold-92 audio is present.** From the project root, run:
   `dvc pull tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/` Verify that
   `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/` contains 93 `.wav`
   files. If the directory is empty or the file count is wrong, check `.dvc/config.local` for the
   Azure Blob Storage connection string. [CRITICAL] Satisfies REQ-1, REQ-2 (prerequisite).

2. **Provision the remote A100/H100 GPU machine.** Use the setup-remote-machine skill to provision
   an A100 80 GB instance (Lambda Labs or RunPod). VRAM requirement: ≥ 6 GB for Granite 4.1 2B; 40
   GB+ A100 is fine and widely available. Estimated runtime: ~1 hour including model download and
   two inference passes. Copy the full project working tree to the remote machine. See
   `arf/specifications/remote_machines_specification.md` for the machine lifecycle protocol.
   [CRITICAL]

3. **Confirm the Granite keyword biasing API and document the streaming/NAR assessment.** On the
   remote machine, open a Python REPL and run:

   ```python
   from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
   processor = AutoProcessor.from_pretrained("ibm-granite/granite-speech-4.1-2b")
   print(dir(processor))
   help(processor.__call__)
   ```

   Check the HuggingFace model card at `https://huggingface.co/ibm-granite/granite-speech-4.1-2b`
   for the exact `hotwords`, `hotword_weight`, or equivalent parameter name for keyword biasing.
   Also inspect the model card for a streaming or NAR (non-autoregressive) variant. Write
   `tasks/t0007_ibm_granite_4_1_benchmark/data/streaming_assessment.md` documenting: (a) the exact
   processor/model parameter for keyword biasing, (b) whether a streaming decode path exists in the
   HuggingFace API, (c) whether a NAR variant is available and its expected latency, (d) whether a
   buffering shim could wrap Granite for `transcribe_stream` compatibility. If the keyword biasing
   parameter cannot be confirmed, create
   `tasks/t0007_ibm_granite_4_1_benchmark/intervention/keyword_biasing_api_unconfirmed.md` instead
   of proceeding with `run_granite_biased.py`. [CRITICAL] Satisfies REQ-6.

### Milestone 2: Copy and adapt the evaluation harness

4. **Copy the four evaluation harness files from t0004.** Copy verbatim (no changes to logic):

   * `tasks/t0004_vocabulary_biasing_experiment/code/load_dataset.py` →
     `tasks/t0007_ibm_granite_4_1_benchmark/code/load_dataset.py`
   * `tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py` →
     `tasks/t0007_ibm_granite_4_1_benchmark/code/compute_metrics.py`
   * `tasks/t0004_vocabulary_biasing_experiment/code/constants.py` →
     `tasks/t0007_ibm_granite_4_1_benchmark/code/constants.py`
   * `tasks/t0004_vocabulary_biasing_experiment/code/write_predictions.py` →
     `tasks/t0007_ibm_granite_4_1_benchmark/code/write_predictions.py`

   Then create `tasks/t0007_ibm_granite_4_1_benchmark/code/paths.py` with t0007-specific path
   constants (modelled on t0004's `paths.py`):

   ```python
   from pathlib import Path
   TASK_ROOT = Path("tasks/t0007_ibm_granite_4_1_benchmark")
   GOLD92_AUDIO = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio"
   )
   GROUND_TRUTH_JSONL = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
   )
   GOLD_SET_JSONL = Path(
       "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
   )
   DATA_DIR = TASK_ROOT / "data"
   RESULTS_DIR = TASK_ROOT / "results"
   GRANITE_BATCH_TRANSCRIPTS = DATA_DIR / "granite_batch_transcripts.json"
   GRANITE_BIASED_TRANSCRIPTS = DATA_DIR / "granite_biased_transcripts.json"
   ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
   METRICS_JSON = RESULTS_DIR / "metrics.json"
   PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"
   GRANITE_BATCH_PREDICTIONS_DIR = PREDICTIONS_DIR / "granite-4.1-2b-gold92-batch"
   GRANITE_BIASED_PREDICTIONS_DIR = PREDICTIONS_DIR / "granite-4.1-2b-gold92-keyword-biased"
   T0004_METRICS_JSON = Path(
       "tasks/t0004_vocabulary_biasing_experiment/results/metrics.json"
   )
   ```

   Update all `from tasks.t0004_vocabulary_biasing_experiment.code.*` imports in the copied files to
   `from tasks.t0007_ibm_granite_4_1_benchmark.code.*`. Also update any hardcoded path references
   that point to t0004 directories. Do not change any metric logic, BCa implementation, Cyrillic
   anomaly handling, or `DOMAIN_VOCAB` list. Satisfies REQ-3, REQ-8 (harness prerequisite).

### Milestone 3: Inference — run 1 (no biasing)

5. **Write and run `run_granite_batch.py` (no biasing).** Create
   `tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_batch.py` using
   `tasks/t0004_vocabulary_biasing_experiment/code/run_whisper_biased.py` as the structural
   template. Replace model loading and transcription with Granite equivalents:

   ```python
   from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
   import torch, torchaudio

   processor = AutoProcessor.from_pretrained("ibm-granite/granite-speech-4.1-2b")
   model = AutoModelForSpeechSeq2Seq.from_pretrained(
       "ibm-granite/granite-speech-4.1-2b",
       torch_dtype=torch.float16,
   ).to("cuda")
   model.eval()
   ```

   For transcription, load each audio clip with `torchaudio.load()`, convert to 16 kHz mono if
   needed, pass through `processor(audio, sampling_rate=16000, return_tensors="pt")`, run
   `model.generate(...)` with `language="en"`, and decode with
   `processor.batch_decode(output_ids, skip_special_tokens=True)`.

   Keep all structural elements from `run_whisper_biased.py` unchanged: `--limit` argument, 3-clip
   warmup (using `torch.no_grad()` to avoid OOM on warmup), per-clip `time.perf_counter()` timing,
   80% rejection criterion, `tqdm` progress bar, JSON output to
   `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_batch_transcripts.json`, and individual
   inspection printout for the first 5 clips.

   **Validation gate — run with `--limit 5` first:**

   ```bash
   uv run python -u tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_batch.py --limit 5
   ```

   Trivial baseline to beat: 0% entity accuracy (random/silent output). If entity accuracy on the
   5-clip sample is at or below 0% (i.e., empty hypotheses or clearly wrong output), STOP and debug
   individual predictions — do not proceed to full scale. Read the 5 printed hypotheses and verify:
   (a) model loaded correctly, (b) audio was decoded at 16 kHz, (c) transcriptions are English text,
   not silence or garbage.

   Once validation passes, run the full 93-clip inference:

   ```bash
   uv run python -u tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_batch.py
   ```

   Expected: `data/granite_batch_transcripts.json` with 93 entries, each with `clip_id`,
   `hypothesis`, `latency_seconds`. [CRITICAL] Satisfies REQ-1, REQ-5 (timing data).

### Milestone 4: Inference — run 2 (keyword biasing)

6. **Write and run `run_granite_biased.py` (keyword biasing).** Create
   `tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_biased.py` by copying
   `run_granite_batch.py` and adding the confirmed keyword biasing parameter (obtained in step 3).
   Based on the IBM Granite Speech model card, the likely parameter is `hotwords` passed to
   `model.generate()` or `processor()` — confirm the exact name in step 3 before writing this file.

   Pass the 31 terms from `constants.DOMAIN_VOCAB` as the hotword list. Use the same model
   checkpoint, same warmup logic, same `--limit` argument, same 80% rejection criterion, same timing
   infrastructure, and same output path structure as `run_granite_batch.py`. Save to
   `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_biased_transcripts.json`.

   **Validation gate — run with `--limit 5` first:**

   ```bash
   uv run python -u tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_biased.py --limit 5
   ```

   Verify that at least one of the 5 hypotheses contains a recognisable domain term (e.g.,
   "Rezolve", "brainpowa", "NASDAQ") that appeared in the reference. This confirms biasing is
   active. If all 5 hypotheses are identical to the no-biasing run and the audio clearly contains a
   domain term, biasing may not be working — STOP and re-check the API parameter.

   Full run:

   ```bash
   uv run python -u tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_biased.py
   ```

   Expected: `data/granite_biased_transcripts.json` with 93 entries. [CRITICAL] Satisfies REQ-2.

### Milestone 5: Metric computation and results

7. **Write `compute_metrics.py` main entry point.** The copied
   `tasks/t0007_ibm_granite_4_1_benchmark/code/compute_metrics.py` (adapted from t0004's
   `compute_metrics_biased.py`) needs a t0007-specific `main()` that:

   * Loads `data/granite_batch_transcripts.json` and `data/granite_biased_transcripts.json`
   * Loads `ground_truth.jsonl` via `load_dataset.load_gold92()` for reference transcripts and
     entity annotations
   * Loads `gold_set.jsonl` for `accent_group` stratification metadata
   * For each variant (batch, biased), calls the metric functions with the correct transcript list
   * Computes stratification over three groups: overall (93 clips), production subset
     (`accent_group == "accented"`, 8 clips), clean-voice subset (remaining 85 clips)
   * Applies `np.nanmean` for entity accuracy to exclude the Cyrillic anomaly clip `error_en_0005`
   * Applies BCa NaN fallback to percentile bootstrap when sample size < 20

   Satisfies REQ-3, REQ-4.

8. **Write `compute_biasing_gain.py`.** Create
   `tasks/t0007_ibm_granite_4_1_benchmark/code/compute_biasing_gain.py` to compute:
   * Δ entity accuracy (domain vocab) = biased − batch
   * Δ WER = biased − batch (negative = improvement) These values are reported as custom metrics in
     results. Satisfies REQ-4.

9. **Run metric computation and write `results/metrics.json`.** Execute:

   ```bash
   uv run python -u tasks/t0007_ibm_granite_4_1_benchmark/code/compute_metrics.py
   ```

   Write `tasks/t0007_ibm_granite_4_1_benchmark/results/metrics.json` in the explicit multi-variant
   format from `arf/specifications/task_results_specification.md`:

   ```json
   {
     "variants": [
       {
         "variant_id": "granite-4.1-2b-batch",
         "label": "Granite Speech 4.1 2B (no biasing)",
         "dimensions": {"model": "granite-speech-4.1-2b", "biasing": "none"},
         "metrics": { ... }
       },
       {
         "variant_id": "granite-4.1-2b-biased",
         "label": "Granite Speech 4.1 2B + keyword biasing",
         "dimensions": {"model": "granite-speech-4.1-2b", "biasing": "keyword-31-terms"},
         "metrics": { ... }
       },
       {
         "variant_id": "whisper-large-v3-biased",
         "label": "Whisper Large v3 + vocab bias (t0004 baseline)",
         "dimensions": {"model": "whisper-large-v3", "biasing": "initial-prompt"},
         "metrics": { ... }
       }
     ]
   }
   ```

   The Whisper variant is populated by loading
   `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` and copying the
   `whisper-large-v3-biased` entry verbatim — do not re-run Whisper inference.

   Registered metric keys to populate per variant: `entity_accuracy_gold92`,
   `entity_accuracy_domain_vocab`, `wer_gold92`, `action_critical_wer_gold92`,
   `intent_preservation_gold92`, `latency_p50_seconds`, `wrong_action_rate_gold92`.

   Also run the BCa bootstrap paired significance test (n=10 000 resamples) for `entity_accuracy`
   and `intent_preservation` comparing Granite biased vs. Whisper large-v3-biased. Record p-values
   in `data/analysis_output.json`. [CRITICAL] Satisfies REQ-3, REQ-4, REQ-5, REQ-7, REQ-8, REQ-11.

10. **Generate comparison charts and per-term breakdown.** Write
    `tasks/t0007_ibm_granite_4_1_benchmark/code/generate_charts.py` using `matplotlib` and `pandas`.
    Produce in `tasks/t0007_ibm_granite_4_1_benchmark/results/images/`:

    * `entity_accuracy_domain_vocab_comparison.png` — grouped bar chart: Granite no-bias vs. Granite
      biased vs. Whisper biased
    * `wer_comparison.png` — same three configurations
    * `action_critical_wer_comparison.png` — same three configurations
    * `latency_p50_comparison.png` — Granite batch vs. Whisper batch

    Call `compute_per_term_accuracy()` from `compute_metrics.py` for the biased Granite variant and
    write per-term accuracy table to `data/per_term_accuracy.json`. Include the per-term table in
    `data/analysis_output.json` as well for downstream reference.

    Satisfies REQ-7, REQ-8, REQ-10.

### Milestone 6: Prediction assets

11. **Create two prediction assets conforming to predictions spec v2.** Run
    `tasks/t0007_ibm_granite_4_1_benchmark/code/write_predictions.py` (adapted from t0004's
    `write_predictions.py`) to create:

    * `tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-4.1-2b-gold92-batch/`
      * `details.json` (spec_version: "2", predictions_id: "granite-4.1-2b-gold92-batch", model_id:
        null, dataset_ids: ["stt-benchmark-gold-92"], prediction_format: "jsonl", prediction_schema:
        "Each line is a JSON object with fields: clip_id (string), ground_truth (string), prediction
        (string), wer_local (float), entity_accuracy_local (float or null), latency_ms (float).",
        categories: ["stt-evaluation", "granite"], created_by_task:
        "t0007_ibm_granite_4_1_benchmark")
      * `description.md` (spec v2 with mandatory sections: Metadata, Overview, Model, Data,
        Prediction Format, Metrics, Main Ideas, Summary)
      * `files/predictions-gold92.jsonl` — 93 rows

    * `tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-4.1-2b-gold92-keyword-biased/`
      * Same structure with predictions_id: "granite-4.1-2b-gold92-keyword-biased"

    Each JSONL row schema:
    `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local, latency_ms}`. Note:
    `entity_accuracy_local` is `null` for clip `error_en_0005` due to the Cyrillic anomaly.
    [CRITICAL] Satisfies REQ-9.

12. **Run DVC tracking for prediction files and data outputs.** Run:

    ```bash
    dvc add tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-4.1-2b-gold92-batch/files/
    dvc add tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/granite-4.1-2b-gold92-keyword-biased/files/
    dvc add tasks/t0007_ibm_granite_4_1_benchmark/data/
    dvc push
    ```

    This ensures teammates can `dvc pull` the prediction JSONL files and intermediate data without
    re-running inference. Add the raw directories to `.gitignore` (the `.dvc` pointer files are
    committed to git). Satisfies REQ-9 (DVC requirement from task type guidelines).

## Remote Machines

**GPU required.** Whisper large-v3 on CPU achieved 6.66 s p50 latency. Granite 4.1 2B on CPU will be
similar and cannot approach the 200 ms per-segment target. A GPU is mandatory to measure the latency
metric meaningfully.

* **GPU type**: A100 80 GB (or H100 80 GB) — Granite 4.1 2B requires ~6–8 GB VRAM for the model
  weights in float16; A100 80 GB provides ample headroom
* **Provider**: Lambda Labs (`gpu_1x_a100`) or RunPod (`A100 80GB`) — both available at ~$1.50–$2/hr
* **Estimated runtime**: ~1 hour total (model download ~10 min, inference × 2 ~5 min, metric
  computation ~5 min, setup overhead ~40 min)
* **Machine lifecycle**: follow `arf/specifications/remote_machines_specification.md`; terminate
  after `dvc push` completes

If GPU is unavailable, CPU inference can be run for accuracy metrics only. In that case, the latency
numbers must be clearly flagged as "CPU-only, not comparable to 200 ms GPU target" and the latency
feasibility verdict must be deferred.

## Assets Needed

| Asset | Source | Notes |
| --- | --- | --- |
| Gold-92 audio clips (93 WAV, PCM-16 mono 16 kHz) | `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/` | DVC-tracked; requires `dvc pull` |
| Ground-truth transcripts | `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl` | Canonical reference |
| Gold set JSONL (for accent_group metadata) | `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` | Used for stratification only |
| t0004 metrics (Whisper baseline) | `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` | Loaded to populate comparison variant in `metrics.json`; Whisper inference is not re-run |
| Granite Speech 4.1 2B model weights | `ibm-granite/granite-speech-4.1-2b` via HuggingFace | ~5 GB download; Apache 2.0 license |
| HuggingFace Transformers ≥ 4.40 | `pip install transformers torch torchaudio` | Required for Granite inference |

## Expected Assets

| Type | Asset ID | Description |
| --- | --- | --- |
| `predictions` | `granite-4.1-2b-gold92-batch` | 93-clip JSONL predictions from Granite Speech 4.1 2B, batch mode, no keyword biasing. Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local, latency_ms}`. |
| `predictions` | `granite-4.1-2b-gold92-keyword-biased` | 93-clip JSONL predictions from Granite Speech 4.1 2B, batch mode, with 31-term Rezolve domain vocabulary keyword biasing. Same schema. |

Both assets conform to predictions asset spec v2. Matches `expected_assets` in `task.json`
(`"predictions": 2`).

## Time Estimation

| Phase | Estimated Wall-Clock Time |
| --- | --- |
| Research (complete) | done |
| Planning (this document) | ~1 hour |
| Remote machine provisioning | ~15 minutes |
| Environment setup + model download | ~20 minutes |
| Granite keyword biasing API confirmation (step 3) | ~15 minutes |
| Copy and adapt evaluation harness (step 4) | ~30 minutes |
| Inference run 1 — 93 clips, no biasing (step 5) | ~5 minutes on A100 |
| Inference run 2 — 93 clips, keyword biased (step 6) | ~5 minutes on A100 |
| Metric computation + biasing gain + charts (steps 7–10) | ~30 minutes |
| Prediction asset creation + DVC push (steps 11–12) | ~20 minutes |
| Verification + plan verificator | ~15 minutes |
| **Total** | **~3–4 hours** |

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Granite keyword biasing API parameter not in model card or silently ignored | Medium | Blocks run 2 (REQ-2); biasing gain unmeasurable | Step 3: confirm API parameter before writing `run_granite_biased.py`; if unconfirmed, create intervention file rather than running silently unbiased inference; check GitHub issues for `ibm-granite/granite-speech-4.1-2b` |
| DVC pull fails — Azure connection string missing from `.dvc/config.local` | Medium | Blocks all inference (no audio) | Copy `.dvc/config.local.example` to `.dvc/config.local` and fill in the team-vault connection string before any inference step; verify with `dvc status` |
| Granite 4.1 2B exceeds available VRAM (e.g., on a smaller GPU) | Low | Blocks all inference | Use `torch_dtype=torch.float16`; if still OOM, try `load_in_8bit=True` via bitsandbytes; if A100 80 GB is used, this risk is near-zero |
| BCa NaN on production stratum (8 clips) | High | Metric computation crash | BCa NaN fallback to percentile bootstrap is mandatory — copy unchanged from t0004's `compute_metrics_biased.py`; test with `--limit 8` before full run |
| Granite batch mode latency >> 200 ms on A100 | Medium | Latency feasibility verdict is "fail" | This is an acceptable scientific result; still record the measured p50 and document in `results_summary.md` as batch-only; note NAR variant as a path to sub-200 ms if available |
| WER normalisation mismatch vs. t0004 (capitalisation, punctuation) | Low | Incomparable WER numbers | Use the same normalisation as t0004: lowercase both sides, strip punctuation via regex before passing to `jiwer.wer()`; confirm by re-running t0004 metrics on one sample clip |
| HuggingFace model card unavailable or Granite 4.1 2B removed from hub | Low | Blocks model download | Check `ibm-granite` org page; Granite 4.1 series has Apache 2.0 and is actively maintained as of April 2026 per t0005 survey; contact IBM team if removed |

## Verification Criteria

* **Plan verificator**: run
  `uv run python -u -m arf.scripts.verificators.verify_plan t0007_ibm_granite_4_1_benchmark` and
  confirm zero errors.

* **Inference completeness (REQ-1, REQ-2)**: run
  `python -c "import json; d=json.load(open('tasks/t0007_ibm_granite_4_1_benchmark/data/granite_batch_transcripts.json')); print(len(d))"`
  and confirm output is `93`. Repeat for `granite_biased_transcripts.json`.

* **Metric keys valid (REQ-3)**: run
  `uv run python -u -m arf.scripts.verificators.verify_task_complete t0007_ibm_granite_4_1_benchmark`
  and confirm zero errors. This verificator checks that `metrics.json` contains only registered
  metric keys and that both prediction assets pass spec v2 validation.

* **Entity accuracy comparison (REQ-7)**: run
  `python -c "import json; m=json.load(open('tasks/t0007_ibm_granite_4_1_benchmark/results/metrics.json')); [print(v['variant_id'], v['metrics'].get('entity_accuracy_domain_vocab')) for v in m['variants']]"`
  and confirm three variant rows are present with numeric `entity_accuracy_domain_vocab` values.

* **Both prediction assets exist and are valid (REQ-9)**: confirm both directories exist:
  `ls tasks/t0007_ibm_granite_4_1_benchmark/assets/predictions/` and verify output contains
  `granite-4.1-2b-gold92-batch` and `granite-4.1-2b-gold92-keyword-biased`. Each directory must
  contain `details.json`, `description.md`, and `files/predictions-gold92.jsonl`.

* **Streaming assessment documented (REQ-6)**: confirm
  `tasks/t0007_ibm_granite_4_1_benchmark/data/streaming_assessment.md` exists and contains all four
  assessment points (biasing API parameter, streaming decode path, NAR variant, buffering shim
  viability).

* **Charts generated (REQ-10)**: confirm `ls tasks/t0007_ibm_granite_4_1_benchmark/results/images/`
  contains at least `entity_accuracy_domain_vocab_comparison.png`, `wer_comparison.png`,
  `action_critical_wer_comparison.png`, and `latency_p50_comparison.png`.

* **Rejection criterion not triggered**: confirm neither inference script printed "Rejection
  criterion triggered" during the full 93-clip run. If it did, all metrics from that run are null
  per the pre-registration below.

## Rejection Criteria

The following conditions declare a run's results **null** regardless of any measured numbers. These
are pre-registered before inference runs to prevent retroactive loosening.

* **Run 1 (no biasing)**: if `successful_requests / 93 < 0.8` (fewer than 74 clips transcribed
  successfully), the entire run is null. Do not report any metric from run 1.
* **Run 2 (keyword biasing)**: same threshold — if fewer than 74/93 clips succeed, run 2 is null.
* **Biasing silently inactive**: if `run_granite_biased.py` completes but the keyword biasing
  parameter was never confirmed (step 3 returned no confirmed parameter), all run 2 results are null
  and the biasing gain cannot be reported. Create an intervention file instead of reporting unbiased
  inference as biased.
* **CPU-only latency**: if the inference runs on CPU (no GPU available), latency metrics must be
  reported as "CPU-only, not comparable to 200 ms GPU target" and the latency feasibility verdict
  must be explicitly deferred pending GPU re-run.

Rationale: as established in LESSONS.md Lesson 3, pre-registering failure-rate rejection prevents
infrastructure failures from polluting benchmark conclusions.
