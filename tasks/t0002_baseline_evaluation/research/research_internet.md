---
spec_version: "1"
task_id: "t0002_baseline_evaluation"
research_stage: "internet"
searches_conducted: 12
sources_cited: 16
papers_discovered: 4
date_completed: "2026-06-23"
status: "complete"
---
## Task Objective

Establish baseline metrics for the Rezolve STT research project by running Deepgram Nova-2 (the
current production endpoint) and Whisper Large v3 (the leading open-source alternative) on the
gold-92 benchmark: 93 annotated WAV clips from Rezolve production voice sessions in the
investor-relations domain with accented English speakers. All five registered project metrics must
be computed with BCa bootstrap 95% confidence intervals (n=10,000 resamples): entity accuracy on
action-critical spans (`entity_accuracy_gold92`), full-transcript WER (`wer_gold92`),
action-critical WER (`action_critical_wer_gold92`), intent preservation
(`intent_preservation_gold92`), and end-to-end latency p50 (`latency_p50_seconds`). A paired BCa
bootstrap significance test comparing Whisper Large v3 vs. Deepgram on `entity_accuracy_gold92` is
the primary deliverable.

## Gaps Addressed

From `research_papers.md` Gaps and Limitations:

1. **No published baselines for comparison** — **Resolved**. Found quantitative WER benchmarks for
   both systems. Deepgram Nova-2 achieves a median WER of **8.4%** across real-world domains in
   Deepgram's own evaluations [Deepgram-Nova2-2023]. Whisper Large v3 achieves **2.7% WER** on
   LibriSpeech test-clean, **5.2% WER** on LibriSpeech test-other [HF-Whisper-LargeV3], and a mean
   WER of **7.44** on the open-asr-leaderboard across diverse test conditions. However, both sets of
   numbers are on general-English benchmarks, not on accented investor-relations audio, so gold-92
   results will likely diverge — this caveat remains for the compare-literature step.

2. **No evaluation methodology papers** — **Resolved**. Found `scipy.stats.bootstrap` with
   `method='BCa'` as the canonical Python implementation for BCa confidence intervals
   [SciPy-Bootstrap]. Found Liu & Peng (2020) on blockwise bootstrap for ASR significance testing
   [Liu2020] — relevant when utterances from the same speaker are correlated. Also found a
   ResearchGate preprint (Bisani & Ney, 2004) on bootstrap estimates specifically for ASR confidence
   intervals, confirming standard practice.

3. **No domain-specific STT evaluation papers** — **Partially resolved**. Found papers covering NER
   from speech in noisy business telephone transcripts [Kubis2022-ACL] and a 2020 LREC survey of
   named entity recognition from speech [Caubriere2020]. No ecommerce or investor-relations specific
   STT evaluation papers were found. Whether 93 clips is adequate for BCa at n=10,000 resamples is
   addressed methodologically: BCa is valid for small n; with n=93 paired samples the CI width will
   be wider than for larger corpora but the method is unbiased.

4. **Deepgram not academically documented** — **Partially resolved**. No peer-reviewed paper on
   Deepgram Nova-2 architecture exists. Deepgram's own blog [Deepgram-Nova2-2023] and developer
   documentation [Deepgram-Keywords-Docs] are non-peer-reviewed but are the authoritative primary
   sources. The keyword-boosting API is documented, including limitations for Nova-2 (max 100
   keywords, intensifier parameter format).

## Search Strategy

**Sources searched**: Deepgram developer documentation, Hugging Face model hub, arXiv, ACL
Anthology, PyPI, GitHub, SciPy documentation, ResearchGate, Northflank blog, VexaScribe blog, Modal
blog, Papers With Code.

**Queries executed** (12 total):

*Pass 1 — Gap-targeted queries:*

1. `Deepgram Nova-2 API authentication transcription endpoint Python SDK 2025`
2. `openai-whisper large-v3 Python inference audio files WER benchmark 2024 2025`
3. `BCa bootstrap confidence intervals WER word error rate Python implementation scipy`
4. `jiwer WER word error rate Python STT evaluation library usage examples`

