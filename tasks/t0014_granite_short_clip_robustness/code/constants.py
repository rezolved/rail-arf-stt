"""Constants for t0014_granite_short_clip_robustness."""

SAMPLE_RATE: int = 16_000
BYTES_PER_SAMPLE: int = 2  # int16 PCM-16
CHUNK_SIZE_BYTES: int = 32_768  # 32 kB — production WebSocket chunk size

# Duration bins for short-clip synthesis (seconds)
DURATION_BINS: list[float] = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
CLIPS_PER_BIN: int = 7  # target: 7 × 6 = 42 clips (plus 2 edge cases = 44 total)

# Stratum definitions for stratified analysis
STRATA_KEYS: list[str] = ["lt_1s", "1_to_2s", "2_to_3s", "3_to_5s", "5_to_10s", "gt_10s"]

# Model identifiers (for display)
MODEL_WHISPER: str = "whisper_turbo"
MODEL_PARAKEET: str = "parakeet_tdt"
MODEL_GRANITE: str = "granite_speech"
MODEL_LABELS: dict[str, str] = {
    MODEL_WHISPER: "Whisper turbo",
    MODEL_PARAKEET: "Parakeet TDT 0.6b",
    MODEL_GRANITE: "Granite 4.1 2B",
}

# Remote machine paths
REMOTE_GRANITE_MODEL: str = "/home/azureuser/granite-model/granite-speech-4.1-2b"
REMOTE_PARAKEET_MODEL: str = "/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3"

# 31-term domain vocabulary (identical to t0012)
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

WHISPER_INITIAL_PROMPT: str = ", ".join(DOMAIN_VOCAB)
GRANITE_KEYWORD_PROMPT: str = "transcribe the speech to text. Keywords: " + ", ".join(DOMAIN_VOCAB)

# BoH fallback patterns (used when CSV download fails)
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

# Whisper config
WHISPER_MODEL_SIZE: str = "turbo"
WHISPER_COMPUTE_TYPE: str = "float16"
WHISPER_BEAM_SIZE: int = 1
WHISPER_VAD_FILTER: bool = True
WHISPER_TEMPERATURE: float = 0.0
WHISPER_NO_SPEECH_THRESHOLD: float = 0.6

# Parakeet config
PARAKEET_BOOSTING_ALPHA: float = 1.0
PARAKEET_CONTEXT_SCORE: float = 1.0
PARAKEET_DEPTH_SCALING: float = 2.0
PARAKEET_USE_BPE_DROPOUT: bool = True

# Granite config
GRANITE_MAX_NEW_TOKENS: int = 256
GRANITE_WARMUP_CLIPS: int = 3

# Production latency constraint (seconds)
PRODUCTION_LATENCY_CONSTRAINT: float = 0.800

# BCa bootstrap
BOOTSTRAP_REPLICATES: int = 1_000
BOOTSTRAP_CI_LEVEL: float = 0.95

# Rejection threshold
MIN_SUCCESS_RATE: float = 0.8
