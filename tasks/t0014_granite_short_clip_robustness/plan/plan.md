---
spec_version: "2"
task_id: "t0014_granite_short_clip_robustness"
date_completed: "2026-06-29"
status: "complete"
---

# Plan — Granite Short-Clip Robustness Validation + Production Fit Assessment

## Objective

Validate whether Granite Speech 4.1 2B avoids the short-clip failure modes (empty output,
hallucination) that disqualified Whisper turbo from production use in brainpowa-realtime-api.
Whisper was replaced by Parakeet TDT 0.6b-v3 because it produced hallucinations or empty output on
short audio utterances in the chunked re-transcribe streaming pattern. The gold-92 benchmark
(minimum clip duration 3.07 s) cannot test this failure mode. t0012 showed Granite matches Whisper
on entity accuracy (41.1% vs 42.0%) and significantly outperforms Parakeet (23.2%); the remaining
production decision question is whether Granite avoids Whisper's short-clip failure mode.

This plan covers four parts: (1) synthesize 40–60 short clips (0.5–3 s) trimmed from gold-92 WAV
files; (2) run GPU inference via `STTAdapter.transcribe_stream()` for all three models; (3)
stratified analysis across six duration strata combining synthetic clips with gold-92 data; and (4)
produce an answer asset with a YES/NO/CONDITIONAL production recommendation. Success is defined as:
all three models evaluated on all synthetic clips, all seven registered project metrics computed for
gold-92 strata, hallucination rates reported per stratum, and an answer asset with an explicit
recommendation backed by stratified evidence.

## Task Requirement Checklist

> **Task name**: Granite Short-Clip Robustness Validation + Production Fit Assessment
>
> **Short description**: Validate Granite Speech 4.1 2B robustness on short clips vs Parakeet via
> production streaming simulation, and assess production fit as a Parakeet replacement in brainpowa.
>
> **Key research questions from task_description.md**:
> 1. Does Whisper turbo produce hallucinations or empty output on clips under 3 s when run via
>    `transcribe_stream()` with 32kB PCM-16 chunks? At what duration threshold does failure begin?
> 2. Does Granite Speech 4.1 2B avoid this failure mode on the same clips?
> 3. Does Parakeet show any short-clip failure behavior?
> 4. How do Granite and Parakeet compare on entity accuracy and WER stratified by clip duration?
> 5. What is the integration effort to add a `granite.py` STTAdapter to brainpowa-realtime-api?
>
> **Critical constraint**: All inference MUST use `STTAdapter.transcribe_stream()` with a 32kB
> PCM-16 mono chunk `asyncio.Queue`. Do NOT call `model.transcribe()` directly.

* **REQ-1** Synthesize 40–60 short clips trimmed from gold-92 WAV files at duration bins 0.5 s,
  1.0 s, 1.5 s, 2.0 s, 2.5 s, 3.0 s (5–8 clips per bin), including edge cases (0.5 s silence,
  0.5 s background noise, clips with exactly one domain term). Save to `data/short_clips/` as WAV
  (16 kHz, mono, PCM-16). Save metadata to `data/short_clips_metadata.jsonl` with fields `clip_id`,
  `source_clip_id`, `duration_s`, `reference_text`. Evidence: file count ≥ 40, metadata JSONL
  exists. Satisfied by Step 1.

* **REQ-2** Run Whisper turbo via `WhisperSTT.transcribe_stream()` on all synthetic short clips.
  Config: model=`turbo`, `float16`, `cuda`, `beam_size=1`, `vad_filter=True`, `temperature=0.0`,
  `no_speech_threshold=0.6`, `initial_prompt` = 31 domain vocab terms (same as t0012). Record
  `no_speech_probability` per clip to confirm VAD misfiring mechanism. Save per-clip output to
  `data/short_clip_transcripts_whisper.jsonl`. Evidence: file exists, ≥ 40 rows. Satisfied by
  Step 3.

* **REQ-3** Run Parakeet TDT 0.6b-v3 via `ParakeetSTT.transcribe_stream()` on all synthetic short
  clips. Config: model at `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`, GPU-PB phrase
  boosting `alpha=1.0`, 66 casing variants of 31 domain terms. Save per-clip output to
  `data/short_clip_transcripts_parakeet.jsonl`. Evidence: file exists, ≥ 40 rows. Satisfied by
  Step 4.

* **REQ-4** Run Granite Speech 4.1 2B via `STTAdapter.transcribe_stream()` (base class
  accumulate-then-transcribe) on all synthetic short clips. Config: model at
  `/home/azureuser/granite-model/granite-speech-4.1-2b`, keyword prompt = 31 domain terms (same as
  t0012). Save per-clip output to `data/short_clip_transcripts_granite.jsonl`. Evidence: file
  exists, ≥ 40 rows. Satisfied by Step 5.

