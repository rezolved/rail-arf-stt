---
spec_version: "2"
predictions_id: "parakeet-unified-biasing-best-hyperparam-phrase-expansion"
documented_by_task: "t0019_parakeet_biasing_improvement"
date_documented: "2026-07-02"
---

## What produced these predictions

Baseline predictions were inspected clip-by-clip to find every domain-vocab term with an observed
miss: "Rezolve"/"Rezolve Ai" (25/17 misses out of 93), "brainpowa" (1 miss, -> "brain power"), and
"agentic commerce" (1 miss, -> "Gentic commerce"). `code/phrase_expansion.py` adds 15 additional
**correct-spelling** surface-form variants for these terms (e.g. `REZOLVE`, `Re-zolve`, `Rezolv`,
`brain-powa`) to the 72 casing-expanded phrases, producing an 87-phrase GPU-PB boosted list. This
deliberately does not add the *wrong* spelling ("Resolve") to the boost list, since boosting the
wrong word would reinforce it — GPU-PB biases the decoder toward emitting listed phrases, it does
not substitute wrong output after decoding (that is the separate post-hoc-replacement mechanism).

Decoded with `nvidia/parakeet-unified-en-0.6b`, `greedy_batch` strategy, using the sweep-selected
(= default) hyperparameters `alpha=1.0, depth_scaling=2.0`.

## Dataset

All 93 clips of gold-92 (`t0001_stt_benchmark`, `assets/dataset/stt-benchmark-gold-92`).

## Result: null

WER 11.03%, EA 23.44%, EA-DV 34.78% — **byte-identical** to the baseline predictions
(`parakeet-unified-biasing-baseline`) down to full floating-point precision on the computed metrics.
None of the 15 added surface-form variants changed a single transcript. This indicates the GPU-PB
boosting tree already reaches whatever BPE-decode paths it can from the base phrase forms; the
"Rezolve" -> "Resolve" failure is an acoustic-confidence ceiling upstream of the boosting tree, not
a phrase-list coverage gap. See `results/phrase_expansion_full93.json` for the raw comparison and
the `parakeet-unified-biasing-improvement` answer asset for the full analysis, including the
post-hoc string-replacement approach that did work (EA-DV 34.8% -> 95.7%).
