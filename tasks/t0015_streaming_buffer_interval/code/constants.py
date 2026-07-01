"""Constants for t0015_streaming_buffer_interval."""

SAMPLE_RATE: int = 16_000
BYTES_PER_SAMPLE: int = 2  # int16 PCM-16

# Production chunk size (32 kB) — how audio is delivered in WebSocket stream
CHUNK_SIZE_BYTES: int = 32_768

# Buffer extraction intervals to benchmark (milliseconds → bytes at 16kHz int16)
# 500ms  = 16000 samples/s × 0.5s × 2 bytes = 16000 bytes
# 750ms  = 16000 × 0.75 × 2 = 24000 bytes
# 1000ms = 16000 × 1.0 × 2 = 32000 bytes
BUFFER_INTERVALS_MS: list[int] = [500, 750, 1000]
INTERVAL_BYTES: dict[int, int] = {
    500: 16_000,
    750: 24_000,
    1000: 32_000,
}

# Model identifiers
MODEL_PARAKEET_TDT: str = "parakeet-tdt-0.6b-v3"
MODEL_PARAKEET_UNIFIED: str = "parakeet-unified-en-0.6b"
MODEL_MULTITALKER: str = "multitalker-parakeet-streaming-0.6b-v1"
MODEL_GRANITE: str = "granite-speech-4.1-2b"

# HuggingFace model IDs
HF_PARAKEET_TDT: str = "nvidia/parakeet-tdt-0.6b-v3"
HF_PARAKEET_UNIFIED: str = "nvidia/parakeet-unified-en-0.6b"
HF_MULTITALKER: str = "nvidia/multitalker-parakeet-streaming-0.6b-v1"

# Granite model path on the remote machine
REMOTE_GRANITE_MODEL: str = "/home/azureuser/granite-model/granite-speech-4.1-2b"
GRANITE_MAX_NEW_TOKENS: int = 256
GRANITE_WARMUP_CLIPS: int = 2

# Parakeet GPU-PB boosting parameters (same as t0012/t0014 production)
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

# Granite keyword prompt — same as t0014 best variant
GRANITE_KEYWORD_PROMPT: str = "transcribe the speech to text. Keywords: " + ", ".join(DOMAIN_VOCAB)

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
