---
spec_version: "1"
task_id: "t0014_granite_short_clip_robustness"
research_stage: "papers"
papers_reviewed: 19
papers_cited: 6
categories_consulted:
  - "stt-evaluation"
  - "latency-profiling"
  - "audio-datasets"
date_completed: "2026-06-29"
status: "complete"
---

## Task Objective

Validate Granite Speech 4.1 2B robustness on short audio clips (under 3 seconds) compared to
Parakeet TDT 0.6b-v3 and Whisper turbo, using production-realistic streaming simulation via
`STTAdapter.transcribe_stream()` with 32kB PCM-16 mono chunks. Whisper turbo — the previous
production STT model in brainpowa-realtime-api — was replaced by Parakeet because it produced
hallucinations or empty output on short clips in the chunked re-transcribe streaming pattern. The
gold-92 benchmark (minimum clip duration 3.07 s) cannot test this failure mode. t0012 established
that Granite Speech 4.1 2B matches Whisper turbo on entity accuracy (41.1% vs 42.0%) and
substantially outperforms Parakeet (23.2% EA). This task answers whether Granite avoids the
short-clip failure mode that disqualified Whisper, and whether Granite is production-ready as a
drop-in STTAdapter replacement in brainpowa-realtime-api.

## Category Selection Rationale

**Included categories:**

* `stt-evaluation` — the core task is a benchmarking run comparing three STT models across
  synthetic short-clip strata and the gold-92 benchmark. Papers in this category define evaluation
  protocols, robustness metrics (WER, entity accuracy, hallucination rate), and statistical testing
  methods that directly inform how to design and analyse the stratified experiment.

* `latency-profiling` — the production decision must weigh Granite's 6× latency overhead (249 ms
  vs Parakeet 40 ms p50) against its accuracy advantage. Papers in this category provide reference
  numbers for what latency is achievable in streaming ASR and what architectures enable bounded
  per-chunk compute.

* `audio-datasets` — the task synthesises a short-clip dataset from gold-92 source audio. Although
  no papers in this category were ultimately cited (papers here describe the Rezolve data collection
  process rather than short-clip robustness methods), the category was reviewed and confirmed
  non-contributory to the literature synthesis.

**Excluded categories:**

* `entity-correction` — 11 papers cover post-ASR correction (LLM pass, contextual biasing,
  retrieval-augmented correction). These are relevant to a future correction stage but not to the
  short-clip robustness or streaming architecture questions that t0014 must answer. Two papers with
  entity correction as secondary contribution (Durmus2026, Tsai2026) were retained for their
  primary STT evaluation and streaming latency content.

* `whisper-finetuning` — three papers cover fine-tuning Whisper-class models. Fine-tuning is out of
  scope for t0014, which evaluates zero-shot streaming inference on existing checkpoints.

* `commercial-apis` — no papers exist in this category; the project tracks Deepgram as a production
  baseline but no literature covers it at the required technical depth.

* `confidence-routing` — one paper (Jiang2026) covers interactive correction with human-in-the-loop
  clarification. Routing policy design is a separate future task; it does not inform the short-clip
  robustness or production fit questions here.

## Key Findings

### Short Utterances and Truncated Audio Are High-Risk Failure Zones for All ASR Models

WildASR [Tay2026] is the most directly relevant study: it systematically tests ASR robustness under
11 conditions including short utterances (under 6 words) and truncated/incomplete audio. Short
utterances under 6 words achieve 38–74% WER in English even for top commercial systems [Tay2026,
Section 4.3], and Qwen2-Audio on Korean short utterances produces **102.6% CER** — an
insertion-dominated hallucination rate exceeding the reference length [Tay2026, Table 2]. The
paper confirms that short terse voice commands (common in ecommerce voice commerce: "add it", "next",
"stop") are a high-risk category that standard benchmarks do not expose. Importantly, synthetic
TTS-based evaluation underestimates real failure rates by **5.9×** compared to authentic human
speech [Tay2026, Section 5.1], validating the need for real production audio rather than
synthesised test clips.

