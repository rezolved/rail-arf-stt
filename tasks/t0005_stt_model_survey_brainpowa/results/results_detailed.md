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

**Search coverage:**
- HuggingFace Open ASR Leaderboard (WER, model card metadata)
- Papers-with-Code ASR benchmark
- Artificial Analysis speech-to-text
- GitHub repos + official documentation
- arXiv recent papers (2024–2026)
- Release announcements (NVIDIA, Alibaba, Kyutai, Useful Sensors)

## Key Findings

### Top 3 Shortlist

**1. IBM Granite Speech 4.1 2B** — **PRIMARY CANDIDATE**
- Metric: #1 on Open ASR Leaderboard (5.33% WER, best-in-class)
- Entity accuracy: Native keyword biasing with published F1 metrics
- Latency: ~100–150 ms TTFT (under 800ms budget)
- License: Apache 2.0 (self-hostable, no restrictions)
- Integration: HF Transformers API, PCM-16 mono input native
- **Verdict:** Highest priority for gold-92 benchmark run

**2. FunASR Paraformer (SenseVoice/SeACo variant)** — **SECONDARY CANDIDATE**
- Entity accuracy: 1.8% Entity WER (EWER) with contextual biasing on ~1,800 entities
- Biasing: Shallow fusion + entity embeddings, +20–30% entity recall reported
- Latency: 480–600 ms segment latency (feasible but tight under 800ms total)
- License: Apache 2.0 (self-hostable)
- Integration: Requires NeMo wrapper or HF port
- **Verdict:** Strong if TTFT latency <200ms achievable; test concurrent load

**3. Moonshine v2 Medium** — **EDGE-DEPLOYMENT CANDIDATE**
- Latency: ~258 ms (fastest), no GPU required (MIT license)
- WER: 5.3% with 6× fewer parameters than Whisper turbo
- Entity accuracy: No native biasing; requires external shallow-fusion adapter
- Integration: Python inference simple, but biasing layer needed
- **Verdict:** Viable for edge if external biasing cost acceptable

### Excluded High-Priority Candidates

- **Canary (NVIDIA Qwen 2.5B)**: Good WER (4.8%) but no contextual biasing; ~3s latency too high
- **Kyutai STT 2.6B**: 2.5s output delay inherent; incompatible with 800ms latency budget
- **Whisper large-v3**: 7.4% WER, no contextual biasing (only initial_prompt); t0004 already tested
  upper bound
- **wav2vec2/XLSR**: Fine-tuning base, no ready-to-run model; not production-ready

## Task Requirement Coverage

**REQ-1: Survey open-source STT models**
- ✓ Surveyed 20+ models across 10 families (NVIDIA, Whisper variants, Moonshine, Kyutai, FunASR,
  Granite, etc.)
- ✓ Documented all candidate dimensions (license, weights, biasing, latency, entity-accuracy)
- Deliverable: `research/research_internet.md` (478 lines, comparison table)

**REQ-2: Shortlist top candidates ranked by fit to brainpowa brick + entity accuracy**
- ✓ Ranked top 3 (Granite, Paraformer, Moonshine) with fit rationale
- ✓ Explicitly compared against current parakeet/Whisper/Azure providers
- ✓ Documented integration effort + latency implications
- Deliverable: `research/research_internet.md` § "Shortlist & Recommendations"

**REQ-3: Recommend 1–2 candidates for follow-on gold-92 benchmark**
- ✓ Primary recommendation: IBM Granite 4.1 2B (highest confidence, ready-to-integrate)
- ✓ Secondary: FunASR Paraformer (if latency constraint validated under load)
- Deliverable: research_internet.md § "Next Steps: 4-Week Roadmap"

## Verification

- `verify_research_internet.py` — **PASSED**
  - 478 lines of synthesis (well above 400-word minimum)
  - 20+ sources cited with complete metadata
  - 4 papers identified for future download
  - 13 search queries documented with exact text
  - All inline citations mapped to Source Index

## Limitations

- Entity-accuracy claims for Granite/Paraformer sourced from published papers; not independently
  verified on gold-92 (reserved for next benchmark task).
- Latency measurements from published benchmarks assume batch sizes and hardware specific to each
  paper; concurrent real-time latency may differ.
- No hands-on code integration testing; integration effort estimates based on documentation + GitHub
  repo structure (not execution).
- Moonshine's external-biasing approach speculative; not yet implemented/benchmarked on domain
  vocabulary.

## Files Created

- `research/research_internet.md` — comprehensive survey document (23 KB)
- `research/search_log.md` — audit trail of 13 search queries + sources (9 KB)

## Next Steps

**Recommended benchmarking roadmap (4 weeks):**
1. **Week 1:** Set up Python async wrappers for Granite 4.1 and current Parakeet (STTAdapter
   Protocol)
2. **Week 2:** Benchmark on 10–20 gold-92 clips (entity accuracy + latency, concurrent load test)
3. **Week 3:** Full gold-92 run if promising; evaluate FunASR Paraformer if needed
4. **Week 4:** Finalize integration + implement external biasing adapter if Moonshine selected
