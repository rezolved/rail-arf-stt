# Shallow Fusion Feasibility Assessment: Moonshine v2 Medium

**Task:** t0008_moonshine_v2_benchmark **Date:** 2026-06-25 **Model:**
UsefulSensors/moonshine-streaming-medium (MoonshineStreamingForConditionalGeneration)

## Background

Moonshine v2 Medium achieved only 9.1% domain-vocabulary entity accuracy on the gold-92 benchmark,
compared to 94.5% for Whisper with vocabulary biasing. The root cause is that Moonshine's
transformers API does not support `initial_prompt` (unlike Whisper), and the model has no built-in
hotword boosting. This document assesses three candidate approaches to add vocabulary biasing.

## Candidate Approach 1: Log-linear Model (Beam Search Score Rescoring)

**Description:** At decode time, rescore beam candidates using a domain-aware log-linear model. Add
a term `lambda * log P_lm(hypothesis)` where `P_lm` is an n-gram LM trained on domain vocabulary and
transcripts.

**Integration point:** Post-generation rescoring via `num_return_sequences > 1` in
`model.generate()`. Moonshine uses an auto-regressive decoder; we can request N-best beams and
rescore with a custom KenLM n-gram model.

**Library:** `kenlm` (Python bindings), plus custom rescorer wrapping `generate()`.

**Effort estimate:** 3-5 days. Build a small domain LM from the 31-term vocab and available
transcripts, then wrap the generator with N-best rescoring.

**Latency overhead:** +30-100ms per clip (N-best enumeration + KenLM scoring). Acceptable for
async/offline use but likely too high for <800ms streaming target without pruning.

**Limitation:** Moonshine's tokenizer is character-level, so word-level n-gram rescoring requires
detokenization at each step. Feasible but adds complexity.

* * *

## Candidate Approach 2: CTC Beam-Search Hotword Boosting via pyctcdecode

**Description:** Replace Moonshine's default greedy/beam decoder with `pyctcdecode`'s CTC beam
search, which natively supports hotword boosting. Domain vocabulary terms are injected as hotwords
with a boost weight.

**Integration point:** Moonshine's streaming encoder outputs logit distributions at each frame;
`pyctcdecode` can consume these if we access the encoder output directly and bypass the
auto-regressive decoder.

**Library:** `pyctcdecode>=0.5` (Apache 2.0). Requires access to per-frame CTC logits.

**Effort estimate:** 5-8 days. Moonshine uses an encoder-decoder architecture, not a pure CTC model.
Extracting CTC-compatible logits requires either modifying the model architecture to add a CTC head
or using a separate Moonshine CTC variant (none currently exists). This is the main blocker.

**Latency overhead:** Minimal once integrated; pyctcdecode beam search is ~10-20ms overhead.

**Limitation:** Moonshine is encoder-decoder, not CTC-only. pyctcdecode cannot consume
cross-attention decoder outputs natively. This approach requires substantial model surgery or
waiting for an official Moonshine CTC variant.

* * *

## Candidate Approach 3: Lattice Rescoring with Domain Language Model

**Description:** Generate word lattices from the decoder (multiple hypotheses with scores), then
rescore with a domain LM that heavily weights the 31-term vocabulary.

**Integration point:** Use `num_beams >= 4` in `model.generate()` with
`output_scores=True, return_dict_in_generate=True` to extract beam hypotheses and scores. Build a
domain LM (trigram KenLM) from the Rezolve investor-relations corpus and rescore.

**Library:** `kenlm`, `sentencepiece` for tokenization alignment.

**Effort estimate:** 4-6 days. The Moonshine tokenizer is SentencePiece; aligning KenLM word-level
scores with subword beam candidates is non-trivial but well-understood.

**Latency overhead:** +40-150ms. Beam search is more expensive than greedy; N-beam decode time grows
linearly with `num_beams`. At `num_beams=4`, overhead is modest (~50ms on CPU).

**Limitation:** Requires a domain corpus for LM training. The 31-term vocabulary is small; a
character/trigram LM trained on domain text (annual reports, investor presentations) would be needed
for good coverage. This corpus exists but is not yet preprocessed.

* * *

## Recommended Approach

**Recommendation: Approach 1 (Log-linear N-best Rescoring)** is the most straightforward to
implement without model surgery.

Steps:
1. Train a trigram KenLM on Rezolve domain text (investor-relations transcripts + vocab list)
2. Generate top-4 beams from Moonshine with `num_beams=4`
3. Rescore each beam: `final_score = seq_score + lambda * kenlm_score(hypothesis)`
4. Select the highest-scoring rescored hypothesis

Expected improvement: 15-30% relative gain in domain-vocab entity accuracy based on analogous
experiments in Whisper biasing (t0004). The Rezolve terms are highly distinctive, so even a small
vocabulary LM should produce meaningful boosts.

Expected latency overhead: +50-80ms warmed, bringing p50 from 0.233s to ~0.310s — still well under
the 800ms voice-to-action budget.

* * *

## Feasibility Verdict

**Verdict: Viable for production (with effort)**

- Shallow fusion via N-best rescoring is implementable within 1 sprint (5 days)
- Does not require model surgery or a Moonshine CTC variant
- Expected to meaningfully improve domain-vocab entity accuracy
- Latency overhead is acceptable for the <800ms streaming target
- However, Moonshine's current entity accuracy gap vs. Whisper (9.1% vs. 94.5%) is large enough that
  biasing alone may not close the gap. If entity accuracy after biasing remains below 60%, Whisper
  with vocabulary biasing (t0004) remains the recommended production path.
- A hybrid approach — Moonshine for latency-critical streaming, Whisper for entity-critical queries
  — may be optimal.
