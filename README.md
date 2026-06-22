# STT Research for Ecommerce Voice AI

## Goal

Build and evaluate a Speech-to-Text harness optimised for Rezolve's voice commerce assistant. The
current production system (Deepgram) fails on domain-specific entities — brand names, product lines,
integrations, investor-relations terms — causing silent action failures that break the user
experience. This project benchmarks existing STT systems on a held-out gold set of production audio,
evaluates entity-aware post-correction strategies, and investigates domain-adapted fine-tuning of
Whisper-class models to achieve entity accuracy >92% while keeping voice-to-action latency under 800
ms p50.

## Research Questions

1. What is the current WER and entity accuracy of Deepgram (production) and Whisper Large v3 on the
   gold-92 benchmark, broken down by utterance category and entity type?
2. Do entity-aware post-correction strategies (LLM correction pass, contextual boosting, custom
   vocabulary injection) materially close the gap on action-critical spans without exceeding the 800
   ms p50 latency budget?
3. Does domain-adapted fine-tuning of Whisper-class models on Rezolve production audio improve
   entity accuracy on the gold-92 benchmark without regressing general English WER?
4. What confidence-routing policy (accept / correct / clarify / fallback thresholds) achieves
   wrong-confident-action rate <2% and clarification rate <5% on the gold-92 benchmark?
5. What is the minimum viable dataset size and composition for fine-tuning to achieve a meaningful
   entity accuracy gain, and how does the gain scale with data volume?

## Success Criteria

- Entity accuracy >92% on gold-92 (action-critical spans only) for at least one candidate system.
- Intent preservation >95% on gold-92 for the best candidate.
- Action-critical WER <8% on gold-92 for the best candidate.
- Wrong confident action rate <2% on gold-92 under the chosen confidence-routing policy.
- Voice-to-action latency p50 <800 ms end-to-end (STT + correction + routing).
- At least one STT condition beats production Deepgram on entity accuracy with statistical
  significance (BCa bootstrap p <0.05, n=93 paired samples).

## Current Phase

Phase 0 complete: gold-92 benchmark dataset ingested and DVC-tracked (`t0001_stt_benchmark`). Next
step: run baseline WER and entity accuracy evaluation for Deepgram and Whisper Large v3 on gold-92
(`t0002_baseline_evaluation`).

## Results Dashboard

See [`overview/README.md`](overview/README.md) for aggregated metrics, task status, and the
per-category results breakdown.

## Getting Started

```bash
git clone https://github.com/rezolved/rail-arf-stt.git
cd rail-arf-stt
uv sync                         # Install Python deps
uv run pre-commit install       # Activate git hooks
cp .dvc/config.local.example .dvc/config.local   # Fill in Azure connection string
dvc pull                        # Download gold-92 audio and any tracked results
uv run python3 doctor.py        # Validate environment
```

Do **not** re-run `/setup-project` — that is a one-time initialization for fresh forks. Join
`#stt-research` on Slack for discussion.

## Daily Workflow

```bash
# Plan a new task
/create-task

# Execute a planned task
/execute-task t0002_baseline_evaluation

# After a task completes, generate next task suggestions
/human-brainstorm

# Regenerate the results dashboard
uv run python -m arf.scripts.overview.materialize
```

## Key Rules

These are enforced by verificators — violations block commits.

- **Every CLI call** is wrapped in `uv run python -m arf.scripts.utils.run_with_logs -- <cmd>` so
  logs are captured.
- **Tasks only modify files inside their own folder.** The only top-level files a task may touch are
  `pyproject.toml`, `uv.lock`, `ruff.toml`, and `.gitignore`.
- **Every task stage and every action is a separate, well-described commit.**
- **Completed task folders are immutable.** Fix mistakes via correction files in a new task, never
  by editing past folders.
- **Read through aggregators, never walk task folders directly.** Raw globs miss the corrections
  overlay.
- **Metrics must be registered in `meta/metrics/` before a task reports them.** Unregistered metrics
  fail verification.
