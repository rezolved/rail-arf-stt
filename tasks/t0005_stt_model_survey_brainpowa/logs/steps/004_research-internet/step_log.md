---
spec_version: "3"
task_id: "t0005_stt_model_survey_brainpowa"
step_number: 4
step_name: "research-internet"
status: "completed"
started_at: "2026-06-24T10:51:47Z"
completed_at: "2026-06-24T14:08:00Z"
---

## Summary

Executed the /research-internet skill to comprehensively survey open-source/open-weight STT models suitable for integration into the brainpowa STTAdapter brick. Conducted 13 structured internet searches across multiple sources (HF Open ASR Leaderboard, GitHub, arXiv, official docs) covering the STT model landscape, entity accuracy capabilities, latency characteristics, and integration feasibility. Identified 20+ candidate models and produced a ranked shortlist of top 3 candidates (IBM Granite 4.1, FunASR Paraformer, Moonshine v2) with detailed fit analysis against brainpowa's latency and contextual-biasing constraints.

## Actions Taken

1. Executed 13 structured internet search queries covering model families, biasing mechanisms, latency benchmarks, 2025-2026 releases, and integration pathways.
2. Conducted deep-read research on 7 authoritative technical sources (HF ASR Leaderboard, GitHub repos, benchmark papers) to validate claims.
3. Evaluated 20+ candidate STT models against 8 per-candidate dimensions: family, license, weights availability, streaming, biasing support, GPU/VRAM+latency, WER+entity-recall, integration effort.
4. Produced ranked shortlist of top 3 candidates (IBM Granite 4.1 2B, FunASR Paraformer, Moonshine v2) with comparative analysis against current parakeet/Whisper/Azure providers.
5. Documented all 13 search queries and 50+ consulted sources in search_log.md with reasoning for included/excluded candidates.

## Outputs

- `research/research_internet.md` — comprehensive STT model survey (23 KB, 478 lines) with comparison table, ranked shortlist, and integration recommendations.
- `research/search_log.md` — audit trail of 13 search queries, source metadata, and refinement rationale.

## Issues

No issues encountered. All verificators passed.
