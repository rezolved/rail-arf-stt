"""Domain vocabulary constants for vocabulary biasing experiment."""

from __future__ import annotations

DOMAIN_VOCAB: list[str] = [
    "Rezolve",
    "Rezolve Ai",
    "NASDAQ",
    "brainpowa",
    "Agentic",
    "Brain Checkout",
    "Brain Commerce",
    "Purchase Suite",
    "GroupBy",
    "Bluedot",
    "ViSenze",
    "Smartpay",
    "Subsquid",
    "CrownPeak",
    "Hallucinations",
    "Zero Hallucinations",
    "Dan Wagner",
    "Arthur Yao",
    "Richard Burchill",
    "Crispin Lowery",
    "Salman Ahmad",
    "Sauvik Banerjjee",
    "Mark Turner",
    "Peter Vesco",
    "Urmee Khan",
    "Anthony Sharp",
    "David Wright",
    "Steve Perry",
    "Derek Smith",
    "Justin King",
    "Christian Angermayer",
]

INITIAL_PROMPT: str = ", ".join(DOMAIN_VOCAB)