* **REQ-5** Per-clip output for each model must include fields: `clip_id`, `duration_s`,
  `transcript`, `is_empty` (stripped transcript == ""), `is_hallucination`, `latency_seconds`,
  `ttfd_seconds` (time to first non-empty delta). Hallucination detection: flag when transcript is
  non-empty, contains none of the reference words, AND matches known Whisper hallucination patterns
  ("Thanks for watching", "Subscribe", "[Music]", repeated punctuation, non-English tokens) using
  BoH top-30 list from `DSP-AGH/ICASSP2025_Whisper_Hallucination`. Evidence: all fields present in
  each JSONL. Satisfied by Steps 3–5.

* **REQ-6** Stratified analysis combining synthetic clips (strata 1–3) and gold-92 data from
  `tasks/t0012_whisper_parakeet_granite_streaming/data/` (strata 4–6). Six strata: <1 s, 1–2 s,
  2–3 s, 3–5 s (29 gold clips), 5–10 s (60 gold clips), >10 s (4 gold clips). Per stratum, per
  model: entity accuracy, WER, `empty_rate`, `hallucination_rate`, latency p50. Evidence:
  `results/stratified_analysis.json` with all 6 strata × 3 models × 5 metrics. Satisfied by
  Step 7.

* **REQ-7** All seven registered project metrics computed for the gold-92 strata (3–5 s, 5–10 s,
  >10 s): `entity_accuracy_gold92`, `entity_accuracy_domain_vocab`, `wer_gold92`,
  `action_critical_wer_gold92`, `intent_preservation_gold92`, `latency_p50_seconds`,
  `wrong_action_rate_gold92`. Use explicit multi-variant format in `results/metrics.json` (one
  variant per model). Evidence: `results/metrics.json` passes verificator. Satisfied by Step 8.

* **REQ-8** Three charts saved to `results/images/` and embedded in `results_detailed.md`: (a)
  short-clip failure rate by duration and model (line chart), (b) stratified entity accuracy
  (grouped bar chart), (c) latency by duration stratum (grouped bar chart p50). Evidence: 3 PNG
  files exist, embedded in results. Satisfied by Step 9.

* **REQ-9** Answer asset `granite-vs-parakeet-production-fit` covering: short-clip failure rates,
  stratified accuracy per stratum, overall EA and AC-WER from t0012, latency (249 ms vs 40 ms),
  integration effort estimate (from reading `base.py` and `parakeet.py`), and a final
  YES/NO/CONDITIONAL recommendation. Evidence: answer asset passes `verify_answer_asset.py`.
  Satisfied by Step 10.

* **REQ-10** Three prediction assets created: `whisper-turbo-short-clips`,
  `parakeet-tdt-short-clips-biased`, `granite-speech-short-clips-biased`. Each must pass
  `verify_predictions_asset.py`. Evidence: 3 assets exist under `assets/predictions/`. Satisfied by
  Step 6.

* **REQ-11** Whisper hallucination rate reported for sub-3 s clips specifically, with
  `no_speech_probability` analysis confirming VAD misfiring mechanism. Evidence: present in
  stratified analysis and answer asset. Satisfied by Steps 3 and 7.

* **REQ-12** Integration effort estimate for `granite.py` STTAdapter: read
  `brainpowa-realtime-api/src/brainpowa_realtime_api/pipeline/stt/base.py` and `parakeet.py` to
  identify what `granite.py` must implement. The base class default is accumulate-then-transcribe,
  so `granite.py` only needs to implement `transcribe()`. Document estimate in the answer asset.
  Evidence: integration section present in `full_answer.md`. Satisfied by Step 10.

* **REQ-13** BCa bootstrap with speaker-level blocks (B=1,000 replicates) for all significance
  claims on gold-92 strata. Minimum detectable WER difference at n≈50 per stratum is ±5–8 WER
  points — state this limitation explicitly. Evidence: CI values in stratified analysis.
  Satisfied by Step 7.

## Approach

### Core Design

The fundamental experiment is a duration-stratified empty-output and hallucination-rate benchmark
run via the production streaming interface. All three models are invoked through
`STTAdapter.transcribe_stream()` — not direct model calls — because the failure modes only
materialize through the production streaming path. This was confirmed in the task description and
research: brainpowa-realtime-api delivers audio as a queue of 32kB PCM-16 chunks with a `None`
sentinel, and the adapters' internal logic differs critically from direct inference.

### Key Research Findings Informing the Approach

**Granite's 4-second block-attention window**: Sub-4 s clips are processed in a single Conformer
block pass with no intermediate VAD. A 0.5 s clip yields only ~5 Q-Former acoustic embeddings; the
expected failure mode is empty output (silent degradation), not hallucination. This is why the plan
tracks `is_empty` and `is_hallucination` as separate flags.

**Parakeet chunk_secs=2 default**: All clips under 2 s (the 0.5 s, 1.0 s, 1.5 s bins) are
delivered as a single under-filled chunk plus `None` sentinel — the degenerate single-chunk path.
Confirm during implementation whether the brainpowa adapter overrides this default; results in
strata <2 s must be interpreted with this caveat.

