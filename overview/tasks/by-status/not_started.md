# ⏹ Tasks: Not Started

1 tasks. ⏹ **1 not_started**.

[Back to all tasks](../README.md)

---

## ⏹ Not Started

<details>
<summary>⏹ 0016 — <strong>Streaming Fuzzy Hotword Post-Correction for Domain Entity
Accuracy</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0016_streaming_fuzzy_hotword_correction` |
| **Status** | not_started |
| **Effective date** | — |
| **Dependencies** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Expected assets** | 1 answer |
| **Source suggestion** | — |
| **Task types** | [`experiment-run`](../../../meta/task_types/experiment-run/), [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/) |
| **Task page** | [Streaming Fuzzy Hotword Post-Correction for Domain Entity Accuracy](../../../overview/tasks/task_pages/t0016_streaming_fuzzy_hotword_correction.md) |
| **Task folder** | [`t0016_streaming_fuzzy_hotword_correction/`](../../../tasks/t0016_streaming_fuzzy_hotword_correction/) |

# Streaming Fuzzy Hotword Post-Correction for Domain Entity Accuracy

## Motivation

t0015_streaming_buffer_interval established that Parakeet-TDT-0.6b-v3 at a 500 ms buffer
interval achieves WER 15.25% and entity accuracy on the domain vocabulary (EA-DV) of only
33.3%, with latency p50 250 ms. The low EA-DV score reveals a consistent failure mode: the
model transcribes Rezolve brand names, product SKUs, and commerce terms as phonetically
similar but incorrect tokens (e.g. "resolve" instead of "Rezolve", "pay with card" instead of
"Pay with Card AI"). These errors are not random — they are systematic near-misses against a
bounded, known vocabulary.

Post-correction via fuzzy string matching is a lightweight, latency-safe technique that can
catch these systematic near-misses without any model retraining or GPU overhead. This task
implements and evaluates a post-correction layer that runs after each streaming buffer flush,
compares the transcript against the Rezolve domain vocabulary list (already produced by
t0015_streaming_buffer_interval), and replaces near-miss tokens with the correct domain term.
The target is EA-DV > 70% with a post-correction latency overhead of < 10 ms per clip.

This task directly supports the project's primary goal of beating production Deepgram on
entity accuracy under the 800 ms voice-to-action latency budget.

## Scope

- **Correction algorithm**: Levenshtein edit-distance + phonetic (Double Metaphone or Soundex)
  fuzzy match against the domain vocabulary list from t0015_streaming_buffer_interval.
- **Models evaluated**:
  1. Parakeet-TDT-0.6b-v3 at 500 ms buffer interval (baseline from t0015)
  2. parakeet-unified-en-0.6b at 500 ms buffer interval
  3. multitalker-parakeet-streaming-0.6b-v1 at 500 ms buffer interval
- **Dataset**: gold-92 (93 WAV clips, proprietary, DVC-tracked under t0001_stt_benchmark)
- **Metrics**: All seven registered project metrics computed for every model run — wer_gold92,
  entity_accuracy_gold92, entity_accuracy_domain_vocab (EA-DV), intent_preservation_gold92,
  action_critical_wer_gold92, wrong_action_rate_gold92, latency_p50_seconds — plus
  efficiency_inference_time_per_item_seconds and efficiency_inference_cost_per_item_usd.

## Approach

### Correction Pipeline

After each streaming buffer flush produces a partial or final transcript segment, the
post-corrector runs the following steps:

1. **Tokenise** the transcript segment into word tokens.
2. **For each token**, compute the minimum Levenshtein distance to all terms in the domain
   vocabulary list.
3. **Phonetic pass**: also compute Double Metaphone codes for each token and compare against
   pre-computed phonetic codes for the vocabulary list.
4. **Threshold**: replace a token if (a) Levenshtein distance ≤ 2 and the vocabulary candidate
   is the unique closest match, OR (b) phonetic codes match and Levenshtein distance ≤ 3, with
   no competing candidate within distance 1.
5. **Timing**: measure wall-clock time per flush from transcript segment start to corrected
   output to verify < 10 ms overhead.

### Threshold Tuning

Run a grid search over Levenshtein thresholds (1, 2, 3) and phonetic-match on/off to find the
threshold that maximises EA-DV without degrading WER. Report the full grid results as a table.
Use the Parakeet-TDT-0.6b-v3 predictions JSONL from t0015_streaming_buffer_interval as the
calibration set. Apply the winning threshold to all three models for the final evaluation.

### Re-using t0015 Outputs

t0015_streaming_buffer_interval has already produced:

- Prediction JSONL files for Parakeet-TDT-0.6b-v3, parakeet-unified-en-0.6b, and
  multitalker-parakeet-streaming-0.6b-v1 at 500 ms, 750 ms, and 1000 ms buffer intervals.
- The Rezolve domain vocabulary list used for biasing.

This task reads the 500 ms JSONL predictions directly and applies post-correction in a
separate Python script — no re-inference is required for the Parakeet-TDT-0.6b-v3 run. For
parakeet-unified-en-0.6b and multitalker, use the same JSONL files from t0015 if available;
otherwise re-run inference at 500 ms only.

## Runs

| Run ID | Model | Buffer interval | Post-correction |
| --- | --- | --- | --- |
| run-A | Parakeet-TDT-0.6b-v3 | 500 ms | None (baseline from t0015) |
| run-B | Parakeet-TDT-0.6b-v3 | 500 ms | Fuzzy hotword (best threshold) |
| run-C | parakeet-unified-en-0.6b | 500 ms | None |
| run-D | parakeet-unified-en-0.6b | 500 ms | Fuzzy hotword (best threshold) |
| run-E | multitalker-parakeet-streaming-0.6b-v1 | 500 ms | None |
| run-F | multitalker-parakeet-streaming-0.6b-v1 | 500 ms | Fuzzy hotword (best threshold) |

All six runs report the full set of registered metrics.

## Expected Outputs

- **Answer asset**: A structured answer to "Does Levenshtein + phonetic fuzzy post-correction
  bring EA-DV above 70% on gold-92 for Parakeet streaming at 500 ms, and at what latency
  cost?" Covers all three models.
- **results/metrics.json**: All registered metrics for all six runs.
- **results/results_detailed.md**: Full results narrative with tables and charts.
- **results/images/**: Charts saved as PNG files and embedded in results_detailed.md:
  - EA-DV before/after post-correction for each model (bar chart, y-axis: EA-DV %)
  - WER before/after post-correction for each model (bar chart, y-axis: WER %)
  - Threshold grid: EA-DV vs Levenshtein threshold on Parakeet-TDT-0.6b-v3 (line chart)
  - Latency overhead distribution: post-correction time per clip (histogram, x-axis: ms)

## Compute and Budget

Post-correction runs on CPU — no GPU required for the correction step itself. If re-inference
is needed for parakeet-unified or multitalker (because t0015 JSONL files are unavailable), one
A10G or equivalent GPU instance for < 1 h is sufficient.

Estimated budget: $2–5 total (GPU re-inference if needed: $1–3; CPU post-correction:
negligible).

## Key Questions

1. Does fuzzy post-correction raise EA-DV above the 70% target on Parakeet-TDT-0.6b-v3?
2. Is the per-clip post-correction latency overhead consistently < 10 ms?
3. Does post-correction improve or hurt WER (false-positive replacements may increase WER)?
4. Does the same threshold generalise to parakeet-unified-en-0.6b and multitalker, or does
   each model need its own threshold?
5. Which model + post-correction combination gives the best EA-DV vs latency trade-off?

## Dependencies

- **t0015_streaming_buffer_interval** (in_progress): provides the prediction JSONL files and
  the domain vocabulary list. This task cannot start until those files are available.

## Checklist Coverage

- Motivation: yes — EA-DV 33.3% gap identified in t0015 justifies post-correction
- All runs listed explicitly: yes — six runs across three models, with/without correction
- All registered metrics computed for every run: yes — all seven metrics plus efficiency
  metrics
- Efficiency metrics included: yes — efficiency_inference_time_per_item_seconds and
  efficiency_inference_cost_per_item_usd
- Assets specified: yes — answer asset; expected_assets in task.json set to {"answer": 1}
- Intermediate data: post-corrected JSONL saved to data/ within the task
- Training protocol: N/A — no training
- GPU recommendations: A10G for re-inference if needed; CPU sufficient for correction
- Budget estimate: $2–5 with per-run breakdown
- Charts listed with axis labels: yes — four charts specified above
- All charts saved to results/images/ and embedded: yes
- Key questions: five numbered, concrete, falsifiable
- Source suggestion: none applicable — task derived from t0015 findings
- Dependencies justified: t0015 provides the JSONL and vocab list

</details>
