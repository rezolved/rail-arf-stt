"""Path constants for t0014_granite_short_clip_robustness."""

from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"
IMAGES_DIR = RESULTS_DIR / "images"

# Milestone 1 — dataset synthesis
SHORT_CLIPS_DIR = DATA_DIR / "short_clips"
METADATA_JSONL = DATA_DIR / "short_clips_metadata.jsonl"
BOH_PATTERNS_CSV = DATA_DIR / "boh_patterns.csv"

# Milestone 2 — inference outputs
TRANSCRIPTS_WHISPER = DATA_DIR / "short_clip_transcripts_whisper.jsonl"
TRANSCRIPTS_PARAKEET = DATA_DIR / "short_clip_transcripts_parakeet.jsonl"
TRANSCRIPTS_GRANITE = DATA_DIR / "short_clip_transcripts_granite.jsonl"

# Gold-92 source data (from t0012 — no re-inference needed)
T0012_DIR = TASK_DIR.parent / "t0012_whisper_parakeet_granite_streaming"
T0012_DATA_DIR = T0012_DIR / "data"
GOLD92_WHISPER_TRANSCRIPTS = T0012_DATA_DIR / "whisper_streaming_transcripts.jsonl"
GOLD92_PARAKEET_TRANSCRIPTS = T0012_DATA_DIR / "parakeet_streaming_transcripts.jsonl"
GOLD92_GRANITE_TRANSCRIPTS = T0012_DATA_DIR / "granite_streaming_transcripts.jsonl"

# Gold-92 audio and ground truth
T0001_DIR = TASK_DIR.parent / "t0001_stt_benchmark"
GOLD92_AUDIO_DIR = T0001_DIR / "assets" / "dataset" / "stt-benchmark-gold-92" / "files" / "audio"
GOLD92_GROUND_TRUTH = (
    T0001_DIR / "assets" / "dataset" / "stt-benchmark-gold-92" / "files" / "ground_truth.jsonl"
)

# Milestone 3 — analysis outputs
STRATIFIED_ANALYSIS_JSON = RESULTS_DIR / "stratified_analysis.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"

# Chart outputs
CHART_FAILURE_RATE = IMAGES_DIR / "short_clip_failure_rate.png"
CHART_ENTITY_ACCURACY = IMAGES_DIR / "stratified_entity_accuracy.png"
CHART_LATENCY = IMAGES_DIR / "latency_by_stratum.png"