Noise gaps — silence or background noise inserted between speech fragments — cause an additional
**+67.7 WER points** for English conversational speech [Tay2026, Table 1]. For the Rezolve
short-clip experiment, silence-heavy clips (0.5 s silence, 0.5 s background noise) are an
important edge case because they stress-test VAD thresholds: a model that treats silence as
meaningful audio may hallucinate or produce empty output, while a model using an
accumulate-then-transcribe strategy will simply decode silence.

**Hypothesis**: Whisper's VAD-gated chunked re-transcribe path (which re-transcribes the growing
audio buffer every 32kB interval) is the root cause of short-clip failures because the VAD
threshold (`no_speech_threshold=0.6`) fires on very short or silence-heavy buffers before adequate
speech context accumulates. Granite's accumulate-then-transcribe default (no intermediate VAD
passes, single `transcribe()` call on the complete audio) avoids this failure mode entirely — a
testable hypothesis that the Part 2 short-clip inference run will confirm or refute.

### Whisper's VAD and Long-Form Heuristics Create Short-Clip Vulnerability

Radford et al. describe the long-form decoding heuristics central to Whisper's production use:
beam search with temperature fallback, VAD using `no_speech_probability` threshold 0.6 combined
with log-probability threshold, and previous-text conditioning when temperature < 0.5 [Radford2022,
Section 4.5]. These heuristics reduce average long-form WER from **11.0** (greedy) to **10.0**
with full heuristics across seven long-form datasets [Radford2022, Table 7], and are essential for
production deployment with full utterances.

However, the VAD threshold behaviour documented by Radford et al. creates an inherent short-clip
vulnerability: on audio buffers under 1–2 seconds, the no-speech probability can exceed 0.6 even
when speech is present but sparse, triggering an empty or hallucinated output. The hallucination
patterns listed in the task description ("Thanks for watching", "Subscribe", "\[Music\]", repeated
punctuation) are consistent with Whisper's training data artefacts that surface when the model
receives insufficient speech context. Radford2022 does not report performance on clips under 3 s
explicitly, which is a gap — but the heuristic design makes short-clip brittleness predictable.

faster-whisper's `vad_filter=True` at `no_speech_threshold=0.6` (the configuration used in both
t0012 and t0014) directly inherits this design. The Whisper Turbo model (a distilled variant) was
not evaluated on sub-3 s clips in the original paper; its behaviour in the chunked re-transcribe
streaming mode is an open question, not a known quantity.

**Best practice**: For production streaming where clip duration varies unpredictably, prefer models
with accumulate-then-transcribe semantics (single inference pass on the complete audio, no
intermediate VAD) to avoid VAD false-firings on incomplete buffers.

### Streaming ASR Architecture Determines Latency–Robustness Trade-Off

Moonshine v2 [Kudlur2026] introduces an ergodic streaming encoder using sliding-window
self-attention that processes audio in fixed-size chunks with bounded per-chunk computation. On
Apple M3, the Medium model (244.93M parameters) achieves **258 ms** latency at **28.95%** compute
load, running **43.7×** faster than Whisper Large v3 at 1–2 WER points penalty. The Small variant
achieves **148 ms** at **7.84% average WER** on the Open ASR leaderboard [Kudlur2026, Table 1].

The ergodic encoder architecture provides a clean latency guarantee: per-chunk processing time is
constant regardless of utterance position, unlike encoder-decoder models (Whisper, Granite) that
must process the full audio buffer before decoding. This comparison is directly relevant for t0014:
Granite Speech 4.1 2B's accumulate-then-transcribe strategy means latency scales with clip
duration. On the gold-92 benchmark, Granite achieved p50 249 ms, but this is dominated by
longer utterances (3–10 s). On sub-1 s clips, the audio is smaller and latency should drop; the
question is whether Granite's HuggingFace Transformers inference path adds a non-trivial fixed
overhead that dominates over actual audio length.

