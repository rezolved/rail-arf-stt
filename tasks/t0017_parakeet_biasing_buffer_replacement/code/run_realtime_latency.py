"""Real-time-paced streaming latency for the accuracy winner (+ prod baseline point).

Unlike run_parakeet_buffer_sweep.py (which feeds all audio instantly and measures pure
compute), this paces audio delivery at wall-clock real time: a 20ms frame is released every
20ms of real time (32000 bytes/s at 16kHz int16). Inference blocks the loop, so if a
re-transcribe is slower than real-time frame cadence, subsequent frames are delivered late —
modelling server backpressure exactly as a WebSocket queue would drain after a slow inference.

Metrics per clip (all wall-clock, real-time paced):
    * ttfd_realtime_s      — stream start -> first non-empty delta (perceived time-to-first-word)
    * finalization_s       — end-of-audio-arrival -> final transcript ready (perceived wait
                             after the speaker stops); THIS is the number that must fit the
                             voice-to-action budget
    * total_wall_s         — stream start -> final transcript ready (~= audio_dur + finalization)
    * behind_realtime_s    — how far the stream fell behind real time during speech (backpressure)

Transcripts are identical to the instant-fed run, so accuracy is unchanged — this run only
re-measures latency. Runs unified (winner) across all intervals + tdt at the prod 1000ms
interval as a baseline.

Usage (remote, conda env stt, PYTHONPATH=repo root):
    python -u tasks/t0017_parakeet_biasing_buffer_replacement/code/run_realtime_latency.py
    python -u .../run_realtime_latency.py --limit 3
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import numpy as np

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (
    BUFFER_INTERVALS_MS,
    DOMAIN_VOCAB,
    HF_PARAKEET_TDT,
    HF_PARAKEET_UNIFIED,
    INTERVAL_BYTES,
    MIN_SUCCESS_RATE,
    PARAKEET_BOOSTING_ALPHA,
    SAMPLE_RATE,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import DATA_DIR
from tasks.t0017_parakeet_biasing_buffer_replacement.code.run_parakeet_buffer_sweep import (
    _extract_delta,
    apply_boosting,
    expand_casing_variants,
    load_audio_float32,
    load_gold92_clips,
    transcribe_buffer,
)

BYTES_PER_SEC: int = SAMPLE_RATE * 2  # int16
FRAME_BYTES: int = 640  # 20ms at 16kHz int16 — approximates continuous WebSocket arrival
FRAME_DUR_S: float = FRAME_BYTES / BYTES_PER_SEC


def stream_one_clip(model: Any, raw_bytes: bytes, *, interval_bytes: int) -> dict[str, float]:
    """Stream one clip at real-time pace; return wall-clock latency metrics."""
    accumulated = bytearray()
    bytes_since_last = 0
    prev_transcript = ""
    ttfd_realtime: float | None = None
    max_behind = 0.0

    t0 = time.perf_counter()
    offset = 0
    n_frames = 0
    while offset < len(raw_bytes):
        # Scheduled real-time arrival of this frame; sleep only if we are ahead of schedule.
        scheduled = t0 + (offset / BYTES_PER_SEC)
        dt = scheduled - time.perf_counter()
        if dt > 0:
            time.sleep(dt)
        else:
            # We are behind real time (previous inference overran) — backpressure.
            max_behind = max(max_behind, -dt)

        frame = raw_bytes[offset : offset + FRAME_BYTES]
        accumulated.extend(frame)
        bytes_since_last += len(frame)
        offset += FRAME_BYTES
        n_frames += 1

        if bytes_since_last >= interval_bytes:
            bytes_since_last = 0
            acc_f32 = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            text = transcribe_buffer(model, acc_f32)
            delta = _extract_delta(prev_transcript, text)
            if delta.strip():
                if ttfd_realtime is None:
                    ttfd_realtime = time.perf_counter() - t0
                prev_transcript = text

    # End-of-audio arrival in real time = when the last sample would have arrived.
    audio_dur = len(raw_bytes) / BYTES_PER_SEC
    t_end_audio = t0 + audio_dur

    final_f32 = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
    final_text = transcribe_buffer(model, final_f32)
    t_final = time.perf_counter()

    if ttfd_realtime is None:
        ttfd_realtime = t_final - t0

    return {
        "final_text": final_text,
        "ttfd_realtime_s": round(ttfd_realtime, 4),
        "finalization_s": round(t_final - t_end_audio, 4),
        "total_wall_s": round(t_final - t0, 4),
        "behind_realtime_s": round(max_behind, 4),
        "audio_dur_s": round(audio_dur, 3),
    }


def run_variant(
    model: Any,
    clips: list[dict[str, Any]],
    *,
    model_slug: str,
    interval_ms: int,
) -> list[dict[str, Any]]:
    interval_bytes = INTERVAL_BYTES[interval_ms]
    results: list[dict[str, Any]] = []
    for i, clip in enumerate(clips):
        audio_f32 = load_audio_float32(clip["audio_path"])
        pcm = (audio_f32 * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
        m = stream_one_clip(model, pcm, interval_bytes=interval_bytes)
        results.append(
            {
                "clip_id": clip["clip_id"],
                "transcript": m["final_text"],
                "reference_text": clip["reference_text"],
                "interval_ms": interval_ms,
                "ttfd_realtime_s": m["ttfd_realtime_s"],
                "finalization_s": m["finalization_s"],
                "total_wall_s": m["total_wall_s"],
                "behind_realtime_s": m["behind_realtime_s"],
                "audio_dur_s": m["audio_dur_s"],
            }
        )
        if (i + 1) % 30 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(clips)}] {clip['clip_id']}: "
                f"ttfd={m['ttfd_realtime_s']:.3f}s final={m['finalization_s']:.3f}s "
                f"behind={m['behind_realtime_s']:.3f}s"
            )

    if len(results) / max(len(clips), 1) < MIN_SUCCESS_RATE:
        raise RuntimeError(f"Rejection: {len(results)}/{len(clips)} processed")

    fins = [r["finalization_s"] for r in results]
    ttfds = [r["ttfd_realtime_s"] for r in results]
    behinds = [r["behind_realtime_s"] for r in results]
    print(
        f"  {model_slug} {interval_ms}ms: finalization p50={np.percentile(fins, 50):.3f}s "
        f"p95={np.percentile(fins, 95):.3f}s | ttfd_rt p50={np.percentile(ttfds, 50):.3f}s | "
        f"max_behind p95={np.percentile(behinds, 95):.3f}s"
    )
    return results


def load_model(hf_id: str) -> Any:
    import torch
    from nemo.collections.asr.models import ASRModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ASRModel.from_pretrained(model_name=hf_id, map_location=device).to(device)
    model.eval()
    apply_boosting(model, expand_casing_variants(DOMAIN_VOCAB), alpha=PARAKEET_BOOSTING_ALPHA)
    warm = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_buffer(model, warm)
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Real-time-paced latency (t0017)")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    clips = load_gold92_clips(limit=args.limit)
    print(f"Clips: {len(clips)}  (frame={FRAME_BYTES}B/{FRAME_DUR_S * 1000:.0f}ms real-time paced)")

    out_dir = DATA_DIR / "realtime_latency"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Winner (unified) across all intervals.
    print("\n########## WINNER parakeet-unified-en-0.6b (all intervals, real-time) ##########")
    uni = load_model(HF_PARAKEET_UNIFIED)
    for interval_ms in BUFFER_INTERVALS_MS:
        print(f"\n=== unified | {interval_ms}ms ===")
        rows = run_variant(uni, clips, model_slug="parakeet-unified", interval_ms=interval_ms)
        path = out_dir / f"unified_{interval_ms}ms.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved → {path}")
    del uni

    import torch

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Prod baseline point: tdt at 1000ms.
    print("\n########## BASELINE parakeet-tdt-0.6b-v3 @1000ms (real-time) ##########")
    tdt = load_model(HF_PARAKEET_TDT)
    rows = run_variant(tdt, clips, model_slug="parakeet-tdt", interval_ms=1000)
    path = out_dir / "tdt_1000ms.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved → {path}")

    print("\nAll done.")


if __name__ == "__main__":
    main()
