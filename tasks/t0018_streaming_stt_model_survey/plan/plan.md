---
spec_version: "2"
task_id: "t0018_streaming_stt_model_survey"
date_completed: "2026-07-02"
status: "complete"
---

## Objective

Produce an exhaustive internet-research survey of open-source / open-weight speech-to-text (STT)
models that support **true incremental (streaming) decoding** — models that emit partial
transcription hypotheses as audio arrives, rather than accepting an arbitrary-length buffer and
running one batch pass. The survey's sole axis is streaming capability, in contrast to
`t0005_stt_model_survey_brainpowa`, which treated streaming as one of eight generic dimensions. The
output must let a future task decide which streaming architecture(s) merit a gold-92 benchmark run
as a candidate to replace or complement the current production configuration
(`parakeet-unified-en-0.6b` at a ~300ms buffer, per `t0017_parakeet_biasing_buffer_replacement`).
Success = `research/research_internet.md` exists, covers every candidate family listed in
`task_description.md` plus any newer 2025–2026 releases (weighted toward the last 6 months,
2026-01-02 to 2026-07-02), scores each on the eight required dimensions, explicitly separates
native-streaming from pseudo-streaming models, and ends with a ranked shortlist of 3–5 candidates
with a recommended next benchmark task.

## Task Requirement Checklist

Quoted from `task_description.md` (task `t0018_streaming_stt_model_survey`):

> Which open-source / open-weight STT models support **true incremental (streaming) decoding** —
> producing partial hypotheses as audio arrives, not just accepting arbitrary-length input — and
> how do their streaming architectures compare on chunk/frame granularity, latency or
> real-time-factor (RTF), and integration effort into the brainpowa `STTAdapter.transcribe_stream`
> interface (`src/brainpowa_realtime_api/pipeline/stt/base.py`)?
>
> Recency constraint: prioritize models released or with a major streaming-relevant update in the
> last 6 months (2026-01-02 through 2026-07-02).

* **REQ-1**: Cover every candidate family named in `task_description.md` Scope: NVIDIA
  Parakeet/Canary/FastConformer streaming configs, Kyutai Moshi/Kyutai STT, Moonshine, Whisper
  streaming variants (whisper_streaming, WhisperLive, simul-whisper, faster-whisper streaming
  wrappers), FunASR/Paraformer streaming (U2/U2++), wav2vec2/MMS streaming, IBM Granite Speech
  streaming mode, Google USM/Chirp streaming, plus any newer 2025–2026 releases found. Satisfied by
  Step 3 (per-family research passes) and the comparison table in Step 6.
* **REQ-2**: Record the eight per-candidate dimensions for every candidate: (1) family/size/license/
  weights location, (2) streaming mechanism/architecture class, (3) true-streaming vs
  pseudo-streaming classification with justification, (4) chunk/frame size and look-ahead, (5)
  streaming-mode latency/RTF, (6) contextual biasing support in streaming mode, (7)
  `STTAdapter.transcribe_stream` integration effort, (8) fit verdict vs
  parakeet-unified-en-0.6b@~300ms and Granite Speech 4.1 2B. Satisfied by Step 3 and the table
  structure defined in Step 6.
* **REQ-3**: Explicitly separate "native streaming decoder" candidates from "pseudo-streaming via
  re-inference" candidates in the write-up structure. Satisfied by Step 6 (dedicated subsection
  split).
* **REQ-4**: Apply the recency constraint — weight search effort toward the last 6 months
  (2026-01-02 to 2026-07-02) and run explicit 2026-dated release-announcement searches. Satisfied by
  Step 2 (recency-focused query set) and Step 3.
* **REQ-5**: Exclude closed cloud-only streaming APIs (Azure Speech, Google STT streaming,
  Deepgram, AssemblyAI) from the candidate table — list them only as named comparison baselines.
  Satisfied by Step 6 (baseline callout, not a table row).
* **REQ-6**: Do not re-survey non-streaming accuracy already covered by `t0005`, `t0007`–`t0012`,
  or biasing techniques in general already covered by `t0003` — only note biasing as it interacts
  with streaming mode. Satisfied by Step 1 (read prior task summaries to avoid duplication) and
  Step 3 (biasing dimension scoped to streaming-mode only).
* **REQ-7**: Cross-check every RTF/latency claim against at least one independent source. Satisfied
  by Step 4 (cross-reference pass).
