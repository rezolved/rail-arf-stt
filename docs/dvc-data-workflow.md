# DVC Data Workflow

Large data files — audio clips, model checkpoints, evaluation datasets — are tracked by DVC and
stored in Azure Blob Storage. Git commits only the small `.dvc` pointer files.

## Remote

Storage account: `mldvcstorerezolve` Container path: `azure://ml-dvc-datasets/datasets/rail-arf-stt`

Same storage account as `rail-arf-finetuning` and `rail-benchmarks`, different path prefix.

## Setup

1. Authenticate with the Azure CLI — the default and recommended path, no key to fetch, rotate, or
   leak:

   ```bash
   az login
   ```

   `.dvc/config` carries no credentials (`account_name` only), so `dvc` falls back to
   `DefaultAzureCredential`, which picks up your `az login` session via `AzureCliCredential`.
   `exclude_managed_identity_credential = true` is set in `.dvc/config` because on Azure ML compute
   instances `ManagedIdentityCredential` fails with a non-standard SSO error that aborts the whole
   `DefaultAzureCredential` chain before it reaches `AzureCliCredential` — without that flag,
   `dvc pull`/`dvc push` hang or fail even with a valid `az login` session. Your Azure AD identity
   needs the **Storage Blob Data Contributor** role (or Reader, for pull-only) on the
   `mldvcstorerezolve` storage account.

2. **Fallback (non-interactive / CI, where `az login` isn't available):** copy the example config
   and fill in an account-key connection string from the team vault instead:

   ```bash
   cp .dvc/config.local.example .dvc/config.local
   ```

   Fill in the connection string from the team vault (1Password → "ml-dvc-store connection string").
   It looks like:

   ```
   DefaultEndpointsProtocol=https;AccountName=mldvcstorerezolve;AccountKey=<KEY>;EndpointSuffix=core.windows.net
   ```

   `.dvc/config.local` is gitignored, so this credential never enters version control. Note: any
   credential in `.dvc/config.local` takes priority over `az login` — remove or empty it if you want
   to switch back to `az login`.

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
* `az login` is the default auth method (see Setup step 1); `.dvc/config.local` is only the fallback
  for non-interactive/CI use. It is gitignored — never commit it (it contains the secret connection
  string).
* The `.dvc/` directory itself (excluding `config.local`) IS committed to git.

## What goes in DVC vs git

| File type | Where |
| --- | --- |
| Audio clips (`.wav`, `.mp3`, `.flac`) | DVC |
| Model checkpoints | DVC |
| Large JSONL / parquet (>1 MB) | DVC |
| Small annotation files (<500 KB) | Git |
| `.dvc` pointer files | Git |
| Python scripts, notebooks | Git |
| Results summaries, metrics.json | Git |
