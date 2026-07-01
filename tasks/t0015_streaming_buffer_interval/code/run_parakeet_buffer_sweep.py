"""Buffer interval sweep for Parakeet TDT 0.6b-v3 and Parakeet Unified 0.6b on gold-92.

Simulates chunked re-transcribe streaming: accumulate PCM-16 audio into a growing buffer,
re-transcribe every N ms of accumulated audio. Records TTFD (first non-empty delta) and
final latency for each clip.

GPU-PB TurboBias (boosting_tree) applied for both models — same config as t0012 production.

Usage (on remote machine, conda env stt active):
    python -u tasks/t0015_streaming_buffer_interval/code/run_parakeet_buffer_sweep.py \
        --model tdt  # or --model unified
    python -u tasks/t0015_streaming_buffer_interval/code/run_parakeet_buffer_sweep.py \
        --model tdt --limit 5  # preflight
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

from tasks.t0015_streaming_buffer_interval.code.constants import (
    BUFFER_INTERVALS_MS,
    CHUNK_SIZE_BYTES,
    DOMAIN_VOCAB,
    HF_PARAKEET_TDT,
    HF_PARAKEET_UNIFIED,
    INTERVAL_BYTES,
    MIN_SUCCESS_RATE,
    MODEL_PARAKEET_TDT,
    MODEL_PARAKEET_UNIFIED,
    PARAKEET_BOOSTING_ALPHA,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_DEPTH_SCALING,
    PARAKEET_USE_BPE_DROPOUT,
    SAMPLE_RATE,
)
from tasks.t0015_streaming_buffer_interval.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0015_streaming_buffer_interval.code.paths import (
    BOH_PATTERNS_CSV,
    GOLD92_AUDIO_DIR,
    GOLD92_GROUND_TRUTH,
    PARAKEET_TDT_DIR,
    PARAKEET_UNIFIED_DIR,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parakeet buffer interval sweep")
    parser.add_argument(
        "--model",
        required=True,
        choices=["tdt", "unified"],
        help="Which parakeet model to run",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
    return parser.parse_args()


def expand_casing_variants(phrases: list[str]) -> tuple[str, ...]:
    """Expand each phrase into lowercase, original, and title-case variants."""
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)


def apply_boosting(model: Any, phrases: tuple[str, ...], *, alpha: float) -> None:
    """Apply NeMo GPU-PB TurboBias to the model decoding config."""
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
    """Load WAV as float32 mono array at 16kHz."""
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_buffer(model: Any, audio_float32: np.ndarray) -> str:
    """Transcribe accumulated float32 audio buffer."""
    try:
        outputs = model.transcribe([audio_float32], batch_size=1, verbose=False)
        first = outputs[0] if outputs else ""
        return (getattr(first, "text", first) or "").strip()
    except Exception as exc:
        print(f"  transcribe error: {exc}")
        return ""


def _extract_delta(previous: str, current: str) -> str:
    """Extract new text delta from streaming transcript (mirrors brainpowa ParakeetSTT)."""
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


def load_gold92_clips(
    *,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Load gold-92 clips from ground_truth.jsonl."""
    clips: list[dict[str, Any]] = []
    with GOLD92_GROUND_TRUTH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            clip_id = record["clip_id"]
            audio_path = GOLD92_AUDIO_DIR / f"{clip_id}.wav"
            if not audio_path.exists():
                continue
            clips.append(
                {
                    "clip_id": clip_id,
                    "reference_text": record.get("reference_text", ""),
                    "audio_path": audio_path,
                }
            )
    if limit is not None:
        clips = clips[:limit]
    return clips


