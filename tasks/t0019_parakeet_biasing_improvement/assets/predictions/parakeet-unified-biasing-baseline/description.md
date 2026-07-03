---
spec_version: "2"
predictions_id: "parakeet-unified-biasing-baseline"
documented_by_task: "t0019_parakeet_biasing_improvement"
date_documented: "2026-07-02"
---

## What produced these predictions

`nvidia/parakeet-unified-en-0.6b` loaded via NeMo `ASRModel.from_pretrained()`, decoded with
`greedy_batch` strategy and GPU-PB TurboBias phrase boosting applied through
`model.cfg.decoding.greedy.boosting_tree`. The boosting config uses the production-default
hyperparameters carried over unchanged from `t0017_parakeet_biasing_buffer_replacement`:
`boosting_tree_alpha=1.0`, `context_score=1.0`, `depth_scaling=2.0`, `use_bpe_dropout=True`. The
phrase list is the 31-term Rezolve domain vocabulary expanded into 72 casing variants
(original, lowercase, title-case) via `expand_casing_variants()`.

## Dataset

All 93 clips of the gold-92 STT benchmark (`t0001_stt_benchmark`,
`assets/dataset/stt-benchmark-gold-92`), transcribed in a single non-streaming
`model.transcribe()` call per clip (this task does not sweep buffer intervals — that was already
covered by t0017 and found accuracy-invariant to interval).

## Results

WER 11.03%, Entity Accuracy 23.44%, Entity Accuracy Domain-Vocab (EA-DV) 34.78% — matches the
t0017 biased baseline numbers exactly, confirming this task's harness reproduction is correct. This
is the **control condition** for t0019: the hyperparameter sweep and phrase-list expansion
experiments in this task are compared against these numbers, and both turned out to be null
results (see `t0019` `results/results_summary.md` / the `parakeet-unified-biasing-improvement`
answer asset for the full comparison and the winning post-hoc-replacement approach).

## Known failure mode

25/93 clips mis-transcribe "Rezolve"/"Rezolve Ai" as "Resolve"/"Resolve AI" — this is the dominant
driver of the low EA-DV and was found in this task to be an acoustic-confidence ceiling that GPU-PB
boosting (at any tested hyperparameter setting or phrase-list size) cannot correct.
