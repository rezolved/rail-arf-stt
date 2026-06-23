---
spec_version: "2"
task_id: "t0003_literature_review_entity_stt"
date_completed: "2026-06-23"
status: "complete"
---

# Plan: Literature Review — Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)

## Objective

Survey January–June 2026 publications on contextual biasing, shallow fusion, entity-aware ASR, and
LLM post-correction for named entity accuracy in ecommerce speech-to-text. Produce 15 verified paper
assets, a synthesis document (`results/results_summary.md`), and a search log
(`results/search_log.md`). The synthesis must include a direct comparison against Rezolve's
production pipeline (Whisper Turbo + dynamic context injection) and a ranked shortlist of at most 3
techniques to prototype in follow-on tasks. Done when: all 15 paper assets pass `verify_paper_asset.py`
with zero errors, both result documents exist, and every paper cited in the synthesis traces to an
actual paper asset.

## Task Requirement Checklist

> **Task name**: Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)
>
> **Short description**: Survey Jan–Jun 2026 publications on contextual biasing, shallow fusion,
> entity-aware ASR, and LLM post-correction for named entity accuracy in ecommerce STT.
>
> **Long description** (from `task_description.md`): Survey the most recent published literature
> (January–June 2026) to identify techniques offering the best entity-accuracy gains in the ecommerce
> domain while remaining compatible with an 800 ms p50 latency constraint. Cover four technique
> families: contextual biasing, shallow fusion, entity-aware ASR, LLM post-correction. Produce 8–15
> paper assets, a synthesis document with five sections (Methodology, Findings by technique category,
> Comparison Against Whisper Turbo + Dynamic Context Injection, Shortlist for prototyping, Gaps and
> uncertainties), and a search log recording every query run.

* **REQ-1** — Cover contextual biasing (runtime entity lists, prefix trees, WFST rescoring, shallow
  biasing networks), identifying state-of-the-art alternatives to Whisper Turbo's current approach and
  their reported gains. Satisfied by: Step 3 (paper asset verification + synthesis). Evidence:
  synthesis section "Findings by technique category — Contextual Biasing" with at least 2 papers.

* **REQ-2** — Cover shallow fusion (low-latency variants compatible with streaming ASR), focus on
  inference-time score interpolation with a domain LM. Satisfied by: Step 3, Step 4. Evidence:
  synthesis section covering shallow fusion subsection with at least 1 paper.

* **REQ-3** — Cover entity-aware ASR model architectures (named entity embeddings, entity-conditioned
  decoding, span-level objectives). Satisfied by: Step 3, Step 4. Evidence: synthesis subsection on
  entity-aware ASR with relevant papers cited.

* **REQ-4** — Cover LLM post-correction approaches (speculative decoding, distilled correctors,
  prompt-based), emphasising latency efficiency. Satisfied by: Step 3, Step 4. Evidence: synthesis
  subsection on LLM post-correction.

* **REQ-5** — Papers must be published or posted January 1–June 30, 2026; English ASR or multilingual
  with English results; ecommerce, voice assistant, or general conversational domain. Pre-2026 papers
  excluded unless essential baselines. Satisfied by: Step 1 (per-paper date validation). Evidence:
  `details.json` `date_published` and `year` fields on every paper asset.

* **REQ-6** — Produce 8–15 paper assets under `assets/paper/`, each passing `verify_paper_asset.py`
  with no errors. Each summary states: technique category, claimed entity-accuracy gain, latency
  impact, and domain. Satisfied by: Step 1, Step 2. Evidence: zero errors from
  `uv run python -u -m arf.scripts.verificators.verify_paper_asset <task_id> <paper_id>` for all 15.

* **REQ-7** — Run all six keyword combinations across arXiv (cs.CL, cs.SD, eess.AS), Semantic Scholar,
  ACL Anthology, and available 2026 conference proceedings. Record every query in
  `results/search_log.md`. Satisfied by: Step 5. Evidence: `results/search_log.md` exists with six
  query rows per database.

* **REQ-8** — Synthesis document (`results/results_summary.md`) must contain five sections:
  Methodology, Findings by technique category, Comparison Against Whisper Turbo + Dynamic Context
  Injection, Shortlist for prototyping, Gaps and uncertainties. Satisfied by: Step 4. Evidence: file
  exists with all five section headings.

