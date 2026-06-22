# Post-Correction Experiment Instructions

## Planning Guidelines

- Specify the input transcript source: which stt-benchmark-run task produced the raw ASR
  transcripts this experiment will correct (reference the task ID and JSONL predictions file).
- Describe the correction strategy precisely: model name and version (for LLM passes), vocabulary
  file format and injection point (for vocab injection), or boosting weight schema (for contextual
  boosting).
- Estimate LLM API cost: at ~400 tokens per clip (prompt + response) and 93 clips, cost is
  typically under $1 with GPT-4o-mini; document this in the plan.
- Plan a latency measurement: record per-clip wall-clock time for the correction pass alone (not
  including upstream STT) so it can be added to the base STT latency.

## Implementation Guidelines

- Load raw ASR transcripts from the upstream task's DVC-tracked predictions JSONL rather than
  re-running inference, unless a re-run is explicitly justified in the plan.
- Measure latency at the clip level (p50 of correction-only time) and add it to the upstream STT
  p50 to produce the combined `latency_p50_seconds` metric.
- Report both the delta over uncorrected transcripts and the absolute values for entity accuracy
  and action-critical WER so results can be compared across experiments.
- If the strategy uses an LLM, log the exact prompt template and model version in
  `results_detailed.md` for reproducibility.

## Common Pitfalls

1. Applying correction to gold-92 ground-truth transcripts instead of raw ASR hypotheses — always
   correct the hypothesis, compare against the reference.
2. Counting LLM token costs at plan time but forgetting to record actual costs in `costs.json`.
3. Not testing the correction strategy on a small held-out sample before running all 93 clips —
   catch prompt failures early.

## Related Skills

- `/implementation` — main execution skill
- `/research-code` — review existing correction experiments in prior tasks
