"""Centralized Path constants for t0025 data-prep and training code."""

from __future__ import annotations

from pathlib import Path

TASK_DIR: Path = Path(__file__).resolve().parents[1]
REPO_ROOT: Path = TASK_DIR.parents[1]
REAL_REPOS: Path = REPO_ROOT.parent

DATA_DIR: Path = TASK_DIR / "data"
TRAIN_V6_MANIFEST: Path = DATA_DIR / "train_v6.jsonl"
VAL_V6_MANIFEST: Path = DATA_DIR / "val_v6.jsonl"

# Sources outside this repo (rail-metarepo sibling clones under real-repos/). Override via CLI
# flags in build_manifests_v6.py if running against a different checkout (e.g. the GPU VM's
# own clones).
DEFAULT_TRAIN_V5_MANIFEST: Path = (
    REAL_REPOS / "rail-benchmarks/parakeet-finetune-v3/parakeet_finetune/manifests/train_v5.jsonl"
)
DEFAULT_VAL_V5_MANIFEST: Path = (
    REAL_REPOS / "rail-benchmarks/parakeet-finetune-v3/parakeet_finetune/manifests/val_v5.jsonl"
)
DEFAULT_GOLD92_MANIFEST: Path = (
    REPO_ROOT
    / "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
)
DEFAULT_CLEAN_EVAL_V2_MANIFEST: Path = (
    REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/manifest.jsonl"
)
