# t0018 Search Log

Queries run across four parallel research passes (NVIDIA/Kyutai; Moonshine/Whisper wrappers;
FunASR/wav2vec2; Granite/Google + recency sweep). Result counts and notes as reported by each
research pass.

## NVIDIA Parakeet / Canary / Nemotron / Kyutai pass

| # | Query | Results / notes |
| --- | --- | --- |
| 1 | nvidia parakeet-tdt-0.6b-v3 streaming cache-aware conformer | 9 links; HF model card, arXiv:2604.14493, HF discussion #11 |
| 2 | nvidia parakeet-unified-en-0.6b huggingface streaming | 9 links; model card, sherpa-onnx issue #3573 |
| 3 | nvidia multitalker-parakeet-streaming-0.6b-v1 | 10 links; model card + revision history |
| 4 | NeMo cache-aware streaming Conformer FastConformer chunk size latency | 9 links; arXiv:2312.17279, NeMo docs, Nemotron 3.5 blog |
| 5 | Kyutai STT streaming model huggingface delayed streams modeling | 9 links; stt-2.6b-en model card, GitHub repo, Modal docs |
| 6 | Kyutai Moshi full duplex streaming ASR frame size 80ms | 9 links; GitHub, Moshi paper PDF |
| 7 | NeMo GPU-PB TurboBias contextual biasing hotword streaming | 9 links; arXiv:2508.07014 TurboBias paper |
| 8 | Kyutai Moshi mimi codec async streaming python API websocket real-time | 9 links; confirmed WebSocket + async patterns |
| 9 | Nemotron speech streaming ASR RTF real-time factor benchmark independent GPU | 8 links; Artificial Analysis independent benchmark |
| 10 | Moshi Kyutai latency 200ms independent benchmark review 2025 | 9 links; GitHub issue #229 (community latency complaint) |
| 11 | "nemotron" ASR streaming 2026 release parakeet successor NVIDIA announcement | 9 links; MarkTechPost June 2026 article confirming nemotron-3.5-asr-streaming-0.6b |
| 12 | Kyutai new streaming STT model 2026 release | 9 links; no new 2026 Kyutai STT beyond stt-1b/stt-2.6b |
| 13 | "nemotron 3.5 asr" OR "nemotron-speech-streaming" independent benchmark reproduction third party | 8 links; confirmed arXiv:2604.14493 as independent reproduction |
| 14 | NeMo CacheAwareStreamingAudioBuffer python asyncio generator streaming class | 9 links; confirmed no native async-generator API |
| 15 | NVIDIA Parakeet RTF real-time factor streaming latency benchmark A100 | 10 links; RTFx=3380 batch-128 offline claim, E2E Networks L4 benchmark |
| 16 | NVIDIA Riva ASR streaming Parakeet Canary gRPC support 2026 | 10 results; Riva 2.18.0 streaming claims, NIM docs |
| 17 | NeMo cache_aware_streaming example script speech_to_text_streaming_infer.py | 10 results; NeMo GitHub script paths |
| 18 | Parakeet streaming RTF reddit real-time factor benchmark independent | 10 results |
| 19 | parakeet streaming websocket fastapi github wrapper server | 8 GitHub repos found |
| 20 | Riva ASR streaming gRPC bidirectional API partial final transcript documentation | confirmed StreamingRecognize API shape |
| 21 | NVIDIA Riva Parakeet-TDT streaming support matrix NIM 2026 | resolved streaming-support discrepancy (TDT/Canary offline-only in NIM) |
| ~20 WebFetch calls | model cards, NeMo docs, GitHub source (Riva python client, community FastAPI wrappers), arXiv papers | see per-candidate citations in research_internet.md |

**~30+ WebFetch calls total** against: nvidia/parakeet-unified-en-0.6b, nvidia/parakeet-tdt-0.6b-v3,
nvidia/multitalker-parakeet-streaming-0.6b-v1, nvidia/nemotron-speech-streaming-en-0.6b,
nvidia/nemotron-3.5-asr-streaming-0.6b, nvidia/parakeet_realtime_eou_120m-v1, kyutai.org/stt/,
kyutai-labs/delayed-streams-modeling, kyutai-labs/moshi, arXiv 2312.17279 / 2604.14493 / 2508.07014,
NIM/Riva docs, sherpa-onnx issue #3573, Artificial Analysis leaderboard.

