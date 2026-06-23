"""Path constants for t0004_vocabulary_biasing_experiment."""

from pathlib import Path

TASK_ROOT = Path("tasks/t0004_vocabulary_biasing_experiment")
GOLD92_AUDIO = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio")
GROUND_TRUTH_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
)
GOLD_SET_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
)
DATA_DIR = TASK_ROOT / "data"
RESULTS_DIR = TASK_ROOT / "results"
WHISPER_BIASED_TRANSCRIPTS = DATA_DIR / "whisper_large_v3_biased_transcripts.json"
WHISPER_TURBO_BIASED_TRANSCRIPTS = DATA_DIR / "whisper_turbo_biased_transcripts.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"
PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"
WHISPER_BIASED_PREDICTIONS_DIR = PREDICTIONS_DIR / "whisper-large-v3-biased"
WHISPER_TURBO_BIASED_PREDICTIONS_DIR = PREDICTIONS_DIR / "whisper-turbo-biased"

# t0002 baseline prediction files (for reusing baseline numbers)
T0002_WHISPER_TRANSCRIPTS = Path("tasks/t0002_baseline_evaluation/data/whisper_transcripts.json")
T0002_WHISPER_TURBO_TRANSCRIPTS = Path(
    "tasks/t0002_baseline_evaluation/data/whisper_turbo_transcripts.json"
)
T0002_RESULTS_METRICS = Path("tasks/t0002_baseline_evaluation/results/metrics.json")

# Moonshine base (no biasing — model doesn't support initial_prompt)
MOONSHINE_TRANSCRIPTS = DATA_DIR / "moonshine_base_transcripts.json"
MOONSHINE_PREDICTIONS_DIR = PREDICTIONS_DIR / "moonshine-base-gold92"
