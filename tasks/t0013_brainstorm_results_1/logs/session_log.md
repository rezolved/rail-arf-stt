# Brainstorm Session 1 — Full Transcript

## Project State Presented

**Tasks (12 completed):**

| Model | EA | EA_DV | WER | AC-WER | Lat p50 | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Parakeet TDT 0.6b-v3 (prod) | 23.2% | 33.3% | 15.2% | 33.5% | 38 ms | current prod, weak accuracy |
| Whisper turbo (streaming, t0012) | 42.0% | 89.9% | 9.0% | 6.3% | 290 ms | best overall |
| Granite Speech 4.1 2B (biased, t0012) | 41.1% | 97.1% | 8.8% | 7.6% | 249 ms | best DV recall |
| Whisper large-v3 (batch, t0002) | 46.0% | 94.5% | 8.5% | 2.5% | 6660 ms | too slow |
| Nemotron 3.5 ASR | 18.7% | 12.7% | 19.9% | 42.4% | 720 ms | ELIMINATED |
| Moonshine v2 | 21.7% | 9.1% | 16.6% | 34.2% | 233 ms | ELIMINATED |
| FunASR SeACo-Paraformer | 2.2% | 0.0% | 122.7% | 100% | 48 ms | ELIMINATED |

Active suggestions: 24 (6 high, 14 medium, 2 low). Budget: $2.50 / $2000 (0.125%). No answer assets.

## Clarification Questions

AI: 5 clarifying questions asked — strategic priority, streaming requirement, API budget,
parallelism, task count.

Researcher:
1. Priority: integrate best STT model into production.
2. Streaming mandatory — voice agent, batch not possible.
3. Budget: minimize API costs, find optimal solution.
4. Parallelism: parallel execution preferred.
5. Task count: one task to determine how much Granite can be better than Parakeet. Noted Whisper had
   errors on short recordings (< 30s clip failures).

## Discussion — Round 1: New Tasks

AI: Proposed t0013 as pure analysis task (short-clip stratification using existing t0012 JSONL,
production fit review, answer asset).

Researcher: Questioned whether GPU run is needed ("ты уверен что не стоит на GPU запускать?").

AI: Checked gold-92 duration distribution — 0 clips < 3s, min 3.07s. Gold-92 cannot test short-clip
behavior. GPU needed. Revised proposal to include synthetic short clips (0.5–2s nарезки)
+ GPU run.

AI: Asked for clarification on "Granite biasing tuning" mentioned in proposal. Explained it as
prompt format experiments — concluded not needed given EA_DV already 97.1%.

Researcher: Provided additional context: "моя задача максимально выяснить что Granite может подойти
в продакшне больше Parakeet и Whisper, до был whisper только но он не справлялся с короткими аудио
less 30 sec." AI read brainpowa STT codebase for production context.

Researcher: "только учти необходимо имитировать реальный стриминг как в продакшн" — must simulate
real production streaming via transcribe_stream() with 32kB PCM-16 chunk queue, not direct model
inference.

AI: Confirmed final t0014 scope:
* Part 1: Synthetic short clips (0.5–2s nарезки + edge-cases: silence, noise, single word).
* Part 2: GPU run all three models via transcribe_stream() with 32kB PCM-16 chunk queue.
* Part 3: Stratified gold-92 analysis (2–5s vs 5–10s) + new short-clip results.
* Part 4: Answer asset — production recommendation Granite vs Parakeet.

Researcher: "да" — confirmed.

## Discussion — Round 2: Suggestion Cleanup

AI: Proposed rejecting 6 suggestions:
* S-0002-01: superseded by t0004.
* S-0005-04: Moonshine eliminated.
* S-0005-09: Paraformer eliminated.
* S-0008-01, S-0008-02, S-0008-03: Moonshine eliminated.

Researcher: Confirmed implicitly in overall confirmation.

## Discussion — Round 3: Confirmation

AI: Presented full decision list — 1 new task (t0014), 6 rejections. Verified counts: new tasks = 1,
rejections = 6.

Researcher: "yes" — confirmed all decisions.

## Decisions Summary

1. Create t0014: Granite short-clip robustness + production fit assessment (GPU, streaming sim).
2. Reject S-0002-01 (superseded by t0004).
3. Reject S-0005-04 (Moonshine eliminated).
4. Reject S-0005-09 (Paraformer eliminated).
5. Reject S-0008-01 (Moonshine eliminated).
6. Reject S-0008-02 (Moonshine eliminated).
7. Reject S-0008-03 (Moonshine eliminated).
