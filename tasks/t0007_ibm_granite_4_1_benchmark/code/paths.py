from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data"
RESULTS_DIR = TASK_DIR / "results"

GRANITE_BATCH_TRANSCRIPTS = DATA_DIR / "granite_batch_transcripts.json"
GRANITE_BIASED_TRANSCRIPTS = DATA_DIR / "granite_biased_transcripts.json"
GRANITE_NAR_BIASED_TRANSCRIPTS = DATA_DIR / "granite_nar_biased_transcripts.json"
GRANITE_COMPILED_BIASED_TRANSCRIPTS = DATA_DIR / "granite_compiled_biased_transcripts.json"
GRANITE_POSTPROC_BIASED_TRANSCRIPTS = DATA_DIR / "granite_postproc_biased_transcripts.json"

T0004_WHISPER_BIASED_TRANSCRIPTS = (
    Path(__file__).parents[3]
    / "t0004_vocabulary_biasing_experiment"
    / "assets"
    / "whisper_large_v3_biased_transcripts.json"
)
