"""Run Whisper Large v3 on all 93 gold-92 clips via faster-whisper (local CPU).

Saves outputs to data/whisper_transcripts.json.
Uses faster-whisper with device='cpu', compute_type='int8', language='en'.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

from faster_whisper import WhisperModel
from tqdm import tqdm

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import WHISPER_TRANSCRIPTS

WARMUP_CLIPS = 3  # Number of throwaway clips for cache warming


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Whisper Large v3 on gold-92")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of clips for validation gate (e.g. --limit 5)",
    )
    return parser.parse_args()


def transcribe_clip(
    *,
    model: WhisperModel,
    audio_path: Path,
    clip_id: str,
) -> dict[str, object]:
    """Transcribe a single audio clip with Whisper Large v3.

    Returns dict with clip_id, hypothesis, latency_seconds.
    language='en' is mandatory to prevent accent-misclassification.
    """
    t_start = time.perf_counter()
    segments, _info = model.transcribe(str(audio_path), language="en")
    # Materialise the generator — latency includes full segment decoding
    hypothesis = " ".join(seg.text.strip() for seg in segments)
    latency_seconds = time.perf_counter() - t_start

    if clip_id == CYRILLIC_ANOMALY_CLIP:
        print(
            f"WARNING: Processing anomaly clip {clip_id} — "
            "gold_set.jsonl has Cyrillic ground truth 'ы' for this clip. "
            "Using canonical ground_truth.jsonl reference."
        )

    return {
        "clip_id": clip_id,
        "hypothesis": hypothesis,
        "latency_seconds": latency_seconds,
    }


def main() -> None:
    """Run Whisper Large v3 inference on gold-92 clips."""
    args = parse_args()

    print("Loading Whisper Large v3 model (device=cpu, compute_type=int8)...")
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
    print("Model loaded.")

    clips = load_gold92()
    if args.limit is not None:
        print(f"Running with --limit {args.limit}: processing {len(clips[: args.limit])} clips")

    # Warmup: run WARMUP_CLIPS throwaway clips to warm the cache
    # (only if we're doing a full run, not limited)
    if args.limit is None and len(clips) >= WARMUP_CLIPS:
        print(f"\nWarmup: running {WARMUP_CLIPS} throwaway clips to warm CPU cache...")
        for warmup_clip in clips[:WARMUP_CLIPS]:
            if warmup_clip.audio_path.exists():
                _warmup_segments, _ = model.transcribe(str(warmup_clip.audio_path), language="en")
                _ = list(_warmup_segments)  # materialise
        print("Warmup done.")

    process_clips = clips[: args.limit] if args.limit is not None else clips

    results: list[dict[str, object]] = []
    failed_count = 0

    for i, clip in enumerate(tqdm(process_clips, desc="Whisper Large v3 inference")):
        if not clip.audio_path.exists():
            warnings.warn(
                f"Audio file not found for {clip.clip_id}: {clip.audio_path}",
                stacklevel=2,
            )
            failed_count += 1
            continue

        try:
            result = transcribe_clip(
                model=model,
                audio_path=clip.audio_path,
                clip_id=clip.clip_id,
            )
            results.append(result)

            if (i + 1) % 10 == 0:
                print(f"Whisper: {i + 1}/{len(process_clips)} clips processed")

        except Exception as exc:  # noqa: BLE001
            warnings.warn(f"Whisper transcription failed for {clip.clip_id}: {exc}", stacklevel=2)
            failed_count += 1
            results.append(
                {
                    "clip_id": clip.clip_id,
                    "hypothesis": "",
                    "latency_seconds": 0.0,
                }
            )

    # Rejection check: >20% failures = null results
    total = len(process_clips)
    success_count = total - failed_count
    if total > 0 and success_count / total < 0.8:
        raise RuntimeError(
            f"Rejection criterion triggered: only {success_count}/{total} clips "
            f"({100 * success_count / total:.1f}%) succeeded. "
            "Results are null — check faster-whisper installation and model weights."
        )

    # Save results
    WHISPER_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with WHISPER_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nDone: {success_count}/{total} clips transcribed successfully.")
    print(f"Saved to {WHISPER_TRANSCRIPTS}")
    if failed_count > 0:
        print(f"WARNING: {failed_count} clips failed.")

    # Print first 5 results for individual inspection
    print("\n--- Individual inspection (first 5) ---")
    for r in results[:5]:
        clip_id = r["clip_id"]
        hypothesis = r["hypothesis"]
        latency = r["latency_seconds"]
        print(f"  {clip_id}: '{str(hypothesis)[:80]}...' (latency={latency:.3f}s)")


if __name__ == "__main__":
    main()