def run_buffer_sweep(
    model: Any,
    clips: list[dict[str, Any]],
    *,
    interval_ms: int,
    detector: HallucinationDetector,
) -> list[dict[str, Any]]:
    """Run one interval on all clips. Returns per-clip results."""
    interval_bytes = INTERVAL_BYTES[interval_ms]
    results: list[dict[str, Any]] = []
    errors = 0

    for i, clip_info in enumerate(clips):
        clip_id = clip_info["clip_id"]
        reference_text = clip_info["reference_text"]
        audio_path = clip_info["audio_path"]

        if not audio_path.exists():
            print(f"WARNING: {audio_path} not found — skipping")
            errors += 1
            continue

        try:
            audio_f32 = load_audio_float32(audio_path)
            duration_s = len(audio_f32) / SAMPLE_RATE

            # Simulate streaming: deliver 32kB production chunks, accumulate,
            # re-transcribe every N ms
            pcm_int16 = (audio_f32 * 32767).clip(-32768, 32767).astype(np.int16)
            raw_bytes = pcm_int16.tobytes()

            accumulated = bytearray()
            bytes_since_last_inference: int = 0
            prev_transcript: str = ""
            t_first_chunk: float | None = None
            ttfd: float | None = None

            offset = 0
            while offset < len(raw_bytes):
                chunk = raw_bytes[offset : offset + CHUNK_SIZE_BYTES]
                if t_first_chunk is None:
                    t_first_chunk = time.perf_counter()
                accumulated.extend(chunk)
                bytes_since_last_inference += len(chunk)
                offset += CHUNK_SIZE_BYTES

                if bytes_since_last_inference >= interval_bytes:
                    bytes_since_last_inference = 0
                    acc_f32 = (
                        np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32)
                        / 32767.0
                    )
                    text = transcribe_buffer(model, acc_f32)
                    delta_text = _extract_delta(prev_transcript, text)
                    if delta_text.strip():
                        if ttfd is None:
                            assert t_first_chunk is not None
                            ttfd = time.perf_counter() - t_first_chunk
                        prev_transcript = text

            # Final transcribe on complete buffer
            assert t_first_chunk is not None
            final_f32 = (
                np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            )
            final_text = transcribe_buffer(model, final_f32)
            t_end = time.perf_counter()
            latency = t_end - t_first_chunk

            if ttfd is None:
                ttfd = latency  # no delta fired — use total latency as TTFD

            is_empty = len(final_text.strip()) == 0
            is_hallucination = detector.is_hallucination(
                transcript=final_text,
                reference_text=reference_text,
            )

            n_chunks = int(np.ceil(len(raw_bytes) / CHUNK_SIZE_BYTES))
            n_inferences = int(np.ceil(len(raw_bytes) / interval_bytes))

            results.append(
                {
                    "clip_id": clip_id,
                    "duration_s": round(duration_s, 3),
                    "transcript": final_text,
                    "reference_text": reference_text,
                    "is_empty": is_empty,
                    "is_hallucination": is_hallucination,
                    "ttfd_seconds": round(ttfd, 4),
                    "latency_seconds": round(latency, 4),
                    "interval_ms": interval_ms,
                    "n_chunks": n_chunks,
                    "n_inferences": n_inferences,
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                flag = "EMPTY" if is_empty else ("HALLUC" if is_hallucination else "ok")
                print(
                    f"  [{i + 1}/{len(clips)}] {clip_id} ({duration_s:.1f}s): "
                    f"'{final_text[:50]}' lat={latency:.3f}s ttfd={ttfd:.3f}s [{flag}]"
                )

        except Exception as exc:
            print(f"ERROR on {clip_id}: {exc}")
            errors += 1

    # Rejection gate
    total = len(clips)
    successful = len(results)
    if total > 0 and (successful / total) < MIN_SUCCESS_RATE:
        raise RuntimeError(
            f"Rejection: only {successful}/{total} clips processed "
            f"({successful / total:.1%} < {MIN_SUCCESS_RATE:.0%})"
        )

    empties = sum(1 for r in results if r["is_empty"])
    hallucs = sum(1 for r in results if r["is_hallucination"])
    lats = [r["latency_seconds"] for r in results]
    ttfds = [r["ttfd_seconds"] for r in results]
    print(
        f"  interval={interval_ms}ms: {successful}/{total} clips, "
        f"empty={empties}, halluc={hallucs}, "
        f"lat_p50={np.percentile(lats, 50):.3f}s, ttfd_p50={np.percentile(ttfds, 50):.3f}s"
    )
    return results


def main() -> None:
    import torch

    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    is_tdt = args.model == "tdt"
    model_name = MODEL_PARAKEET_TDT if is_tdt else MODEL_PARAKEET_UNIFIED
    hf_id = HF_PARAKEET_TDT if is_tdt else HF_PARAKEET_UNIFIED
    out_dir = PARAKEET_TDT_DIR if is_tdt else PARAKEET_UNIFIED_DIR

    print(f"Model: {model_name}")

    # Load BoH patterns
    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)
    print(f"BoH: {len(boh_patterns)} patterns loaded")

    # Load clips
    clips = load_gold92_clips(limit=args.limit)
    print(f"Clips: {len(clips)}")

    # Load NeMo model
    from nemo.collections.asr.models import ASRModel

    print(f"Loading {model_name} from HuggingFace ...")
    model = ASRModel.from_pretrained(model_name=hf_id, map_location=device)
    model = model.to(device)
    model.eval()

    # Apply GPU-PB TurboBias
    phrases = expand_casing_variants(DOMAIN_VOCAB)
    try:
        apply_boosting(model, phrases, alpha=PARAKEET_BOOSTING_ALPHA)
        print(f"Boosting: {len(phrases)} phrase variants, alpha={PARAKEET_BOOSTING_ALPHA}")
    except Exception as exc:
        print(f"WARNING: Boosting failed ({exc}), continuing without")

    # Warmup
    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_buffer(model, warmup_audio)
    print("Warmup done.")

    # Run sweep over all intervals
    out_dir.mkdir(parents=True, exist_ok=True)

    for interval_ms in BUFFER_INTERVALS_MS:
        print(f"\n=== {model_name} | interval={interval_ms}ms ===")
        results = run_buffer_sweep(model, clips, interval_ms=interval_ms, detector=detector)

        out_path = out_dir / f"predictions_{interval_ms}ms.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for r in results:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved → {out_path}")

    print(f"\nDone. Results in {out_dir}")


if __name__ == "__main__":
    main()
