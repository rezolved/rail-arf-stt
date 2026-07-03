---
spec_version: "2"
answer_id: "parakeet-unified-biasing-improvement"
answered_by_task: "t0019_parakeet_biasing_improvement"
date_answered: "2026-07-02"
---

## Question

How can GPU-PB biasing quality for parakeet-unified-en-0.6b on the gold-92 benchmark be improved
beyond the t0017 biased baseline (EA-DV 34.8%), and which approach should ship to
brainpowa-realtime-api production?

## Answer

Neither decode-time GPU-PB approach improves biasing: a hyperparameter sweep (alpha 1.0-3.0,
depth_scaling 2.0-4.0) is a null result — near-default values move nothing and far-from-default
values wreck WER by 20-27 absolute points from over-boosting, and phrase-list expansion with
phonetic surface-form variants is also a null result, producing byte-identical transcripts (0.000
delta on every metric). The dominant failure ("Rezolve" transcribed as "Resolve" in 25/93 clips) is
acoustic, not a boosting-tree coverage gap, so boosting cannot fix it. A deterministic post-decode
string-replacement pass — using the `stt_replacements` channel that already exists in
`brainpowa-realtime-api` (separate from GPU-PB boosting) but currently ships with an empty default
(`{}`, no hardcoded brand map) — raised EA-DV from 34.8% to 95.7% and even slightly improved WER
(11.0% → 8.5%). Recommendation: populate a deployment-level default `stt_replacements` map with the
Rezolve-domain alias list below; do not invest further in GPU-PB hyperparameter tuning or phrase-list
engineering for this failure mode.

## Sources

* Task: `t0017_parakeet_biasing_buffer_replacement`
* Task: `t0019_parakeet_biasing_improvement`
