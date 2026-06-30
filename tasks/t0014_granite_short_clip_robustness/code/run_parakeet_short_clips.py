"""Run Parakeet TDT 0.6b-v3 on short clips via production streaming simulation.

Mirrors the ParakeetSTT.transcribe_stream() pattern: accumulates all PCM-16 chunks from
a 32kB-chunk queue, then transcribes the complete buffer once.

Parakeet's chunk_secs=2 is checked in brainpowa-realtime-api's parakeet.py. For clips under
2 s, the entire clip arrives as a single chunk (degenerate single-chunk path). Results for
sub-2s bins are labelled with a `single_chunk_degenerate` flag.

GPU-PB phrase boosting: 66 casing variants of 31 domain terms, alpha=1.0 (same as t0012).

Usage (on remote machine, conda stt active):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_parakeet_short_clips.py

    # Preflight check (10 clips only):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_parakeet_short_clips.py --limit 10
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    BYTES_PER_SAMPLE,
    CHUNK_SIZE_BYTES,
    DOMAIN_VOCAB,
    PARAKEET_BOOSTING_ALPHA,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_DEPTH_SCALING,
    PARAKEET_USE_BPE_DROPOUT,
    REMOTE_PARAKEET_MODEL,
    SAMPLE_RATE,
)
from tasks.t0014_granite_short_clip_robustness.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    BOH_PATTERNS_CSV,
    METADATA_JSONL,
    TRANSCRIPTS_PARAKEET,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Parakeet on short clips")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
    return parser.parse_args()


def load_metadata() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with METADATA_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line.strip()))
    return records


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

        audio = soxr.resample(audio, sr, SAMPLE_RATE)
    return audio


def simulate_streaming_accumulate(audio_float32: np.ndarray) -> tuple[np.ndarray, float, bool]:
    """Chunk PCM-16 bytes and accumulate (mirrors transcribe_stream default pattern).

    Returns (accumulated_float32, t_first_chunk, is_single_chunk_degenerate).
    """
    pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
    raw_bytes = pcm_int16.tobytes()

    accumulated: list[bytes] = []
    t_first_chunk: float | None = None
    chunk_count = 0
    offset = 0

    while offset < len(raw_bytes):
        chunk = raw_bytes[offset : offset + CHUNK_SIZE_BYTES]
        if t_first_chunk is None:
            t_first_chunk = time.perf_counter()
        accumulated.append(chunk)
        chunk_count += 1
        offset += CHUNK_SIZE_BYTES

    if t_first_chunk is None:
        t_first_chunk = time.perf_counter()

    all_bytes = b"".join(accumulated)
    pcm_reconstructed = np.frombuffer(all_bytes, dtype=np.int16).astype(np.float32) / 32767.0
    is_single_chunk_degenerate = chunk_count == 1

    return pcm_reconstructed, t_first_chunk, is_single_chunk_degenerate


def transcribe_parakeet(model: Any, audio: np.ndarray) -> str:
    try:
        outputs = model.transcribe([audio], batch_size=1, verbose=False)
        first = outputs[0] if outputs else ""
        return (getattr(first, "text", first) or "").strip()
    except Exception as exc:
        print(f"  Parakeet transcription error: {exc}")
        return ""


def main() -> None:
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Load BoH patterns
    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)
    print(f"BoH: {len(boh_patterns)} patterns loaded")

    # Load metadata
    metadata = load_metadata()
    if args.limit is not None:
        metadata = metadata[: args.limit]
    print(f"Processing {len(metadata)} clips")

    # Load model
    print(f"Loading Parakeet from {REMOTE_PARAKEET_MODEL} ...")
    from nemo.collections.asr.models import ASRModel

    nemo_path = Path(REMOTE_PARAKEET_MODEL + ".nemo")
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

    # Warmup
    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_parakeet(model, warmup_audio)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    errors = 0

    for i, meta in enumerate(metadata):
        clip_id = str(meta["clip_id"])
        duration_s = float(meta["duration_s"])  # type: ignore[arg-type]
        reference_text = str(meta["reference_text"])

        clip_path = METADATA_JSONL.parent / "short_clips" / f"{clip_id}.wav"
        if not clip_path.exists():
            print(f"WARNING: {clip_path} not found — skipping")
            errors += 1
            continue

        try:
            audio_f32 = load_audio_float32(clip_path)
            accumulated, t_first_chunk, is_single_chunk = simulate_streaming_accumulate(audio_f32)

            transcript = transcribe_parakeet(model, accumulated)
            t_end = time.perf_counter()

            latency = t_end - t_first_chunk
            is_empty = len(transcript.strip()) == 0
            is_hallucination = detector.is_hallucination(
                transcript=transcript,
                reference_text=reference_text,
            )
            ttfd_seconds = latency if not is_empty else None

            # Flag degenerate single-chunk case for sub-2s clips
            n_chunks = int(np.ceil(len(audio_f32) * BYTES_PER_SAMPLE / CHUNK_SIZE_BYTES))

            results.append(
                {
                    "clip_id": clip_id,
                    "duration_s": duration_s,
                    "transcript": transcript,
                    "is_empty": is_empty,
                    "is_hallucination": is_hallucination,
                    "latency_seconds": latency,
                    "ttfd_seconds": ttfd_seconds,
                    "num_chunks": n_chunks,
                    "single_chunk_degenerate": is_single_chunk,
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                flag = "EMPTY" if is_empty else ("HALLUC" if is_hallucination else "ok")
                sc = " [SINGLE-CHUNK]" if is_single_chunk else ""
                print(
                    f"  [{i + 1}/{len(metadata)}] {clip_id} ({duration_s}s): "
                    f"'{transcript[:50]}' lat={latency:.3f}s [{flag}]{sc}"
                )

        except Exception as exc:
            print(f"ERROR on {clip_id}: {exc}")
            errors += 1

    # Rejection check
    total = len(metadata)
    successful = len(results)
    if total > 0 and (successful / total) < 0.8:
        raise RuntimeError(
            f"Rejection: only {successful}/{total} clips processed "
            f"(success rate {successful / total:.1%} < 80%)"
        )

    # Save results
    TRANSCRIPTS_PARAKEET.parent.mkdir(parents=True, exist_ok=True)
    with TRANSCRIPTS_PARAKEET.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nParakeet short clips: {successful}/{total} clips ({errors} errors)")
    empties = sum(1 for r in results if r["is_empty"])
    hallucinations = sum(1 for r in results if r["is_hallucination"])
    single_chunks = sum(1 for r in results if r["single_chunk_degenerate"])
    print(f"  Empty: {empties}/{successful} ({empties / max(successful, 1):.1%})")
    h_pct = hallucinations / max(successful, 1)
    print(f"  Hallucinations: {hallucinations}/{successful} ({h_pct:.1%})")
    print(f"  Single-chunk degenerate: {single_chunks}/{successful}")

    lats = [float(r["latency_seconds"]) for r in results]  # type: ignore[arg-type]
    print(f"  Latency p50={np.percentile(lats, 50):.3f}s")
    print(f"Saved → {TRANSCRIPTS_PARAKEET}")


if __name__ == "__main__":
    main()
