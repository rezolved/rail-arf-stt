---
spec_version: "1"
task_id: "t0014_granite_short_clip_robustness"
updated_at: "2026-06-29T12:27:00Z"
completed_steps: 4
next_step_number: 5
next_step_id: "research-internet"
---
# Task Objective

Validate Granite Speech 4.1 2B robustness on short clips vs Parakeet via production streaming
simulation, and assess production fit as a Parakeet replacement in brainpowa.

* * *

## Step History

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

Step 4 (research-papers) completed successfully. The research corpus contained 19 relevant papers; 6
were cited in `research/research_papers.md`. The literature establishes that short clips (sub-6-word
commands) are the highest-risk failure zone for ASR models, with WildASR documenting 38–74% WER and
synthetic TTS underestimating failures by 5.9×. Whisper's VAD heuristics (`no_speech_threshold=0.6`,
temperature fallback) are the mechanistic cause of short-clip drop failures. For the internet
research step (step 5), focus on brainpowa streaming adapter integration details, Granite Speech 4.1
2B release notes and known short-clip behavior, and any production deployment documentation not
captured in the paper corpus.
