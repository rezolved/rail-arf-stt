"""Decoding-strategy helpers for t0026_biasing_on_finetune_ablation.

`apply_malsd_boost` is copied verbatim from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines
281-299, per this task's `plan/plan.md` Approach section (REQ-10). `apply_malsd_no_boost` is a new
~10-line function modeled on that file's `reset_greedy_no_boost` (lines 248-256) but targeting
`malsd_batch` instead of `greedy_batch`, so that every arm in this task's 2x2 ablation uses the same
decoder strategy (REQ-2) — only B/D additionally get a boosting tree.
"""

import copy
from typing import Any

from omegaconf import OmegaConf, open_dict


def apply_malsd_no_boost(model: Any) -> None:
    """Set `malsd_batch` decoding with no boosting tree — the "no bias" arm's decoding config."""
    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "malsd_batch"
        cfg.beam.beam_size = 4
    model.change_decoding_strategy(cfg)


def apply_malsd_boost(
    model: Any,
    phrases: list[str],
    *,
    alpha: float,
    context_score: float,
    depth_scaling: float,
) -> None:
    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "malsd_batch"
    OmegaConf.update(cfg, "beam.beam_size", 4, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.key_phrases_list", phrases, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.context_score", context_score, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.depth_scaling", depth_scaling, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)
