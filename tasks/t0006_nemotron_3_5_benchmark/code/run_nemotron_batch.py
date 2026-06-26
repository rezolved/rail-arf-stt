"""Run Nemotron 3.5 ASR in batch mode (no biasing) on all 93 gold-92 clips.

Uses the official NeMo cache-aware streaming inference script via manifest.
Model: nvidia/nemotron-3.5-asr-streaming-0.6b (.nemo file).
att_context_size=[56,13] → 1.12s chunks (batch mode, non-streaming measurement).
Saves outputs to data/nemotron_batch_transcripts.json.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import warnings
from pathlib import Path

import soundfile as sf

from tasks.t0006_nemotron_3_5_benchmark.code.constants import MODEL_ID
from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0006_nemotron_3_5_benchmark.code.paths import NEMOTRON_BATCH_TRANSCRIPTS

NEMO_SCRIPT = Path(
    "/home/azureuser/nemo-src/examples/asr/asr_cache_aware_streaming/speech_to_text_cache_aware_streaming_infer.py"
)
ATT_CONTEXT_SIZE = "[56,13]"  # 1.12s chunks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Nemotron 3.5 ASR batch inference on gold-92")
    parser.add_argument("--limit", type=int, default=None, help="Limit clips for validation")
    return parser.parse_args()


def ensure_mono_wav(src: Path, mono_dir: Path) -> Path:
    """Return src if already mono; otherwise write a mono copy to mono_dir and return that."""
    data, sr = sf.read(str(src), always_2d=True)  # shape: (samples, channels)
    if data.shape[1] == 1:
        return src
    mono = data.mean(axis=1)
    dst = mono_dir / src.name
    sf.write(str(dst), mono, sr, subtype="PCM_16")
    return dst


def write_manifest(clips: list, audio_paths: dict[str, Path], path: Path) -> None:
    """Write NeMo manifest JSONL with target_lang=en-US for each clip."""
    with path.open("w", encoding="utf-8") as fh:
        for clip in clips:
            fh.write(
                json.dumps(
                    {
                        "audio_filepath": str(audio_paths[clip.clip_id]),
                        "duration": 30.0,
                        "text": "",
                        "target_lang": "en-US",
                        "clip_id": clip.clip_id,
                    }
                )
                + "\n"
            )


def run_nemo_inference(manifest_path: Path, output_dir: Path) -> Path:
    """Run NeMo streaming inference script. Returns output JSON path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(NEMO_SCRIPT),
        f"model_path={MODEL_ID}",
        f"dataset_manifest={manifest_path}",
        "batch_size=8",
        "target_lang=en-US",
        f"att_context_size={ATT_CONTEXT_SIZE}",
        "strip_lang_tags=true",
        f"output_path={output_dir}",
    ]
    print(f"Running: {' '.join(cmd)}")
    t_start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.perf_counter() - t_start
    if result.returncode != 0:
        raise RuntimeError(f"NeMo inference script failed (exit {result.returncode})")
    print(f"Inference done in {elapsed:.1f}s")

    # Find output file
    out_files = list(output_dir.glob("streaming_out_*.json"))
    if not out_files:
        raise RuntimeError(f"No output file found in {output_dir}")
    return out_files[0]


def parse_nemo_output(
    output_path: Path,
    clips: list,
    total_elapsed: float,
) -> list[dict[str, object]]:
    """Convert NeMo output JSON to our transcript format."""
    with output_path.open(encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]

    n = len(records)
    per_clip_latency = total_elapsed / n if n > 0 else 0.0

    results: list[dict[str, object]] = []
    for clip, record in zip(clips, records, strict=False):
        hypothesis = record.get("pred_text", "")

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": per_clip_latency,
            }
        )

    return results


def main() -> None:
    args = parse_args()
    clips = load_gold92()
    process_clips = clips[: args.limit] if args.limit is not None else clips

    if args.limit is not None:
        print(f"--limit {args.limit}: processing {args.limit} clips")

    # Filter clips with missing audio
    available = [c for c in process_clips if c.audio_path.exists()]
    missing = len(process_clips) - len(available)
    if missing > 0:
        warnings.warn(f"{missing} audio files not found — skipping", stacklevel=2)

    if len(available) == 0:
        raise RuntimeError("No audio files found. Run dvc pull first.")

    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_path = Path(tmpdir) / "manifest.jsonl"
        output_dir = Path(tmpdir) / "output"
        mono_dir = Path(tmpdir) / "mono"
        mono_dir.mkdir()

        audio_paths = {
            c.clip_id: ensure_mono_wav(c.audio_path.resolve(), mono_dir) for c in available
        }
        converted = sum(1 for c in available if audio_paths[c.clip_id] != c.audio_path.resolve())
        if converted:
            print(f"Pre-converted {converted} stereo clips to mono")

        write_manifest(available, audio_paths, manifest_path)
        print(f"Manifest: {len(available)} clips → {manifest_path}")

        t_start = time.perf_counter()
        output_path = run_nemo_inference(manifest_path, output_dir)
        total_elapsed = time.perf_counter() - t_start

        results = parse_nemo_output(output_path, available, total_elapsed)

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    NEMOTRON_BATCH_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with NEMOTRON_BATCH_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nDone: {success}/{total} clips transcribed")
    print(f"Saved to {NEMOTRON_BATCH_TRANSCRIPTS}")

    print("\n--- First 5 results ---")
    for r in results[:5]:
        print(f"  {r['clip_id']}: '{str(r['hypothesis'])[:80]}' ({r['latency_seconds']:.3f}s)")


if __name__ == "__main__":
    main()
