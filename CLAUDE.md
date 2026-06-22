# rail-arf-stt — STT Research for Ecommerce Voice AI (ARF)

Autonomous-research project to benchmark and improve Speech-to-Text (STT) for Rezolve's voice
commerce assistant. Goal: beat production Deepgram on entity accuracy (brands, products, SKUs)
and intent preservation using a domain-specific evaluation harness, with fast latency (<800 ms
p50 voice-to-action) and confidence-based routing to reduce wrong-action rate below 2%.

This repo is a private fork of `rezolved/rail-arf` (Rezolve's canonical ARF fork-base). See
`project/description.md` for the full goal and success criteria.

## Commands

```bash
# Setup
uv sync                                            # Install deps
uv run pre-commit install                          # Activate git hooks
python3 doctor.py                                  # Validate environment

# Development
uv run python -u <script.py>                                       # Run a script
uv run python -m arf.scripts.utils.run_with_logs --task-id <id> -- <cmd>   # ARF logging

# Quality
uv run flowmark --inplace --nobackup <path.md>      # Format markdown
uv run ruff check --fix . && uv run ruff format .   # Lint and format Python
uv run mypy .                                        # Type check
uv run pytest                                        # Run framework tests in arf/tests

# DVC (large data files — see docs/dvc-data-workflow.md)
dvc pull                                            # Download all tracked data files
dvc push                                            # Upload new/updated data files
dvc add <file-or-dir>                               # Track a new large file with DVC
```

## DVC data workflow

Large data files (audio clips, model checkpoints, large eval datasets) are tracked by DVC and
stored in Azure Blob Storage at `azure://ml-dvc-datasets/datasets/rail-arf-stt` (account:
`mldvcstorerezolve`). Git commits only the small `.dvc` pointer files — not the data bytes.

**After `git pull`, always run `dvc pull` to sync data.**

Setup: copy `.dvc/config.local.example` to `.dvc/config.local` and fill in the connection string
from the team vault (same key as `rail-benchmarks` and `rail-arf-finetuning`). See
`docs/dvc-data-workflow.md` for full instructions.

Key rules for task agents:

* Any task that produces audio files, model checkpoints, or multi-MB eval sets MUST gitignore
  the data and track it with `dvc add`.
* Run `dvc push` before merging the task PR so teammates can `dvc pull` the data.
* NEVER commit raw audio blobs to git — only `.dvc` pointer files are committed.

## Key References

* Project description and goals: `project/description.md`
* STT strategy and phase plan: Confluence — STT Strategy for Ecommerce Voice AI
* Benchmark data (gold 92 clips): `tasks/t0001_stt_benchmark/` (DVC-tracked audio)
* New project onboarding: `arf/skills/setup-project/SKILL.md`
* ARF architecture and glossary: `arf/README.md`
* Lessons from prior Rezolve projects: `LESSONS.md`
* Python style guide: `arf/styleguide/python_styleguide.md`
* Markdown style guide: `arf/styleguide/markdown_styleguide.md`
* DVC workflow: `docs/dvc-data-workflow.md`

## Benchmark

The primary metric is **entity accuracy** on the gold-92 benchmark (`t0001_stt_benchmark`):
93 WAV clips from Rezolve production sessions (investor-relations domain, accented English)
annotated with ground-truth transcripts. Secondary metrics: WER, intent preservation, latency.

NEVER train or tune on gold-92 — it is a held-out regression set only.

## Rezolve conventions

* Always write **brainpowa** in lowercase — never "Brainpowa" or "BrainPowa".
* Use the `gh` CLI for GitHub operations (PR reads, diffs, status checks). Never paste credentials
  into commits, logs, or agent prompts.
* External communications (PRs, Jira, Confluence, Slack) go in English even when prompting in
  Russian.
