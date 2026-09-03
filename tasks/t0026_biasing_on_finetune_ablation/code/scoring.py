"""Brand-scoring and WER helpers for t0026_biasing_on_finetune_ablation.

Copied verbatim from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 186-240
(`label_brand`, `brand_in_ref`, `wer`, `_expand_casing_variants`, `build_phrase_list`), per this
task's `plan/plan.md` Approach section (REQ-10). Imports `DOMAIN_VOCAB`/`BRAND_VARIANTS` from this
task's own `code/constants.py` rather than from t0023.
"""

import re

from tasks.t0026_biasing_on_finetune_ablation.code.constants import (
    BRAND_VARIANTS,
    DOMAIN_VOCAB,
    EXACT_PATTERNS,
    PHONETIC_PATTERNS,
    TARGET_BRANDS,
)

_WORD_PATTERN: re.Pattern[str] = re.compile(r"[a-z0-9']+")


def label_brand(hyp: str, brand: str) -> str:
    if EXACT_PATTERNS[brand].search(hyp):
        return "EXACT"
    if PHONETIC_PATTERNS[brand].search(hyp):
        return "PHONETIC"
    return "GARBAGE"


def brand_in_ref(ref: str) -> str | None:
    """Whether the ground-truth reference mentions a target brand.

    Adaptation from t0023's verbatim `brand_in_ref` (REQ-10 copy) — t0023's version also falls
    back to `PHONETIC_PATTERNS` on the reference text, which is correct on gold-92 (no collisions)
    but produces false positives on `clean_eval_v2`: 11 clips mention "Brain Commerce" (a real,
    distinct Rezolve product), which the `brainpowa` phonetic pattern (`\\bbrain.?com`) matches,
    inflating the brand-clip count from the dataset's documented 43 (`task_description.md`
    "Eval set": 40 Rezolve + 3 brainpowa) to 54. Phonetic matching belongs on ASR *hypotheses*
    (`label_brand`, unchanged below) where it detects a mis-transcription — not on the
    ground-truth reference, which either contains the brand term verbatim or does not. Restricting
    this function to `EXACT_PATTERNS` reproduces the dataset's documented 43/48 split exactly.
    """
    for brand in TARGET_BRANDS:
        if EXACT_PATTERNS[brand].search(ref):
            return brand
    return None


def wer(ref: str, hyp: str) -> float:
    r: list[str] = _WORD_PATTERN.findall(ref.lower())
    h: list[str] = _WORD_PATTERN.findall(hyp.lower())
    if len(r) == 0 and len(h) == 0:
        return 0.0
    if len(r) == 0:
        return 1.0
    d: list[int] = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        prev, d[0] = d[0], i
        for j, hw in enumerate(h, 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (rw != hw))
            prev = cur
    return d[len(h)] / len(r)


def _expand_casing_variants(phrases: list[str]) -> list[str]:
    """Mirror prod: expand each phrase to {as-given, lower, Capitalized}, deduped."""
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant != "" and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return out


def build_phrase_list() -> list[str]:
    phrases: list[str] = list(DOMAIN_VOCAB)
    for variants in BRAND_VARIANTS.values():
        for v in variants:
            if v not in phrases:
                phrases.append(v)
    # Mirror prod: expand each phrase to casing variants before building boosting tree
    return _expand_casing_variants(phrases)
