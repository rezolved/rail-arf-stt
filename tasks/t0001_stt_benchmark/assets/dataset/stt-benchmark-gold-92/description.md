# STT Benchmark Gold-92

## Overview

Gold held-out benchmark for STT evaluation in the Rezolve voice commerce assistant. 93 WAV
clips recorded from real production sessions during an investor-relations demonstration. Each
clip is annotated with a manually verified ground-truth transcript and compared against two
baseline STT systems (production Deepgram and Whisper Large v2).

## Composition

| Category | Count | Notes |
|----------|-------|-------|
| Product capability questions | ~15 | "What is brainpowa?", integrations |
| Investor relations | ~10 | Stock, employees, revenue, NASDAQ |
| Technical / API questions | ~10 | Languages, platforms, enterprise |
| Partner / integration questions | ~8 | Salesforce, Shopify, Google Cloud, Azure |
| Short commands | ~5 | "Get stock price", "Contact sales" |
| Other / demo questions | ~45 | Mixed investor-site queries |

Speakers: multiple, predominantly French-accented English.

## Files

* `files/gold_set.jsonl` — 93 records; fields: `clip_id`, `source`, `filename`,
  `ground_truth`, `production` (Deepgram), `whisper` (Whisper Large v2).
* `files/ground_truth.jsonl` — 91 records; fields: `clip_id`, `ground_truth` (ground truth
  only, no model outputs).
* `files/audio/` — 93 WAV files, DVC-tracked. Run `dvc pull` to download.

## Key observations (preliminary)

* Production (Deepgram) struggles with proper nouns: "NASDAQ" → "nas dag",
  "Salesforce" → "sales force", "Rezolve" → "resolve".
* Whisper shows similar entity errors but slightly different failure modes.
* Both systems handle common commerce vocabulary well.

## Usage

This dataset is **held-out only**. It MUST NOT be used for training, fine-tuning, or prompt
engineering. Its sole purpose is regression evaluation: run a candidate STT system on all 93
clips and compare WER + entity accuracy against ground truth.