* **REQ-8**: Log every search query and result count in `research/search_log.md`. Satisfied by
  Step 2 and ongoing logging during Step 3.
* **REQ-9**: Produce a comparison table (rows = candidates, columns = the eight dimensions), a
  ranked shortlist (top 3–5) with rationale and source URLs, an explicit comparison against the
  current production baseline (parakeet-unified-en-0.6b @ ~300ms, t0017) and the entity-accuracy
  leader (Granite Speech 4.1 2B, batch-only), and a "recommended next experiment" note. Satisfied by
  Step 6.
* **REQ-10**: `expected_assets: {}` in `task.json` — no model, dataset, or paper assets required.
  Satisfied trivially; no asset-creation steps in this plan.

No ambiguity requires special handling: the task text is unusually precise about which dimensions
and families are in scope, and the recency window is stated as exact dates (2026-01-02 to
2026-07-02) in `task_description.md`.

## Approach

**Task type**: `internet-research` (already set in `task.json`). Per
`meta/task_types/internet-research/instruction.md` Planning Guidelines: define the research
question precisely (done above), list 3–5 specific search queries up front (Step 2), identify
relevant source types (official model cards/GitHub/docs as primary, HF Open ASR Leaderboard and
arXiv as secondary, independent benchmarks for cross-checking, never sole-sourced), and set a time
budget (this is a research-only task with no paid compute; budget is bounded by search/read effort,
not dollars).

