"""Path constants for t0017_parakeet_biasing_buffer_replacement."""

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

# Model slug -> output dir
MODEL_OUTPUT_DIRS: dict[str, Path] = {
    "parakeet-tdt": PARAKEET_TDT_DIR,
    "parakeet-unified": PARAKEET_UNIFIED_DIR,
}


def predictions_path(model_slug: str, interval_ms: int) -> Path:
    """Per-model, per-interval prediction JSONL path."""
    return MODEL_OUTPUT_DIRS[model_slug] / f"predictions_{interval_ms}ms.jsonl"


# Predictions assets
PREDICTIONS_DIR = TASK_DIR / "assets" / "predictions"
PARAKEET_TDT_ASSET = PREDICTIONS_DIR / "parakeet-tdt-buffer-sweep-biased"
PARAKEET_UNIFIED_ASSET = PREDICTIONS_DIR / "parakeet-unified-buffer-sweep-biased"

# Metrics
METRICS_JSON = RESULTS_DIR / "metrics.json"
