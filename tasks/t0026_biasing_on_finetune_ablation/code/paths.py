"""Path constants for t0026_biasing_on_finetune_ablation."""

from pathlib import Path

REPO_ROOT: Path = Path(__file__).parents[3]
TASK_DIR: Path = Path(__file__).parents[1]
DATA_DIR: Path = TASK_DIR / "data"
RESULTS_DIR: Path = TASK_DIR / "results"
IMAGES_DIR: Path = RESULTS_DIR / "images"

# t0021_parakeet_finetune_vs_biasing — clean_eval_v2 holdout (91 clips, dependency task)
T0021_MANIFEST: Path = (
    REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/manifest.jsonl"
)
T0021_AUDIO_DIR: Path = (
    REPO_ROOT / "tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/audio"
)

# This task's own gitignored copy of the manifest, with machine-resolved audio paths.
FIXED_MANIFEST: Path = DATA_DIR / "clean_eval_v2_manifest_fixed.jsonl"

# t0024_parakeet_unified_checkpoint_archive — fine-tuned checkpoint model asset (dependency task)
FT_CHECKPOINT: Path = (
    REPO_ROOT
    / "tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5"
    / "files/parakeet-unified-finetuned-best.nemo"
)

# t0024_biasing_pareto_and_ft_biasing_ablation — frontier-selected biasing cell (dependency task)
PARETO_UNIFIED_JSON: Path = (
    REPO_ROOT / "tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json"
)
