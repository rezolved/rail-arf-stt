from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

PARAKEET_BATCH_TRANSCRIPTS = DATA_DIR / "parakeet_batch_transcripts.json"
PARAKEET_BIASED_TRANSCRIPTS = DATA_DIR / "parakeet_biased_transcripts.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