**Grounding in prior task findings** (no `research_summary.md` exists yet since this is the first
research step for t0018 — using `task_description.md` and prior task result files directly, per the
planning skill's documented fallback):

* `t0017_parakeet_biasing_buffer_replacement` established current production reality: brainpowa
  reframes audio into 1024-byte/32ms VAD frames before STT (`orchestrator.py:946-952`), currently
  re-transcribes every `stt_stream_interval_bytes=32000` (~1s, `config.py:75`), and the corrected
  recommendation is to lower this to ~300ms. `parakeet-unified-en-0.6b` is the current
  accuracy-winner within Parakeet (WER 11.0%, EA-DV 34.8%) but Parakeet's streaming today is
  accumulate-then-retranscribe on GPU-PB TurboBias — a pseudo-streaming pattern, not a native
  streaming decoder. This survey should determine whether any candidate offers genuine incremental
  decoding that could beat this pattern on TTFD without the retranscribe-cadence cost.
* `t0015_streaming_buffer_interval` already benchmarked `multitalker-parakeet-streaming-0.6b-v1` —
  this is a named NVIDIA streaming-specific checkpoint and must be included in the Parakeet family
  row, distinguishing it from the plain `parakeet-tdt`/`parakeet-unified` checkpoints used via
  batch re-inference.
* `t0007`/`t0012`/`t0014` established Granite Speech 4.1 2B as the entity-accuracy leader
  (97.1% EA-DV) but it has only been run in batch/whole-utterance mode in this project — this
  survey must determine if Granite has any native streaming mode at all, since that would be the
  highest-value finding (best accuracy + true streaming).
* `t0008` eliminated Moonshine on accuracy (EA 21.7%) but Moonshine's core value proposition is
  fast **streaming** ASR — this survey must document its streaming architecture on its own terms
  (chunk size, RTF) even though it lost on the accuracy axis in a different task.
* `t0010` eliminated Paraformer on WER (122.7%) in batch mode — FunASR's streaming variant
  (Paraformer-streaming, U2/U2++) is architecturally distinct from the batch checkpoint tested and
  must be evaluated fresh on streaming architecture merits, not skipped due to the batch result.

**Alternative approach considered and rejected**: a code-first approach (cloning each candidate's
GitHub repo and inspecting streaming inference code directly) would give higher-confidence answers
to REQ-2 dimension 3 (true vs pseudo streaming) but is far more expensive (10+ repos, environment
setup per repo) and out of scope for a `$0`-budget internet-research task. This survey uses
documentation, model cards, and papers instead, cross-checked across ≥2 sources per REQ-7, and
flags any claim it cannot independently verify from docs alone as "unverified — recommend code
inspection in a follow-on task" rather than guessing.

**Sources prioritized** (per instruction.md and the internet-research task type): official model
cards / GitHub repos / vendor docs (authoritative for architecture, license, chunk size); NeMo
streaming inference documentation (for Parakeet/Canary/FastConformer); Kyutai's Moshi paper and repo
(for full-duplex architecture); HF Open ASR Leaderboard and Papers-with-Code (for WER cross-checks
only, not streaming-specific claims); vendor blogs/changelogs dated in 2026 for the recency
requirement (REQ-4).

## Cost Estimation

**Total: $0.** This is a pure internet-research task with `expected_assets: {}` and no model
training, no GPU compute, and no paid API calls beyond the implementation agent's own LLM usage
(covered by the ARF session budget, not a separate line item). All sources are public
documentation, model cards, GitHub repos, and papers — no downloads of gated/paid datasets or
models are required. This is consistent with `project/budget.json`
(`total_budget: 2000.0 USD`, `per_task_default_limit: 100.0 USD`) — $0 spend leaves full headroom
for the follow-on benchmark task this survey recommends.

## Step by Step

**Milestone 1 — Setup and query design (REQ-4, REQ-8)**

1. **Create the research folder and search log.** Create `research/search_log.md` with a table:
   columns `query`, `date`, `result_count`, `notes`. [CRITICAL] This is the traceability record
   required by REQ-8 and the internet-research verification criteria (≥3 independent sources
   cited, every claim sourced).

2. **Define and log the query set before searching**, covering both general and recency-focused
   angles (REQ-4):
   * General: `"streaming ASR" architecture 2026`, `"incremental speech recognition" streaming
     decoder`, `"real-time speech-to-text" chunk size latency`, `"streaming RNNT" transducer`,
     `"streaming transducer" chunked attention Conformer`, `"full-duplex speech" model`.
   * Per-family: `"parakeet streaming" NeMo chunk`, `"kyutai moshi" streaming architecture`,
     `"moonshine" streaming ASR chunk size`, `whisper_streaming OR WhisperLive OR simul-whisper`,
     `"paraformer streaming" U2++ FunASR`, `"wav2vec2 streaming" OR "MMS streaming" CTC`,
     `"granite speech" streaming mode NVIDIA IBM`, `"USM streaming" OR "Chirp streaming" Google`.
   * Recency-focused (REQ-4, weight the bulk of effort here): `"streaming ASR" 2026 release`,
     `"new streaming speech recognition model" 2026`, `NVIDIA streaming ASR 2026 blog`,
     `Kyutai 2026 release`, `Hugging Face streaming ASR model 2026`, `Alibaba FunASR 2026 update`,
     `IBM Granite Speech 2026 update`, `Google Chirp 2026 streaming`, `Meta streaming ASR 2026`.
   Log every query and its result count in `research/search_log.md` immediately after running it.
   Satisfies REQ-8.

**Milestone 2 — Per-candidate research passes (REQ-1, REQ-2, REQ-6)**

3. **Research each candidate family and record the eight dimensions.** For each family in the
   Scope list of `task_description.md` — NVIDIA Parakeet/Canary/FastConformer (including
   `multitalker-parakeet-streaming-0.6b-v1` specifically, per t0015), Kyutai Moshi/Kyutai STT,
   Moonshine, Whisper streaming variants, FunASR/Paraformer streaming, wav2vec2/MMS streaming,
   IBM Granite Speech streaming mode, Google USM/Chirp streaming — search using the query set from
   Step 2, read the official model card/GitHub repo/paper, and write findings incrementally into
   `research/research_internet.md` structured by candidate. For each candidate, record: (1)
   family/sizes/params/license/weights location, (2) streaming mechanism architecture class, (3) a
   true-streaming vs pseudo-streaming verdict with the specific evidence (e.g., "NeMo streaming
   Conformer-Transducer API documents per-chunk cache-aware streaming — true streaming" vs "vendor
   markets streaming but code re-runs full-utterance inference on a growing buffer —
   pseudo-streaming"), (4) chunk/frame size and look-ahead/right-context if configurable, (5)
   streaming-mode latency or RTF as reported (mark "not reported" rather than guessing), (6)
   contextual biasing support specifically in streaming mode, (7) integration effort into
   `STTAdapter.transcribe_stream` (async generator support, framework, PCM-16 mono handling), (8)
   leave the fit-verdict column for Step 6 (it needs the full table assembled first). Do not
   re-derive non-streaming WER/entity-accuracy numbers already reported in `t0005`, `t0007`,
   `t0008`, `t0010`, `t0012` — cite those task IDs directly instead of re-researching. Satisfies
   REQ-1, REQ-2 (dimensions 1–7), REQ-6.

4. **Cross-check every latency/RTF claim against ≥1 independent source.** For each streaming-mode
   latency or RTF number recorded in Step 3, search for at least one second source (an independent
   benchmark, a different vendor doc, a community reproduction) that corroborates or contradicts
   it. Log the second source in the candidate's entry in `research/research_internet.md` and flag
   any single-sourced number explicitly as "single-source, unverified." Satisfies REQ-7.

5. **Search specifically for any 2025–2026 releases not already covered**, using the recency
   queries from Step 2. Add any newly-found candidate as a new row using the same Step 3 process.
   This step has no fixed candidate list — continue until two consecutive recency-focused searches
   surface no new candidate family, at which point stop (this task's stopping criterion per
   `task_description.md`).

**Milestone 3 — Synthesis (REQ-3, REQ-5, REQ-9)**

6. **Write the comparison table, native-vs-pseudo split, shortlist, and recommendation into
   `research/research_internet.md`.** [CRITICAL] This is the deliverable the task exists to
   produce.
   * Build one markdown table: rows = every candidate from Steps 3 and 5, columns = the eight
     dimensions (with dimension 8 — fit verdict — filled in now by comparing each candidate's
     chunk size/latency/biasing/integration-effort against `parakeet-unified-en-0.6b` at ~300ms
     buffer (t0017 result) and Granite Speech 4.1 2B's batch-only entity accuracy (t0007/t0012/
     t0014/t0015)).
   * Add a dedicated subsection "Native Streaming Decoders" listing every candidate whose
     dimension-3 verdict is true-streaming, and a subsection "Pseudo-Streaming (Batch
     Re-Inference)" for the rest. Satisfies REQ-3.
   * Add a "Closed/Comparison-Only Baselines" callout naming Azure Speech, Google STT streaming,
     Deepgram, AssemblyAI as named references, explicitly excluded from the candidate table.
     Satisfies REQ-5.
   * Write a ranked shortlist of 3–5 candidates with one-paragraph rationale and source URLs each,
     an explicit comparison paragraph against the current production baseline and Granite, and a
     "recommended next experiment" paragraph naming which 1–2 candidates merit a gold-92 streaming
     benchmark task. Satisfies REQ-9.
   * No metrics apply to this task (see Metrics section below) — no `results/metrics.json` writing
     step is needed.

