from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

WHISPER_STREAMING_TRANSCRIPTS = DATA_DIR / "whisper_streaming_transcripts.jsonl"
WHISPER_BATCH_TRANSCRIPTS = DATA_DIR / "whisper_batch_transcripts.jsonl"
PARAKEET_STREAMING_TRANSCRIPTS = DATA_DIR / "parakeet_streaming_transcripts.jsonl"
PARAKEET_CHUNKED_TRANSCRIPTS = DATA_DIR / "parakeet_chunked_transcripts.jsonl"
GRANITE_STREAMING_TRANSCRIPTS = DATA_DIR / "granite_streaming_transcripts.jsonl"
GRANITE_CHUNKED_TRANSCRIPTS = DATA_DIR / "granite_chunked_transcripts.jsonl"

LATENCY_LOG = DATA_DIR / "latency_log.jsonl"
METRICS_JSON = RESULTS_DIR / "metrics.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