*Pass 2 — Broadening queries:*

5. `Deepgram Nova-2 WER benchmark accuracy comparison 2024 entity keyword boosting`
6. `STT entity accuracy evaluation named entity recognition speech recognition ecommerce domain`
7. `Whisper large-v3 accented English non-native speaker WER performance`
8. `Deepgram keyword boosting custom vocabulary injection API transcription accuracy`

*Pass 3 — Snowball queries prompted by findings:*

9. `Whisper large-v3 latency inference speed CPU GPU seconds per audio clip`
10. `Deepgram Nova-2 vs Whisper large-v3 comparison accuracy WER benchmark 2024`
11. `bootstrap hypothesis test ASR speech recognition paired samples significance NLP evaluation`
12. `Radford 2023 Whisper robust speech recognition large-scale weak supervision WER results`

**Date range**: 2019–2026. No lower cutoff for foundational papers.

**Inclusion criteria**: Sources must provide at least one of: (a) quantitative WER or entity
accuracy benchmarks for Deepgram Nova-2 or Whisper Large v3, (b) Python API/SDK usage patterns for
either system, (c) implementation details for BCa bootstrap CI or paired significance tests for ASR,
(d) STT evaluation methodology for named entity or span-level accuracy, (e) latency characterization
for either system. Excluded: real-time streaming-only evaluations, non-English ASR papers, TTS
literature.

**Search iterations**: Pass 3 queries were prompted by: query 10 uncovering the Deepgram vs. Whisper
whitepaper PDF; query 11 uncovering Liu & Peng (2020) blockwise bootstrap paper on arXiv; query 12
confirming the Whisper paper PMLR proceedings URL and arXiv ID for the Discovered Papers section.

## Key Findings

### Deepgram Nova-2 Benchmarks and API

Deepgram Nova-2 reports a median WER of **8.4%** across real-world domains (podcast, video/media,
meeting, phone call), representing a **36.4% relative WER improvement** over Whisper Large (not
Large v3) in Deepgram's own benchmarking white paper [Deepgram-Nova2-2023] (non-peer-reviewed,
vendor-produced). Entity-specific improvements from Nova-1 include a **15% relative reduction in
entity error rate** and **22.6% improvement in punctuation accuracy**. These numbers are from a
vendor white paper and may not generalise to accented investor-relations audio.

For API integration, Deepgram Nova-2 is accessed via HTTPS POST to
`https://api.deepgram.com/v1/listen` with header `Authorization: Token YOUR_API_KEY`. The Python SDK
(v3+) uses `DeepgramClient().listen.v1.media.transcribe_file()` for pre-recorded audio
[Deepgram-SDK-GH]. The response object exposes per-word confidence scores, timestamps, and the full
transcript at `response.results.channels[0].alternatives[0]`. Pricing is **$0.0043/minute** for
pre-recorded audio, making the 93-clip gold-92 set cost approximately **$0.08–$0.10** total.

Keyword boosting is available for Nova-2 via the `keywords=WORD:INTENSIFIER` query parameter (max
100 keywords, intensifier is an exponential multiplier defaulting to 1) [Deepgram-Keywords-Docs].
The task baseline run uses **no keyword boosting** — that is reserved for a later improvement task.
Nova-3 has superseded Nova-2 with keyterm prompting instead of keyword boosting and achieves **5.26%
batch WER**, but Nova-2 is the current Rezolve production endpoint and must be the baseline.

**Best practice**: Set `smart_format=True` and `punctuate=True` in the transcription request to get
normalised output comparable to Whisper's default output. Record `response.metadata.duration` for
latency measurement alongside wall-clock timing.

### Whisper Large v3 Benchmarks and Inference

