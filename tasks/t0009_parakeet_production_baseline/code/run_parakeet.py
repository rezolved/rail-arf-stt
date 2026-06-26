"""Run Parakeet TDT 0.6b-v3 on gold-92, replicating production config exactly.

Runs two variants:
  1. Unbiased: no boosting tree (alpha=0)
  2. Biased: DOMAIN_VOCAB phrases + casing variants, alpha=1.0

Production reference: brainpowa-realtime-api/src/.../pipeline/stt/parakeet.py
"""

from __future__ import annotations

import argparse
import copy
import json
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0009_parakeet_production_baseline.code.constants import (
    BOOSTING_ALPHA,
    CONTEXT_SCORE,
    DEPTH_SCALING,
    DOMAIN_VOCAB,
    MODEL_LOCAL_DIR,
    SAMPLE_RATE,
    USE_BPE_DROPOUT,
)
from tasks.t0009_parakeet_production_baseline.code.paths import (
    PARAKEET_BATCH_TRANSCRIPTS,
    PARAKEET_BIASED_TRANSCRIPTS,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Parakeet production baseline on gold-92")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def expand_casing_variants(phrases: list[str]) -> tuple[str, ...]:
    """Mirror production _expand_casing_variants exactly."""
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)


def apply_boosting(model: Any, phrases: tuple[str, ...], *, alpha: float) -> None:
    """Mirror production _apply_boosting_to exactly."""
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(
        cfg,
        "greedy.boosting_tree.key_phrases_list",
        list(phrases) if phrases else None,
        force_add=True,
    )
    OmegaConf.update(cfg, "greedy.boosting_tree.context_score", CONTEXT_SCORE, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.depth_scaling", DEPTH_SCALING, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.use_bpe_dropout", USE_BPE_DROPOUT, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)


def load_audio(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_clip(model: Any, audio: np.ndarray) -> str:
    outputs = model.transcribe([audio], batch_size=1, verbose=False)
    first = outputs[0] if outputs else ""
    return (getattr(first, "text", first) or "").strip()


def run_variant(
    model: Any,
    clips: list,
    *,
    biased: bool,
    output_path: Path,
) -> None:
    if biased:
        phrases = expand_casing_variants(DOMAIN_VOCAB)
        apply_boosting(model, phrases, alpha=BOOSTING_ALPHA)
        print(f"Boosting tree: {len(phrases)} phrase variants, alpha={BOOSTING_ALPHA}")
    else:
        apply_boosting(model, (), alpha=0.0)
        print("No boosting (alpha=0)")

    results: list[dict[str, object]] = []
    for i, clip in enumerate(clips):
        audio = load_audio(clip.audio_path)

        t0 = time.perf_counter()
        hypothesis = transcribe_clip(model, audio)
        latency = time.perf_counter() - t0

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i + 1}/{len(clips)}] {clip.clip_id}: '{hypothesis[:60]}' ({latency:.2f}s)")

    total = len(clips)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} non-empty. Check model.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"Done: {success}/{total} clips → {output_path}")


def main() -> None:
    import torch

    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    clips = load_gold92()
    process_clips = clips[: args.limit] if args.limit is not None else clips
    available = [c for c in process_clips if c.audio_path.exists()]
    missing = len(process_clips) - len(available)
    if missing > 0:
        warnings.warn(f"{missing} audio files not found — skipping", stacklevel=2)
    if len(available) == 0:
        raise RuntimeError("No audio files. Run dvc pull first.")

    print(f"Loading model from {MODEL_LOCAL_DIR} ...")
    from nemo.collections.asr.models import ASRModel

    nemo_path = Path(MODEL_LOCAL_DIR + ".nemo")
    if nemo_path.exists():
        model = ASRModel.restore_from(str(nemo_path))
    else:
        model = ASRModel.from_pretrained(
            model_name="nvidia/parakeet-tdt-0.6b-v3", map_location=device
        )
    model = model.to(device)
    model.eval()
    print("Model loaded. Warming up ...")
    apply_boosting(model, (), alpha=0.0)
    model.transcribe([np.zeros(SAMPLE_RATE, dtype=np.float32)], batch_size=1, verbose=False)
    print("Warmup done.")

    print("\n=== Run 1: Unbiased (production equivalent: no stt_initial_prompt) ===")
    run_variant(model, available, biased=False, output_path=PARAKEET_BATCH_TRANSCRIPTS)

    print("\n=== Run 2: Biased (production equivalent: stt_initial_prompt=DOMAIN_VOCAB) ===")
    run_variant(model, available, biased=True, output_path=PARAKEET_BIASED_TRANSCRIPTS)


if __name__ == "__main__":
    main()
