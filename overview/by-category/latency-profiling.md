# Category: Latency Profiling

End-to-end measurement of voice-to-action latency from speech end to tool call across
candidate STT pipeline configurations.

[Back to Dashboard](../README.md)

**Detail pages**: [Papers (5)](../papers/by-category/latency-profiling.md) | [Suggestions
(7)](../suggestions/by-category/latency-profiling.md)

---

## Papers (5)

<details>
<summary>📝 <strong>Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical
Speech Applications</strong> — Kudlur et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2602.12241` |
| **Authors** | Manjunath Kudlur, Evan King, James Wang, Pete Warden |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2602.12241` |
| **URL** | https://arxiv.org/abs/2602.12241 |
| **Date added** | 2026-06-23 |
| **Categories** | [`latency-profiling`](../../meta/categories/latency-profiling/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12241/summary.md) |

Moonshine v2 addresses latency in on-device ASR through an ergodic streaming encoder that
processes audio in fixed-size chunks with bounded per-chunk computation. The motivation is
that standard transformer encoders block on full-utterance processing, creating latency
proportional to utterance length that is unacceptable for real-time voice assistants.

The architecture uses sliding-window self-attention to provide each audio frame a fixed
receptive field, enabling stateless chunk-by-chunk processing. Three model sizes (Tiny, Small,
Medium) are provided, all using the same encoder design with varying capacity. The decoder
remains a standard autoregressive transformer.

Measured on Apple M3, the Tiny model achieves **50ms** latency at **8.03%** compute load while
the Medium achieves **258ms** at **28.95%** load. Average WER ranges from **12.01%** (Tiny) to
**6.65%** (Medium) on the Open ASR leaderboard. The Medium model is **43.7×** faster than
Whisper Large v3 at 1-2pp WER penalty.

For Rezolve's pipeline, Moonshine v2 represents a viable low-latency streaming ASR alternative
that fits comfortably within the 800ms p50 budget. The Small variant (148ms, 7.84% WER) is the
most promising trade-off point. However, no entity-level accuracy data is reported;
domain-specific evaluation on ecommerce entities is a prerequisite before production adoption.

</details>

<details>
<summary>📝 <strong>Back to Basics: Revisiting ASR in the Age of Voice
Agents</strong> — Tay et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.25727` |
| **Authors** | Geeyang Tay, Wentao Ma, Jaewon Lee, Yuzhi Tang, Daniel Lee, Weisu Yin, Dongming Shen, Silin Meng, Yi Zhu, Mu Li, Alex Smola |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2603.25727` |
| **URL** | https://arxiv.org/abs/2603.25727 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../meta/categories/stt-evaluation/), [`latency-profiling`](../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/summary.md) |

Tay et al. (2026) challenge the assumption that ASR is a solved problem by demonstrating that
modern systems achieving sub-5% WER on standard benchmarks fail severely and unpredictably
under real-world voice agent conditions. The paper's motivation is direct: voice agents do not
passively transcribe speech but use transcripts to trigger downstream tool calls and execute
actions. Under out-of-distribution conditions, hallucinated or garbled transcripts cause
silent action failures — exactly the problem Rezolve faces with its production Deepgram
deployment on accented investor-relations audio. The paper introduces WildASR, a multilingual
diagnostic benchmark (EN/ZH/JA/KO) constructed entirely from real human speech.

The benchmark decomposes OOD robustness into 11 conditions across three axes: environmental
degradation (reverberation, far-field, phone codec, noise gap, clipping), demographic shift
(children, older adults, accented speakers), and linguistic diversity (short utterances,
truncated audio, code-switching). Seven systems — Whisper Large V3, GPT-4o Transcribe, Gemini
2.5/3 Pro, Qwen2-Audio, Deepgram Nova 2, ElevenLabs Scribe V1 — are evaluated under a unified
protocol. Three diagnostic tools supplement raw metrics: a P90 Elbow detector, a prompt
sensitivity profiler (10 paraphrased instructions), and integration of Hallucination Error
Rate to catch semantic fabrications that WER misses.

The headline results are stark. Noise gaps cause **+67.7% WER** for English conversational
speech and **+121% CER** for Korean. No model achieves below **18.2% WER** on English child
speech. Deepgram Nova 2 on Chinese code-switching produces 33.7% lexical error but **68.4%
semantic hallucination rate**. Prompt phrasing alone induces up to **σ = 46.1%** performance
swing for Chinese. Robustness does not transfer across languages: a model robust to
reverberation in English may catastrophically fail in Japanese under the same perturbation.
Synthetic TTS-based evaluation underestimates real failure rates by 5.9× compared to authentic
child speech.

