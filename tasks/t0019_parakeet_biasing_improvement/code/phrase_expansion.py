"""Phonetic/surface-form phrase-list expansion for GPU-PB boosting (t0019 Step 4).

Baseline-predictions inspection (data/hyperparam_top2/alpha1.0_depth2.0/predictions.jsonl, 93
clips, alpha=1.0/depth_scaling=2.0 — the config carried forward since the hyperparam sweep was a
null result) found consistent misses:
  - "Rezolve" / "Rezolve Ai": 25 / 17 misses out of 93 clips, always transcribed as "Resolve AI".
  - "brainpowa": 1 miss, transcribed as "brain power".
  - "agentic commerce": 1 miss, transcribed as "Gentic commerce" (dropped leading syllable).

NeMo GPU-PB boosting biases the decoder toward emitting phrases already in the key_phrases_list —
it does not substitute wrong output after the fact (that is the separate post-hoc-replacement
approach, Step 5 / posthoc_replacement_check.py). So this expansion adds MORE surface-form/BPE-
segmentation variants of the CORRECT terms (alternate casing, hyphenation, spacing) to give the
boosting tree more prefix paths that converge on the right spelling. It deliberately does NOT add
the wrong spelling ("Resolve") to the phrase list, since boosting the wrong word would reinforce it.
"""

from __future__ import annotations

# Extra surface-form variants per term, beyond the casing-only variants already produced by
# expand_casing_variants() in t0017's run_parakeet_buffer_sweep.py. Targets the terms with observed
# misses in the baseline run.
EXTRA_SURFACE_VARIANTS: dict[str, list[str]] = {
    "Rezolve": ["REZOLVE", "Re-zolve", "RE-ZOLVE", "Rezolv", "Re zolve"],
    "Rezolve Ai": ["REZOLVE AI", "Re-zolve AI", "Rezolve A.I.", "Re zolve AI"],
    "brainpowa": ["BRAINPOWA", "brain-powa", "Brain-Powa", "brain powa"],
    "agentic commerce": ["Agentic Commerce", "a-gentic commerce", "AGENTIC COMMERCE"],
}


def expand_with_surface_variants(phrases: tuple[str, ...]) -> tuple[str, ...]:
    """Append EXTRA_SURFACE_VARIANTS entries to an already casing-expanded phrase tuple.

    `phrases` is expected to be the output of expand_casing_variants(DOMAIN_VOCAB) from
    t0017's run_parakeet_buffer_sweep.py. Dedupes and preserves order.
    """
    out: list[str] = list(phrases)
    seen: set[str] = set(phrases)
    for extras in EXTRA_SURFACE_VARIANTS.values():
        for variant in extras:
            if variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)
