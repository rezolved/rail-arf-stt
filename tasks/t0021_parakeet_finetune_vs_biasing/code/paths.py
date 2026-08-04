"""Path constants for t0021_parakeet_finetune_vs_biasing."""

from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
CODE_DIR = TASK_DIR / "code"
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

# Gold-92 dataset (from t0001)
T0001_DIR = TASK_DIR.parent / "t0001_stt_benchmark"
GOLD92_DATASET_DIR = T0001_DIR / "assets" / "dataset" / "stt-benchmark-gold-92" / "files"
GOLD92_AUDIO_DIR = GOLD92_DATASET_DIR / "audio"
GOLD92_GROUND_TRUTH = GOLD92_DATASET_DIR / "ground_truth.jsonl"
GOLD92_GOLD_SET = GOLD92_DATASET_DIR / "gold_set.jsonl"

CLEAN_EVAL_DIR: Path = DATA_DIR / "clean_eval"
CLEAN_EVAL_AUDIO_DIR: Path = DATA_DIR / "clean_eval_audio"

# Finetuned checkpoint (on gpu-azure)
FINETUNED_NEMO = Path("/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo")

# Output
PREDICTIONS_FINETUNED = DATA_DIR / "predictions_finetuned.jsonl"
