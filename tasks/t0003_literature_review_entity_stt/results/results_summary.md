---
task_id: "t0003_literature_review_entity_stt"
date: "2026-06-23"
---
# Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)

## Summary

Systematic literature review of Jan–Jun 2026 publications on entity-aware STT. **15 paper assets**
were created covering contextual biasing, entity-aware ASR architectures, and LLM post-correction.
The top no-retraining candidates for prototyping on gold-92 are **RECOVER** (33–35% relative E-WER
reduction, Earnings-21) and **Ron2026** (17% relative WER reduction via Whisper `initial_prompt`).
Shallow fusion has effectively no 2026 literature — documented as a gap, not a search failure.

## Metrics

* **Paper assets created**: **15** (all passing `verify_paper_asset.py`, 0 errors)
* **Databases searched**: **9** (arXiv, Semantic Scholar, ACL Anthology, ICASSP 2026, Interspeech
  2026, Papers With Code, AssemblyAI, Emergent Mind, Google web search)
* **Search queries run**: **14** (6 required keyword combinations + 8 gap-filling queries)
* **Best no-retraining entity accuracy gain (RECOVER)**: **33–35% relative E-WER reduction** on
  Earnings-21 domain, ~+100–200ms latency overhead
* **Best no-retraining WER gain (Ron2026)**: **17% relative WER reduction** on entity-dense NBA
  commentary, estimated ~550–650ms total pipeline latency
* **Lowest B-WER in survey (RLBR, requires retraining)**: **0.59%** at 100 bias words on LibriSpeech
  test-clean

## Verification

* `verify_research_papers.py t0003_literature_review_entity_stt` — PASSED (0 errors, 0 warnings)
* `verify_research_internet.py t0003_literature_review_entity_stt` — PASSED (0 errors, 0 warnings)
* `verify_research_code.py t0003_literature_review_entity_stt` — PASSED (0 errors, 0 warnings)
* `verify_plan.py t0003_literature_review_entity_stt` — PASSED (0 errors, 1 warning: PL-W009
  documented)
* `verify_paper_asset.py` — PASSED for all 15 paper assets (15/15, 0 errors)

* * *

## Methodology

### Research Question

What are the most effective techniques published between January and June 2026 for improving STT
accuracy on domain-specific named entities (brand names, product names, SKUs), and which of these
are compatible with a sub-800 ms voice-to-action latency requirement in an English ecommerce voice
AI context?

### Databases Queried

* arXiv (cs.CL, cs.SD, eess.AS)
* Semantic Scholar
* ACL Anthology
* ICASSP 2026 proceedings
* Interspeech 2026 proceedings
* Papers With Code
* AssemblyAI benchmark platform
* Emergent Mind
* Google web search (gap-filling)

### Keyword Combinations

All six required combinations were run:

1. `contextual biasing ASR named entity 2026`
2. `entity-aware speech recognition ecommerce 2026`
3. `shallow fusion ASR latency 2026`
4. `LLM post-correction ASR named entity 2026`
5. `domain-specific ASR brand product 2026`
6. `Whisper fine-tuning named entity ecommerce 2026`

Eight additional gap-filling and snowball queries were run (see `results/search_log.md` for the full
log with result counts and selected papers per query).

### Date Range

January 1, 2026 to June 30, 2026 for primary papers. Papers outside this range are included only as
background references when directly cited by 2026 papers or when addressing open gaps identified
during research.

### Inclusion Criteria

* Papers reporting entity-level accuracy, entity WER (E-WER), or bias-word WER (B-WER)
* Papers with latency measurements or streaming-compatible architectures
* Ecommerce, voice assistant, or general conversational domain
* English ASR or multilingual with English results reported

### Exclusion Criteria

* Papers published before 2026 (noted as background; not added as primary paper assets)
* Purely offline batch transcription with no latency data
* Non-English-only systems with no English results
* Vendor marketing content without reproducible methodology

### Papers Reviewed vs. Selected

* **Papers reviewed**: approximately 60 candidates identified across all queries and databases
* **Papers selected as primary assets**: 15 (from 11 paper-research discoveries + 4 internet-search
  additions: Durmus2026, Wang2026, Wang2026b, Tay2026)
