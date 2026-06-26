# FunASR short alias — resolves to:
#   iic/speech_paraformer-large-vad-punc_asr_nat-en-16k-common-vocab10020
# Same model for both runs; hotword parameter controls contextual biasing.
# SeACo-Paraformer is only available in Chinese; the English model supports
# hotword biasing natively.
MODEL_ID: str = "paraformer-en"
SAMPLE_RATE: int = 16_000
WARMUP_CLIPS: int = 2

# Same 31-term domain vocabulary as t0004/t0007 for cross-task comparability.
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
