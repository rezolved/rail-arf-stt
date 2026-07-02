# Streaming STT Model Survey: Native Incremental Decoding Architectures

## Motivation

`t0005_stt_model_survey_brainpowa` surveyed open-source STT candidates across eight dimensions, of
which streaming support was only one. Since then, `t0012`–`t0017` established that streaming
behavior is the dominant lever for perceived latency in the brainpowa voice-commerce pipeline:
t0017's real-time-paced measurement showed TTFD scales almost linearly with buffer interval, and
production already reframes audio into 32ms VAD frames before STT
(`brainpowa-realtime-api/pipeline/orchestrator.py:946-952`). The project has so far only evaluated
streaming behavior for models already in scope (Parakeet family, Granite, Whisper, Moonshine).

This task closes the gap on the *model landscape* side: a survey whose sole axis is streaming
capability, done exhaustively rather than as one of many dimensions. The goal is to surface any
candidate — including ones not yet considered — whose native incremental-decoding architecture could
beat the current Parakeet-unified + ~300ms-buffer configuration on responsiveness without
sacrificing the entity-accuracy gains already won.

## Research Question

Which open-source / open-weight STT models support **true incremental (streaming) decoding** —
producing partial hypotheses as audio arrives, not just accepting arbitrary-length input — and how
do their streaming architectures compare on chunk/frame granularity, latency or real-time-factor
(RTF), and integration effort into the brainpowa `STTAdapter.transcribe_stream` interface
(`src/brainpowa_realtime_api/pipeline/stt/base.py`)?

