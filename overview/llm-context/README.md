# LLM Context Archives

Generated XML archives for pasting into ChatGPT, Gemini, Claude, and similar tools.

## Preset Archives

Curated presets that mix content from multiple aggregator types for specific use cases.

| Preset | Tokens | Best For |
|---|---:|---|
| [`project-overview`](project-overview.xml) | 3K | General orientation, quick status questions, and lightweight strategy chats. |
| [`full`](full.xml) | 33K | Deep project review, comprehensive planning, and long-context synthesis. |
| [`research-history`](research-history.xml) | 45K | Literature review continuity, methodology discussion, and prior-investigation lookup. |
| [`results-deep-dive`](results-deep-dive.xml) | 23K | Performance analysis, experiment comparison, and result interpretation. |
| [`roadmap`](roadmap.xml) | 14K | Deciding what to do next, prioritizing experiments, and planning follow-up work. |
| [`literature-and-assets`](literature-and-assets.xml) | 8K | Method discussion, resource selection, and related-work chats. |
| [`qa`](qa.xml) | 3K | Answer review, follow-up questioning, and project knowledge-base chats. |
| [`project-memory`](project-memory.xml) | 13K | Keeping a durable project memory in medium-size chat sessions. |

## Per-Type Archives

One file per aggregator type with complete untruncated data.

| Type | Tokens | Description |
|---|---:|---|
| [`tasks`](type-tasks.xml) | 26K | Complete task data with full descriptions, results summaries, dependencies, and status. |
| [`papers`](type-papers.xml) | 51K | Complete paper corpus with full summaries, metadata, and abstracts. |
| [`datasets`](type-datasets.xml) | 2K | Complete dataset inventory with full descriptions, access info, and sizes. |
| [`suggestions`](type-suggestions.xml) | 7K | Complete suggestion list with full descriptions, priority, and status. |
| [`predictions`](type-predictions.xml) | 13K | Complete predictions inventory with full descriptions, metrics, and model references. |
| [`metrics`](type-metrics.xml) | 868 | Complete metric definitions with full descriptions, units, and associated datasets. |
| [`categories`](type-categories.xml) | 1K | Complete category definitions with full detailed descriptions. |
| [`task-types`](type-task-types.xml) | 24K | Complete task type definitions with descriptions and instructions. |
| [`costs`](type-costs.xml) | 325 | Complete cost breakdown with budget, per-service, and per-task details. |

## Context Windows

* `131k-class` — up to 131,072 estimated tokens
* `200k-class` — up to 200,000 estimated tokens
* `1M-class` — up to 1,000,000 estimated tokens

Token counts are approximate and use the shared rule `1 token ~= 4 chars`.

## Project Overview

Compact starter context for general project chats.

* Preset id: `project-overview`
* Short label: `overview` (3K)
* Best for: General orientation, quick status questions, and lightweight strategy chats.
* File: [`project-overview.xml`](project-overview.xml)
* Size: 12.8 KiB (13,077 bytes; 13,012 chars)
* Estimated tokens: 3,253
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with short-answer coverage only. |

## Full Project Context

Largest preset with detailed completed-task reports and the full project knowledge base.

* Preset id: `full`
* Short label: `full` (33K)
* Best for: Deep project review, comprehensive planning, and long-context synthesis.
* File: [`full.xml`](full.xml)
* Size: 131.6 KiB (134,752 bytes; 133,989 chars)
* Estimated tokens: 33,497
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Detailed results | Every available completed-task `results/results_detailed.md` file in full. |
| Planned tasks | All planned or active tasks with status, date, dependencies, short descriptions, and full long descriptions. |
| Questions and answers | All questions with full-answer bodies when available. |
| Papers | All papers with metadata and summary excerpts from paper summaries, full summaries, or abstracts. |
| Datasets | All datasets with access, size, source task, and description excerpts. |
| Libraries | All libraries with module paths, source task, and description excerpts. |
| Metrics | All registered metrics with units, value types, and description excerpts. |

## Research History

Research-stage documents across completed tasks, plus core project context.

* Preset id: `research-history`
* Short label: `research` (45K)
* Best for: Literature review continuity, methodology discussion, and prior-investigation
  lookup.
* File: [`research-history.xml`](research-history.xml)
* Size: 176.9 KiB (181,166 bytes; 180,521 chars)
* Estimated tokens: 45,130
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with short-answer coverage only. |
| Research documents | All available completed-task `research_papers.md`, `research_internet.md`, and `research_code.md` files in full. |

## Results Deep Dive

Completed-task result summaries plus all detailed results reports.

* Preset id: `results-deep-dive`
* Short label: `results` (23K)
* Best for: Performance analysis, experiment comparison, and result interpretation.
* File: [`results-deep-dive.xml`](results-deep-dive.xml)
* Size: 91.8 KiB (93,952 bytes; 93,395 chars)
* Estimated tokens: 23,348
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Detailed results | Every available completed-task `results/results_detailed.md` file in full. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with short-answer coverage only. |

## Roadmap

Project planning preset centered on upcoming tasks and open suggestions.

* Preset id: `roadmap`
* Short label: `roadmap` (14K)
* Best for: Deciding what to do next, prioritizing experiments, and planning follow-up work.
* File: [`roadmap.xml`](roadmap.xml)
* Size: 55.8 KiB (57,184 bytes; 56,912 chars)
* Estimated tokens: 14,228
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, short descriptions, and full long descriptions. |
| Questions and answers | All questions with short-answer coverage only. |
| Suggestions | All open suggestions with priority, kind, source task, and description excerpts. |

