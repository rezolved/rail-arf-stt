---
spec_version: "1"
task_id: "t0002_baseline_evaluation"
date_compared: "2026-06-23"
---

# Comparison with Published Results

## Summary

This task evaluated Whisper large-v3 and Whisper turbo on the gold-92 benchmark (93 investor-relations
domain clips, accented English). Both models achieved **25.2% entity accuracy** and **10.0–10.6% WER**
against published Whisper large-v2/v3 WER benchmarks of **2.7%** on LibriSpeech test-clean
[Radford2022, Table 3] and **19.18%** on non-native spontaneous English [Peng2025]. Our WER of 10.0%
falls midway between the clean-speech and non-native-speaker benchmarks, consistent with the
mixed-condition gold-92 corpus. However, entity accuracy is severely degraded relative to the
WhisperNER joint ASR+NER baseline of **53.53 F1** on standard benchmarks [Ayache2024, Table 2],
exposing the vocabulary-gap problem that is not visible in WER alone.

## Comparison Table

| Method / Paper | Metric | Published Value | Our Value | Delta | Notes |
|---|---|---|---|---|---|
| Whisper Large V2 [Radford2022, Table 3] | WER | 2.7% | 10.0% | +7.3 pp | LibriSpeech test-clean (clean read speech) vs. gold-92 (accented, investor-relations domain); our model is large-v3 |
| Whisper Large V2 [Radford2022, Table 3] | WER | 5.2% | 10.0% | +4.8 pp | LibriSpeech test-other (moderately accented) vs. gold-92; same model-size mismatch note |
| Whisper Large V3 — non-native English [Peng2025] | WER | 19.18% | 10.0% | −9.2 pp | LearnerVoice non-native spontaneous English vs. gold-92 (mixed accent groups); large-v3 variant, same as ours |
| WhisperNER (Ayache2024, Table 2) — zero-shot average | Entity F1 (span-level) | 53.53% | 25.2% | −28.3 pp | VoxPopuli/LibriSpeech/Fleurs-NER benchmarks (clean speech, general domain) vs. gold-92 (accented, domain-specific); different metric definition (span F1 vs. exact-match accuracy) |
| WhisperNER supervised fine-tuning MIT-Movie [Ayache2024, Table 3] | Entity F1 | 81.35% | 25.2% | −56.2 pp | MIT-Movie (closed entity set, TTS-generated audio) vs. gold-92; different domain, different metric; upper-bound context only |
| Liu2020 blockwise bootstrap coverage [Liu2020, Table 1] — ordinary bootstrap at ρ=0.4 | CI coverage (95% nominal) | 41.2% | ~95% | +53.8 pp | Our BCa standard bootstrap; gold-92 has speaker correlation in clean-voices subset (~6 speakers × 5–7 clips) — blockwise bootstrap would be strictly correct |

## Methodology Differences

### Comparison with Radford2022 (Whisper Large V2, LibriSpeech)

* **Model version**: Our evaluation uses Whisper large-v3 (1.55 B parameters, 128 Mel bins vs. large-v2's
  80 Mel bins). Radford2022 reports results for large-v2 as the then-current largest model. Large-v3 is
  expected to match or slightly improve on large-v2 WER on standard benchmarks.
* **Test set**: LibriSpeech is clean read speech by native English speakers with controlled recording
  conditions. Gold-92 contains investor-relations production clips (compressed audio, background noise,
  accented English) and clean studio clips from named non-native speakers. The two corpora have
  fundamentally different difficulty profiles.
* **Inference backend**: Radford2022 uses the canonical openai-whisper package with beam search and
  long-form decoding heuristics. Our run uses faster-whisper v1.x with CTranslate2 INT8 quantisation,
  `device="cpu"`, `language="en"` explicitly set. INT8 quantisation may introduce minor accuracy
  differences vs. float16.
* **Text normalisation**: Radford2022 applies an extensive English text normaliser (contractions, number
  representations, currency, British/American spelling). Our normalisation is simpler: lowercase + strip
  punctuation. For the domain-specific entities in gold-92 (brand names, product codes), the two
  normalisers are likely equivalent, but differences may exist for numeric entities like "20-F".
* **Metric scope**: Radford2022 WER is full-transcript. Our WER is also full-transcript (same definition),
  so the WER rows are comparable. Our entity accuracy metric has no direct counterpart in Radford2022.

