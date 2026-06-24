# STT Model Survey: Open-Source Candidates for the brainpowa Pipeline

## Motivation

Rezolve's voice-commerce assistant runs on the `brainpowa-realtime-api`, an OpenAI-compatible
realtime server with a pluggable STT brick. Production today uses Whisper Turbo (via faster-whisper)
with runtime context injection; the pipeline also ships Azure Speech and NVIDIA Parakeet
(`parakeet-tdt-0.6b-v3` via NeMo, the current default, which unlocks GPU phrase-boosting /
contextual biasing) plus omni-LLM transcriber modes (Qwen3-Omni).

The gold-92 benchmark (`t0001_stt_benchmark`) confirmed that the dominant failure mode is **entity
accuracy** — brand names, product names, and SKUs are mangled or dropped, pushing the wrong-action
rate above the 2% target. `t0003_literature_review_entity_stt` surveyed *techniques* (contextual
biasing, shallow fusion, entity-aware ASR, LLM post-correction) and
`t0004_vocabulary_biasing_experiment` tested initial-prompt biasing on Whisper. Those tasks answered
"what methods help"; they did **not** answer "which concrete, integratable model should we run."

This task closes that gap: a structured survey of **open-source / open-weight STT models** that
could be dropped into the brainpowa STT brick as a candidate to improve entity accuracy over the
current production baseline. GPU-requiring models are explicitly in scope — self-hosting on GPU is
acceptable.

## Research Question

Which open-source / open-weight STT models (released or actively maintained, including recent
2025–2026 releases) are the best candidates to integrate as a brainpowa STT brick to improve
**entity accuracy** over the current production baseline under an **800 ms p50 voice-to-action**
latency budget — weighed on contextual-biasing support, streaming capability, GPU footprint,
license, and English / accented-English accuracy?

This is **not** a generic "best STT models" listicle. Every candidate must be assessed against our
concrete integration interface and product constraints below. A model that tops a WER leaderboard
but cannot do contextual biasing or stream is a weaker fit than a slightly-worse model that can.

## Constraints (the bar every candidate is measured against)

### Integration interface

The brainpowa STT brick is defined by the `STTAdapter` Protocol
(`src/brainpowa_realtime_api/pipeline/stt/base.py`):

* `async transcribe(pcm16_mono_bytes, *, options, session_id) -> TranscriptionResult(text, no_speech_prob, segment_count)`
  — mandatory.
* `async transcribe_stream(audio_queue) -> AsyncGenerator[(delta, result)]` — optional, for **true
  incremental** recognition. The default base implementation buffers the whole segment and calls
  `transcribe` once; only override-capable models give low-latency streaming UX.
* Input is **raw PCM-16 mono** at the configured sample rate. Must run as a self-hosted Python
  service brick (importable inference, not a closed cloud-only API).
* Existing providers for comparison: faster-whisper (`whisper turbo`), Azure Speech, and
  `nvidia/parakeet-tdt-0.6b-v3` via `nemo_toolkit[asr]`. Use these as the integration-effort and
  accuracy reference points.

### Product constraints

* Primary goal: improve entity accuracy (brands, products, SKUs) and intent preservation over the
  current production STT baseline.
* Latency: **< 800 ms p50** voice-to-action. STT is one stage of that budget, so per-segment STT
  latency / real-time-factor matters a lot.
* Language: **English, accented** (investor-relations domain in gold-92).
* Must support **contextual biasing / hotwords / initial_prompt** for domain vocabulary, and ideally
  streaming/incremental decoding for low latency.
* Open weights strongly preferred; permissive license (Apache-2.0 / MIT / CC-BY) is a plus, copyleft
  or non-commercial is a minus to flag.

## Scope

### Candidates to evaluate (not exhaustive)

* **NVIDIA Parakeet / Canary family** — Parakeet TDT/RNNT/CTC variants, Canary, FastConformer.
  Already partly integrated; establish the upgrade ceiling within this family.
* **Whisper variants** — large-v3, turbo, distil-whisper, whisper.cpp, WhisperX.
* **Moonshine** — fast English-focused streaming ASR.
* **Kyutai / Moshi STT** — streaming speech-to-text.
* **FunASR family** — Paraformer, SenseVoice.
* **Conformer / FastConformer** CTC/transducer baselines.
* **wav2vec2 / MMS**.
* **IBM Granite Speech**.
* **Microsoft Phi-4-multimodal** (audio).
* **Qwen-Omni / Qwen-Audio** (already referenced by the omni transcriber path).
* **Any newer 2025–2026 open ASR releases** surfaced during search.

