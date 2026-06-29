SAMPLE_RATE: int = 16_000
BYTES_PER_SAMPLE: int = 2  # int16 PCM (production WebSocket format)
STREAM_INTERVAL_BYTES: int = 32_000  # ~1 s at 16 kHz mono int16 = 16000 samples

# Whisper config (mirrors brainpowa-realtime-api WhisperSTT production defaults exactly)
# Using HuggingFace transformers — faster-whisper (ctranslate2) has a multi-GPU bug on this host
WHISPER_HF_MODEL_ID: str = "openai/whisper-large-v3-turbo"
WHISPER_DEVICE: str = "cuda:0"
WHISPER_BEAM_SIZE: int = 1
WHISPER_MAX_NEW_TOKENS: int = 200  # prompt=~116 tokens; 116+200=316 < 448 (Whisper limit)

# Parakeet config (mirrors brainpowa-realtime-api production exactly)
PARAKEET_MODEL_LOCAL_DIR: str = "/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3"
PARAKEET_BOOSTING_ALPHA: float = 1.0
PARAKEET_CONTEXT_SCORE: float = 1.0
PARAKEET_DEPTH_SCALING: float = 2.0
PARAKEET_USE_BPE_DROPOUT: bool = True

# Granite config (mirrors t0007 kw-biased best variant)
GRANITE_MODEL_LOCAL_DIR: str = "/home/azureuser/granite-model/granite-speech-4.1-2b"
GRANITE_MAX_NEW_TOKENS: int = 256
GRANITE_PROMPT_BIASED_PREFIX: str = "transcribe the speech to text. Keywords: "
GRANITE_WARMUP_CLIPS: int = 2

# 31-term domain vocab (identical across all tasks)
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

# Whisper initial_prompt: comma-separated domain vocab for decoder steering
WHISPER_INITIAL_PROMPT: str = ", ".join(DOMAIN_VOCAB)