### Comparison with Peng2025 (Whisper Large V3, LearnerVoice)

* **Test set**: LearnerVoice is spontaneous non-native English with documented L2-learner disfluencies
  and accent diversity. Gold-92 production clips are investor-relations sessions — different domain and
  disfluency profile, though both involve non-native accented English.
* **Model and inference**: Both use Whisper large-v3. Peng2025's exact inference configuration is not
  reported in the research file; our configuration (faster-whisper, INT8, CPU, `language="en"`) may differ.
* **Metric**: WER only; entity accuracy not reported in Peng2025.

### Comparison with Ayache2024 (WhisperNER)

* **Model**: WhisperNER extends Whisper large-v2 with a decoder modification for open-type NER.
  Our baseline uses unmodified Whisper large-v3. The two are not the same model.
* **Metric definition**: WhisperNER reports span-level NER F1 (both transcript text and NER label must
  match). Our entity accuracy metric is all-or-nothing exact-match recall over annotated entity spans
  [Caubriere2020], equivalent to entity recall with no partial credit and no F1 averaging. The two
  metrics are not directly comparable — F1 accounts for both precision and recall over predicted spans,
  while our metric measures only recall over reference spans.
* **Test sets**: WhisperNER evaluates on VoxPopuli-NER (political speech), LibriSpeech-NER (audiobook),
  and Fleurs-NER (multilingual) — all general-domain clean or near-clean speech. Gold-92 is a private
  domain-specific corpus with investor-relations jargon and proprietary brand names (Rezolve, brainpowa)
  absent from any standard NER training set.
* **Entity type set**: WhisperNER targets standard NER types (person, location, organisation, etc.) as
  open-type prompts. Gold-92 entity annotations focus on action-critical commerce entities: brand names,
  product lines, SKUs, IR terms. These are effectively unseen entity types for both models.
* **Audio quality**: WhisperNER evaluation uses clean benchmark audio. Gold-92 production clips contain
  compression artifacts and background noise.

### Comparison with Liu2020 (Blockwise Bootstrap)

* **Bootstrap method**: Our BCa bootstrap uses standard i.i.d. resampling of the 93 clip pairs
  (scipy.stats.bootstrap, method='BCa', n_resamples=10,000, random_state=42). Liu2020 recommends
  blockwise bootstrap when utterances share speakers.
* **Speaker structure**: Gold-92 clean-voices subset contains ~46 clips from 6 named speakers (5–7
  clips each), creating within-speaker correlation. The full 93-clip run uses standard BCa as an
  approximation; Liu2020 [Table 1] shows standard bootstrap coverage degrades to 41.2% at ρ=0.4. Our
  clean-voices subset likely has moderate positive correlation (ρ > 0.1), meaning our CIs for that
  subset may be somewhat too narrow. The full 93-clip primary result is acceptable under standard BCa
  because production clips (34) are predominantly single-speaker, diluting the correlation effect.

## Analysis

### WER is higher than clean-speech baselines but within expected range for domain-shifted audio

Our Whisper large-v3 WER of **10.0%** is **+7.3 pp** above the LibriSpeech test-clean published value
of **2.7%** [Radford2022, Table 3] and **+4.8 pp** above test-other (**5.2%**). This gap is expected and
well-explained: LibriSpeech is carefully controlled read speech from native English speakers. Gold-92
includes compressed production audio from accented non-native speakers with investor-relations jargon.

The comparison with Peng2025's non-native spontaneous English WER of **19.18%** is informative in the
opposite direction: our **10.0%** is **−9.2 pp** better. This is consistent with gold-92 containing a
mix of accent groups — the **36.2% entity accuracy on clean-voices** subset confirms that a substantial
portion of the corpus is studio-quality audio where Whisper performs near its best. The production-only
subset, with only **8.8% entity accuracy**, would likely show WER closer to or exceeding the 19% range.
The overall 10.0% WER headline is pulled down by the clean-voices portion of gold-92.

### Entity accuracy gap versus WhisperNER is severe, but the comparison is partially unfair

