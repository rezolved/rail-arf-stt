# ✅ STT Benchmark — Gold-92 Dataset Ingestion

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0001_stt_benchmark` |
| **Status** | ✅ completed |
| **Started** | 2026-06-22T00:00:00Z |
| **Completed** | 2026-06-22T00:00:00Z |
| **Duration** | 0s |
| **Task types** | `audio-dataset-curation` |
| **Categories** | [`audio-datasets`](../../by-category/audio-datasets.md), [`stt-evaluation`](../../by-category/stt-evaluation.md) |
| **Expected assets** | 1 dataset |
| **Step progress** | 6/6 |
| **Task folder** | [`t0001_stt_benchmark/`](../../../tasks/t0001_stt_benchmark/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0001_stt_benchmark/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source: [`task_description.md`](../../../tasks/t0001_stt_benchmark/task_description.md)*

# STT Benchmark — Gold-92 Dataset Ingestion

## Objective

Ingest the gold-92 held-out STT benchmark dataset from Rezolve production voice sessions into
the ARF task structure, version the audio files with DVC, and register the dataset asset so
all future evaluation tasks can depend on it.

## Background

The gold-92 dataset was curated from Rezolve production brainpowa-realtime-api sessions. It
contains 93 WAV clips annotated with manually verified ground-truth transcripts plus existing
Deepgram Nova-2 and Whisper Large v2 hypotheses. Speakers include accented English (French,
German, Hebrew, Korean, Russian, Spanish native languages) and English-native Rezolve
investor-relations recordings.

This dataset is the primary held-out regression set for all STT experiments in this project.
It must never be used for training or fine-tuning — only for evaluation.

## What Was Done

- Copied 93 WAV clips from the local benchmark directory
  (`tmp/stt-research/bencmark-92/gold_combined/`) into
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/`.
- Created `gold_set.jsonl` (93 records) with full annotation schema: clip_id, source,
  filename, ground_truth, production (Deepgram), whisper.
- Created `ground_truth.jsonl` (93 records) with simplified clip_id + ground_truth index.
- Tracked the `audio/` directory with DVC (`dvc add`) pointing to the Azure Blob remote
  `azure://ml-dvc-datasets/datasets/rail-arf-stt`.
- Committed the `.dvc` pointer file to git; actual audio bytes go through `dvc push`.

## Constraints

- Gold-92 is **held-out only**. Never split into train or validation. Never fine-tune on it.
- Audio files are DVC-managed — do not commit raw WAV bytes to git.
- The `audio.dvc` pointer must be kept up to date if audio files change.

</details>

## Metrics

| Metric | Value |
|--------|-------|
| [`note`](../../metrics-results/note.md) | **Formal metrics (WER, entity accuracy) will be reported in t0002_baseline_evaluation.** |
| [`dataset_clips`](../../metrics-results/dataset_clips.md) | **93** |
| [`ground_truth_entries`](../../metrics-results/ground_truth_entries.md) | **91** |

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| dataset | [STT Benchmark Gold-92](../../../tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/) | [`description.md`](../../../tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/description.md) |

## Research

* [`research_code.md`](../../../tasks/t0001_stt_benchmark/research/research_code.md)
* [`research_internet.md`](../../../tasks/t0001_stt_benchmark/research/research_internet.md)
* [`research_papers.md`](../../../tasks/t0001_stt_benchmark/research/research_papers.md)

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0001_stt_benchmark/results/results_summary.md)*

# Results Summary: t0001_stt_benchmark

## Outcome

Gold-92 STT benchmark dataset successfully ingested and registered. 93 WAV clips with
ground-truth annotations are now version-controlled: JSONL files in git, audio in DVC (Azure
Blob Storage at `azure://ml-dvc-datasets/datasets/rail-arf-stt`).

## Assets Produced

* Dataset asset `stt-benchmark-gold-92` with 93 clips, 2 JSONL annotation files, and
  DVC-tracked audio directory.

## Baseline Observations (from gold_set.jsonl)

* Production (Deepgram) transcripts are present for all 93 clips.
* Whisper Large v2 transcripts are present for all 93 clips.
* Formal WER and entity accuracy evaluation is deferred to `t0002_baseline_evaluation`.

## Next Steps

Task `t0002_baseline_evaluation`: run WER and entity accuracy scoring on both Deepgram and
Whisper against `ground_truth.jsonl`, broken down by utterance category.

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0001_stt_benchmark/results/results_detailed.md)*

# Results Detailed: t0001_stt_benchmark

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total clips | 93 |
| Ground-truth entries | 91 |
| Audio size | ~58 MB |
| Avg clip duration (estimated) | ~4 s |
| Domain | Investor-relations / ecommerce voice |
| Language | English (French accent) |

## File Inventory

| File | Records | Size | Storage |
|------|---------|------|---------|
| `files/gold_set.jsonl` | 93 | 36 KB | git |
| `files/ground_truth.jsonl` | 91 | 16 KB | git |
| `files/audio/` | 93 WAV | 58 MB | DVC |

## DVC Pointer

Audio is tracked at `files/audio.dvc`. After `dvc push`, data lives at:
`azure://ml-dvc-datasets/datasets/rail-arf-stt` in the `mldvcstorerezolve` account.

## Preliminary Observations

From manual inspection of `gold_set.jsonl` (production vs ground_truth):

* Deepgram production transcriptions are frequently correct on common words but fail on:
  * Product/company proper nouns: "Rezolve AI" → "resolve AI", "NASDAQ" → "nas dag"
  * Technical terms: "brainpowa" → various
  * Integration names: "Salesforce" → "sales force"
* Whisper shows a different error profile — sometimes more accurate on brand names but less
  consistent on accented speech.
* The two-clip discrepancy between `gold_set.jsonl` (93) and `ground_truth.jsonl` (91) should
  be investigated in `t0002`.

</details>
