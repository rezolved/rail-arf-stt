---
spec_version: "3"
paper_id: "10.48550_arXiv.2603.25727"
citation_key: "Tay2026"
summarized_by_task: "t0003_literature_review_entity_stt"
date_summarized: "2026-06-23"
---

# Back to Basics: Revisiting ASR in the Age of Voice Agents

## Metadata

* **File**: `files/tay_2026_back-to-basics-asr.pdf`
* **Published**: 2026
* **Authors**: Geeyang Tay, Wentao Ma, Jaewon Lee, Yuzhi Tang, Daniel Lee, Weisu Yin,
  Dongming Shen, Silin Meng, Yi Zhu, Mu Li, Alex Smola (all at Boson AI)
* **Venue**: arXiv preprint (arXiv:2603.25727v1 [cs.AI])
* **DOI**: `10.48550/arXiv.2603.25727`

## Abstract

Automatic speech recognition (ASR) systems have achieved near-human accuracy on curated
benchmarks, yet still fail in real-world voice agents under conditions that current evaluations do
not systematically cover. Without diagnostic tools that isolate specific failure factors, practitioners
cannot anticipate which conditions, in which languages, will cause what degree of degradation. We
introduce WildASR, a multilingual (four-language) diagnostic benchmark sourced entirely from real
human speech that factorizes ASR robustness along three axes: environmental degradation,
demographic shift, and linguistic diversity. Evaluating seven widely used ASR systems, we find
severe and uneven performance degradation, and model robustness does not transfer across languages
or conditions. Critically, models often hallucinate plausible but unspoken content under partial or
degraded inputs, creating concrete safety risks for downstream agent behavior. Our results
demonstrate that targeted, factor-isolated evaluation is essential for understanding and improving
ASR reliability in production systems. Besides the benchmark itself, we also present three
analytical tools that practitioners can use to guide deployment decisions.

## Overview

This paper directly addresses the gap between benchmark-level ASR performance and real-world
voice agent deployments. The central observation is that modern ASR systems routinely achieve
below-5% WER on curated benchmarks like LibriSpeech and FLEURS, yet fail dramatically and
unevenly when deployed in production voice agents. The authors argue that aggregate WER on
in-distribution data provides no predictive power for real-world reliability.

The paper introduces WildASR, a multilingual diagnostic benchmark covering English (EN),
Chinese (ZH), Japanese (JA), and Korean (KO). Unlike previous robustness benchmarks that often
use TTS-generated audio, WildASR sources all audio from real human speech. This design choice
is validated empirically: Whisper Large V3 achieved near-ceiling **3.7% WER** on synthetic child
speech but **21.7% WER** on real child speech, confirming that synthetic audio substantially
underestimates failure rates by roughly 5.9×.

WildASR decomposes robustness failures into three axes: (1) environmental degradation (five
controlled perturbation types: reverberation, far-field, phone codec, noise gap, clipping),
(2) demographic shift (children, older adults, accented speakers), and (3) linguistic diversity
(short utterances, incomplete/truncated audio, code-switching). This factor-isolated structure
enables practitioners to diagnose where, for whom, and under what linguistic conditions a given
model degrades.

Beyond the benchmark data, the paper introduces three deployment-oriented analytical tools: a P90
Elbow analysis that identifies distortion instability thresholds, a prompt sensitivity profiling
methodology that quantifies variance from instruction phrasing, and a Hallucination Error Rate
(HER) metric that detects semantic fabrications orthogonal to lexical WER. The paper also argues
against replacing ASR with end-to-end speech-to-speech systems, positioning robust explicit
transcription as an auditable safety guardrail for voice agents.

## Architecture, Models and Methods

**Benchmark construction**: WildASR follows a "real source, controlled perturbation" principle.
Source audio is drawn from FLEURS test split (read speech) and MagicData conversational
datasets. A 7-stage curation pipeline is applied: Data Collection (DC), Speaker Filtering (SF),
Quality Filtering (QF), Audio Normalization (NR), Acoustic Augmentation (AA), Manual
Truncation & Transcript Alignment (MT), and Manual Verification (MV).