## Moonshine / Whisper streaming variants pass

| # | Query | Results / notes |
| --- | --- | --- |
| 1 | Moonshine ASR usefulsensors streaming architecture live captioning | 9 results |
| 2 | Moonshine speech recognition paper arxiv streaming variable length audio | 8 results; found v2 paper arXiv:2602.12241 |
| 3 | "moonshine" streaming latency benchmark real-time factor 2026 edge device | 7 results, mixed v1/v2 marketing claims |
| 4 | moonshine-voice pip package streaming MicTranscriber github usefulsensors | 9 results |
| 5 | Moonshine ASR hotword biasing initial_prompt custom vocabulary | 9 results, disconfirmed bias_terms claim |
| 6 | ufal whisper_streaming github LocalAgreement | found README, LocalAgreement algorithm |
| 7 | "Turning Whisper into Real-Time Transcription System" arxiv | arXiv:2307.14743 |
| 8 | whisper_streaming latency benchmark RTF | only downstream citations of same paper number found |
| 9 | collabora WhisperLive github streaming architecture | found README, server.py structure |
| 10 | WhisperLive latency TensorRT benchmark | only qualitative claims |
| 11 | WhisperLive initial_prompt hotword | not prominently exposed |
| 12 | simul_whisper github backspacetg | found repo |
| 13 | Simul-Whisper arxiv attention guided truncation detection | found paper abstract/methodology |
| 14 | Simul-Whisper KV cache streaming Whisper independent reproduction | none found beyond paper's own curves |
| 15 | faster-whisper-server fedirz speaches streaming VAD github | identified speaches-ai/speaches successor |
| 16 | shashikg WhisperS2T streaming github VAD chunking | ruled out — batch-only |
| 17 | KoljaB RealtimeSTT faster-whisper streaming architecture github | found docs + fastapi server example |
| 18 | SYSTRAN faster-whisper streaming VAD example github issue | confirmed issue #384 open/unresolved |
| 19 | ggerganov whisper.cpp examples stream real-time | inspected stream.cpp re-invocation pattern |
| 20 | Whisper streaming 2026 new release paper / simultaneous speech recognition Whisper 2026 arxiv / real-time Whisper ASR 2026 paper | no new 2026 algorithmic release found (run twice, consistent) |
| ~10 WebFetch/gh api calls | GitHub source (usefulsensors/moonshine, moonshine-ai/moonshine, ufal/whisper_streaming, collabora/WhisperLive, speaches-ai/speaches source files, KoljaB/RealtimeSTT source files), HF model cards (moonshine-streaming-tiny/medium), arXiv 2602.12241 | see per-candidate citations |

## FunASR / Paraformer streaming + wav2vec2/MMS pass

| # | Query | Results / notes |
| --- | --- | --- |
| 1 | FunASR Paraformer streaming architecture scout monotonic alignment | 10 results |
| 2 | U2++ dynamic chunk streaming Conformer WeNet true streaming CTC attention rescoring | 9 results |
| 3 | wav2vec2 streaming chunked CTC inference implementation 2025 | 10 results |
| 4 | FunASR paraformer-streaming HuggingFace model card 2025 2026 | 8 results |
| 5 | FunASR SCAMA streaming paraformer chunk lookback lookahead attention mask paper | 9 results |
| 6 | "SCAMA" streaming chunk-aware multihead attention paraformer arxiv paper | 8 results; found arXiv:2006.01712 |
| 7 | wav2vec2 streaming ASR maintained implementation huggingface github 2025 real-time production | 9 results |
| 8 | Meta MMS streaming ASR 2025 2026 wav2vec2 successor model | 8 results; none found |
| 9 | WeNet U2++ RTF real time factor GPU CPU AISHELL benchmark table | 9 results |
| 10 | Fun-ASR-Nano streaming support autoregressive LLM-ASR real-time incremental | 7 results |
| 11 | Fun-ASR streaming table 3 first token latency CER online offline comparison | 10 results |
| ~8 WebFetch calls | huggingface.co/funasr/paraformer-zh-streaming, github.com/modelscope/FunASR, arXiv 2106.05642 (U2++, via ar5iv mirror after PDF-extraction failure), github.com/wenet-e2e/wenet runtime/gpu/README.md, huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512, arXiv 2509.12508 (Fun-ASR technical report) | see per-candidate citations |

