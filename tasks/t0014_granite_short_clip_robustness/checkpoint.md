---
spec_version: "1"
task_id: "t0014_granite_short_clip_robustness"
updated_at: "2026-06-30T07:55:00Z"
completed_steps: 13
next_step_number: 14
next_step_id: "suggestions"
---
# Task Objective

Validate Granite Speech 4.1 2B robustness on short clips vs Parakeet via production streaming
simulation, and assess production fit as a Parakeet replacement in brainpowa.

* * *

## Step History

### Step 12 — results

Wrote `results_summary.md` and `results_detailed.md` with all mandatory sections, 12 concrete
examples from prediction JSONLs (with fenced code blocks showing raw JSON outputs), and full REQ-1
through REQ-13 coverage. Key finding confirmed: Granite 0% empty rate vs Parakeet 27.3% on short
clips; Granite 94.8% EA vs Parakeet 65.0% on gold-92. `verify_task_results` passed 0 errors, 0
warnings. RM-E001 documented in Limitations (reserved instance not destroyed, expected).

### Step 10 — teardown

Reserved Azure H100 NVL machine (`llm-t1-nc80`) was NOT destroyed — shared reserved instance. All
results already synced locally during implementation. Cost is $0 (no per-minute billing). Key
outputs: `results/costs.json` ($0), `results/remote_machines_used.json` (1 entry),
`machine_log.json` updated with `total_cost_usd: 0.0` and reserved-instance note.

### Step 9 — implementation

All 4 milestones completed on Azure H100 NVL (`azureuser@llm-t1-nc80`): 44 synthetic short clips
synthesized across 6 duration bins (0.5–3.0 s), 3 models benchmarked via
`STTAdapter.transcribe_stream()` simulation, stratified analysis with BCa bootstrap CIs computed,
and answer + prediction assets created. Key finding: Granite 0% empty rate vs Parakeet 27.3% on
short clips; Granite superior entity accuracy on gold-92 (94.8% vs Parakeet 65.0%). Key outputs:
`results/stratified_analysis.json`, `results/metrics.json`, `results/images/` (3 charts),
`assets/answer/granite-vs-parakeet-production-fit/`, and 3 prediction assets.

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

Step 14 is `suggestions`. Run `prestep t0014_granite_short_clip_robustness suggestions`, then invoke
the `/generate-suggestions` skill to create `results/suggestions.json`. Key inputs for the
suggestions agent: Granite 0% empty rate vs Parakeet 27.3%, CONDITIONAL YES production
recommendation with 2.0 s minimum clip gate, 6× latency premium (251 ms vs 41 ms), RM-E001 noted.
The suggestions agent should look at existing suggestions to avoid duplicates, and prioritize
actionable follow-up tasks for the brainpowa integration (e.g., implementing `granite.py`
STTAdapter, setting up minimum clip gate in production, measuring latency impact in end-to-end
streaming tests).