* **Background papers noted but not added as assets**: 7 (Gong2025/BR-ASR, Hori2025/Delayed Fusion,
  Trinh2025, Sudo2025/OWSM-Biasing, WhisperNER, Im2025/DeRAGEC, Altinok2025)
* **Papers excluded after initial inspection**: remaining candidates fell outside date range,
  reported no entity-level metrics, or were non-English-only

* * *

## Findings by Technique Category

### Contextual Biasing

Contextual biasing — injecting a runtime list of domain-specific terms into the ASR decoder —
remains the dominant paradigm in Jan–Jun 2026. However, the field has shifted decisively from flat
word-list prompting toward retrieval-augmented and RL-optimized variants that address scalability
limits.

**RLBR** (`10.48550_arXiv.2601.13409`, Ren2026) achieves the lowest reported B-WER on English
LibriSpeech in the survey: 0.59% on test-clean and 2.11% on test-other at 100 bias words. The key
mechanism is reinforcement learning reward shaping — entity tokens receive a 5× reward multiplier
during training, forcing the model to prioritize correct entity decoding. At 500 bias words the
B-WER rises to 2.37%/6.49%, reflecting the context saturation that affects all flat-list approaches.
RLBR requires full model retraining; it is not applicable to the existing Whisper Turbo checkpoint
without fine-tuning.

**CLAR** (`10.48550_arXiv.2603.25460`, Huang2026) achieves 97.03% Recall@1, 0.92% CER, and 2.78%
B-WER on AISHELL-1-NE via CIF-localized alignment for retrieval-augmented ASR. The CIF
(Connectionist Temporal Classification with Integrated Fusion) mechanism produces token-level
acoustic representations without explicit timestamps, enabling length-aware localized matching for
short entities (1–3 syllable brand names) that global-average-pooled embeddings miss. Evaluated on
Mandarin Chinese only; English accuracy transfer is unverified.

**Novitasari2026** (`10.48550_arXiv.2604.12398`) addresses a practical gap: existing
phoneme-assisted biasing approaches require a G2P (grapheme-to-phoneme) system, which fails on
non-standard product names and SKUs. The common-word cue approach achieves a 16.3% reduction in
bias-word recognition errors without G2P by exploiting phonetically similar common words as soft
anchors. The method is additive to other biasing techniques and applicable to Whisper Turbo without
retraining.

**Tsai2026** (`10.48550_arXiv.2605.18222`) extends CTC-based word spotting to streaming ASR via
stateful token passing across 160ms audio chunks. Active trie paths are preserved across chunk
boundaries, enabling detection of keywords that straddle chunk boundaries. An incremental commitment
threshold controls the latency/recall trade-off. The method requires no modification to the
underlying acoustic model and is directly applicable to Whisper's CTC auxiliary output. Specific
absolute B-WER numbers are not reported in the abstract; full-paper validation is needed.

**Consensus finding**: Contextual biasing is not superseded — it is being industrialized. The
community has converged on retrieval-augmented biasing (Gong2025/BR-ASR background: B-WER 2.8% at
200k entries with 20ms latency) and RL fine-tuning (RLBR: 0.59% B-WER) as the successors to flat
word-list prompting. For Rezolve's catalog scale (potentially 10,000+ brand/product entries), flat
prompting will saturate the context window; retrieval-first architectures are required.

### Shallow Fusion

No standalone shallow fusion paper appeared in Jan–Jun 2026. This is a literature gap, not a search
failure — internet search confirmed the finding across arXiv, ACL Anthology, Semantic Scholar, and
ICASSP/Interspeech proceedings.

The community has moved to two alternatives: direct LLM integration (Delayed Fusion, Hori2025
background, ICASSP 2025) and retrieval-augmented biasing. Delayed Fusion integrates LLM scores
during first-pass decoding with reduced LLM call count — effectively superseding classic shallow
fusion in both speed and entity accuracy. LOGIC (`10.48550_arXiv.2601.15397`, Wang2026) achieves
constant-time contextual biasing via logit-space integration, bypassing the context window entirely;
however, this paper was withdrawn from arXiv in February 2026 and cannot be implemented until it
reappears at a conference venue (Interspeech 2026 or ICASSP 2026 are probable destinations).

