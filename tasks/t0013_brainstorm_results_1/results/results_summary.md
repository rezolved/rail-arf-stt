# Results Summary — t0013 Brainstorm Session 1

## Summary

First brainstorm session after 12 completed tasks. One new task created (t0014: Granite short-clip
robustness + production fit assessment) and six suggestions rejected for eliminated models or
superseded experiments. The session established that the next priority is validating Granite Speech
4.1 2B as a production replacement for Parakeet TDT 0.6b-v3, with explicit focus on short-clip
robustness using real production streaming simulation.

## Session Overview

Date: 2026-06-29. First brainstorm session for the project. Prompted by completion of all 12
benchmark and research tasks, particularly t0012 which established a three-model production
streaming comparison. The researcher identified short-clip failures as the original reason Whisper
was replaced by Parakeet in production, and requested a focused validation task.

## Decisions

1. **Create t0014** — Granite Short-Clip Robustness Validation + Production Fit Assessment. Uses
   synthetic short clips (0.5–2s) + stratified gold-92 analysis. Simulates real production streaming
   via `transcribe_stream()` with 32kB PCM-16 chunk queue. GPU on Azure H100 NVL. Covers S-0003-07
   partially.
2. **Reject S-0002-01** — Vocabulary-biased Whisper via STT_INITIAL_PROMPT. Superseded by t0004.
3. **Reject S-0005-04** — Moonshine shallow-fusion biasing. Moonshine eliminated (EA 21.7%).
4. **Reject S-0005-09** — Granite vs Paraformer integration effort. Paraformer eliminated (WER
   122.7%).
5. **Reject S-0008-01** — Moonshine ONNX Medium. Moonshine eliminated.
6. **Reject S-0008-02** — Moonshine model-size ablation. Moonshine eliminated.
7. **Reject S-0008-03** — KenLM domain LM for Moonshine. Moonshine eliminated.

## Metrics

| Item | Count |
| --- | --- |
| Tasks reviewed | 12 |
| New tasks created | 1 |
| Suggestions reviewed | 24 |
| Suggestions rejected | 6 |
| Suggestions reprioritized | 0 |
| Corrections written | 6 |

Rejections verified: 6 — confirmed against correction file table above.

## Verification

* verify_task_file — pending Phase 6
* verify_corrections — pending Phase 6
* verify_suggestions — pending Phase 6
* verify_logs — pending Phase 6

## Next Steps

Execute t0014 on Azure H100 NVL. No other dependencies — t0014 depends only on t0012 data and
brainpowa codebase read access.
