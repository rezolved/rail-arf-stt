# Benchmark Moonshine v2 on Gold-92

## Motivation

Task t0005 (STT model survey) ranked **Moonshine v2** as an **edge-deployment candidate** — the only
**CPU-only open-source STT model** in the survey:

- **No GPU required**: runs on CPU via OnnxRuntime; eliminates cloud infrastructure overhead
- **Ultra-low latency**: 50–258 ms per clip (Tiny/Small/Medium variants), well under 800 ms budget
- **Small model size**: 6× fewer parameters than Whisper large-v3; efficient memory footprint
- **5.3% WER**: competitive with Whisper turbo on general English; VoxPopuli (accented) WER not
  published
- **MIT license**: permissive, fully open-weight

The current production baseline (t0004, Whisper large-v3 + initial_prompt) achieves **94.5% domain
entity accuracy** on gold-92 through vocabulary biasing. Moonshine's key limitation is the **absence
of native contextual biasing**. Instead, Moonshine must use external shallow-fusion adapters (not
yet implemented) to boost entity recall. This task establishes Moonshine's baseline entity accuracy
**without biasing** and assesses the integration feasibility of an external biasing layer.

**Strategic value**: If entity accuracy without biasing is ≥ 46% (Whisper overall baseline) and a
shallow-fusion biasing adapter can be prototyped, Moonshine becomes a viable **edge-deployment
fallback** — low latency, no cloud GPU, minimal infrastructure. This is especially valuable for
devices with limited GPU access or offline deployment scenarios.

## Research Question

**What is Moonshine v2's entity accuracy and latency on gold-92 without native biasing, and is an
external shallow-fusion biasing layer feasible for improving entity recall toward the Whisper
baseline (94.5% domain vocab)?**

Secondary questions:

- How does Moonshine's WER compare to Whisper turbo on gold-92?
- What is Moonshine's action-critical WER (AC-WER) vs. the Whisper baseline (2.5%)?
- Can Moonshine achieve ≤ 200 ms p50 latency on local CPU (warm-up included)?
- Is Moonshine's latency degradation from cold-start to warmed-up inference acceptable for real-time
  voice commerce?

## Scope

### Runs

1. **Moonshine v2 Medium — Batch Mode (No Biasing)**
   - Model: `usefulsensors/moonshine` via HuggingFace (Medium variant, ~4.7M params)
   - Input: all 93 gold-92 clips (PCM-16 mono, 16 kHz)
   - Configuration: default batch inference, OnnxRuntime CPU backend
   - Metrics: WER, entity accuracy (overall + domain vocab), intent preservation, action-critical
     WER, latency p50/p95/p99 (including cold-start warmup)

2. **Moonshine v2 Medium — Shallow Fusion (External Biasing Assessment)**
   - Model: same as above
   - Biasing vocabulary: identical 31 terms from t0004
   - Biasing method: external shallow-fusion adapter (NOT yet implemented; this run assesses
     feasibility and estimates integration effort)
   - Metrics: same as run 1 + feasibility verdict (can shallow fusion be integrated in reasonable
     time?)

### Comparators

**t0004 Baseline (Whisper large-v3 + initial_prompt):**

| Metric | Value |
| --- | --- |
| Entity accuracy (domain vocab) | 94.5% |
| Entity accuracy (overall) | 46.0% |
| WER | 8.5% |
| AC-WER | 2.5% |
| Intent preservation | 98.9% |
| Latency p50 | 6.66 s |

### Registered Metrics

All metrics computed on the **full gold-92 set (93 clips)**, stratified by:

- Overall (93 clips)
- Production subset (8 clips, accented English, "wrong-action" prone)
- Clean-voice subset (remaining 85 clips)

**Per run:**

- `wer_gold92`
- `entity_accuracy_gold92`
- `entity_accuracy_domain_vocab`
- `action_critical_wer_gold92`
- `intent_preservation_gold92`
- `latency_p50_seconds`
- `wrong_action_rate_gold92`

**Custom metrics:**

- Cold-start latency (first clip)
- Warm-up warmup latency (clips 2–5)
- Warmed latency (clips 6–93)
- Production subset entity accuracy (accented English, 8 clips)

### Shallow Fusion Feasibility Assessment

This is a qualitative research + prototyping subtask, not a separate benchmark run:

- Document shallow-fusion implementation approaches (speech-to-speech fusion, lattice rescoring,
  log-linear model, etc.)
- Identify 1–2 candidate open-source shallow-fusion libraries (e.g., `fuse-viterbi`,
  `kaldi-native-io`, custom PyTorch layer)
- Estimate implementation effort in hours
- Estimate latency overhead per clip (5–30 ms estimated)
- Write feasibility verdict: "viable for production", "needs research", or "infeasible within
  budget"

## Approach

### Setup

1. Install `moonshine-vad`, `onnxruntime`, `librosa` (CPU inference path)
2. Load gold-92 clips and ground-truth transcripts from t0001
3. Load t0004 predictions (Whisper large-v3 + initial_prompt) for side-by-side comparison
4. Prepare the 31-term domain vocabulary from t0004 for the biasing assessment

### Implementation Steps

1. **Run 1 (no biasing):** iterate over 93 gold-92 clips, run Moonshine batch transcription on CPU,
   collect predictions + per-clip wall-clock latency (track cold-start vs. warm-up separately)

2. **Run 2 (shallow fusion assessment):** research shallow-fusion libraries, write a shallow-fusion
   adapter prototype (or detailed design doc if time-constrained), estimate latency overhead and
   implementation effort, produce a feasibility report

3. **Metric computation:** WER (normalized Levenshtein), entity accuracy (substring match), domain
   vocab accuracy, AC-WER, intent preservation, latency p50/p95/p99; BCa bootstrap 95% confidence
   intervals on all accuracy metrics

