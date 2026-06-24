# Search Log for t0005_stt_model_survey_brainpowa

## Search Queries Executed

Total searches: 13

### Pass 1: Initial Landscape Queries

#### Query 1
- **Text**: `open-source STT models 2025 2026 entity accuracy contextual biasing`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 8 results
- **Key findings**: NVIDIA Parakeet/Canary performance, zero-shot contextual biasing emergence in 1B+ models, entity recognition via keyterm prompting

#### Query 2
- **Text**: `Hugging Face Open ASR Leaderboard WER streaming models`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: IBM Granite Speech 4.1 2B ranked #1 (5.33% WER), NVIDIA Canary Qwen #2 (5.63%), 86 models total on leaderboard, longform evaluation track

#### Query 3
- **Text**: `NVIDIA Parakeet Canary streaming contextual biasing latency`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 8 results
- **Key findings**: Parakeet 160ms minimum latency with RNN-Transducer, Canary streaming support, LOGIC method for contextual biasing (2.8% latency overhead)

#### Query 4
- **Text**: `Whisper v3 turbo WhisperX entity accuracy domain vocabulary`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 9 results
- **Key findings**: Whisper Turbo 8x faster than Large v3, domain vocabulary weakness, WhisperX adds diarization/timestamps, no native contextual biasing

### Pass 2: Model-Specific Queries

#### Query 5
- **Text**: `Moonshine streaming ASR low latency English 2025`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: Moonshine v2 50-258ms latency (Tiny/Small/Medium), 5.3% WER, ergodic encoder, no hallucinations, OnnxRuntime CPU-first

#### Query 6
- **Text**: `FunASR Paraformer SenseVoice contextual biasing entity accuracy`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 7 results
- **Key findings**: EWER 1.8% with ~1,800 entities, 10% entity error reduction via deep biasing, 480-600ms streaming latency, Apache 2.0 license

#### Query 7
- **Text**: `Kyutai Moshi STT streaming speech recognition 2025`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 9 results
- **Key findings**: Two models (1B English-French, 2.6B English-only), 2.5s output delay (delayed streams), 400 concurrent streams on H100, WebSocket server

#### Query 8
- **Text**: `wav2vec2 Massively Multilingual Speech XLSR entity recognition`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: XLSR-53 fine-tuning base (not ready-to-run), 53-language pretraining, 72% phoneme error reduction, low-resource language support

### Pass 3: Breadth and Comparison Queries

#### Query 9
- **Text**: `IBM Granite Speech open-source ASR entity accuracy 2025 2026`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 9 results
- **Key findings**: Granite 4.1 2B #1 leaderboard (5.33% WER), keyword biasing with F1 metrics, 174k hours training, Apache 2.0, NAR variant for speed

#### Query 10
- **Text**: `Qwen Audio Qwen2-Audio multimodal speech recognition 2025`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: Qwen2-Audio unified audio-language model, 30+ tasks, 8 languages, Qwen2.5-Omni end-to-end multimodal with real-time responses

#### Query 11
- **Text**: `Conformer FastConformer streaming ASR contextual biasing GPU latency`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: FastConformer 8x subsampling vs. 4x, cache-aware streaming 17x latency reduction, 560 concurrent streams on H100, contextual biasing minimal overhead

#### Query 12
- **Text**: `STT model comparison benchmark latency RTF entity accuracy 2026`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 8 results
- **Key findings**: Latency-accuracy tradeoff curve, Deepgram Nova 3/2 fastest (25.2-25.3% WER), Gradium STT most accurate (2.4% WER), entity accuracy 50-70% on alphanumeric

### Pass 4: Deepening and Comparison Queries

#### Query 13
- **Text**: `Alibaba FunASR vs NVIDIA Parakeet vs Moonshine comparison 2026`
- **Source**: Google Web Search
- **Date**: 2026-06-24
- **Result count**: 10 results
- **Key findings**: Fun-ASR 7.7B (Qwen3 base), Parakeet 600M (23rd accuracy, 6.5x faster than Canary), Moonshine 245M (6x smaller than Whisper, matches/beats on English)

## Deep-Read Sources (WebFetch)

### [Moonshine-v2-PDF]
- **URL**: https://arxiv.org/pdf/2602.12241
- **Prompt**: Extract latency, WER, model sizes, streaming details, hardware requirements
- **Result**: Technical details extracted (latency 50-258ms, streaming architecture, edge deployment patterns)

