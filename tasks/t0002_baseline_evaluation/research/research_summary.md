# Research Summary — t0002_baseline_evaluation

## Key Findings (top 10 insights directly actionable for this task)

1. **Use `faster-whisper` on Apple M5** — CTranslate2 backend with `device="cpu",
   compute_type="int8"` gives ~4x speedup over `openai-whisper`. Budget ~15–40 min for 93 clips on
   M5 CPU. Always pass `language="en"` to prevent accent-misclassification failure mode.

2. **Deepgram SDK breaking change** — use `deepgram-sdk>=3.0` with
   `DeepgramClient().listen.v1.media.transcribe_file()`. Legacy `listen.prerecorded` client is
   deprecated. Set `smart_format=True` and `punctuate=True` for normalised output. Cost: ~$0.09
   total for 93 clips at $0.0043/min.

3. **`error_en_0005` has Cyrillic ground truth `"ы"`** — an annotation error. Include in the full
   run for completeness, log a warning, note it in `metadata.json`, and verify it does not
   disproportionately skew aggregate metrics. Flag it in the predictions asset.

4. **Use `ground_truth.jsonl` for references, not `gold_set.jsonl`** — the `ground_truth.jsonl`
   file is the canonical reference; `gold_set.jsonl`'s `ground_truth` field has normalisation
   inconsistencies. Never use `gold_set.jsonl`'s `production` or `whisper` columns as baselines
   — re-run inference fresh.

5. **Entity accuracy definition (Caubrière et al., 2020)** — an entity span is correct only if all
   constituent words exactly match after normalisation (all-or-nothing, no partial credit).
   `entity_accuracy_gold92 = 1 - EER`. Compute on lowercased, punctuation-stripped text.

6. **BCa bootstrap** — `scipy.stats.bootstrap(method='BCa', n_resamples=10_000, random_state=42)`.
   For the paired Whisper vs. Deepgram significance test use `paired=True`. Add fallback to
   `method='percentile'` if BCa returns NaN (all scores identical — degenerate distribution).

7. **Speaker correlation in gold-92** — 6 named speakers contribute 5–7 clips each in the
   `clean_voices` source (~40 clips total). Standard i.i.d. BCa is biased for this subset per Liu
   & Peng (2020). Document the bootstrap method choice (standard vs. blockwise) in `metadata.json`.
   For the full 93-clip primary result, standard BCa is an acceptable approximation.

8. **Latency measurement** — use `time.perf_counter()` around each API/inference call; do NOT use
   `response.metadata.duration` (that is audio duration, not processing time). Deepgram latency
   includes network round-trip; Whisper latency is local-only — the two are not directly comparable.
   Record hardware and package versions in `metadata.json`.

9. **Known entity failure patterns** — "Rezolve AI" → "resolve AI" / "Hezos"; "brainpowa" →
   "brain power"; "20-F" → "20f"; comma-insertion in "Salesforce Commerce Cloud" by accented
   speakers. These patterns confirm entity accuracy will diverge substantially from full-transcript
   WER, justifying the separate `entity_accuracy_gold92` and `action_critical_wer_gold92` metrics.

10. **Expected WER range** — Whisper Large v3: 2.7%/5.2% WER (LibriSpeech clean/other), but 19.18%
    on non-native spontaneous English (LearnerVoice); expect gold-92 Whisper WER 8–20%. Deepgram
    Nova-2: 8.4% median across real-world domains (vendor benchmark). Both will likely be higher on
    accented IR domain audio.

## Best Approaches (top 3 recommended implementation approaches from research)

### Approach 1: faster-whisper for local Whisper inference

Use `faster-whisper` (`WhisperModel("large-v3", device="cpu", compute_type="int8")`) rather than
`openai-whisper` or the `transformers` pipeline. On Apple M5 (no NVIDIA GPU), CTranslate2 INT8
quantization cuts inference time by ~4x and RAM from ~10 GB to ~2.5 GB without accuracy loss.
Always pass `language="en"` to the `transcribe()` call to prevent misclassification of accented
speech as a non-English language — a documented failure mode.

