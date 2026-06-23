"""Run Moonshine base (ONNX) on all gold-92 clips.

Moonshine does not support initial_prompt/vocabulary biasing, so this run
is a plain baseline. Results are saved to data/moonshine_base_transcripts.json.

Note: UsefulSensors/moonshine has no "small" variant. Available models are
"tiny" (~27M) and "base" (~60M). Using "base" as the closest equivalent.

Uses: useful-moonshine-onnx (moonshine_onnx package).
Model: moonshine/base (~60M parameters, CPU-optimised).
"""

from __future__ import annotations

import json
import time

from moonshine_onnx import MoonshineOnnxModel, load_audio, load_tokenizer

from tasks.t0004_vocabulary_biasing_experiment.code.paths import (
    GOLD92_AUDIO,
    GROUND_TRUTH_JSONL,
    MOONSHINE_TRANSCRIPTS,
)

MODEL_NAME = "moonshine/base"


def main() -> None:
    clip_ids: list[str] = []
    with GROUND_TRUTH_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                record = json.loads(line)
                clip_ids.append(record["clip_id"])

    print(f"Loading Moonshine ONNX model: {MODEL_NAME}")
    model = MoonshineOnnxModel(model_name=MODEL_NAME)
    tokenizer = load_tokenizer()

    results: list[dict] = []
    failed: list[str] = []

    for i, clip_id in enumerate(clip_ids, 1):
        audio_path = GOLD92_AUDIO / f"{clip_id}.wav"
        if not audio_path.exists():
            print(f"  [{i}/{len(clip_ids)}] MISSING: {clip_id}")
            failed.append(clip_id)
            continue

        try:
            # load_audio uses librosa: resamples to 16 kHz, returns [1, num_samples]
            audio = load_audio(str(audio_path))
            start = time.perf_counter()
            tokens = model.generate(audio)
            text = tokenizer.decode_batch(tokens)[0]
            latency = time.perf_counter() - start

            results.append(
                {
                    "clip_id": clip_id,
                    "hypothesis": text.strip(),
                    "latency_seconds": latency,
                }
            )

            if i % 10 == 0 or i == len(clip_ids):
                print(f"  [{i}/{len(clip_ids)}] {clip_id}: {text.strip()[:60]!r}")

        except Exception as exc:  # noqa: BLE001
            print(f"  [{i}/{len(clip_ids)}] ERROR {clip_id}: {exc}")
            failed.append(clip_id)

    MOONSHINE_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with MOONSHINE_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(results)} transcripts to {MOONSHINE_TRANSCRIPTS}")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
