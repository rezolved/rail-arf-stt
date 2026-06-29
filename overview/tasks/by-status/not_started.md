# ⏹ Tasks: Not Started

1 tasks. ⏹ **1 not_started**.

[Back to all tasks](../README.md)

---

## ⏹ Not Started

<details>
<summary>⏹ 0014 — <strong>Granite Short-Clip Robustness Validation + Production
Fit Assessment</strong></summary>

| Field | Value |
|---|---|
| **ID** | `t0014_granite_short_clip_robustness` |
| **Status** | not_started |
| **Effective date** | — |
| **Dependencies** | [`t0013_brainstorm_results_1`](../../../overview/tasks/task_pages/t0013_brainstorm_results_1.md), [`t0012_whisper_parakeet_granite_streaming`](../../../overview/tasks/task_pages/t0012_whisper_parakeet_granite_streaming.md) |
| **Expected assets** | 1 answer, 3 predictions |
| **Source suggestion** | `S-0005-03` |
| **Task types** | [`stt-benchmark-run`](../../../meta/task_types/stt-benchmark-run/), [`experiment-run`](../../../meta/task_types/experiment-run/), [`answer-question`](../../../meta/task_types/answer-question/) |
| **Task page** | [Granite Short-Clip Robustness Validation + Production Fit Assessment](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Task folder** | [`t0014_granite_short_clip_robustness/`](../../../tasks/t0014_granite_short_clip_robustness/) |

# t0014 — Granite Short-Clip Robustness Validation + Production Fit Assessment

## Motivation

Whisper turbo was the previous production STT model in brainpowa-realtime-api and was replaced
by Parakeet TDT 0.6b-v3 because it produced hallucinations or empty output on short audio
utterances in the chunked re-transcribe streaming pattern. The gold-92 benchmark (minimum clip
duration 3.07s) cannot test this failure mode — all existing benchmark results are biased
toward longer utterances.

t0012 established that Granite Speech 4.1 2B matches Whisper turbo on entity accuracy (41.1%
vs 42.0%) and significantly outperforms the current production Parakeet model (23.2% EA). The
remaining question for the production decision is: does Granite avoid the short-clip failure
mode that disqualified Whisper? And is Granite production-ready as a drop-in STTAdapter
replacement?

This task answers both questions with evidence from actual inference runs in production
streaming mode.

## Key Research Questions

1. Does Whisper turbo produce hallucinations or empty output on clips under 3 seconds when run
   via `transcribe_stream()` with 32kB PCM-16 chunks? At what duration threshold does failure
   begin?
2. Does Granite Speech 4.1 2B avoid this failure mode on the same clips?
3. Does Parakeet show any short-clip failure behavior?
4. How do Granite and Parakeet compare on entity accuracy and WER stratified by clip duration?
5. What is the integration effort to add a `granite.py` STTAdapter to brainpowa-realtime-api?

## Critical Constraint: Production Streaming Simulation

**All inference MUST use the `STTAdapter.transcribe_stream()` interface with a 32kB PCM-16
mono chunk `asyncio.Queue`.** Do NOT call `model.transcribe()` directly. The production path
in brainpowa-realtime-api delivers audio as a queue of 32kB chunks with a `None` sentinel —
this is what the benchmark must simulate. Using direct model inference would not reproduce the
failure modes observed in production.

Each adapter's `transcribe_stream()` behavior:

* **Whisper** (`WhisperSTT.transcribe_stream`): chunked re-transcribe — transcribes the
  growing buffer every 32kB interval. On short clips, may trigger VAD on incomplete audio,
  producing hallucinations or empty results.
* **Parakeet** (`ParakeetSTT.transcribe_stream`): chunked re-transcribe — same pattern as
  Whisper but with NeMo. Short clips may only deliver 1 chunk before the `None` sentinel.
* **Granite** (`STTAdapter` base class default): accumulate-then-transcribe — accumulates all
  chunks, then calls `transcribe()` once on the complete audio. No intermediate VAD passes.

## Scope

### Part 1 — Synthetic Short-Clip Dataset

Synthesize short clips from gold-92 WAV files by trimming each to fixed durations:

* Duration bins: 0.5s, 1.0s, 1.5s, 2.0s, 2.5s, 3.0s
* Select 5–8 source clips per bin (varying content: speech-rich, silence-heavy, single-word)
* Edge cases: 0.5s silence (generated), 0.5s background noise (first 0.5s of a noisy clip),
  clips containing exactly one recognizable domain term ("Rezolve", "brainpowa")
* Target: 40–60 test clips total
* Save to `data/short_clips/` as WAV (16kHz, mono, PCM-16)
* Save clip metadata to `data/short_clips_metadata.jsonl`: clip_id, source_clip_id,
  duration_s, reference_text (from gold-92 ground truth, truncated to actual spoken content)

### Part 2 — GPU Inference on Short Clips

Machine: Azure H100 NVL (`gpu-azure`, `azureuser@llm-t1-nc80`, conda env `stt`).

Run all three models via `transcribe_stream()` on every short clip:

**Whisper turbo** (faster-whisper):

* Model size: `turbo`, `float16`, `cuda`
* `beam_size=1`, `vad_filter=True`, `temperature=0.0`, `no_speech_threshold=0.6`
* `initial_prompt`: comma-separated 31 domain vocab terms (same as t0012)

**Parakeet TDT 0.6b-v3** (NeMo):

* Model path: `/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3`
* GPU-PB phrase boosting, `alpha=1.0`, 66 casing variants of 31 domain terms

**Granite Speech 4.1 2B** (HuggingFace Transformers):

* Model path: `/home/azureuser/granite-model/granite-speech-4.1-2b`
* Keyword prompt injection: `"transcribe the speech to text. Keywords: Rezolve, ..."` (same 31
  terms as t0012)

Per-clip output (save to `data/short_clip_transcripts_<model>.jsonl`):

* `clip_id`, `duration_s`, `transcript`, `is_empty` (transcript stripped == ""),
  `latency_seconds`, `ttfd_seconds` (time to first non-empty delta from `transcribe_stream()`)

Hallucination detection: flag as `is_hallucination=True` when transcript is non-empty but
contains none of the reference words AND matches known Whisper hallucination patterns (e.g.,
"Thanks for watching", "Subscribe", "[Music]", repeated punctuation, non-English tokens on
English audio).

### Part 3 — Stratified Analysis

Combine new short-clip results with t0012 gold-92 data (from
`tasks/t0012_whisper_parakeet_granite_streaming/data/`).

Duration strata:

| Stratum | Duration range | Source |
| --- | --- | --- |
| < 1s | 0–1s | synthetic only |
| 1–2s | 1–2s | synthetic only |
| 2–3s | 2–3s | synthetic only |
| 3–5s | 3–5s | gold-92 (29 clips) |
| 5–10s | 5–10s | gold-92 (60 clips) |
| > 10s | > 10s | gold-92 (4 clips) |

Metrics per stratum per model:

* Entity accuracy (substring match against reference)
* WER (computed only for strata with reference transcripts)
* `empty_rate` — fraction of clips with empty transcript
* `hallucination_rate` — fraction of clips with `is_hallucination=True`
* Latency p50 (seconds)

### Part 4 — Answer Asset: Production Recommendation

Answer ID: `granite-vs-parakeet-production-fit`

Question: "Should Granite Speech 4.1 2B replace Parakeet TDT 0.6b-v3 as the production STT
model in brainpowa-realtime-api?"

Evidence to cover in the answer:

* Short-clip failure rates: Whisper vs Granite vs Parakeet (from Part 2)
* Stratified accuracy at each duration stratum (from Part 3)
* Overall EA and AC-WER from t0012 (Granite 41.1% / 7.6% vs Parakeet 23.2% / 33.5%)
* Latency: Granite p50 249ms vs Parakeet 40ms — is the 6x overhead acceptable?
* Integration effort: read
  `brainpowa-realtime-api/src/brainpowa_realtime_api/pipeline/stt/base.py` and `parakeet.py`
  to determine what `granite.py` needs to implement. The base class
  `STTAdapter.transcribe_stream()` default is accumulate-then-transcribe, so `granite.py` only
  needs to implement `transcribe()`. Estimate implementation effort.
* Final recommendation: YES/NO/CONDITIONAL with explicit conditions

## Metrics

All seven registered project metrics computed for the stratified gold-92 portion (strata 3–5s,
5–10s, > 10s):

| Metric | All three models |
| --- | --- |
| Entity Accuracy (gold-92) | ✓ |
| Entity Accuracy — Domain Vocabulary | ✓ |
| Word Error Rate (gold-92) | ✓ |
| Action-Critical WER (gold-92) | ✓ |
| Intent Preservation (gold-92) | ✓ |
| Latency p50 (seconds) | ✓ |
| Wrong Action Rate (gold-92) | ✓ |

Additional metrics (short clips, all strata):

* `empty_rate` per stratum per model
* `hallucination_rate` per stratum per model (Whisper primarily)
* TTFD p50 per stratum per model

## Baselines

* Parakeet production (t0009): EA=23.2%, AC-WER=33.5%, lat p50=38ms
* Granite streaming (t0012): EA=41.1%, AC-WER=7.6%, lat p50=249ms
* Whisper turbo streaming (t0012): EA=42.0%, AC-WER=6.3%, lat p50=290ms

## Assets

1. `whisper-turbo-short-clips` — Whisper predictions on synthetic short clips
2. `parakeet-tdt-short-clips-biased` — Parakeet predictions on synthetic short clips
3. `granite-speech-short-clips-biased` — Granite predictions on synthetic short clips
4. `granite-vs-parakeet-production-fit` — Answer asset: production recommendation

## Charts

All charts saved to `results/images/` and embedded in `results_detailed.md`.

1. **Short-clip failure rate by duration and model** — line chart, x-axis: duration bin,
   y-axis: failure rate (%), lines: empty_rate and hallucination_rate per model. Answers: at
   what duration does each model start failing?
2. **Stratified entity accuracy** — grouped bar chart, x-axis: duration stratum, y-axis: EA
   (%), bars: Whisper / Granite / Parakeet. Answers: does Granite maintain accuracy advantage
   across all durations?
3. **Latency by duration stratum** — grouped bar chart p50, x-axis: stratum, y-axis: seconds.
   Answers: does Granite's latency overhead increase on short clips?

## Compute and Budget

| Run | Est. wall-clock | Notes |
| --- | --- | --- |
| Part 1 — dataset synthesis | 10 min | CPU, local or remote |
| Part 2 — Whisper short clips | 15 min | GPU, O(N) passes |
| Part 2 — Parakeet short clips | 10 min | GPU |
| Part 2 — Granite short clips | 20 min | GPU |
| Part 3–4 — analysis + answer | 30 min | CPU |

Total GPU time: ~45 min on Azure H100 NVL. Estimated cost: $0 (reserved instance).

## Data Handling

* Gold-92 source audio: `tasks/t0001_stt_benchmark/` (DVC-tracked). Run `dvc pull` before
  starting.
* t0012 JSONL predictions: `tasks/t0012_whisper_parakeet_granite_streaming/data/` (already on
  disk, no re-inference needed for gold-92 portion).
* Synthetic clips saved to `data/short_clips/` and DVC-tracked.
* Prediction JSONLs saved to `data/`.

## Verification Criteria

* 40+ synthetic clips generated and saved to `data/short_clips/`.
* All three models run on all synthetic clips via `transcribe_stream()` (not direct model
  call).
* `hallucination_rate` reported for Whisper on sub-3s clips.
* Answer asset written with explicit YES/NO/CONDITIONAL recommendation.
* All registered metrics computed for gold-92 strata.
* Three charts generated and embedded in `results_detailed.md`.

</details>
