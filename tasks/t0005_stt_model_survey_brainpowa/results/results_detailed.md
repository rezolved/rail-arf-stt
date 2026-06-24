---
spec_version: "2"
task_id: "t0005_stt_model_survey_brainpowa"
---
# Results Detailed: STT Model Survey for brainpowa Pipeline

## Summary

Executed the `/research-internet` skill to survey open-source/open-weight STT models (2020–2026,
emphasis 2024–2026) for integration as a brainpowa STTAdapter brick candidate. Conducted 13
structured internet searches across official documentation, GitHub repos, arXiv, HF Open ASR
Leaderboard, and independent benchmarks. Evaluated 20+ models against 8 per-candidate dimensions
(family, license, weights, streaming, biasing, GPU/latency, WER+entity-recall, integration effort).
Produced ranked shortlist of 3 top candidates and documented all search queries + rationale for
exclusions.

## Methodology

**Research process:**
1. Defined 8 per-candidate evaluation dimensions based on brainpowa STTAdapter Protocol and product
   constraints (800ms p50, entity accuracy, contextual biasing).
2. Executed 13 structured search queries covering model families (NVIDIA, HuggingFace, FunASR,
   Moonshine, Kyutai), biasing mechanisms, latency benchmarks, 2025-2026 releases, and integration
   pathways.
3. Conducted deep reads on 7 authoritative sources (HF ASR Leaderboard, GitHub repos, benchmark
   papers, official docs).
4. Cross-referenced accuracy/latency claims across ≥2 independent sources; flagged single-source
   claims.
5. Excluded candidates with clear disqualifiers (no contextual biasing, <800ms infeasible, or
   closed/commercial).
6. Ranked top 3 by entity-accuracy fit + latency + biasing support.

## Key Findings

### Top 3 Shortlist

**1. IBM Granite Speech 4.1 2B** — **PRIMARY CANDIDATE**
- #1 on Open ASR Leaderboard (5.33% WER)
- Native keyword biasing with published F1 metrics
- ~100–150 ms TTFT (under 800ms budget)
- Apache 2.0 license, self-hostable
- Highest priority for gold-92 benchmark run

**2. FunASR Paraformer** — **SECONDARY CANDIDATE**
- 1.8% Entity WER with contextual biasing on ~1,800 entities
- 480–600 ms segment latency
- Apache 2.0 license
- Test if TTFT <200ms achievable under concurrent load

**3. Moonshine v2 Medium** — **EDGE-DEPLOYMENT CANDIDATE**
- ~258 ms latency, no GPU required
- 5.3% WER with 6× fewer parameters than Whisper turbo
- No native biasing; requires external shallow-fusion adapter
- Viable if external biasing cost acceptable

## Verification

- `verify_research_internet.py` — **PASSED**
  - 478 lines of synthesis
  - 20+ sources cited
  - 13 search queries documented
  - 4 papers identified for download

## Limitations

- Entity-accuracy claims sourced from published papers; not independently verified on gold-92.
- Latency measurements assume batch sizes and hardware specific to each paper; concurrent real-time
  latency may differ.
- Integration effort estimates based on documentation + GitHub repo structure, not execution.
- Moonshine's external-biasing approach speculative; not yet implemented/benchmarked on domain
  vocabulary.

## Files Created

- `research/research_internet.md` — comprehensive survey document (23 KB)
- `research/search_log.md` — audit trail of 13 search queries + sources (9 KB)
- `results/suggestions.json` — 10 follow-up suggestions (2 KB)

## Task Requirement Coverage

**REQ-1: Survey open-source STT models for brainpowa** — **Done**. Deliverable:
`research/research_internet.md` with 20+ models surveyed across 8 evaluation dimensions. Evidence:
research/research_internet.md (23 KB, 478 lines, comparison table, sources).

**REQ-2: Shortlist top candidates ranked by brainpowa fit** — **Done**. Deliverable:
`research/research_internet.md` with top-3 candidates (Granite 4.1, Paraformer, Moonshine) ranked by
entity accuracy + latency fit + biasing support. Evidence: research/research_internet.md §
"Shortlist & Recommendations" with explicit comparison vs current parakeet/Whisper/Azure.

**REQ-3: Recommend 1–2 candidates for follow-on gold-92 benchmark** — **Done**. Deliverable:
`research/research_internet.md` § "Next Steps: 4-Week Roadmap" with primary (Granite 4.1 2B) and
secondary (FunASR Paraformer) recommendations. Evidence: research/research_internet.md "Next Steps"
section with 4-week benchmarking roadmap.