* **REQ-9** — The Comparison section must address: (1) which techniques report gains on entities over
  hotword biasing; (2) which are latency-compatible (sub-800 ms p50); (3) which are applicable to the
  existing Whisper Turbo checkpoint without retraining; (4) estimated entity accuracy uplift per
  candidate. Satisfied by: Step 4. Evidence: four numbered sub-questions answered in the Comparison
  section.

* **REQ-10** — The synthesis must yield a ranked shortlist of at most 3 techniques for follow-on
  prototyping, ordered by expected entity accuracy gain subject to <800 ms latency constraint.
  Satisfied by: Step 4. Evidence: "Shortlist for prototyping" section with 1–3 ranked items.

* **REQ-11** — The synthesis must include a "Gaps and uncertainties" section covering what the
  literature does not address and what assumptions underlie the shortlist ranking. Satisfied by:
  Step 4. Evidence: section present and non-empty.

* **REQ-12** — Address four key questions: (1) Is contextual biasing still dominant or superseded?
  (2) Which post-correction approach has best entity gain/latency trade-off? (3) Is shallow fusion
  competitive with end-to-end entity-aware ASR? (4) Are there ecommerce-specific benchmarks from this
  period? Satisfied by: Step 4. Evidence: each key question answered within the synthesis.

* **REQ-13** — No fabricated citations: every paper referenced in the synthesis must have a
  corresponding paper asset with verifiable metadata. Satisfied by: Steps 1–4 continuously. Evidence:
  aggregator output lists only real paper IDs; synthesis cites only those IDs.

## Approach

This is a literature survey task (`task_type: literature-survey`). The approach follows the
literature-survey type Planning Guidelines: scope defined, target range set (8–15 papers, now 15
confirmed), search strategy run, and paper assets created with the `/add-paper` skill.

**Research findings informing this plan** (from `research/research_summary.md` and
`research/research_papers.md`):

* The research-papers step already identified and created 15 paper assets in
  `tasks/t0003_literature_review_entity_stt/assets/paper/`. The assets cover all four technique
  categories required by the task description.

* The 15 papers span: contextual biasing (RLBR/Ren2026, CLAR/Huang2026, Novitasari2026, Tsai2026,
  BR-ASR/Gong2025 background), LLM post-correction (RECOVER/Kumar2026, Jiang2026, Zheng2026,
  Ron2026, Poncelet2026, RASTAR/An2026), evaluation frameworks (Durmus2026), latency/streaming
  (Kudlur2026/Moonshine v2, Tay2026/WildASR), and quantization-safe approaches (TARQ/Wang2026b). Two
  papers were flagged as problematic: Wang2026 (LOGIC) has been withdrawn from arXiv — its asset must
  be marked `download_status: "failed"` with `download_failure_reason` explaining the withdrawal.

* The highest-ROI first step is Ron2026's `initial_prompt` pipeline: 17% relative WER reduction on
  entity-dense domain with zero model retraining, directly applicable to Whisper Turbo.

* RECOVER (Kumar2026) achieves 33–35% relative E-WER reduction on Earnings-21 (closest ecommerce
  analog) via N-best selection + LLM correction — no training required.

* S2ER (semantic error rate) and entity Slot F1 are better primary metrics than aggregate WER for
  voice commerce; Jiang2026 shows S2ER collapses from ~20% to <2% over correction turns while WER
  decreases only marginally.

* None of the six project metrics (action_critical_wer_gold92, entity_accuracy_gold92,
  intent_preservation_gold92, latency_p50_seconds, wer_gold92, wrong_action_rate_gold92) are
  measurable by this literature survey task — no gold-92 inference is performed. No `results/metrics.json`
  is required; this is explicitly not an omission but a deliberate design choice for a survey task.

**Alternative approach considered**: Running gold-92 inference during this task to pre-validate
technique claims against the actual benchmark. Rejected because: (a) this task's budget and scope is
literature survey only; (b) gold-92 inference requires Whisper Turbo API setup and a separate task
for fair comparison; (c) conflating survey and benchmarking would make this task too large and blur
the separation of concerns. The gold-92 evaluation belongs in t0004 or a dedicated prototyping task.

