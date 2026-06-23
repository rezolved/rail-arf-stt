"""Run Deepgram Nova-2 on all 93 gold-92 clips via the cloud API.

Saves raw responses to data/deepgram_transcripts.json.
Uses deepgram-sdk>=7.0 with client.listen.v1.media.transcribe_file() keyword API.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import warnings
from pathlib import Path
from typing import Any

from deepgram import DeepgramClient
from tqdm import tqdm

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import DEEPGRAM_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Deepgram Nova-2 on gold-92")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of clips for validation gate (e.g. --limit 5)",
    )
    return parser.parse_args()


def _serialize_response(response: Any) -> dict[str, Any]:
    """Safely serialize a Deepgram response to a plain dict."""
    try:
        if hasattr(response, "to_dict"):
            result: dict[str, Any] = response.to_dict()
            return result
        elif hasattr(response, "model_dump"):
            result = response.model_dump()
            return result
    except Exception:  # noqa: BLE001
        pass
    return {}


def transcribe_clip(
    *,
    client: DeepgramClient,
    audio_path: Path,
    clip_id: str,
) -> dict[str, Any]:
    """Transcribe a single audio clip using Deepgram Nova-2.

    Returns dict with clip_id, hypothesis, latency_seconds, raw_response.
    """
    audio_bytes = audio_path.read_bytes()

    t_start = time.perf_counter()
    response = client.listen.v1.media.transcribe_file(
        request=audio_bytes,
        model="nova-2",
        smart_format=True,
        punctuate=True,
    )
    latency_seconds = time.perf_counter() - t_start

    # Extract transcript from response
    hypothesis = ""
    try:
        channels = response.results.channels
        if len(channels) > 0 and len(channels[0].alternatives) > 0:
            transcript = channels[0].alternatives[0].transcript
            hypothesis = transcript if transcript is not None else ""
    except (AttributeError, IndexError) as exc:
        warnings.warn(f"Failed to extract transcript for {clip_id}: {exc}", stacklevel=2)

    if clip_id == CYRILLIC_ANOMALY_CLIP:
        print(
            f"WARNING: Processing anomaly clip {clip_id} — "
            "gold_set.jsonl has Cyrillic ground truth 'ы' for this clip. "
            "Using canonical ground_truth.jsonl reference instead."
        )

    raw_response_dict = _serialize_response(response)

    return {
        "clip_id": clip_id,
        "hypothesis": hypothesis,
        "latency_seconds": latency_seconds,
        "raw_response": raw_response_dict,
    }


def main() -> None:
    """Run Deepgram inference on gold-92 clips."""
    args = parse_args()

    api_key = os.environ.get("DEEPGRAM_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "DEEPGRAM_API_KEY environment variable is not set. "
            "Please set it before running this script."
        )

    client = DeepgramClient(api_key=api_key)

    clips = load_gold92()
    if args.limit is not None:
        clips = clips[: args.limit]
        print(f"Running with --limit {args.limit}: processing {len(clips)} clips")

    results: list[dict[str, Any]] = []
    failed_count = 0

    for clip in tqdm(clips, desc="Deepgram Nova-2 inference"):
        if not clip.audio_path.exists():
            warnings.warn(
                f"Audio file not found for {clip.clip_id}: {clip.audio_path}",
                stacklevel=2,
            )
            failed_count += 1
            continue

        try:
            result = transcribe_clip(
                client=client,
                audio_path=clip.audio_path,
                clip_id=clip.clip_id,
            )
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            warnings.warn(f"Deepgram API call failed for {clip.clip_id}: {exc}", stacklevel=2)
            failed_count += 1
            results.append(
                {
                    "clip_id": clip.clip_id,
                    "hypothesis": "",
                    "latency_seconds": 0.0,
                    "raw_response": {"error": str(exc)},
                }
            )

    # Rejection check: >20% failures = null results
    total = len(clips)
    success_count = total - failed_count
    if total > 0 and success_count / total < 0.8:
        raise RuntimeError(
            f"Rejection criterion triggered: only {success_count}/{total} clips "
            f"({100 * success_count / total:.1f}%) succeeded. "
            "Results are null — check Deepgram API key and connectivity."
        )

    # Save results
    DEEPGRAM_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with DEEPGRAM_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nDone: {success_count}/{total} clips transcribed successfully.")
    print(f"Saved to {DEEPGRAM_TRANSCRIPTS}")
    if failed_count > 0:
        print(f"WARNING: {failed_count} clips failed.")

    # Print first 5 results for individual inspection
    print("\n--- Individual inspection (first 5) ---")
    for r in results[:5]:
        clip_id_val = r["clip_id"]
        hypothesis_val = r["hypothesis"]
        latency_val = r["latency_seconds"]
        print(f"  {clip_id_val}: '{str(hypothesis_val)[:80]}...' (latency={latency_val:.3f}s)")


if __name__ == "__main__":
    main()