No registered project metric applies to this task. All seven registered metrics
(`action_critical_wer_gold92`, `entity_accuracy_domain_vocab`, `entity_accuracy_gold92`,
`intent_preservation_gold92`, `latency_p50_seconds`, and the remaining two per
`tasks/t0018_streaming_stt_model_survey/ctx/metrics.json`) require running inference on the gold-92
benchmark. This task performs no inference and produces no predictions — it is a literature/
documentation survey. This omission is deliberate: the survey's own Step 6 output ("recommended
next experiment") is what will trigger a future task that does measure these metrics.

## Remote Machines

None required. This task involves no model inference, training, or GPU compute — it is internet
research reading public documentation, model cards, GitHub repos, and papers.

## Assets Needed

None as formal ARF assets. Informational inputs (not blocking, read for context only): prior task
result summaries — `tasks/t0005_stt_model_survey_brainpowa/research/research_internet.md` (general
survey to avoid duplicating non-streaming findings), `tasks/t0017_parakeet_biasing_buffer_replacement/
results/results_detailed.md` and `results/buffer_interval_realtime.md` (current production baseline
numbers for the fit-verdict column), `tasks/t0007_ibm_granite_4_1_benchmark/results/
results_summary.md`, `tasks/t0012_whisper_parakeet_granite_streaming/results/results_summary.md`,
`tasks/t0014_granite_short_clip_robustness/results/results_summary.md`,
`tasks/t0015_streaming_buffer_interval/results/results_summary.md` (Granite and Parakeet-streaming
context), `tasks/t0008_moonshine_v2_benchmark/results/results_summary.md`,
`tasks/t0010_funasr_paraformer_benchmark/results/results_summary.md` (batch-mode accuracy results
to cite rather than re-derive), `tasks/t0003_literature_review_entity_stt/research/
research_internet.md` (biasing technique survey, to avoid re-surveying general biasing methods).
All are read-only references within this repository; no external asset dependency exists (task.json
`dependencies: []` is correct).

## Expected Assets