### Approach 2: jiwer for WER with shared normalisation

Use `jiwer.process_words` (batch, all 93 pairs at once) to get word-level alignment for both
full-transcript and entity-span WER. Define one `normalise(text)` function (lowercase + strip
punctuation) called on both reference and hypothesis — inconsistent normalisation is the most
common source of inflated/deflated WER. For action-critical WER, filter the aligned word list to
entity-span tokens only before computing substitution/deletion/insertion counts.

### Approach 3: scipy BCa bootstrap with NaN guard

Compute all five metric CIs with `scipy.stats.bootstrap(method='BCa', n_resamples=10_000,
random_state=42)`. Run the paired significance test for `entity_accuracy_gold92` using
`paired=True`. Guard against degenerate distributions (all scores identical → BCa NaN) by falling
back to `method='percentile'` with a logged warning. This handles `error_en_0005` and any
trivially easy or impossible clips without crashing.

## Reusable Code / Assets

- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl` — 93-record
  annotation file; use `source` and `clip_id` for stratification only
- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl` —
  canonical references for all metric computation (authoritative)
- `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio/` — 93 WAV files,
  DVC-tracked (~58 MB); must run `dvc pull` to materialise before inference

No shared Python code exists in this project yet — all five modules must be written from scratch.

## Key Papers (top 5, with finding most relevant to this task)

- **Caubrière et al. 2020** — Defines entity error rate (EER = 1 − entity recall) with
  all-or-nothing exact-match span criterion; methodological reference for `entity_accuracy_gold92`.
- **Liu & Peng 2020** — Standard i.i.d. bootstrap is biased when ASR utterances share speakers;
  blockwise bootstrap by speaker session is the correct alternative for correlated evaluation sets.
- **Radford et al. 2023** — Foundational Whisper paper; published WER benchmarks (2.7% LibriSpeech
  test-clean) needed for the compare-literature step (step 13) — add via `add-paper` before that
  step.
- **Peng et al. 2025** — Whisper Large v3 achieves 19.18% WER on non-native spontaneous English
  (LearnerVoice), calibrating expected gold-92 performance on accented speakers.
- **Ashkenazi et al. 2024 (WhisperNER)** — Joint ASR+NER achieves near-perfect entity recall under
  clean conditions; contextualises the upper bound this baseline should be compared against in later
  tasks.

## Risks Flagged in Research

- **`error_en_0005` Cyrillic ground truth `"ы"`** — include with warning; log anomaly in
  `metadata.json`; check whether it disproportionately skews aggregate metrics.
- **DVC pull required before inference** — audio files are not in git; verify exactly 93 WAV files
  present after pull before running any inference script.
- **Existing `gold_set.jsonl` hypotheses must not be used** — `production` column is uncontrolled
  live-session Nova-2; `whisper` column is v2 not v3. Re-run inference fresh.
- **Latency figures are not comparable** — Deepgram latency is network-bound; Whisper is
  hardware-bound. Document this in `metadata.json` and results tables.
- **Speaker correlation biases BCa** — 6 named speakers × 5–7 clips each in clean-voice subset.
  Document standard vs. blockwise bootstrap decision in `metadata.json`.
- **No peer-reviewed Deepgram paper** — all Nova-2 WER numbers are from vendor white papers;
  treat with caution in the compare-literature step.

## Full Detail Available In

- `tasks/t0002_baseline_evaluation/research/research_papers.md` — 0 papers (corpus empty at time
  of writing; partial status; `t0003_literature_review_entity_stt` will fill this)
- `tasks/t0002_baseline_evaluation/research/research_internet.md` — 16 sources
- `tasks/t0002_baseline_evaluation/research/research_code.md` — 1 task reviewed (t0001)