**Whisper hallucination mechanism confirmed**: Top-2 phrases account for 35% of all non-speech
hallucinations; top-10 account for >50%. Root cause: 3 of 20 decoder heads responsible for >75% of
non-speech hallucinations — `vad_filter=True` alone does not eliminate them (Wang 2025, Baranski
2025). Log `no_speech_probability` per Whisper clip; if empty outputs correlate with
`no_speech_probability > 0.6`, the VAD misfiring mechanism is confirmed (Radford 2022).

**Hallucination detection uses BoH top-30**: The public Bag of Hallucinations CSV from
`DSP-AGH/ICASSP2025_Whisper_Hallucination` provides a citable, reproducible pattern list. Aho-
Corasick string matching is used for detection — negligible compute cost.

**Synthetic clips must be real audio trimmed from gold-92**: Synthetic TTS clips underestimate real
failure rates by 5.9× (Tay 2026). Trim real gold-92 WAV files to fixed durations rather than
generating speech.

**BCa bootstrap required for significance**: Ordinary utterance-level bootstrap gives 41.2% CI
coverage (vs 95% nominal) on correlated sets. BCa with speaker-level blocks is required. At n≈50
per stratum, minimum detectable WER difference is ±5–8 WER points — all sub-threshold differences
must be reported as not statistically distinguishable (Liu 2020).

**Granite is structurally superior for short clips**: Accumulate-then-transcribe means no VAD gate
fires on partial buffers. This structurally avoids Whisper's failure mechanism. Whether it also
avoids empty output on sub-1 s clips (due to insufficient Q-Former embeddings) is empirically
unknown — this experiment provides the evidence.

### Existing Code to Reuse

* `tasks/t0002_baseline_evaluation/` — gold-92 evaluation harness, WER and entity accuracy scoring
* `tasks/t0012_whisper_parakeet_granite_streaming/` — all three STTAdapter implementations,
  latency harness, gold-92 prediction JSONLs (no re-inference needed for gold-92 portion)
* t0012 gold-92 results (Granite EA=41.1%, Parakeet EA=23.2%, Whisper EA=42.0%) are reused
  directly from `tasks/t0012_whisper_parakeet_granite_streaming/data/`

### Task Types Applied

Task types in `task.json`: `stt-benchmark-run`, `experiment-run`, `answer-question`. All three
apply:

* **stt-benchmark-run**: Drives the registered-metric computation on gold-92 strata and the
  predictions-asset creation. Per the instruction: always start with `dvc pull`, compute all 7
  registered metrics, warm up models before timing.
* **experiment-run**: Drives the multi-variant `metrics.json` format (one variant per model),
  efficiency metrics, chart generation, predictions assets, and per-item prediction logging for
  traceability.
* **answer-question**: Drives the answer asset `granite-vs-parakeet-production-fit` with a
  YES/NO/CONDITIONAL recommendation. Per the instruction: conclusion first, no hedging, no inline
  citations in `## Answer` or `## Short Answer`.

### Alternatives Considered

**Alternative 1 — Direct model inference (model.transcribe())**: Faster to implement but does not
reproduce production failure modes. The streaming interface introduces intermediate VAD passes and
buffer-filling logic that cause the observed failures. Rejected: direct inference would produce
falsely optimistic results for Whisper and Parakeet.

**Alternative 2 — TTS-synthesized short clips**: Faster than trimming real audio and allows precise
duration control. Rejected: Tay 2026 shows TTS clips underestimate real failure rates by 5.9× due
to acoustic characteristics of clean synthetic speech. Results would not generalize to production
audio.

**Alternative 3 — Evaluate only on existing gold-92 (min 3.07 s)**: Zero new data collection cost.
Rejected: cannot answer the core research question about sub-3 s behavior; all existing benchmarks
are biased toward longer utterances.

## Cost Estimation

| Item | Cost | Reasoning |
|---|---|---|
| GPU compute — Part 2 inference (H100 NVL, ~45 min) | $0 | Reserved instance; no per-minute billing |
| GPU compute — dataset synthesis (CPU, ~10 min) | $0 | CPU-only, no GPU needed |
| External API calls (no LLM APIs used) | $0 | All inference is local model inference |
| BoH CSV download (GitHub, public) | $0 | Public repository, no cost |
| **Total** | **$0** | Within per-task limit of $100 |

GPU compute is on the Azure H100 NVL reserved instance (`azureuser@llm-t1-nc80`, conda env `stt`).
No API services billed. Total estimated cost is $0. Project budget: $2,000 total, $100 per-task
default limit. This task does not approach the limit.

## Step by Step

### Milestone 1 — Dataset Synthesis (CPU, local or remote)

1. **Set up paths and pull gold-92 audio.** On the remote machine (`azureuser@llm-t1-nc80`, conda
   env `stt`), run `dvc pull` from the task root to ensure gold-92 WAV files are present at
   `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/`. Create
   `code/paths.py` with all path constants: `GOLD92_DIR`, `SHORT_CLIPS_DIR` (`data/short_clips/`),
   `METADATA_JSONL` (`data/short_clips_metadata.jsonl`), `TRANSCRIPTS_DIR` (`data/`). Satisfies
   REQ-1 (setup).

