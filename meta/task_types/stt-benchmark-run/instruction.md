# STT Benchmark Run Instructions

## Planning Guidelines

- Specify the full STT configuration: model or API name and version, any post-correction layer,
  any confidence routing policy. The combination is the "system under test" (SUT).
- Estimate API or inference cost for 93 clips. Deepgram Nova-2 is ~$0.004/min; Whisper local
  inference on Mac Metal is free; Azure GPU inference cost depends on VM size and clip duration.
- State the primary comparison target (usually production Deepgram baseline from t0002) so the
  plan can include a significance test step.
- Plan the output explicitly: `metrics.json` keyed by the 6 registered project metrics, plus
  per-clip predictions in `results/predictions/` for post-hoc analysis.

## Implementation Guidelines

- Always start with `dvc pull` to ensure the gold-92 audio is present locally.
- Transcribe all 93 clips; never subsample unless the task plan explicitly approves it with
  a stated rationale.
- Compute all registered project metrics: `entity_accuracy_gold92`, `intent_preservation_gold92`,
  `action_critical_wer_gold92`, `wer_gold92`, `wrong_action_rate_gold92`, `latency_p50_seconds`.
- Run a BCa bootstrap significance test (n=10 000 resamples, paired) vs the Deepgram baseline
  for entity accuracy and intent preservation. Record p-values in `results_detailed.md`.
- Save per-clip prediction rows (clip ID, reference, hypothesis, entity match, latency) to a
  JSONL file in `results/` tracked by DVC so future tasks can load them without re-running
  inference.

## Common Pitfalls

1. Measuring latency on the first clip only — warm up the model/connection with 3-5 throwaway
   clips before recording timing.
2. Using a different normalisation for WER than the gold-92 reference — always strip punctuation
   and lowercase both sides before computing WER.
3. Forgetting to push prediction JSONL files with `dvc push` before merging.
4. Reporting entity accuracy over all tokens instead of action-critical spans only — the
   registered metric is span-restricted.

## Verification Additions

- Confirm all 93 clips were transcribed (no skips due to errors).
- Check that `metrics.json` contains only registered metric keys.

## Related Skills

- `/implementation` — main execution skill
- `/research-code` — inspect existing eval harness in `brainpowa-realtime-api/scripts/evals/stt/`
