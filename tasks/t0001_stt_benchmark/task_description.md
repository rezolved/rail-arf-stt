# STT Benchmark — Gold-92 Dataset Ingestion

## Objective

Ingest the gold-92 held-out STT benchmark dataset from Rezolve production voice sessions into the
ARF task structure, version the audio files with DVC, and register the dataset asset so all future
evaluation tasks can depend on it.

## Background

The gold-92 dataset was curated from Rezolve production brainpowa-realtime-api sessions. It
contains 93 WAV clips annotated with manually verified ground-truth transcripts plus existing
Deepgram Nova-2 and Whisper Large v2 hypotheses. Speakers include accented English (French, German,
Hebrew, Korean, Russian, Spanish native languages) and English-native Rezolve investor-relations
recordings.

This dataset is the primary held-out regression set for all STT experiments in this project. It
must never be used for training or fine-tuning — only for evaluation.

## What Was Done

- Copied 93 WAV clips from the local benchmark directory
  (`tmp/stt-research/bencmark-92/gold_combined/`) into
  `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/`.
- Created `gold_set.jsonl` (93 records) with full annotation schema: clip_id, source, filename,
  ground_truth, production (Deepgram), whisper.
- Created `ground_truth.jsonl` (93 records) with simplified clip_id + ground_truth index.
- Tracked the `audio/` directory with DVC (`dvc add`) pointing to the Azure Blob remote
  `azure://ml-dvc-datasets/datasets/rail-arf-stt`.
- Committed the `.dvc` pointer file to git; actual audio bytes go through `dvc push`.

## Constraints

- Gold-92 is **held-out only**. Never split into train or validation. Never fine-tune on it.
- Audio files are DVC-managed — do not commit raw WAV bytes to git.
- The `audio.dvc` pointer must be kept up to date if audio files change.