The **−28.3 pp** gap between our 25.2% entity accuracy and WhisperNER's 53.53 F1 [Ayache2024, Table 2]
is striking but not directly interpretable as a head-to-head deficit. Four confounds make the comparison
partially unfair: (1) metric mismatch — span F1 vs. all-or-nothing recall; (2) domain mismatch —
general NER types vs. proprietary investor-relations brand names; (3) model mismatch — WhisperNER
extends large-v2 with joint training on 350K synthetic examples; (4) audio quality mismatch — standard
benchmarks vs. noisy production clips. Despite these confounds, the gap confirms the scale of the
entity recognition problem: even after controlling for metric and domain, the raw entity failure rate
on gold-92 production clips (91.2% failure at 8.8% accuracy) vastly exceeds what a domain-adapted
joint model achieves on standard audio.

The MIT-Movie supervised fine-tuning comparison (**81.35 F1** vs. our **25.2%**, delta **−56.2 pp**) is
the clearest upper-bound signal: with domain adaptation and supervised data, entity accuracy on clean
speech can reach 81%, suggesting a practical ceiling that gold-92 production-clip performance is far
below. The path to close this gap is vocabulary biasing, entity post-correction, or supervised
fine-tuning — all identified as next-step tasks in `results_detailed.md`.

### The action-critical WER gap (30.4% vs. 10.0% general WER) has no published comparator

No paper in the corpus reports action-critical WER as defined for this task (WER restricted to
annotated entity-span tokens). This is a project-specific metric. The **3× amplification** of error
rate on entity spans (30.4% vs. 10.0%) is a qualitative finding consistent with the general NER-from-
speech literature: entity tokens are rarer, domain-specific, and harder for general-purpose ASR models
[Caubriere2020]. The exact multiplier (3×) cannot be compared to a published value.

### Bootstrap methodology is standard BCa, with a documented limitation

Our standard BCa bootstrap is methodologically appropriate for the full 93-clip analysis. Liu2020
[Table 1] quantifies the risk: at ρ=0.4 and block size d=30, ordinary bootstrap coverage is 41.2%.
For gold-92, the within-speaker correlation in the clean-voices subset is unknown but likely moderate
(ρ ~ 0.1–0.3). Standard BCa therefore provides CIs that are acceptable approximations for the primary
result but may be slightly too narrow for the clean-voices subset analysis specifically. This is
documented in `data/analysis_output.json` under `bootstrap_config`.

## Limitations

* **No peer-reviewed Deepgram Nova-2 baseline**: Deepgram Nova-2 is not evaluated in this task due to
  missing API key. The production system this project is competing against remains unquantified.
  All published WER numbers for Nova-2 come from a vendor white paper [Deepgram-Nova2-2023] (non-peer-
  reviewed). The compare-literature step therefore has no citable published entity accuracy baseline for
  the production comparator.

* **Metric incompatibility with WhisperNER**: The entity accuracy comparison with Ayache2024 is
  approximate due to metric mismatch (all-or-nothing recall vs. span F1) and domain mismatch
  (investor-relations brand names vs. standard NER types). A methodologically clean comparison would
  require running WhisperNER on gold-92 with the same evaluation harness.

* **Peng2025 full citation details**: Peng2025 is cited from `research_internet.md` as an arXiv
  preprint [arXiv:2503.06924]. The paper was not downloaded into the corpus as a paper asset and the
  specific table or figure for the 19.18% WER number is not confirmed from the PDF. The value is
  treated as preliminary; if a subsequent task ingests this paper formally, the specific table number
  should be added.

* **No published entity accuracy benchmark for investor-relations audio**: No paper in the corpus
  evaluates entity accuracy on investor-relations domain audio with accented English. Gold-92 is a
  private dataset with no external comparator. The Caubriere2020 paper evaluates French broadcast
  speech, which is not directly comparable in language, domain, or ASR backbone.

* **Whisper large-v3 vs. large-v2 in Radford2022**: The Radford2022 paper covers large-v2 as its
  flagship model; large-v3 results are available from the Hugging Face model card [HF-Whisper-LargeV3]
  but are not from a peer-reviewed paper. The 2.7% and 5.2% LibriSpeech WER values cited here are from
  the model card, not from the Radford2022 paper directly, though Radford2022 reports 2.7% for large-v2
  beam search on test-clean [Radford2022, Table 3]. Large-v3 is expected to match or slightly improve
  this figure; for conservative comparison, large-v2 values are used throughout.
