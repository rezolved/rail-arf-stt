"""GPU-PB hyperparameter screening sweep for parakeet-unified-en-0.6b (t0019, Step 3 screening).

Grid over alpha x depth_scaling on a fixed 20-clip gold-92 subsample to find top candidate
configs by entity_accuracy_domain_vocab (EA-DV), before a full-93-clip confirmation run.
Reuses transcription/boosting/loading helpers directly from t0017's harness (no duplication).

Usage (remote, conda env stt active, PYTHONPATH=repo root):
    python -u tasks/t0019_parakeet_biasing_improvement/code/run_hyperparam_sweep.py
    python -u .../run_hyperparam_sweep.py --clips 5   # smoke test
"""

from __future__ import annotations

import argparse
import json
import re
import string
from pathlib import Path
from typing import Any

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (
    DOMAIN_VOCAB,
    HF_PARAKEET_UNIFIED,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_USE_BPE_DROPOUT,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import (
    BOH_PATTERNS_CSV,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.run_parakeet_buffer_sweep import (
    apply_boosting,
    expand_casing_variants,
    load_audio_float32,
    load_gold92_clips,
    transcribe_buffer,
)

# Screening grid — REQ-2. context_score held fixed per plan/plan.md Step 3.
ALPHA_GRID: list[float] = [1.0, 1.5, 2.0, 2.5, 3.0]
DEPTH_SCALING_GRID: list[float] = [2.0, 3.0, 4.0]
SCREEN_CLIP_COUNT: int = 20

TASK_DIR = Path(__file__).parents[1]
RESULTS_DIR = TASK_DIR / "results"
SWEEP_OUTPUT = RESULTS_DIR / "hyperparam_sweep.jsonl"

ENTITY_PATTERNS: list[str] = [
    r"\bRezolve AI\b",
    r"\bRezolve\b",
    r"\bbrainpowa\b",
    r"\bSalesforce Commerce Cloud\b",
    r"\bShopify Plus\b",
    r"\bAdobe Commerce\b",
    r"\bAdobe\b",
    r"\bShopify\b",
    r"\bSalesforce\b",
    r"\bNASDAQ\b",
    r"\bAI Foundry\b",
    r"\bNLU\b",
    r"\bASR\b",
    r"\bSKU\b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hyperparam screening sweep (t0019 Step 3)")
    parser.add_argument(
        "--clips", type=int, default=SCREEN_CLIP_COUNT, help="Screening subsample size"
    )
    return parser.parse_args()


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def entity_accuracy_domain_vocab(hyp: str, ref: str) -> tuple[int, int]:
    """Return (correct, total) domain-vocab entity mentions found in ref, per t0017's scheme."""
    hyp_norm = normalise(hyp)
    correct = 0
    total = 0
    for pattern in ENTITY_PATTERNS:
        if re.search(pattern, ref, flags=re.IGNORECASE):
            total += 1
            bare = pattern.strip(r"\b").replace(r"\b", "")
            if re.search(re.escape(normalise(bare)), hyp_norm):
                correct += 1
    return correct, total


def run_config(
    model: Any,
    clips: list[dict[str, Any]],
    *,
    alpha: float,
    depth_scaling: float,
    detector: HallucinationDetector,
) -> dict[str, Any]:
    phrases = expand_casing_variants(DOMAIN_VOCAB)
    apply_boosting(model, phrases, alpha=alpha)
    # depth_scaling is fixed inside apply_boosting via PARAKEET_DEPTH_SCALING; override here
    # by re-applying with a patched constant so each config gets its own depth_scaling.
    import copy as copy_module

    from omegaconf import OmegaConf, open_dict

    cfg = copy_module.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree.key_phrases_list", list(phrases), force_add=True)
    OmegaConf.update(
        cfg, "greedy.boosting_tree.context_score", PARAKEET_CONTEXT_SCORE, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree.depth_scaling", depth_scaling, force_add=True)
    OmegaConf.update(
        cfg, "greedy.boosting_tree.use_bpe_dropout", PARAKEET_USE_BPE_DROPOUT, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)

    correct_sum = 0
    total_sum = 0
    empties = 0
    hallucs = 0

    for clip_info in clips:
        audio_f32 = load_audio_float32(clip_info["audio_path"])
        text = transcribe_buffer(model, audio_f32)
        reference_text = clip_info["reference_text"]
        c, t = entity_accuracy_domain_vocab(text, reference_text)
        correct_sum += c
        total_sum += t
        if len(text.strip()) == 0:
            empties += 1
        if detector.is_hallucination(transcript=text, reference_text=reference_text):
            hallucs += 1

    ea_dv = correct_sum / total_sum if total_sum > 0 else 0.0
    return {
        "alpha": alpha,
        "depth_scaling": depth_scaling,
        "context_score": PARAKEET_CONTEXT_SCORE,
        "ea_dv_20clip": round(ea_dv, 4),
        "n_domain_mentions": total_sum,
        "empties": empties,
        "hallucinations": hallucs,
        "n_clips": len(clips),
    }


def main() -> None:
    args = parse_args()

    import torch
    from nemo.collections.asr.models import ASRModel

    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)

    clips = load_gold92_clips(limit=args.clips)
    print(f"Screening on {len(clips)} clips (fixed subsample, sorted by clip_id load order)")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {HF_PARAKEET_UNIFIED} ...")
    model = ASRModel.from_pretrained(model_name=HF_PARAKEET_UNIFIED, map_location=device)
    model = model.to(device)
    model.eval()

    warmup_audio = load_audio_float32(clips[0]["audio_path"])
    for _ in range(3):
        transcribe_buffer(model, warmup_audio)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for alpha in ALPHA_GRID:
        for depth_scaling in DEPTH_SCALING_GRID:
            print(f"\n=== alpha={alpha} depth_scaling={depth_scaling} ===")
            row = run_config(
                model, clips, alpha=alpha, depth_scaling=depth_scaling, detector=detector
            )
            print(f"  EA-DV={row['ea_dv_20clip']:.3f} ({row['n_domain_mentions']} mentions)")
            rows.append(row)

    with SWEEP_OUTPUT.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(rows)} configs -> {SWEEP_OUTPUT}")

    top2 = sorted(rows, key=lambda r: r["ea_dv_20clip"], reverse=True)[:2]
    print("\nTop-2 by 20-clip EA-DV:")
    for row in top2:
        print(
            f"  alpha={row['alpha']} depth_scaling={row['depth_scaling']}"
            f" EA-DV={row['ea_dv_20clip']:.3f}"
        )


if __name__ == "__main__":
    main()
