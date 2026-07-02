# Streaming STT Model Survey — Native Incremental Decoding Architectures

**Question:** Which open-source / open-weight STT models support true incremental (streaming)
decoding, and how do their streaming architectures compare on chunk/frame granularity, latency/RTF,
and integration effort into brainpowa's `STTAdapter.transcribe_stream`?

**Recency window applied:** 2026-01-02 through 2026-07-02 (today). Older established families
(Parakeet-TDT, Moonshine, Whisper, FunASR/Paraformer, Granite) are documented for comparison but the
search effort was weighted toward what shipped in this window.

## Executive Summary

* **Two genuinely new true-streaming candidates surfaced in the recency window**:
  `nvidia/nemotron-3.5-asr-streaming-0.6b` (2026-06-04, cache-aware FastConformer, 40
  language-locales) and **T-one** (t-tech/T-Bank, 71M params, Apache 2.0, Conformer+CTC with
  explicit `state`-threading streaming API).
* **Current production model (`parakeet-unified-en-0.6b`, t0017 winner) IS true streaming** —
  cache-aware FastConformer/RNNT, same lineage as Nemotron. Its predecessor `parakeet-tdt-0.6b-v3`
  is confirmed **pseudo-streaming** (chunked batch re-inference), with an independently measured 46%
  relative WER degradation when forced into chunks (6.32%→9.22%, arXiv:2604.14493).
