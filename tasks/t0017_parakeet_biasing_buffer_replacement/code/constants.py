"""Constants for t0017_parakeet_biasing_buffer_replacement.

Fresh biased benchmark of parakeet-tdt-0.6b-v3 vs parakeet-unified-en-0.6b on gold-92 with NeMo
GPU-PB TurboBias, plus a fine streaming buffer sweep (200-1000ms). Mirrors the t0015 harness with an
extended interval grid and only the two Parakeet models in scope.
"""

SAMPLE_RATE: int = 16_000
BYTES_PER_SAMPLE: int = 2  # int16 PCM-16

# Production chunk size (32 kB) — how audio is delivered in the WebSocket stream
CHUNK_SIZE_BYTES: int = 32_768

# Buffer extraction intervals to benchmark (milliseconds -> bytes at 16kHz int16).
# bytes = 16000 samples/s * seconds * 2 bytes/sample.
BUFFER_INTERVALS_MS: list[int] = [200, 300, 350, 500, 750, 1000]
INTERVAL_BYTES: dict[int, int] = {
    200: 6_400,
    300: 9_600,
    350: 11_200,
    500: 16_000,
    750: 24_000,
    1000: 32_000,
}

# Model identifiers
MODEL_PARAKEET_TDT: str = "parakeet-tdt-0.6b-v3"
MODEL_PARAKEET_UNIFIED: str = "parakeet-unified-en-0.6b"

# HuggingFace model IDs
HF_PARAKEET_TDT: str = "nvidia/parakeet-tdt-0.6b-v3"
HF_PARAKEET_UNIFIED: str = "nvidia/parakeet-unified-en-0.6b"

# Parakeet GPU-PB boosting parameters (same as brainpowa production / t0012 / t0015)
PARAKEET_BOOSTING_ALPHA: float = 1.0
PARAKEET_CONTEXT_SCORE: float = 1.0
PARAKEET_DEPTH_SCALING: float = 2.0
PARAKEET_USE_BPE_DROPOUT: bool = True

# 31-term Rezolve domain vocabulary (identical across all tasks)
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

# BoH hallucination fallback patterns
BOH_FALLBACK_PATTERNS: list[str] = [
    "Thanks for watching",
    "Subscribe",
    "[Music]",
    "[Applause]",
    "[Laughter]",
    "Thank you for watching",
    "Thank you.",
    "Please subscribe",
    "Like and subscribe",
    "See you next time",
]

# Minimum success rate before rejection (80%)
MIN_SUCCESS_RATE: float = 0.80

# Cyrillic anomaly clip ID (excluded from entity accuracy)
CYRILLIC_ANOMALY_CLIP: str = "error_en_0005"