- **Audio and model files go in DVC, never in git.** Run `dvc add` then `dvc push` before merging.

## Project Structure

```text
arf/            Framework code: scripts, skills, specifications, styleguide, docs, tests
meta/           Project metadata: asset_types/, categories/, metrics/, task_types/
tasks/          One folder per research task (created by the create-task skill)
overview/       Materialized aggregator dashboard (regenerated, committed)
project/        Project-level files: description.md, budget.json, azure_vm.json
docs/           Project docs: dvc-data-workflow.md
.dvc/           DVC config and cache pointers
.claude/        Claude Code config (settings.json, rules/, skills/ symlinks)
.codex/         Codex CLI config (agents/, skills/ symlinks)
CLAUDE.md       Project overview loaded at Claude Code session start
pyproject.toml  Python deps and tooling config
doctor.py       Environment validation script
```

## Categories

- **audio-datasets** — Audio Datasets: collection, curation, annotation, and DVC versioning of
  production audio
- **commercial-apis** — Commercial APIs: integration and evaluation of third-party STT APIs
  (Deepgram Nova-2)
- **confidence-routing** — Confidence Routing: threshold-based accept / correct / clarify / fallback
  decision logic
- **entity-correction** — Entity Correction: post-correction strategies to improve domain-specific
  entity accuracy
- **latency-profiling** — Latency Profiling: end-to-end voice-to-action latency measurement
- **stt-evaluation** — STT Evaluation: benchmarking ASR systems on entity accuracy, WER, and intent
  preservation
- **whisper-finetuning** — Whisper Fine-Tuning: domain-adapted fine-tuning of Whisper-class models

## Metrics

Key metrics (🎯 headline):

- 🎯 `entity_accuracy_gold92` — Entity Accuracy (gold-92) · `accuracy`
- ✅ `intent_preservation_gold92` — Intent Preservation (gold-92) · `accuracy`
- ⚠️ `action_critical_wer_gold92` — Action-Critical WER (gold-92) · `ratio` (lower is better)
- 🚫 `wrong_action_rate_gold92` — Wrong Action Rate (gold-92) · `ratio` (lower is better)
- ⚡ `latency_p50_seconds` — Latency p50 (seconds) · `seconds` (lower is better)

Supporting:

- `wer_gold92` — Word Error Rate (gold-92) · `ratio` (lower is better)

## Task Types

**Project-specific** (added for this project):

- `audio-dataset-curation` — Audio Dataset Curation
- `stt-benchmark-run` — STT Benchmark Run
- `post-correction-experiment` — Post-Correction Experiment
- `whisper-finetuning-run` — Whisper Fine-Tuning Run

**Generic** (built-in ARF types):

- `answer-question`, `baseline-evaluation`, `brainstorming`, `build-model`, `code-reproduction`,
  `comparative-analysis`, `correction`, `data-analysis`, `deduplication`, `download-dataset`,
  `download-paper`, `experiment-run`, `feature-engineering`, `infrastructure-setup`,
  `internet-research`, `literature-survey`, `write-library`

## Budget and Services

Total budget: **$2 000 USD** · per-task default limit: $100 · Services: `anthropic_api`,
`openai_api`, `azure_ml`

## Documentation

- [`arf/docs/explanation/safety.md`](arf/docs/explanation/safety.md) — autonomy and safety risks
- [`arf/docs/tutorial/`](arf/docs/tutorial/) — five-page walkthrough from empty fork to first
  results
- [`arf/docs/reference/`](arf/docs/reference/) — glossary, task folder structure, verificators,
  aggregators, skills
- [`arf/styleguide/python_styleguide.md`](arf/styleguide/python_styleguide.md) — Python style guide
- [`arf/styleguide/markdown_styleguide.md`](arf/styleguide/markdown_styleguide.md) — Markdown style
  guide
- [`docs/dvc-data-workflow.md`](docs/dvc-data-workflow.md) — DVC setup and daily audio data workflow

## License

Apache License 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE) for details.
