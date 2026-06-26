from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

PARAKEET_STREAMING_TRANSCRIPTS = DATA_DIR / "predictions_streaming_parakeet.jsonl"
GRANITE_STREAMING_TRANSCRIPTS = DATA_DIR / "predictions_streaming_granite.jsonl"
LATENCY_LOG = DATA_DIR / "latency_log.jsonl"
METRICS_JSON = RESULTS_DIR / "metrics.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
