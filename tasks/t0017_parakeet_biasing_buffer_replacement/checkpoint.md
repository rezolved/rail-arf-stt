---
spec_version: "1"
task_id: "t0017_parakeet_biasing_buffer_replacement"
updated_at: "2026-07-02T12:00:00Z"
completed_steps: 14
next_step_number: null
next_step_id: null
---
# Task Objective

Biased head-to-head of parakeet-unified-en-0.6b vs prod parakeet-tdt-0.6b-v3 (EA/EA-DV, latency)
plus fine buffer sweep (200-1000ms) on the winner, to decide the brainpowa production Parakeet.

* * *

## Step History

### Step 1 — create-branch

Branch `task/t0017_parakeet_biasing_buffer_replacement` created; task folder initialized.

### Step 2 — check-deps

Confirmed `t0015_streaming_buffer_interval`, `t0012_whisper_parakeet_granite_streaming`, and
`t0009_parakeet_production_baseline` are completed.

### Step 3 — init-folders

Initialized the standard task folder structure (`code/`, `data/`, `results/`, `plan/`, `logs/`).

### Step 4 — research-papers

No new paper research performed — architecture questions already covered in t0012's literature
pass.

### Step 5 — research-internet

No new internet research performed — both candidate checkpoints already identified and reviewed in
t0015.

### Step 6 — research-code

No new code research performed — harness reused directly from t0015 (copied into `code/`, imports
repointed to t0017).

### Step 7 — planning

Planned a biased head-to-head sweep of `parakeet-tdt-0.6b-v3` vs `parakeet-unified-en-0.6b` on
gold-92 across an extended interval grid (200/300/350/500/750/1000ms), reusing t0015's harness
copied into `code/` with imports repointed to t0017.

### Step 8 — setup-machines

Reused the reserved Azure H100 NVL instance `llm-t1-nc80` from t0015; both checkpoints already
cached in the HF cache on that machine.

### Step 9 — implementation

Ran the biased buffer sweep for both models across all 6 intervals on gold-92 (93 clips). Mid-task,
found and fixed a bug in `expand_casing_variants()`: it only capitalized the first character of the
whole phrase (`phrase[:1].upper() + phrase[1:]`) instead of each word, so multi-word domain terms
never got a real title-case biasing variant. Fixed to `phrase.title()` in both this task's code and
the shared t0015 harness (`t0015_streaming_buffer_interval/code/ run_parakeet_buffer_sweep.py` and
`run_multitalker_buffer_sweep.py`). Reran the full sweep with the fix; conclusion (unified wins)
unchanged, numbers moved slightly (WER improved ~0.1-0.3pp for both models). t0015's own results
were not rerun.

### Step 11 — results

Computed metrics with `code/compute_and_write_metrics.py`, generated charts with
`code/make_charts.py`, and wrote `results/results_detailed.md` / `results/results_summary.md`
reflecting the post-fix numbers.

### Step 10 — teardown

`llm-t1-nc80` is a shared reserved instance kept alive across tasks per team policy — not torn
down.

### Step 12 — compare-literature

No new literature was reviewed for this task.

### Step 13 — suggestions

Wrote `results/suggestions.json`: audit other consumers of the same casing-expansion pattern for the
same bug; consider rerunning t0015 with the fix.

### Step 14 — reporting

Built `assets/predictions/{parakeet-tdt-buffer-sweep,parakeet-unified-buffer-sweep}/` and
`assets/answer/parakeet-unified-vs-tdt-production-fit/`, set `task.json` status to `completed`,
opened the PR.

* * *

## Cross-Step Decisions

- Reuse t0015's harness verbatim rather than reimplementing — keeps biasing config and streaming
  simulation identical for a fair head-to-head.
- The casing-variant bug fix is applied to both t0017 and t0015's code, but only t0017's results
  were regenerated. Rerunning t0015 is logged as a follow-on suggestion, not done in this task.
- `llm-t1-nc80` is a shared reserved GPU instance kept alive across tasks per team policy — no
  teardown step was run.

## Next Step Notes

Task complete. No further steps pending.