Whisper Large v3 (1.55 billion parameters, 128 Mel bins) achieves **2.7% WER on LibriSpeech
test-clean** and **5.2% WER on LibriSpeech test-other** [HF-Whisper-LargeV3]. Its mean WER on the
open-asr-leaderboard across diverse datasets is **7.44**. These benchmarks are on clean or
moderately accented read speech. On non-native spontaneous English (LearnerVoice dataset), vanilla
Whisper Large v3 achieves **19.18% WER** [Peng2025] — a figure relevant to the gold-92 benchmark
which contains accented English speakers.

The openai-whisper package (MIT licence) provides the canonical CLI and Python API. For Python
inference, the `transformers` pipeline API (Hugging Face) is the recommended approach for
production-quality inference with GPU acceleration [HF-Whisper-LargeV3]:

```python
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-large-v3",
    torch_dtype=torch.float16)
pipe = pipeline("automatic-speech-recognition", model=model, processor=processor)
result = pipe("audio.wav")
```

For CPU-only inference, `faster-whisper` (CTranslate2 backend) provides **up to 4× speedup** over
the original openai-whisper package at the same accuracy, with INT8 quantization reducing VRAM from
~10 GB to ~2.5 GB [FasterWhisper-GH]. On an RTX 4070, large-v3 runs at **~12× real-time** with
faster-whisper. On CPU (M5 Pro), ~3× real-time. On CPU alone, a 10-second clip takes approximately
**30–100 seconds** with the standard openai-whisper package — for 93 clips this implies 46–155
minutes total, confirming the task description's estimate.

**Hypothesis**: Whisper Large v3's accented English WER on gold-92 may exceed its LibriSpeech
benchmark by a factor of 2–4× (projected: 8–20% WER) given the LearnerVoice evidence of 19.18% WER
on non-native spontaneous speech. The paired BCa test will determine whether Deepgram Nova-2 or
Whisper is better on entity accuracy for this specific domain.

**Best practice**: Pass `language="en"` explicitly to prevent Whisper from misclassifying accented
speech as a non-English language — a known failure mode documented in the Hugging Face model card
[HF-Whisper-LargeV3].

### BCa Bootstrap CI and Significance Testing

`scipy.stats.bootstrap` (available since SciPy 1.7) implements BCa as the default method
[SciPy-Bootstrap]. BCa is the bias-corrected and accelerated variant that adjusts percentile limits
for second-order effects. Usage for a scalar statistic:

```python
from scipy import stats
import numpy as np

def mean_stat(x, axis):
    return np.mean(x, axis=axis)

boot = stats.bootstrap((per_utterance_scores,), mean_stat,
                       n_resamples=10000, method='BCa', random_state=42)
ci_low, ci_high = boot.confidence_interval
```

For paired comparisons (Whisper vs. Deepgram on the same 93 utterances), use `paired=True`:

```python
def paired_diff(x, y, axis):
    return np.mean(x - y, axis=axis)

boot = stats.bootstrap((whisper_scores, deepgram_scores), paired_diff,
                       n_resamples=10000, method='BCa', paired=True, random_state=42)
```

A BCa CI that excludes zero constitutes a one-sample significance test at α=0.05 for the null
hypothesis of no difference [SciPy-Bootstrap].

Liu & Peng (2020) [Liu2020] show that the standard i.i.d. bootstrap is biased when utterances from
the same speaker are correlated. For gold-92, if multiple clips come from the same speaker,
blockwise bootstrap on speaker-grouped blocks is more statistically sound. However, with only 93
clips, the block size must be small (2–3 clips per block) and the power will be lower. The
implementation choice — standard vs. blockwise — should be documented in `metadata.json`.

**Best practice (from Liu & Peng 2020)**: If gold-92 has speaker metadata grouping utterances by
speaker, use blockwise bootstrap (block = speaker session) for the significance test. If all
utterances are from distinct speakers, standard BCa is appropriate.

### WER Computation with jiwer

