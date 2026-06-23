---
spec_version: "3"
task_id: "t0002_baseline_evaluation"
step_number: 5
step_name: "research-internet"
status: "completed"
started_at: "2026-06-23T08:11:30Z"
completed_at: "2026-06-23T08:17:00Z"
---
## Summary

Conducted 12 web searches across 3 passes covering Deepgram Nova-2 API documentation, Whisper Large
v3 inference, BCa bootstrap methodology, and STT evaluation frameworks. Resolved all four gaps
identified in research_papers.md. Found 4 papers for corpus addition. Identified the complete
evaluation toolchain: faster-whisper for local inference, deepgram-sdk>=3.0 for API calls, jiwer for
WER/entity-span computation, and scipy.stats.bootstrap(method='BCa') for significance testing.

## Actions Taken

1. Ran 12 search queries across Deepgram docs, Hugging Face, arXiv, ACL Anthology, PyPI, and GitHub.
2. Resolved gap: Deepgram Nova-2 median WER 8.4%, Whisper Large v3 2.7%/5.2% on LibriSpeech, 19.18%
   WER on non-native English.
3. Resolved gap: scipy.stats.bootstrap(method='BCa', n_resamples=10000, paired=True) confirmed as
   the standard approach.
4. Discovered 4 papers for corpus addition (Whisper, blockwise bootstrap, NER-from-speech,
   WhisperNER).
5. Verified research_internet.md with verify_research_internet — PASSED, 0 errors, 0 warnings.

## Outputs

* `tasks/t0002_baseline_evaluation/research/research_internet.md` — 4 papers in Discovered Papers
  section

## Issues

No IR/ecommerce STT domain papers exist in the literature — this is expected and documented. Note
for planning: user has Apple M5 — prefer mlx-whisper or faster-whisper with CoreML/Metal backend
over remote GPU. All 93 clips can be processed locally in under 5 minutes.