2. **[CRITICAL] Synthesize short clips from gold-92 WAV files.** Create `code/synthesize_clips.py`.
   Load ground-truth transcripts from
   `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl`.
   For each duration bin `[0.5, 1.0, 1.5, 2.0, 2.5, 3.0]`, select 5–8 source clips with variety
   (speech-rich, silence-heavy, single recognizable domain term). Trim to exact duration using
   `soundfile` (import: `import soundfile as sf`) from the clip start. For the 0.5 s silence edge
   case, generate a silent WAV using `numpy` zeros at 16 kHz. For the 0.5 s background noise edge
   case, take the first 0.5 s of the noisiest gold-92 clip. Save all clips to `data/short_clips/`
   as WAV (16 kHz, mono, PCM-16, filename: `{source_clip_id}_{duration_s}s.wav`). Write
   `data/short_clips_metadata.jsonl` with one JSON line per clip: `clip_id`, `source_clip_id`,
   `duration_s`, `reference_text` (gold-92 transcript truncated to spoken words within the clip
   duration using word-level timing if available, else full transcript). Target: 40–60 clips total.
   Run: `uv run python -u -m arf.scripts.utils.run_with_logs --task-id t0014_granite_short_clip_robustness
   -- python code/synthesize_clips.py`. Expected output: 40–60 WAV files in `data/short_clips/`,
   metadata JSONL with matching row count. Satisfies REQ-1.

   Validation gate: run `python -c "import json; lines=open('data/short_clips_metadata.jsonl').readlines();
   print(len(lines))"` — expect ≥ 40. If < 40, check source clip count in gold-92 and expand
   selection criteria.

### Milestone 2 — GPU Inference (Remote: azureuser@llm-t1-nc80, conda stt)

3. **[CRITICAL] Run Whisper turbo on all short clips via transcribe_stream().** Create
   `code/run_whisper_short_clips.py`. Copy streaming harness from
   `tasks/t0012_whisper_parakeet_granite_streaming/code/` as a starting point. Construct an
   `asyncio.Queue` of 32kB PCM-16 chunks for each WAV file (chunk the raw PCM bytes into 32 768-
   byte blocks, enqueue them, then enqueue `None` as sentinel). Call
   `WhisperSTT.transcribe_stream(queue)` for each clip. Config: `model_size="turbo"`,
   `device="cuda"`, `compute_type="float16"`, `beam_size=1`, `vad_filter=True`,
   `temperature=0.0`, `no_speech_threshold=0.6`, `initial_prompt` = comma-separated 31 domain
   vocab terms (same prompt as t0012: "Rezolve, brainpowa, Symbiosys, ..."). Also capture
   `no_speech_probability` from the segment metadata (faster-whisper exposes this per segment).
   Warm up the model with 3 throwaway clips before recording timing. Record wall-clock latency per
   clip (`latency_seconds`), time to first non-empty delta (`ttfd_seconds`).

   Load BoH top-30 patterns from the CSV at
   `tasks/t0014_granite_short_clip_robustness/data/boh_patterns.csv` (download once from
   `https://raw.githubusercontent.com/DSP-AGH/ICASSP2025_Whisper_Hallucination/main/...` and save
   locally). Use `ahocorasick` (import: `import ahocorasick`) for pattern matching. Flag
   `is_hallucination=True` when transcript is non-empty, contains none of the reference words, and
   matches a BoH pattern.

   Write results to `data/short_clip_transcripts_whisper.jsonl` (one JSON line per clip: `clip_id`,
   `duration_s`, `transcript`, `is_empty`, `is_hallucination`, `no_speech_probability`,
   `latency_seconds`, `ttfd_seconds`). Run:
   `uv run python -u -m arf.scripts.utils.run_with_logs --task-id t0014_granite_short_clip_robustness
   -- python code/run_whisper_short_clips.py`. Expected output: JSONL with ≥ 40 rows.

   Validation gate: after run, print 5 individual rows: `python -c "import json; [print(json.loads(l))
   for l in open('data/short_clip_transcripts_whisper.jsonl')][:5]"`. Verify input was correctly
   formatted, transcript is reasonable for the clip content, scoring logic (is_empty, is_hallucination)
   is correct. If Whisper's empty rate is 0% on sub-1 s clips (implausible given VAD filtering), halt
   and debug the queue construction — chunks may be too large relative to clip length. Satisfies
   REQ-2, REQ-5, REQ-11.

4. **[CRITICAL] Run Parakeet TDT 0.6b-v3 on all short clips via transcribe_stream().** Create
   `code/run_parakeet_short_clips.py`. Same 32kB chunk queue construction as Step 3. Call
   `ParakeetSTT.transcribe_stream(queue)` for each clip. Config: model path
   `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`, GPU-PB phrase boosting `alpha=1.0`,
   66 casing variants of 31 domain terms (same as t0012). Check in `parakeet.py` whether
   `chunk_secs` is overridden — if the default of 2 s is in effect, clips under 2 s will hit the
   degenerate single-chunk path; document this in the JSONL field `notes` or a separate flag.
   Warm up with 3 throwaway clips. Write results to `data/short_clip_transcripts_parakeet.jsonl`
   (same schema as Whisper output, without `no_speech_probability`). Expected output: JSONL with
   ≥ 40 rows. Satisfies REQ-3, REQ-5.

