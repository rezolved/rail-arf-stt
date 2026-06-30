---
spec_version: "2"
answer_id: "granite-vs-parakeet-production-fit"
answered_by_task: "t0014_granite_short_clip_robustness"
date_answered: "2026-06-30"
---
## Question

Should Granite Speech 4.1 2B replace Parakeet TDT 0.6b-v3 as the production STT model in
brainpowa-realtime-api?

## Answer

YES, with a minimum clip duration gate of 2.0 s recommended for the first deployment. Granite Speech
4.1 2B produces 0% empty output and 0% hallucination across all 44 short clips tested (0.5–3.0 s),
while Parakeet fails on 27.3% of short clips (55.6% empty rate at sub-1 s bins) — directly matching
the failure mode that disqualified Whisper from production. On gold-92 (clips 3–13 s), Granite
achieves 94.8% entity accuracy versus Parakeet's 65.0%, with comparable latency (125–215 ms p50 vs
32–46 ms); both well within the 800 ms production constraint. Integration effort is low: reading
brainpowa-realtime-api base.py confirms the STTAdapter base class already implements
transcribe_stream() as accumulate-then-transcribe, so a granite.py adapter only needs to implement
transcribe() and model loading — approximately 60–80 lines of Python.

## Sources

* Task: `t0012_whisper_parakeet_granite_streaming`
* Task: `t0014_granite_short_clip_robustness`
* URL: https://huggingface.co/ibm-granite/granite-speech-4.1-2b
* URL: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
