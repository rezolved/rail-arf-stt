---
spec_version: "3"
paper_id: "no-doi_Caubriere2020_ner-from-speech-survey"
citation_key: "Caubriere2020"
summarized_by_task: "t0002_baseline_evaluation"
date_summarized: "2026-06-23"
---
# Where are we in Named Entity Recognition from Speech?

## Metadata

* **File**: `files/caubriere_2020_ner-from-speech-survey.pdf`
* **Published**: 2020
* **Authors**: Antoine Caubrière 🇫🇷, Sophie Rosset 🇫🇷, Yannick Estève 🇫🇷, Antoine Laurent 🇫🇷,
  Emmanuel Morin 🇫🇷
* **Venue**: LREC 2020 (12th Language Resources and Evaluation Conference), Marseille, France
* **DOI**: N/A (ELRA publication, no DOI assigned)

## Abstract

Named entity recognition (NER) from speech is usually made through a pipeline process that consists
in (i) processing audio using an automatic speech recognition system (ASR) and (ii) applying a NER
to the ASR outputs. The latest data available for named entity extraction from speech in French were
produced during the ETAPE evaluation campaign in 2012. Since the publication of ETAPE's campaign
results, major improvements were done on NER and ASR systems, especially with the development of
neural approaches for both of these components. In addition, recent studies have shown the
capability of End-to-End (E2E) approach for NER / SLU tasks. In this paper, we propose a study of
the improvements made in speech recognition and named entity recognition for pipeline approaches.
For this type of systems, we propose an original 3-pass approach. We also explore the capability of
an E2E system to do structured NER. Finally, we compare the performances of ETAPE's systems
(state-of-the-art systems in 2012) with the performances obtained using current technologies. The
results show the interest of the E2E approach, which however remains below an updated pipeline
approach.

## Overview

This paper revisits NER from speech eight years after the French ETAPE evaluation campaign (2012),
which had been the last major benchmark for extracting tree-structured named entities from spoken
French. The authors ask a straightforward question: given the dramatic improvements in both ASR
(HMM-GMM to HMM-DNN chain models) and NER (CRF to bLSTM-CRF), how much has the state of the art
actually advanced on the same ETAPE test set?

The paper makes two concrete contributions. First, it introduces a 3-pass decomposition for
tree-structured NER: instead of concatenating all BIO tags (which balloons to ~1,690 possible labels
with severe sparsity), the annotation tree is split into three hierarchical levels — root entity
types, intermediate types/components, and leaf components — each handled by a separate sequence
labeler. The predictions from each level feed forward as additional features to the next. This
allows the authors to match the 2012 ETAPE winning system (which used 68 binary CRF models) using
only 3 CRF models, and to substantially outperform it with modern bLSTM-CRF components.

The second contribution is an end-to-end (E2E) system based on DeepSpeech 2, where NE tags are
encoded directly into the character-level output sequence. A Curriculum-based Transfer Learning
(CTL) strategy trains the model progressively: first on ASR, then on NE types only, then on full
structured annotation. While the E2E system shows clear progress over the 2012 baseline (**56.9%
SER** vs. **59.3%**), it still falls behind the updated pipeline system (**51.1% SER**), suggesting
that for tree-structured NER the pipeline approach remains superior with current technology.

The evaluation metric throughout is the Slot Error Rate (SER) from the ETAPE campaign, which counts
boundary substitutions (weight 0.5), type substitutions (weight 0.5), combined boundary and type
substitutions (weight 1), deletions (weight 1), and insertions (weight 1), normalized by the number
of reference slots. Lower SER is better. This metric captures both span detection and type
classification errors in a single number, making it the primary entity-level error measure for this
benchmark — directly analogous to Entity Error Rate (EER) used in related NER from speech
literature.

## Architecture, Models and Methods

### Task Definition

Named entities follow the Quaero guideline with 8 main types (amount, event, func, loc, org, pers,
prod, time), 39 type+subtype combinations (e.g., `loc.adm.town`), and 28 components (e.g., `name`,
`kind`). Entities have unlimited nesting depth (tree structure), making standard sequence labeling
intractable without decomposition.

### Pipeline Systems

**CRF baseline**: Trained with WAPITI using a [-2,+2] word window, character prefixes and suffixes,
yes/no orthographic features (capitalization, non-alphanumeric), and optional morpho-syntactic
features from TreeTagger. Trained with the rprop algorithm, max 40 iterations.

**3-pass decomposition**: The BIO annotation tree is split into three levels:

* Level 1 (root): 96 predictable tags; trained first
* Level 2 (intermediate): 187 predictable tags; receives Level 1 predictions as features
* Level 3 (leaves): 57 predictable tags; receives Level 1 and Level 2 predictions as features

**bLSTM-CRF (NeuroNlp2)**: Based on Ma and Hovy (2016). Architecture: 1 CNN layer for character
embeddings, concatenated with word embeddings, fed into 2 bLSTM hidden layers (200 units each), then
CRF decoder. Dropout on bLSTM input/output and CNN input.

**ASR pipeline component**: Kaldi chain model (lattice-free MMI), TDNN acoustic model with sMBR
discriminative training. Language model: regular backoff n-gram, 160k vocabulary, 2-gram decoding
followed by 3-gram and 4-gram rescoring. Trained on approximately 220 hours (ESTER 1&2, REPERE,
VERA).

### End-to-End System

Based on DeepSpeech 2: 2 x 2D-CNN layers → 5 bLSTM layers with sequence-wise batch normalization →
softmax. Loss: CTC over character sequences. Input: log-spectrograms on 20ms windows. NE tags are
encoded as special characters in the output sequence (start and end delimiters), enabling the model
to emit both words and NE annotations jointly.

**Curriculum-based Transfer Learning (CTL)**: (1) train ASR task on all ~220 hours of audio; (2)
transfer to NER with NE types only; (3) transfer to NER with full structured annotation. All model
parameters except the top softmax layer are retained across transfers. Language model decoding:
3-gram and 4-gram LMs trained on ETAPE + Quaero train sets applied during beam search.

### Evaluation Metric

Slot Error Rate (SER) from Makhoul et al. (1999):

```
SER = (0.5*Sb + 0.5*St + 1*Sbt + 1*D + 1*I) / R
```

Where Sb = boundary substitutions, St = type substitutions, Sbt = both, D = deletions, I =
insertions, R = reference slot count. All experiments use the official ETAPE evaluation scripts with
manual NE annotations projected onto ASR transcripts for comparability.

## Results

* **2012 ETAPE baseline** (68-CRF-model pipeline on ASR2012): **59.3% SER** — reference point
* ASR2012 WER: **21.8%**; ASR2019 WER: **16.5%** (**24.3% relative** WER improvement)
* Sys A (1-pass CRF + ASR2012): **69.4% SER** — worse than 2012 baseline due to label sparsity
* Sys B (3-pass CRF + ASR2012): **59.5% SER** — matches 2012 baseline with only 3 CRF models vs. 68;
  **14.3% relative gain** over Sys A
* Sys C (3-pass CRF + ASR2019): **55.0% SER** — **7.6% relative** gain from better ASR
* Sys D (3-pass bLSTM-CRF + ASR2012): **56.1% SER** — neural NER improves over CRF
* Sys E (3-pass bLSTM-CRF + ASR2019): **51.1% SER** — new pipeline state of the art; **13.8%
  relative** improvement over 2012 ETAPE baseline
* E2E greedy (ASR → NERstruct): **62.9% SER**
* E2E greedy with CTL (ASR → NERtypes → NERfull): **61.9% SER** — CTL cuts SER by 1.0 pt
* E2E with 4-gram LM and CTL: **56.9% SER** — best E2E result
* Pipeline vs. best E2E: **51.1% vs. 56.9% SER** — pipeline leads by **10.2% relative**

## Innovations

### 3-Pass Tree Decomposition for Structured NER

The paper introduces a systematic decomposition of tree-structured BIO annotations into three
hierarchical levels (root → intermediate → leaf), each handled by a separate sequence labeler with
cascading predictions. This reduces the label space from ~1,690 concatenated tags with severe
sparsity to 96, 187, and 57 tags respectively, making standard CRF and bLSTM-CRF models tractable.
Three models replace a 68-model ensemble while matching its performance, and with modern components
significantly outperform it.

### Curriculum-Based Transfer Learning for E2E Structured NER

Applying CTL to tree-structured entities by inserting an intermediate training stage on NE types
only (before fine-tuning on full structured annotation). This exploits the hierarchical dependency
between types and components, reducing greedy-decoding SER from **62.9%** to **61.9%** and
beam-search SER from **57.3%** to **56.9%**.

### Joint Character-Level NE Tag Encoding for E2E

NE start and end tags are encoded as single special characters within the DeepSpeech 2
character-sequence output, allowing the CTC-trained model to emit structured NE annotation jointly
with word transcription. This eliminates the need for a separate NER stage and avoids the
label-sparsity problem of BIO encoding by representing nested tags as character sequences.