**Consensus finding**: Shallow fusion as a distinct technique is effectively obsolete in the 2026
literature. For latency-compatible LM integration in a streaming ASR pipeline, Delayed Fusion
(background) is the successor method. For catalog-scale entity biasing specifically, retrieval
followed by prompt injection (BR-ASR architecture) is the preferred alternative.

### Entity-Aware ASR

**CLAR** (`10.48550_arXiv.2603.25460`, Huang2026) — covered in Contextual Biasing above — is the
strongest entity-aware architecture in the survey for retrieval accuracy (97.03% Recall@1), but is
Mandarin-only and requires retraining.

**RASTAR** (`10.48550_arXiv.2602.12287`, An2026) achieves 17.96% and 34.42% relative NE-CER
reduction on AISHELL-1 and Homophone test sets respectively via adaptive chain-of-thought reasoning
for named entity correction. The adaptive reasoning depth (using 30–40% fewer tokens than full CoT)
is directly relevant to latency-sensitive deployment. RASTAR is also Mandarin Chinese only; English
evaluation is absent.

**Poncelet2026** (`10.48550_arXiv.2606.10838`) trains a speech-LLM to use broad metadata
descriptions (video topics and categories) as chain-of-thought context for ASR correction, achieving
a −2.5% relative NE-WER reduction on M3AV YouTube-derived test sets. While the absolute gain is
modest (−0.6pp absolute on NE-WER), the approach addresses entities absent from a pre-defined bias
list but inferrable from session context — directly applicable to Rezolve's session-level metadata
(product category browsed, recent search queries, cart contents). The training data construction
pipeline uses GPT-4o paired with video metadata at 400 hours of training data without human
annotation; a comparable pipeline over Rezolve's session logs could yield an ecommerce-specific
contextual reasoning dataset.

**WildASR** (`10.48550_arXiv.2603.25727`, Tay2026) evaluates seven ASR systems across environmental
degradation, demographic variation, and linguistic diversity. Key finding: "model robustness does
not transfer across languages or conditions" and systems "hallucinate plausible but unspoken content
under partial or degraded inputs." The hallucination finding is directly relevant to wrong-action
rate — plausible but wrong brand names are not captured by WER. WildASR provides an evaluation
methodology applicable to extending gold-92 stress testing.

**Consensus finding**: End-to-end entity-aware ASR architectures (CLAR, RASTAR) achieve the highest
reported entity accuracy in their domains but are exclusively Mandarin Chinese, require retraining,
and do not address Rezolve's English ecommerce use case directly. Session-context reasoning
(Poncelet2026) is the most transferable entity-aware approach: it is model-agnostic, uses inference-
time metadata, and handles entities absent from static bias lists.

### LLM Post-Correction

**Ron2026** (`10.48550_arXiv.2602.18966`) demonstrates 17% relative WER reduction on entity-dense
NBA commentary via Whisper's `initial_prompt` parameter populated by a six-agent LLM pipeline. The
pipeline extracts topic, named entities, and domain jargon from an initial first-pass transcript and
constructs a context prompt (≤224 tokens) for a second Whisper decoding pass. Zero model retraining
is required; it is directly applicable to Whisper Turbo. Estimated total latency: ~550–650ms (two
Whisper passes plus multi-agent LLM coordination).

**RECOVER** (`10.48550_arXiv.2603.16411`, Kumar2026) achieves 8–46% relative E-WER reductions across
five diverse English domains. On Earnings-21 — the closest publicly available proxy for ecommerce
entities — the gain is 33–35% relative E-WER reduction. The mechanism collects top-5 beam-search
hypotheses and uses GPT-4o (LLM-Select strategy) to pick the most entity-informative one. No
training is required. Adding ~100–200ms for N-best collection and GPT-4o selection over the baseline
single-pass Whisper Turbo latency keeps the total well within 800ms.

