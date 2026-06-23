# Vocabulary Biasing Experiment — initial_prompt Impact on Gold-92 Entity Accuracy

## Motivation

t0002_baseline_evaluation established a sobering finding: Whisper large-v3 and Whisper turbo both
score **25.2% entity accuracy overall** and only **8.8% on production clips** (real
investor-relations call recordings). Crucially, this gap is model-size invariant — scaling from
turbo to large-v3 yields no entity accuracy gain. The bottleneck is that domain terms (brand names,
product names, people's names) are absent from Whisper's training distribution.

In production (brainpowa-realtime-api), the codebase already uses `STT_INITIAL_PROMPT` as a
vocabulary hint, populated by `get_voice_utterance_transcription_prompt()`. This function returns a
comma-separated list of 31 domain terms. However, the actual impact of this biasing strategy on
entity recognition has never been quantified against a held-out benchmark.

This task closes that gap by running a controlled ablation: identical evaluation conditions as
t0002, with the only variable being the presence or absence of the 31-term `initial_prompt`. The
results will tell us whether the production biasing is effective and by how much, and will identify
which domain terms remain problematic even after biasing.

## Domain Vocabulary List

The exact 31 terms used in production (verbatim from `get_voice_utterance_transcription_prompt()`):

> Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
> GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations, Dan
> Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee, Mark Turner,
> Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith, Justin King,
> Christian Angermayer

This string is passed verbatim as the `initial_prompt` parameter to faster-whisper's `transcribe()`
call.

## Runs

Four runs in total. Two baselines are **reused from t0002** (no re-inference needed — load
predictions from t0002's assets directly):

| Run | Model | initial_prompt | Source |
| --- | --- | --- | --- |
| R1 | Whisper large-v3 | None (no biasing) | Reuse t0002 predictions |
| R2 | Whisper large-v3 | 31-term domain vocab | New inference (this task) |
| R3 | Whisper turbo | None (no biasing) | Reuse t0002 predictions |
| R4 | Whisper turbo | 31-term domain vocab | New inference (this task) |

New inference (R2 and R4) uses the same setup as t0002: faster-whisper int8 on CPU (Apple M5), beam
size 5, language "en", no other parameters changed from t0002.

## Metrics

All six registered project metrics are computed for every run:

| Metric key | Description |
| --- | --- |
| `entity_accuracy_gold92` | Entity accuracy across all 93 clips (primary comparison) |
| `entity_accuracy_production` | Entity accuracy on the 34 production-accent clips only |
| `entity_accuracy_domain_vocab` | Entity accuracy over the 31 domain terms appearing in gold-92 ground truth (primary for this task) |
| `wer_gold92` | Word error rate across all 93 clips |
| `latency_p50_seconds` | p50 inference latency (new inference runs only; baselines carry t0002 values) |
| `intent_preservation_gold92` | Intent preservation across all 93 clips |

All metrics reported with BCa bootstrap 95% CIs (n=10,000, seed=42). The
`entity_accuracy_domain_vocab` subset metric is the primary metric for this task because it directly
measures whether biasing helps with the 31 terms that were injected.

**Note**: `entity_accuracy_production` is not a registered project metric. Report it as a derived
sub-metric within results but do not register it separately. The registered metrics listed above are
sufficient for cross-task comparability.

## Compute

No GPU required. Runs on CPU (Apple M5 Pro/Max), faster-whisper int8. Each new inference run (R2,
R4) takes approximately the same wall-clock time as a full t0002 inference pass (~15–25 minutes per
model). Total estimated compute: under 1 hour.

Budget: $0 (CPU-only, no cloud resources).

## Key Questions

1. Does `initial_prompt` with the 31-term domain vocabulary improve entity accuracy on domain terms?
   By how much (absolute and relative)?
2. Which of the 31 domain terms are still misrecognised after biasing (term-level breakdown)?
3. Does biasing cause any WER regression on non-domain utterances (hallucination or drift)?
4. Is the entity accuracy improvement larger on production-accent clips (34 clips) than on
   clean-voice clips?
5. Is the biasing effect consistent across both model sizes (large-v3 vs turbo), or does one model
   benefit more?

## Expected Assets

Two new prediction assets produced by this task:

- `predictions/whisper-large-v3-biased` — transcript predictions for all 93 gold-92 clips from
  Whisper large-v3 with domain `initial_prompt`
- `predictions/whisper-turbo-biased` — transcript predictions for all 93 gold-92 clips from Whisper
  turbo with domain `initial_prompt`

The two no-biasing baselines (R1, R3) are referenced from t0002 assets, not regenerated.

## Dependencies

Depends on **t0002_baseline_evaluation** for:

1. The no-biasing prediction assets for Whisper large-v3 and turbo (reused directly, no
   re-inference)
2. The evaluation harness code and metric computation scripts developed in t0002
3. The gold-92 dataset split definitions and clip-level metadata (production vs non-production
   stratification)

## Results Structure

Results will be reported in `results/results_detailed.md` with:

- A summary comparison table: all four runs × all six metrics with CIs
- A per-term breakdown table: for each of the 31 domain terms that appear in gold-92 ground truth,
  show recognition rate before and after biasing (both model sizes)
- A stratified comparison: production-accent clips vs clean-voice clips, biased vs unbiased
- A WER regression check: histogram or table of WER per clip, biased vs unbiased, flagging any clips
  where biasing increased WER by more than 5%

All charts saved to `results/images/` and embedded in `results_detailed.md`.

## Source

This task was motivated by suggestion **S-0003-02** ("Prototype Ron2026 initial_prompt multi-agent
pipeline on gold-92"). The current task implements the simpler ablation first — quantifying the
single-prompt biasing baseline — before moving to the multi-agent pipeline described in the
suggestion.
