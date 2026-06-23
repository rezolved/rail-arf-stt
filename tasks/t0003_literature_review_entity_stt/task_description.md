# Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)

## Motivation

Rezolve's voice commerce assistant currently uses Whisper Turbo with dynamic context injection (a
runtime hotword list passed to the decoder) as its production STT pipeline. The primary bottleneck,
confirmed by the gold-92 benchmark (`t0001_stt_benchmark`), is entity accuracy: brand names, product
names, and SKUs are frequently mangled or dropped, leading to wrong-action rates that exceed the 2%
target.

Before investing engineering effort in a new approach, this task surveys the most recent published
literature (January–June 2026) to identify which techniques offer the best entity-accuracy gains in
the ecommerce domain while remaining compatible with the project's 800 ms p50 latency constraint.
The findings will directly inform the design of follow-on benchmark and model tasks.

## Research Question

What are the most effective techniques published between January and June 2026 for improving STT
accuracy on domain-specific named entities (brand names, product names, SKUs), and which of these
are compatible with a sub-800 ms voice-to-action latency requirement in an English ecommerce voice
AI context?

## Scope

### Techniques to cover

1. **Contextual biasing** — runtime entity lists fed to the decoder (prefix trees, WFST rescoring,
   shallow biasing networks). This is the approach used in our current Whisper Turbo pipeline; the
   survey must identify state-of-the-art alternatives and their reported gains over this baseline.
2. **Shallow fusion** — interpolating ASR decoder scores with a domain language model at inference
   time. Focus on low-latency variants compatible with streaming ASR.
3. **Entity-aware ASR** — model architectures that embed entity knowledge during training or
   fine-tuning (named entity embeddings, entity-conditioned decoding, span-level objectives).
4. **LLM post-correction** — using a language model as a second-pass corrector of the ASR
   hypothesis, with or without entity grounding. Emphasis on latency-efficient approaches
   (speculative decoding, distilled correctors, prompt-based).

### Inclusions

- Papers published or posted between January 1 and June 30, 2026.
- English-language ASR or multilingual ASR with English results reported.
- Ecommerce, voice assistant, or general conversational domain.
- Any evaluation on named entity recognition accuracy, entity WER, or brand/product recall.

### Exclusions

- Papers published before 2026 (background reading only; do not add as task paper assets unless they
  are essential baselines cited by 2026 papers).
- Purely offline batch transcription systems with no latency data.
- Non-English-only systems with no English results.

## Approach

### Search strategy

Query the following databases using at least the keyword combinations listed below. Record every
query and its result count in `results/search_log.md`.

**Databases**: arXiv (cs.CL, cs.SD, eess.AS), Semantic Scholar, ACL Anthology, Interspeech 2026
proceedings (if published), ICASSP 2026 proceedings.

**Keyword combinations** (run all six):

1. `contextual biasing ASR named entity 2026`
2. `entity-aware speech recognition ecommerce 2026`
3. `shallow fusion ASR latency 2026`
4. `LLM post-correction ASR named entity 2026`
5. `domain-specific ASR brand product 2026`
6. `Whisper fine-tuning named entity ecommerce 2026`

### Paper selection

- Target: a minimum of 8 and a maximum of 15 papers added as paper assets.
- Prioritize papers that report: (a) entity-level accuracy or entity WER, (b) latency measurements
  or inference cost, and (c) ecommerce or voice assistant domain results.
- Papers that do not report latency data are still in scope if they address entity accuracy directly
  — note the omission explicitly in the synthesis.

### Asset creation

Use `/add-paper` for each selected paper to create a paper asset under `assets/paper/<paper_id>/`.
Use `/download_paper` to obtain PDF files where available. For each paper, read the full text before
writing the summary. Mark abstract-only summaries explicitly in the paper asset when a PDF is
unavailable.

## Comparison Against Current Approach

The synthesis document must include a dedicated section titled **"Comparison Against Whisper Turbo +
Dynamic Context Injection"** that addresses:

1. Which surveyed techniques report gains on entities over a runtime hotword-biasing baseline?
2. Which techniques are latency-compatible (sub-800 ms p50 for a ~5-second utterance) based on
   reported numbers or reasonable extrapolation?
3. Which techniques are practically implementable without full model retraining (i.e., can be
   applied to our existing Whisper Turbo checkpoint)?
4. For each viable candidate: what is the estimated entity accuracy uplift vs. the hotword baseline?

This comparison should yield a ranked shortlist of at most 3 techniques to prototype in follow-on
tasks.

## Expected Outputs

### Paper assets

- 8–15 paper assets under `assets/paper/`, each passing `verify_paper_asset.py` with no errors.
- Each paper summary states: technique category, claimed entity-accuracy gain, latency impact, and
  domain.

### Synthesis document (`results/results_summary.md`)

Organized as follows:

1. **Methodology** — search queries, databases, inclusion/exclusion criteria, total papers reviewed
   vs. selected.
2. **Findings by technique category** — one subsection per category (contextual biasing, shallow
   fusion, entity-aware ASR, LLM post-correction), summarizing the 2–4 most relevant papers and the
   consensus finding for each category.
3. **Comparison Against Whisper Turbo + Dynamic Context Injection** — see above.
4. **Shortlist for prototyping** — the top 1–3 techniques ranked by expected entity accuracy gain
   while respecting the <800 ms latency constraint.
5. **Gaps and uncertainties** — what the surveyed literature does not cover, and what assumptions
   underlie the shortlist ranking.

### Search log (`results/search_log.md`)

Records every query run, the database, the date, the result count, and the number of papers selected
from that query.

## Key Questions

1. Does contextual biasing (the technique underlying our current dynamic context injection) remain
   the dominant approach in Jan–Jun 2026 literature, or have newer methods superseded it?
2. Which post-correction approach offers the best entity accuracy gain with the lowest added
   latency?
3. Is shallow fusion still competitive with end-to-end entity-aware ASR architectures for ecommerce
   domains?
4. Are there ecommerce-specific benchmarks published in this period that could complement gold-92
   for ongoing evaluation?

## Dependencies

No task dependencies. This is a pure literature survey and can start immediately. The gold-92
benchmark dataset (`t0001_stt_benchmark`) provides domain context but is not a runtime input to this
task.

## Budget and Compute

This task requires no GPU compute. Costs are limited to:

- LLM API calls for paper summarization: estimated $2–5 total.
- Web search and paper download: no direct cost.

No remote machine setup is needed.
