# Category: Audio Datasets

Collection, curation, ground-truth annotation, and DVC versioning of production audio used for
STT experiments.

[Back to Dashboard](../README.md)

**Detail pages**: [Suggestions (6)](../suggestions/by-category/audio-datasets.md) | [Datasets
(1)](../datasets/by-category/audio-datasets.md)

---

## Papers (0)

No papers in this category.

## Tasks (0)

No tasks related to this category.

## Answers (0)

No answers in this category.

## Suggestions (6 open, 0 closed)

<details>
<summary>📂 <strong>Expand short-clip robustness benchmark to 200+ clips with real
production audio diversity</strong> (S-0014-03)</summary>

**Kind**: dataset | **Priority**: medium | **Date**: 2026-06-30 | **Source**:
[t0014_granite_short_clip_robustness](../../tasks/t0014_granite_short_clip_robustness/)

The synthetic short-clip dataset (44 clips, 7-14 per bin) is underpowered for stratum-level
significance testing (MDD ±20 pp for empty rate). Expanding to 200+ clips from a wider variety
of production audio sessions, accents, and domain terms would enable statistically reliable
per-bin comparisons and better characterize Granite behavior in the <1 s and 1-2 s strata
where entity accuracy is near zero for all models. Recommended task types:
audio-dataset-curation.

</details>

<details>
<summary>📂 <strong>Preprocess Rezolve investor-relations transcript corpus for KenLM
domain language model training</strong> (S-0008-03)</summary>

**Kind**: dataset | **Priority**: medium | **Date**: 2026-06-25 | **Source**:
[t0008_moonshine_v2_benchmark](../../tasks/t0008_moonshine_v2_benchmark/)

The t0008 shallow fusion feasibility assessment (Approach 1) identified that implementing
log-linear N-best rescoring for Moonshine requires a domain LM trained on Rezolve
investor-relations text. The corpus exists (annual reports, investor presentations, brainpowa
session transcripts) but is noted as not yet preprocessed. Curate and clean this corpus into a
plaintext format suitable for KenLM trigram training, covering at minimum the 31-term domain
vocabulary and surrounding IR context. Estimated size: 50k–500k tokens. This unblocks both the
Moonshine shallow fusion task (S-0005-04) and any future domain adaptation work. Recommended
task types: audio-dataset-curation.

</details>

<details>
<summary>🧪 <strong>Domain fine-tuning of Whisper turbo on Rezolve investor-relations
audio</strong> (S-0002-04)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

Fine-tune Whisper turbo on Rezolve-domain audio (investor-relations sessions, brand names,
product terms) to close the vocabulary gap revealed by the baseline. Both large-v3 and turbo
achieved identical entity accuracy (25.2%), confirming model size is not the bottleneck —
training data distribution is. The WhisperNER supervised fine-tuning comparison showed 81.35
F1 on a domain-specific corpus vs our 25.2%, indicating large headroom. A fine-tuning task
should collect or synthesize domain audio+transcript pairs, run LoRA or full fine-tune on
turbo (pragmatic: 25% lower latency than large-v3 with no accuracy loss), and evaluate on
gold-92 production clips (baseline: 8.8%). Recommended task types: whisper-finetuning-run,
experiment-run.

</details>

<details>
<summary>📂 <strong>Expand gold-92 benchmark with more production clips and fix
annotation inconsistencies</strong> (S-0002-05)</summary>

**Kind**: dataset | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

Three findings motivate benchmark expansion: (1) the 34-clip production subset scores only
8.8% entity accuracy but drives all business-critical decisions; a larger production sample
would tighten BCa confidence intervals and reduce the risk of outlier clips dominating
results; (2) at least three clips (Examples 10, 13, 14) show verbatim transcript matches
scoring 0 entity accuracy due to annotation normalisation mismatches — the annotation schema
needs an audit; (3) clip error_en_0005 has Cyrillic ground truth indicating upstream data
quality issues. The expanded benchmark should also apply blockwise bootstrap by speaker for
the clean_voices subset as recommended by Liu2020. Recommended task types:
audio-dataset-curation, data-analysis.

</details>

<details>
<summary>📂 <strong>Annotate gold-92 with entity span offsets to enable E-WER and
Slot F1</strong> (S-0003-03)</summary>

**Kind**: dataset | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../../tasks/t0003_literature_review_entity_stt/)

Add entity-offset markup to gold-92 ground-truth transcripts, tagging brand names, product
names, and SKUs with character-level span annotations. This unblocks computation of E-WER
(required to evaluate RECOVER) and Slot F1 (required to evaluate Zheng2026 selective span
editing). Without entity spans, only substring-match and overall WER can be reported on
gold-92. The annotation should cover all 93 clips and follow a schema compatible with the
Contextual Earnings-22 format (Durmus2026) to enable cross-benchmark comparison. Recommended
task types: audio-dataset-curation.

</details>

<details>
<summary>📊 <strong>Stratify gold-92 evaluation by speaker accent to quantify
accent-induced entity errors</strong> (S-0003-07)</summary>

**Kind**: evaluation | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0003_literature_review_entity_stt](../../tasks/t0003_literature_review_entity_stt/)

WildASR (Tay2026) confirmed that model robustness does not transfer across accent conditions
and that ASR systems hallucinate plausible but unspoken content under degraded inputs. Gold-92
contains six non-native English speaker clips, making accent-induced entity errors a direct
project risk. Stratify all gold-92 evaluation results by speaker accent group and compare
entity accuracy between native and non-native speakers. If accent is the primary driver of
entity errors rather than lexical ambiguity, post-correction methods (RECOVER, Ron2026) will
have limited effect and ASR-stage improvements should be prioritized instead. Recommended task
types: data-analysis, stt-benchmark-run.

</details>