`jiwer` (maintained by Jitsi, backed by RapidFuzz C++ engine) is the de facto standard Python
library for WER computation in STT evaluation [JiWER-GH]. It supports WER, MER, WIL, WIP, and CER.
Basic usage:

```python
from jiwer import wer, process_words
# Single pair
error = wer("reference text", "hypothesis text")
# Batch
error = wer(["ref1", "ref2"], ["hyp1", "hyp2"])
# Word-level alignment for debugging
alignment = process_words(references, hypotheses)
```

For action-critical WER, `process_words` alignment output allows filtering to only words within
annotated entity spans before computing the substitution/deletion/insertion counts.

**Contradiction with research_papers.md**: The prior document states entity accuracy must be
"implemented from first principles without a citable methodological reference." This is partially
incorrect — the ACL Anthology paper by Caubrière et al. (2020) [Caubriere2020] defines entity error
rate (EER) as 1 − entity recall, where an entity is correct only if all constituent words are
correctly decoded. This is the standard definition from the NER-from-speech community and can serve
as the methodological reference.

### Entity Accuracy Metric Definition

The NER-from-speech community defines two span-level metrics [Caubriere2020]:

* **Entity recall** (ER): fraction of reference entity spans where all constituent words are
  correctly transcribed (exact match, no partial credit).
* **Entity Error Rate** (EER): 1 − ER. Equivalent to `entity_accuracy_gold92 = 1 − EER`.

For the task's `action_critical_wer_gold92`, the standard approach is to compute WER restricted to
tokens within annotated entity spans — i.e., filter the reference and hypothesis word lists to only
entity-span tokens, then run standard WER. The jiwer `process_words` output provides word-level
alignment needed to identify which reference positions correspond to entity spans.

The paper WhisperNER (2024) [WhisperNER2024] jointly models ASR and NER in a single end-to-end
system with near-perfect entity recall under clean conditions, but that is out of scope for this
baseline task.

### Latency Measurement Protocol

For Deepgram, `latency_p50_seconds` must be measured as wall-clock time from audio submission to
transcript receipt. The SDK does not expose internal queue time separately; the entire round-trip
includes network overhead. The Deepgram documentation [Deepgram-Timestamps] notes that
`response.metadata.duration` is audio duration, not processing time — wall-clock timing via
`time.perf_counter()` before and after the API call is the correct approach.

For Whisper Local, latency is hardware-dependent. The metadata.json must record: GPU/CPU model, RAM,
`openai-whisper` or `faster-whisper` package version, and quantization mode. The two systems'
latency figures are **not directly comparable** (Deepgram includes network; Whisper is local) — the
metadata must document this.

**Best practice**: Time each clip individually and compute p50 from all 93 measurements. For
Deepgram, retry on network timeouts (add exponential back-off with 3 retries) and log any failed
clips for exclusion.

## Methodology Insights

* **Use `scipy.stats.bootstrap` with `method='BCa'`, `n_resamples=10000`, `paired=True`** for the
  primary entity accuracy significance test [SciPy-Bootstrap]. This is the project-specified method
  and is directly supported by the library.

* **jiwer batch WER** is the most efficient approach — pass all 93 reference/hypothesis pairs as
  lists rather than looping. Use `process_words` for per-utterance alignment data [JiWER-GH].

* **Deepgram SDK version**: Use `deepgram-sdk>=3.0` (v6 Python SDK) not the legacy v2 client. The
  API endpoint changed from `listen.prerecorded` to `listen.v1.media.transcribe_file`
  [Deepgram-SDK-GH].

* **Whisper language pinning**: Always pass `language="en"` to avoid accent → language
  misclassification [HF-Whisper-LargeV3]. This is a known production failure mode on accented
  speakers.

* **faster-whisper as the inference backend**: For the gold-92 run, use `faster-whisper` rather than
  `openai-whisper` if GPU is available — 4× speedup at identical accuracy. Load with
  `WhisperModel("large-v3", device="cuda", compute_type="float16")` [FasterWhisper-GH].

