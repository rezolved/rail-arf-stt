# Research Summary — t0014_granite_short_clip_robustness

## Key Findings (top 10 insights directly actionable for this task)

1. **Granite 4.1 2B has a 4-second block-attention window**: Sub-4 s clips are processed in a
   single Conformer block pass with no intermediate VAD. A 0.5 s clip yields only 5 Q-Former
   acoustic embeddings; expected failure mode is empty output (silent degradation), not
   hallucination. [HF-GraniteDoc, Saon2025]

2. **Parakeet default chunk_secs=2**: All clips under 2 s (the 0.5 s, 1.0 s, 1.5 s bins) are
   delivered as a single under-filled chunk plus `None` sentinel — degenerate single-chunk path.
   Confirm whether `ParakeetSTT.transcribe_stream()` overrides this default. [HF-ParakeetV3]

3. **Whisper hallucinations are mechanistically explained and concentrated**: Top-2 phrases account
   for 35% of all non-speech hallucinations; top-10 account for >50%. Root cause: 3 of 20 decoder
   heads responsible for >75% of non-speech hallucinations — `vad_filter=True` alone does not
   eliminate them. [Baranski2025, Wang2025]

4. **Empty output is tolerable; hallucination is dangerous**: A model returning "" on a 0.5 s clip
   triggers a clarification; a model returning "Thanks for watching" causes a silent wrong action.
   Track `is_empty` and `is_hallucination` as separate flags per duration stratum. [Tay2026]

5. **Granite uses accumulate-then-transcribe (single model.generate() call)**: No VAD gate, no
   intermediate chunking. This structurally avoids the VAD false-firing that disqualified Whisper.
   Confirmed by HuggingFace Transformers API documentation. [HF-GraniteDoc]

6. **VAD-misfiring is the Whisper failure mechanism to confirm**: faster-whisper exposes
   `no_speech_probability` per clip. Log this value; if empty outputs on Whisper turbo correlate
   with `no_speech_probability > 0.6` [Radford2022], the mechanism is confirmed.

7. **Granite 4.1 2B achieves 5.33% mean WER on OpenASR Leaderboard** (top position as of 2026).
   RTFx ~231 on H100. t0012 measured 249 ms p50 — consistent with ~4.3 ms/s of audio. The NAR
   variant (RTFx ~1820) is a future latency mitigation but requires Flash Attention. [MindStudio-Granite41]

8. **BCa bootstrap with speaker-level blocks required for significance testing**: Ordinary
   utterance-level bootstrap gives 41.2% CI coverage (vs. 95% nominal) on correlated sets.
   Minimum detectable WER difference at n≈50 per stratum is ±5–8 WER points. [Liu2020]

9. **Keyword precision and recall can diverge from WER under context conditioning**: Granite's
   keyword prompt (31 domain terms) acts as local-context oracle; Parakeet's GPU-PB boosting
   with 66 casing variants may suffer precision loss from distractors. Report separately.
   [Durmus2026]

10. **Use transcribe_stream() for all three models — not direct model.transcribe() calls**: The
    failure modes are only reproducible via the production streaming path. brainpowa-realtime-api
    has no public docs; read `base.py` and `parakeet.py` directly during implementation.

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: Duration-stratified empty/hallucination rate benchmark

Run all three models via `STTAdapter.transcribe_stream()` on synthetic clips at 0.5 s, 1.0 s,
1.5 s, 2.0 s, 2.5 s, 3.0 s bins (real audio trimmed from gold-92 sources). Track `is_empty` and
`is_hallucination` per bin separately. For Whisper, log `no_speech_probability` to confirm VAD
misfiring. This directly answers whether Granite avoids Whisper's failure mode.

### Approach 2: Hallucination detection using BoH top-30 list

Use the public Bag of Hallucinations CSV from `DSP-AGH/ICASSP2025_Whisper_Hallucination` as the
pattern reference for `is_hallucination`, making detection logic citable and reproducible. The
patterns listed in the task description ("Thanks for watching", "Subscribe", "[Music]") are a
subset of the BoH top-30. Aho-Corasick matching is computationally negligible.

