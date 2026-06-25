"""Run Moonshine Streaming Medium inference on all 93 gold-92 clips.

Uses UsefulSensors/moonshine-streaming-medium via HuggingFace Transformers.
Outputs: tasks/t0008_moonshine_v2_benchmark/data/moonshine_v2_medium_transcripts.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import torch
from transformers import (  # type: ignore[attr-defined]
    AutoProcessor,
    MoonshineStreamingForConditionalGeneration,
)

from tasks.t0008_moonshine_v2_benchmark.code.paths import (
    DATA_DIR,
    GOLD92_AUDIO,
    GROUND_TRUTH_JSONL,
    MOONSHINE_V2_TRANSCRIPTS,
)

MODEL_NAME = "UsefulSensors/moonshine-streaming-medium"


def load_clip_ids(ground_truth_path: Path) -> list[str]:
    """Load clip IDs from ground_truth.jsonl."""
    clip_ids: list[str] = []
    with ground_truth_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            clip_ids.append(record["clip_id"])
    clip_ids.sort()
    return clip_ids


def get_latency_stage(index: int) -> str:
    """Classify latency stage by clip index."""
    if index == 0:
        return "cold_start"
    if index < 5:
        return "warmup"
    return "warmed"


def transcribe_clip(
    *,
    audio_path: Path,
    model: MoonshineStreamingForConditionalGeneration,
    processor: AutoProcessor,
) -> tuple[str, float]:
    """Load audio, run inference, return (hypothesis, latency_seconds)."""
    # Load audio at 16kHz mono using librosa
    audio_array, _ = librosa.load(str(audio_path), sr=16000, mono=True)
    audio_np = audio_array.astype(np.float32)

    # Process inputs
    inputs = processor(
        audio_np,
        sampling_rate=16000,
        return_tensors="pt",
    )

    # Compute max_length from token_limit_factor per the README example
    token_limit_factor = 6.5 / processor.feature_extractor.sampling_rate
    max_length = int(audio_np.shape[0] * token_limit_factor) + 10

    start_time = time.perf_counter()
    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_values"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=max_length,
        )
    elapsed = time.perf_counter() - start_time

    # Decode output
    transcription: str = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return transcription.strip(), elapsed


def main(limit: int | None = None) -> None:
    """Run inference on gold-92 clips and save results."""
    from arf.scripts.utils.heartbeat import write_heartbeat

    write_heartbeat(
        task_id="t0008_moonshine_v2_benchmark", step_number=5, current_owner="implementation"
    )

    print(f"Loading model: {MODEL_NAME}")
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = MoonshineStreamingForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.eval()
    print("Model loaded.")

    write_heartbeat(
        task_id="t0008_moonshine_v2_benchmark", step_number=5, current_owner="implementation"
    )

    # Load clip IDs
    clip_ids = load_clip_ids(GROUND_TRUTH_JSONL)
    if limit is not None:
        clip_ids = clip_ids[:limit]
    print(f"Running inference on {len(clip_ids)} clips...")

    results: list[dict[str, Any]] = []
    failures = 0

    for idx, clip_id in enumerate(clip_ids):
        audio_path = GOLD92_AUDIO / f"{clip_id}.wav"

        if not audio_path.exists():
            print(f"  WARNING: audio file not found: {audio_path}")
            failures += 1
            results.append(
                {
                    "clip_id": clip_id,
                    "hypothesis": "",
                    "latency_seconds": 0.0,
                    "latency_stage": get_latency_stage(idx),
                }
            )
            continue

        try:
            hypothesis, latency = transcribe_clip(
                audio_path=audio_path,
                model=model,
                processor=processor,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR transcribing {clip_id}: {exc}")
            failures += 1
            results.append(
                {
                    "clip_id": clip_id,
                    "hypothesis": "",
                    "latency_seconds": 0.0,
                    "latency_stage": get_latency_stage(idx),
                }
            )
            continue

        results.append(
            {
                "clip_id": clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
                "latency_stage": get_latency_stage(idx),
            }
        )

        if (idx + 1) % 10 == 0:
            print(f"  [{idx + 1}/{len(clip_ids)}] Last: {clip_id!r} -> {hypothesis[:60]!r}")
            write_heartbeat(
                task_id="t0008_moonshine_v2_benchmark",
                step_number=5,
                current_owner="implementation",
            )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with MOONSHINE_V2_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} records to {MOONSHINE_V2_TRANSCRIPTS}")
    print(f"Failures: {failures}/{len(clip_ids)}")

    if results:
        sample = results[5] if len(results) > 5 else results[0]
        print(f"Sample (idx 5): {sample['clip_id']!r} -> {sample['hypothesis'][:80]!r}")

    write_heartbeat(
        task_id="t0008_moonshine_v2_benchmark", step_number=5, current_owner="implementation"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Moonshine v2 Medium inference on gold-92")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips to process")
    args = parser.parse_args()
    main(limit=args.limit)