**Recency constraint:** prioritize models released or with a major streaming-relevant update in the
**last 6 months** (2026-01-02 through 2026-07-02, relative to this task's creation date). Older
established families already covered by prior tasks (Parakeet, Granite, Whisper, Moonshine,
FunASR/Paraformer) should be included for comparison but only re-documented briefly by pointing to
existing task results; the bulk of the search effort goes toward surfacing what shipped in this
window that is new to the project.

This is **not** a general STT survey (that is `t0005`). A candidate that has excellent offline WER
but only supports batch/whole-utterance inference (bolted-on "streaming" via re-running batch
inference on a growing buffer, e.g. the current Parakeet accumulate-then-retranscribe pattern) must
be explicitly flagged as *pseudo-streaming*, distinct from models with native streaming decoder
architectures (streaming RNNT/TDT, streaming CTC with chunked attention, streaming Conformer,
full-duplex models like Moshi).

## Scope

### Candidate families (not exhaustive — expand with any 2025–2026 releases found)

* **NVIDIA Parakeet / Canary / FastConformer** — streaming RNNT/TDT/CTC configs, chunked attention
  variants, `multitalker-parakeet-streaming-0.6b-v1` (used in t0015).
* **Kyutai Moshi / Kyutai STT** — full-duplex streaming, the most architecturally distinct
  candidate; capture its frame size and codec-based streaming approach in detail.
* **Moonshine** — fast English streaming ASR (already benchmarked non-streaming-focused in t0008).
* **Whisper streaming variants** — whisper_streaming, WhisperLive, simul-whisper, faster-whisper
  streaming wrappers — distinguish true incremental decoding from sliding-window re-inference.
* **FunASR / Paraformer streaming** — Paraformer-streaming, U2/U2++ streaming Conformer.
* **wav2vec2 / MMS streaming** — chunked/streaming CTC configs if they exist.
* **IBM Granite Speech streaming** mode (already used non-streaming in t0007/t0012/t0014/t0015 —
  document what native streaming support exists, if any).
* **Google USM / Chirp streaming** (if open-weight variants exist; flag closed/API-only clearly).
* **Any newer 2025–2026 streaming ASR releases** surfaced during search (e.g. streaming
  Conformer-Transducer research releases, new Alibaba/NVIDIA/Meta streaming models).

### Per-candidate dimensions to record

For every candidate, capture (mark "unknown / not reported" rather than guessing):

1. Model family, sizes, parameter count, license, weights location (HF/GitHub).
2. **Streaming mechanism**: architecture class (streaming RNNT/TDT, chunked CTC, streaming
   Conformer, full-duplex codec-based, etc.) — the core focus of this survey.
3. **True streaming vs pseudo-streaming**: does the model emit partial hypotheses incrementally, or
   does "streaming support" mean re-running batch inference on a growing buffer? State the mechanism
   explicitly, do not take vendor marketing claims at face value — check the model card / paper /
   code for how partial results are produced.
4. Chunk / frame size the streaming mode operates on (e.g., 32ms, 80ms, 320ms) and any configurable
   look-ahead/right-context.
5. Reported latency or RTF in streaming mode specifically (not offline/batch RTF).
6. Contextual biasing / hotword support in streaming mode (may differ from batch mode).
7. Integration effort into `STTAdapter.transcribe_stream` — existing async generator support,
   framework (NeMo streaming API, HF, ctranslate2, custom), PCM-16 mono input handling.
8. Fit verdict vs currently-integrated parakeet-unified-en-0.6b at ~300ms buffer (t0017 result) and
   Granite Speech 4.1 2B (t0007/t0012/t0014/t0015, best entity accuracy but batch-only so far).

### Inclusions

* Open-source / open-weight, self-hostable inference.
* GPU-requiring models acceptable.
* Any model with a documented streaming/incremental mode, even if evaluated non-streaming elsewhere
  in this project.

### Exclusions

* Closed cloud-only streaming APIs with no downloadable weights (Azure Speech, Google STT streaming,
  Deepgram, AssemblyAI) — list as named comparison baselines only, not candidates.
* Re-surveying non-streaming accuracy already covered by `t0005`, `t0007`–`t0012`.
* Techniques already covered by `t0003_literature_review_entity_stt` (contextual biasing methods in
  general) — only note biasing *as it interacts with streaming mode* here.

## Approach

Follow the `internet-research` task type guidelines.

### Search strategy

Define queries before searching; log every query + result count in `research/search_log.md`. Cover
at least:

* "streaming ASR" / "incremental speech recognition" / "real-time speech-to-text" + each candidate
  family.
* "streaming RNNT" / "streaming transducer" / "chunked attention streaming Conformer" / "full-duplex
  speech" architecture terms.
* Official model cards, GitHub repos, and NeMo/HF streaming inference docs for chunk size and
  latency claims.
* 2025–2026 release announcements from NVIDIA, Kyutai, Useful Sensors, Alibaba, IBM, Google, Meta.
* Cross-check any RTF/latency claim against at least one independent source or benchmark.

### Process

* Broad landscape pass first (what streaming architectures exist), then narrow per candidate.
* Weight search effort toward releases/updates from the last 6 months (2026-01-02 to 2026-07-02);
  explicitly search "2026 streaming ASR release", "new streaming speech recognition model 2026", and
  vendor blogs/changelogs (NVIDIA, Kyutai, HF, Alibaba, IBM, Google, Meta) for that window.
* Record every URL with date accessed, source org, and a one-line contribution note.
* Explicitly separate "native streaming decoder" candidates from "pseudo-streaming via re-inference"
  candidates in the write-up structure — this distinction is the main value of the survey.
* Write `research/research_internet.md` incrementally, structured by dimension/candidate.

### Stopping criterion

Stop when every candidate family listed above (plus any newer releases found) is scored on all eight
dimensions, the true-streaming vs pseudo-streaming split is clear for each, and at least 3
candidates are ranked with enough evidence to justify a follow-on streaming benchmark task.

## Expected Outputs

* `research/research_internet.md`:
  * A comparison table (rows = candidate models, columns = the eight dimensions above).
  * A clear split: "native streaming decoders" vs "pseudo-streaming (batch re-inference)" models.
  * A ranked shortlist (top 3–5) by fit for low-latency brainpowa streaming, each with rationale and
    source URLs.
  * Explicit comparison against the current production configuration (parakeet-unified-en-0.6b,
    ~300ms buffer, t0017) and the entity-accuracy leader (Granite Speech 4.1 2B, batch-only so far).
  * A "recommended next experiment" note naming which 1–2 candidates merit a gold-92 streaming
    benchmark.
* `research/search_log.md` — every query and result count.

No model, dataset, or paper assets required (`expected_assets: {}`). No paid compute beyond LLM /
search usage; budget is low.

## Cross-References

* `t0005_stt_model_survey_brainpowa` — general survey this task narrows and deepens on the streaming
  axis only; do not re-litigate non-streaming accuracy findings.
* `t0012_whisper_parakeet_granite_streaming`, `t0014_granite_short_clip_robustness`,
  `t0015_streaming_buffer_interval`, `t0017_parakeet_biasing_buffer_replacement` — established the
  current streaming baselines (Parakeet unified/TDT, Granite) and the buffer-latency relationship
  this survey's candidates should be compared against.
* `t0003_literature_review_entity_stt` — contextual biasing technique survey; do not re-survey
  biasing methods in general, only their streaming-mode interaction.
* Integration target: `brainpowa-realtime-api` STT brick
  (`src/brainpowa_realtime_api/pipeline/stt/`), specifically `STTAdapter.transcribe_stream`.

Dependencies are intentionally empty: this is internet research independent of any other task's
concrete file output.