### [Canary-Parakeet-Paper]
- **URL**: https://arxiv.org/pdf/2509.14128
- **Prompt**: Performance metrics, contextual biasing, latency RTF, model sizes
- **Result**: Specifications extracted (Canary 1B, Parakeet 0.6B, streaming support, biasing mechanisms)

### [OWSM-Biasing-Paper]
- **URL**: https://arxiv.org/pdf/2506.09448
- **Prompt**: Entity accuracy metrics, contextual biasing approach, Whisper integration
- **Result**: PDF binary content; metadata extracted (title, authors); full text requires dedicated PDF reader

### [Moonshine-GitHub-Repo]
- **URL**: https://github.com/moonshine-ai/moonshine
- **Prompt**: Python API, streaming configuration, input formats (PCM16), GPU requirements, integration instructions
- **Result**: API documented (`Transcriber` class, `add_audio()`, 32-bit float mono PCM, auto-resampling to 16kHz, OnnxRuntime, CPU-first)

### [Northflank-Benchmark]
- **URL**: https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks
- **Prompt**: WER, latency, GPU requirements, entity accuracy for all compared models
- **Result**: Benchmark table extracted (Canary 5.63%, IBM Granite 5.85%, Whisper 7.4%, Parakeet ~8%)

### [ASR-Deep-Dive-2026]
- **URL**: https://ruoqijin.com/blog/asr-deep-dive-2025-2026
- **Prompt**: 2025-2026 technology recommendations, entity accuracy, latency budgets, integration effort
- **Result**: Selection guide extracted (Conformer+LLM as SOTA, Chinese/English/code-switch recommendations, 3-7x real-world degradation vs. benchmarks)

### [Local-STT-Comparison]
- **URL**: https://www.onresonant.com/resources/local-stt-models-2026
- **Prompt**: Detailed comparison table (WER, latency, GPU, entity accuracy, biasing for Moonshine/Parakeet/Whisper)
- **Result**: Comparison extracted (Moonshine 245M MIT vs. Parakeet 600M, Whisper 1.5B, hallucination risks noted)

## Summary Statistics

- **Total queries**: 13
- **Search sources**: Google Web Search (primary), arXiv, GitHub, Hugging Face, official documentation
- **Deep-read sources (WebFetch)**: 7
- **Papers/preprints discovered**: 8
- **Blog/documentation sources cited**: 16
- **Date range covered**: 2020–2026, emphasis on 2024–2026 releases
- **Key themes**: Streaming ASR, contextual biasing, entity accuracy, latency-accuracy tradeoffs, 2025-2026 releases

## Search Refinement Notes

- **Query 8 (wav2vec2/XLSR)**: Returned fine-tuning frameworks rather than ready-to-run models; decision made to exclude from shortlist per task constraints (self-hostable inference required).
- **Query 11 (Conformer/FastConformer)**: Returned architectural research; clarified that Conformer is foundation for multiple models (NVIDIA Nemotron, Granite, Parakeet); cache-aware streaming not a separate product.
- **Queries 2 and 12 convergence**: Multiple sources reported latency-accuracy tradeoff; no single model leads on both dimensions simultaneously. Latency budget (800ms p50) is achievable by all shortlist candidates with optimization.
- **Entity accuracy sparsity**: Only FunASR/IBM Granite explicitly document entity-specific recall; most others report general WER. Downstream benchmarking on gold-92 will be essential to validate shortlist.

## Excluded Candidates and Rationale

- **Whisper variants (base, small, medium)**: Prioritized Whisper Large v3/Turbo as production baseline; smaller variants trade accuracy for speed without matching Moonshine's speed-accuracy frontier.
- **Azure Speech, Deepgram**: Closed cloud APIs per task constraints (named comparison baselines only, not candidates).
- **Kaldi, Julius, CMU Sphinx**: Legacy systems; deprioritized in favor of modern neural approaches.
- **Multilingual models without English focus**: Qwen3-ASR 7.7B prioritizes Chinese-English; not evaluated due to size and latency concerns for English-only task.
- **TTS/Voice conversion models**: Excluded per scope (STT only).

## Key Sources Not Yet Explored (Future Work)

- Papers With Code ASR benchmark (leaderboard alternative perspective)
- Artificial Intelligence Metrics (AIMetrics) speech-to-text benchmark
- Industry white papers (Deepgram Nova, AssemblyAI Universal, etc.) on entity accuracy improvements
- Conference proceedings (ICASSP 2026, Interspeech 2025) for contextual biasing methods
- Preprint servers beyond arXiv (ResearchGate discussions on practical implementations)