4. **Stratification:** report all metrics on full set, production subset (8 accented clips),
   clean-voice subset

5. **Shallow fusion report:** document the feasibility verdict and effort estimate for downstream
   follow-up tasks

### Compute

**CPU:** Any modern multi-core CPU (Moonshine is OnnxRuntime CPU-native; no GPU required)\
**Budget estimate:** $0 (local compute only)

## Output Specification

### Prediction Assets (1–2 total)

1. `moonshine-v2-medium-gold92` — batch mode, no biasing
   - Schema: `{clip_id, ground_truth, prediction, wer_local, entity_accuracy_local, latency_ms}`
   - Format: JSONL

2. `moonshine-v2-medium-gold92-biasing-assessment` — shallow fusion prototype or design doc
   - Format: markdown + optional code snippets

### Results Files

- `results/results_summary.md` — headline metrics (WER, entity accuracy vs. Whisper baseline,
  latency feasibility, shallow fusion verdict)
- `results/results_detailed.md` — full methodology, per-clip breakdown, stratification, cold-start
  vs. warm-up analysis, shallow fusion feasibility report
- `results/metrics.json` — registered metrics (run 1 only; run 2 is assessment, not metrics)
- `results/costs.json` — `{"total_cost_usd": 0, "breakdown": {}}`
- `results/images/` — comparison bar charts:
  - Entity accuracy (domain vocab): Moonshine vs. Whisper baseline
  - WER: same comparison
  - AC-WER: same comparison
  - Latency distribution: cold-start, warm-up, warmed (histogram or violin plot)

### Key Questions (numbered, falsifiable)

1. **Entity accuracy (domain vocab) without biasing:** Does Moonshine ≥ 46% (Whisper overall
   baseline)?
   - Hypothesis: UNCERTAIN — Moonshine WER is competitive (5.3%), but entity accuracy without
     biasing may lag

2. **WER:** Is Moonshine ≤ 8.5% (Whisper baseline)?
   - Hypothesis: YES — 5.3% reported WER is below Whisper; gold-92 may be slightly higher

3. **Action-critical WER:** Does Moonshine AC-WER ≤ 2.5% (Whisper baseline)?
   - Hypothesis: UNCERTAIN — depends on entity-heavy vs. generic token distribution

4. **Latency:** Is Moonshine p50 ≤ 200 ms on local CPU after warm-up?
   - Hypothesis: YES — Medium variant ~80–150 ms reported; gold-92 segment lengths and local CPU
     speed TBD

5. **Cold-start latency:** Is first-clip latency acceptable for real-time UX?
   - Hypothesis: UNCERTAIN — cold-start may be 500+ ms; production would need pre-warming or caching

6. **Shallow fusion feasibility:** Can a shallow-fusion biasing adapter be integrated in <20 hours
   of effort?
   - Hypothesis: YES — log-linear fusion or lattice rescoring are well-established; open-source
     tools exist

7. **Accented English (production subset):** Does Moonshine entity accuracy > Whisper on 8
   production clips?
   - Hypothesis: UNCERTAIN — no VoxPopuli (accented) WER data for Moonshine

## Dependencies

- **t0001_stt_benchmark:** Gold-92 dataset (93 clips, ground-truth transcripts, entity annotations).
  Required before any inference can run.
- **t0004_vocabulary_biasing_experiment:** Whisper baseline results and the 31-term biasing
  vocabulary. Provides the comparison baseline and domain vocabulary for the shallow fusion
  assessment.

## Expected Assets

- `predictions` asset (count: 1–2) — Moonshine predictions on gold-92 (+ optional shallow fusion
  design/prototype)

## Budget

- **Estimated:** $0 (local CPU compute only)
- No cloud GPU, no paid inference APIs
- Shallow fusion research time budgeted within the task (estimate <3 hours for assessment)

## Success Criteria

1. All 93 clips transcribed successfully on local CPU
2. All registered metrics computed with valid BCa bootstrap confidence intervals
3. Entity accuracy (domain vocab) measured and compared to t0004 baseline (46.0% overall target)
4. Latency p50/p95/p99 measured with cold-start/warm-up breakdown
5. WER and AC-WER measured and compared to Whisper baseline
6. Shallow fusion assessment documented with feasibility verdict and effort estimate
7. Predictions asset created and verified
8. Results document includes side-by-side comparison vs. Whisper baseline and interpretation:
   - If entity accuracy ≥ 46% AND shallow fusion is feasible: Moonshine is viable edge fallback
   - If entity accuracy < 46% OR shallow fusion is not feasible: recommend follow-up direction or
     alternative (Paraformer, Granite with GPU)

## Cross-References

- **t0001_stt_benchmark** — gold-92 dataset (93 clips, held-out regression set, NEVER tune on)
- **t0004_vocabulary_biasing_experiment** — Whisper large-v3 + initial_prompt baseline (WER, entity
  accuracy, 31-term domain vocabulary); defines comparison target and biasing vocabulary
- **t0005_stt_model_survey_brainpowa** — identified Moonshine v2 as edge-deployment candidate;
  documented CPU-only latency, WER, and biasing limitations
- **t0006_nemotron_3_5_benchmark** — parallel benchmark of Nemotron 3.5 (streaming native); results
  from t0006 + t0008 together should form the "streaming-capable fast" + "CPU-only low-cost" leg of
  the candidacy evaluation
- **t0007_ibm_granite_4_1_benchmark** — parallel benchmark of Granite 4.1 (highest WER); results
  from all three (t0006, t0007, t0008) form a comprehensive 3-way comparison
- **brainpowa-realtime-api** integration target — Moonshine findings will inform STTAdapter brick
  implementation (OnnxRuntime CPU backend + optional shallow-fusion adapter)
