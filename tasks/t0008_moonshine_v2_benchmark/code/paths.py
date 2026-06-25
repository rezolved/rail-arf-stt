"""Path constants for t0008_moonshine_v2_benchmark.

Note: Moonshine ONNX package only supports tiny/base (v1).
Using moonshine-streaming-medium (UsefulSensors/moonshine-streaming-medium) as the v2 Medium
equivalent.
"""

from __future__ import annotations

from pathlib import Path

TASK_ROOT = Path("tasks/t0008_moonshine_v2_benchmark")
DATA_DIR = TASK_ROOT / "data"
RESULTS_DIR = TASK_ROOT / "results"
MOONSHINE_V2_TRANSCRIPTS = DATA_DIR / "moonshine_v2_medium_transcripts.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"
ANALYSIS_OUTPUT = DATA_DIR / "analysis_output.json"
PREDICTIONS_DIR = TASK_ROOT / "assets" / "predictions"
IMAGES_DIR = RESULTS_DIR / "images"
GOLD92_AUDIO = Path("tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/audio")
GROUND_TRUTH_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/ground_truth.jsonl"
)
GOLD_SET_JSONL = Path(
    "tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl"
)
