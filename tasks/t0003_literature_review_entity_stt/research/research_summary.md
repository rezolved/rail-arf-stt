# Research Summary — t0003_literature_review_entity_stt

## Key Findings (top 10 insights directly actionable for this task)

1. **Ron2026 initial_prompt pipeline is the highest-ROI first step.** Whisper's `initial_prompt`
   parameter accepts a context prompt built by a multi-agent LLM (topic, entities, jargon extracted
   from a first-pass transcript). On NBA entity-dense domain: 17% relative WER reduction. Zero model
   retraining; directly applicable to Whisper Turbo.

2. **RECOVER N-best + LLM-Select yields 33-35% relative E-WER reduction on business entities.**
   Collect top-5 beam search hypotheses; use GPT-4o (or local 7B) to select the most
   entity-informative one. On Earnings-21 (closest ecommerce analog) it achieves 33-35% relative
   E-WER reduction. No training required.

3. **BR-ASR scales retrieval-augmented biasing to 200k entries at 20ms latency.** Interspeech 2025
   (background), English LibriSpeech: B-WER 2.8%/7.1% at 2k bias words with 99.99% pruning rate.
   This is the most production-actionable retrieval architecture for Rezolve's full brand/product
   catalog; preferred over CLAR (no English evaluation) for English deployment.

4. **S2ER and entity Slot F1 are better optimization targets than aggregate WER.** Jiang2026 shows
   S2ER (LLM-judged sentence-level semantic error rate) collapses from ~20% to <2% over correction
   turns while WER improves only marginally. Wrong-action rate correlates with S2ER, not WER. Adopt
   S2ER and entity-span Slot F1 for gold-92 evaluation; requires adding entity-span offsets to
   gold-92 annotations.

5. **Deepgram Nova-3: 25.5% missed entity rate; AssemblyAI Universal-3 Pro: 5.38% (vendor
   benchmark).** A provider switch may resolve entity gaps without custom engineering. Evaluate
   AssemblyAI against gold-92 before investing in custom pipelines.

6. **Latency budget: ASR can consume 50-260ms, leaving ample margin.** Moonshine v2 Small (123M
   params): 148ms, 7.84% WER on Apple M3. Whisper Turbo at INT8 on RTX 4090: ~22ms per chunk. The
   end-to-end 800ms p50 target allows ~150ms ASR + ~150ms retrieval + ~300ms LLM post-correction
   + ~200ms margin.

7. **Selective span rewriting reduces hallucination ~30% vs. unconstrained LLM correction
   (Zheng2026).** For fully automated correction (no user confirmation), use selective editing;
   multi-turn unconstrained correction (Jiang2026) is viable only with clarification routing.

8. **Gold-92 has no entity span annotations; this limits span-level F1 until augmented.** Current
   schema supports only WER and substring-match entity accuracy. Techniques requiring typed span
   annotations cannot be evaluated on gold-92 as-is. The annotation gap must be addressed in a
   future task before entity Slot F1 can be computed.

9. **TARQ preserves rare-word accuracy during INT4 quantization at zero training cost.** If Whisper
   Turbo is quantized for latency reduction, apply TARQ's rareBAL calibration. Tested across 8
   backbones and 6 datasets. Implement as a production deployment step independent of the main
   correction pipeline.

10. **RLBR RL fine-tuning achieves the lowest B-WER (0.59% at 100 bias words) but requires full
    model access.** The alpha=5x reward multiplier for entity tokens is a transferable training
    principle. Defer until prompt-based approaches are benchmarked on gold-92; require if
    prompt-based methods fall short of the <2% wrong-action rate target.

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: Ron2026 Initial-Prompt Multi-Agent Pipeline + RECOVER N-Best

Run Whisper Turbo to get a first-pass transcript and collect top-5 beam hypotheses. A multi-agent
LLM extracts entity candidates (NER + fuzzy match, Levenshtein tau=0.75) and builds a context
prompt (<=224 tokens) for a second Whisper pass. Apply RECOVER LLM-Select on the top-5 to pick
the most entity-informative hypothesis, then run a single-pass LLM corrector. Combined estimated
gain: 35-45% relative entity error reduction. No training required; estimated latency ~550-650ms.

### Approach 2: BR-ASR Retrieval-Augmented Biasing Index