**Jiang2026** (`10.48550_arXiv.2605.29430`) introduces S2ER (Sentence-level Semantic Error Rate), an
LLM-judged metric that better correlates with wrong-action rate than WER. S2ER collapses from 19–28%
to under 2% over 10 correction turns across GigaSpeech, WenetSpeech, and AISHELL-NER, while WER
decreases only marginally (10–12% to 9–10%). Named entity error rates improve from ~2% to <1% within
the first 1–2 correction turns. The multi-turn approach requires user confirmation at each turn,
making it most suitable for a clarification-routing pipeline rather than fully automated correction.

**Zheng2026** (`10.48550_arXiv.2601.21347`) reports 14.51% WER reduction and +7.66pp Slot Micro F1
on the difficult stratum of SAP-Hypo5 via selective span editing. By identifying uncertain spans
through hypothesis agreement analysis and rewriting only those spans, Zheng2026 reduces
hallucinations by ~30% compared to unconstrained LLM rewriting. For fully automated pipelines
without user confirmation, selective span editing is the safer correction strategy.

**Consensus finding**: LLM post-correction is the most actionable technique category for Rezolve's
pipeline because all leading methods (Ron2026, RECOVER, Zheng2026) require zero model retraining and
operate on the existing Whisper Turbo checkpoint. The standard evaluation metric (WER) understates
the semantic gains: S2ER (Jiang2026) is a better proxy for wrong-action rate. For automated
deployment, selective span editing (Zheng2026) is preferred over unconstrained rewriting to control
hallucination risk.

* * *

## Comparison Against Whisper Turbo + Dynamic Context Injection

Rezolve's current production pipeline: Whisper Turbo + dynamic context injection (runtime hotword
list passed to the decoder). The comparison below evaluates each technique family against this
baseline on four dimensions.

### 1. Techniques Reporting Gains on Entities Over Hotword Biasing

All four technique families report entity accuracy gains over flat word-list baselines equivalent to
Rezolve's dynamic context injection:

* **Ron2026** (`10.48550_arXiv.2602.18966`): 17% relative WER reduction on entity-dense domain via
  `initial_prompt` population — the same mechanism as dynamic context injection but with an
  LLM-generated context prompt rather than a static hotword list.
* **RECOVER** (`10.48550_arXiv.2603.16411`): 33–35% relative E-WER reduction on Earnings-21 via
  N-best hypothesis selection. E-WER directly measures entity phrase accuracy, not aggregate WER.
* **RLBR** (`10.48550_arXiv.2601.13409`): 0.59%/2.11% B-WER at 100 bias words on LibriSpeech
  test-clean/other — the lowest B-WER in the survey, but requires full retraining.
* **LOGIC** (`10.48550_arXiv.2601.15397`): 9% relative Entity WER reduction with constant-time
  complexity (withdrawn from arXiv; cannot be implemented until republished).
* **Novitasari2026** (`10.48550_arXiv.2604.12398`): 16.3% bias-word error reduction additive to
  existing biasing, without G2P.

### 2. Latency-Compatible Techniques (Sub-800 ms P50)

Based on reported latency numbers and reasonable extrapolation for a ~5-second utterance:

* **Ron2026** (~550–650ms estimated): two sequential Whisper passes plus multi-agent LLM
  coordination. Fits within 800ms on Whisper Turbo at INT8 (~22ms/chunk on RTX 4090), assuming LLM
  pipeline adds ~400–500ms.
* **RECOVER** (~+100–200ms over single Whisper pass): N-best collection is free (beam search already
  produces top-5); GPT-4o LLM-Select adds ~100–200ms API latency. Total well within 800ms.
* **Tsai2026 CTC streaming** (`10.48550_arXiv.2605.18222`): 160ms chunk streaming; no added latency
  vs. baseline CTC streaming. Token-passing overhead is negligible.
* **Novitasari2026** (`10.48550_arXiv.2604.12398`): zero added latency; common-word cue injection is
  a pre-processing step.
* **Moonshine v2 Small** (`10.48550_arXiv.2602.12241`): 148ms ASR stage on Apple M3. Leaves ~650ms
  for correction, retrieval, and routing — the most latency-efficient ASR-stage option in the
  survey.
* **RLBR** and **CLAR**: latency of retrained model not reported; cannot confirm sub-800ms without
  empirical measurement.
