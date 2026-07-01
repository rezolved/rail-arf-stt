# Suggestions: `latency-profiling`

12 suggestion(s) in category
[`latency-profiling`](../../../meta/categories/latency-profiling/) **11 open** (2 high, 8
medium, 1 low), **1 closed**.

[Back to all suggestions](../README.md)

---

## High Priority

<details>
<summary>🧪 <strong>Implement granite.py STTAdapter and deploy Granite as production
STT in brainpowa-realtime-api</strong> (S-0014-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0014-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-30 |
| **Source task** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

t0014 confirmed CONDITIONAL YES: replace Parakeet with Granite Speech 4.1 2B, gating on a 2.0
s minimum clip duration. The integration effort is ~50-100 lines (only transcribe() needs
implementing). This task should implement granite.py, add the 2.0 s minimum clip gate to the
streaming pipeline, run the existing brainpowa STT evals, and merge to production. Recommended
task types: experiment-run, answer-question.

</details>

<details>
<summary>🧪 <strong>Optimize Granite Speech 4.1 2B latency to meet 800ms p50
target</strong> (S-0015-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0015-01` |
| **Kind** | experiment |
| **Date added** | 2026-07-01 |
| **Source task** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Granite Speech 4.1 2B achieves the highest entity accuracy (96.25%) across all buffer
intervals but its p50 latency (1.11s–1.23s) exceeds the 800ms production target. A dedicated
task should explore batching, quantization (INT8/FP16), and smaller buffer sizes below 500ms
to determine if the latency gap can be closed without sacrificing entity accuracy.

</details>

## Medium Priority

<details>
<summary>🧪 <strong>Benchmark Moonshine ONNX Medium on gold-92 when UsefulSensors
ships the ONNX export</strong> (S-0008-01)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-01` |
| **Kind** | experiment |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

t0008 used the HuggingFace Transformers CPU backend because moonshine_onnx does not include a
Medium variant. The ONNX export is expected to be ~30ms faster per clip, which would bring
warmed p50 from 233ms to ~200ms and potentially meet the project latency target. Once
UsefulSensors ships an ONNX Medium model, run it on all 93 gold-92 clips using the same
inference harness as t0008 and compare latency p50/p95/p99 and entity accuracy. Recommended
task types: stt-benchmark-run.

</details>

<details>
<summary>🔧 <strong>Implement Novitasari2026 common-word cue injection as a
zero-latency biasing add-on</strong> (S-0003-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-05` |
| **Kind** | technique |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | [`10.48550_arXiv.2604.12398`](../../../tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.12398/) |
| **Categories** | [`entity-correction`](../../../meta/categories/entity-correction/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

Implement the common-word cue approach from Novitasari2026 as a pre-processing step on top of
Rezolve's existing dynamic context injection. The method maps non-standard brand names and
SKUs to phonetically similar common-word anchors, adding them to the bias list without G2P.
Novitasari2026 reported 16.3% reduction in bias-word errors with zero added latency and no
model retraining, and the method is additive to any existing biasing technique. Evaluate on
gold-92 entity accuracy and confirm zero latency impact. Recommended task types:
post-correction-experiment, stt-benchmark-run.

</details>

<details>
<summary>🧪 <strong>Investigate why Parakeet models are unresponsive to buffer
interval changes in WER and entity accuracy</strong> (S-0015-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0015-02` |
| **Kind** | experiment |
| **Date added** | 2026-07-01 |
| **Source task** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

All three Parakeet variants (parakeet-tdt-0.6b-v3, parakeet-unified-en-0.6b,
multitalker-parakeet-streaming-0.6b-v1) show zero variance in WER and entity accuracy across
the 500ms, 750ms, and 1000ms intervals, while latency varies slightly. This suggests the
streaming buffer interval does not influence transcript quality for these models in the tested
range. A targeted ablation at finer intervals (100ms, 250ms) and at the chunk-accumulation
level would clarify whether interval effects are architecturally absent or simply outside the
tested range.

</details>

<details>
<summary>📊 <strong>Measure end-to-end latency of RECOVER and Ron2026 pipelines on
Rezolve infrastructure</strong> (S-0003-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0003-06` |
| **Kind** | evaluation |
| **Date added** | 2026-06-23 |
| **Source task** | [`t0003_literature_review_entity_stt`](../../../overview/tasks/task_pages/t0003_literature_review_entity_stt.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

The survey found that latency estimates for both RECOVER (~+100-200ms) and Ron2026 (~550-650ms
total) are extrapolations from known Whisper Turbo inference speed and GPT-4o API latency, not
empirical measurements. Before confirming either method fits the 800ms p50 budget, measure
actual pipeline latency on Rezolve's production infrastructure at p50 and p95. This is a
prerequisite for any production deployment decision. If GPT-4o API latency exceeds the budget,
evaluate a local 7B model substitute for the LLM-Select step. Recommended task types:
latency-profiling, experiment-run.

</details>

<details>
<summary>🧪 <strong>Measure Granite latency on brainpowa production hardware (CPU
inference path) for edge deployment</strong> (S-0014-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0014-06` |
| **Kind** | experiment |
| **Date added** | 2026-06-30 |
| **Source task** | [`t0014_granite_short_clip_robustness`](../../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

All Granite latency measurements in t0012 and t0014 used Azure H100 NVL GPU (p50 249-251 ms).
The brainpowa-realtime-api production deployment may use CPU inference or a smaller GPU.
Measuring Granite's CPU latency on the actual production server would determine whether the
800 ms p50 constraint holds outside the H100 environment and whether quantization (S-0005-10)
is needed. Recommended task types: experiment-run, answer-question.

</details>

<details>
<summary>🧪 <strong>Moonshine model-size ablation: benchmark tiny, base, and large
variants on gold-92 entity accuracy</strong> (S-0008-02)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0008-02` |
| **Kind** | experiment |
| **Date added** | 2026-06-25 |
| **Source task** | [`t0008_moonshine_v2_benchmark`](../../../overview/tasks/task_pages/t0008_moonshine_v2_benchmark.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

t0008 found that Moonshine v2 Medium (266M params) achieves exactly the same
entity_accuracy_gold92 (21.7%) and entity_accuracy_domain_vocab (9.1%) as the base model (38M
params) from t0004. This contradicts the assumption that a larger model would improve entity
recall. A controlled ablation across all published Moonshine variants (tiny, base,
streaming-medium, and any large variant) would confirm whether the entity accuracy plateau is
a training-distribution gap or a tokenizer/decoder limit, and would determine the optimal
model size for latency/accuracy trade-off before investing in S-0005-04 shallow fusion work.
Recommended task types: stt-benchmark-run, comparative-analysis.

</details>

<details>
<summary>🧪 <strong>Run buffer interval sweep on sub-200ms intervals for
Parakeet-unified to characterize TTFD</strong> (S-0015-04)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0015-04` |
| **Kind** | experiment |
| **Date added** | 2026-07-01 |
| **Source task** | [`t0015_streaming_buffer_interval`](../../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

Parakeet-unified-en-0.6b achieves the best latency among Parakeet models (0.34–0.38s p50) and
competitive WER (9.5%). The current sweep covers only 500ms–1000ms. Extending the sweep to
50ms, 100ms, 200ms intervals would characterize the first-token latency floor and determine
the minimum viable buffer size before transcription quality degrades, enabling tighter
real-time streaming for voice commerce.

</details>

<details>
<summary>📊 <strong>Test entity-biasing mechanisms at scale (1,000+ entity
vocabulary)</strong> (S-0005-06)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-06` |
| **Kind** | evaluation |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`stt-evaluation`](../../../meta/categories/stt-evaluation/), [`latency-profiling`](../../../meta/categories/latency-profiling/) |

The survey reports contextual biasing results on 50–1,800 entity lists. Rezolve's product
catalog scales to 10,000+ SKUs. Test whether Granite 4.1 keyword biasing and Paraformer
deep-biasing maintain performance (latency, entity accuracy) when biasing context grows from
1,800 to 10,000 entities. Measure latency scaling curve and F1 degradation if any. If latency
exceeds budget at production scale, design a retrieval-based filtering pre-pass (e.g.,
retrieve top-100 entities relevant to the speaker/context before biasing) to cap the active
biasing vocabulary. Recommended task types: experiment-run, data-analysis.

</details>

## Low Priority

<details>
<summary>🔧 <strong>Implement quantized variants of Granite/Paraformer for edge and
latency optimization</strong> (S-0005-10)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-10` |
| **Kind** | technique |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

If benchmarking shows that Granite or Paraformer meet accuracy targets but exceed VRAM or
latency budgets at scale, implement quantized (int8/float16) variants using ONNX, TensorRT, or
vLLM to reduce model size and improve inference speed. Moonshine already ships as a
245M-parameter model optimized for edge; quantization could reduce Granite (2B) and Paraformer
(varies) to similar footprints. Measure quantization impact on entity accuracy and latency. If
quantization preserves accuracy within 1–2% while halving latency, quantized variants become
the recommended production deployment. Recommended task types: experiment-run, build-model.

</details>

## Closed

<details>
<summary>✅ <s>Profile Granite 4.1, Paraformer, and Whisper latency under concurrent
request load</s> — covered by <a
href="../../../tasks/t0011_streaming_stt_benchmark/"><code>t0011_streaming_stt_benchmark</code></a>
(S-0005-05)</summary>

| Field | Value |
|---|---|
| **ID** | `S-0005-05` |
| **Kind** | evaluation |
| **Date added** | 2026-06-24 |
| **Source task** | [`t0005_stt_model_survey_brainpowa`](../../../overview/tasks/task_pages/t0005_stt_model_survey_brainpowa.md) |
| **Source paper** | — |
| **Categories** | [`latency-profiling`](../../../meta/categories/latency-profiling/), [`stt-evaluation`](../../../meta/categories/stt-evaluation/) |

The survey reports single-request latencies; production voice-to-action pipelines receive
concurrent requests. Profile all three candidates (Granite, Paraformer, Whisper turbo) on
Rezolve's production infrastructure under 10, 50, and 100 concurrent sessions. Measure TTFT
(time-to-first-token), total latency, p50/p95/p99 percentiles, and VRAM utilization at each
concurrency level. This determines whether Granite/Paraformer can sustain the latency budget
under realistic load, and whether GPU memory becomes the bottleneck. If latency degrades
significantly at >10 concurrent sessions, batch-processing or model quantization strategies
become necessary. Recommended task types: experiment-run, data-analysis.

</details>
