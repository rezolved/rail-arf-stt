---
spec_version: "2"
task_id: "t0007_ibm_granite_4_1_benchmark"
date_completed: "2026-06-25"
---
# Results Detailed — IBM Granite Speech 4.1 2B Benchmark on Gold-92

## Summary

IBM Granite Speech 4.1 2B with keyword biasing was benchmarked on all 93 gold-92 clips from
Rezolve's investor-relations production sessions. The keyword-biased variant achieves 40.2% overall
entity accuracy and 98.5% domain-vocabulary entity accuracy, with WER=8.8% and latency p50=248 ms.
Against the actual production baseline (Parakeet TDT 0.6b-v3, t0009), Granite biased is materially
better on all accuracy metrics: +73% overall entity accuracy, +196% domain-vocab accuracy, −75%
action-critical WER. Against the t0004 Whisper large-v3 reference, Granite biased exceeds Whisper on
domain-vocab accuracy (98.5% vs. 94.5%) and latency (248 ms vs. 6.66 s), but is 5.8 pp below Whisper
on overall entity accuracy (40.2% vs. 46.0%) and 5.7 pp above Whisper on AC-WER (8.2% vs. 2.5%).
Two optimization variants (torch.compile, extended keywords + post-processing) were evaluated; neither
improved over the biased baseline.

**Strategic conclusion**: Granite biased is a credible production replacement for Parakeet. Latency
(248 ms p50) is within the 800 ms voice-to-action budget. A streaming shim accumulating full segments
before inference is sufficient for `transcribe_stream` compatibility. The primary remaining gap vs.
Whisper is overall entity accuracy (−5.8 pp); fine-tuning on Rezolve domain data is the highest-
leverage path to closing it.

## Methodology

**Model**: `ibm-granite/granite-speech-4.1-2b` via HuggingFace Transformers 4.57.6,
`GraniteSpeechForConditionalGeneration` + `AutoProcessor`. Weights loaded from local mirror at
`/home/azureuser/granite-model/granite-speech-4.1-2b` (bfloat16, ~4 GB VRAM).

**Dataset**: 93 WAV clips from `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`.
Ground truth from `ground_truth.jsonl`. Accent-group labelling from `gold_set.jsonl`:
34 production (accented), 46 clean-voice, 13 error-cases. Stereo clips pre-converted to mono via
soundfile channel-averaging before inference.

**Inference pattern**: Sequential per-clip. Prompt text injected via chat template `<|audio|>{prompt}`;
new tokens extracted from `output_ids[:, num_input_tokens:]` and decoded. Per-clip wall-clock latency
measured around `model.generate()`. 2 warmup clips excluded from latency statistics.

**Keyword biasing mechanism**: Prompt-injection shallow fusion. Biased run uses:
`"transcribe the speech to text. Keywords: <31 domain terms>"`. This is Granite's documented
keyword-biasing API; no beam-search or decoder modification is required.

**Optimization variants** (additional runs in `run_granite_optimized.py`):

- *torch.compile*: `torch.compile(model, mode="default")` applied before inference; same biased
  prompt as baseline.
- *Extended keywords + post-processing*: 36-term vocabulary (baseline 31 + 5 phonetic variants) +
  conservative regex post-processing for known misrecognitions (brainpowa, Rezolve, NASDAQ).
- *NAR variant* (`granite-speech-4.1-2b-nar`): loading failed due to transformers 4.57.6
  incompatibility with custom `trust_remote_code` processor — skipped.

**Metric computation**: `code/compute_metrics.py`. WER via `jiwer` (normalized). Entity accuracy:
substring match on annotated entity spans from gold-92. BCa bootstrap CIs: n=10,000 resamples.
Domain vocabulary: 31 terms from t0004 `DOMAIN_VOCAB`. Anomaly clip `error_en_0005` (Cyrillic
ground truth) included with anomaly flag.

**Machine**: Azure H100 NVL (CUDA 12.2), conda env `stt`, transformers 4.57.6. Run date: 2026-06-25.
Inference: ~25 s per 93-clip run. Latency measured on GPU.

## Metrics

### All Variants vs. Baselines

| Variant | EA | EA_DV | WER | AC-WER | IP | Lat p50 |
| --- | --- | --- | --- | --- | --- | --- |
| **Parakeet TDT prod (t0009)** | 23.2% | 33.3% | 15.2% | 33.5% | 87.1% | 0.038 s |
| **Whisper large-v3 + prompt (t0004)** | 46.0% | 94.5% | 8.5% | 2.5% | 98.9% | 6.660 s |
| Granite 4.1 2B — batch (no biasing) | 19.5% | 31.9% | 12.3% | 43.0% | 84.9% | 0.250 s |
| **Granite 4.1 2B — keyword biased** | **40.2%** | **98.5%** | **8.8%** | **8.2%** | **92.5%** | **0.248 s** |
| Granite 4.1 2B + torch.compile | 40.2% | 98.5% | 8.8% | 8.2% | 92.5% | 0.246 s |
| Granite 4.1 2B + ext-keywords + postproc | 39.1% | 100.0% | 9.2% | 10.1% | 91.4% | 0.230 s |