* **Raw output preservation**: Save `deepgram_transcripts.json` and `whisper_transcripts.json`
  before metric computation. For Deepgram, save the full response dict (including word-level
  confidences and timestamps). For Whisper, save the full `result` dict from the pipeline output
  (includes segments with start/end times and per-segment confidence if using `transformers`
  pipeline with `return_timestamps=True`).

* **BCa degenerate case**: `scipy.stats.bootstrap` may return NaN for the BCa CI if all
  per-utterance scores are identical (e.g., all entity accuracy = 1.0). Add a fallback to
  `method='percentile'` and log a warning when this occurs [SciPy-Bootstrap].

* **Hypothesis to test**: Based on LearnerVoice benchmark evidence (Whisper Large v3: 19.18% WER on
  non-native English), Whisper may *underperform* Deepgram on raw WER for gold-92's accented
  speakers despite outperforming on clean benchmarks. Entity accuracy could diverge from WER —
  Deepgram's 15% relative entity error rate improvement (Nova-1→Nova-2) suggests it is specifically
  optimised for named-entity transcription, which may advantage it on gold-92's IR entities.

* **Blockwise bootstrap consideration**: Liu & Peng (2020) recommend blockwise bootstrap when
  evaluation utterances share speakers. The task description does not specify whether gold-92 clips
  are multi-speaker or single-speaker. Verify accent-group labels in the dataset schema — if groups
  correspond to speakers, use blockwise bootstrap grouped by accent/speaker [Liu2020].

## Discovered Papers

### [Radford2023]

* **Title**: Robust Speech Recognition via Large-Scale Weak Supervision
* **Authors**: Radford, A. et al.
* **Year**: 2023
* **DOI**: `10.48550/arXiv.2212.04356`
* **URL**: https://proceedings.mlr.press/v202/radford23a.html
* **Suggested categories**: `whisper-finetuning`, `stt-evaluation`
* **Why download**: Foundational Whisper paper. Provides the published WER benchmarks for Whisper
  Large v3 on LibriSpeech, Common Voice, and other standard datasets. Directly required for the
  compare-literature step (step 13) of this task.

### [Liu2020]

* **Title**: Statistical Testing on ASR Performance via Blockwise Bootstrap
* **Authors**: Liu, Z., Peng, F.
* **Year**: 2020
* **DOI**: `10.21437/Interspeech.2020-1158`
* **URL**: https://arxiv.org/abs/1912.09508
* **Suggested categories**: `stt-evaluation`
* **Why download**: Methodological reference for ASR significance testing. Directly addresses the
  "no evaluation methodology papers" gap from research_papers.md. Justifies or argues against
  standard BCa bootstrap depending on speaker correlation structure in gold-92.

### [Caubriere2020]

* **Title**: Where Are We in Named Entity Recognition from Speech?
* **Authors**: Caubrière, A. et al.
* **Year**: 2020
* **DOI**: `10.5281/zenodo.3534395`
* **URL**: https://aclanthology.org/2020.lrec-1.556/
* **Suggested categories**: `stt-evaluation`, `entity-correction`
* **Why download**: Defines entity error rate (EER) and entity recall as standard metrics for NER
  from speech. Provides the methodological reference for the `entity_accuracy_gold92` metric
  computation that research_papers.md noted was missing.

### [WhisperNER2024]

* **Title**: WhisperNER: Unified Open Named Entity and Speech Recognition
* **Authors**: Ashkenazi, O. et al.
* **Year**: 2024
* **DOI**: `10.48550/arXiv.2409.08107`
* **URL**: https://arxiv.org/abs/2409.08107
* **Suggested categories**: `entity-correction`, `stt-evaluation`
* **Why download**: State-of-the-art joint ASR+NER system directly relevant to future entity
  post-correction tasks. Contextualises the upper bound on entity recall achievable with end-to-end
  models vs. pipeline approaches like this baseline.

## Recommendations for This Task