For this project, the paper delivers three concrete takeaways. First, the gold-92 evaluation
harness must stratify by utterance condition type and adopt HER alongside WER and entity
accuracy — aggregate WER alone will miss the hallucination risk that production Deepgram
carries. Second, Deepgram Nova 2 and Whisper Large V3 both show condition-specific failure
modes that mean their gold-92 rankings may not reflect their behavior on domain-specific OOD
inputs like accented investor-relations vocabulary. Third, the paper validates Rezolve's
methodological choice to use real production audio for gold-92 rather than TTS-synthesized
data, and confirms that short terse commands — a common voice commerce pattern — are a
high-risk category that merits dedicated coverage in the benchmark design.

</details>

<details>
<summary>📝 <strong>Contextual Biasing for Streaming ASR via CTC-based Word
Spotting</strong> — Tsai et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.18222` |
| **Authors** | Kai-Chen Tsai, Tien-Hong Lo, Yun-Ting Sun, Berlin Chen |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.18222` |
| **URL** | https://arxiv.org/abs/2605.18222 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`latency-profiling`](../../meta/categories/latency-profiling/), [`stt-evaluation`](../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.18222/summary.md) |

Tsai et al. adapt CTC-based word spotting to streaming ASR by maintaining trie search state
across audio chunks. The core contribution is that keyword paths are not discarded at chunk
boundaries but preserved in a stateful token passing buffer, allowing detections that straddle
chunk boundaries. An incremental commitment threshold controls how long ambiguous segments are
held before being emitted.

The approach is model-agnostic: it operates on CTC posteriors, not encoder activations, making
it applicable without any retraining. The streaming window is 160ms per chunk, consistent with
practical streaming ASR deployment constraints.

Results demonstrate reduced WER and improved keyword F-score compared to streaming CTC without
biasing; specific absolute numbers are not reported in the abstract. Latency overhead is
bounded and configurable via the commitment threshold β.

For Rezolve's pipeline, the most attractive property is zero training cost: the stateful
CTC-WS can be applied directly to Whisper Turbo's CTC head without modifying model weights.
The 160ms chunk size matches typical streaming deployment, and the commitment mechanism can be
tuned to stay within the 800ms p50 latency budget. The absence of absolute metric values in
the paper's available metadata is a gap; full-paper validation is needed before concluding on
entity F-score gains.

</details>

<details>
<summary>📝 <strong>Beyond Prompting: Efficient and Robust Contextual Biasing for
Speech LLMs via Logit-Space Integration (LOGIC)</strong> — Wang, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.15397` |
| **Authors** | Peidong Wang |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2601.15397` |
| **URL** | https://arxiv.org/abs/2601.15397 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`latency-profiling`](../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.15397/summary.md) |

LOGIC (Logit-Space Integration for Contextual Biasing) addresses the inability of Speech LLMs
to reliably recognise domain-specific entities — brand names, contact names, product
identifiers — without the scalability failures of prompting or the hallucination failures of
generative error correction. The paper motivates the problem by demonstrating that prompting
collapses with as few as 460 entities (exhibiting "list-vomiting" output) and that GEC
introduces hallucinated entities based on textual similarity rather than acoustic evidence.
LOGIC is proposed as a decoding-layer alternative that injects entity bias directly into the
logit distribution at each auto-regressive step using a subword-aware prefix tree, achieving
O(1) complexity with respect to entity list size.

The method constructs a Token-Level Trie from the entity phrase list using Multi-Path
Tokenization to handle SentencePiece's context-dependent subword segmentation, then applies a
sparse logit bonus at each decoding step for tokens that extend a valid Trie path. Immediate
Prefix Boosting (IPB) fires the bias from the very first token of any entity to maximise
recall for short entries, while Retroactive Score Rectification (RSR) penalises hypotheses
that accumulate partial-match bonuses but diverge before completing the entity string. The
CUDA implementation uses a sparse kernel with O(D) per-step complexity, deployed as a vLLM
LogitsProcessor with zero-copy GPU state.

Experiments using Phi-4-Mini across 11 multilingual locales on an internal Microsoft Person
Name test suite show **9% average relative EWER improvement** in a conservative configuration
and **17%** in an aggressive configuration, with average FAR increase of just **+0.30%** and
RTF overhead of only **+2.8%** on A100 GPUs. French (**19%**), German (**14%**), and Mexican
Spanish (**17%**) see the strongest improvements. The method generalises to logographic
languages (zh-CN **9%**, ja-JP **6%**) despite the added complexity of context-sensitive
subword tokenization.