### Per-candidate dimensions to record

For every shortlisted model, capture (mark "unknown / not reported" rather than guessing):

1. Model family, sizes available, parameter count.
2. License + weights availability (HF repo / GitHub), and any commercial-use restriction.
3. Streaming vs batch; native incremental decoding support (maps to `transcribe_stream`).
4. Contextual biasing / hotword / initial-prompt / phrase-boost support and the mechanism.
5. GPU / VRAM footprint and reported latency or real-time-factor (RTF) at a stated batch/segment
   size.
6. Reported WER (English + accented if available) and any **entity / keyword-recall** numbers.
7. Integration effort into the `STTAdapter` brick (existing Python inference path? NeMo / HF /
   ctranslate2? PCM-16 mono input handling?).
8. Fit verdict vs the current parakeet / whisper / Azure providers.

### Inclusions

* Open-source / open-weight models with self-hostable inference.
* GPU-requiring models (acceptable; record the footprint).
* English or multilingual-with-English-results models.

### Exclusions

* Closed cloud-only APIs with no downloadable weights (Azure, Google, AssemblyAI, etc.) — except as
  **named comparison baselines**, not candidates.
* Pure TTS / diarization / VAD-only systems.
* Models with no English results and no path to English use.

## Approach

Follow the `internet-research` task type guidelines.

### Search strategy

Define queries before searching; log every query + result count in `research/search_log.md`. Cover
at least these angles:

* Open ASR leaderboards — Hugging Face Open ASR Leaderboard, Papers-with-Code ASR/WER, Artificial
  Analysis speech-to-text.
* "contextual biasing" / "hotword" / "keyword boosting" + each model family.
* "streaming ASR" / "low latency" / "RTF" + each model family.
* 2025–2026 release announcements (NVIDIA, Kyutai, Useful Sensors/Moonshine, Alibaba FunASR, IBM,
  Microsoft, Qwen).
* GitHub repos + model cards for license, input format, and inference API.

**Sources**: official model cards / GitHub repos / docs (authoritative for license, API, footprint);
HF Open ASR Leaderboard (WER); arXiv (architecture + entity/biasing results); independent benchmarks
(cross-check, never sole source).

### Process

* Broad landscape pass first, then narrow per candidate.
* Record every URL immediately with date accessed, source org, and a one-line contribution note.
* Cross-reference accuracy/latency claims across ≥2 independent sources; flag single-source claims.
* Write `research/research_internet.md` incrementally, structured **by dimension/candidate**, not by
  search.

### Stopping criterion

Stop when the candidate set covers the families above plus any newer releases found, each scored on
all eight dimensions, and ≥3 candidates are ranked with enough evidence to justify a follow-on
benchmark task. Do not expand into technique re-surveys already covered by `t0003`.

## Expected Outputs

* `research/research_internet.md` — the survey, containing:
  * A **comparison table** (rows = candidate models, columns = the eight per-candidate dimensions).
  * A ranked **shortlist** (top 3–5) of candidates by fit to the brainpowa brick + entity-accuracy /
    latency goals, each with a one-paragraph rationale and source URLs.
  * An explicit comparison of the shortlist against the currently-integrated parakeet / whisper /
    Azure providers.
  * A short "recommended next experiment" note pointing at which 1–2 candidates merit a gold-92
    benchmark run.
* `research/search_log.md` — every query and result count.

No model assets, datasets, or paper assets are required (`expected_assets: {}`). No model training
or paid compute beyond LLM / search usage; budget is low.

## Cross-References

* `t0001_stt_benchmark` — gold-92 held-out regression set; defines the entity-accuracy metric the
  candidates must eventually beat. **Never tune on gold-92.**
* `t0003_literature_review_entity_stt` — technique survey; this task supplies the concrete models
  that implement those techniques. Do not re-survey techniques.
* `t0004_vocabulary_biasing_experiment` — established initial-prompt biasing baseline on Whisper;
  informs the contextual-biasing dimension.
* Integration target: `brainpowa-realtime-api` STT brick
  (`src/brainpowa_realtime_api/pipeline/stt/`).

Dependencies are intentionally empty: this is internet research that can start without any other
task's concrete file output. The prior tasks above are motivation and context, not blocking inputs.
