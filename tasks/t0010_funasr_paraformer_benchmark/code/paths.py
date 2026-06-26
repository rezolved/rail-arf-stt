from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

PARAFORMER_BATCH_TRANSCRIPTS = DATA_DIR / "paraformer_batch_transcripts.json"
PARAFORMER_BIASED_TRANSCRIPTS = DATA_DIR / "paraformer_biased_transcripts.json"

METRICS_JSON = RESULTS_DIR / "metrics.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
