# t0022 — GPU-PB Biasing Diagnostic: parakeet-unified brand recognition failure

## Goal

Determine **why** GPU-PB context biasing does not improve "Rezolve" and "brainpowa" recognition in
parakeet-unified-en-0.6b, and classify the failure as either:

- **config-fixable** — wrong decoding strategy, wrong params, phrase-list mismatch
- **fundamental** — encoder cannot represent the brand acoustically; boosting alone cannot fix it

## Model

`nvidia/parakeet-unified-en-0.6b` (EncDecHybridRNNTCTCBPEModel, NeMo 3.1.0).
Loaded from HuggingFace; no local .nemo checkpoint required.

## Eval set

29 golden_candidates clips that contain "Rezolve" or "brainpowa" (from
`rail-benchmarks/realtime-voice-benchmark/data/raw/production_logs/golden_candidates.jsonl`).
Plus ~10 brand-free neutral clips from the same file for over-boosting detection.
Do NOT use gold-92 for training or tuning — it remains held-out.

## Key phrases source

`tasks/t0017_parakeet_biasing_buffer_replacement/code/constants.py` → `DOMAIN_VOCAB`.
No external file; list passed in-memory via `greedy.boosting_tree.key_phrases_list`.

## Diagnostic steps (single script: `code/diagnostic.py`)

### 1. Tokenization probe
For each brand in `["Rezolve", "brainpowa"]` + full DOMAIN_VOCAB:
- Print SentencePiece subword split and token IDs from `asr_model.tokenizer`
- Flag: splits into >3 fragments, or fragments are high-frequency English tokens

### 2. Decoding matrix (4 configs, same eval set)
| Config | Strategy | Boosting |
|--------|----------|---------|
| (a) greedy-no-boost | greedy_batch | — |
| (b) greedy-boost | greedy_batch | GPU-PB, current params |
| (c) beam-no-boost | beam (alsd) | — |
| (d) beam-boost | beam (alsd) + boosting_tree | GPU-PB params |

Note: NeMo 3.1.0 parakeet-unified uses `alsd` beam, not `malsd_batch`.
Boosting for beam: `beam.boosting_tree.*` (mirror greedy structure — verify against installed NeMo).

### 3. Per-brand verdict
For each brand occurrence, label each config output:
- `EXACT` — matches reference brand
- `PHONETIC` — recognizable near-miss ("Resolve", "brain power", "Brain Commerce")
- `GARBAGE` — unrelated or dropped

Also test orthographic variants in phrase list: `["brainpowa", "Brain Powa", "Brain Power", "Brainpowa"]`.

### 4. Param sweep (config d only)
Grid: `context_score ∈ {1, 2, 4}`, `depth_scaling ∈ {1, 2, 3}`, `alpha ∈ {1.0, 2.0, 3.0}`.
Per cell: brand recognition rate on brand clips + WER on neutral clips.

### 5. Summary verdict
Print table: brand recognition rate per config (a)–(d), greedy→beam delta,
dominant failure label, best sweep cell, neutral WER regression.
Final line: `config-fixable` or `fundamental`.

## Constraints

- GPU if available; CPU fallback acceptable (small eval set)
- Write all outputs to `tasks/t0022_gpu_pb_diagnostic/results/`
- Do NOT modify production configs
- Do NOT train on or tune against gold-92

## Expected outputs

- `results/tokenization_probe.txt`
- `results/decoding_matrix.jsonl` (per-clip, per-config)
- `results/brand_verdicts.jsonl`
- `results/param_sweep.jsonl`
- `results/summary.md` (human-readable verdict)