* **Jiang2026 multi-turn correction**: 10 correction turns are not latency-compatible for real-time
  use; applicable only with clarification routing where user confirmation gates each turn.

### 3. Applicable to Existing Whisper Turbo Without Retraining

The following techniques require no model weight updates and can be applied to the existing Whisper
Turbo checkpoint:

* **Ron2026**: `initial_prompt` is a Whisper decoder parameter; no weight modification.
* **RECOVER**: post-hoc N-best selection; operates on decoder output only.
* **Novitasari2026**: common-word cue injection is a pre-processing step to the bias list.
* **Tsai2026**: CTC-WS operates on CTC posterior probabilities; requires Whisper's CTC auxiliary
  output (verify that Whisper Turbo exports CTC scores in the deployment config).
* **Zheng2026**: selective span editing is a post-processing step; no model access required.
* **TARQ** (`10.48550_arXiv.2605.27808`, Wang2026b): rareBAL calibration is applied at quantization
  time, not at model training time; applicable if Whisper Turbo is quantized to INT4/W4.

The following techniques **require retraining** and are not directly applicable to Whisper Turbo:

* RLBR (Ren2026): full RL fine-tuning required; Whisper Turbo commercial license must be confirmed.
* CLAR (Huang2026): CIF-localized alignment requires training on aligned data.
* RASTAR (An2026): requires fine-tuning on NE-correction reasoning chains.
* Poncelet2026: requires training on metadata-paired speech data.

### 4. Estimated Entity Accuracy Uplift per Viable Candidate

| Technique | Paper | Uplift (entity metric) | Latency Added | Retraining? |
| --- | --- | --- | --- | --- |
| Ron2026 initial_prompt pipeline | `10.48550_arXiv.2602.18966` | ~17% rel. WER reduction on entity-dense domain | ~+400–500ms (two Whisper passes + LLM) | No |
| RECOVER N-best + LLM-Select | `10.48550_arXiv.2603.16411` | 33–35% rel. E-WER reduction (Earnings-21) | ~+100–200ms | No |
| Novitasari2026 common-word cues | `10.48550_arXiv.2604.12398` | 16.3% bias-word error reduction (additive) | ~0ms | No |
| Tsai2026 CTC streaming biasing | `10.48550_arXiv.2605.18222` | Significant keyword F-score gain (abs. values TBD) | ~0ms | No |
| Zheng2026 selective span editing | `10.48550_arXiv.2601.21347` | +7.66pp Slot Micro F1 | ~+50–150ms | No |
| TARQ (if deploying INT4 Whisper) | `10.48550_arXiv.2605.27808` | Prevents rare-WER regression at INT4 quantization | 0ms (calibration step) | No |
| RLBR RL fine-tuning | `10.48550_arXiv.2601.13409` | B-WER 0.59% at 100 bias words (LibriSpeech clean) | Not reported | Yes |

Note: Ron2026's 17% WER reduction is on the NBA domain (entity-dense English commentary), not
ecommerce. RECOVER's 33–35% E-WER reduction is on Earnings-21 (financial entities), not brand SKUs.
Direct measurement on gold-92 is required before these estimates can be treated as confirmed gains
for Rezolve's pipeline.

* * *

## Shortlist for Prototyping

Ranked by expected entity accuracy gain within the <800ms latency constraint, requiring no model
retraining, and directly applicable to the existing Whisper Turbo checkpoint:

### 1. Ron2026 — Initial-Prompt Multi-Agent Pipeline

**Paper**: `10.48550_arXiv.2602.18966`

**Mechanism**: A six-agent LLM pipeline processes a first-pass Whisper transcript to extract topic
labels, named entities, and domain jargon. These are assembled into a context prompt (≤224 tokens)
for a second Whisper decoding pass using the `initial_prompt` parameter.

**Why first**: Directly exploits Whisper Turbo's `initial_prompt` mechanism with no code changes to
the model. Zero training cost. Reported gain of 17% relative WER reduction on an entity-dense
English domain. The multi-agent LLM pipeline can be seeded with Rezolve's brand/product catalog for
the entity extraction step, making it directly applicable to ecommerce without dataset collection.