For the Rezolve STT project, LOGIC is directly actionable as a production-grade entity-biasing
layer for any Speech LLM (Phi-4, GPT-4o Audio) used as a replacement for or complement to
Deepgram. Its near-zero latency overhead is compatible with the 800 ms p50 voice-to-action
budget, and RSR's hallucination suppression is critical for ecommerce where false entity
insertions cause incorrect purchase actions. The key validation gap is whether the EWER
improvements on Person Names transfer to Rezolve's entity types (brand names, product lines,
investor-relations terms), which have different phonetic distributions and may require
independent tuning of the biasing bonus λ per entity category.

</details>

<details>
<summary>📝 <strong>TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust
Automatic Speech Recognition</strong> — Wang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.27808` |
| **Authors** | Xinyu Wang, Ziyu Zhao, Ke Bai, Silin Meng, Dongming Shen, Xiao-Wen Chang, Yixuan He |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.27808` |
| **URL** | https://arxiv.org/abs/2605.27808 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../meta/categories/entity-correction/), [`latency-profiling`](../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.27808/summary.md) |

TARQ diagnoses and fixes a structural flaw in data-aware post-training quantization for ASR:
standard calibration metrics inherit the Zipfian token-frequency distribution of the
calibration corpus, assigning only ~6.9% of trace mass to rare tokens (names, numerals, domain
terms) that represent a disproportionate share of recognition risk in entity-sensitive
applications. The research question is whether this metric-level imbalance — not solver
quality — is the root cause of rare-word degradation under W4G128 quantization of modern ASR
models.

TARQ addresses this through RAREBAL, a closed-form per-Linear-layer trace equalization that
reweights the calibration metric to give equal mass to common and rare token groups, computed
from a single scalar derived from activation second moments already accumulated during PTQ. A
propagation-aware residual correction ensures the sequential layer sweep remains aligned with
the rebalanced metric. Both components require no entity labels, no additional data, and no
extra calibration pass, making TARQ a drop-in enhancement to any GPTQ-family solver.

Across 8 backbones and 6 datasets, TARQ achieves rank-1 mean plain WER on all backbones and
rank-1 mean rare-WER on 6 of 8, with a cross-corpus stability swing of just 0.63 pp vs 2.51 pp
for GPTQ. Entity-rich benchmarks (ProfASR, ContextASR-Speech-En) confirm transfer without
entity supervision. Deployment profiling shows 1.06x–2.18x GPU speedup and 33%–67% VRAM
reduction, with Whisper-large-v3 reaching CPU real time (RTF 0.87 at 8 threads).

For Rezolve's voice commerce pipeline, TARQ offers a practical path to compressed ASR without
sacrificing brand name and SKU recognition quality. The identified limitation — failure on
isolated rare proper nouns lacking phonetic context — directly motivates the entity-correction
research track in this project, confirming that inference-time contextual biasing or
vocabulary injection must complement quantization-time fixes. The paper's rare-WER metric also
provides a precise template for enriching the gold-92 benchmark evaluation beyond aggregate
WER.

</details>

## Tasks (1)

| # | Task | Status | Completed |
|---|------|--------|-----------|
| 0003 | [Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)](../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) | completed | 2026-06-23 09:25 |

## Answers (0)

No answers in this category.

## Suggestions (7 open, 0 closed)

<details>
<summary>🧪 <strong>Benchmark Moonshine ONNX Medium on gold-92 when UsefulSensors
ships the ONNX export</strong> (S-0008-01)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-25 | **Source**:
[t0008_moonshine_v2_benchmark](../../tasks/t0008_moonshine_v2_benchmark/)

t0008 used the HuggingFace Transformers CPU backend because moonshine_onnx does not include a
Medium variant. The ONNX export is expected to be ~30ms faster per clip, which would bring
warmed p50 from 233ms to ~200ms and potentially meet the project latency target. Once
UsefulSensors ships an ONNX Medium model, run it on all 93 gold-92 clips using the same
inference harness as t0008 and compare latency p50/p95/p99 and entity accuracy. Recommended
task types: stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Moonshine model-size ablation: benchmark tiny, base, and large
variants on gold-92 entity accuracy</strong> (S-0008-02)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-25 | **Source**:
[t0008_moonshine_v2_benchmark](../../tasks/t0008_moonshine_v2_benchmark/)