5. **[CRITICAL] Run Granite Speech 4.1 2B on all short clips via transcribe_stream().** Create
   `code/run_granite_short_clips.py`. Same 32kB chunk queue construction. The `GraniteSTT` adapter
   uses the base class `STTAdapter.transcribe_stream()` default (accumulate-then-transcribe): it
   drains the queue into a buffer, then calls `transcribe()` once on the complete audio. Model
   path: `/home/azureuser/granite-model/granite-speech-4.1-2b`. Keyword prompt injection:
   `"transcribe the speech to text. Keywords: Rezolve, brainpowa, Symbiosys, ..."` (same 31 terms).
   Warm up with 3 throwaway clips. Write results to `data/short_clip_transcripts_granite.jsonl`
   (same schema). Expected output: JSONL with ≥ 40 rows.

   Validation gate (before full run): run on first 10 clips with `--limit 10`. Check that: (a)
   the 0.5 s clips do not produce hallucinations (expected: either empty or short transcripts),
   (b) the 2.5 s and 3.0 s clips produce plausible transcripts, (c) latency is <1 s per clip.
   If latency exceeds 1 s per clip on 0.5 s clips, investigate HuggingFace Transformers fixed
   overhead. If 0 rows are produced for all clips (pipeline bug), halt and debug the queue
   draining logic. Satisfies REQ-4, REQ-5.

6. **Create three prediction assets.** Create the asset folder structure for each model:
   * `assets/predictions/whisper-turbo-short-clips/`
   * `assets/predictions/parakeet-tdt-short-clips-biased/`
   * `assets/predictions/granite-speech-short-clips-biased/`

   For each asset, copy the JSONL from `data/short_clip_transcripts_<model>.jsonl` to
   `assets/predictions/<id>/files/predictions-short-clips.jsonl`. Write `details.json` per the
   predictions specification (spec_version "2", all required fields). Write `description.md` with
   mandatory sections (Metadata, Overview, Model, Data, Prediction Format, Metrics, Main Ideas,
   Summary). Categories: use registered categories from `meta/categories/` — `stt-evaluation`
   or the closest applicable slug. Run `uv run python -u -m arf.scripts.verificators.verify_predictions_asset
   t0014_granite_short_clip_robustness --all` and fix any errors. Satisfies REQ-10.

### Milestone 3 — Analysis and Metrics

7. **[CRITICAL] Compute stratified analysis.** Create `code/compute_stratified_analysis.py`.
   Load the three short-clip JSONLs from `data/`. Load gold-92 prediction JSONLs from
   `tasks/t0012_whisper_parakeet_granite_streaming/data/` (Whisper, Parakeet, Granite predictions
   on 93 clips). Assign each clip to a duration stratum:

   | Stratum key | Duration range | Source |
   |---|---|---|
   | `lt_1s` | 0–1 s | synthetic only |
   | `1_to_2s` | 1–2 s | synthetic only |
   | `2_to_3s` | 2–3 s | synthetic only |
   | `3_to_5s` | 3–5 s | gold-92 (29 clips) |
   | `5_to_10s` | 5–10 s | gold-92 (60 clips) |
   | `gt_10s` | >10 s | gold-92 (4 clips) |

   For each (stratum, model) combination, compute: entity accuracy (substring match against
   reference), WER (computed for strata with reference transcripts; import `jiwer` for WER),
   `empty_rate`, `hallucination_rate`, latency p50. For gold-92 strata (3_to_5s, 5_to_10s,
   gt_10s), also compute: `entity_accuracy_domain_vocab` (31 domain terms only),
   `action_critical_wer_gold92`, `intent_preservation_gold92`, `wrong_action_rate_gold92`.

   Apply BCa bootstrap with speaker-level blocks (B=1,000 replicates) for all comparisons on
   gold-92 strata. Report 95% CIs. Note: minimum detectable WER difference at n≈50 per stratum
   is ±5–8 WER points — all sub-threshold differences must be explicitly labelled as "not
   statistically distinguishable".

   Save to `results/stratified_analysis.json`: a dict with keys for each stratum, each containing
   per-model metrics. Satisfies REQ-6, REQ-13.

8. **Write results/metrics.json in explicit multi-variant format.** Import the seven registered
   metric keys: `action_critical_wer_gold92`, `entity_accuracy_domain_vocab`,
   `entity_accuracy_gold92`, `intent_preservation_gold92`, `latency_p50_seconds`, `wer_gold92`,
   `wrong_action_rate_gold92`. Use the explicit variant format (one variant per model ×
   gold-92-stratum combination) per `arf/specifications/task_results_specification.md`. Each
   variant key: `whisper_turbo`, `parakeet_tdt`, `granite_speech`. Write values from the gold-92
   strata aggregated results (strata 3_to_5s + 5_to_10s + gt_10s combined). Run:
   `uv run python -u -m arf.scripts.verificators.verify_task_results t0014_granite_short_clip_robustness`
   to confirm metrics.json is valid. Satisfies REQ-7.