1. **Use `deepgram-sdk>=3.0` with `listen.v1.media.transcribe_file`** — the new SDK interface
   replaces the legacy `listen.prerecorded` client used in older tutorials. Set `smart_format=True`,
   `punctuate=True`, and measure wall-clock latency with `time.perf_counter()` around each API call
   [Deepgram-SDK-GH].

2. **Use `faster-whisper` with `WhisperModel("large-v3")` on GPU** — 4× speedup over openai-whisper
   at identical accuracy. Always pass `language="en"` to prevent accent misclassification
   [FasterWhisper-GH]. If only CPU is available, budget 46–155 minutes for 93 clips.

3. **Compute all WER metrics with jiwer** — use `process_words` for per-utterance alignment to
   isolate entity-span tokens for `action_critical_wer_gold92`. Batch all 93 pairs in a single call
   for efficiency [JiWER-GH].

4. **Compute BCa CIs with `scipy.stats.bootstrap(method='BCa', n_resamples=10000, paired=True)`** —
   this is the standard implementation and directly matches the task specification
   [SciPy-Bootstrap]. Add NaN fallback to percentile method for degenerate distributions.

5. **Verify speaker structure before choosing standard vs. blockwise bootstrap** — if multiple clips
   share a speaker (detectable from accent-group metadata), Liu & Peng (2020) [Liu2020] recommend
   blockwise bootstrap. Document the choice in `metadata.json`.

6. **Use the Caubrière et al. (2020) EER definition for entity accuracy** — an entity phrase is
   correct only if all constituent words are correctly transcribed (exact match). This resolves the
   "no methodological reference" gap from research_papers.md [Caubriere2020].

7. **Add Radford et al. (2023) to the corpus before step 13** — the compare-literature step requires
   published Whisper WER benchmarks to compare against gold-92 results [Radford2023].

8. **Do not enable keyword boosting in the baseline run** — keyword boosting is a Nova-2-specific
   feature (max 100 keywords, intensifier parameter) evaluated in a separate task. The baseline must
   use default settings for reproducibility [Deepgram-Keywords-Docs].

## Tool and Library Landscape

| Tool | Version | Purpose | Notes |
| --- | --- | --- | --- |
| `deepgram-sdk` | ≥3.0 (Python v6) | Deepgram Nova-2 API calls | `listen.v1.media.transcribe_file` |
| `openai-whisper` | latest | Whisper Large v3 inference | Canonical but slow on CPU |
| `faster-whisper` | latest | Whisper Large v3 inference | 4× faster, same accuracy |
| `jiwer` | ≥3.0 | WER, CER, MER computation | RapidFuzz C++ backend |
| `scipy` | ≥1.7 | BCa bootstrap CIs | `scipy.stats.bootstrap` |
| `transformers` | ≥4.35 | Whisper via HF pipeline | GPU-optimised |
| `torch` | ≥2.0 | GPU inference backend | Required for transformers |

## Source Index

### [Deepgram-Nova2-2023]

* **Type**: blog
* **Title**: Introducing Nova-2: The Fastest, Most Accurate Speech-to-Text API
* **Author/Org**: Deepgram
* **Date**: 2023-11
* **URL**: https://deepgram.com/learn/nova-2-speech-to-text-api
* **Peer-reviewed**: no
* **Relevance**: Primary quantitative source for Nova-2 WER (8.4% median), entity error rate
  improvement (15% relative vs. Nova-1), and pricing ($0.0043/min). Vendor-produced benchmark
  report; treat with appropriate caution.

### [Deepgram-SDK-GH]

* **Type**: repository
* **Title**: deepgram-python-sdk — Official Python SDK for Deepgram
* **Author/Org**: Deepgram
* **Date**: 2024-01
* **URL**: https://github.com/deepgram/deepgram-python-sdk
* **Last updated**: 2026-06
* **Peer-reviewed**: no
* **Relevance**: Authoritative implementation reference for `listen.v1.media.transcribe_file`,
  authentication patterns, and response format (words, confidence, timestamps).