## Granite / Google USM-Chirp / recency sweep pass

| # | Query | Results / notes |
| --- | --- | --- |
| 1 | IBM Granite Speech streaming real-time transcription | 7 results |
| 2 | Granite Speech 4.1 2B architecture | 8 results |
| 3 | Granite Speech incremental decoding online ASR | 10 results |
| 4 | granite-speech huggingface model card | 7 results |
| 5 | Granite Speech arxiv conformer Q-Former architecture | 9 results |
| 6 | "granite speech" arxiv 2025 ASR | 8 results; arXiv 2505.08699 |
| 7 | Granite speech block attention "self-conditioned CTC" causal query | 10 results |
| 8 | "Google USM Universal Speech Model open weights huggingface" | 9 results — none found |
| 9 | "Google USM model download github" | 10 results — unofficial reproduction only |
| 10 | "Google Chirp 2 open source weights" | 10 results — none, API-only |
| 11 | "Chirp streaming speech-to-text API Google Cloud" | 10 results |
| 12 | "Chirp 2 streaming recognition latency benchmark" | 9 results — no official latency numbers |
| 13 | USM paper weights release plan | 9 results — no release plan found |
| 14 | "Chirp 1 streaming not supported batch only" | 10 results — confirmed Chirp 1 has no streaming |
| 15 | "Google Cloud Speech-to-Text V2 StreamingRecognize gRPC python client" | 8 results |
| 16 | "google-research usm github repository official" | 10 results — no official repo |
| 17 | "streaming ASR" 2026 release open weight | 9 results |
| 18 | "new streaming speech recognition model" 2026 | 9 results |
| 19 | streaming speech-to-text model announcement 2026 | 10 results |
| 20 | HuggingFace new streaming ASR model 2026 | 10 results |
| 21 | Meta streaming ASR 2026 open source | 10 results — none found |
| 22 | Microsoft Phi streaming speech 2026 | 6 results — no streaming-specific release |
| 23 | "real-time speech recognition" open source model 2026 | 7 results |
| 24 | new open weight ASR model 2026 low latency streaming | 10 results |
| 25 | Qwen3-ASR streaming architecture | 9 results — chunk-from-scratch, not true streaming |
| 26 | Cohere Transcribe open source streaming | 9 results — batch-only |
| 27 | t-tech T-one ASR streaming Russian | 10 results — new true-streaming candidate found |
| 28 | Typhoon ASR realtime Thai | 9 results — same FastConformer-Transducer family, excluded as duplicate architecture |
| 29 | AssemblyAI Universal-3 Pro streaming | 9 results — closed/proprietary, excluded |
| 30 | "streaming ASR" new model paper 2026 arxiv | 10 results |
| 31 | GigaAM RNNT streaming 2026 | 10 results — pre-2026-window, excluded |
| 32 | T-one release date announcement | 8 results |
| ~10 WebFetch calls | HF model cards (granite-speech-4.1-2b, -2b-plus), arXiv 2505.08699, MindStudio blog, docs.cloud.google.com/chirp-2, arXiv 2303.01037 (USM), research.google USM blog, Cohere Transcribe HF page, t-tech/T-one GitHub + HF page, BrightCoding blog | see per-candidate citations |

**Stopping criterion met**: the recency sweep (queries 17-31 above) ran well past the two
consecutive dry-search threshold defined in the plan — most queries returned only already-covered
families (Parakeet-unified, Nemotron 3.5, Granite, Qwen3-ASR, GigaAM) or closed/excluded systems
(Cohere Transcribe, AssemblyAI, Deepgram Flux, Microsoft MAI-Transcribe-1). Exactly one genuinely
new true-streaming open-weight candidate was found: **T-one** (t-tech/T-Bank, Apache 2.0).
