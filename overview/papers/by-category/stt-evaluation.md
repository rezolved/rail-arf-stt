# Papers: `stt-evaluation` (20)

20 papers across 5 year(s).

[Back to all papers](../README.md)

---

## 2026 (13)

<details>
<summary>📝 Back to Basics: Revisiting ASR in the Age of Voice Agents — Tay et al.,
2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.25727` |
| **Authors** | Geeyang Tay, Wentao Ma, Jaewon Lee, Yuzhi Tang, Daniel Lee, Weisu Yin, Dongming Shen, Silin Meng, Yi Zhu, Mu Li, Alex Smola |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2603.25727` |
| **URL** | https://arxiv.org/abs/2603.25727 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/summary.md) |

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
<summary>🏤 CLAR: CIF-Localized Alignment for Retrieval-Augmented Speech LLM-Based
Contextual ASR — Huang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.25460` |
| **Authors** | Shangkun Huang, Huan Wei, Yunzhang Chen |
| **Venue** | Interspeech 2026 (conference) |
| **DOI** | `10.48550/arXiv.2603.25460` |
| **URL** | https://arxiv.org/abs/2603.25460 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25460/summary.md) |

CLAR targets the representation dilution and alignment mismatches that limit
retrieval-augmented contextual ASR in speech LLMs. The paper provides a rigorous diagnosis of
why global-pooling encoders fail for short entities and why prompt injection creates alignment
ambiguity. The proposed solution — CIF-based monotonic alignment combined with length-aware
localized window matching — is principled and directly addresses both failure modes.

The dual-encoder system uses a Paraformer speech encoder with a CIF predictor alongside a
Chinese-RoBERTa text encoder, projecting into a shared embedding space. Multi-granularity
contrastive training (sentence-level + hotword-level) ensures the retriever can both retrieve
the right entity from the corpus and locate its acoustic position within the utterance.

Results on AISHELL-1-NE: **0.92% CER** and **2.78% B-WER**, state-of-the-art on this
benchmark, representing a **-9.14pp** B-WER improvement over SeACo-Paraformer. Hotword
Recall@1 of **97.03%** means nearly all relevant entities are retrieved before injection.

For Rezolve, CLAR's architecture is directly applicable to the Whisper Turbo + dynamic context
injection pipeline: the CIF localization principle can be applied to Whisper's encoder to
improve entity retrieval precision. The English adaptation requires training on English
entity-annotated data; the AISHELL-1-NE benchmark protocol (R1 hotwords with recall < 40%
under base ASR) closely mirrors the gold-92 challenge entities.

</details>

<details>
<summary>🏤 Contextual Biasing for ASR in Speech LLM with Common Word Cues and Bias
Word Position Prediction — Novitasari et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2604.12398` |
| **Authors** | Sashi Novitasari, Takashi Fukuda, Gakuto Kurata, George Saon |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2604.12398` |
| **URL** | https://arxiv.org/abs/2604.12398 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/summary.md) |

Novitasari et al. address the G2P dependency problem in phoneme-assisted contextual biasing
for speech LLMs. The practical motivation is that brand names, model numbers, and domain
jargon often have phonetically irregular spellings not covered by general-purpose G2P systems,
causing phoneme-assisted biasing to fail silently.

The solution uses common words with phonetically overlapping substrings as acoustic proxies
for rare bias targets, extracted from the speech LLM's encoder. An additional position
prediction objective jointly trains the model to locate where in the output sequence a bias
word will appear, improving recall and spatial attention.

Key result: **16.3% relative reduction** in bias word recognition errors on both in-domain and
out-of-domain evaluation, with no regression on non-bias words. The position prediction head
adds a further **+2.1pp** recall improvement beyond the cue method alone.

For Rezolve's Whisper Turbo + dynamic context injection pipeline, this paper is directly
relevant: the G2P-free approach matches the constraint that product names and SKUs resist
standard phonemization. The position prediction objective is applicable as a fine-tuning
modification. The gain (16.3%) is notable but smaller than retrieval-based methods like CLAR,
suggesting it would be most valuable as a complementary addition to a retrieval layer.

</details>

<details>
<summary>📝 Contextual Biasing for Streaming ASR via CTC-based Word Spotting — Tsai
et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.18222` |
| **Authors** | Kai-Chen Tsai, Tien-Hong Lo, Yun-Ting Sun, Berlin Chen |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.18222` |
| **URL** | https://arxiv.org/abs/2605.18222 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.18222/summary.md) |

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
<summary>📝 Contextual Earnings-22: A Speech Recognition Benchmark with Custom
Vocabulary in the Wild — Durmus et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2604.07354` |
| **Authors** | Berkin Durmus, Chen Cen, Eduardo Pacheco, Arda Okan, Atila Orhon |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2604.07354` |
| **URL** | https://arxiv.org/abs/2604.07354 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`entity-correction`](../../../meta/categories/entity-correction/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.07354/summary.md) |

Durmus et al. introduce Contextual Earnings-22, a standardized benchmark for evaluating STT
systems on custom vocabulary — specifically proper nouns including person names, company
names, and product names in earnings call recordings. The motivation is a demonstrable
mismatch between academic benchmark WER (where top systems cluster tightly) and real-world
transcript utility in domain-heavy applications. The authors argue that contextual
conditioning on a custom vocabulary list is the primary differentiator, and that no prior
public benchmark provides the structure to measure it rigorously across competing systems.

The benchmark is built from 55 earnings call recordings in the Earnings-22 corpus. An
LLM-based NER pass (GPT-5) extracts keyword candidates; forced alignment clips 15-second audio
windows around keyword mentions; and manual review corrects transcript artifacts in all 760
clips, achieving **98.7%** artifact-free quality with **29.5%** of clips requiring
corrections. The benchmark tests two context regimes — local (precise, no distractors) and
global (full call inventory with distractors) — and uses both WER and keyword
Precision/Recall/F-score for evaluation. Six systems are benchmarked: three commercial
keyword-prompting APIs, one open-source Whisper, and two CTC-WS keyword-boosting
configurations.

All six systems improve keyword F-score under context conditioning, validating that both
prompting and boosting approaches help. However, WER changes are inconsistent — OpenAI
Whisper-1's WER worsens under context despite better keyword F-score — demonstrating that the
two metrics capture different aspects of quality and should both be reported. Global context
stresses precision ( distractor-induced false insertions), while local context primarily
improves recall. Keyword boosting and keyword prompting reach comparable accuracy when scaled
to large models. Failure modes include hallucinations, partial outputs, and language switching
when prompts containing non-English-sounding names perturb decoding.

For this project, Contextual Earnings-22 is a methodological reference for both evaluation
design and entity correction strategy. The paper validates keyword-centric evaluation as a
necessary supplement to WER, directly aligned with Rezolve's entity accuracy goal on the
gold-92 benchmark. The dual-regime design maps onto Rezolve's scenario where a global entity
vocabulary (all brands, products, investor-relations terms) will contain distractors for any
given utterance, and precision loss from false insertions is a direct threat to the
wrong-action rate target of less than 2%. The benchmark's construction pipeline is a
replicable recipe for extending the gold-92 benchmark, and the comparison of prompting vs.
boosting baselines provides concrete references for the entity correction experiments planned
in this project.

</details>

<details>
<summary>📝 Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical Speech
Applications — Kudlur et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2602.12241` |
| **Authors** | Manjunath Kudlur, Evan King, James Wang, Pete Warden |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2602.12241` |
| **URL** | https://arxiv.org/abs/2602.12241 |
| **Date added** | 2026-06-23 |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12241/summary.md) |

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
<summary>🏤 RECOVER: Robust Entity Correction via Agentic Orchestration of Hypothesis
Variants for Evidence-based Recovery — Kumar & Sachdeva, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2603.16411` |
| **Authors** | Abhishek Kumar, Aashraya Sachdeva |
| **Venue** | Interspeech 2026 (conference) |
| **DOI** | `10.48550/arXiv.2603.16411` |
| **URL** | https://arxiv.org/abs/2603.16411 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.16411/summary.md) |