### [Deepgram-Keywords-Docs]

* **Type**: documentation
* **Title**: Keywords — Deepgram Docs
* **Author/Org**: Deepgram
* **Date**: 2024-01
* **URL**: https://developers.deepgram.com/docs/keywords
* **Last updated**: 2025
* **Peer-reviewed**: no
* **Relevance**: Defines keyword boosting parameter format for Nova-2, max-100 keyword limit, and
  intensifier mechanics. Needed to document what is *not* enabled in the baseline run.

### [HF-Whisper-LargeV3]

* **Type**: documentation
* **Title**: openai/whisper-large-v3 — Hugging Face Model Card
* **Author/Org**: OpenAI / Hugging Face
* **Date**: 2023-11
* **URL**: https://huggingface.co/openai/whisper-large-v3
* **Last updated**: 2024
* **Peer-reviewed**: no
* **Relevance**: Published WER benchmarks (2.7% LibriSpeech test-clean, 5.2% test-other, mean 7.44
  on open-asr-leaderboard), Python inference example, and note on disparate accent/demographic
  performance.

### [SciPy-Bootstrap]

* **Type**: documentation
* **Title**: scipy.stats.bootstrap — SciPy Documentation
* **Author/Org**: SciPy Project
* **Date**: 2021-07
* **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
* **Last updated**: 2026
* **Peer-reviewed**: no
* **Relevance**: API reference for BCa bootstrap CI computation. Documents `method='BCa'`,
  `n_resamples`, `paired=True` parameters. Implementation guide for all five metric CIs.

### [JiWER-GH]

* **Type**: repository
* **Title**: jiwer — Evaluate your speech-to-text system
* **Author/Org**: Jitsi / Jørgen Holm
* **Date**: 2019
* **URL**: https://github.com/jitsi/jiwer
* **Last updated**: 2025
* **Peer-reviewed**: no
* **Relevance**: Standard Python library for WER/CER/MER. Batch evaluation of all 93 clip pairs.
  Word-level alignment via `process_words` enables entity-span WER computation.

### [FasterWhisper-GH]

* **Type**: repository
* **Title**: faster-whisper — Faster Whisper transcription with CTranslate2
* **Author/Org**: SYSTRAN
* **Date**: 2023-04
* **URL**: https://github.com/SYSTRAN/faster-whisper
* **Last updated**: 2026
* **Peer-reviewed**: no
* **Relevance**: CTranslate2-backed Whisper implementation providing 4× speedup and INT8
  quantization. Recommended inference backend for large-v3 on GPU; documented 12× real-time on RTX
  4070\.

### [Liu2020]

* **Type**: paper
* **Title**: Statistical Testing on ASR Performance via Blockwise Bootstrap
* **Authors**: Liu, Z., Peng, F.
* **Year**: 2020
* **DOI**: `10.21437/Interspeech.2020-1158`
* **URL**: https://arxiv.org/abs/1912.09508
* **Peer-reviewed**: yes (Interspeech 2020)
* **Relevance**: Demonstrates that standard i.i.d. bootstrap is biased for ASR significance testing
  when utterances share speaker/session correlation. Provides blockwise bootstrap as the
  methodologically sound alternative — directly relevant to gold-92 if clips share speakers.

### [Radford2023]

* **Type**: paper
* **Title**: Robust Speech Recognition via Large-Scale Weak Supervision
* **Authors**: Radford, A. et al.
* **Year**: 2023
* **DOI**: `10.48550/arXiv.2212.04356`
* **URL**: https://proceedings.mlr.press/v202/radford23a.html
* **Peer-reviewed**: yes (ICML 2023)
* **Relevance**: Foundational Whisper paper with published WER on 25+ benchmarks. Required for the
  compare-literature step (step 13) to contextualise gold-92 Whisper results.

### [Caubriere2020]