**Environmental degradation subset**: Five perturbation types applied to all four languages.
Reverberation varies RT60 at three levels (0.4 / 0.8 / 1.6 s) using the image-source method.
Far-field varies source-microphone distance (4 / 8 / 16 m) with fixed room acoustics. Phone
codec applies GSM and G.711 µ-law codecs (8 kHz downsampling and resampling). Noise gap
injects stationary noise between speech fragments in 4 configurations: (Ngap, Δt) ∈ {(3, 0.2),
(5, 0.2), (3, 0.4), (5, 0.4)} seconds. Clipping saturates the top 40% of signal amplitude values
followed by RMS rescaling. Sample sizes range from ~682 (KO clipping) to ~4,980 (ZH noise
gap) per language-condition pair.

**Demographic shift subset**: English and Chinese only. Children's speech sourced from Zenodo
children speech recordings and BAAI/ChildMandarin (ages 3–5); older adults (age 50+) from
GLOBE V3 and SeniorTalk; accented speech from GLOBE V2 (non-native English) and KeSpeech
(regional Mandarin). Manual filtering ensures age-related or accent-related degradation is the
dominant factor. Sample sizes: 300 (EN) or 1,000 (ZH) per demographic condition.

**Linguistic diversity subset**: Short utterances select items under 6 words/characters from YODAS
(~255–467 samples per language). Incomplete audio truncates utterances mid-sentence or mid-word
(EN: 2,345 samples). Code-switching sourced from SwitchLingua (700 samples per target language:
ZH, JA, KO mixed with EN).

**Models evaluated**: Whisper Large V3 (open-source), GPT-4o Transcribe (proprietary), Gemini
2.5 Pro (proprietary), Gemini 3 Pro (proprietary), Qwen2-Audio (open-source), Deepgram Nova 2
(commercial API), ElevenLabs Scribe V1 (commercial API). Inference protocols standardized per
model; full per-model breakdowns provided in appendix.

**Metrics**: WER for English; CER (character error rate) for CJK languages; MER (mixed error
rate) for code-switching. Hallucination Error Rate (HER) from Atwany et al. (2025) measures
semantic-level errors beyond lexical metrics. P90 Elbow computed via knee-detection on the 90th-
percentile WER curve as a function of distortion severity. **Human baseline**: independent
annotators achieved **4.7% average error** on WildASR samples, confirming the benchmark
tests model limitations rather than signal ambiguity.

## Results

* Model-average clean baseline across 7 systems on FLEURS: **5.7% error rate** across all
  languages — establishes the in-distribution reference
* Noise gap (conversational speech, MagicData) increases EN WER by **+67.7 pp** (to 87.6%),
  JA CER by **+118.9 pp** (to 138.7%), KO CER by **+121.0 pp** (to 140.5%)
* Reverberation (MagicData) increases EN WER by **+12.0 pp**; KO CER by **+27.0 pp**
* Clipping increases EN WER by **+10.7 pp** (conversational); ZH CER by **+22.7 pp**
* Child speech: best model (Gemini 3 Pro) achieves **18.2% EN WER** — no model drops below
  this threshold on English child speech
* Qwen2-Audio on KO short utterances: **102.6% CER** (insertion-dominated hallucinations);
  on KO code-switching: **211.7% MER**; on JA incomplete audio: **224.4% CER**
* Deepgram Nova 2 on ZH code-switching: **33.7% MER** but **68.4% HER**, revealing semantic
  fabrication far exceeding lexical error
* Gemini 3 Pro on FLEURS/Clean: **3.8% WER**; degrades to **61.2%** on MagicData/Noise gap
  and **52.7%** on short utterances — clean-benchmark rank does not predict OOD rank
