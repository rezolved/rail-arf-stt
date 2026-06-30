---
spec_version: "1"
task_id: "t0014_granite_short_clip_robustness"
updated_at: "2026-06-30T00:00:00Z"
completed_steps: 8
next_step_number: 9
next_step_id: "implementation"
---
# Task Objective

Validate Granite Speech 4.1 2B robustness on short clips vs Parakeet via production streaming
simulation, and assess production fit as a Parakeet replacement in brainpowa.

* * *

## Step History

### Step 8 — setup-machines

Azure H100 NVL machine (`azureuser@llm-t1-nc80`) verified live: 2x H100 NVL GPUs confirmed via
`nvidia-smi`, conda env `stt` with NeMo 3.1.0 active, Granite model at
`/home/azureuser/granite-model/granite-speech-4.1-2b`, Parakeet from HuggingFace cache, Whisper
available. Step was recovered from a stuck `in_progress` state — machine was already provisioned
when recovery ran. Key output: `logs/steps/008_setup-machines/machine_log.json`.

### Step 13 — compare-literature

Skipped: researcher requested fast path to experiment; literature comparison deferred to after
implementation results are available.

### Step 11 — creative-thinking

Skipped: researcher requested fast path to experiment; no creative analysis needed at this stage.

### Step 7 — planning

Plan specifies a four-milestone GPU experiment on Azure H100 NVL: (1) synthesize 40-60 short clips
at 6 duration bins (0.5-3 s) from gold-92 audio, (2) run all 3 models via
`STTAdapter.transcribe_stream()` with 32kB PCM-16 chunk queues, (3) compute stratified `empty_rate`,
`hallucination_rate`, WER, EA, and latency across 6 duration strata with BCa bootstrap CIs, (4)
produce answer asset with explicit YES/NO/CONDITIONAL recommendation on Granite replacing Parakeet.
Verificator passed 0 errors, 0 warnings.

### Step 6 — research-code

Skipped: researcher requested fast path to experiment; t0012 streaming harness and brainpowa
STTAdapter already reviewed in t0013 brainstorm session context.

### Step 5 — research-internet

Conducted 12 web searches across arXiv, GitHub, and official IBM/NVIDIA docs; 3 new papers
discovered (Baranski2025 Whisper BoH, Wang2025 Calm-Whisper, Saon2025 Granite-speech architecture)
and add-paper subagents launched in parallel. Key findings: Granite 4.1 2B uses a 4-second
block-attention window (so sub-4 s clips process in one Conformer pass with expected empty-output
failure mode, not hallucination), Parakeet default `chunk_secs=2` means all sub-2 s bins are
degenerate single-chunk cases, and brainpowa-realtime-api has no public docs (must be assessed from
source). Output: `research/research_internet.md` (verificator passed 0 errors, 0 warnings).

### Step 4 — research-papers

Reviewed 19 papers across stt-evaluation, latency-profiling, and audio-datasets categories; 6 cited
in `research/research_papers.md`. Key finding: short utterances are the primary failure zone (WER
38–74% on sub-6-word commands per WildASR), Whisper VAD heuristics (`no_speech_threshold=0.6`) are
the mechanistic cause of short-clip failures, and hallucination rate must be tracked separately from
empty-output rate. Verificator passed with zero errors.

### Step 3 — init-folders

Standard task folder structure created (plan/, research/, results/, results/images/, corrections/,
intervention/, code/, logs/ subdirs, assets/answer/, assets/predictions/). Key output:
`logs/steps/003_init-folders/folders_created.txt`. Aggregator cache populated in ctx/ (task_types,
costs, tasks, metrics, suggestions).

### Step 2 — check-deps

Both dependencies (`t0013_brainstorm_results_1` and `t0012_whisper_parakeet_granite_streaming`) are
`completed` and satisfied. Key output: `logs/steps/002_check-deps/deps_report.json` (0 errors, 0
warnings).

### Step 1 — create-branch

Branch `task/t0014_granite_short_clip_robustness` created from main (9f4d798). Worktree at
`rail-arf-stt-worktrees/t0014_granite_short_clip_robustness`. `step_tracker.json` written with 15
steps (all required + 8 optional per union of stt-benchmark-run / experiment-run / answer-question
task types). Step 1 is a mechanical setup step with no research output.

* * *

## Cross-Step Decisions

* * *

## Next Step Notes

For implementation (step 9): the GPU machine is confirmed live at `azureuser@llm-t1-nc80` with 2x
H100 NVL, conda env `stt`, NeMo 3.1.0, Parakeet from HuggingFace cache, Granite at
`/home/azureuser/granite-model/granite-speech-4.1-2b`, and Whisper available. Read
`tasks/t0014_granite_short_clip_robustness/plan/plan.md` in full before starting — the plan covers
four milestones: dataset synthesis (Milestone 1, CPU), GPU inference for all three models (Milestone
2), stratified analysis (Milestone 3), and answer asset (Milestone 4). Run `dvc pull` on the remote
machine first to ensure gold-92 WAV files are present. All inference MUST use
`STTAdapter.transcribe_stream()` — not direct model calls. Machine lock file at
`~/.arf-locks/t0014_granite_short_clip_robustness.lock` should be written before starting work.
