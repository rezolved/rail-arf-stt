# DVC Data Workflow

Large data files — audio clips, model checkpoints, evaluation datasets — are tracked by DVC and
stored in Azure Blob Storage. Git commits only the small `.dvc` pointer files.

## Remote

Storage account: `mldvcstorerezolve`
Container path: `azure://ml-dvc-datasets/datasets/rail-arf-stt`

Same storage account as `rail-arf-finetuning` and `rail-benchmarks`, different path prefix.

## Setup

1. Copy the example config:

   ```bash
   cp .dvc/config.local.example .dvc/config.local
   ```

2. Fill in the connection string from the team vault (1Password → "ml-dvc-store connection
   string"). It looks like:

   ```
   DefaultEndpointsProtocol=https;AccountName=mldvcstorerezolve;AccountKey=<KEY>;EndpointSuffix=core.windows.net
   ```

3. Verify the remote is reachable:

   ```bash
   dvc remote list
   dvc status -c
   ```

## Daily workflow

### Pull data after git pull

```bash
git pull
dvc pull
```

### Add a new large file or directory

```bash
dvc add tasks/t0005_whisper_finetune/assets/model/whisper-rezolve-v1/
git add tasks/t0005_whisper_finetune/assets/model/whisper-rezolve-v1.dvc
git add .gitignore
git commit -m "Track whisper-rezolve-v1 checkpoint via DVC"
dvc push
```

### Before opening a PR

Run `dvc push` so teammates can reproduce your data:

```bash
dvc push
git push origin task/t0005_whisper_finetune
gh pr create ...
```

## Rules

* NEVER commit audio `.wav` files, model checkpoints, or datasets >1 MB directly to git.
* ALWAYS run `dvc push` before merging — a PR with unpushed DVC data blocks anyone who pulls it.
* `.dvc/config.local` is gitignored — never commit it (it contains the secret connection string).
* The `.dvc/` directory itself (excluding `config.local`) IS committed to git.

## What goes in DVC vs git

| File type | Where |
|-----------|-------|
| Audio clips (`.wav`, `.mp3`, `.flac`) | DVC |
| Model checkpoints | DVC |
| Large JSONL / parquet (>1 MB) | DVC |
| Small annotation files (<500 KB) | Git |
| `.dvc` pointer files | Git |
| Python scripts, notebooks | Git |
| Results summaries, metrics.json | Git |