None. `task.json` sets `expected_assets: {}`. This task produces only research documents
(`research/research_internet.md`, `research/search_log.md`), no dataset/model/paper/predictions/
answer assets.

## Time Estimation

* Milestone 1 (setup + query design): ~15 minutes.
* Milestone 2 (per-candidate research, ~9 named families + recency sweep): ~2–3 hours — the bulk of
  the task, since each candidate needs its own model-card/repo/paper read plus a cross-check
  source.
* Milestone 3 (synthesis — table, split, shortlist, recommendation): ~45 minutes.
* Total estimated wall-clock: ~3–4 hours of agent research time. No remote-compute or asset-creation
  time applies.

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Vendor docs claim "streaming support" without disclosing whether it's true incremental decoding or batch re-inference on a growing buffer, and the ambiguity can't be resolved from docs alone | High | Medium — weakens REQ-2 dimension 3 confidence for some candidates | Default to "pseudo-streaming (unverified)" rather than guessing true-streaming; explicitly flag these in the table and note "recommend code inspection" in the shortlist writeup. Never assert true-streaming without a specific documented mechanism (e.g., named cache-aware streaming API, published chunk-size parameter). |
| Latency/RTF numbers are reported inconsistently across sources (different batch sizes, different hardware, different audio duration) and cannot be cleanly cross-checked per REQ-7 | Medium | Medium — could produce misleading fit-verdict comparisons | Record the exact reported conditions (hardware, chunk size, dataset) alongside every latency number instead of a bare figure; if two sources disagree, report both with their conditions rather than picking one, and flag the discrepancy explicitly in the candidate's entry. |
| Some 2025–2026 "release" search results turn out to be minor version bumps or blog re-announcements of older architectures, inflating the candidate count without new information | Low | Low — wastes research time, not correctness | Apply the stopping criterion literally: only add a candidate row if it introduces a genuinely new streaming mechanism or measurably different chunk/latency profile from an already-covered family; note re-announcements as a one-line mention under the existing family instead of a new row. |
| A candidate family (e.g., Google USM/Chirp) turns out to have no open-weight release at all, only a closed API | Low | Low — REQ-1 coverage gap | Document this explicitly as "closed/API-only, no open weights — moved to the Closed/Comparison-Only Baselines callout" rather than silently dropping the family; this itself is a valid finding for REQ-1/REQ-5. |

## Verification Criteria

* Run `test -f "tasks/t0018_streaming_stt_model_survey/research/research_internet.md" && wc -w
  tasks/t0018_streaming_stt_model_survey/research/research_internet.md` — expect the file to exist
  and exceed 500 words (internet-research task type minimum per
  `meta/task_types/internet-research/instruction.md`).
* Run `test -f "tasks/t0018_streaming_stt_model_survey/research/search_log.md"` — expect the file
  to exist and contain every query listed in Step 2 plus any added in Step 5, each with a
  result-count column filled in (REQ-8).
* Run `grep -c '^| ' tasks/t0018_streaming_stt_model_survey/research/research_internet.md` — expect
  a non-trivial count of table rows (>15, accounting for header/separator rows across the
  comparison table), confirming the eight-dimension comparison table from Step 6 was produced
  (REQ-2, REQ-9).
* Run `grep -iE 'native streaming|pseudo-streaming' tasks/t0018_streaming_stt_model_survey/research/
  research_internet.md` — expect matches confirming the required native-vs-pseudo-streaming split
  section exists (REQ-3).
* Run `grep -c 'http' tasks/t0018_streaming_stt_model_survey/research/research_internet.md` —
  expect ≥3 distinct source URLs cited (internet-research verification requirement: at least 3
  independent sources).
* Manually confirm every `REQ-1` through `REQ-10` item in the Task Requirement Checklist above maps
  to content actually present in `research/research_internet.md` and `research/search_log.md` —
  this is the direct requirement-coverage check requested by the plan specification.

## Rejection Criteria

Not applicable in the standard benchmark-null sense (this task produces no paired predictions or
success/failure request counts to compute a `successful_requests / total_requests` ratio against).
The task-specific rejection condition is: if fewer than 6 of the 9 named candidate families in
`task_description.md` Scope can be researched with at least dimensions 1–4 filled in (i.e., more
than 3 families are entirely "unknown / not reported" across the board), the research is
incomplete and must not be reported as a finished survey — the implementation agent must create an
intervention file identifying which families could not be researched and why (e.g., no public
documentation exists) before the task can be marked complete.
