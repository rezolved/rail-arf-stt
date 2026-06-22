---
spec_version: "2"
dataset_id: "stt-benchmark-gold-92"
---

# STT Benchmark Gold-92

## Metadata

| Field | Value |
|-------|-------|
| Dataset ID | stt-benchmark-gold-92 |
| Version | v1 |
| Created | 2026-06-22 |
| Task | t0001_stt_benchmark |
| Access | Proprietary — Rezolve internal only |
| License | Proprietary |
| Language | English (accented) |
| Domain | Ecommerce voice commerce / investor relations |

## Overview

The STT Benchmark Gold-92 is the primary held-out evaluation set for all Speech-to-Text research
in the `rail-arf-stt` project. It contains 93 WAV audio clips sourced from Rezolve production
voice sessions and annotated with manually verified ground-truth transcripts. The benchmark covers
ecommerce voice queries and investor-relations questions spoken by non-native English speakers
with a range of accents.

The dataset was created to address a critical gap: production STT (Deepgram Nova-2) fails silently
on domain-specific entity names — brand names, product lines, integrations — causing wrong actions
in the voice commerce assistant. Gold-92 captures exactly these failure modes in real production
audio so that research candidates can be evaluated on conditions that matter for the product.

## Content & Annotation

Each clip is a single utterance (question or short command) lasting 2–8 seconds. The annotation
schema in `files/gold_set.jsonl` contains:

- `clip_id` — unique identifier derived from session UUID and turn number (e.g.,
  `7acf2e4f-0bfe-4016-843e-bf73cda8f54a_turn3`) or from the structured naming convention for
  curated voice samples (e.g., `French_NoemieMarciano__en-NoemieMarciano-q01`).
- `source` — provenance label: `"production"` (live Rezolve sessions), `"clean_voices"` (curated
  voice samples from the rail-artifacts repository), or `"error_cases"` (clips where production
  Deepgram made a notable error).
- `filename` — WAV filename matching a file in `files/audio/` (DVC-tracked).
- `ground_truth` — manually verified correct transcript. This is the reference string for all WER
  and entity accuracy computation.
- `production` — Deepgram Nova-2 transcript from the production system at time of recording.
- `whisper` — Whisper Large v2 transcript produced offline.

The simplified `files/ground_truth.jsonl` contains only `clip_id` and `ground_truth` for
evaluation scripts that do not need the baseline hypotheses.

Speaker demographics: French (NoemieMarciano), French/Spanish (StephaniaCesborn), German
(ErcanKilic), Hebrew (FelixTseitlin), Korean (JemmaLee), Russian (OlyaShtalberg), plus
unattributed Rezolve production session speakers (English-native and non-native).

## Statistics

| Statistic | Value |
|-----------|-------|
| Total clips | 93 |
| Audio size | ~58 MB |
| Source: production sessions | ~63 clips |
| Source: clean voices (curated) | ~17 clips |
| Source: error cases | ~13 clips |
| Annotated speakers | 6 named + production pool |
| Average clip duration | ~4–6 s (estimated) |
| Audio format | WAV, mono, 16 kHz (nominal) |
| Ground-truth annotation | Manually verified |

Preliminary transcription comparison (from `gold_set.jsonl`):

- Deepgram Nova-2 and Whisper Large v2 both struggle with proper nouns: "NASDAQ" → "nas dag",
  "Rezolve" → "resolve", "Salesforce" → "sales force".
- Entity failure patterns differ between the two systems, suggesting complementary errors.

## Usage Notes

**This dataset is held-out only.** It must never be used for:

- Training or fine-tuning any model.
- Validation loss monitoring during fine-tuning.
- Prompt engineering or few-shot example selection.

Its sole permitted use is **regression evaluation**: run a candidate STT pipeline on all 93 clips,
compute WER and entity accuracy against `ground_truth.jsonl`, and compare the results against the
production Deepgram baseline.

**DVC access**: audio files are tracked by DVC. Run `dvc pull` after cloning to download them from
`azure://ml-dvc-datasets/datasets/rail-arf-stt`. The DVC connection string must be set in
`.dvc/config.local` (see `docs/dvc-data-workflow.md`).

**Cross-referencing gold_set vs ground_truth**: the full annotation set (`gold_set.jsonl`) includes
production and Whisper hypotheses; the simplified set (`ground_truth.jsonl`) includes only the
ground-truth string. Both contain all 93 clips. Evaluation scripts should load from
`ground_truth.jsonl` for the reference and separately from `gold_set.jsonl` for existing baseline
hypotheses when available.

## Main Ideas

- Gold-92 captures real production failure modes: entity names (brands, products, integrations)
  that both Deepgram and Whisper mis-transcribe in investor-relations voice sessions.
- The benchmark spans six distinct non-native speaker accents plus English-native production audio,
  making it representative of Rezolve's actual investor and ecommerce user base.
- Deepgram Nova-2 and Whisper Large v2 show different entity error patterns on gold-92, suggesting
  that a combined or ensemble approach may outperform either system alone.
- The `source` field separates production clips, curated clean-voice samples, and known error cases,
  enabling stratified evaluation by clip provenance.

## Summary

STT Benchmark Gold-92 is the canonical regression test for all STT research in `rail-arf-stt`. It
provides 93 production voice clips with manually verified ground-truth transcripts covering
ecommerce and investor-relations utterances from speakers with diverse accents. Its primary value is
that it captures exactly the entity-name failures (brand names, product lines, integrations) that
cause wrong actions in the Rezolve voice commerce assistant.

All future evaluation tasks (`stt-benchmark-run` type) must run against gold-92 and report the
registered project metrics: `entity_accuracy_gold92`, `intent_preservation_gold92`,
`action_critical_wer_gold92`, `wer_gold92`, `wrong_action_rate_gold92`, and
`latency_p50_seconds`. Statistical significance against the production Deepgram baseline must be
reported using BCa bootstrap with 10 000 resamples on all 93 paired samples.
