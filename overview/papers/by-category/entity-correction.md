# Papers: `entity-correction` (13)

13 papers across 1 year(s).

[Back to all papers](../README.md)

---

## 2026 (13)

<details>
<summary>📝 Beyond Prompting: Efficient and Robust Contextual Biasing for Speech
LLMs via Logit-Space Integration (LOGIC) — Wang, 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2601.15397` |
| **Authors** | Peidong Wang |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2601.15397` |
| **URL** | https://arxiv.org/abs/2601.15397 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2601.15397/summary.md) |

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
<summary>📝 TARQ: Tail-Aware Reconstruction Quantization for Rare-Word Robust
Automatic Speech Recognition — Wang et al., 2026</summary>

| Field | Value |
|---|---|
| **ID** | `10.48550_arXiv.2605.27808` |
| **Authors** | Xinyu Wang, Ziyu Zhao, Ke Bai, Silin Meng, Dongming Shen, Xiao-Wen Chang, Yixuan He |
| **Venue** | arXiv preprint (preprint) |
| **DOI** | `10.48550/arXiv.2605.27808` |
| **URL** | https://arxiv.org/abs/2605.27808 |
| **Date added** | 2026-06-23 |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |
| **Added by** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Full summary** | [`summary.md`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.27808/summary.md) |

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
