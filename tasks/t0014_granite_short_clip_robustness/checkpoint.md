---
spec_version: "1"
task_id: "t0014_granite_short_clip_robustness"
updated_at: "2026-06-29T12:55:00Z"
completed_steps: 5
next_step_number: 6
next_step_id: "research-code"
---
# Task Objective

Validate Granite Speech 4.1 2B robustness on short clips vs Parakeet via production streaming
simulation, and assess production fit as a Parakeet replacement in brainpowa.

* * *

## Step History

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

For the research-code step (step 6), focus on reviewing t0012 code and predictions (the streaming
harness and Granite/Parakeet inference scripts), t0009 baselines (entity accuracy evaluation code),
t0011 streaming harness implementation, and the brainpowa STTAdapter interface in the production
codebase. Key questions: does the existing streaming harness already handle sub-2 s clip injection,
what metrics/utilities can be reused, and does the brainpowa ParakeetSTT adapter override
`chunk_secs` from NeMo's default of 2 s. Three add-paper subagents (Baranski2025, Wang2025,
Saon2025) are running in parallel and must complete before compare-literature and reporting steps.
