"""Constants for t0006_nemotron_3_5_benchmark."""

from __future__ import annotations

MODEL_ID: str = "/home/azureuser/nemotron-model/nemotron-3.5-asr-streaming-0.6b.nemo"
STREAMING_CHUNK_SECONDS: float = 1.12  # matches published RTF benchmarks
SAMPLE_RATE: int = 16_000
WARMUP_CLIPS: int = 3

# Same 31-term domain vocabulary as t0004
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