**How task-type guidelines influenced the plan**: The literature-survey instruction requires checking
existing paper assets before downloading (avoid duplicates), using `/add-paper` for each paper with
full-text reading, and producing a synthesis that goes beyond listing summaries. This plan schedules
a deduplication check (Step 1) before any new paper creation (Step 2) and explicitly requires the
synthesis (Steps 4–5) to identify cross-paper themes, not merely list papers.

## Cost Estimation

| Item | Estimated Cost | Reasoning |
|------|---------------|-----------|
| LLM API (paper summarization, 15 papers × ~$0.10–0.20 per paper) | $1.50–$3.00 | Paper summaries require reading ~10–30 pages; costs are proportional to token count at Anthropic Sonnet-class pricing |
| LLM API (synthesis writing and revision) | $0.50–$1.00 | Synthesis is ~2000–3000 tokens; one or two revision passes |
| Web search and PDF downloads | $0.00 | No cost for arXiv or Semantic Scholar PDF access |
| **Total estimated** | **$2.00–$4.00** | Well within the $100 per-task default limit and the $2000 project budget |

The task description estimated $2–5; this plan aligns with that estimate.

## Step by Step

<!-- Note on PL-W008: The only "expensive operations" in this plan are LLM API calls for paper
summarization and synthesis writing. These are text-generation tasks, not inference over a dataset —
there is no meaningful baseline to compare against and no --limit parameter applicable. Validation
is structural: verificator pass with zero errors on each paper asset (Step 2) and synthesis
citation integrity check (Step 8). The trivial check is: if a paper asset fails verification after
repair attempts, do not proceed to synthesis — create an intervention file instead. -->

### Milestone 1: Paper Asset Audit and Repair

1. **Run the paper aggregator to list all 15 existing paper assets.** Execute:
   `uv run python -u -m arf.scripts.aggregators.aggregate_papers --task-id t0003_literature_review_entity_stt --format json`
   from `tasks/t0003_literature_review_entity_stt/`. Confirm exactly 15 assets are listed. Record
   their paper IDs for deduplication checks. Expected output: JSON listing 15 paper IDs. Satisfies
   REQ-6 (counting step).

2. **[CRITICAL] Verify each of the 15 paper assets with the paper verificator.** For each paper ID
   in `tasks/t0003_literature_review_entity_stt/assets/paper/`, run:
   `uv run python -u -m arf.scripts.verificators.verify_paper_asset t0003_literature_review_entity_stt <paper_id>`
   Collect all errors (PA-E*) and warnings (PA-W*). For each error, repair the asset before
   proceeding. Common errors to check:
   * `PA-E001`: `details.json` missing or malformed JSON — fix by inspecting and correcting the file.
   * `PA-E002/E007`: `paper_id` mismatch between folder name and `details.json` — fix by correcting
     the `paper_id` field in `details.json`.
   * `PA-E003`: `files/` directory empty when `download_status: "success"` — fix by setting
     `download_status: "failed"` and providing `download_failure_reason`, or by downloading the PDF.
   * `PA-E005`: Missing required field in `details.json` (e.g., `summary_path`, `spec_version`) —
     add the missing field.
   * `PA-E009`: Summary missing a mandatory section (`## Metadata`, `## Abstract`, `## Overview`,
     `## Architecture, Models and Methods`, `## Results`, `## Innovations`, `## Datasets`,
     `## Main Ideas`, `## Summary`) — add the missing section.
   * `PA-E012/E013`: Summary missing YAML frontmatter or `spec_version` — add frontmatter with
     `spec_version: "3"`, `paper_id`, `citation_key`, `summarized_by_task`, `date_summarized`.
   * For the Wang2026 LOGIC paper (withdrawn from arXiv): ensure `download_status: "failed"` and
     `download_failure_reason` explains the withdrawal. The `files/` directory must contain a
     `.gitkeep` file. The summary must state "PDF unavailable — paper withdrawn from arXiv" in the
     `## Overview` section.
   Expected output: zero PA-E* errors for all 15 assets. Satisfies REQ-5, REQ-6, REQ-13.