Build a speech-and-bias contrastive retrieval index over Rezolve's brand/product catalog (BR-ASR
architecture, Interspeech 2025). At inference retrieve top-20 acoustically similar candidates
(20ms at 200k entries), inject into decoder context, and run CTC streaming word spotting
(Tsai2026). Handles catalog-scale biasing without context-window saturation; no Whisper weight
modification required; compatible with Whisper's CTC auxiliary output.

### Approach 3: RLBR or CLAR Fine-Tuning (Phase 2, Training Required)

If Approaches 1-2 leave wrong-action rate above 2%, invest in training-based methods. RLBR (RL
reward shaping with alpha=5x on entity tokens) achieves B-WER 0.59% on LibriSpeech — lowest in
the survey. CLAR (CIF-localized alignment for retrieval) achieves B-WER 2.78% but lacks English
evaluation. Both require full model access; confirm Whisper Turbo license before proceeding.

## Reusable Code / Assets

- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` — 93
  ground-truth records with existing Deepgram Nova-2 and Whisper Large v2 hypotheses; load directly
  for all evaluation tasks.
- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl` — 91
  ground-truth strings only (2-record gap vs. gold_set.jsonl; investigate in t0002).
- No implementation code exists in the project yet; all evaluation code must be written from
  scratch in follow-on tasks.

## Key Papers (top 5, with finding most relevant to this task)

- **Ron et al. 2026** — 17% relative WER reduction on Whisper via initial_prompt multi-agent
  pipeline; zero training cost; directly applicable to Whisper Turbo.
- **Kumar and Sachdeva 2026 (RECOVER)** — 33-35% relative E-WER reduction on business entities via
  N-best hypothesis selection + LLM correction; no training required.
- **Gong et al. 2025 (BR-ASR)** — B-WER 2.8% on English LibriSpeech with 20ms retrieval at 200k
  entries; production-scale retrieval-augmented biasing baseline.
- **Jiang et al. 2026** — Introduces S2ER metric (LLM-judged semantic error rate); S2ER collapses
  from ~20% to <2% over correction turns; recommended as gold-92 primary metric alongside entity
  Slot F1.
- **Kudlur et al. 2026 (Moonshine v2)** — Streaming ASR: Small model 148ms / 7.84% WER on Apple
  M3; confirms ASR stage can stay under 150ms, leaving 650ms for correction and routing.

## Risks Flagged in Research

- **CLAR and RASTAR evaluated on Mandarin Chinese only.** CIF-alignment and adaptive CoT NE
  correction results may not transfer to English; English adaptation work required before
  adoption.
- **No ecommerce-specific entity benchmark in Jan-Jun 2026.** Contextual Earnings-22 (Durmus2026)
  is the closest public proxy but covers financial entities, not brand SKUs. Gold-92 remains
  Rezolve's only directly relevant evaluation set.
- **Gold-92 lacks entity span annotations.** Span-level Slot F1 and E-WER computation require
  adding entity offsets; this is a dependency for fully evaluating LLM post-correction gains.
- **LLM post-correction hallucination risk.** Unconstrained LLM rewriting can introduce plausible
  but wrong entity names (+wrong-action rate). Use selective span rewriting or constrain to
  catalog-grounded corrections.
- **RLBR and CLAR require full model retraining.** Whisper Turbo commercial license must be
  confirmed to permit RL fine-tuning before investing in training infrastructure.
- **Latency of post-correction methods unmeasured.** Only Moonshine v2 and BR-ASR report concrete
  latency. All other methods (CLAR, RASTAR, Jiang2026 multi-turn) require empirical latency
  measurement before declaring 800ms p50 compatibility.
- **Accented English entity accuracy gap remains open.** WildASR (Tay2026) confirms accent causes
  severe degradation but does not measure entity accuracy. Gold-92's six non-native speakers make
  this a direct project risk; stratified evaluation by accent is needed.
- **LOGIC (Wang2026) paper withdrawn from arXiv.** Logit-space biasing result (9% relative Entity
  WER, constant-time complexity) cannot be implemented until the paper reappears at a conference
  venue (expected Interspeech 2026 or ICASSP 2026).

## Full Detail Available In

- `tasks/t0003_literature_review_entity_stt/research/research_papers.md` — 11 papers
- `tasks/t0003_literature_review_entity_stt/research/research_internet.md` — 16 sources
- `tasks/t0003_literature_review_entity_stt/research/research_code.md` — 1 task reviewed (t0001),
  0 libraries
