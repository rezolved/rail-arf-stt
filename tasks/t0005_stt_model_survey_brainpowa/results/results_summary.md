# Results Summary: STT Model Survey for brainpowa Pipeline

## Summary

Comprehensive internet research identified and ranked 20+ open-source/open-weight STT models
suitable for integration as a brainpowa STTAdapter brick candidate. Top 3 shortlist: **IBM Granite
4.1 2B** (highest entity accuracy + latency fit), **FunASR Paraformer** (best entity-specific
metrics), **Moonshine v2** (fastest, CPU-only). Research revealed entity-biasing capability gaps in
standard Whisper/Canary and positioned Granite + Paraformer as primary next-step benchmarking
candidates for gold-92 evaluation against current Whisper turbo + initial_prompt baseline.

## Metrics

- **Models surveyed**: 20+ (15 detailed, 5 excluded with rationale)
- **Search queries executed**: 13 structured queries with 50+ consulted sources
- **Top candidates shortlisted**: 3 (Granite, Paraformer, Moonshine)
- **Verified citations**: 20 sources with complete metadata, 4 papers identified for download
- **Entity-accuracy candidates**: 2 with native biasing (Granite, Paraformer)
- **Latency-optimized candidates**: 2 under 800ms (Moonshine <300ms, Granite ~150ms)

## Verification

- `verify_research_internet.py` — **PASSED** (478 lines, 20+ sources, 13 queries documented)
- Task requirement coverage: REQ-1 (model survey completed) ✓, REQ-2 (shortlist with fit rationale)
  ✓