9. **Generate three charts.** Create `code/generate_charts.py` using `matplotlib` and `seaborn`.

   Chart A (`results/images/short_clip_failure_rate.png`): Line chart. X-axis: duration bins
   [0.5, 1.0, 1.5, 2.0, 2.5, 3.0] seconds. Y-axis: failure rate (%). Lines: `empty_rate` and
   `hallucination_rate` per model (6 lines total). Title: "Short-Clip Failure Rate by Duration and
   Model".

   Chart B (`results/images/stratified_entity_accuracy.png`): Grouped bar chart. X-axis: 6 duration
   strata. Y-axis: entity accuracy (%). Bars: Whisper / Granite / Parakeet. Include error bars from
   BCa CIs for gold-92 strata. Title: "Stratified Entity Accuracy by Duration".

   Chart C (`results/images/latency_by_stratum.png`): Grouped bar chart. X-axis: 6 duration strata.
   Y-axis: latency p50 (seconds). Bars: Whisper / Granite / Parakeet. Title: "Latency p50 by
   Duration Stratum". Include horizontal reference line at 0.800 s (production latency constraint).

   Expected output: 3 PNG files at `results/images/`. Satisfies REQ-8.

### Milestone 4 — Answer Asset

10. **[CRITICAL] Read brainpowa adapter source and write answer asset.** Read
    `brainpowa-realtime-api/src/brainpowa_realtime_api/pipeline/stt/base.py` and
    `brainpowa-realtime-api/src/brainpowa_realtime_api/pipeline/stt/parakeet.py` to determine:
    (a) what methods `STTAdapter` declares as abstract, (b) what `ParakeetSTT` implements beyond
    `transcribe()`, (c) what `granite.py` would need to implement. The base class default
    `transcribe_stream()` is accumulate-then-transcribe — so `granite.py` only needs to implement
    `transcribe()` plus model loading. Estimate: ~50–100 lines of Python.

    Create answer asset at
    `assets/answer/granite-vs-parakeet-production-fit/`:
    * `details.json` — spec_version "2", `answer_id` "granite-vs-parakeet-production-fit",
      `question` = "Should Granite Speech 4.1 2B replace Parakeet TDT 0.6b-v3 as the production
      STT model in brainpowa-realtime-api?", `answer_methods` includes "code-experiment",
      `source_task_ids` includes "t0012_whisper_parakeet_granite_streaming" and
      "t0014_granite_short_clip_robustness", `confidence` based on evidence quality.
    * `short_answer.md` — mandatory sections: `## Question`, `## Answer` (2-5 sentences,
      YES/NO/CONDITIONAL first, no inline citations), `## Sources`.
    * `full_answer.md` — mandatory sections: Question, Short Answer, Research Process, Evidence
      from Papers, Evidence from Internet Sources, Evidence from Code or Experiments (citing this
      task's inference results), Synthesis, Limitations, Sources (with markdown reference links).

    Evidence to cover in full_answer.md:
    * Short-clip failure rates per model per duration bin (from Step 7)
    * Stratified entity accuracy per stratum (from Step 7)
    * Overall EA and AC-WER from t0012: Granite 41.1%/7.6% vs Parakeet 23.2%/33.5% vs Whisper
      42.0%/6.3%
    * Latency: Granite p50 249 ms vs Parakeet 40 ms — both within 800 ms p50 production
      constraint, but 6× overhead is material
    * Integration effort from `base.py`/`parakeet.py` analysis
    * Recommendation: YES if Granite avoids empty output on sub-2 s clips; CONDITIONAL if empty
      rate >10% on sub-2 s bins (recommend with minimum clip duration gate in production);
      NO if empty rate >30% and entity accuracy advantage lost in short-duration strata.

    Run `uv run python -u -m arf.scripts.verificators.verify_answer_asset t0014_granite_short_clip_robustness
    granite-vs-parakeet-production-fit` and fix any errors. Satisfies REQ-9, REQ-12.

11. **DVC-track synthetic clips and prediction JSONLs.** Run `dvc add data/short_clips/` and
    `dvc add data/short_clip_transcripts_*.jsonl`. Run `dvc push`. This ensures data is available
    for downstream tasks without re-running inference.

## Remote Machines

**Machine required**: Azure H100 NVL, hostname `llm-t1-nc80`, user `azureuser`, conda environment
`stt`.

* **GPU type**: NVIDIA H100 NVL (80 GB HBM3)
* **VRAM**: ~20 GB peak (all three models loaded sequentially, not simultaneously)
* **Estimated runtime**: ~45 min GPU time (15 min Whisper, 10 min Parakeet, 20 min Granite),
  plus 10 min CPU for dataset synthesis
* **Provider**: Azure reserved instance (no per-minute cost)
* **Access**: SSH via `azureuser@llm-t1-nc80`; see `arf/specifications/remote_machines_specification.md`
  for lifecycle details

Milestone 1 (dataset synthesis) and Milestones 3–4 (analysis and answer asset) can run locally
or on the remote machine. Milestone 2 (inference) requires the remote GPU machine for model loading
and CUDA inference.

## Assets Needed

* **Gold-92 audio**: `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/` —
  DVC-tracked; run `dvc pull` before starting.
* **Gold-92 ground truth**: `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/
  ground_truth.jsonl` — clip transcripts used to generate reference_text for short clips.
* **t0012 prediction JSONLs**: `tasks/t0012_whisper_parakeet_granite_streaming/data/` — gold-92
  predictions for all three models; no re-inference needed for the gold-92 portion.
* **t0012 STTAdapter code**: `tasks/t0012_whisper_parakeet_granite_streaming/code/` — streaming
  harness to adapt for short-clip queue construction.
* **brainpowa adapter source**: `brainpowa-realtime-api/src/brainpowa_realtime_api/pipeline/stt/
  base.py` and `parakeet.py` — read during Step 10 for integration effort estimate.
* **BoH top-30 CSV**: `https://raw.githubusercontent.com/DSP-AGH/ICASSP2025_Whisper_Hallucination/
  main/...` — download once and save to `data/boh_patterns.csv` before Step 3.
* **Model checkpoints** (on remote machine):
  * Whisper turbo: loaded via faster-whisper API (auto-download or cached)
  * Parakeet: `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`
  * Granite: `/home/azureuser/granite-model/granite-speech-4.1-2b`

## Expected Assets

As specified in `task.json` (`expected_assets: {answer: 1, predictions: 3}`):

* **predictions** (×3):
  * `assets/predictions/whisper-turbo-short-clips/` — Whisper turbo predictions on 40–60 synthetic
    short clips (0.5–3 s). Per-clip fields: clip_id, duration_s, transcript, is_empty,
    is_hallucination, no_speech_probability, latency_seconds, ttfd_seconds.
  * `assets/predictions/parakeet-tdt-short-clips-biased/` — Parakeet TDT 0.6b-v3 predictions on
    the same clips. Labeled "biased" because results for sub-2 s clips are affected by the
    degenerate single-chunk behavior of the chunk_secs=2 default.
  * `assets/predictions/granite-speech-short-clips-biased/` — Granite Speech 4.1 2B predictions on
    the same clips. Labeled "biased" because results for sub-4 s clips involve the single-block
    attention path.

* **answer** (×1):
  * `assets/answer/granite-vs-parakeet-production-fit/` — Answer to: "Should Granite Speech 4.1 2B
    replace Parakeet TDT 0.6b-v3 as the production STT model in brainpowa-realtime-api?" Contains
    `details.json`, `short_answer.md`, `full_answer.md`. The short answer begins with YES, NO, or
    CONDITIONAL followed by specific conditions.

## Time Estimation

| Phase | Wall-clock | Notes |
|---|---|---|
| Research (already complete) | — | research_summary.md exists |
| Planning (this step) | 1 h | Done |
| Dataset synthesis (Milestone 1) | 20 min | CPU; audio trimming with soundfile |
| GPU inference — Whisper (Milestone 2, Step 3) | 20 min | 40–60 clips × ~20 s each |
| GPU inference — Parakeet (Milestone 2, Step 4) | 15 min | 40–60 clips × ~15 s each |
| GPU inference — Granite (Milestone 2, Step 5) | 25 min | 40–60 clips × ~30 s each |
| Predictions asset creation (Step 6) | 20 min | Writing JSON metadata |
| Stratified analysis + metrics (Steps 7–8) | 30 min | BCa bootstrap B=1,000 |
| Chart generation (Step 9) | 20 min | 3 matplotlib charts |
| Answer asset writing (Step 10) | 45 min | Reading base.py, writing full_answer.md |
| DVC push (Step 11) | 10 min | Upload to Azure Blob |
| **Total** | **~4 h** | Including setup and verification |

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Granite empty output on all sub-1 s clips (5 Q-Former embeddings insufficient) | Medium | Reduces evidence base for sub-1 s stratum; does not block task | Proceed; report `empty_rate=100%` for that stratum; state explicitly in answer asset that sub-1 s behavior is empirically unknown from prior literature |
| Parakeet chunk_secs=2 not overridden in brainpowa adapter, making sub-2 s results unreliable | High | Sub-2 s strata data is structurally confounded | Confirm in `parakeet.py` before inference; add `notes` field to JSONL; label prediction asset "biased"; note in answer asset |
| BoH CSV URL broken or repository moved | Low | Hallucination detection pattern unavailable | Fall back to hardcoded list from task description ("Thanks for watching", "Subscribe", "[Music]", repeated punctuation). Cite task description as source instead of BoH paper. |
| t0012 prediction JSONLs not on disk (dvc pull needed) | Medium | Steps 7–8 cannot load gold-92 strata | Run `dvc pull` from t0012 task directory; if DVC remote unreachable, contact team for direct file transfer |
| Remote machine unavailable or conda env `stt` missing models | Medium | Blocks Milestone 2 entirely | SSH to `llm-t1-nc80` before starting; verify model paths exist; if unavailable, create `plan/INTERVENTION.md` documenting the blocker |
| NeMo streaming bugs (NeMo-Issue14714, NeMo-Issue15143) causing Parakeet word-confidence crashes | Low | Parakeet inference aborts on some clips | Wrap `ParakeetSTT.transcribe_stream()` in try-except; log errors to JSONL as `is_empty=True`; document in results |
| brainpowa-realtime-api not present in working directory (needed for integration estimate) | Medium | REQ-12 cannot be satisfied without reading base.py | Check path; if absent, estimate from t0012 code knowledge and label as approximate in answer asset |
| BCa bootstrap unstable at n=4 clips (gt_10s stratum) | High | CIs for gt_10s stratum are meaningless | Report raw metrics only for gt_10s stratum; exclude from significance claims; note explicitly |

## Verification Criteria

* **Clip count and metadata**: `python -c "import json; lines=open('tasks/t0014_granite_short_clip_robustness/data/short_clips_metadata.jsonl').readlines(); print(len(lines))"` — expect ≥ 40 and ≤ 60. All fields (`clip_id`, `source_clip_id`, `duration_s`, `reference_text`) must be present. Satisfies REQ-1.

* **Inference output completeness**: `for f in data/short_clip_transcripts_whisper.jsonl data/short_clip_transcripts_parakeet.jsonl data/short_clip_transcripts_granite.jsonl; do python -c "import json; rows=[json.loads(l) for l in open('tasks/t0014_granite_short_clip_robustness/$f')]; print(f, len(rows), 'rows')"; done` — expect ≥ 40 rows per file. Satisfies REQ-2, REQ-3, REQ-4.

* **Predictions assets pass verificator**: `uv run python -u -m arf.scripts.verificators.verify_predictions_asset t0014_granite_short_clip_robustness --all` — zero errors. Satisfies REQ-10.

* **Plan verificator**: `uv run python -u -m arf.scripts.verificators.verify_plan t0014_granite_short_clip_robustness` — zero errors. Satisfies plan completeness.

* **Metrics.json is valid**: `uv run python -u -m arf.scripts.verificators.verify_task_results t0014_granite_short_clip_robustness` — zero errors. All 7 registered metrics present for 3 model variants. Satisfies REQ-7.

* **Answer asset passes verificator**: `uv run python -u -m arf.scripts.verificators.verify_answer_asset t0014_granite_short_clip_robustness granite-vs-parakeet-production-fit` — zero errors. Short answer `## Answer` section begins with YES, NO, or CONDITIONAL. Satisfies REQ-9.

* **Charts exist and are embedded**: `ls tasks/t0014_granite_short_clip_robustness/results/images/` — expect `short_clip_failure_rate.png`, `stratified_entity_accuracy.png`, `latency_by_stratum.png`. All three embedded in `results_detailed.md` using `![...](images/...)` syntax. Satisfies REQ-8.

* **Hallucination rate reported for Whisper sub-3 s clips**: `python -c "import json; rows=[json.loads(l) for l in open('tasks/t0014_granite_short_clip_robustness/data/short_clip_transcripts_whisper.jsonl')]; sub3=[r for r in rows if r['duration_s']<3.0]; print('sub3s count:', len(sub3), 'halluc rate:', sum(r['is_hallucination'] for r in sub3)/len(sub3))"` — expect sub3 count ≥ 30 and halluc_rate is a numeric value (not NaN). Satisfies REQ-11.

* **REQ coverage check**: Confirm `results/stratified_analysis.json` contains keys for all 6 strata and all 3 models, with `empty_rate` and `hallucination_rate` fields in each. `python -c "import json; d=json.load(open('tasks/t0014_granite_short_clip_robustness/results/stratified_analysis.json')); assert len(d)==6; print('strata:', list(d.keys()))"` — expect 6 strata keys. Satisfies REQ-6.

## Rejection Criteria

These conditions require declaring this task's benchmark results **null** — do not report them as
real measurements:

* **Inference pipeline broken**: If `successful_clips / total_clips < 0.8` for any model, the run
  is null for that model. This means ≥ 8 clips returning errors (not empty transcripts — errors in
  the transcribe_stream() call itself). Pre-register before running: do not retroactively loosen.

* **Direct model calls used**: If any inference step bypassed `transcribe_stream()` and called
  `model.transcribe()` directly, results are null — they do not reproduce production failure modes.

* **Wrong audio format**: If short clips were not saved as 16 kHz, mono, PCM-16, results may not
  reflect production conditions. Verify with `soxi data/short_clips/*.wav | grep "Sample Rate"` —
  all must be 16000.

* **Model checkpoint mismatch**: If a model at a different path or version than specified was used
  (e.g., a different Granite version), results are not comparable to t0012 baselines. Document
  the actual model path in prediction asset metadata.
