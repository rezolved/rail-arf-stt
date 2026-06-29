"""Run Parakeet TDT 0.6b-v3 in production chunked re-transcribe mode on gold-92.

Mirrors ParakeetSTT.transcribe_stream() from brainpowa-realtime-api exactly:
  - Every STREAM_INTERVAL_BYTES of accumulated PCM-16 audio: transcribe full buffer,
    extract delta (word-level LCP matching), yield delta if non-empty.
  - Final transcribe on complete audio after all chunks delivered.
  - Latency: wall-clock from first chunk to final transcript returned.
  - TTFD: first chunk to first non-empty delta.

Complements run_streaming_parakeet.py (accumulate-then-transcribe) to measure
real production TTFD — production ParakeetSTT.transcribe_stream() is chunked,
not accumulate-then-transcribe.
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
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import PARAKEET_CHUNKED_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Parakeet chunked re-transcribe on gold-92")
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


def _extract_delta(previous: str, current: str) -> str:
    """Exact copy of ParakeetSTT._extract_delta() from brainpowa-realtime-api."""
    if not previous.strip():
        return current
    if current.startswith(previous):
        return current[len(previous) :]
    prev_words = previous.split()
    curr_words = current.split()
    common = 0
    for pw, cw in zip(prev_words, curr_words, strict=False):
        if pw.lower().rstrip(".,!?;:") == cw.lower().rstrip(".,!?;:"):
            common += 1
        else:
            break
    if common > 0 and (common >= len(prev_words) - 1 or common >= len(prev_words) // 2):
        delta_words = curr_words[common:]
        return " ".join(delta_words) if delta_words else ""
    return current


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_buffer(model: Any, audio_float32: np.ndarray) -> str:
    outputs = model.transcribe([audio_float32], batch_size=1, verbose=False)
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
    transcribe_buffer(model, warmup_audio)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    num_chunks_per_clip: list[int] = []

    for i, clip in enumerate(available):
        audio_float32 = load_audio_float32(clip.audio_path)
        raw_bytes_len = len(audio_float32) * BYTES_PER_SAMPLE
        n_chunks = int(np.ceil(raw_bytes_len / STREAM_INTERVAL_BYTES))
        num_chunks_per_clip.append(n_chunks)
        audio_duration = len(audio_float32) / SAMPLE_RATE

        # Simulate streaming: deliver int16 PCM chunks, accumulate, re-transcribe per interval
        pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
        raw_bytes = pcm_int16.tobytes()

        accumulated = bytearray()
        bytes_since_last: int = 0
        prev_transcript: str = ""
        t_first_chunk: float | None = None
        ttfd: float | None = None

        offset = 0
        while offset < len(raw_bytes):
            chunk = raw_bytes[offset : offset + STREAM_INTERVAL_BYTES]
            if t_first_chunk is None:
                t_first_chunk = time.perf_counter()
            accumulated.extend(chunk)
            bytes_since_last += len(chunk)
            offset += STREAM_INTERVAL_BYTES

            if bytes_since_last >= STREAM_INTERVAL_BYTES:
                bytes_since_last = 0
                acc_float = (
                    np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
                )
                text = transcribe_buffer(model, acc_float)
                delta_text = _extract_delta(prev_transcript, text)
                if delta_text.strip():
                    if ttfd is None:
                        ttfd = time.perf_counter() - t_first_chunk  # type: ignore[operator]
                    prev_transcript = text

        # Final transcribe on complete buffer
        assert t_first_chunk is not None
        final_float = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
        final_text = transcribe_buffer(model, final_float)
        t_end = time.perf_counter()
        latency = t_end - t_first_chunk

        if ttfd is None:
            ttfd = latency

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": final_text,
                "latency_seconds": latency,
                "ttfd_seconds": ttfd,
                "num_chunks": n_chunks,
                "audio_duration_seconds": audio_duration,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: "
                f"'{final_text[:60]}' lat={latency:.3f}s ttfd={ttfd:.3f}s chunks={n_chunks}"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    PARAKEET_CHUNKED_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with PARAKEET_CHUNKED_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    ttfds = [float(r["ttfd_seconds"]) for r in results]
    print(f"\nParakeet chunked: {success}/{total} clips")
    print(
        f"  lat  p50={np.percentile(lats, 50):.3f}s"
        f"  p95={np.percentile(lats, 95):.3f}s"
        f"  p99={np.percentile(lats, 99):.3f}s"
    )
    print(f"  ttfd p50={np.percentile(ttfds, 50):.3f}s  p95={np.percentile(ttfds, 95):.3f}s")
    print(f"  avg chunks/clip: {np.mean(num_chunks_per_clip):.1f}")
    print(f"Saved → {PARAKEET_CHUNKED_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