The latency contrast to Parakeet (40 ms p50, NeMo CTC) reflects a fundamental architecture
difference: Parakeet's CTC decoder produces output in a single forward pass without autoregressive
decoding, giving it a structural latency advantage. Granite's encoder-decoder design with
autoregressive decoding incurs irreducible per-token generation latency regardless of audio length.

**Best practice**: When evaluating streaming production fit, report per-stratum latency (not just
aggregate p50) to reveal whether short clips amplify or reduce the latency gap relative to Parakeet.
A 6× overall latency overhead may be acceptable if the absolute numbers remain under 300 ms even on
short clips.

### Statistical Significance on Small Benchmarks Requires Blockwise Bootstrap

Liu and Peng [Liu2020] demonstrate that the standard utterance-level bootstrap for WER confidence
intervals assumes utterance independence — an assumption that fails when clips come from the same
speaker or session. At realistic within-speaker correlation levels (block size d=30, correlation
ρ=0.4), ordinary bootstrap CI coverage collapses to **41.2%** while blockwise bootstrap maintains
**95.9%** [Liu2020, Table 1]. On two real datasets, blockwise CIs are **1.5–2.3×** wider than
ordinary bootstrap CIs [Liu2020, Section 4]. The gold-92 benchmark (93 clips) likely contains
multiple clips per speaker; blockwise bootstrap with speaker-level blocks is therefore required to
avoid false-positive significance claims when comparing Granite vs Parakeet (or vs Whisper).

The task description specifies BCa bootstrap p < 0.05 as the significance threshold. BCa bootstrap
is an acceleration-corrected variant that also handles non-normal CI shapes — it addresses the same
independence assumption issue as blockwise bootstrap when applied with speaker-level blocks. Both
methods require B = 1,000 replicates (computationally trivial for n = 93 clips).

### Entity Accuracy on Domain Vocabulary Requires Dual Metrics: Keyword F-Score and WER

Durmus et al. [Durmus2026] demonstrate on Contextual Earnings-22 that aggregate WER and keyword
F-score can move in **opposite directions** under context conditioning: OpenAI Whisper-1's WER
worsens under keyword prompting while keyword F-score improves [Durmus2026, Section 4]. All six
evaluated systems (Deepgram Nova-3, OpenAI Whisper-1, AssemblyAI, Whisper OSS Large-v3-turbo,
CTC-WS FastConformer, Argmax Parakeet-TDT-0.6B-v2 + CTC-WS) improve keyword F-score under context
but show inconsistent WER changes [Durmus2026, Table S1].

The benchmark distinguishes two context regimes: local (keywords present in clip only — higher
precision) vs. global (full call inventory with distractors — precision loss from false insertions)
[Durmus2026, Section 3.2]. For the gold-92 benchmark, Granite's keyword prompt (31 domain terms in
a keyword string) operates as a local-context oracle because only the terms relevant to the actual
utterance are active. The Parakeet GPU-PB phrase boosting with 66 casing variants effectively
operates in a denser vocabulary space (more potential distractors), which may explain part of
Parakeet's lower entity accuracy (23.2% vs Granite's 41.1%) — not architecture alone, but
also precision-loss from aggressive boosting.

**Best practice**: Report keyword precision and recall separately alongside WER for the short-clip
strata; precision-first matters more than recall for the wrong-action rate constraint of <2%.

### Hallucination Rate Is a First-Class Metric Distinct from WER

WildASR [Tay2026] introduces Hallucination Error Rate (HER) as a complement to WER, demonstrating
that semantic fabrications can dominate over lexical errors. Deepgram Nova 2 on code-switching
Chinese produces **33.7% MER** lexically but **68.4% HER** semantically [Tay2026, Table 3] —
the model appears to transcribe plausibly but invents content not present in the audio. This gap
matters most for short clips and truncated audio, where an ASR model receives insufficient speech
context to decode reliably.