* **Granite Speech 4.1 2B (the project's entity-accuracy leader, 97.1% EA-DV) has NO true streaming
  mode.** Its 97% accuracy comes from prompt-based keyword biasing on a batch-only Conformer+LLM
  decoder — this is the single most important finding for the project's roadmap: the accuracy-leader
  and the streaming-leader are currently different models.
* **Kyutai STT is the architecturally purest true-streaming candidate** (codec-based full-duplex,
  decoder-only Transformer, native async-generator-shaped API) but has no contextual biasing
  mechanism at all.
* Most "streaming" wrappers around Whisper (WhisperLive, RealtimeSTT, whisper.cpp stream, speaches)
  are **pseudo-streaming** — repeated full batch re-inference on a growing/sliding buffer. Two
  Whisper-family exceptions do genuine incremental work: `whisper_streaming`'s LocalAgreement
  prefix-commitment policy, and `simul_whisper`'s KV-cache-reuse + attention-guided truncation
  detection.
* wav2vec2/MMS have **no maintained streaming implementation** — pseudo-streaming via VAD-chunking
  only, confirmed by HuggingFace's own "asr-chunking" blog framing it as an approximation.
* Google USM/Chirp are **closed, API-only** — excluded from the candidate table, listed as a
  comparison baseline only.

* * *

## Native Streaming Decoders

Models where the decoder architecture itself emits partial hypotheses incrementally via cache/state
carried across chunk boundaries — not re-running batch inference on a growing buffer.

### `parakeet-unified-en-0.6b` (NVIDIA)

* **Family/license/weights**: NeMo/Parakeet, 0.6B params, NVIDIA Open Model License.
  [huggingface.co/nvidia/parakeet-unified-en-0.6b](https://huggingface.co/nvidia/parakeet-unified-en-0.6b),
  released 2026-04-07. This is the current production winner within Parakeet per
  `t0017_parakeet_biasing_buffer_replacement` (WER 11.0%, EA-DV 34.8%, 0 empty transcripts).
* **Streaming mechanism**: FastConformer encoder (24 layers) + RNNT decoder using chunked
  self-attention masks (left/middle-chunk/right context) plus Dynamic Chunked Convolutions inside
  each layer. All parameters shared between offline and streaming modes — one unified checkpoint.
* **True vs pseudo verdict**: **TRUE STREAMING.** Model card documents `att_context_size` configs
  with explicit left/chunk/right context (e.g. left=5.6s cached history, chunk=0.08s, right=0.08s →
  0.16s latency) — a stateful cache-based encoder. A
  [sherpa-onnx feature request (#3573)](https://github.com/k2-fsa/sherpa-onnx/issues/3573)
  explicitly contrasts this model's chunked RNNT decoding against the fallback workaround of
  "repeatedly decode a growing buffer," confirming the architecture is designed for stateful
  incremental decoding.
* **Chunk/frame size**: Configurable; documented latencies 160ms (min), 240ms, 320ms, 560ms, 1.12s,
  2.08s, with fixed 5.6s left context cache in all configs.
* **Latency/RTF**: Only chunk-latency table above published; no RTF figure found; no independent
  second source located — **single-source, unverified**.
* **Contextual biasing in streaming**: No hotword/TurboBias mention on this specific model card.
* **Integration effort**: Moderate. NeMo exposes `speech_to_text_cache_aware_streaming_infer.py` and
  a `CacheAwareStreamingAudioBuffer` utility
  ([NeMo GitHub](https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/asr/asr_cache_aware_streaming/speech_to_text_cache_aware_streaming_infer.py))
  — a CLI/simulation script, not a native async generator. Building `async def transcribe_stream`
  requires wrapping the buffer/cache-step API yourself.
* **Fit verdict**: This IS the current production baseline (t0017, ~300ms buffer per the corrected
  recommendation). Any new candidate must beat it on WER/EA-DV, latency, or integration effort to be
  worth switching to.

### `nemotron-3.5-asr-streaming-0.6b` / `nemotron-speech-streaming-en-0.6b` (NVIDIA) — NEW, 2026-06-04

* **Family/license/weights**: NVIDIA Nemotron, successor line to Parakeet streaming. Two
  checkpoints: `nvidia/nemotron-speech-streaming-en-0.6b` (English-only, updated 2026-03-12/13,
  NVIDIA Open Model License) and `nvidia/nemotron-3.5-asr-streaming-0.6b` (multilingual, 40
  language-locales, released 2026-06-04, **OpenMDW-1.1** license — note the license differs between
  the two checkpoints). 600M params.
  [huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b),
  [huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b).
  Coverage:
  [MarkTechPost, 2026-06-06](https://www.marktechpost.com/2026/06/06/nvidia-releases-nemotron-3-5-asr-a-600m-parameter-cache-aware-streaming-model-transcribing-40-language-locales-in-real-time/).
* **Streaming mechanism**: Cache-Aware FastConformer-RNNT, 24 encoder layers, with language-ID
  prompt conditioning in the multilingual variant. Explicitly "stores encoded internal states from
  previously processed audio chunks" and reuses them.
* **True vs pseudo verdict**: **TRUE STREAMING.** Same cache-based lineage as the foundational
  "Stateful Conformer with Cache-based Inference for Streaming ASR" paper (arXiv:2312.17279, ICASSP
  2024). Independently corroborated by arXiv:2604.14493 (April 2026, "Pushing the Limits of
  On-Device Streaming ASR"), which explicitly labels this mechanism cache-based — in direct contrast
  to its finding that Parakeet TDT-0.6b-v3 is pseudo-streaming (see below).
* **Chunk/frame size**: Configurable via `att_context_size` in 80ms units, no retraining needed:
  80ms `[56,0]`, 160ms `[56,1]`, 320ms `[56,3]`, 560ms `[56,6]`, 1120ms `[56,13]`. Left context
  fixed at 56 frames (~4.48s cached history).
* **Latency/RTF**: NVIDIA claims 17x more concurrent streams than buffered approaches on the same
  H100 (240 vs 14 at 80ms chunk; 2,400 vs ~400 at 1120ms chunk) — vendor-originated claim (same
  underlying source cited by two URLs). **Independently corroborated by two separate third
  parties**: (1)
  [Artificial Analysis](https://artificialanalysis.ai/speech-to-text/models/nvidia-nemotron-asr-streaming)
  ranks it 2nd in latency among all streaming ASR models, citing 0.07s time-to-final-transcript
  after end of speech; (2) arXiv:2604.14493 independently benchmarked an int4-quantized variant on
  **AMD EPYC 7V12 CPU (no GPU)**: RTFx >6x real-time, 0.56s algorithmic latency, 8.20% average
  streaming WER across 8 benchmarks — different hardware, different lab, genuinely independent.
* **Contextual biasing in streaming**: No TurboBias/hotword mention on the model card itself. The
  TurboBias paper (arXiv:2508.07014) states GPU-PB "allows boosting phrases in streaming decoding"
  via greedy decoding in principle, but the paper's own evaluation is offline/pre-segmented audio
  only — **biasing-in-cache-aware-streaming interaction is architecturally plausible but not
  empirically documented**.
* **Integration effort**: Same NeMo CLI/buffer-utility situation as parakeet-unified. A
  Transformers-library path with `TextIteratorStreamer` support also exists, which is thread-based
  and more naturally wrapped into a Python async generator — likely the lower-effort integration
  path of the streaming Parakeet/Nemotron family.
* **Fit verdict**: **Highest-priority candidate for a follow-on benchmark.** Same architecture
  family and integration profile as the current production model, but purpose-built for streaming
  (vs. parakeet-unified's shared offline/streaming checkpoint) with independently-corroborated
  best-in-class streaming latency and native multilingual coverage. Should be benchmarked head-to-
  head against parakeet-unified-en-0.6b on gold-92 with GPU-PB biasing.

### `multitalker-parakeet-streaming-0.6b-v1` (NVIDIA) — already used in t0015

* **Family/license**: Parakeet-based, 600M params, NVIDIA Open Model License.
  [huggingface.co/nvidia/multitalker-parakeet-streaming-0.6b-v1](https://huggingface.co/nvidia/multitalker-parakeet-streaming-0.6b-v1).
* **Streaming mechanism**: FastConformer encoder (NEST-based) with learnable speaker kernels
  injected into the pre-encode layer, driven by external speaker-diarization output. One model
  instance per speaker.
* **True vs pseudo verdict**: **TRUE STREAMING** — cache-aware, same lineage as
  parakeet-unified/Nemotron. Uses `CacheAwareStreamingAudioBuffer` in its own example script.
* **Chunk/frame size**: `att_context_size` in 80ms frames: [70,0]=80ms, [70,1]=160ms, [70,6]=560ms,
  [70,13]=1.12s (primary benchmark config).
* **Latency/RTF**: Not reported; only cpWER accuracy given (AMI IHM 21.26%, AMI SDM 37.44%, CH109
  15.81%, Mixer6 23.81% at 1.12s chunk). No RTF found, cannot cross-check.
* **Contextual biasing**: Not supported — relies solely on diarization output.
* **Integration effort**: High — requires pairing with a separate streaming diarization model
  (Sortformer), one model instance per active speaker.
* **Fit verdict**: Niche — only relevant if brainpowa needs multi-speaker overlap handling, which is
  not a stated requirement. Already benchmarked in t0015; not a priority for further work.

### Kyutai STT (`stt-1b-en_fr`, `stt-2.6b-en`) — Delayed Streams Modeling

* **Family/license/weights**: Two checkpoints: `kyutai/stt-1b-en_fr` (~1B params, English+French,
  built-in semantic VAD) and `kyutai/stt-2.6b-en` (~2.6B params, English-only, accuracy-optimized).
  Code MIT/Apache dual; **model weights CC-BY-4.0** (confirmed on the
  [stt-2.6b-en model card](https://huggingface.co/kyutai/stt-2.6b-en)).
  [github.com/kyutai-labs/delayed-streams-modeling](https://github.com/kyutai-labs/delayed-streams-modeling).
* **Streaming mechanism**: The architecturally most distinct candidate in this survey — full-duplex,
  codec-based. Audio is encoded by the Mimi neural codec (12.5Hz, 1.1kbps) into discrete tokens; a
  decoder-only Transformer consumes the Mimi-tokenized stream and emits a time-aligned text token
  stream with a fixed delay offset ("Delayed Streams Modeling") — not derived from Conformer/RNNT
  lineage at all.
* **True vs pseudo verdict**: **TRUE STREAMING**, arguably the purest in the field. The model has
  explicit `reset_streaming()` state on both the Mimi codec and the LM
  (`self.mimi.reset_streaming()`, `self.lm_gen.reset_streaming()`), consuming raw PCM frame-by-
  frame with the text stream genuinely offset in time (0.5s for stt-1b, 2.5s for stt-2.6b) rather
  than being re-run over a growing buffer. Confirmed by
  [Modal's implementation](https://modal.com/docs/examples/streaming_kyutai_stt), which shows a
  native `async def transcribe(self, pcm, all_pcm_data)` generator yielding partial text
  incrementally.
* **Chunk/frame size**: 80ms audio frames at 12.5Hz (Mimi codec native rate, fixed by the codec —
  not user-configurable the way NeMo chunk sizes are). What's configurable instead is the text/audio
  delay offset (0.5s vs 2.5s, baked into the two checkpoints).
* **Latency/RTF**: RTFx 88.37 on the stt-2.6b-en model card (hardware unstated on that specific
  card). Kyutai's own Rust production server reports 64 simultaneous WebSocket connections at RTF 3x
  on one L40S GPU, and H100 handling 400 concurrent streams — vendor-internal cross-check only
  (different metric/hardware/doc, but same vendor), not third-party verified.
* **Contextual biasing**: **Not supported / not reported.** No hotword or contextual-biasing
  mechanism; the only "context" feature is stt-1b-en_fr's semantic VAD (end-of-turn prediction, not
  biasing).
* **Integration effort**: **Low — the best architectural fit for the target interface.** The
  framework already exposes an async-generator pattern natively, and the underlying Rust server
  speaks WebSocket streaming with partial-transcript push semantics.
* **Fit verdict**: Cleanest streaming architecture and integration path of any candidate surveyed,
  but the complete absence of contextual biasing is disqualifying on its own for this project's
  stated goal (entity accuracy on Rezolve domain vocabulary) unless paired with an external
  post-correction layer. Worth a benchmark run specifically to quantify the biasing gap, not as a
  drop-in production replacement.

### Kyutai Moshi (full-duplex speech-to-speech, ASR sub-component)

* **Family/license**: Kyutai Moshi, full-duplex dialogue model; STT is a component, distinct from
  the dedicated Kyutai STT checkpoints above. MIT/Apache dual license, weights CC-BY-4.0.
  [github.com/kyutai-labs/moshi](https://github.com/kyutai-labs/moshi).
* **Streaming mechanism**: Same Mimi codec (80ms frame, 12.5Hz) feeding a joint speech-text
  Transformer modeling both user and system audio streams simultaneously (true full-duplex, not just
  one-directional streaming).
* **True vs pseudo verdict**: **TRUE STREAMING / full-duplex.** Theoretical latency 160ms (80ms Mimi
  frame + 80ms acoustic delay), per the original paper
  ([kyutai.org/Moshi.pdf](https://kyutai.org/Moshi.pdf), arXiv:2410.00037).
* **Chunk/frame size**: 80ms (Mimi codec native), same as Kyutai STT.
* **Latency/RTF**: Theoretical 160ms; practical ~200ms end-to-end on L4 GPU per Kyutai's own
  paper/repo, repeated by secondary sources without independent measurement. **One partially
  independent contradiction**: a
  [GitHub issue (#229, "High latency on a L4 GPU")](https://github.com/kyutai-labs/moshi/issues/229)
  reports a user observing latency substantially higher than the claimed 200ms in practice.
* **Contextual biasing**: Not applicable — conversational agent model, not a transcription product.
* **Integration effort**: Wrong shape for a pure `transcribe_stream` use case — full-duplex dialogue
  model, not transcription-only. If forced into ASR-only use, same async-friendly Mimi primitives
  apply as Kyutai STT, but the dual-stream design isn't its intended mode.
* **Fit verdict**: Not recommended as a candidate — use dedicated Kyutai STT instead.

### T-one (t-tech / T-Bank) — NEW, recency-sweep find

* **Family/license/weights**: T-one, by T-Software DC (T-Bank, Russia). 71M (71.7M) params. Apache
  2.0. [huggingface.co/t-tech/T-one](https://huggingface.co/t-tech/T-one),
  [github.com/voicekit-team/T-one](https://github.com/voicekit-team/T-one).
* **Streaming mechanism**: Conformer encoder + CTC output (not RNNT/attention-decoder) with
  SwiGLU/RMSNorm/RoPE, U-Net-style downsample/upsample blocks, streaming state confined to the final
  two layers, paired with a phrase-boundary detector and CTC greedy/KenLM beam-search decoder.
* **True vs pseudo verdict**: **TRUE STREAMING.** Published API explicitly threads state across
  chunks: `new_phrases, state = pipeline.forward(audio_chunk, state)`
  ([HF model card](https://huggingface.co/t-tech/T-one)) — genuine incremental hidden-state
  carryover, explicitly contrasted against Qwen3-ASR's chunk-from-scratch approach (see below) in
  arXiv:2601.21337.
* **Chunk/frame size**: Fixed 300ms audio chunks (HF card, GitHub,
  [BrightCoding blog](https://www.blog.brightcoding.dev/2026/06/01/t-one-the-high-performance-russian-asr-pipeline-developers-love)).
  Look-ahead/right-context not documented.
* **Latency/RTF**: 600-800ms end-to-end phrase latency (300ms buffering + 50ms inference + 250-
  450ms boundary detection), ~350ms for single-word commands — **single-source, unverified**
  (developer blog only). Throughput figures (5,952-57,344 RPS T4→H100) come from HF/GitHub but don't
  corroborate the latency number specifically.
* **Contextual biasing**: Not documented. CTC+KenLM decoding architecture means hotword biasing
  would require external lexicon/lattice rescoring — not natively supported.
* **Integration effort**: Moderate-low. Existing sync `forward(chunk, state) -> (phrases, state)`
  maps directly onto the target async interface via `asyncio.to_thread` (no native async support); a
  `finalize(state)` call flushes trailing phrases on stream close.
* **Fit verdict**: Interesting architecture (true incremental CTC streaming, small 71M footprint)
  but Russian-language/telephony-specialized with no biasing mechanism and an unverified single-
  source latency claim — low priority for this project's English/investor-relations domain unless a
  lightweight-CTC-streaming architecture pattern itself is of interest.

### Paraformer-Streaming (`funasr/paraformer-zh-streaming`, Alibaba DAMO)

* **Family/license/weights**: Alibaba DAMO/FunASR, `paraformer-zh-streaming`, 220M params (bilingual
  Chinese/English). Apache 2.0.
  [huggingface.co/funasr/paraformer-zh-streaming](https://huggingface.co/funasr/paraformer-zh-streaming),
  [github.com/modelscope/FunASR](https://github.com/modelscope/FunASR). Architecturally distinct
  from the batch `funasr/paraformer-zh` checkpoint eliminated in `t0010` (WER 122.7%) — that result
  does not apply here.
* **Streaming mechanism**: **SCAMA** (Streaming Chunk-Aware Multihead Attention) + LC-SAN-M
  (latency-controlled memory self-attention), from
  [Zhang et al. 2020, arXiv:2006.01712](https://arxiv.org/abs/2006.01712). LC-SAN-M restricts
  self-attention to chunk-level input; a jointly-trained predictor (SCAMA) controls how much encoder
  output is released to the decoder per chunk.
* **True vs pseudo verdict**: **TRUE STREAMING.** The model maintains an explicit cache across chunk
  calls (`cache={}` persists encoder/decoder state between `model.generate()` calls per the FunASR
  streaming quick-start) and only ingests new `chunk_stride` samples per call — genuine online
  decoding with carried state, not re-running the whole buffer each time.
* **Chunk/frame size**: Configurable via `chunk_size=[0, 10, 5]` = [lookback, chunk, lookahead] in
  60ms-frame units → 600ms processing chunk with 300ms look-ahead. Additional
  `encoder_chunk_look_back=4` and `decoder_chunk_look_back=1` (chunks) control reused prior context.
* **Latency/RTF**: **Not reported** for this specific checkpoint — the chunk config implies a lower
  bound of ~600-900ms algorithmic latency, but this is inferred, not measured/published. FunASR's
  oft-cited "170x realtime" applies to SenseVoice/offline models, not this checkpoint.
* **Contextual biasing in streaming**: FunASR has hotword support elsewhere (SeaCo-Paraformer,
  Fun-ASR-Nano), but this specific streaming checkpoint's model card does not document hotword
  support — **unknown / not reported** for this variant specifically.
* **Integration effort**: FunASR already exposes a chunked Python `generate()` call with explicit
  cache dict, mapping naturally onto an async wrapper — pull PCM16 chunks off a queue, accumulate to
  chunk_stride boundary, call with cache, yield delta text. FunASR also ships a full WebSocket
  server. Estimated: low effort (~1 day) to wrap the library call.
* **Fit verdict**: Solid true-streaming candidate but no confirmed streaming-mode latency number and
  unclear hotword support in this specific variant — would need a validation pass before committing
  to a full benchmark.

### U2 / U2++ Streaming Conformer (WeNet)

* **Family/license/weights**: WeNet toolkit (Mobvoi/NPU origin, community-maintained, wenet-e2e).
  Papers: U2
  ([Yao et al. 2021](https://www.isca-archive.org/interspeech_2021/yao21_interspeech.pdf)), U2++
  ([Wu et al. 2021, arXiv:2106.05642](https://arxiv.org/pdf/2106.05642)). Apache 2.0. No single
  fixed param count — per-recipe (typical Conformer recipes ~30-120M).
  [github.com/wenet-e2e/wenet](https://github.com/wenet-e2e/wenet) (per-recipe checkpoints, not one
  canonical HF repo).
* **Streaming mechanism**: **Dynamic chunk training** for a unified streaming/non-streaming
  Conformer with joint CTC/attention. Two-pass decoding: Pass 1 = streaming CTC (frame- synchronous,
  fast partial/n-best hypotheses); Pass 2 = attention decoder(s) rescore the n-best list. U2++ adds
  a right-to-left decoder alongside left-to-right, combined at rescoring:
  `Score = λ·CTC + (1-α)·L2R + α·R2L`.
* **True vs pseudo verdict**: **HYBRID.** Genuinely incremental for the CTC first pass (frame-
  synchronous partial output as chunks arrive) but the attention-rescoring second pass is NOT
  streaming — it needs the (near-)complete utterance to run bidirectional rescoring, adding a small
  utterance-final delay. True streaming for the fast/partial path, pseudo-streaming (buffered) for
  the corrected final output.
* **Chunk/frame size**: Dynamic chunk training randomizes chunk size during training; the paper's
  representative streaming benchmark uses chunk=16 frames (~640ms at typical 40ms/frame
  downsampling).
* **Latency/RTF**: Paper reports average latency ~320ms (range 0-640ms) for chunk=16 on AISHELL-1/2
  — algorithmic/theoretical latency, not measured wall-clock, hardware unstated. WeNet's own GPU
  runtime README separately reports RTF 0.0009-0.0011 on a T4 GPU (FP16, ONNX) for offline/batched
  serving — measures a different thing (throughput RTF under load, not per- utterance streaming
  latency), so this corroborates "fast" generally but is **not a true apples- to-apples second
  source** for the 320ms figure. Treat the 320ms number as single-source, unverified.
* **Contextual biasing**: Not reported in core U2/U2++ papers or WeNet docs — would need a custom
  TLG/WFST-based biasing module, a research add-on not shipped by default.
* **Integration effort**: Moderate. WeNet is streaming-first by design (unlike Paraformer, which had
  streaming bolted onto a fundamentally non-autoregressive architecture), so wrapping the chunked
  encoder + CTC prefix search into an async generator is architecturally natural, but WeNet's Python
  API is less polished than FunASR's `AutoModel` — more manual state management.
* **Fit verdict**: Architecturally interesting hybrid, but weaker evidence base (single-source
  latency, no biasing) than the NVIDIA cache-aware family or Kyutai. Lower priority.

### Fun-ASR-Nano-2512 (Alibaba/FunAudioLLM) — NEW, Dec 2025 / active through June 2026

* **Family/license/weights**: FunAudioLLM/Fun-ASR, successor line to Paraformer within Alibaba.
  `Fun-ASR-Nano` = 800M params; full `Fun-ASR` = 7.7B (LLM-ASR architecture). Apache 2.0.
  [huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512),
  [github.com/FunAudioLLM/Fun-ASR](https://github.com/FunAudioLLM/Fun-ASR). Released 2025-12-15;
  FunASR framework v1.3.12 shipped 2026-06-21 — actively updated inside the recency window.
* **Streaming mechanism**: LLM-based ASR (speech encoder + LLM decoder) with a "decoupled streaming
  inference strategy" — the acoustic encoder has native streaming/causal capability, decoupled from
  LLM decoding via an "incremental context extension mechanism" for KV-cache reuse. Source:
  [Fun-ASR Technical Report, arXiv:2509.12508](https://arxiv.org/html/2509.12508v4).
* **True vs pseudo verdict**: **Likely true streaming, weaker verification than U2++.** Authors
  describe training with "streaming-style training data that explicitly emulate the streaming
  decoding process" plus the decoupled-encoder/KV-cache-reuse design — consistent with genuine
  incremental decoding, but the retrieved technical report did not expose architecture
  diagrams/pseudocode to independently verify token-by-token incrementality the way U2++'s paper
  does. Self-reported description only.
* **Chunk/frame size**: **Not reported** in accessible sections of the report or model card.
* **Latency/RTF**: The report's Table 3 gives streaming-mode WER (In-house 7.00%, Fairfield 5.33%,
  English General 14.74%) but **no first-token latency or streaming RTF number** was found. The
  "340x realtime" / "26x faster than Whisper-large-v3" figures apply to offline/batched vLLM-
  accelerated inference, not streaming — do not conflate.
* **Contextual biasing in streaming**: **Yes, explicitly confirmed** — a "RAG-based mechanism for
  hotword customization" with the technical report's Table 6 reporting hotword accuracy/recall
  broken out separately for offline vs. streaming evaluation, confirming streaming-mode support.
* **Integration effort**: Ships inside the same FunASR framework/AutoModel API and websocket runtime
  as Paraformer-streaming, plus a dedicated vLLM serving path — similarly low effort assuming
  streaming hooks are exposed the same way. Not independently verified against actual code.
* **Fit verdict**: The only candidate besides Nemotron 3.5 with both confirmed streaming-mode
  hotword biasing AND a plausible true-streaming architecture. Worth a validation-scale benchmark to
  confirm the true-streaming claim and measure actual latency, given the strength of the biasing
  signal.

* * *

## Pseudo-Streaming (Batch Re-Inference)

Models where "streaming support" means re-running (or nearly re-running) full batch inference on a
growing or sliding buffer, not incremental decoder-state carryover.

### `parakeet-tdt-0.6b-v3` (NVIDIA) — current-until-t0017 production model

* Not natively cache-aware. NeMo's streaming script offers configurable chunking but this is chunked
  inference on an offline-trained model. **Independently confirmed pseudo-streaming**:
  arXiv:2604.14493 tested it via chunking and found the best chunked config reached 9.22% WER — a
  46% relative degradation from its 6.32% batch WER. A
  [HF discussion thread (#11)](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/discussions/11)
  shows the community asking NVIDIA to confirm cache-awareness, unanswered.
* **Fit note**: this is the exact accuracy tax `t0017` avoided by moving to `parakeet-unified` and
  its ~300ms buffer, rather than chunking the TDT checkpoint further.

### IBM Granite Speech (4.1-2B / 4.1-2B-Plus / 3.3 family) — project's entity-accuracy leader

* **Family/license/weights**: `granite-speech-3.3-8b/2b`, `granite-4.0-1b-speech`,
  `granite-speech-4.1-2b/2b-plus/2b-nar`. Apache 2.0. HF org `ibm-granite`, e.g.
  [huggingface.co/ibm-granite/granite-speech-4.1-2b-plus](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus).
  Paper: [arXiv 2505.08699](https://arxiv.org/html/2505.08699v2). Native `transformers` support.
* **Streaming mechanism**: Conformer encoder with 4-second block-local attention + CTC (dual-head)
  feeding a 2-layer windowed Q-Former adapter (15-frame blocks, 3 queries/block, 10x downsample to
  10Hz) into a Granite LLM decoder doing full-sequence autoregressive generation via `.generate()`.
  The NAR variant uses a bidirectional (non-causal) LLM editor over a full CTC draft — even less
  streamable.
* **True vs pseudo verdict**: **NO TRUE STREAMING MODE.** The encoder's 4s block-local attention is
  architecturally streaming-friendly, but the LLM decoder consumes the whole projected embedding
  sequence at once. What IBM calls "incremental decoding" (4.1-2B-Plus only) is a `prefix_text`
  mechanism for stitching batch decodes of pre-segmented long files (up to 9 min) — not live/
  frame-level streaming. No partial-hypothesis emission, no persistent cross-buffer encoder state,
  no documented streaming API anywhere.
* **Chunk/frame size**: Encoder block-attention window = 4 seconds. Adapter window = 15 frames →
  10Hz LLM input rate. No fixed chunk/overlap spec for the pseudo-streaming `prefix_text` mode.
* **Latency/RTF**: Batch-mode only. `granite-speech-4.1-2b`: RTF ≈ 231x (HF card).
  `granite-speech-4.1-2b-nar`: RTF ≈ 1820x on H100 (press-relayed, not independently measured). No
  streaming-mode latency/TTFW numbers exist anywhere.
* **Contextual biasing**: Confirmed — Keyword List Biasing (KWB) via a `Keywords: ...` prompt
  clause, present in 4.1-2b and 4.1-2b-plus. This is very likely the source of the project's
  measured 97.1% EA-DV in `t0007`/`t0012`/`t0014`/`t0015`. Because biasing lives in the text prompt,
  it would *plausibly* survive a hand-built chunked pseudo-streaming wrapper — inference, not a
  tested claim.
* **Integration effort**: **Substantial custom engineering, not a thin wrapper.** Would require:
  chunk buffering (undocumented, untuned window size, likely 3-9s), an overlap/stitching strategy
  reusing the unresolved `prefix_text` mechanism, manual delta-diff (model returns full strings, not
  partial hypotheses, per chunk), and async plumbing around blocking `model.generate()` calls
  needing fully materialized audio arrays. Estimated multi-day to 1-2 week effort, with no guarantee
  the 97.1% entity accuracy survives chunking (entities spanning chunk boundaries, keyword-biasing
  prompt scope changes).
* **Fit note**: **This is the single most important finding of the survey.** The project's
  accuracy-leader (Granite) and its streaming-leader candidates (Nemotron 3.5, parakeet-unified,
  Fun-ASR-Nano) are architecturally disjoint — Granite's biasing lives in an LLM prompt that
  requires whole-utterance context, while the true-streaming candidates use cache-aware
  Conformer/RNNT or codec-based decoders without that mechanism (or with weaker biasing). Closing
  this gap (streaming + Granite-level entity accuracy) is not solved by any single candidate found
  in this survey — it would require either a Granite chunking experiment (high engineering risk) or
  a hybrid architecture not yet released.

### Moonshine (Useful Sensors) v2 — architecture note (accuracy already eliminated in `t0008`)

* **Family/license/weights**: Useful Sensors, `moonshine-streaming-tiny/small/medium`. Paper v2:
  [arXiv:2602.12241](https://arxiv.org/html/2602.12241v1). Python package `moonshine-voice`
  ([github.com/moonshine-ai/moonshine](https://github.com/moonshine-ai/moonshine)).
* **Streaming mechanism**: 50Hz frame rate (20ms/frame). Sliding window: 16 frames left context, 4
  frames right context (lookahead layers) → 80ms algorithmic lookahead for middle (strictly causal)
  layers; a more conservative bound for fully-finalized representations is 320ms (16 frames).
* **True vs pseudo verdict**: **Architecture is true-streaming-capable by design** (unlike original
  Moonshine v1, which was pseudo-streaming via padding-free batch re-inference) **but the widely-
  used HF/Transformers reference integration is not yet a fully efficient streaming implementation**
  — the actual incremental-cache streaming lives in the separate `moonshine-voice` C++/ONNX-adjacent
  library, not the HF path. Net: real streaming exists, but only via one specific production
  library, not the "easy" HF path.
* **Latency**: Primary source (arXiv:2602.12241, Apple M3): Tiny 50ms/5.91% compute load, Small
  148ms/17.97%, Medium 258ms/28.95%. A commonly-cited "107ms on MacBook Pro" figure traces back to
  the original 2024 v1 marketing claim (different hardware generation, different architecture) —
  **not independent corroboration of the v2 numbers**. Treat as single-source, unverified.
* **Contextual biasing**: **Not supported.** No `bias_terms`/`hotword`/`initial_prompt` in the HF
  API, `moonshine-voice`, or the paper. Only customization path is commercial full-model
  fine-tuning.
* **Integration effort**: Moderate — `moonshine-voice` provides `Transcriber`/`Stream`/
  `MicTranscriber` classes with incremental encoder-state caching already implemented, but exposed
  via a callback/event-listener pattern (`on_line_text_changed`, etc.), not an async generator.
  Wrapping the callback in an `asyncio.Queue` is light glue (~1 day) — no chunking logic needs
  writing from scratch.
* **Fit note**: `t0008` already eliminated Moonshine on accuracy (21.7% EA); this survey's finding
  is that even its streaming architecture, while real, has no biasing mechanism — doubly
  disqualifying for this project regardless of the streaming question.

### Whisper streaming wrappers (whisper_streaming, WhisperLive, simul_whisper, speaches, RealtimeSTT, whisper.cpp stream)

Whisper itself has no native streaming decoder — every wrapper works around this. Verdicts vary per
wrapper:

* **`whisper_streaming`** (ufal, MIT,
  [github.com/ufal/whisper_streaming](https://github.com/ufal/whisper_streaming)): LocalAgreement-n
  policy — repeatedly re-decode a rolling buffer, commit only the longest common prefix agreed
  across n consecutive updates ([arXiv:2307.14743](https://arxiv.org/abs/2307.14743)). **Verdict:
  pseudo-streaming at the model level (full batch re-decode each step), with a genuine incremental-
  commitment algorithm at the hypothesis level** — the most sophisticated of the "wrapper" category.
  Min chunk ~1s, LocalAgreement-2 default. Paper-reported latency ~3.3s (non-VAC), sub-1s with VAC
  variant — single-source, unverified. Exposes `initial_prompt`, carried forward via the growing
  confirmed transcript. Integration: low-moderate — ships a reference socket server
  (`whisper_online_server.py`) with a good template for an async generator.
* **WhisperLive** (collabora, MIT): VAD-gated buffer, full re-inference per cycle. **Pseudo-
  streaming**, no LocalAgreement-style voting. No rigorous latency numbers. `initial_prompt`
  supported by backends but not threaded through the mainline protocol. Integration: **low** — best
  starting point of the wrapper category, already ships a working async-friendly WebSocket server
  with incremental partial-update semantics.
* **simul_whisper** (backspacetg, attention-guided truncation detection): Fixed small chunks (~1s);
  decoder inspects cross-attention weights to detect boundary-truncated tokens, holds them back,
  reuses KV-cache across chunks rather than fully re-encoding. **Closer to true incremental
  streaming than the other wrappers** — KV-cache reuse + token-level commit/hold decision. No
  independent latency reproduction found (paper's own curves only). No documented biasing.
  Integration: **high** — research codebase, no production async example.
* **speaches** (formerly faster-whisper-server, MIT): OpenAI-Realtime-API-compatible WebSocket using
  Silero VAD; fires one full independent transcription call per finalized utterance — no
  partial/interim transcript mid-utterance. **Pseudo-streaming.** No latency numbers published.
  Batch endpoint exposes `prompt`/`hotwords`; the realtime path does not.
* **RealtimeSTT** (KoljaB, MIT, 9,943 stars): Background worker snapshots the entire accumulated
  buffer every 0.2s and re-runs full inference — confirmed from source (`core/realtime.py`).
  **Unambiguous pseudo-streaming.** `RealtimeTextStabilizer` smooths jittery re-transcriptions.
  Exposes separate `initial_prompt`/`initial_prompt_realtime` (re-applied identically each tick, not
  accumulated, since each tick is stateless). Integration: low-moderate — ships a FastAPI example
  server with interim/final event types close to the target shape.
* **whisper.cpp stream example** (ggerganov, MIT): Fixed-length sliding window, full
  `whisper_full()` re-invocation each step with periodic context reset. **Pseudo-streaming.**
  Default 3s step / 10s window. No rigorous latency table from maintainers. Integration: high for a
  Python target — C++ library needing async-executor bridging.
* **No genuinely new Whisper-streaming algorithm was found in the 2026-01 to 2026-07 recency
  window** — only continued maintenance on existing projects (speaches last pushed 2026-07-02,
  RealtimeSTT 2026-06-12).

### wav2vec2 / MMS — no maintained streaming implementation

* `facebook/wav2vec2-*` (base 95M/large 317M) and `facebook/mms-1b-all` (1B params) are CTC-based
  full-utterance encoders with no dedicated streaming mode, causal-attention variant, or chunked
  training recipe shipped by Meta or HF.
* **Verdict: pseudo-streaming only, via community workarounds.** HuggingFace's own
  ["asr-chunking" blog](https://huggingface.co/blog/asr-chunking) explicitly frames chunked
  inference as running overlapping-chunk batch inference with discarded edges to approximate
  full-utterance output — repeated batch inference, not incremental state-carrying decoding.
  Community tools ([oliverguhr/wav2vec2-live](https://github.com/oliverguhr/wav2vec2-live)) and HF
  forum guidance confirm no incremental/causal architecture exists.
* No standardized chunk size, no latency benchmark, no biasing mechanism, no 2025-2026 Meta
  successor found that changes this (only unrelated third-party research, e.g. GigaAM,
  arXiv:2506.01192, pre-2026-window).
* Integration effort: **high** — building the streaming layer (VAD segmentation, chunk overlap/
  stitching, latency tuning) essentially from scratch.

* * *

## Closed / Comparison-Only Baselines (excluded from candidate table)

Named per REQ-5 for context — none are open-weight candidates:

* **Azure Speech Services, Deepgram, AssemblyAI Universal-3 Pro Streaming** — closed cloud streaming
  APIs, no downloadable weights. AssemblyAI confirmed proprietary during the recency sweep.
* **Google USM** — 2B-param Conformer ([arXiv 2303.01037](https://arxiv.org/abs/2303.01037)), **no
  public weights ever released** (request-based API access only). An unofficial from-scratch
  reproduction exists ([github.com/kyegomez/USM](https://github.com/kyegomez/USM)) but is not
  Google's trained weights.
* **Google Chirp / Chirp 2 / Chirp 3** — productized USM descendants, available only inside Google
  Cloud Speech-to-Text API v2. No parameter counts, no weights, no published architecture. Chirp 1
  has **no streaming** (`StreamingRecognize` unsupported per
  [Google Cloud docs](https://docs.cloud.google.com/speech-to-text/docs/models/chirp-2)). Chirp 2/3
  add `StreamingRecognize` with `stability`-scored interim results (API-level true streaming
  confirmed; underlying model streaming architecture undisclosed). Phrase-hint contextual biasing
  documented for Chirp 2, streaming-mode extension presumed but not confirmed. Integration would be
  a thin `google-cloud-speech` gRPC client wrapper — lower engineering effort than local-weight
  wrapping, but trades away self-hosting, offline capability, and cost predictability.
* **Cohere Transcribe** — confirmed batch-only per its own HF card.
* **Qwen3-ASR** — confirmed **pseudo-streaming** (chunk-from-scratch, causing boundary-duplication
  artifacts per arXiv:2601.21337) — not closed, but explicitly ruled out as true-streaming, kept
  here as a named comparison rather than a table row since its verdict is unambiguous pseudo.
* **GigaAM-RNNT/v3** — pre-2026-window (originated 2024-2025), Russian self-supervised ASR encoder;
  not investigated further given the recency weighting.
* **Typhoon ASR Realtime (Thai)** — same FastConformer-Transducer family as Parakeet/Nemotron;
  excluded as a duplicate architecture pattern, not a distinct finding.
* **OpenAI GPT-Realtime-Whisper, Deepgram Flux, Microsoft MAI-Transcribe-1/VibeVoice ASR** —
  proprietary/closed-weight, out of scope per task exclusions.

* * *

## Comparison Table

| Model | Streaming mechanism | True/Pseudo | Chunk/frame | Streaming latency | Biasing in streaming | Integration effort | Fit vs current prod (parakeet-unified @~300ms) / Granite (batch, 97.1% EA-DV) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **parakeet-unified-en-0.6b** (current prod) | Cache-aware FastConformer+RNNT | True | 160ms-2.08s configs | Not reported (single-source config table only) | Not documented | Moderate (NeMo CLI/buffer API) | Baseline — this IS production |
| **nemotron-3.5-asr-streaming-0.6b** (NEW 2026-06) | Cache-aware FastConformer+RNNT, 40 locales | True | 80ms-1.12s configs | 0.07s TTFT (Artificial Analysis, independent); RTFx>6x on CPU (arXiv:2604.14493, independent) | Plausible, not empirically documented | Moderate (TextIteratorStreamer path may ease this) | **Top candidate** — same family as prod, best-corroborated streaming latency |
| **multitalker-parakeet-streaming-0.6b-v1** (t0015) | Cache-aware FastConformer + speaker kernels | True | 80ms-1.12s configs | Not reported | Not supported | High (needs external diarizer) | Niche — multi-speaker only |
| **Kyutai stt-1b/stt-2.6b-en** | Mimi codec + decoder-only Transformer, full-duplex | True | 80ms (fixed by codec) | RTFx 88.37 (vendor); 3x RTF/64 streams on L40S (vendor cross-check only) | Not supported | **Low** — native async generator | Best architecture, but no biasing — accuracy-risk vs Granite/prod |
| **Kyutai Moshi** | Same Mimi codec, full-duplex dialogue | True | 80ms | ~200ms (vendor, disputed by 1 GitHub issue) | Not applicable | Wrong shape (dialogue, not ASR-only) | Not recommended — use Kyutai STT instead |
| **T-one** (NEW, recency sweep) | Conformer+CTC, explicit state param | True | 300ms fixed | 600-800ms phrase latency (single-source) | Not supported | Moderate-low | Low priority — Russian/telephony-specialized |
| **Paraformer-streaming** (funasr) | SCAMA + LC-SAN-M, cached chunks | True | 600ms chunk / 300ms lookahead | Not reported | Unknown for this variant | Low (~1 day, existing generate()+cache API) | Needs validation before benchmark |
| **U2/U2++** (WeNet) | Dynamic chunk training, 2-pass CTC+rescore | Hybrid (CTC pass true, rescore pass buffered) | ~640ms (chunk=16) | ~320ms algorithmic (single-source) | Not supported | Moderate (less polished API than FunASR) | Lower priority — weaker evidence base |
| **Fun-ASR-Nano-2512** (NEW, Dec 2025/active 2026) | Decoupled streaming encoder + LLM decoder, KV-cache reuse | Likely true (self-reported) | Not reported | Not reported (only offline/batch speed figures found) | **Yes, confirmed** (RAG-based hotwords, streaming-mode table) | Low (same FunASR framework) | **Second-priority candidate** — only one besides Nemotron with confirmed streaming biasing |
| **parakeet-tdt-0.6b-v3** (prior prod, pre-t0017) | Chunked batch re-inference on offline model | **Pseudo** | User-configurable, no defaults | 9.22% WER at best chunk config vs 6.32% batch (independent, arXiv:2604.14493) | Not documented for streaming | Higher (inherits accuracy tax) | Already superseded by t0017 |
| **Granite Speech 4.1-2B(-Plus)** (entity-accuracy leader) | Conformer+CTC → Q-Former → LLM decoder, `.generate()` on full sequence | **No true streaming mode** | 4s encoder block / `prefix_text` batch-stitch (Plus only) | Batch-only: RTF~231x (2b), ~1820x (nar, press-relayed) | Yes in batch (Keyword List Biasing — likely source of 97.1% EA-DV) | **High** (multi-day-to-2-week custom engineering, accuracy risk) | **Accuracy leader but architecturally disjoint from streaming candidates** |
| **Moonshine v2** (eliminated on accuracy, t0008) | 50Hz causal + lookahead layers; real streaming only via `moonshine-voice` lib | True (architecture), but HF path not fully streaming-efficient | 80ms lookahead (320ms conservative) | 50-258ms by size (Apple M3, single-source) | Not supported | Moderate (~1 day glue via moonshine-voice) | Disqualified on accuracy + no biasing |
| **whisper_streaming** | LocalAgreement-n prefix commitment | Pseudo (model-level), true (hypothesis-commit level) | ~1s chunks | ~3.3s (non-VAC, single-source) | `initial_prompt`, carried forward | Low-moderate | Weak vs prod — high latency |
| **WhisperLive** | VAD-gated full re-inference | Pseudo | ~1s-scale | Not reported | Not threaded through | Low | Weak — no biasing, unverified latency |
| **simul_whisper** | Attention-guided truncation + KV-cache reuse | Closer to true | ~1s chunks | Not reported (paper curves only) | Not documented | High (research codebase) | Interesting architecture, immature |
| **speaches** | VAD-gated, one full call per utterance | Pseudo | VAD-defined (`silence_duration_ms=550`) | Not reported | Prompt/hotwords in batch endpoint only | Moderate | Weak |
| **RealtimeSTT** | Full re-inference every 0.2s tick | Pseudo | 512-sample buffer (~32ms), 0.2s tick | Not reported | `initial_prompt` (reapplied each tick) | Low-moderate | Weak |
| **whisper.cpp stream** | Sliding window + `whisper_full()` re-invocation | Pseudo | 3s step / 10s window | Not reported | Loose `init_prompt` support | High (C++ bridging) | Weak |
| **wav2vec2/MMS** | VAD-chunked batch inference (community only) | Pseudo, no maintained impl | Ad hoc, no standard | Not reported | Not supported | High (build from scratch) | Not viable |

*(Google USM/Chirp, Azure/Deepgram/AssemblyAI, Qwen3-ASR, GigaAM, Typhoon are named baselines in the
Closed/Comparison-Only section above, not table rows, per REQ-5.)*

* * *

## Ranked Shortlist for Follow-On Benchmarking

1. **`nvidia/nemotron-3.5-asr-streaming-0.6b`** — same NeMo cache-aware architecture family as the
   current production winner (`parakeet-unified-en-0.6b`), purpose-built for streaming (vs.
   parakeet-unified's shared offline/streaming checkpoint), with the strongest independent
   corroboration of streaming latency in this entire survey (Artificial Analysis + an independent
   CPU-only academic reproduction, arXiv:2604.14493). Same integration profile as the current model,
   so a benchmark is low-risk relative to the potential latency win.
   [huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
2. **`FunAudioLLM/Fun-ASR-Nano-2512`** — the only other candidate besides Nemotron 3.5 with
   confirmed streaming-mode contextual biasing (RAG-based hotwords, evaluated separately for
   streaming vs. offline in the technical report). If its true-streaming claim and biasing gain hold
   up on gold-92, it could close some of the Granite-vs-streaming accuracy gap without Granite's
   engineering cost.
   [huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512)
3. **`kyutai/stt-2.6b-en`** — architecturally the cleanest true-streaming implementation and the
   lowest integration effort of any candidate, but zero biasing support. Worth a benchmark run
   specifically to measure the raw accuracy floor without biasing, to quantify exactly how much the
   project's entity-accuracy gains depend on contextual biasing vs. base model quality.
   [huggingface.co/kyutai/stt-2.6b-en](https://huggingface.co/kyutai/stt-2.6b-en)
4. **`funasr/paraformer-zh-streaming`** — genuine cache-based true streaming with a promising
   architecture (SCAMA), but needs a preliminary check (does the English portion of this bilingual
   checkpoint perform reasonably, does hotword biasing work in this specific streaming variant)
   before committing to a full gold-92 run.
5. **Granite Speech streaming feasibility spike (not a benchmark, an engineering investigation)** —
   given Granite is the entity-accuracy leader but has no streaming mode, a short (1-2 day) spike
   chunking Granite via the undocumented `prefix_text` mechanism and measuring whether the 97.1%
   EA-DV survives chunking would resolve the project's most consequential open question: whether the
   accuracy leader can ever become streaming-viable, or whether streaming and entity-accuracy
   leadership will remain two different models for the foreseeable future.

## Comparison Against Current Production and Entity-Accuracy Leader

* **vs. `parakeet-unified-en-0.6b` @ ~300ms buffer (t0017, current production target)**: Nemotron
  3.5 ASR Streaming is architecturally a direct successor/sibling with better-corroborated streaming
  latency; it is the natural next benchmark. No other true-streaming candidate in this survey
  clearly beats parakeet-unified on both latency and integration effort simultaneously — Kyutai wins
  on integration effort and architectural purity but has no biasing, and Fun-ASR-Nano wins on
  biasing but has no measured streaming latency yet.
* **vs. Granite Speech 4.1 2B (97.1% EA-DV, batch-only)**: No candidate in this survey combines
  Granite's entity accuracy with true streaming. This is the project's central unresolved tension —
  documented above as the top finding and reflected in shortlist item 5 (a feasibility spike rather
  than a benchmark, since the underlying architecture question — can an LLM-decoder ASR model stream
  at all — has not been solved by IBM itself, per the unresolved community discussion on the
  `prefix_text` mechanism).

## Recommended Next Experiment

Benchmark **`nemotron-3.5-asr-streaming-0.6b`** against **`parakeet-unified-en-0.6b`** on gold-92
with GPU-PB biasing, using the same methodology as `t0017` (biased WER/EA/EA-DV, latency at multiple
buffer intervals, real-time-paced TTFD per the `t0017` correction). If GPU-PB or an equivalent
biasing mechanism does not transfer cleanly to Nemotron's architecture, that itself would be a key
finding, paralleling `t0017`'s finding that biasing barely helps the Parakeet family generally. In
parallel (or as a fast follow), run the Granite `prefix_text` chunking feasibility spike described
in shortlist item 5 to determine whether closing the streaming/ entity-accuracy gap is
architecturally possible at all.
