# Results Summary: t0001_stt_benchmark

## Outcome

Gold-92 STT benchmark dataset successfully ingested and registered. 93 WAV clips with
ground-truth annotations are now version-controlled: JSONL files in git, audio in DVC
(Azure Blob Storage at `azure://ml-dvc-datasets/datasets/rail-arf-stt`).

## Assets Produced

* Dataset asset `stt-benchmark-gold-92` with 93 clips, 2 JSONL annotation files, and DVC-tracked
  audio directory.

## Baseline Observations (from gold_set.jsonl)

* Production (Deepgram) transcripts are present for all 93 clips.
* Whisper Large v2 transcripts are present for all 93 clips.
* Formal WER and entity accuracy evaluation is deferred to `t0002_baseline_evaluation`.

## Next Steps

Task `t0002_baseline_evaluation`: run WER and entity accuracy scoring on both Deepgram and
Whisper against `ground_truth.jsonl`, broken down by utterance category.
