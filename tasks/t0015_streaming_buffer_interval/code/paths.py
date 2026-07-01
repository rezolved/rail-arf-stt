"""Path constants for t0015_streaming_buffer_interval."""

from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
CODE_DIR = TASK_DIR / "code"
RESULTS_DIR = TASK_DIR / "results"
IMAGES_DIR = RESULTS_DIR / "images"
DATA_DIR = TASK_DIR / "data"

# Gold-92 dataset (from t0001)
T0001_DIR = TASK_DIR.parent / "t0001_stt_benchmark"
GOLD92_DATASET_DIR = T0001_DIR / "assets" / "dataset" / "stt-benchmark-gold-92" / "files"
GOLD92_AUDIO_DIR = GOLD92_DATASET_DIR / "audio"
GOLD92_GROUND_TRUTH = GOLD92_DATASET_DIR / "ground_truth.jsonl"
GOLD92_GOLD_SET = GOLD92_DATASET_DIR / "gold_set.jsonl"

# BoH patterns CSV (from t0014)
T0014_DIR = TASK_DIR.parent / "t0014_granite_short_clip_robustness"
BOH_PATTERNS_CSV = T0014_DIR / "data" / "boh_patterns.csv"

# Inference outputs (written locally by GPU scripts, then synced back)
PARAKEET_TDT_DIR = DATA_DIR / "parakeet_tdt"
PARAKEET_UNIFIED_DIR = DATA_DIR / "parakeet_unified"
MULTITALKER_DIR = DATA_DIR / "multitalker"
GRANITE_DIR = DATA_DIR / "granite"

# Per-interval JSONL output paths — parakeet-tdt
PARAKEET_TDT_500MS = PARAKEET_TDT_DIR / "predictions_500ms.jsonl"
PARAKEET_TDT_750MS = PARAKEET_TDT_DIR / "predictions_750ms.jsonl"
PARAKEET_TDT_1000MS = PARAKEET_TDT_DIR / "predictions_1000ms.jsonl"

# Per-interval JSONL output paths — parakeet-unified
PARAKEET_UNIFIED_500MS = PARAKEET_UNIFIED_DIR / "predictions_500ms.jsonl"
PARAKEET_UNIFIED_750MS = PARAKEET_UNIFIED_DIR / "predictions_750ms.jsonl"
PARAKEET_UNIFIED_1000MS = PARAKEET_UNIFIED_DIR / "predictions_1000ms.jsonl"

# Per-interval JSONL output paths — multitalker
MULTITALKER_500MS = MULTITALKER_DIR / "predictions_500ms.jsonl"
MULTITALKER_750MS = MULTITALKER_DIR / "predictions_750ms.jsonl"
MULTITALKER_1000MS = MULTITALKER_DIR / "predictions_1000ms.jsonl"

# Per-interval JSONL output paths — granite
GRANITE_500MS = GRANITE_DIR / "predictions_500ms.jsonl"
GRANITE_750MS = GRANITE_DIR / "predictions_750ms.jsonl"
GRANITE_1000MS = GRANITE_DIR / "predictions_1000ms.jsonl"

# Predictions assets
PREDICTIONS_DIR = TASK_DIR / "assets" / "predictions"
PARAKEET_TDT_ASSET = PREDICTIONS_DIR / "parakeet-tdt-buffer-sweep"
PARAKEET_UNIFIED_ASSET = PREDICTIONS_DIR / "parakeet-unified-buffer-sweep"
MULTITALKER_ASSET = PREDICTIONS_DIR / "multitalker-parakeet-buffer-sweep"
GRANITE_ASSET = PREDICTIONS_DIR / "granite-buffer-sweep"

# Metrics
METRICS_JSON = RESULTS_DIR / "metrics.json"
