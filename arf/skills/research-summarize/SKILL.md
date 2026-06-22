---
name: "research-summarize"
description: "Compress research files into a compact summary for downstream subagents. Run after all research steps complete, before planning."
---
# Research Summarize

**Version**: 2

## Goal

Read the research files produced by the research stage and write a compact
`tasks/$TASK_ID/research/research_summary.md` that planning and implementation agents can load
instead of the full research files.

## Inputs

* `$TASK_ID` — task ID

## Context

Read before starting:

* `tasks/$TASK_ID/research/research_papers.md` (if it exists — research-papers step is optional)
* `tasks/$TASK_ID/research/research_internet.md` (if it exists — research-internet step is optional)
* `tasks/$TASK_ID/research/research_code.md` (if it exists — research-code step is optional)
* `tasks/$TASK_ID/task.json` — to understand what the task needs

## Steps

1. Read all available research files, skipping any that do not exist. If none exist, write a
   minimal summary grounded solely in `task.json`.

2. Write `tasks/$TASK_ID/research/research_summary.md` with these sections:

   ```markdown
   # Research Summary — $TASK_ID

   ## Key Findings (top 10 insights directly actionable for this task)

   1. ...
   2. ...

   ## Best Approaches (top 3 recommended implementation approaches from research)

   ### Approach 1: <name>
   <2-3 sentences>

   ### Approach 2: <name>
   <2-3 sentences>

   ### Approach 3: <name>
   <2-3 sentences>

   ## Reusable Code / Assets
   (file paths and one-line descriptions of relevant prior-task code)

   ## Key Papers (top 5, with finding most relevant to this task)

   * **<Author Year>** — <one-sentence relevant finding>

   ## Risks Flagged in Research

   * ...

   ## Full Detail Available In
   * `tasks/$TASK_ID/research/research_papers.md` — <N> papers
   * `tasks/$TASK_ID/research/research_internet.md` — <N> sources
   * `tasks/$TASK_ID/research/research_code.md` — <N> code references
   ```

   For each research file that was not generated (step was skipped), write
   "(not generated — step skipped)" instead of a source count.

3. Keep the summary under 200 lines / 8 KB. If you cannot fit critical information, prefer
   specificity over breadth — include the most actionable findings and omit peripheral detail.

## Done When

* `tasks/$TASK_ID/research/research_summary.md` exists.
* File is under 200 lines and 8 KB.
* All mandatory sections are present.

## Forbidden

* NEVER copy large blocks from research files verbatim. Compress and synthesize.
* NEVER omit the "Full Detail Available In" section — downstream agents use it to decide which
  research files to read. For files not generated (step skipped), write "(not generated — step
  skipped)" instead of a source count.
* NEVER commit. The orchestrator owns commits.
