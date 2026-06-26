"""Path constants for t0006_nemotron_3_5_benchmark."""

from pathlib import Path

TASK_ROOT = Path("tasks/t0006_nemotron_3_5_benchmark")
GOLD92_AUDIO = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio")
GROUND_TRUTH_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
)
GOLD_SET_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
)

DATA_DIR = TASK_ROOT / "data"
RESULTS_DIR = TASK_ROOT / "results"
PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"

NEMOTRON_BATCH_TRANSCRIPTS = DATA_DIR / "nemotron_batch_transcripts.json"
NEMOTRON_BOOSTED_TRANSCRIPTS = DATA_DIR / "nemotron_word_boosted_transcripts.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"

BATCH_PREDICTIONS_DIR = PREDICTIONS_DIR / "nemotron-3.5-asr-gold92-batch"
BOOSTED_PREDICTIONS_DIR = PREDICTIONS_DIR / "nemotron-3.5-asr-gold92-word-boosted"

# t0004 baseline predictions for comparison
T0004_WHISPER_BIASED_TRANSCRIPTS = Path(
    "tasks/t0004_vocabulary_biasing_experiment/data/whisper_large_v3_biased_transcripts.json"
)
T0004_METRICS = Path("tasks/t0004_vocabulary_biasing_experiment/results/metrics.json")