* Prompt sensitivity (Gemini 2.5 Pro, 10 paraphrased prompts): Chinese Children subset shows
  **σ = 46.1%** performance standard deviation; EN shows σ ≤ **0.6%** across all conditions
* Whisper Large V3 on synthetic child speech: **3.7% WER**; on real child speech: **21.7% WER**
* Human error rate on WildASR: **4.7%**, confirming models have substantial headroom to improve

## Innovations

### WildASR Benchmark

A multilingual (EN/ZH/JA/KO) ASR robustness benchmark built entirely from real human speech,
covering 11 distinct OOD conditions across three axes simultaneously. This is the first benchmark
to factorize ASR robustness across environmental, demographic, and linguistic dimensions in a
multilingual setting at this scale. Released publicly at HuggingFace (`bosonai/WildASR`) and
GitHub (`boson-ai/WildASR-public`).

### P90 Elbow Analysis

A deployment-oriented instability threshold detector that plots the 90th-percentile WER as a
function of distortion severity and identifies the elbow point at which tail failures accelerate. This
provides a principled bound on allowable acoustic degradation before a system becomes unreliable
for production — more actionable than mean WER curves alone.

### Prompt Sensitivity Profiling

A controlled methodology using 10 semantically equivalent paraphrased instructions to quantify
how much prompt phrasing affects ASR output. Reveals that Chinese ASR with prompt-conditioned
models can shift by tens of percentage points purely from instruction wording, making prompt
stability a first-class deployment metric.

### Hallucination Error Rate (HER) as a First-Class Metric

Demonstrates that WER/CER systematically underreports risk for voice agents by missing semantic
fabrications. HER from Atwany et al. (2025) is integrated as a complement metric. The gap
between WER and HER (e.g., Nova 2: 33.7% MER vs. 68.4% HER on ZH code-switching)
reveals cases where surface transcription appears acceptable while meaning is severely distorted.

### Real-Speech vs. Synthetic Evaluation Validation

The first direct head-to-head comparison of TTS-generated vs. real child speech evaluation,
showing a 5.9× underestimation of failure rates when using synthetic data, providing rigorous
empirical justification for real-speech-only benchmark design.

## Datasets

* **FLEURS** (Conneau et al., 2022): multilingual read-speech corpus used as environmental
  degradation source; public, CC-BY 4.0; covers EN/ZH/JA/KO
* **MagicData** conversational datasets (Zhou et al., 2025): spontaneous speech; public
* **YODAS** (Li et al., 2023): YouTube audio dataset for short utterances; EN/ZH/JA/KO; public
* **SwitchLingua** (Xie et al., 2025): code-switching benchmark; ZH/JA/KO mixed with EN;
  700 samples per language pair; public
* **Zenodo Children Speech Recording** (Kennedy et al., 2016) and **TomRoma/Child Speech**:
  English child speech; public
* **BAAI/ChildMandarin** (Zhou et al., 2024): Chinese child speech ages 3–5; public
* **MushanW/GLOBE V3** (Wang et al., 2024): English older adults (age 50+); public
* **evan0617/SeniorTalk** (Chen et al., 2025): Chinese elderly speech; public
* **MushanW/GLOBE V2** (Wang et al., 2024): non-native English accented speech; public
* **TwinkStart/KeSpeech** (Shi et al., 2026): regional Mandarin varieties; public
* **WildASR** (this paper): public release at
  `https://huggingface.co/datasets/bosonai/WildASR`

## Main Ideas

* **Aggregate WER on curated benchmarks does not predict production reliability**: the 5.7%
  model-average clean score on FLEURS conceals noise-gap failures exceeding 120% CER in
  JA/KO — the gold-92 evaluation harness must stratify results by utterance condition type, not
  just report a single WER number.
* **Noise gaps and short utterances are the highest-risk conditions for voice commerce**: noise
  gaps cause +67.7 pp WER for English and +121 pp CER for Korean; short commands under 6
  words hit 38–74% WER even in English — voice commerce utterances like "stop", "add it", and
  "next" fall directly in this failure zone and should be a dedicated test category on gold-92.
