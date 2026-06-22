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