* **Type**: paper
* **Title**: Where Are We in Named Entity Recognition from Speech?
* **Authors**: Caubrière, A. et al.
* **Year**: 2020
* **DOI**: `10.5281/zenodo.3534395`
* **URL**: https://aclanthology.org/2020.lrec-1.556/
* **Peer-reviewed**: yes (LREC 2020)
* **Relevance**: Defines entity error rate (EER = 1 − entity recall) and the all-or-nothing entity
  span accuracy metric. Methodological reference for `entity_accuracy_gold92` computation.

### [WhisperNER2024]

* **Type**: paper
* **Title**: WhisperNER: Unified Open Named Entity and Speech Recognition
* **Authors**: Ashkenazi, O. et al.
* **Year**: 2024
* **DOI**: `10.48550/arXiv.2409.08107`
* **URL**: https://arxiv.org/abs/2409.08107
* **Peer-reviewed**: no (arXiv preprint)
* **Relevance**: Joint ASR+NER system that represents the state-of-the-art upper bound on entity
  accuracy from speech. Contextualises the gap between pipeline (this baseline) and end-to-end
  entity-aware approaches.

### [Peng2025]

* **Type**: paper
* **Title**: Automatic Speech Recognition for Non-Native English: Accuracy and Disfluency Handling
* **Authors**: Peng, S. et al.
* **Year**: 2025
* **DOI**: `10.48550/arXiv.2503.06924`
* **URL**: https://arxiv.org/pdf/2503.06924
* **Peer-reviewed**: no (arXiv preprint)
* **Relevance**: Reports Whisper Large v3 achieves 19.18% WER on LearnerVoice (non-native English
  spontaneous speech) — key calibration for expected gold-92 WER on accented speakers.

### [Deepgram-Timestamps]

* **Type**: documentation
* **Title**: Working with Timestamps, Utterances, and Speaker Diarization in Deepgram
* **Author/Org**: Deepgram
* **Date**: 2023
* **URL**:
  https://deepgram.com/learn/working-with-timestamps-utterances-and-speaker-diarization-in-deepgram
* **Last updated**: 2025
* **Peer-reviewed**: no
* **Relevance**: Clarifies that `response.metadata.duration` is audio duration, not processing
  latency. Essential for correct `latency_p50_seconds` measurement implementation.

### [Deepgram-Benchmarks]

* **Type**: blog
* **Title**: Speech-to-Text API Benchmarks: Accuracy, Speed, and Cost Compared
* **Author/Org**: Deepgram
* **Date**: 2023
* **URL**: https://deepgram.com/learn/speech-to-text-benchmarks
* **Peer-reviewed**: no
* **Relevance**: Provides broader context on Nova-2 performance across vendor comparisons; notes
  Nova-2's 36.4% relative WER improvement over Whisper Large (non-v3) in Deepgram's own evaluation.

### [Northflank-STT-2026]

* **Type**: blog
* **Title**: Best open source speech-to-text (STT) model in 2026 (with benchmarks)
* **Author/Org**: Northflank
* **Date**: 2026-01
* **URL**: https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks
* **Peer-reviewed**: no
* **Relevance**: Independent benchmark survey of Whisper Large v3 and alternatives on real-world
  audio. Contextualises vendor-reported WER numbers against third-party evaluations.

### [Kubis2022-ACL]

* **Type**: paper
* **Title**: An Effective, Performant Named Entity Recognition System for Noisy Business Telephone
  Conversation Transcripts
* **Authors**: Kubis, M. et al.
* **Year**: 2022
* **DOI**: `10.18653/v1/2022.wnut-1.10`
* **URL**: https://aclanthology.org/2022.wnut-1.10/
* **Peer-reviewed**: yes (ACL WNUT 2022)
* **Relevance**: NER evaluation on noisy ASR transcripts in a business domain — closely analogous to
  the investor-relations ecommerce domain of gold-92. Validates that pipeline (ASR then NER)
  approaches are practical for domain-specific entity recognition.