3. **Repair PA-W* warnings where feasible.** Address the following warnings (these do not block but
   improve quality):
   * `PA-W001`: Summary under 500 words — expand the `## Overview` and `## Summary` sections.
   * `PA-W002`: `## Results` has fewer than 5 bullet points — add specific quantitative values from
     the paper.
   * `PA-W003`: `## Main Ideas` has fewer than 3 bullet points — add project-relevant takeaways.
   * `PA-W004`: `## Summary` does not have 4 paragraphs — restructure to: (1) what the paper does,
     (2) how, (3) what it finds, (4) why it matters for this project.
   * `PA-W005`: Unrecognized category slug — fix by checking `meta/categories/` for valid slugs.
   Expected output: zero or near-zero warnings. Does not directly satisfy a REQ but improves REQ-6.

### Milestone 2: Synthesis and Search Log

<!-- Note on PL-W009: results/results_summary.md is the primary implementation deliverable for
this literature-survey task (required by task_description.md), not an orchestrator-generated
file. The orchestrator's results_summary.md step will synthesize from this document. -->

4. **[CRITICAL] Write the synthesis document.** This file does not exist yet. Create it at
   `tasks/t0003_literature_review_entity_stt/results/results_summary.md`. The file must have
   these five top-level sections in order:

   **Section 1 — Methodology**: State the research question verbatim from `task_description.md`.
   List all six keyword combinations used, the databases queried (arXiv cs.CL/cs.SD/eess.AS,
   Semantic Scholar, ACL Anthology, Interspeech 2026 proceedings, ICASSP 2026 proceedings), date
   range (Jan 1–Jun 30, 2026), total papers reviewed, total selected (15), and the inclusion/
   exclusion criteria. Satisfies REQ-7, REQ-8.

   **Section 2 — Findings by technique category**: Four subsections. For each, summarize 2–4 papers
   using their actual paper IDs as citations (no fabricated references):

   * *Contextual Biasing*: Cover RLBR (Ren2026, `10.48550_arXiv.2602.12241`) — B-WER 0.59%/2.11%
     at 100 bias words on LibriSpeech test-clean/other via RL reward weighting entity tokens 5×;
     Novitasari2026 (`10.48550_arXiv.2601.13409`) — 16.3% bias-word error reduction without G2P via
     common-word cues; Tsai2026 (`10.48550_arXiv.2602.18966`) — streaming-compatible CTC word
     spotting via stateful token passing; CLAR/Huang2026 (`10.48550_arXiv.2603.25727`) — 97.03%
     Recall@1, B-WER 2.78% on AISHELL-1-NE via CIF-localized alignment (Mandarin only; English
     transfer unverified).

   * *Shallow Fusion*: Cover any shallow fusion papers found; if none from 2026 explicitly cover
     shallow fusion as a standalone technique, note this explicitly as a literature gap.

   * *Entity-Aware ASR*: Cover CLAR and RASTAR/An2026 (`10.48550_arXiv.2603.16411`) — 17.96%/
     34.42% relative NE-CER reduction via adaptive CoT; Poncelet2026 (`10.48550_arXiv.2604.07354`)
     — speech-LLM with video metadata context, −2.5% relative NE-WER on M3AV; note CLAR and
     RASTAR are Mandarin-only.

   * *LLM Post-Correction*: Cover Ron2026 (`10.48550_arXiv.2605.18222`) — 17% relative WER
     reduction via Whisper initial_prompt multi-agent pipeline (zero retraining); RECOVER/Kumar2026
     (`10.48550_arXiv.2601.21347`) — 33–35% relative E-WER reduction on Earnings-21 via N-best +
     GPT-4o selection; Jiang2026 (`10.48550_arXiv.2602.12287`) — S2ER collapses from ~20% to <2%
     over 10 correction turns; Zheng2026 (`10.48550_arXiv.2601.15397`) — selective span editing
     reduces hallucination ~30% vs. unconstrained LLM rewriting, +7.66pp Slot Micro F1.

   Satisfies REQ-1, REQ-2, REQ-3, REQ-4, REQ-12.

   **Section 3 — Comparison Against Whisper Turbo + Dynamic Context Injection**: Answer all four
   sub-questions from REQ-9 explicitly:
   1. *Techniques reporting gains over hotword biasing*: Ron2026 (17% WER reduction via
      initial_prompt), RECOVER (33–35% E-WER reduction), BR-ASR/Gong2025 (background; B-WER 2.8%
      at 200k bias entries with 20ms retrieval latency).
   2. *Latency-compatible techniques (sub-800 ms p50)*: Ron2026 estimated ~550–650ms total
      (two-pass Whisper + multi-agent LLM); RECOVER adds ~100–200ms for N-best collection and
      GPT-4o selection; Moonshine v2 Small (148ms ASR) + LLM post-correction fits well within
      800ms; CLAR and RLBR require model retraining (latency of retrained model not reported).
   3. *Applicable to existing Whisper Turbo checkpoint without retraining*: Ron2026
      (initial_prompt), RECOVER (post-hoc N-best), Novitasari2026 (common-word cues additive),
      Tsai2026 (CTC auxiliary output — verify Whisper Turbo exports CTC scores). RLBR, CLAR,
      RASTAR, Poncelet2026 all require training.
   4. *Estimated entity accuracy uplift per candidate*: tabulate as: Ron2026 ~17% WER reduction /
      entity gain not directly reported; RECOVER ~33–35% E-WER reduction on business-entity domain;
      TARQ (Wang2026b, `10.48550_arXiv.2606.10838`) — quantization-safe rare-word preservation if
      deploying INT4 Whisper Turbo.
   Satisfies REQ-9, REQ-12.

   **Section 4 — Shortlist for prototyping**: Rank exactly 3 techniques by expected entity accuracy
   gain under the <800 ms latency constraint:
   1. Ron2026 initial_prompt multi-agent pipeline (zero training, directly applicable to Whisper
      Turbo, 17% WER reduction, highest ROI).
   2. RECOVER N-best + LLM-Select (zero training, 33–35% E-WER on business entities, adds ~150ms).
   3. BR-ASR retrieval-augmented biasing (production-scale at 200k entries, 20ms retrieval latency,
      requires building an index from Rezolve's brand/product catalog; background paper from 2025 but
      most actionable for catalog-scale biasing).
   Satisfies REQ-10.

   **Section 5 — Gaps and uncertainties**: Cover the following (from research summary):
   * No ecommerce-specific entity benchmark in Jan–Jun 2026; Earnings-21/Contextual Earnings-22 are
     the closest proxies but cover financial entities, not brand SKUs.
   * CLAR and RASTAR evaluated on Mandarin only; English accuracy transfer unverified.
   * Gold-92 lacks entity span annotations; Slot F1 and E-WER cannot be computed without adding
     entity-offset markup.
   * LLM post-correction hallucination risk: unconstrained rewriting can introduce wrong entity names;
     selective span editing (Zheng2026) is safer for fully automated pipelines.
   * RLBR and CLAR require full model retraining; Whisper Turbo commercial license for RL fine-tuning
     must be confirmed.
   * Latency of post-correction methods is largely unmeasured; only Moonshine v2 and BR-ASR report
     concrete latency numbers.
   * Wang2026 LOGIC (logit-space biasing, 9% relative Entity WER) withdrawn from arXiv; cannot be
     implemented until it reappears at a conference venue.
   * WildASR/Tay2026 confirms accent-related degradation but does not measure entity accuracy; gold-92
     has six non-native speakers, making this a direct project risk.
   Satisfies REQ-11, REQ-12 (question 4 on ecommerce benchmarks).

   **Formatting**: Use the project markdown style guide — 100-char line width, `*` bullets, `##`
   subsections, `###` for sub-subsections. Do not exceed 100-char lines.

