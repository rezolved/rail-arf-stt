"""Path constants for t0002_baseline_evaluation."""

from pathlib import Path

TASK_ROOT = Path("tasks/t0002_baseline_evaluation")
GOLD92_AUDIO = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio")
GROUND_TRUTH_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
)
GOLD_SET_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
)
DATA_DIR = TASK_ROOT / "data"
RESULTS_DIR = TASK_ROOT / "results"
RESULTS_IMAGES_DIR = RESULTS_DIR / "images"
DEEPGRAM_TRANSCRIPTS = DATA_DIR / "deepgram_transcripts.json"
WHISPER_TRANSCRIPTS = DATA_DIR / "whisper_transcripts.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"
PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"
DEEPGRAM_PREDICTIONS_DIR = PREDICTIONS_DIR / "deepgram-nova2-gold92"
WHISPER_PREDICTIONS_DIR = PREDICTIONS_DIR / "whisper-large-v3-gold92"
