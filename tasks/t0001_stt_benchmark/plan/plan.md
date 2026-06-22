# Plan: t0001_stt_benchmark

## Objective

Ingest the gold-92 STT benchmark dataset produced from Rezolve production voice sessions,
register it as a DVC-tracked dataset asset, and commit the pointer files and annotations to git.

## Approach

The dataset was pre-built in `tmp/stt-research/bencmark-92/gold_combined/`. This task imports
it into the ARF task structure:
* Audio files → DVC-tracked under `files/audio/`
* JSONL annotation files → committed to git (small, <100 KB each)

## Cost Estimation

$0 — no paid API or compute. Local copy + DVC push to existing Azure Blob account.

## Step by Step

1. Create task folder and ARF structure.
2. Copy JSONL files into `files/`.
3. Copy audio directory into `files/audio/`.
4. Run `dvc add files/audio/` to create `.dvc` pointer.
5. Run `dvc push` to upload audio to `azure://ml-dvc-datasets/datasets/rail-arf-stt`.
6. Write `details.json`, `description.md`, `task.json`.
7. Commit and push PR.

## Remote Machines

None required.

## Assets Needed

* Source data from `tmp/stt-research/bencmark-92/gold_combined/` (local).
* DVC Azure remote access (connection string from team vault).

## Expected Assets

* 1 dataset asset: `stt-benchmark-gold-92` (JSONL in git, audio via DVC).

## Time Estimation

< 1 hour.

## Risks and Fallbacks

* DVC push requires Azure connection string — if unavailable, commit pointer files only and
  document that `dvc push` is pending.

## Verification Criteria

* `files/audio.dvc` exists and is valid YAML.
* `files/gold_set.jsonl` has 93 lines.
* `files/ground_truth.jsonl` has 91 lines.
* `dvc status` reports clean after push.