**Estimated latency**: ~550–650ms total (two Whisper passes + LLM coordination). Fits within 800ms
at Whisper Turbo INT8 inference speeds.

**Prototype action**: Implement the six-agent pipeline from Ron2026 against Whisper Turbo on
gold-92. Seed the NER agent with Rezolve's brand/product catalog. Measure entity accuracy (substring
match and Slot F1) and latency on all 93 clips.

### 2. RECOVER — N-Best Hypothesis Selection + LLM Correction

**Paper**: `10.48550_arXiv.2603.16411`

**Mechanism**: Collect top-5 beam-search hypotheses from Whisper Turbo; use GPT-4o (or a local 7B
model) to select the hypothesis with the highest entity-phrase accuracy (LLM-Select strategy), then
apply single-pass LLM correction on the selected hypothesis.

**Why second**: 33–35% relative E-WER reduction on Earnings-21 is the largest entity-accuracy gain
reported for a no-retraining method in the survey. The Earnings-21 domain (company names, product
names, person names in financial speech) is the closest available proxy for Rezolve's ecommerce
entity challenge. The method adds only ~100–200ms over a single Whisper pass.

**Estimated latency**: ~+100–200ms over baseline single-pass Whisper. Total pipeline within 800ms.

**Prototype action**: Enable beam-width-5 decoding on Whisper Turbo; implement LLM-Select using
GPT-4o on gold-92 N-best outputs. Compare against single-pass baseline and Ron2026 initial_prompt
pipeline.

### 3. BR-ASR — Retrieval-Augmented Catalog Biasing

**Background paper**: Gong2025 (Interspeech 2025, not added as primary asset due to 2025 date).

**Mechanism**: Build a speech-and-bias contrastive retrieval index over Rezolve's full brand/product
catalog. At inference, retrieve the top-20 acoustically similar candidates in ~20ms at 200k entries,
inject into Whisper's decoder context, and optionally apply Tsai2026 CTC streaming word spotting
(`10.48550_arXiv.2605.18222`) for real-time bias detection.

