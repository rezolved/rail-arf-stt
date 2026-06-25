# Research Summary — t0007_ibm_granite_4_1_benchmark

## Key Findings (top 10 insights directly actionable for this task)

1. **Granite ranked #1 on HuggingFace Open ASR Leaderboard** (5.33% mean WER, April 2026), flagged
   by t0005 as the primary benchmark candidate — this is the core motivation for t0007.

2. **Comparison target**: Whisper large-v3 + initial_prompt from t0004 scored 94.5%
   `entity_accuracy_domain_vocab`, 8.5% WER, 2.5% AC-WER at 6.66 s p50 (CPU). Granite must beat or
   match these numbers.

3. **Domain vocabulary is 31 terms** (authoritative in
   `tasks/t0004_vocabulary_biasing_experiment/code/constants.py`): brands, products, IR terms, and
   named persons including Rezolve, brainpowa, Brain Commerce, NASDAQ, Dan Wagner, Christian
   Angermayer, etc.

4. **Granite keyword biasing API must be confirmed** before writing `run_granite_biased.py`. The
   `ibm-granite/granite-speech-4.1-2b` model card specifies the exact processor parameter for
   keyword lists — this was not confirmed in research_code.md and is the key implementation unknown.

5. **GPU inference is mandatory**. Whisper CPU latency was 6.66 s p50; Granite on CPU will be
   similar. GPU (A100/H100) is required to approach the 200 ms p50 per-segment target. Estimated
   cost: $3–8 USD for ~1 hour A100.

6. **Two prediction assets are required**: `granite-4.1-2b-gold92-batch` (no biasing) and
   `granite-4.1-2b-gold92-keyword-biased`, both conforming to predictions asset spec v2.

7. **Cyrillic anomaly**: clip `error_en_0005` has a Cyrillic ground truth in `gold_set.jsonl`.
   Exclude from entity accuracy aggregate via `np.nanmean`, include in WER — carry this handling
   unchanged from t0004.

8. **BCa NaN guard is necessary**: On small strata (~8 production clips), BCa bootstrap can return
   NaN. Both prior tasks implement a percentile fallback — copy it unchanged.

9. **`ground_truth.jsonl` is the canonical reference** — not `gold_set.jsonl`. The latter is used
   only for `accent_group` stratification metadata.

10. **Per-term domain vocab breakdown** via `compute_per_term_accuracy()` (from t0004) is mandatory
    in results — it directly answers which of the 31 terms Granite's biasing still misses.

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: Copy-and-adapt from t0004 (recommended)

Copy four files from `tasks/t0004_vocabulary_biasing_experiment/code/`: `load_dataset.py`,
`compute_metrics_biased.py`, `constants.py`, and `write_predictions.py`. These are the most
complete, verified versions of the evaluation harness. Update only imports (paths module), variant
IDs, and model description strings. Create two new inference scripts (`run_granite_batch.py`,
`run_granite_biased.py`) using `run_whisper_biased.py` as the template — replace only model loading
and transcription call, keep warmup/timing/rejection logic intact.

### Approach 2: Minimal adaptation — reuse t0002 harness

Use the simpler t0002 harness (`compute_metrics.py`, 735 lines) which lacks
`entity_accuracy_domain_vocab` and `compute_per_term_accuracy`. This would require adding those
functions from scratch. Not recommended — t0004's version already has everything needed and is more
complete.

### Approach 3: Fresh implementation

Write all scripts from scratch using the task description as spec. Highest risk of inconsistency
with established metric definitions (normalisation, BCa parameters, anomaly handling). Not
recommended given the established, verified code base in t0002/t0004.

## Reusable Code / Assets

| File | Source | Description |
| --- | --- | --- |
| `tasks/t0004_vocabulary_biasing_experiment/code/load_dataset.py` | t0004 | Loads gold-92 as `GoldClip` dataclasses; handles Cyrillic anomaly; 22-regex entity span inference |
| `tasks/t0004_vocabulary_biasing_experiment/code/compute_metrics_biased.py` | t0004 | All 6 metrics incl. `entity_accuracy_domain_vocab`; BCa CIs; writes `metrics.json` and `analysis_output.json` |
| `tasks/t0004_vocabulary_biasing_experiment/code/constants.py` | t0004 | Authoritative 31-term `DOMAIN_VOCAB` list |
| `tasks/t0004_vocabulary_biasing_experiment/code/write_predictions.py` | t0004 | Writes predictions asset spec v2 (JSONL + details.json + description.md) |
| `tasks/t0004_vocabulary_biasing_experiment/code/run_whisper_biased.py` | t0004 | Inference template: warmup, tqdm, per-clip timing, `--limit`, 80% rejection criterion |
| `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/` | t0001 | 93 WAV clips (PCM-16 mono 16 kHz) + JSONL annotations — DVC-tracked, requires `dvc pull` |
| `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json` | t0004 | Whisper large-v3 baseline numbers to load for comparison tables |

## Key Papers (top 5, with finding most relevant to this task)

(not generated — step skipped)

## Risks Flagged in Research

- **Granite keyword biasing API is unconfirmed**: The exact processor/model parameter for passing
  keyword lists to `ibm-granite/granite-speech-4.1-2b` was not pinned in code research. Must check
  model card before implementing `run_granite_biased.py` — wrong parameter silently degrades to
  unbiased inference.
- **GPU availability required**: Without A100/H100, latency targets are unachievable. CPU runs are
  valid for accuracy metrics only; latency numbers would be non-comparable to the 200 ms target.
- **BCa NaN on production stratum**: ~8 clips in production subset is near-minimum for BCa; NaN
  fallback to percentile bootstrap must be present or metric computation will crash.
- **DVC pull required before inference**: Audio files are not in git. A missing `dvc pull` will
  cause silent 0-clip failures if the directory exists but is empty.
- **Streaming/NAR path unclear**: t0005 estimated 100–200 ms TTFT for Granite but did not confirm a
  streaming decode path or NAR variant. The qualitative assessment in `results_detailed.md` may find
  no streaming support, limiting production viability.
- **Biasing may not match Whisper `initial_prompt` effectiveness**: t0004 showed `initial_prompt`
  gives 5× improvement for Whisper. Granite's shallow-fusion keyword biasing is a different
  mechanism; effectiveness on Rezolve domain terms is unproven.

## Full Detail Available In

- `tasks/t0007_ibm_granite_4_1_benchmark/research/research_papers.md` — (not generated — step
  skipped)
- `tasks/t0007_ibm_granite_4_1_benchmark/research/research_internet.md` — (not generated — step
  skipped)
- `tasks/t0007_ibm_granite_4_1_benchmark/research/research_code.md` — 5 tasks reviewed, 4 cited
