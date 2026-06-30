# Task t0015 — Streaming Buffer Interval Experiment

## Objective

Measure how the streaming buffer extraction interval (how often accumulated audio is sent to STT)
affects TTFD, latency p50/p95, WER, and entity accuracy across four models.

## Models

| Model | Biasing mechanism |
|-------|------------------|
| parakeet-unified-en-0.6b | NeMo GPU-PB TurboBias |
| parakeet-tdt-0.6b-v3 | NeMo GPU-PB TurboBias |
| multitalker-parakeet-streaming-0.6b-v1 | NeMo GPU-PB TurboBias (if supported); internal VAD |
| Granite Speech 4.1 2B | Keyword prompt injection |

## Buffer Intervals

- 500ms
- 750ms
- 1000ms

## Design

For each model × interval combination (12 total, plus multitalker which has internal VAD logic):

1. Simulate streaming: chunk audio into 32kB PCM-16 blocks, re-transcribe every N ms worth of
   accumulated audio.
2. Record: TTFD (first non-empty transcript), latency to final stable transcript, WER, EA
   domain-vocab.
3. For multitalker: test all three intervals but note that the model has internal segment
   boundaries — interval controls how often the buffer is flushed to the model, not when it
   decides to output.

## Dataset

gold-92: 93 WAV clips, ≥3.07s, 16kHz mono PCM.

## Success Criteria

- At least one model × interval combination beats Granite accumulate-then-transcribe (WER 8.8%,
  EA-DV 97.1%, TTFD 77ms p50) on either latency or quality.
- Full results table: 12+ rows, each with TTFD p50, lat p50, WER, EA, EA-DV.