For the Whisper short-clip experiment in t0014, `is_hallucination=True` is flagged when the
transcript is non-empty but contains none of the reference words AND matches known Whisper
hallucination patterns. This flag is directly analogous to HER and should be tracked per duration
stratum. The task description's hallucination patterns ("Thanks for watching", "Subscribe",
"\[Music\]") are consistent with WildASR's finding that models hallucinate plausible but unspoken
content — specifically, training data artefacts that surface when acoustic context is ambiguous.

**Hypothesis**: Granite's hallucination rate on sub-1 s clips will be lower than Whisper's because
the accumulate-then-transcribe design does not fire intermediate VAD on incomplete buffers, reducing
the probability of hallucinating from partial context. Parakeet's CTC-based architecture lacks
sequential generation, which may further reduce hallucination-type errors compared to Whisper's
autoregressive decoder.

## Methodology Insights

* **Hallucination detection protocol**: Flag `is_hallucination=True` only when the transcript is
  non-empty AND contains none of the reference words AND matches a known hallucination pattern list
  ("Thanks for watching", "Subscribe", "\[Music\]", repeated punctuation, non-English tokens). This
  matches the WER/HER distinction from [Tay2026]: lexical emptiness and semantic fabrication are
  separate failure modes and must be tracked separately (`is_empty` vs `is_hallucination`).

* **Duration-stratified reporting is essential**: [Tay2026] shows robustness does not aggregate
  cleanly — short utterances and noise gaps produce failure rates 10–20× higher than aggregate
  WER. Report `empty_rate` and `hallucination_rate` per duration bin (< 1 s, 1–2 s, 2–3 s, 3–5 s,
  5–10 s, > 10 s), not as a single number. This enables pinpointing the duration threshold where
  each model starts failing.

* **VAD threshold behaviour is the mechanism to test**: Whisper turbo with `vad_filter=True` and
  `no_speech_threshold=0.6` [Radford2022] is expected to fail on sub-2 s clips. To confirm the
  mechanism, track whether empty outputs correlate with higher `no_speech_probability` values in
  the faster-whisper result metadata. If `no_speech_probability` > 0.6 for clips where reference
  text is non-empty, this confirms VAD misfiring as the direct cause.

* **Accumulate-then-transcribe vs. chunked re-transcribe**: Granite's `STTAdapter` base class uses
  accumulate-then-transcribe (single `transcribe()` call on complete audio, no intermediate VAD).
  Whisper and Parakeet use chunked re-transcribe (buffer grows with each 32kB chunk, transcribed
  every interval). The production test must use `transcribe_stream()` for all three models — NOT
  direct `model.transcribe()` calls — to reproduce the actual failure modes [from task description].

* **Statistical significance with small n**: With 40–60 synthetic clips and 93 gold-92 clips, use
  BCa bootstrap with B = 1,000 replicates and speaker-level blocks [Liu2020]. At n ≈ 50 per
  stratum, the minimum detectable absolute WER difference at 95% CI is approximately ±5–8 WER
  points depending on within-stratum variance. Differences smaller than this may not be
  statistically distinguishable.

* **Latency definition for short clips**: Report TTFD (time to first delta from `transcribe_stream()`)
  separately from end-to-end latency. For an accumulate-then-transcribe model, TTFD equals
  end-to-end latency (no partial output). For chunked re-transcribe, TTFD can be lower (first
  partial output from the growing buffer). This distinction matters for the brainpowa user
  experience even if it does not change entity accuracy.

* **Context injection protocol**: Whisper turbo uses `initial_prompt` (comma-separated 31 domain
  terms). Granite uses keyword prompt injection ("transcribe the speech to text. Keywords: ...").
  Durmus2026 validates that prompt-based context conditioning consistently improves keyword F-score
  [Durmus2026]. For short clips, context injection may backfire if the prompt accounts for a large
  fraction of the effective context window — this risk is worth monitoring but is not a blocking
  issue at 31 domain terms.

* **Hallucination vs. empty output distinction**: For the production fit assessment, empty output
  (silent failure) is preferable to hallucination (dangerous failure). A model that returns an
  empty string on a 0.5 s clip can trigger a clarification; a model that returns "Thanks for
  watching" on a 0.5 s command will cause a silent wrong action. This asymmetry must be explicit
  in the recommendation: if Granite returns empty on short clips, that is tolerable; if Whisper
  hallucinated, that is why it was removed from production.