### Approach 3: BCa bootstrap with speaker-level blocks for all significance claims

With n≈50 synthetic clips per stratum and 93 gold-92 clips, use BCa bootstrap with B=1,000
replicates and speaker-level blocks. Report 95% CIs on WER and entity accuracy for all
comparisons. Differences below ±5–8 WER points are not statistically distinguishable at this
sample size — state this explicitly in the answer asset rather than overclaiming significance.

## Reusable Code / Assets

- `tasks/t0002_baseline_evaluation/` — gold-92 benchmark clips, evaluation harness baseline
- `tasks/t0012_whisper_parakeet_granite_streaming/` — STTAdapter implementations for all three
  models; latency measurement harness; gold-92 entity accuracy results (Granite 41.1%, Parakeet
  23.2%, Whisper 42.0%)
- `tasks/t0003_literature_review_entity_stt/assets/paper/` — downloaded paper PDFs for Tay2026,
  Kudlur2026, Durmus2026
- `tasks/t0002_baseline_evaluation/assets/paper/` — downloaded PDFs for Liu2020, Radford2022

## Key Papers (top 5, with finding most relevant to this task)

- **Tay 2026** — WildASR: short utterances achieve 38–74% WER and 68.4% semantic hallucination
  rate on commercial systems; introduces HER as a first-class metric separate from WER.
- **Baranski 2025** — ICASSP: Whisper non-speech hallucination top-2 phrases = 35% of all
  hallucinations; BoH post-processing CSV publicly available for citable detection logic.
- **Wang 2025** — Calm-Whisper: 3 of 20 decoder heads cause >75% of non-speech hallucinations;
  >80% reduction achievable — confirms `vad_filter` alone is insufficient.
- **Radford 2022** — Whisper: documents `no_speech_threshold=0.6` VAD heuristic that misfires on
  sub-2 s buffers — the confirmed mechanism for Whisper's short-clip failure.
- **Liu 2020** — Blockwise bootstrap: ordinary bootstrap CI coverage collapses to 41.2% on
  correlated ASR sets; speaker-level blockwise bootstrap required for gold-92.

## Risks Flagged in Research

- **Granite empty output on sub-1 s clips**: 5 Q-Former acoustic embeddings may be insufficient
  for reliable LLM decoding. Empirically unknown until inference run; monitor for empty transcripts
  in the 0.5 s bin.
- **Parakeet degenerate single-chunk for sub-2 s clips**: NeMo default chunk_secs=2 means all
  synthetic bins 0.5–1.5 s hit a single-chunk edge case. Confirm whether brainpowa adapter
  overrides this before interpreting results.
- **No paper directly evaluates Granite 4.1 2B or Parakeet TDT 0.6b-v3 on sub-3 s clips**:
  All architectural hypotheses must be empirically validated — do not treat them as proven.
- **Granite 6× latency overhead (249 ms vs Parakeet 40 ms)**: Both are within the 800 ms p50
  constraint, but report absolute milliseconds per stratum to confirm short clips do not
  unexpectedly increase latency due to HuggingFace Transformers fixed overhead.
- **NeMo streaming bugs in v3** (NeMo-Issue14714, NeMo-Issue15143): Timestamp and word-confidence
  mismatches in NeMo's streaming scripts; may affect the ParakeetSTT adapter if it accesses
  word-level confidence from the NeMo API.
- **Synthetic TTS clips underestimate real failure rates by 5.9×** [Tay2026]: Use real audio
  trimmed from gold-92, not TTS-generated clips, to avoid underestimating failure rates.

## Full Detail Available In

- `tasks/t0014_granite_short_clip_robustness/research/research_papers.md` — 6 papers cited (19
  reviewed)
- `tasks/t0014_granite_short_clip_robustness/research/research_internet.md` — 15 sources cited
  (12 searches, 7 deep fetches)
- `tasks/t0014_granite_short_clip_robustness/research/research_code.md` — (not generated — step
  skipped)
