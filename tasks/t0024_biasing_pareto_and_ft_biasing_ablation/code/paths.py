"""Path constants for t0024_biasing_pareto_and_ft_biasing_ablation.

Part A only this round (see checkpoint.md / intervention/checkpoint_not_found.md): Part B's
checkpoint/audio/manifest constants are kept here for a future resumption, but nothing in this
round's code reads them.
"""

from pathlib import Path

TASK_DIR = Path(__file__).parents[1]
REPO_ROOT = TASK_DIR.parents[1]
RESULTS_DIR = TASK_DIR / "results"
IMAGES_DIR = RESULTS_DIR / "images"

# Part A inputs (read-only, owned by upstream tasks).
T0022_SWEEP = REPO_ROOT / "tasks" / "t0022_gpu_pb_diagnostic" / "results" / "param_sweep.jsonl"
T0023_SWEEP = REPO_ROOT / "tasks" / "t0023_tdt_vs_unified_biasing" / "results" / "tdt_sweep.jsonl"

# Part B inputs (unused this round; Part B deferred).
T0021_MANIFEST = (
    REPO_ROOT
    / "tasks"
    / "t0021_parakeet_finetune_vs_biasing"
    / "data"
    / "clean_eval"
    / "manifest.jsonl"
)
T0021_AUDIO_DIR = (
    REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval_audio"
)
T0021_FINETUNED_NEMO = Path("/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo")
T0021_CLEAN_BIASED = (
    REPO_ROOT / "tasks" / "t0021_parakeet_finetune_vs_biasing" / "data" / "clean_eval_biased.jsonl"
)
T0021_CLEAN_FINETUNED = (
    REPO_ROOT
    / "tasks"
    / "t0021_parakeet_finetune_vs_biasing"
    / "data"
    / "clean_eval_finetuned.jsonl"
)
