"""Constants for t0026_biasing_on_finetune_ablation.

`DOMAIN_VOCAB` is copied verbatim from `tasks/t0021_parakeet_finetune_vs_biasing/code/constants.py`.
`TARGET_BRANDS`, `BRAND_VARIANTS`, `PHONETIC_PATTERNS`, `EXACT_PATTERNS`, and `TERM_FILTER` are
copied verbatim from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 85-98. Per this task's
`plan/plan.md` Approach section (REQ-10), these are copies, not cross-task imports — the project has
no registered `library` asset for them yet.
"""

import re

# Rezolve domain vocabulary — same list as t0015 for metric consistency
DOMAIN_VOCAB: list[str] = [
    "Rezolve",
    "Rezolve Ai",
    "NASDAQ",
    "brainpowa",
    "brainpowa AI",
    "AI Foundry",
    "Shopify Plus",
    "Adobe Commerce",
    "Salesforce Commerce Cloud",
    "conversational AI",
    "voice AI",
    "agentic AI",
    "agentic commerce",
    "omnichannel",
    "multimodal",
    "product recommendation",
    "intent detection",
    "entity recognition",
    "product catalog",
    "inventory",
    "fulfillment",
    "shopping assistant",
    "voice assistant",
    "smart speaker",
    "cross-channel",
    "real-time",
    "low-latency",
    "NLU",
    "ASR",
    "SKU",
    "E-commerce",
]

TARGET_BRANDS: list[str] = ["Rezolve", "brainpowa"]
BRAND_VARIANTS: dict[str, list[str]] = {
    "Rezolve": ["Rezolve", "Rezolve AI", "rezolve"],
    "brainpowa": ["brainpowa", "Brain Powa", "Brain Power", "Brainpowa", "brain powa"],
}
PHONETIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "Rezolve": re.compile(r"\bresolve\b|\brezolve\b|\brezolv\b|\bresolved\b", re.I),
    "brainpowa": re.compile(r"\bbrain.?pow|\bbrain.?com|\bbrainpow|\bbraincom|\bbrain pow", re.I),
}
EXACT_PATTERNS: dict[str, re.Pattern[str]] = {
    "Rezolve": re.compile(r"\bRezolve\b"),
    "brainpowa": re.compile(r"\bbrainpowa\b", re.I),
}
TERM_FILTER: re.Pattern[str] = re.compile(r"rezolve|resolve|brainpowa|brain.?pow|brain.?com", re.I)

# Unified-model Pareto-frontier cell selected by t0024 Part A (not re-swept here — see
# `plan/plan.md` REQ-3). Source: tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/
# pareto_unified.json `selected_cell`, confirmed at runtime in `code/run_ablation.py` against the
# live file rather than trusted from this comment alone.
SELECTED_CELL: dict[str, float] = {
    "context_score": 3.0,
    "depth_scaling": 0.5,
    "alpha": 1.5,
}