## Literature and Assets

Paper summaries and reusable project assets without the heaviest task reports.

* Preset id: `literature-and-assets`
* Short label: `assets` (8K)
* Best for: Method discussion, resource selection, and related-work chats.
* File: [`literature-and-assets.xml`](literature-and-assets.xml)
* Size: 32.6 KiB (33,414 bytes; 33,322 chars)
* Estimated tokens: 8,330
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with short-answer coverage only. |
| Papers | All papers with metadata and summary excerpts from paper summaries, full summaries, or abstracts. |
| Datasets | All datasets with access, size, source task, and description excerpts. |
| Libraries | All libraries with module paths, source task, and description excerpts. |
| Metrics | All registered metrics with units, value types, and description excerpts. |

## Questions and Answers

Question-centric preset with the full answer corpus and compact project state.

* Preset id: `qa`
* Short label: `qa` (3K)
* Best for: Answer review, follow-up questioning, and project knowledge-base chats.
* File: [`qa.xml`](qa.xml)
* Size: 12.8 KiB (13,077 bytes; 13,012 chars)
* Estimated tokens: 3,253
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with full-answer bodies when available. |

## Project Memory

Mid-size preset intended as a reusable working memory for ongoing chats.

* Preset id: `project-memory`
* Short label: `memory` (13K)
* Best for: Keeping a durable project memory in medium-size chat sessions.
* File: [`project-memory.xml`](project-memory.xml)
* Size: 49.3 KiB (50,460 bytes; 50,348 chars)
* Estimated tokens: 12,587
* Fits: 131k-class, 200k-class, 1M-class

### Included Types

| Included Type | Coverage |
|---|---|
| Project description | Full `project/description.md`. |
| Completed tasks | All completed tasks with `results_summary` excerpts and short descriptions. |
| Planned tasks | All planned or active tasks with status, date, dependencies, and short descriptions. |
| Questions and answers | All questions with short-answer coverage only. |
| Papers | The 20 most recent papers with metadata and summary excerpts. |
| Datasets | All datasets with access, size, source task, and description excerpts. |
| Libraries | All libraries with module paths, source task, and description excerpts. |
| Metrics | All registered metrics with units, value types, and description excerpts. |
| Suggestions | The top 20 open suggestions ordered by priority and date. |

## Per-Type Archive Details

### All Tasks

Complete task data with full descriptions, results summaries, dependencies, and status.

* Type id: `tasks`
* File: [`type-tasks.xml`](type-tasks.xml)
* Size: 101.6 KiB (104,023 bytes; 103,347 chars)
* Estimated tokens: 25,836
* Fits: 131k-class, 200k-class, 1M-class

### All Papers

Complete paper corpus with full summaries, metadata, and abstracts.

* Type id: `papers`
* File: [`type-papers.xml`](type-papers.xml)
* Size: 200.5 KiB (205,335 bytes; 204,288 chars)
* Estimated tokens: 51,072
* Fits: 131k-class, 200k-class, 1M-class

### All Datasets

Complete dataset inventory with full descriptions, access info, and sizes.

* Type id: `datasets`
* File: [`type-datasets.xml`](type-datasets.xml)
* Size: 7.3 KiB (7,506 bytes; 7,478 chars)
* Estimated tokens: 1,869
* Fits: 131k-class, 200k-class, 1M-class

### All Suggestions

Complete suggestion list with full descriptions, priority, and status.

* Type id: `suggestions`
* File: [`type-suggestions.xml`](type-suggestions.xml)
* Size: 26.3 KiB (26,938 bytes; 26,910 chars)
* Estimated tokens: 6,727
* Fits: 131k-class, 200k-class, 1M-class

### All Predictions

Complete predictions inventory with full descriptions, metrics, and model references.

* Type id: `predictions`
* File: [`type-predictions.xml`](type-predictions.xml)
* Size: 51.9 KiB (53,105 bytes; 52,947 chars)
* Estimated tokens: 13,236
* Fits: 131k-class, 200k-class, 1M-class

### All Metrics

Complete metric definitions with full descriptions, units, and associated datasets.

* Type id: `metrics`
* File: [`type-metrics.xml`](type-metrics.xml)
* Size: 3.4 KiB (3,477 bytes; 3,475 chars)
* Estimated tokens: 868
* Fits: 131k-class, 200k-class, 1M-class

### All Categories

Complete category definitions with full detailed descriptions.

* Type id: `categories`
* File: [`type-categories.xml`](type-categories.xml)
* Size: 4.7 KiB (4,775 bytes; 4,769 chars)
* Estimated tokens: 1,192
* Fits: 131k-class, 200k-class, 1M-class

### All Task Types

Complete task type definitions with descriptions and instructions.

* Type id: `task-types`
* File: [`type-task-types.xml`](type-task-types.xml)
* Size: 95.8 KiB (98,048 bytes; 97,926 chars)
* Estimated tokens: 24,481
* Fits: 131k-class, 200k-class, 1M-class

### Project Costs

Complete cost breakdown with budget, per-service, and per-task details.

* Type id: `costs`
* File: [`type-costs.xml`](type-costs.xml)
* Size: 1.3 KiB (1,300 bytes; 1,300 chars)
* Estimated tokens: 325
* Fits: 131k-class, 200k-class, 1M-class
