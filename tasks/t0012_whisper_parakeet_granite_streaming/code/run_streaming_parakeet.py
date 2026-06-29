"""Run Parakeet TDT 0.6b-v3 with production streaming simulation on gold-92.

Streaming simulation:
  - WAV audio split into STREAM_INTERVAL_BYTES chunks (32 kB = ~1 s at 16 kHz int16)
  - Chunks accumulated in-memory (no sleep) — mirrors STTAdapter.transcribe_stream() pattern
  - Latency clock starts at first chunk delivery, ends when transcription returns
  - Biasing: NeMo GPU-PB phrase boosting (mirrors brainpowa production config exactly)
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
from tasks.t0012_whisper_parakeet_granite_streaming.code.constants import (
    BYTES_PER_SAMPLE,
    DOMAIN_VOCAB,
    PARAKEET_BOOSTING_ALPHA,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_DEPTH_SCALING,
    PARAKEET_MODEL_LOCAL_DIR,
    PARAKEET_USE_BPE_DROPOUT,
    SAMPLE_RATE,
    STREAM_INTERVAL_BYTES,
)
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import PARAKEET_STREAMING_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Parakeet streaming simulation on gold-92")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def expand_casing_variants(phrases: list[str]) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)


def apply_boosting(model: Any, phrases: tuple[str, ...], *, alpha: float) -> None:
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
    OmegaConf.update(
        cfg, "greedy.boosting_tree.context_score", PARAKEET_CONTEXT_SCORE, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.depth_scaling", PARAKEET_DEPTH_SCALING, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.use_bpe_dropout", PARAKEET_USE_BPE_DROPOUT, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def simulate_streaming(audio_float32: np.ndarray) -> tuple[np.ndarray, float]:
    """Chunk audio into STREAM_INTERVAL_BYTES int16 PCM frames, accumulate, return float32.

    Returns (accumulated_audio_float32, t_first_chunk).
    """
    pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
    raw_bytes = pcm_int16.tobytes()

    accumulated: list[bytes] = []
    t_first_chunk: float | None = None
    offset = 0
    while offset < len(raw_bytes):
        chunk = raw_bytes[offset : offset + STREAM_INTERVAL_BYTES]
        if t_first_chunk is None:
            t_first_chunk = time.perf_counter()
        accumulated.append(chunk)
        offset += STREAM_INTERVAL_BYTES

    all_bytes = b"".join(accumulated)
    pcm_reconstructed = np.frombuffer(all_bytes, dtype=np.int16).astype(np.float32) / 32767.0

    assert t_first_chunk is not None
    return pcm_reconstructed, t_first_chunk


def transcribe(model: Any, audio: np.ndarray) -> str:
    outputs = model.transcribe([audio], batch_size=1, verbose=False)
    first = outputs[0] if outputs else ""
    return (getattr(first, "text", first) or "").strip()


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

    print(f"Loading model from {PARAKEET_MODEL_LOCAL_DIR} ...")
    from nemo.collections.asr.models import ASRModel

    nemo_path = Path(PARAKEET_MODEL_LOCAL_DIR + ".nemo")
    if nemo_path.exists():
        model = ASRModel.restore_from(str(nemo_path))
    else:
        model = ASRModel.from_pretrained(
            model_name="nvidia/parakeet-tdt-0.6b-v3", map_location=device
        )
    model = model.to(device)
    model.eval()

    phrases = expand_casing_variants(DOMAIN_VOCAB)
    apply_boosting(model, phrases, alpha=PARAKEET_BOOSTING_ALPHA)
    print(f"Boosting: {len(phrases)} phrase variants, alpha={PARAKEET_BOOSTING_ALPHA}")

    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    transcribe(model, warmup_audio)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    num_chunks_per_clip: list[int] = []

    for i, clip in enumerate(available):
        audio_f32 = load_audio_float32(clip.audio_path)
        accumulated_audio, t_first_chunk = simulate_streaming(audio_f32)

        n_chunks = int(np.ceil(len(audio_f32) * BYTES_PER_SAMPLE / STREAM_INTERVAL_BYTES))
        num_chunks_per_clip.append(n_chunks)

        hypothesis = transcribe(model, accumulated_audio)
        t_end = time.perf_counter()
        latency = t_end - t_first_chunk

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
                "num_chunks": n_chunks,
                "audio_duration_seconds": len(audio_f32) / SAMPLE_RATE,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: "
                f"'{hypothesis[:60]}' lat={latency:.3f}s chunks={n_chunks}"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} non-empty. Check model.")

    PARAKEET_STREAMING_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with PARAKEET_STREAMING_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    print(f"\nParakeet streaming: {success}/{total} clips")
    print(
        f"  lat p50={np.percentile(lats, 50):.3f}s"
        f"  p95={np.percentile(lats, 95):.3f}s"
        f"  p99={np.percentile(lats, 99):.3f}s"
    )
    print(f"  avg chunks/clip: {np.mean(num_chunks_per_clip):.1f}")
    print(f"Saved → {PARAKEET_STREAMING_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
