"""Load gold-92 dataset for t0006. Thin wrapper over t0004 loader."""

from __future__ import annotations

from pathlib import Path

from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
)
from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    load_gold92 as _load_gold92,
)
from tasks.t0006_nemotron_3_5_benchmark.code.paths import (
    GOLD92_AUDIO,
    GOLD_SET_JSONL,
    GROUND_TRUTH_JSONL,
)

__all__ = ["CYRILLIC_ANOMALY_CLIP", "GoldClip", "load_gold92"]


def load_gold92(
    *,
    ground_truth_path: Path = GROUND_TRUTH_JSONL,
    gold_set_path: Path = GOLD_SET_JSONL,
    audio_dir: Path = GOLD92_AUDIO,
) -> list[GoldClip]:
    """Load all 93 gold-92 clips using t0004 loader with t0006 paths."""
    return _load_gold92(
        ground_truth_path=ground_truth_path,
        gold_set_path=gold_set_path,
        audio_dir=audio_dir,
    )


if __name__ == "__main__":
    clips = load_gold92()
    print(f"Loaded {len(clips)} clips")
    assert len(clips) == 93, f"Expected 93, got {len(clips)}"  # noqa: S101
    print("PASS")