t0008 found that Moonshine v2 Medium (266M params) achieves exactly the same
entity_accuracy_gold92 (21.7%) and entity_accuracy_domain_vocab (9.1%) as the base model (38M
params) from t0004. This contradicts the assumption that a larger model would improve entity
recall. A controlled ablation across all published Moonshine variants (tiny, base,
streaming-medium, and any large variant) would confirm whether the entity accuracy plateau is
a training-distribution gap or a tokenizer/decoder limit, and would determine the optimal
model size for latency/accuracy trade-off before investing in S-0005-04 shallow fusion work.
Recommended task types: stt-benchmark-run, comparative-analysis.

</details>

<details>
<summary>📊 <strong>Profile Granite 4.1, Paraformer, and Whisper latency under
concurrent request load</strong> (S-0005-05)</summary>

**Kind**: evaluation | **Priority**: high | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../../tasks/t0005_stt_model_survey_brainpowa/)

The survey reports single-request latencies; production voice-to-action pipelines receive
concurrent requests. Profile all three candidates (Granite, Paraformer, Whisper turbo) on
Rezolve's production infrastructure under 10, 50, and 100 concurrent sessions. Measure TTFT
(time-to-first-token), total latency, p50/p95/p99 percentiles, and VRAM utilization at each
concurrency level. This determines whether Granite/Paraformer can sustain the latency budget
under realistic load, and whether GPU memory becomes the bottleneck. If latency degrades
significantly at >10 concurrent sessions, batch-processing or model quantization strategies
become necessary. Recommended task types: experiment-run, data-analysis.

</details>

<details>
<summary>📊 <strong>Test entity-biasing mechanisms at scale (1,000+ entity
vocabulary)</strong> (S-0005-06)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../../tasks/t0005_stt_model_survey_brainpowa/)

The survey reports contextual biasing results on 50–1,800 entity lists. Rezolve's product
catalog scales to 10,000+ SKUs. Test whether Granite 4.1 keyword biasing and Paraformer
deep-biasing maintain performance (latency, entity accuracy) when biasing context grows from
1,800 to 10,000 entities. Measure latency scaling curve and F1 degradation if any. If latency
exceeds budget at production scale, design a retrieval-based filtering pre-pass (e.g.,
retrieve top-100 entities relevant to the speaker/context before biasing) to cap the active
biasing vocabulary. Recommended task types: experiment-run, data-analysis.

</details>

<details>
<summary>🔧 <strong>Implement quantized variants of Granite/Paraformer for edge and
latency optimization</strong> (S-0005-10)</summary>

**Kind**: technique | **Priority**: low | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../../tasks/t0005_stt_model_survey_brainpowa/)

If benchmarking shows that Granite or Paraformer meet accuracy targets but exceed VRAM or
latency budgets at scale, implement quantized (int8/float16) variants using ONNX, TensorRT, or
vLLM to reduce model size and improve inference speed. Moonshine already ships as a
245M-parameter model optimized for edge; quantization could reduce Granite (2B) and Paraformer
(varies) to similar footprints. Measure quantization impact on entity accuracy and latency. If
quantization preserves accuracy within 1–2% while halving latency, quantized variants become
the recommended production deployment. Recommended task types: experiment-run, build-model.

</details>

<details>
<summary>🔧 <strong>Implement Novitasari2026 common-word cue injection as a
zero-latency biasing add-on</strong> (S-0003-05)</summary>

**Kind**: technique | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../../tasks/t0003_literature_review_entity_stt/)

Implement the common-word cue approach from Novitasari2026 as a pre-processing step on top of
Rezolve's existing dynamic context injection. The method maps non-standard brand names and
SKUs to phonetically similar common-word anchors, adding them to the bias list without G2P.
Novitasari2026 reported 16.3% reduction in bias-word errors with zero added latency and no
model retraining, and the method is additive to any existing biasing technique. Evaluate on
gold-92 entity accuracy and confirm zero latency impact. Recommended task types:
post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>📊 <strong>Measure end-to-end latency of RECOVER and Ron2026 pipelines on
Rezolve infrastructure</strong> (S-0003-06)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../../tasks/t0003_literature_review_entity_stt/)

The survey found that latency estimates for both RECOVER (~+100-200ms) and Ron2026 (~550-650ms
total) are extrapolations from known Whisper Turbo inference speed and GPT-4o API latency, not
empirical measurements. Before confirming either method fits the 800ms p50 budget, measure
actual pipeline latency on Rezolve's production infrastructure at p50 and p95. This is a
prerequisite for any production deployment decision. If GPT-4o API latency exceeds the budget,
evaluate a local 7B model substitute for the LLM-Select step. Recommended task types:
latency-profiling, experiment-run.

</details>