* **Deepgram Nova 2's semantic hallucination rate (68.4% HER on ZH code-switching) is far
  higher than its lexical error rate (33.7% MER)**: for Rezolve's production baseline, HER should
  be added to the gold-92 evaluation alongside WER and entity accuracy to surface action-critical
  semantic fabrications.
* **Prompt phrasing for GPT-4o Transcribe and Gemini-based ASR can shift performance by
  tens of percentage points**: if any prompt-conditioned model is considered for Rezolve's
  pipeline, the instruction prompt must be treated as a hyperparameter and locked before
  benchmarking.
* **Real production audio (gold-92) is methodologically essential**: the 5.9× underestimation
  of failure rates with synthetic speech confirms that Rezolve's use of real production audio for
  benchmarking is the only valid approach — TTS-generated test data would hide the actual
  entity-accuracy gap.
* **Explicit ASR should be retained as an auditable layer**: for Rezolve's tool-call use case,
  a transparent transcript is necessary for action debugging, confidence routing, and compliance —
  end-to-end S2S would obscure hallucinations that currently manifest as detectable WER spikes.

## Summary

Tay et al. (2026) challenge the assumption that ASR is a solved problem by demonstrating that
modern systems achieving sub-5% WER on standard benchmarks fail severely and unpredictably
under real-world voice agent conditions. The paper's motivation is direct: voice agents do not
passively transcribe speech but use transcripts to trigger downstream tool calls and execute actions.
Under out-of-distribution conditions, hallucinated or garbled transcripts cause silent action
failures — exactly the problem Rezolve faces with its production Deepgram deployment on accented
investor-relations audio. The paper introduces WildASR, a multilingual diagnostic benchmark
(EN/ZH/JA/KO) constructed entirely from real human speech.

The benchmark decomposes OOD robustness into 11 conditions across three axes: environmental
degradation (reverberation, far-field, phone codec, noise gap, clipping), demographic shift
(children, older adults, accented speakers), and linguistic diversity (short utterances, truncated
audio, code-switching). Seven systems — Whisper Large V3, GPT-4o Transcribe, Gemini 2.5/3 Pro,
Qwen2-Audio, Deepgram Nova 2, ElevenLabs Scribe V1 — are evaluated under a unified protocol.
Three diagnostic tools supplement raw metrics: a P90 Elbow detector, a prompt sensitivity profiler
(10 paraphrased instructions), and integration of Hallucination Error Rate to catch semantic
fabrications that WER misses.

The headline results are stark. Noise gaps cause **+67.7% WER** for English conversational speech
and **+121% CER** for Korean. No model achieves below **18.2% WER** on English child speech.
Deepgram Nova 2 on Chinese code-switching produces 33.7% lexical error but **68.4% semantic
hallucination rate**. Prompt phrasing alone induces up to **σ = 46.1%** performance swing for
Chinese. Robustness does not transfer across languages: a model robust to reverberation in English
may catastrophically fail in Japanese under the same perturbation. Synthetic TTS-based evaluation
underestimates real failure rates by 5.9× compared to authentic child speech.

For this project, the paper delivers three concrete takeaways. First, the gold-92 evaluation harness
must stratify by utterance condition type and adopt HER alongside WER and entity accuracy —
aggregate WER alone will miss the hallucination risk that production Deepgram carries. Second,
Deepgram Nova 2 and Whisper Large V3 both show condition-specific failure modes that mean
their gold-92 rankings may not reflect their behavior on domain-specific OOD inputs like accented
investor-relations vocabulary. Third, the paper validates Rezolve's methodological choice to use
real production audio for gold-92 rather than TTS-synthesized data, and confirms that short terse
commands — a common voice commerce pattern — are a high-risk category that merits dedicated
coverage in the benchmark design.