EA = entity_accuracy_gold92. EA_DV = entity_accuracy_domain_vocab. IP = intent_preservation.

### BCa Bootstrap 95% Confidence Intervals (biased variant)

| Metric | Value | CI Low | CI High |
| --- | --- | --- | --- |
| entity_accuracy_gold92 | 40.2% | 30.4% | 50.0% |
| entity_accuracy_domain_vocab | 98.5% | 88.6% | 100% |
| wer_gold92 | 8.8% | 7.1% | 12.6% |
| intent_preservation_gold92 | 92.5% | — | — |
| action_critical_wer_gold92 | 8.2% | — | — |

### Keyword-Biasing Gain (biased vs. batch)

| Metric | Delta |
| --- | --- |
| ΔWER | −3.5 pp |
| ΔEntity accuracy (overall) | +20.7 pp |
| ΔEntity accuracy (domain vocab) | +66.7 pp |

### Stratified Metrics — Granite 4.1 2B keyword biased

| Subset | N | EA | EA_DV |
| --- | --- | --- | --- |
| All | 93 | 40.2% | 97.7% |
| Production (accented) | 34 | 29.4% | 90.0% |
| Clean-voice | 46 | 41.3% | 100.0% |
| Error-cases | 13 | 66.7% | 100.0% |

### Latency (keyword biased, 93 clips, 2 warmup excluded)

| Percentile | Batch | Biased | Compiled | Postproc |
| --- | --- | --- | --- | --- |
| p50 | 0.250 s | 0.248 s | 0.246 s | 0.230 s |
| p95 | 0.421 s | 0.400 s | 0.396 s | 0.384 s |
| p99 | 0.504 s | 0.462 s | 0.455 s | 0.456 s |

## Key Questions

1. **Entity accuracy (domain vocab) ≥ 94.5%?**
   YES — 98.5% (biased). Exceeds Whisper baseline by +4 pp. Hypothesis confirmed.

2. **Overall entity accuracy ≥ 46.0%?**
   NO — 40.2%. 5.8 pp below Whisper. Hypothesis not confirmed. Granite's WER advantage does not
   generalise to overall entity recall without fine-tuning on domain-specific entities.

3. **Keyword biasing improves entity accuracy over no-biasing?**
   YES — +20.7 pp overall EA, +66.7 pp domain-vocab EA. Hypothesis confirmed.

4. **AC-WER ≤ 2.5%?**
   NO — 8.2% biased. 3.3× higher than Whisper baseline. Entity-span words still misrecognised for
   non-domain entities. Hypothesis not confirmed.

5. **Latency p50 ≤ 200 ms?**
   NO — 248 ms biased. Target not met. Postproc variant reaches 230 ms (still above target).
   NAR variant could not be evaluated (transformers 4.57.6 incompatibility).

6. **Accented English (production subset): Granite > Whisper?**
   EA_DV=90.0% on 34 production clips vs. Whisper EA_DV=94.5% overall — slightly below. Overall EA
   on production subset 29.4% vs. Whisper 46.0% overall. Hypothesis not confirmed.

## Streaming Assessment

Granite 4.1 2B is an encoder-decoder (Whisper-like) batch inference model. It has no native
streaming decode path — the full audio segment must be available before decoding begins.