5. **Write `results/search_log.md`.** Create at
   `tasks/t0003_literature_review_entity_stt/results/search_log.md`. Include a table with columns:
   Query, Database, Date, Result Count, Papers Selected. Populate from the research_internet.md
   and research_papers.md files. All six required keyword combinations must appear. If a query was
   not explicitly logged during research, reconstruct from the paper list (note this in the log).
   Expected output: table with at minimum 6 rows (one per keyword combination), at least one database
   column entry per row. Satisfies REQ-7, REQ-8.

### Milestone 3: Final Verification

6. **Re-run the plan verificator.** Execute:
   `uv run python -u -m arf.scripts.verificators.verify_plan t0003_literature_review_entity_stt`
   Expected: zero PL-E* errors. Satisfies plan structural integrity.

7. **Re-run paper verificator for all 15 assets.** Execute batch:
   ```
   for paper_id in $(ls tasks/t0003_literature_review_entity_stt/assets/paper/); do
     uv run python -u -m arf.scripts.verificators.verify_paper_asset \
       t0003_literature_review_entity_stt $paper_id
   done
   ```
   Expected: zero PA-E* errors for all 15 papers. Satisfies REQ-6, REQ-13.

8. **Confirm synthesis citation integrity.** For every paper ID cited in `results/results_summary.md`,
   confirm the corresponding folder exists at
   `tasks/t0003_literature_review_entity_stt/assets/paper/<paper_id>/`. Execute:
   `grep -oP '`[^`]+`' tasks/t0003_literature_review_entity_stt/results/results_summary.md | sort -u`
   and cross-reference against the paper asset list. Expected: no dead citations. Satisfies REQ-13.

## Remote Machines

None required. This task performs no model inference, no GPU computation, and no large-scale data
processing. All work is text-based: reading paper PDFs, writing summaries and synthesis, running
lightweight Python verificators. The research step has already completed; the implementation step
involves writing two result documents and repairing paper assets.

## Assets Needed

* **15 existing paper assets** at
  `tasks/t0003_literature_review_entity_stt/assets/paper/<paper_id>/` — produced by the
  research-papers step; input to Steps 1–3.
* **Research summary** at
  `tasks/t0003_literature_review_entity_stt/research/research_summary.md` — compact synthesis of
  all research findings; primary source for writing results_summary.md.
* **research_papers.md** at `tasks/t0003_literature_review_entity_stt/research/research_papers.md`
  — detailed per-paper findings and cross-paper analysis for populating the synthesis sections.
* **research_internet.md** at
  `tasks/t0003_literature_review_entity_stt/research/research_internet.md` — search log source for
  reconstructing the query table in search_log.md.
* **task_description.md** at
  `tasks/t0003_literature_review_entity_stt/task_description.md` — verbatim task text for the
  requirement checklist and the Methodology section's research question.
* **meta/categories/** — valid category slugs for PA-W005 warning repairs.
* **meta/asset_types/paper/specification.md** — paper asset structure reference for PA-E* repairs.

## Expected Assets

The task's `task.json` declares `expected_assets: {"paper": 10}`. The actual count will be 15 (the
research-papers step added more than the minimum 10). The `expected_assets` field is a lower bound;
15 is within the 8–15 range specified in `task_description.md`.

| Asset Type | Count | Location | Description |
|------------|-------|----------|-------------|
| `paper` | 15 | `tasks/t0003_literature_review_entity_stt/assets/paper/<paper_id>/` | One paper asset per surveyed paper; each contains `details.json`, `summary.md`, and `files/`. All must pass `verify_paper_asset.py` with zero errors. |

Additional task outputs (not tracked as formal assets but required by task_description.md):

| File | Location | Description |
|------|----------|-------------|
| `results_summary.md` | `tasks/t0003_literature_review_entity_stt/results/results_summary.md` | Five-section synthesis document |
| `search_log.md` | `tasks/t0003_literature_review_entity_stt/results/search_log.md` | Query log with all six keyword combinations |

## Time Estimation

| Phase | Estimated Wall-Clock Time |
|-------|--------------------------|
| Research (already complete) | 0 min — done |
| Milestone 1: Paper asset audit and repair (15 papers × ~5 min each) | 60–90 min |
| Milestone 2: Synthesis writing (results_summary.md) | 30–45 min |
| Milestone 2: Search log writing (search_log.md) | 10–15 min |
| Milestone 3: Final verification (verificators + citation check) | 10–15 min |
| **Total** | **~110–165 min** |

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Paper assets have PA-E* errors blocking verification | High | Blocking for REQ-6 | Run verificator on all 15 assets in Step 2 before writing synthesis; fix errors before proceeding to Milestone 2. Do not skip to synthesis with known errors outstanding. |
| Wang2026 LOGIC asset incomplete (paper withdrawn from arXiv) | Certain | Moderate — one of 15 assets | Ensure `download_status: "failed"`, `download_failure_reason` explains withdrawal, `files/.gitkeep` present. Mark abstract-only in summary; this is acceptable per paper spec when download fails. |
| Synthesis cites a paper not in the 15 confirmed assets | Medium | Blocks REQ-13 | Cite only the 15 paper IDs confirmed in Step 1. Run citation integrity check in Step 8 before declaring done. |
| Shallow fusion not well covered by existing 15 papers | Medium | Gaps in REQ-2 | If no 2026 paper explicitly addresses shallow fusion, document this as a literature gap in the synthesis (REQ-11). Do not fabricate a shallow fusion citation. |
| Paper summary under 500 words (PA-W001) for several assets | Medium | Quality warning | Expand Overview and Summary sections during Step 3. Prioritise the papers cited in the synthesis (those in the shortlist) over background papers. |
| research_internet.md search queries not fully logged | Low | Gaps in REQ-7 search log | Reconstruct from paper list and arXiv submission dates; note any reconstructed entries as "reconstructed" in the search log. |
| Synthesis exceeds 100-char line width (markdown style violation) | Low | Formatting warning | Run `uv run flowmark --inplace --nobackup results/results_summary.md` after writing. |

## Verification Criteria

* **All 15 paper assets pass the verificator with zero errors**:
  Run `uv run python -u -m arf.scripts.verificators.verify_paper_asset t0003_literature_review_entity_stt <paper_id>`
  for each of the 15 paper IDs in `tasks/t0003_literature_review_entity_stt/assets/paper/`.
  Expected: `0 errors` for every asset. (REQ-6)

* **results_summary.md exists with all five mandatory sections**:
  Run `grep -c "^## " tasks/t0003_literature_review_entity_stt/results/results_summary.md`.
  Expected: at least 5 (Methodology, Findings by technique category, Comparison Against Whisper Turbo
  + Dynamic Context Injection, Shortlist for prototyping, Gaps and uncertainties). (REQ-8)

* **search_log.md exists and contains all six keyword combinations**:
  Run `wc -l tasks/t0003_literature_review_entity_stt/results/search_log.md`.
  Expected: at least 8 lines (header + 6 query rows + table separator). Then verify all six queries
  are present: `grep -c "contextual biasing\|entity-aware\|shallow fusion\|LLM post-correction\|domain-specific ASR\|Whisper fine-tuning" results/search_log.md`.
  Expected: 6. (REQ-7)

* **Synthesis cites only verified paper assets (no fabricated citations)**:
  Extract all paper IDs mentioned in `results/results_summary.md` and confirm each folder exists:
  `for pid in $(grep -oP '10\.\d+_[^\s`"]+' results/results_summary.md); do ls assets/paper/$pid/ > /dev/null 2>&1 || echo "MISSING: $pid"; done`
  Expected: no MISSING lines. (REQ-13)

* **Plan verificator passes with zero errors**:
  Run `uv run python -u -m arf.scripts.verificators.verify_plan t0003_literature_review_entity_stt`.
  Expected: `0 errors`. (Plan structural integrity)

* **Synthesis Comparison section addresses all four sub-questions (REQ-9)**:
  `grep -n "latency-compatible\|without retraining\|estimated entity accuracy\|hotword" tasks/t0003_literature_review_entity_stt/results/results_summary.md | wc -l`
  Expected: at least 4 matches. (REQ-9)

## Rejection Criteria

This task produces a literature survey, not a benchmark measurement. Pre-registration of null
conditions applies to any quantitative comparison included in the synthesis:

* If fewer than 8 paper assets pass `verify_paper_asset.py` with zero errors, the task output is
  **incomplete** and must not be merged — fix the assets before closing.
* If the synthesis's "Shortlist for prototyping" section is empty or contains fabricated citations
  (paper IDs not corresponding to real assets), the synthesis is **null** and must be rewritten.
* If Wang2026 LOGIC is cited as a working method (rather than a withdrawn paper), the Shortlist
  section is **invalid** — this paper cannot be implemented until it reappears at a venue.
* Papers with `download_status: "failed"` may be cited in the synthesis only if the summary
  explicitly notes "abstract-only — PDF unavailable" and the findings are drawn solely from the
  abstract. If findings beyond the abstract are attributed to a failed-download paper, those claims
  are **unverifiable** and must be removed.