## Gaps and Limitations

* **No paper directly evaluates Granite Speech 4.1 2B or Parakeet TDT 0.6b-v3**: All reviewed
  papers use different models (Whisper, Moonshine, generic Conformer CTC, commercial APIs). The
  Granite and Parakeet model families are too recent and specialised to appear in the reviewed
  literature. This means architectural hypotheses about their short-clip robustness (accumulate-then-
  transcribe vs. chunked re-transcribe) must be empirically validated rather than drawn from the
  literature.

* **Short-clip ASR robustness as a first-class topic is understudied**: WildASR [Tay2026] tests
  clips under 6 words as one of 11 conditions but does not isolate duration in seconds as the
  independent variable. No paper systematically sweeps clip duration from 0.5 s to 3 s and
  measures empty rate and hallucination rate as continuous functions of duration. The 0.5 s–3 s
  range examined in t0014 is not covered by any reviewed paper.

* **Streaming chunk size effects on short clips are unquantified**: Tsai2026 uses 160 ms chunks;
  the brainpowa production pattern uses 32kB PCM-16 chunks (~1 s at 16kHz). The interaction
  between short clip duration (< 3 s) and chunk size (1 s) means that sub-1 s clips may deliver
  only a single chunk before the `None` sentinel — a degenerate streaming case not studied in any
  reviewed paper. Behaviour in this regime is task-specific and empirically unknown.

* **Latency of Granite Speech 4.1 2B on the Azure H100 NVL is not in the literature**: Moonshine
  v2 reports latency on Apple M3 [Kudlur2026]; Tay2026 does not report inference latency. The
  249 ms Granite p50 from t0012 is the best available reference. Whether this degrades, improves,
  or stays constant on sub-3 s clips is unknown prior to Part 2 inference runs.

* **HuggingFace Transformers inference overhead for short audio**: Granite is loaded via HuggingFace
  Transformers, which adds model loading and tokenisation overhead. For very short clips (< 1 s),
  this fixed overhead may dominate total latency. No reviewed paper benchmarks HuggingFace
  Transformers speech model inference on sub-1 s audio.

## Recommendations for This Task

1. **Track `is_empty` and `is_hallucination` as separate failure modes, per duration bin** — do not
   aggregate into a single failure rate. Empty output is a tolerable graceful degradation; hallucination
   is a dangerous failure. [Tay2026] shows these behave differently across architectures.

2. **Test the VAD-misfiring hypothesis explicitly**: Log `no_speech_probability` from faster-whisper
   for each clip. If empty outputs on Whisper turbo correlate with `no_speech_probability > 0.6`
   [Radford2022], the mechanism is confirmed. This strengthens the argument for Granite's
   accumulate-then-transcribe design.

3. **Use BCa bootstrap with speaker-level blocks for significance testing** — ordinary utterance-level
   bootstrap will produce CIs that are 1.5–2.3× too narrow on correlated evaluation sets [Liu2020].
   With n ≈ 50 synthetic clips per experiment, a ±5–8 WER point detectable difference is the
   practical significance floor.

4. **Report keyword precision and recall separately from WER for the gold-92 strata** — [Durmus2026]
   demonstrates these can diverge under context conditioning. The wrong-action rate target (< 2%)
   is driven by precision, not recall; a model with high recall but low precision may look good on
   entity accuracy but exceed the wrong-action rate threshold.

5. **Measure TTFD (time to first delta) separately from end-to-end latency for the streaming
   strata** — for production UX assessment, TTFD matters more than total latency for short terse
   commands. Moonshine v2 [Kudlur2026] reports 50–258 ms TTFD as a primary latency metric; the
   same convention should be used for the t0014 latency strata.

6. **For the production recommendation, frame latency as absolute milliseconds, not relative ratio**
   — Granite 249 ms vs Parakeet 40 ms is a 6× ratio but both are comfortably under the 800 ms p50
   constraint. The decision driver is whether the 200+ ms overhead affects downstream tool-call
   dispatch in brainpowa, not whether the ratio looks large.

