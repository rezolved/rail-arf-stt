"""Magic strings and tunables for t0025 data-prep and training code."""

from __future__ import annotations

BRAND_TERMS: list[str] = ["Rezolve", "brainpowa", "Rezolve AI"]
OVERSAMPLE_FACTOR: int = 3

# gold-92 clip_ids pulled into val_v6 from the gold-92-inside-train_v5 overlap set (see
# build_manifests_v6.py docstring). Selected from the 17 brand-bearing clips in that overlap:
# all 6 error_cases (includes the project's only brainpowa mention in that pool) plus 2
# production clips, skipping clean_voices (TTS-persona reads of the same production-style
# questions, already well represented in train).
VAL_ADDITION_CLIP_IDS: list[str] = [
    "error_en_0092",
    "error_en_0010",
    "error_en_0014",
    "error_en_0018",
    "error_en_0020",  # only brainpowa mention among the candidates
    "error_en_0011",
    "b86db565-531a-484d-8b6f-07f460b0b36b_turn0",
    "da47fc8f-7d5b-4cdd-8f5d-2bbb3b524590_turn2",
]