**Streaming shim compatibility with `brainpowa-realtime-api`**: YES, via the accumulate-then-
transcribe pattern. The `STTAdapter.transcribe_stream` default implementation in `base.py:109`
already accumulates all audio chunks and delegates to `transcribe()` once the `None` sentinel
arrives. `GraniteSTT` can implement only `transcribe()` and inherit `transcribe_stream()` for free.
For incremental interim transcripts (like `ParakeetSTT`'s interval re-transcription), the same
pattern applies: accumulate → re-transcribe every `stream_interval_bytes` → yield delta.

**NAR variant** (`ibm-granite/granite-speech-4.1-2b-nar`, non-autoregressive): Loading failed in
transformers 4.57.6 due to a `trust_remote_code` processor resolution bug (`NoneType` attribute name
error in `processing_utils.py:1459`). NAR uses parallel token generation and may achieve sub-200 ms
latency. Requires transformers upgrade or a patched environment to evaluate.

**Integration effort**: ~100 lines (`granite.py` adapter mirroring `parakeet.py`; register in
`factory.py`). Biasing maps naturally: `stt_initial_prompt` → comma-split →
`"Keywords: kw1, kw2, ..."` prompt prefix.

## Analysis

### Biasing Mechanism

Granite's keyword biasing is prompt-injection, not decoder-level beam search. The 31-term domain
vocabulary is appended as `"Keywords: ..."` text in the chat prompt. This is simpler than Parakeet's
NeMo GPU-PB boosting tree and requires no model-level changes. The +66.7 pp domain-vocab gain
confirms the mechanism is effective for Rezolve-domain terms.

### Why Overall EA Trails Whisper

Whisper large-v3 is a 1.5B parameter multilingual model fine-tuned on 680,000 hours of audio.
Granite 4.1 2B, while achieving lower WER on standard benchmarks, appears to underperform on the
long-tail entity recall that drives overall entity accuracy on gold-92 (investor-relations,
accented English, product names outside the keyword list). The 5.8 pp gap is likely closed by
fine-tuning on Rezolve-domain transcripts.

### Optimization Variants

- **torch.compile**: Identical accuracy to biased baseline; 2 ms latency saving. Not worth the added
  complexity (compilation overhead at startup, potential incompatibility with NeMo if co-deployed).
- **Extended keywords + post-processing**: EA_DV reaches 100.0% (all domain-vocab terms captured) at
  the cost of −1.1 pp overall EA and +1.9 pp AC-WER. The regex rules overcorrect on non-domain
  words phonetically similar to domain terms. Tighter patterns could recover the quality gap.

### Production Viability

Granite biased is a viable Parakeet replacement: every accuracy metric improves substantially, and
248 ms p50 is within the 800 ms voice-to-action budget. The remaining AC-WER gap vs. Whisper (8.2%
vs. 2.5%) means approximately 1 in 12 clips has a wrong entity transcribed in an action-critical
span — acceptable for a V1 rollout with monitoring, but should be tracked in production.

## Limitations

1. **NAR variant not evaluated**: transformers 4.57.6 incompatible with `granite-speech-4.1-2b-nar`
   custom processor. Sub-200 ms latency target may be achievable with NAR; requires a newer
   transformers version.

2. **No per-clip Whisper comparison**: t0004 Whisper predictions exist but per-clip side-by-side
   was not computed. Stratified Whisper baselines use t0004 aggregate numbers.

3. **Single inference run per variant**: no ensemble, no temperature sampling. Results represent
   greedy decoding out-of-the-box.

4. **wrong_action_rate proxy**: computed as `1 − intent_preservation`. No downstream routing layer
   present; this is the best available approximation without gold action labels.

5. **Latency on H100 NVL**: production deployment may use a different GPU or CPU, changing the
   latency profile.

6. **Post-processing regexes not tuned**: the 7 regex rules in the postproc variant were written
   conservatively. A tuned set on held-out clips (not gold-92) could recover the −1.1 pp EA loss.

## Verification

- 93/93 clips transcribed, batch and biased runs (0 failures)
- 93/93 clips transcribed, torch.compile and postproc optimization runs
- BCa bootstrap CIs computed (n=10,000 resamples); 1 degenerate CI (EA_DV all-ones) fell back to
  percentile method
- `ruff check tasks/t0007_ibm_granite_4_1_benchmark/code/` — PASSED

## Files Created

- `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_batch_transcripts.json` — 93-clip batch transcripts with latency
- `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_biased_transcripts.json` — 93-clip keyword-biased transcripts
- `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_compiled_biased_transcripts.json` — torch.compile variant
- `tasks/t0007_ibm_granite_4_1_benchmark/data/granite_postproc_biased_transcripts.json` — ext-keywords + postproc variant
- `tasks/t0007_ibm_granite_4_1_benchmark/data/analysis_output.json` — per-clip breakdown, biasing gain
- `tasks/t0007_ibm_granite_4_1_benchmark/results/metrics.json` — registered metrics, all 4 variants
- `tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_batch.py` — batch inference script
- `tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_biased.py` — keyword-biased inference script
- `tasks/t0007_ibm_granite_4_1_benchmark/code/run_granite_optimized.py` — optimization variants (NAR, compile, postproc)
- `tasks/t0007_ibm_granite_4_1_benchmark/code/compute_metrics.py` — metric computation with BCa CIs
- `tasks/t0007_ibm_granite_4_1_benchmark/code/constants.py` — model ID, domain vocabulary, prompts
- `tasks/t0007_ibm_granite_4_1_benchmark/code/paths.py` — centralized path constants

## Next Steps

1. **Evaluate NAR variant** — upgrade transformers to ≥4.58 on Azure server; re-run latency test;
   NAR may bring p50 below 200 ms target.
2. **Implement `GraniteSTT` adapter** — `brainpowa-realtime-api/src/.../pipeline/stt/granite.py`;
   ~100 lines; register in `factory.py`; maps `stt_initial_prompt` → keyword prompt.
3. **Fine-tune on Rezolve domain data** — highest-leverage path to closing the 5.8 pp overall EA
   gap vs. Whisper; use gold-92 as held-out eval (NEVER for training).
4. **Tune postproc regexes** — tighter patterns on a dev split could recover the −1.1 pp EA loss
   and make the 100% EA_DV postproc variant production-ready.