**Why third**: This is the most production-scalable approach for Rezolve's full catalog. B-WER of
2.8%/7.1% at 2k bias words on English LibriSpeech with a measured 20ms retrieval latency — well
within the 800ms budget. Unlike flat context injection (Rezolve's current approach), retrieval-first
architectures handle 10,000+ entry catalogs without context window saturation.

**Caveat**: BR-ASR is a 2025 paper. The retrieval index requires upfront engineering to build
(speech contrastive encoder training on domain data). This is higher implementation cost than #1 or
#2.

**Prototype action**: Implement the BR-ASR retrieval index against a sample of Rezolve's brand
catalog; evaluate B-WER on a subset of gold-92 clips that contain known brand entities.

* * *

## Gaps and Uncertainties

### No Ecommerce-Specific Entity Benchmark in Jan–Jun 2026

No publicly available benchmark targeting brand SKUs, product names, or ecommerce-specific voice
commands was published in January–June 2026. Contextual Earnings-22 (`10.48550_arXiv.2604.07354`,
Durmus2026) is the closest public proxy, targeting company names and person names in financial
earnings calls. Earnings-21 is the closest analog for RECOVER's reported E-WER gains. Gold-92
remains Rezolve's only directly relevant evaluation set. The shortlist gain estimates are
extrapolations from adjacent domains, not measurements on ecommerce entities.

### CLAR and RASTAR Are Mandarin Chinese Only

Both CLAR (Huang2026, `10.48550_arXiv.2603.25460`) and RASTAR (An2026, `10.48550_arXiv.2602.12287`)
are evaluated exclusively on AISHELL-1 and AISHELL-1-NE (Mandarin Chinese benchmarks). The CIF
alignment mechanism and adaptive CoT reasoning approach may transfer to English, but no English
evaluation exists in the Jan–Jun 2026 literature. These techniques are excluded from the shortlist
for this reason; they are tracked as Phase 2 candidates if initial English evaluations are
conducted.

### Gold-92 Lacks Entity Span Annotations

The gold-92 benchmark (`t0001_stt_benchmark`) contains ground-truth transcripts but no entity span
annotations (offsets marking brand names, product names, SKUs). Slot F1 and E-WER — the metrics most
directly correlated with wrong-action rate, as demonstrated by Jiang2026
(`10.48550_arXiv.2605.29430`) — cannot be computed on gold-92 without adding entity-offset markup.
This is a dependency for fully evaluating RECOVER (E-WER) and Zheng2026 (Slot F1) on gold-92. Until
entity spans are annotated, substring-match entity accuracy and overall WER are the only available
metrics.

### LLM Post-Correction Hallucination Risk

Unconstrained LLM rewriting can introduce plausible but incorrect entity names, increasing the
wrong-action rate even while reducing WER. Zheng2026 (`10.48550_arXiv.2601.21347`) quantifies this:
~30% more hallucinations with unconstrained vs. selective span rewriting. For fully automated
pipelines, selective span editing is the recommended approach. Ron2026's initial_prompt method does
not rewrite the transcript — it guides the decoder — and so is not subject to post-hoc
hallucination, but may generate incorrect entities in the second pass if the context prompt contains
errors from the first pass.

### RLBR and CLAR Require Full Model Retraining

RLBR (Ren2026) and CLAR (Huang2026) require full model weight updates. Rezolve must confirm that the
Whisper Turbo commercial license permits RL fine-tuning before investing in training infrastructure
for either method.

### Latency of Post-Correction Methods Is Largely Unmeasured

Only two papers in the survey report concrete latency numbers: Moonshine v2
(`10.48550_arXiv.2602.12241`, 148ms ASR stage on Apple M3) and BR-ASR (background: 20ms retrieval at
200k entries). Ron2026, RECOVER, and Zheng2026 do not report end-to-end latency for their correction
pipelines. The 550–650ms estimate for Ron2026 and 100–200ms for RECOVER are extrapolations based on
known Whisper Turbo inference speed and GPT-4o API latency; they require empirical measurement on
Rezolve's production infrastructure before the 800ms p50 constraint can be confirmed.

### LOGIC (Wang2026) Withdrawn from arXiv

The LOGIC paper (`10.48550_arXiv.2601.15397`, Wang2026) — logit-space biasing achieving 9% relative
Entity WER reduction with constant-time complexity — was withdrawn from arXiv in February 2026 for
institutional publication approval compliance. The method is architecturally distinct and addresses
context window saturation, but cannot be implemented until the paper reappears at a conference venue
(Interspeech 2026 or ICASSP 2026 proceedings are probable). A preprint v1 PDF was accessible at time
of asset creation, so the paper is retained as a pending asset with `download_status: "success"`
(v1). Monitor for reappearance before implementing.

### Accented English Entity Accuracy Gap Remains Open

WildASR (Tay2026, `10.48550_arXiv.2603.25727`) confirms that accent causes severe ASR degradation
across seven systems, but does not measure entity-level accuracy on accented speech specifically.
Gold-92 includes six non-native English speaker clips, making accent-induced entity errors a direct
project risk. No Jan–Jun 2026 paper directly addresses entity accuracy on accented English. The gap
must be addressed by stratifying gold-92 evaluation by speaker accent before interpreting aggregate
entity accuracy numbers.

### Assumptions Underlying the Shortlist Ranking

The shortlist ranking (Ron2026 > RECOVER > BR-ASR) assumes:

1. WER and E-WER gains on NBA/Earnings-21 domains transfer to Rezolve's ecommerce entity domain.
   This has not been validated on gold-92.
2. Whisper Turbo `initial_prompt` behaves consistently with the Whisper Large v2 model used in
   Ron2026. Whisper Turbo is a distilled variant; context prompt effectiveness may differ.
3. GPT-4o LLM-Select latency (~100–200ms) is achievable on Rezolve's infrastructure. If API latency
   exceeds this, a local 7B model substitute should be evaluated.
4. Gold-92 entity accuracy is primarily limited by lexical rather than acoustic factors. If accent-
   related acoustic degradation is the primary cause, post-correction methods will have limited
   effect and ASR-stage improvements (Moonshine v2, BR-ASR) will be more impactful.
