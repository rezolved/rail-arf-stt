# STT Research for Ecommerce Voice AI

## Goal

Build and evaluate a Speech-to-Text harness optimised for Rezolve's voice commerce assistant.
The current production system (Deepgram) fails on domain-specific entities — brand names, product
lines, integrations, investor-relations terms — causing silent action failures that break the user
experience. This project benchmarks existing STT systems on a held-out gold set of production audio,
evaluates entity-aware post-correction strategies, and investigates domain-adapted fine-tuning of
Whisper-class models to achieve entity accuracy >92% while keeping voice-to-action latency under
800 ms p50.

## Scope

### In Scope

* Evaluation of commercial STT APIs (Deepgram) and open-source models (Whisper variants) on
  Rezolve production audio.
* Entity-aware post-correction strategies: LLM correction pass, custom vocabulary injection,
  contextual entity boosting.
* Confidence-based routing: accept / correct / clarify / fallback thresholds.
* Domain-adapted fine-tuning of Whisper-class models on Rezolve production audio.
* Latency measurement end-to-end (speech end → tool call) for each candidate approach.
* English-first ecommerce and investor-relations voice utterances.

### Out of Scope

* Non-English STT (deferred to a follow-up project after English PoC is validated).
* Full TTS or voice synthesis pipeline — STT only.
* Real-time streaming ASR protocol changes (out-of-scope for this research phase).
* Production deployment and A/B testing infrastructure.

## Research Questions

1. What is the current WER and entity accuracy of Deepgram (production) and Whisper Large v3 on
   the gold-92 benchmark, broken down by utterance category and entity type?
2. Do entity-aware post-correction strategies (LLM correction pass, contextual boosting, custom
   vocabulary injection) materially close the gap on action-critical spans without exceeding the
   800 ms p50 latency budget?
3. Does domain-adapted fine-tuning of Whisper-class models on Rezolve production audio improve
   entity accuracy on the gold-92 benchmark without regressing general English WER?
4. What confidence-routing policy (accept / correct / clarify / fallback thresholds) achieves
   wrong-confident-action rate <2% and clarification rate <5% on the gold-92 benchmark?
5. What is the minimum viable dataset size and composition for fine-tuning to achieve a meaningful
   entity accuracy gain, and how does the gain scale with data volume?

## Success Criteria

* Entity accuracy >92% on gold-92 (action-critical spans only) for at least one candidate system.
* Intent preservation >95% on gold-92 for the best candidate.
* Action-critical WER <8% on gold-92 for the best candidate.
* Wrong confident action rate <2% on gold-92 under the chosen confidence-routing policy.
* Voice-to-action latency p50 <800 ms end-to-end (STT + correction + routing).
* At least one STT condition beats production Deepgram on entity accuracy with statistical
  significance (BCa bootstrap p <0.05, n=93 paired samples).

## Key References

* Radford et al. (2023) — "Robust Speech Recognition via Large-Scale Weak Supervision" (Whisper).
* Deepgram Nova-2 documentation and API — current production STT endpoint.
* Rezolve gold-92 benchmark (`tasks/t0001_stt_benchmark`) — 93 production voice clips,
  investor-relations domain, annotated ground truth.
* brainpowa-realtime-api STT evals (`scripts/evals/stt/`) — existing eval harness on public models.
* Rezolve Confluence: STT Strategy for Ecommerce Voice AI — English-First Implementation Plan
  (internal, 2026-06-10).

## Current Phase

Phase 0 complete: gold-92 benchmark dataset ingested and DVC-tracked (`t0001_stt_benchmark`).
Next step: run baseline WER and entity accuracy evaluation for Deepgram and Whisper Large v3 on
gold-92 (`t0002_baseline_evaluation`).