## Datasets

* **ETAPE corpus** (Gravier et al., 2012): 36 hours of French radio and TV speech (France Inter,
  LCP, BFMTV, TV8), recorded 2010–2011. Split: 22h train / 7h dev / 7h test. Fully manually
  transcribed and annotated with Quaero tree-structured named entities. Distributed by ELRA for
  research purposes.
* **Quaero corpus** (Grouin et al., 2011): 100 hours of French radio and TV speech, 1998–2004. Used
  to augment NER training data. Annotated with Quaero guidelines.
* **ASR training corpora**: ESTER 1&2 (Galliano et al., 2009), REPERE (Giraudel et al., 2012), VERA
  (Goryainova et al., 2014) — approximately 220 hours total of French speech for acoustic model
  training.
* All corpora are French-language, broadcast news/talk show domain. ETAPE and Quaero are available
  through ELRA (European Language Resources Association).

## Main Ideas

* The SER (Slot Error Rate) metric from the ETAPE campaign is the standard evaluation measure for
  structured NER from speech; it penalizes boundary errors, type errors, and combined errors with
  calibrated weights, providing a more informative entity-level error signal than flat entity F1 for
  evaluating entity accuracy in ASR output. This directly informs design of an entity accuracy
  metric for the gold-92 benchmark.
* ASR quality has a large multiplicative effect on downstream entity extraction: reducing WER from
  **21.8%** to **16.5%** (24.3% relative) translated to **4.4–5.0 SER point** gains regardless of
  the NER component used. Improving STT accuracy first — e.g., using Whisper over Deepgram — will
  produce proportional entity accuracy gains before any post-correction.
* A pipeline approach (STT followed by entity post-correction) consistently outperforms joint E2E
  transcription + NER (**51.1% vs. 56.9% SER**), supporting the two-stage architecture planned for
  this project (Whisper + entity correction pass).
* The 3-pass cascading idea is transferable: for Rezolve's flat entity types (brands, products,
  SKUs), a single-pass model suffices, but injecting entity-type hypotheses from a first pass as
  features into a correction model mirrors the hierarchical cascade logic.
* Domain-adapted neural NER (bLSTM-CRF) on ASR output provides the largest single improvement over
  legacy CRF systems; the analogous investment for this project is an entity-aware post-correction
  or contextual boosting layer applied to Whisper output.

## Summary

Caubrière et al. (2020) revisit named entity recognition from speech using the French ETAPE
benchmark, eight years after the original evaluation campaign established the prior state of the
art. Their central question is how much the combination of modern neural ASR (Kaldi chain model,
16.5% WER) and NER systems (bLSTM-CRF) improves entity extraction from spoken French compared to
2012-era HMM-GMM and CRF baselines. The paper is motivated by the complete absence of new published
results on this tree-structured NER-from-speech benchmark since 2012, despite major advances in both
component technologies.

The methodology centers on two contributions. For pipeline systems, the authors introduce a 3-pass
decomposition that splits the Quaero-style BIO annotation tree into three hierarchical levels, each
trained as a separate sequence labeler with cascading predictions, reducing the tag space from
~1,690 to manageable subsets of 96, 187, and 57 tags. For end-to-end systems, they adapt DeepSpeech
2 with Curriculum-based Transfer Learning, encoding NE tags as special characters in CTC output and
training progressively from ASR to NE-types to full structured annotation. All systems are evaluated
on the official ETAPE test set using Slot Error Rate (SER), which jointly penalizes span boundary
errors and entity type errors with calibrated weights.

The best pipeline system (3-pass bLSTM-CRF + updated ASR) achieves **51.1% SER**, a **13.8% relative
improvement** over the 2012 ETAPE state of the art (**59.3% SER**). The best E2E system reaches
**56.9% SER**, showing a 4% relative improvement over the baseline but remaining **10.2% relative**
behind the pipeline. Improved ASR alone — reducing WER from 21.8% to 16.5% — contributed 4.4–5.0 SER
points across all NER configurations.

For this project, the paper is most valuable as a methodological reference for entity-level
evaluation metrics in STT systems. The SER/EER decomposition (boundary errors vs. type errors,
weighted separately) directly informs the entity accuracy metric design for the gold-92 benchmark.
The finding that ASR quality improvements translate proportionally into downstream entity accuracy
gains supports prioritizing Whisper Large v3 over Deepgram as the ASR backbone before investing in
post-correction layers. The pipeline-beats-E2E result also validates the two-stage architecture (STT
\+ entity post-correction) planned for this project over a hypothetical joint model.
