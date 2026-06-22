# STT Research for Ecommerce Voice AI

## Goal

Build and evaluate a Speech-to-Text harness optimised for Rezolve's voice commerce assistant.
The current production system (Deepgram) fails on domain-specific entities — brand names,
product lines, integrations, investor-relations terms — causing silent action failures that break
the user experience. This project benchmarks existing STT systems on a held-out gold set of
production audio, evaluates entity-aware post-correction strategies, investigates domain-adapted
fine-tuning of Whisper-class models, and measures confidence-routing approaches to reduce wrong
confident actions below 2% while keeping voice-to-action latency under 800 ms p50.

## Research Questions

1. What is the current WER and entity accuracy of Deepgram (production) and Whisper Large v3
   on the gold-92 benchmark, broken down by utterance category and entity type?
2. Do entity-aware post-correction strategies (LLM correction pass, contextual boosting, custom
   vocabulary injection) materially close the gap on action-critical spans without exceeding the
   800 ms p50 latency budget?
3. Does domain-adapted fine-tuning of Whisper-class models on Rezolve production audio improve
   entity accuracy on the gold-92 benchmark without regressing general English WER?
4. What confidence-routing policy (accept / correct / clarify / fallback thresholds) achieves
   wrong-confident-action rate <2% and clarification rate <5% on the gold-92 benchmark?
5. What is the minimum viable dataset size and composition for fine-tuning to achieve a
   meaningful entity accuracy gain, and how does the gain scale with data volume?

## Success Criteria

* Entity accuracy >92% on gold-92 (action-critical spans only).
* Intent preservation >95% on gold-92.
* Action-critical WER <8% on gold-92.
* Wrong confident action rate <2% on gold-92 under the confidence-routing policy.
* Voice-to-action latency p50 <800 ms end-to-end (STT + correction + routing).
* At least one STT condition beats production Deepgram on entity accuracy with statistical
  significance (BCa bootstrap p <0.05).

## Current Phase

Phase 0: Benchmark harness and baseline evaluation.

Task `t0001_stt_benchmark` — completed. Gold-92 benchmark dataset ingested and DVC-tracked.
Next: run baseline evaluation of Deepgram and Whisper Large v3 on gold-92 (`t0002`).

## Budget

Total: $2000 USD.

Available services: `anthropic_api`, `openai_api`, `azure_ml`.

Paid API usage is expected primarily for LLM-as-judge evaluation and entity-correction
experiments. GPU compute (Azure ML) is reserved for Whisper fine-tuning tasks.