Kumar and Sachdeva address the entity recovery gap in LLM post-correction by exploiting the
N-best hypothesis diversity from beam search. The core finding is that the 1-best hypothesis
frequently omits rare entities that appear in hypotheses ranked 2-5, and that collecting this
diversity significantly improves entity recovery when a smart selection strategy is applied.

RECOVER evaluates four hypothesis selection strategies from trivial (1-Best) to LLM-based
(LLM-Select with GPT-4o), measuring entity-phrase WER (E-WER) and recall on five diverse
English domains. LLM-Select is the most robust strategy, achieving the best or near-best E-WER
on 4 of 5 datasets.

Key results: **8-46% relative E-WER reductions** and **up to +22pp entity recall** across
datasets. Earnings-21 (closest to Rezolve's entity-rich domain) sees **33-35% relative** E-WER
reduction. ROVER Ensemble degrades on noisy domains — LLM-based selection is required for
reliable cross-domain performance.

For Rezolve, RECOVER's multi-hypothesis approach is immediately applicable to the production
Whisper Turbo pipeline: collecting beam search top-5 is free, and the LLM-Select + correction
approach adds a post-processing layer with no model retraining. The main obstacle is latency:
GPT-4o adds 200-500ms per utterance. A distilled local corrector (7B class) would be needed to
meet the 800ms p50 target.

</details>

<details>
<summary>📝 Retrieval-Augmented Self-Taught Reasoning Model with Adaptive
Chain-of-Thought for ASR Named Entity Correction — An et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2602.12287` |
| **Authors** | Junjie An, Jingguang Tian, Tianyi Wang, Yu Gao, Xiaofeng Mou, Yi Xu |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2602.12287` |
| **URL** | https://arxiv.org/abs/2602.12287 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12287/summary.md) |

An et al. propose RASTAR, a two-stage pipeline for named entity correction in ASR. The first
stage identifies entity spans using a BERT-based masked language model (RLM) trained on the
distinction between correct and ASR-corrupted entity forms. The second stage retrieves
candidate entities phonetically and applies an adaptive chain-of-thought reasoning model
(A-STAR) to select and substitute the correct entity.

A-STAR's difficulty-adaptive mechanism classifies each correction instance as Simple,
Challenging, or Formidable based on phonetic similarity, then applies proportional
chain-of-thought depth. DPO training on synthetic difficulty-stratified pairs eliminates
manual annotation of reasoning chains.

Key results: **17.96%** and **34.42%** relative NE-CER reduction on AISHELL-1 and the harder
Homophone test respectively. Token reduction of 30-40% vs. full CoT. RLM achieves **94.18%
F1** on standard NE identification and **83.91%** on phonetically confusing cases.

For Rezolve, A-STAR's adaptive reasoning depth is the most attractive property: it reduces
inference cost for easy cases while preserving accuracy on hard ones (homophones). The English
adaptation requires training on English brand-name ASR data, but the framework is
architecturally straightforward. The Homophone results are directly relevant to ecommerce
brand names that sound like common English words.

</details>

<details>
<summary>🏤 RLBR: Reinforcement Learning with Biasing Rewards for Contextual Speech
Large Language Models — Ren et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.13409` |
| **Authors** | Bo Ren, Ruchao Fan, Yelong Shen, Weizhu Chen, Jinyu Li |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2601.13409` |
| **URL** | https://arxiv.org/abs/2601.13409 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.13409/summary.md) |

Ren et al. address the SFT misalignment for contextual biasing: standard supervised
fine-tuning gives equal gradient weight to common function words and rare domain entities,
even though the entire value of contextual biasing lies in the rare entity accuracy. RLBR
corrects this by using a RL reward function that multiplies the reward for correct bias word
transcription by alpha=5, focusing the policy gradient where it matters.

The GRPO-based RL training generates 8 hypothesis samples per utterance and scores them with
the bias-word-preferred reward. A reference-aware augmentation prevents mode collapse by
ensuring the exploration space covers the correct entity handling paths.

Results on LibriSpeech: B-WER of **0.59%/2.11%** at 100 bias words, **1.09%/3.24%** at 500
words, and **1.36%/4.04%** at 1000 words (test-clean/test-other). These represent
state-of-the-art biased WERs among methods published in Jan-Jun 2026 for English ASR.

For Rezolve, RLBR requires fine-tuning the production ASR model (Whisper Turbo or equivalent)
on ecommerce entity data — a higher-investment approach than post-processing methods. The
reward shaping principle is directly transferable: any RL-based ASR fine-tuning for ecommerce
should weight brand/product/SKU tokens at alpha=5×. The reference-aware exploration mechanism
addresses a practical training stability concern that would arise when fine-tuning on a small
(~1000 utterance) ecommerce entity dataset.

</details>

<details>
<summary>🏤 Towards Deep Contextual Reasoning from Broad Descriptions for ASR with
Speech-LLM via Metadata-Driven Reasoning Chains — Poncelet & hamme, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2606.10838` |
| **Authors** | Jakob Poncelet, Hugo Van hamme |
| **Venue** | Interspeech 2026 (conference) |
| **DOI** | `10.48550/arXiv.2606.10838` |
| **URL** | https://arxiv.org/abs/2606.10838 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2606.10838/summary.md) |

Poncelet and Van hamme train a speech-LLM to reason from broad contextual descriptions using
chain-of-thought fine-tuning. The motivation is that keyword lists cannot capture the semantic
richness of context available in real applications (video metadata, session context). The
training data is constructed automatically: GPT-4o generates reasoning chain explanations
pairing ASR errors with video metadata, creating 400 hours of reasoning-augmented training
data.

The model is fine-tuned to produce initial transcript, reasoning, and corrected output. Four
speech-LLM architectures are tested on the M3AV YouTube test set. Results: overall WER
improves from **9.4% to 9.3%**, rare word WER from **24.0% to 23.1%**, named entity WER from
**23.9% to 23.3%** — modest but consistent improvements across all architectures.

The improvements are smaller in absolute terms than keyword-biasing methods but complement
them: reasoning over context semantics catches entity corrections that keyword matching misses
(e.g., inferring a brand from product category context rather than requiring the exact brand
name in the bias list).

For Rezolve, the session metadata pipeline is particularly relevant: product categories,
search queries, and cart contents provide natural broad-description context for ecommerce
voice sessions. The automated training data construction from session logs and production
transcripts could be applied to the gold-92 domain without human annotation overhead.

</details>

<details>
<summary>📝 Towards Human-Like Interactive Speech Recognition With Agentic Correction
and Semantic Evaluation — Jiang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.29430` |
| **Authors** | Zixuan Jiang, Yanqiao Zhu, Peng Wang, Qinyuan Chen, Xipeng Qiu, Kai Yu |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.29430` |
| **URL** | https://arxiv.org/abs/2605.29430 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`confidence-routing`](../../../meta/categories/confidence-routing/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.29430/summary.md) |

Jiang et al. reframe ASR as a closed-loop interactive task and demonstrate that semantic
errors (wrong intent, wrong entity) are far more correctable than surface token errors. The
motivating observation is that WER fails to distinguish high-value errors (brand names,
quantities) from low-value ones (function words), understating how correctable
business-critical mistakes actually are.

The Agentic ASR framework adds semantic correction, intent routing, and reasoning-based
editing on top of a standard ASR front-end. The S2ER metric provides a semantically meaningful
evaluation via LLM judging with 0.83-0.90 human correlation. An Interactive Simulation System
enables automated multi-turn evaluation.

Key results: S2ER collapses from **~20-28% to <2%** across 10 correction loops while WER
decreases only from ~12% to ~10%. Named entity error rates improve from ~2% to <1% on
specialized NER test sets. The dramatic S2ER vs. WER divergence confirms that semantic errors
concentrate in a small set of critical tokens.

For Rezolve, the primary takeaway is the S2ER metric: adopting it for gold-92 evaluation would
more accurately measure wrong-action rate than WER. The multi-turn correction approach is
appealing but requires latency budgeting — at most 1-2 correction turns are feasible within
800ms. The heavy Qwen3-32B backend requires distillation for production.

</details>

<details>
<summary>🏤 Towards Robust Dysarthric Speech Recognition: LLM-Agent Post-ASR
Correction Beyond WER — Zheng et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.21347` |
| **Authors** | Xiuwen Zheng, Sixun Dong, Bornali Phukon, Mark Hasegawa-Johnson, Chang D. Yoo |
| **Venue** | ICASSP 2026 (conference) |
| **DOI** | `10.48550/arXiv.2601.21347` |
| **URL** | https://arxiv.org/abs/2601.21347 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.21347/summary.md) |

Zheng et al. address the disconnect between WER and actual downstream accuracy for ASR
post-correction. Standard WER counts all token substitutions equally, regardless of whether
the error affects a function word or a business-critical entity name. The paper frames
post-correction as a selective editing task rather than a full rewrite, motivated by the
observation that LLM hallucination replaces rare domain terms with plausible but wrong
alternatives.

The Judge-Editor architecture takes k=5 ASR hypotheses and uses span-level agreement as a
proxy for transcription confidence. High-agreement spans are preserved unchanged;
low-agreement spans are rewritten by an LLM guided by structured prompts. The SAP-Hypo5
benchmark, introduced alongside the method, provides a reproducible evaluation environment
with five hypotheses per utterance and multi-metric scoring.

Key results: **14.51% WER reduction**, **+7.59 pp MENLI**, and **+7.66 pp Slot Micro F1** on
difficult samples. The selective editing mechanism reduces hallucinations by ~30% compared to
unconstrained LLM rewriting, practically important when rare entities must be preserved.

For Rezolve's voice commerce pipeline, the takeaways are: (a) Slot Micro F1 on brand/product
spans is a better proxy for wrong-action rate than WER; (b) an N-best post-correction agent
using multiple ASR hypotheses is a viable low-latency add-on avoiding model retraining; and
(c) domain fine-tuning on ecommerce entity examples would materially improve entity correction
accuracy.

</details>

<details>
<summary>📝 Whisper: Courtside Edition — Multi-Agent LLM Pipeline for Domain-Specific
ASR via Context Generation — Ron et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2602.18966` |
| **Authors** | Yonathan Ron, Shiri Gilboa, Tammuz Dubnov |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2602.18966` |
| **URL** | https://arxiv.org/abs/2602.18966 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.18966/summary.md) |

Ron et al. demonstrate that Whisper's initial_prompt parameter can be systematically exploited
for domain-specific entity recognition without model retraining. A six-agent LLM pipeline
extracts domain signals from Whisper's preliminary transcript and constructs a compact prompt
that guides the decoder toward rare entity recognition.

The pipeline processes topic classification, NER with fuzzy matching, jargon extraction, and a
decision filter that prevents over-prompting. Evaluation on 421 NBA basketball commentary
segments (dense proper nouns and technical jargon) shows a **17.0% relative WER reduction**
(0.217 → 0.180, p < 0.001), improving **40.1%** of segments while degrading only **7.1%**.

The approach is architecturally straightforward and requires only Whisper API access. The
decision filter is the key practical contribution: it prevents Whisper's 224-token context
window from being filled with low-confidence candidates that degrade performance. Error
analysis confirms that the gains are entity-driven (35% names, 28% jargon).

For Rezolve, this approach is the most immediately deployable: it leverages the existing
Whisper Turbo checkpoint and adds an LLM-based prompt generation step with no model training.
The NBA domain closely parallels ecommerce in entity density and proper noun challenges. The
main engineering work is tuning the fuzzy matching threshold for Rezolve's brand/product
vocabulary and ensuring the multi-agent latency fits within the 800ms p50 budget.

</details>

## 2025 (3)

<details>
<summary>🏤 Calm-Whisper: Reduce Whisper Hallucination On Non-Speech By Calming Crazy
Heads Down — Wang et al., 2025</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2505.12969` |
| **Authors** | Yingzhi Wang, Anas Alhmoud, Saad Alsahly, Muhammad Alqurishi, Mirco Ravanelli |
| **Venue** | Interspeech 2025 (conference) |
| **DOI** | `10.48550/arXiv.2505.12969` |
| **URL** | https://arxiv.org/abs/2505.12969 |
| **Date added** | 2026-06-29 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/paper/10.48550_arXiv.2505.12969/summary.md) |

This paper targets a severe and practically important failure mode of Whisper-large-v3:
hallucination on non-speech audio. With a baseline hallucination rate of **99.97%** on
UrbanSound8K — meaning virtually every non-speech clip produces fabricated text — Whisper is
unsafe to deploy in production pipelines that handle mixed-content audio without external VAD
safeguards. The authors set out to eliminate this hallucination from within the model, without
adding inference-time complexity or external pre/post-processing.

The technical approach proceeds in two stages. First, a head-wise masking study isolates which
of Whisper-large-v3's 20 decoder self-attention heads contributes most to hallucination. Three
heads (#1, #6, #11) are identified as responsible for over **75%** of the problem. Second,
only the weights of those three heads are fine-tuned on 105 hours of pure non-speech audio
(AudioSet, DEMAND, MUSAN) paired with blank target labels. All other weights remain frozen,
preventing regression on standard speech transcription tasks.

The results are striking: the best model (5-epoch fine-tune) reduces hallucination on
UrbanSound8K from **99.97%** to **15.51%** — an **84.5%** relative reduction — while WER on
LibriSpeech test-clean rises by only **+0.07%** (from **2.12%** to **2.19%**). Long
hallucinations exceeding 5 tokens drop from **742** instances to **91**. The paper also
demonstrates that broader fine-tuning (full decoder) completely destroys transcription quality
(**100% WER**), confirming that surgical head-level targeting is essential. The Calm-Whisper
hallucination rate of **15.51%** approaches the **13.52%** of Conformer-CTC-large — a
CTC-based model fundamentally less prone to autoregressive hallucination — validating that the
gap can be largely closed through targeted fine-tuning.

For this project, Calm-Whisper is directly relevant to the robustness goal of evaluating
Whisper-class models on short production audio clips from Rezolve voice commerce sessions.
Short clips, silences, and background noise are common in that setting, and the **99.97%**
baseline hallucination rate means any such segment would produce spurious transcripts
corrupting downstream entity recognition and intent parsing. Adopting the Calm-Whisper
fine-tuning recipe — or applying an equivalent head-attribution study to Granite STT or
another Whisper-variant — could be a low-cost, high-impact robustness improvement for the
Rezolve pipeline, with negligible WER regression cost.

</details>

<details>
<summary>📝 Granite-speech: open-source speech-aware LLMs with strong English ASR
capabilities — Saon et al., 2025</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2505.08699` |
| **Authors** | George Saon, Avihu Dekel, Alexander Brooks, Tohru Nagano, Abraham Daniels, Aharon Satt, Ashish Mittal, Brian Kingsbury, David Haws, Edmilson Morais, Gakuto Kurata, Hagai Aronowitz, Ibrahim Ibrahim, Jeff Kuo, Kate Soule, Luis Lastras, Masayuki Suzuki, Ron Hoory, Samuel Thomas, Sashi Novitasari, Takashi Fukuda, Vishal Sunder, Xiaodong Cui, Zvi Kons |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2505.08699` |
| **URL** | https://arxiv.org/abs/2505.08699 |
| **Date added** | 2026-06-29 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Added by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/paper/10.48550_arXiv.2505.08699/summary.md) |

Saon et al. (IBM Research, 2025) introduce Granite-speech-3.3, a family of open-source
speech-aware LLMs in 2B and 8B parameter variants, designed primarily for English ASR. The
central research question is whether compact models trained exclusively on publicly licensed
audio corpora (~76K hours Apache 2.0 compatible data) can match or surpass models trained on
orders of magnitude more proprietary data. The motivation is both scientific — advancing
open-source speech models — and practical, enabling commercial deployment without licensing
barriers.

The architecture integrates three components trained sequentially: a 10-layer conformer CTC
encoder with block attention and self-conditioned CTC (1.5M updates, 275M parameters), a
windowed Q-former speech modality adapter achieving 10x total acoustic compression (660K
updates, 32 H100 GPUs), and LoRA adapters (rank 64) applied to all LLM attention layers. The
design supports dual-mode inference: the same model weights serve as the base
granite-3.3-instruct text LLM (LoRA off) or as a speech-aware model (encoder + Q-former + LoRA
active) depending on whether an `<|audio|>` token appears in the prompt. Key training
innovations include character-level CTC tokenization, balanced corpus sampling with α=0.6, and
ensemble-based MT filtering for synthetic AST data that retains under 50% of examples but
improves BLEU by more than 10 points.

The 8B model achieves the lowest WER among all sub-8B parameter models on 7 of 9 English ASR
benchmarks, including **1.5% WER** on LibriSpeech clean, **3.0%** on LibriSpeech other,
**9.2%** on AMI IHM, **26.1%** on AMI SDM, and **5.8%** on VoxPopuli — beating Whisper Large
v3, Gemini 2.0 Flash, Qwen2-Audio, and Phi-4-mm. The 2B model is competitive, especially on
AMI SDM (**26.7% WER**), suggesting robustness to adverse acoustic conditions at smaller
scale. Ablations confirm that character-level CTC tokenization outperforms BPE variants after
joint LLM training, and the windowed Q-former outperforms MLP and cross-attention projectors.

For the Rezolve STT project, Granite-speech-3.3 is a high-priority candidate for the gold-92
benchmark evaluation. Its strong performance on conversational and meeting corpora (AMI,
VoxPopuli) that share acoustic characteristics with Rezolve production call-center audio makes
it directly relevant for entity accuracy benchmarking. The dual-mode design is particularly
attractive: a single model instance could handle both transcription and entity-aware
post-correction, potentially collapsing the two-step Deepgram + LLM correction pipeline and
reducing voice-to-action latency below the 800 ms p50 budget. The Apache 2.0 license removes
all commercial deployment barriers, and the planned future work on contextual biasing aligns
directly with the Rezolve entity boosting objective.

</details>

<details>
<summary>🏤 Investigation of Whisper ASR Hallucinations Induced by Non-Speech Audio
— Barański et al., 2025</summary>

| Field | Value |
|---|---|
| **ID** | `10.1109_ICASSP49660.2025.10890105` |
| **Authors** | Mateusz Barański, Jan Jasiński, Julitta Bartolewska, Stanisław Kacprzak, Marcin Witkowski, Konrad Kowalczyk |
| **Venue** | ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (conference) |
| **DOI** | `10.1109/ICASSP49660.2025.10890105` |
| **URL** | https://arxiv.org/abs/2501.11378 |
| **Date added** | 2026-06-29 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/paper/10.1109_ICASSP49660.2025.10890105/summary.md) |

Barański et al. investigate a well-known but under-characterised failure mode of Whisper ASR:
the generation of hallucinated text when the input audio contains no speech. Rather than
relying on imprecise phonetic similarity measures to define hallucinations, the paper
constructs a controlled setting — running Whisper exclusively on verified non-speech audio —
where every output is definitionally a hallucination. This clean experimental design enables a
large-scale empirical characterisation across 301,317 audio files from four public sound
datasets, with additional experiments on speech augmented with non-speech sounds.

The methodology proceeds through six experiment groups. Experiment 1 collects an exhaustive
hallucination list from non-speech audio; Experiments 2–3 examine how clip duration and sound
category affect hallucination rate. The authors construct the Bag of Hallucinations (BoH) by
filtering the raw list using an n-gram language model (log probability < −10) and a frequency
threshold (> 4 occurrences). Experiments 4–5 extend to augmented speech with different noise
durations and positions. Experiment 6 evaluates Whisper's internal parameters (beam size,
hallucination silence threshold). Experiment 7 benchmarks full mitigation strategies
end-to-end using WER on held-out Freesound material.

The headline results show hallucinations are surprisingly predictable: **40.3%** of non-speech
clips trigger a hallucination, but **35%** of all hallucinations are just two strings. The
30-second Whisper segment boundary is identified as a primary trigger for elevated
hallucination rates. Among mitigation strategies, SileroVAD + delooping + BoH achieves the
best WER of **6.5%** (non-overlap) versus a raw baseline of **104.8%**, while BoH alone
(without VAD) achieves **17.1% WER** — a strong result for a purely text-side, model-agnostic
filter.

For this project (t0014, Granite short-clip robustness), the paper is directly relevant at two
levels. First, the hallucination patterns it documents for Whisper provide a benchmark against
which Granite's behaviour on short, potentially noisy clips can be compared — if Granite
exhibits lower hallucination rates on non-speech clips, that is a concrete robustness
advantage. Second, the BoH post-processing pipeline is immediately applicable as a defensive
layer for the Rezolve STT harness regardless of which model is used, offering measurable WER
improvement with no model changes.

</details>

## 2024 (1)

<details>
<summary>🏤 WhisperNER: Unified Open Named Entity and Speech Recognition — Ayache
et al., 2024</summary>

| Field | Value |
|---|---|
| **ID** | `10.1109_ASRU65441.2025.11434797` |
| **Authors** | Gil Ayache, Menachem Pirchi, Aviv Navon, Aviv Shamsian, Gill Hetz, Joseph Keshet |
| **Venue** | 2025 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU) (conference) |
| **DOI** | `10.1109/ASRU65441.2025.11434797` |
| **URL** | https://arxiv.org/abs/2409.08107 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/), [`entity-correction`](../../../meta/categories/entity-correction/) |
| **Added by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0002_baseline_evaluation/assets/paper/10.1109_ASRU65441.2025.11434797/summary.md) |

Ayache et al. propose WhisperNER to solve error propagation in pipeline-based speech-NLP
systems. In standard ASR+NER pipelines, transcription errors in the first stage degrade entity
recognition in the second stage. The paper also identifies a key gap: existing end-to- end
NER-from-speech models support only fixed, closed entity sets, limiting their applicability to
dynamic or domain-specific scenarios where entity vocabularies change over time.

WhisperNER extends Whisper large-v2 by conditioning the decoder on a user-supplied list of
entity type labels at inference time. The model is trained on 350K samples from the NuNER
synthetic dataset augmented with TTS-generated audio, spanning 1.8M unique entity types.
Training incorporates negative entity sampling (~66% negative types per example) and entity
type dropout to reduce hallucination. Only the decoder is updated; the Whisper encoder is
frozen. A scalar logit bias on the entity start token provides inference-time precision-recall
control without retraining.

On zero-shot open-type NER, WhisperNER achieves **53.53 F1** averaged across VoxPopuli-NER,
LibriSpeech-NER, and Fleurs-NER, outperforming the best pipeline baseline (GLiNER at **52.29
F1**) while adding no parameters over Whisper large-v2. Pipeline baselines add 248M-459M NLP
parameters on top of the same Whisper backbone. On supervised fine- tuning, WhisperNER reaches
**81.35 F1** on MIT-Movie at **2.31% WER**, outperforming all baselines on both metrics
simultaneously. The WER cost of NER integration is modest at approximately +0.9 pp on
VoxPopuli.

For the Rezolve STT project, WhisperNER is the most directly relevant paper in the corpus: it
directly targets the entity accuracy problem by integrating NER into ASR, uses the same
Whisper architecture targeted for fine-tuning in this project, and its open-type prompt
interface allows Rezolve-specific entities to be targeted without retraining. The logit-bias
precision-recall control maps onto the confidence-routing framework. The main open question is
performance on gold-92 (accented English production audio), given the known acoustic mismatch
from synthetic TTS training data. A baseline evaluation of the released WhisperNER model on
gold-92 should be part of t0002_baseline_evaluation.

</details>

## 2022 (1)

<details>
<summary>📝 Robust Speech Recognition via Large-Scale Weak Supervision — Radford
et al., 2022</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2212.04356` |
| **Authors** | Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2212.04356` |
| **URL** | https://arxiv.org/abs/2212.04356 |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`whisper-finetuning`](../../../meta/categories/whisper-finetuning/) |
| **Added by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0002_baseline_evaluation/assets/paper/10.48550_arXiv.2212.04356/summary.md) |

Radford et al. present Whisper, a speech recognition system trained on 680,000 hours of weakly
supervised audio-transcript pairs scraped from the internet. The central research question is
whether scaling weak supervision — using noisy but abundant internet data rather than
expensive human-validated corpora — can match or surpass fully supervised approaches while
achieving substantially better real-world robustness. The work is motivated by the observation
that prior state-of-the-art models trained on LibriSpeech are effectively measuring
in-distribution generalization, not the out-of-distribution robustness needed for production
deployment.

The approach uses a standard encoder-decoder Transformer trained end-to-end on 30-second audio
segments with a multitask format: all tasks (transcription, translation, language ID, VAD,
timestamp alignment) are encoded as decoder token sequences, allowing a single model to
replace multiple pipeline stages. Training uses AdamW with linear LR decay for approximately
2-3 passes over the dataset without data augmentation, relying on dataset diversity for
robustness. Five model sizes are released (39M–1.55B parameters). A text normalizer and
long-form decoding heuristics are developed as essential practical components.

The key findings are that Whisper Large V2 achieves **55.2%** average relative error reduction
over the best comparable supervised model on 13 OOD datasets despite similar LibriSpeech
performance, and its transcription quality approaches professional human transcribers on
Kincaid46 (Whisper **8.81%** WER vs. best human service **7.61%**). For translation, Whisper
achieves **29.1 BLEU** on CoVoST2 zero-shot, a new state of the art. A strong data scaling law
is identified: WER halves for every 16× increase in per-language training hours (log-log R² =
0.83 on Fleurs). Multitask and multilingual training provides positive transfer at large model
sizes.

For this project, Whisper Large V2 is the open-source baseline to benchmark against production
Deepgram on gold-92. The paper directly supports the research roadmap: fine-tuning Whisper on
Rezolve production audio is the most direct path to improving entity accuracy on
investor-relations and ecommerce terms. The custom vocabulary prompting mechanism is
immediately actionable for injecting brand names and product entities. The model size family
gives a latency-accuracy trade-off ladder to explore within the 800 ms p50 constraint.

</details>

## 2020 (2)

<details>
<summary>🏤 Statistical Testing on ASR Performance via Blockwise Bootstrap — Liu
& Peng, 2020</summary>

| Field | Value |
|---|---|
| **ID** | `10.21437_Interspeech.2020-1338` |
| **Authors** | Zhe Liu, Fuchun Peng |
| **Venue** | Interspeech 2020 (conference) |
| **DOI** | `10.21437/Interspeech.2020-1338` |
| **URL** | https://www.isca-archive.org/interspeech_2020/liu20c_interspeech.html |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |
| **Added by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0002_baseline_evaluation/assets/paper/10.21437_Interspeech.2020-1338/summary.md) |

Liu and Peng (2020) address a specific but important methodological gap in ASR evaluation: the
standard bootstrap procedure for WER confidence intervals assumes utterance-level
independence, but real evaluation sets almost always contain correlated utterances from the
same speakers, sessions, or topics. The paper proposes blockwise bootstrap, which resamples
groups of correlated utterances as atomic units, preserving within-group dependence while
treating groups as independent. The motivation is to prevent systematically overconfident
claims of ASR improvement that arise when ordinary bootstrap artificially narrows confidence
intervals.

The method partitions utterances into K non-overlapping blocks using existing evaluation
metadata (e.g., speaker IDs), then resamples blocks with replacement B = 1,000 times. The 95%
CI for ΔW is the empirical (2.5%, 97.5%) percentile range of the B bootstrap statistics. The
authors prove an L2-consistency theorem showing the variance estimator converges to the true
variance as both K and block size grow with n. Simulation experiments with n = 3,000
utterances and correlation ρ up to 0.4 confirm that ordinary bootstrap coverage collapses to
**41.2%** while blockwise bootstrap consistently stays near **95%**.

Experiments on two real datasets confirm the failure of ordinary bootstrap in practice:
blockwise CIs are **1.5–2.3x** wider than ordinary bootstrap CIs. On the Conversational Speech
dataset (13,987 utterances, 235 blocks), the standard error increases from **0.074%** to
**0.116%**; on AMI Meeting (25,741 utterances, 135 blocks), from **0.067%** to **0.153%**.
Neither method changes the sign of the estimated WER difference, but ordinary bootstrap
understates uncertainty by a large margin, risking false-positive significance results.

For this project, the finding is directly actionable. The gold-92 benchmark likely contains
multiple utterances per speaker from Rezolve production sessions, creating exactly the within-
speaker correlation the paper diagnoses. The success criterion — beating Deepgram with BCa
bootstrap p < 0.05 on n = 93 paired samples — should use blockwise or BCa bootstrap with
speaker-level blocks rather than ordinary bootstrap. The implementation overhead is minimal:
only speaker IDs are needed as the block key.

</details>

<details>
<summary>🏤 Where are we in Named Entity Recognition from Speech? — Caubrière et
al., 2020</summary>

| Field | Value |
|---|---|
| **ID** | `no-doi_Caubriere2020_ner-from-speech-survey` |
| **Authors** | Antoine Caubrière, Sophie Rosset, Yannick Estève, Antoine Laurent, Emmanuel Morin |
| **Venue** | Proceedings of the 12th Language Resources and Evaluation Conference (LREC 2020) (conference) |
| **DOI** | — |
| **URL** | https://aclanthology.org/2020.lrec-1.556/ |
| **Date added** | 2026-06-23 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`entity-correction`](../../../meta/categories/entity-correction/) |
| **Added by** | [`t0002_baseline_evaluation`](../../../overview/tasks/task_pages/t0002_baseline_evaluation.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0002_baseline_evaluation/assets/paper/no-doi_Caubriere2020_ner-from-speech-survey/summary.md) |

Caubrière et al. (2020) revisit named entity recognition from speech using the French ETAPE
benchmark, eight years after the original evaluation campaign established the prior state of
the art. Their central question is how much the combination of modern neural ASR (Kaldi chain
model, 16.5% WER) and NER systems (bLSTM-CRF) improves entity extraction from spoken French
compared to 2012-era HMM-GMM and CRF baselines. The paper is motivated by the complete absence
of new published results on this tree-structured NER-from-speech benchmark since 2012, despite
major advances in both component technologies.

The methodology centers on two contributions. For pipeline systems, the authors introduce a
3-pass decomposition that splits the Quaero-style BIO annotation tree into three hierarchical
levels, each trained as a separate sequence labeler with cascading predictions, reducing the
tag space from ~1,690 to manageable subsets of 96, 187, and 57 tags. For end-to-end systems,
they adapt DeepSpeech 2 with Curriculum-based Transfer Learning, encoding NE tags as special
characters in CTC output and training progressively from ASR to NE-types to full structured
annotation. All systems are evaluated on the official ETAPE test set using Slot Error Rate
(SER), which jointly penalizes span boundary errors and entity type errors with calibrated
weights.

The best pipeline system (3-pass bLSTM-CRF + updated ASR) achieves **51.1% SER**, a **13.8%
relative improvement** over the 2012 ETAPE state of the art (**59.3% SER**). The best E2E
system reaches **56.9% SER**, showing a 4% relative improvement over the baseline but
remaining **10.2% relative** behind the pipeline. Improved ASR alone — reducing WER from 21.8%
to 16.5% — contributed 4.4–5.0 SER points across all NER configurations.

For this project, the paper is most valuable as a methodological reference for entity-level
evaluation metrics in STT systems. The SER/EER decomposition (boundary errors vs. type errors,
weighted separately) directly informs the entity accuracy metric design for the gold-92
benchmark. The finding that ASR quality improvements translate proportionally into downstream
entity accuracy gains supports prioritizing Whisper Large v3 over Deepgram as the ASR backbone
before investing in post-correction layers. The pipeline-beats-E2E result also validates the
two-stage architecture (STT \+ entity post-correction) planned for this project over a
hypothetical joint model.

</details>
