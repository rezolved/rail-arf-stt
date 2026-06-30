# Answers: `entity-correction` (1)

1 answer(s).

[Back to all answers](../README.md)

---

<details>
<summary><strong>Should Granite Speech 4.1 2B replace Parakeet TDT 0.6b-v3 as the
production STT model in brainpowa-realtime-api?</strong></summary>

**Confidence**: high

YES, with a minimum clip duration gate of 2.0 s recommended for the first deployment. Granite
Speech 4.1 2B produces 0% empty output and 0% hallucination across all 44 short clips tested
(0.5–3.0 s), while Parakeet fails on 27.3% of short clips (55.6% empty rate at sub-1 s bins) —
directly matching the failure mode that disqualified Whisper from production. On gold-92
(clips 3–13 s), Granite achieves 94.8% entity accuracy versus Parakeet's 65.0%, with
comparable latency (125–215 ms p50 vs 32–46 ms); both well within the 800 ms production
constraint. Integration effort is low: reading brainpowa-realtime-api base.py confirms the
STTAdapter base class already implements transcribe_stream() as accumulate-then-transcribe, so
a granite.py adapter only needs to implement transcribe() and model loading — approximately
60–80 lines of Python.

| Field | Value |
|---|---|
| **Full answer** | [`full_answer.md`](../../../tasks/t0014_granite_short_clip_robustness/assets/answer/granite-vs-parakeet-production-fit/full_answer.md) |
| **ID** | [`granite-vs-parakeet-production-fit`](../../../tasks/t0014_granite_short_clip_robustness/assets/answer/granite-vs-parakeet-production-fit/) |
| **Question** | Should Granite Speech 4.1 2B replace Parakeet TDT 0.6b-v3 as the production STT model in brainpowa-realtime-api? |
| **Methods** | `code-experiment`, `papers`, `internet` |
| **Confidence** | high |
| **Date created** | 2026-06-30 |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`entity-correction`](../../../meta/categories/entity-correction/) |
| **Paper sources** | — |
| **Task sources** | [`t0012_whisper_parakeet_granite_streaming`](../../../overview/tasks/task_pages/t0012_whisper_parakeet_granite_streaming.md), [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **URL sources** | [url 1](https://huggingface.co/ibm-granite/granite-speech-4.1-2b), [url 2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) |
| **Created by** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |

</details>