## Paper Index

### [Radford2022]

* **Title**: Robust Speech Recognition via Large-Scale Weak Supervision
* **Authors**: Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., Sutskever, I.
* **Year**: 2022
* **DOI**: `10.48550/arXiv.2212.04356`
* **Asset**: `tasks/t0002_baseline_evaluation/assets/paper/10.48550_arXiv.2212.04356/`
* **Categories**: `stt-evaluation`, `whisper-finetuning`
* **Relevance**: Defines Whisper's VAD heuristics (`no_speech_threshold=0.6`, temperature
  fallback) that create the short-clip failure mode being investigated. Documents the long-form
  decoding pipeline used by faster-whisper in both t0012 and t0014.

### [Tay2026]

* **Title**: Back to Basics: Revisiting ASR in the Age of Voice Agents
* **Authors**: Tay, G. et al.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2603.25727`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2603.25727/`
* **Categories**: `stt-evaluation`, `latency-profiling`
* **Relevance**: WildASR benchmark quantifies short utterance and truncated audio failure modes
  across 7 systems. Documents 38–74% WER on short commands and 68.4% semantic hallucination rate,
  directly motivating t0014's `is_hallucination` flag and duration-stratified evaluation design.

### [Kudlur2026]

* **Title**: Moonshine v2: Ergodic Streaming Encoder ASR for Latency-Critical Speech Applications
* **Authors**: Kudlur, M., King, E., Wang, J., Warden, P.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2602.12241`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2602.12241/`
* **Categories**: `latency-profiling`, `stt-evaluation`
* **Relevance**: Provides reference latency numbers (50–258 ms on Apple M3) for streaming ASR
  models and explains the architectural tradeoff between encoder-decoder autoregressive models
  (Granite) and CTC/streaming models (Parakeet, Moonshine) for latency-critical deployment.

### [Liu2020]

* **Title**: Statistical Testing on ASR Performance via Blockwise Bootstrap
* **Authors**: Liu, Z., Peng, F.
* **Year**: 2020
* **DOI**: `10.21437/Interspeech.2020-1338`
* **Asset**: `tasks/t0002_baseline_evaluation/assets/paper/10.21437_Interspeech.2020-1338/`
* **Categories**: `stt-evaluation`
* **Relevance**: Proves that ordinary bootstrap for WER significance testing collapses to 41.2%
  coverage (vs. 95% nominal) on correlated evaluation sets. Required for gold-92 stratified
  significance testing where multiple clips per speaker are likely correlated.

### [Durmus2026]

* **Title**: Contextual Earnings-22: A Speech Recognition Benchmark with Custom Vocabulary in
  the Wild
* **Authors**: Durmus, B., Cen, C., Pacheco, E., Okan, A., Orhon, A.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2604.07354`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2604.07354/`
* **Categories**: `stt-evaluation`, `entity-correction`
* **Relevance**: Demonstrates that keyword F-score and WER can move in opposite directions under
  context conditioning, and that global context (with distractors) causes precision loss. Relevant
  to evaluating Granite's keyword prompt and Parakeet's GPU-PB boosting on short clips.

### [Tsai2026]

* **Title**: Contextual Biasing for Streaming ASR via CTC-based Word Spotting
* **Authors**: Tsai, K.-C., Lo, T.-H., Sun, Y.-T., Chen, B.
* **Year**: 2026
* **DOI**: `10.48550/arXiv.2605.18222`
* **Asset**: `tasks/t0003_literature_review_entity_stt/assets/paper/10.48550_arXiv.2605.18222/`
* **Categories**: `entity-correction`, `latency-profiling`, `stt-evaluation`
* **Relevance**: Stateful CTC-based word spotting for streaming ASR uses 160 ms chunks and bounded
  incremental latency. Relevant as a comparison point for the 32kB chunk streaming simulation
  and the latency implications of chunk size in production.
