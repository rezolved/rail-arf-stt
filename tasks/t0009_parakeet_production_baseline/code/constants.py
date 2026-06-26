# Exact production config from brainpowa-realtime-api/src/.../config.py
MODEL_ID: str = "nvidia/parakeet-tdt-0.6b-v3"
MODEL_LOCAL_DIR: str = "/home/azureuser/parakeet-model/parakeet-tdt-0.6b-v3"
SAMPLE_RATE: int = 16_000

# Exact production boosting config (config.py:105-109)
BOOSTING_ALPHA: float = 1.0
CONTEXT_SCORE: float = 1.0
DEPTH_SCALING: float = 2.0
USE_BPE_DROPOUT: bool = True

# 31-term domain vocab (identical to t0004/t0006/t0007)
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
