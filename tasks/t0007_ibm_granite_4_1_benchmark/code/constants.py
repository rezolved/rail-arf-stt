MODEL_ID: str = "ibm-granite/granite-speech-4.1-2b"
MODEL_LOCAL_DIR: str = "/home/azureuser/granite-model/granite-speech-4.1-2b"
SAMPLE_RATE: int = 16_000
MAX_NEW_TOKENS: int = 256
WARMUP_CLIPS: int = 2

PROMPT_UNBIASED: str = "transcribe the speech with proper punctuation and capitalization."
PROMPT_BIASED_PREFIX: str = "transcribe the speech to text. Keywords: "

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
