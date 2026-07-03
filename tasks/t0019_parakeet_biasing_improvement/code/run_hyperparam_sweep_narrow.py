"""Narrow GPU-PB hyperparameter screening near baseline.

Follow-up to run_hyperparam_sweep.py (t0019).

The wide grid (alpha 1.0-3.0, depth_scaling 2.0-4.0) confirmed on all 93 clips that alpha>=2.0 or
depth_scaling>=3.0 causes catastrophic WER regression (+20-27pp) even though EA-DV improves —
classic over-boosting garbling non-entity words. This script screens a narrow grid close to the
production default (alpha=1.0, depth_scaling=2.0) and tracks WER (not just EA-DV) per config so a
regressing config is caught at the 20-clip screening stage instead of only at full-93 confirmation.

Usage (remote, conda env stt active, PYTHONPATH=repo root):
    python -u tasks/t0019_parakeet_biasing_improvement/code/run_hyperparam_sweep_narrow.py
"""

from __future__ import annotations

import json
import re
import string
from pathlib import Path
from typing import Any

import jiwer

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
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import BOH_PATTERNS_CSV
from tasks.t0017_parakeet_biasing_buffer_replacement.code.run_parakeet_buffer_sweep import (
    expand_casing_variants,
    load_audio_float32,
    load_gold92_clips,
    transcribe_buffer,
)

# Narrow grid close to production default (alpha=1.0, depth_scaling=2.0).
ALPHA_GRID: list[float] = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
DEPTH_SCALING_GRID: list[float] = [2.0, 2.25, 2.5]
SCREEN_CLIP_COUNT: int = 20

TASK_DIR = Path(__file__).parents[1]
RESULTS_DIR = TASK_DIR / "results"
SWEEP_OUTPUT = RESULTS_DIR / "hyperparam_sweep_narrow.jsonl"

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


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def entity_accuracy_domain_vocab(hyp: str, ref: str) -> tuple[int, int]:
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


def apply_config(model: Any, phrases: tuple[str, ...], alpha: float, depth_scaling: float) -> None:
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


def run_config(
    model: Any,
    clips: list[dict[str, Any]],
    *,
    alpha: float,
    depth_scaling: float,
    phrases: tuple[str, ...],
    detector: HallucinationDetector,
) -> dict[str, Any]:
    apply_config(model, phrases, alpha, depth_scaling)

    correct_sum = 0
    total_sum = 0
    empties = 0
    hallucs = 0
    refs: list[str] = []
    hyps: list[str] = []

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
        refs.append(normalise(reference_text))
        hyps.append(normalise(text))

    ea_dv = correct_sum / total_sum if total_sum > 0 else 0.0
    wer_result = jiwer.process_words(refs, hyps)
    n = wer_result.hits + wer_result.substitutions + wer_result.deletions
    wer = (
        (wer_result.substitutions + wer_result.deletions + wer_result.insertions) / n
        if n > 0
        else 0.0
    )

    return {
        "alpha": alpha,
        "depth_scaling": depth_scaling,
        "context_score": PARAKEET_CONTEXT_SCORE,
        "ea_dv_20clip": round(ea_dv, 4),
        "wer_20clip": round(wer, 4),
        "n_domain_mentions": total_sum,
        "empties": empties,
        "hallucinations": hallucs,
        "n_clips": len(clips),
    }


def main() -> None:
    import torch
    from nemo.collections.asr.models import ASRModel

    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)

    clips = load_gold92_clips(limit=SCREEN_CLIP_COUNT)
    print(f"Screening on {len(clips)} clips (same fixed subsample as wide sweep)")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {HF_PARAKEET_UNIFIED} ...")
    model = ASRModel.from_pretrained(model_name=HF_PARAKEET_UNIFIED, map_location=device)
    model = model.to(device)
    model.eval()

    warmup_audio = load_audio_float32(clips[0]["audio_path"])
    for _ in range(3):
        transcribe_buffer(model, warmup_audio)

    phrases = expand_casing_variants(DOMAIN_VOCAB)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for alpha in ALPHA_GRID:
        for depth_scaling in DEPTH_SCALING_GRID:
            print(f"\n=== alpha={alpha} depth_scaling={depth_scaling} ===")
            row = run_config(
                model,
                clips,
                alpha=alpha,
                depth_scaling=depth_scaling,
                phrases=phrases,
                detector=detector,
            )
            print(f"  EA-DV={row['ea_dv_20clip']:.3f} WER={row['wer_20clip']:.3f}")
            rows.append(row)

    with SWEEP_OUTPUT.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(rows)} configs -> {SWEEP_OUTPUT}")

    baseline_wer = next(
        (r["wer_20clip"] for r in rows if r["alpha"] == 1.0 and r["depth_scaling"] == 2.0), None
    )
    print(f"\nBaseline (alpha=1.0, depth=2.0) WER_20clip = {baseline_wer}")

    within_cap = [
        r for r in rows if baseline_wer is not None and r["wer_20clip"] <= baseline_wer + 0.01
    ]
    within_cap.sort(key=lambda r: r["ea_dv_20clip"], reverse=True)
    print("\nConfigs within +1pp WER cap, sorted by EA-DV:")
    for row in within_cap:
        print(
            f"  alpha={row['alpha']} depth_scaling={row['depth_scaling']} "
            f"EA-DV={row['ea_dv_20clip']:.3f} WER={row['wer_20clip']:.3f}"
        )


if __name__ == "__main__":
    main()
