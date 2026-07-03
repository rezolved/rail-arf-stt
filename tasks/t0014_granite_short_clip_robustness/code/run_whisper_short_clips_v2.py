"""Run Whisper turbo on short clips via production-accurate streaming simulation (C001 fix).

Correction C001: replaces run_whisper_short_clips.py which used accumulate-then-transcribe
(base class default). This script replicates the actual WhisperSTT.transcribe_stream() behavior:
chunked re-transcribe — transcribes the growing buffer every CHUNK_SIZE_BYTES.

Uses faster-whisper (same as production), not HuggingFace Transformers.

The multi-GPU faster-whisper bug on this host is avoided by pinning to device_index=0.

Key output fields added vs v1:
  any_intermediate_empty     — True if any intermediate transcription was empty (the primary
                               production failure mode: VAD fires on partial audio before the
                               final chunk arrives)
  any_intermediate_halluc    — True if any intermediate result was a hallucination
  intermediate_count         — number of intermediate transcription passes fired
  final_transcript           — transcript from the final pass on complete audio

is_empty and is_hallucination still refer to the FINAL transcription (consistent with how
production handles the stream's last delta).

Usage (on remote machine, conda stt active):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_whisper_short_clips_v2.py

    # Preflight check (10 clips only):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_whisper_short_clips_v2.py \
        --limit 10
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    BYTES_PER_SAMPLE,
    CHUNK_SIZE_BYTES,
    MIN_SUCCESS_RATE,
    SAMPLE_RATE,
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_INITIAL_PROMPT,
    WHISPER_MODEL_SIZE,
    WHISPER_NO_SPEECH_THRESHOLD,
    WHISPER_TEMPERATURE,
    WHISPER_VAD_FILTER,
)
from tasks.t0014_granite_short_clip_robustness.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    BOH_PATTERNS_CSV,
    DATA_DIR,
    METADATA_JSONL,
)

TRANSCRIPTS_WHISPER_V2 = DATA_DIR / "short_clip_transcripts_whisper_v2.jsonl"

# Pin to single GPU — faster-whisper multi-GPU bug on this host (confirmed t0012/t0014)
WHISPER_DEVICE = "cuda"
WHISPER_DEVICE_INDEX = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Whisper turbo on short clips (C001 fix)")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def load_metadata() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with METADATA_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line.strip()))
    return records


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE)
    return audio


def transcribe_fw(
    model: object,
    audio_float32: np.ndarray,
) -> tuple[str, float]:
    """Transcribe via faster-whisper. Returns (text, max_no_speech_prob)."""
    from faster_whisper import WhisperModel

    fw_model: WhisperModel = model  # type: ignore[assignment]
    segments_iter, _info = fw_model.transcribe(
        audio_float32,
        language="en",
        beam_size=WHISPER_BEAM_SIZE,
        vad_filter=WHISPER_VAD_FILTER,
        initial_prompt=WHISPER_INITIAL_PROMPT,
        temperature=WHISPER_TEMPERATURE,
        no_speech_threshold=WHISPER_NO_SPEECH_THRESHOLD,
    )
    parts: list[str] = []
    max_nsp = 0.0
    n_segs = 0
    for seg in segments_iter:
        parts.append(seg.text.strip())
        max_nsp = max(max_nsp, seg.no_speech_prob)
        n_segs += 1
    if n_segs == 0:
        max_nsp = 1.0
    return " ".join(parts).strip(), max_nsp


def run_chunked_retranscribe(
    model: object,
    audio_float32: np.ndarray,
    detector: HallucinationDetector,
    reference_text: str,
) -> dict[str, object]:
    """Simulate production WhisperSTT.transcribe_stream() chunked re-transcribe pattern.

    Replicates brainpowa-realtime-api/pipeline/stt/whisper.py:transcribe_stream():
      - accumulate chunks
      - every CHUNK_SIZE_BYTES: transcribe growing buffer, record intermediate result
      - final pass on complete audio
    """
    pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
    raw_bytes = pcm_int16.tobytes()
    total_bytes = len(raw_bytes)

    accumulated = bytearray()
    bytes_since_last = 0
    intermediates: list[dict[str, object]] = []

    t_start = time.perf_counter()
    offset = 0

    while offset < total_bytes:
        chunk_end = min(offset + CHUNK_SIZE_BYTES, total_bytes)
        chunk = raw_bytes[offset:chunk_end]
        accumulated.extend(chunk)
        bytes_since_last += len(chunk)
        offset = chunk_end

        if bytes_since_last >= CHUNK_SIZE_BYTES:
            bytes_since_last = 0
            buf_f32 = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            text, nsp = transcribe_fw(model, buf_f32)
            is_empty = len(text) == 0
            is_halluc = detector.is_hallucination(transcript=text, reference_text=reference_text)
            intermediates.append(
                {
                    "bytes": len(accumulated),
                    "text": text,
                    "is_empty": is_empty,
                    "is_hallucination": is_halluc,
                    "no_speech_prob": nsp,
                }
            )

    # Final pass on complete audio
    final_f32 = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
    final_text, final_nsp = transcribe_fw(model, final_f32)
    t_end = time.perf_counter()

    final_empty = len(final_text) == 0
    final_halluc = detector.is_hallucination(transcript=final_text, reference_text=reference_text)

    any_intermediate_empty = any(r["is_empty"] for r in intermediates)
    any_intermediate_halluc = any(r["is_hallucination"] for r in intermediates)

    return {
        "final_transcript": final_text,
        "final_no_speech_prob": final_nsp,
        "is_empty": final_empty,
        "is_hallucination": final_halluc,
        "any_intermediate_empty": any_intermediate_empty,
        "any_intermediate_halluc": any_intermediate_halluc,
        "intermediate_count": len(intermediates),
        "intermediates": intermediates,
        "latency_seconds": t_end - t_start,
        "ttfd_seconds": (t_end - t_start) if not final_empty else None,
    }


def main() -> None:
    from faster_whisper import WhisperModel

    args = parse_args()

    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)
    print(f"BoH: {len(boh_patterns)} patterns loaded")

    metadata = load_metadata()
    if args.limit is not None:
        metadata = metadata[: args.limit]
    print(f"Processing {len(metadata)} clips")

    dev_str = f"{WHISPER_DEVICE}:{WHISPER_DEVICE_INDEX}"
    print(f"Loading faster-whisper {WHISPER_MODEL_SIZE} on {dev_str} ...")
    model = WhisperModel(
        WHISPER_MODEL_SIZE,
        device=WHISPER_DEVICE,
        device_index=WHISPER_DEVICE_INDEX,
        compute_type=WHISPER_COMPUTE_TYPE,
    )
    print("Model loaded.")

    # Warmup
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_fw(model, warmup_audio)
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
            n_chunks = int(np.ceil(len(audio_f32) * BYTES_PER_SAMPLE / CHUNK_SIZE_BYTES))
            run = run_chunked_retranscribe(model, audio_f32, detector, reference_text)

            record = {
                "clip_id": clip_id,
                "duration_s": duration_s,
                "transcript": run["final_transcript"],
                "is_empty": run["is_empty"],
                "is_hallucination": run["is_hallucination"],
                "any_intermediate_empty": run["any_intermediate_empty"],
                "any_intermediate_halluc": run["any_intermediate_halluc"],
                "intermediate_count": run["intermediate_count"],
                "no_speech_probability": run["final_no_speech_prob"],
                "latency_seconds": run["latency_seconds"],
                "ttfd_seconds": run["ttfd_seconds"],
                "num_chunks": n_chunks,
                # Keep intermediates for debugging (strip before final JSONL if too large)
                "intermediates": run["intermediates"],
            }
            results.append(record)

            if (i + 1) % 10 == 0 or i == 0:
                flag = (
                    "EMPTY" if run["is_empty"] else ("HALLUC" if run["is_hallucination"] else "ok")
                )
                inter_flag = "INT-EMPTY" if run["any_intermediate_empty"] else ""
                print(
                    f"  [{i + 1}/{len(metadata)}] {clip_id} ({duration_s}s) "
                    f"n_inter={run['intermediate_count']}: "
                    f"'{str(run['final_transcript'])[:40]}' [{flag}] {inter_flag}"
                )

        except Exception as exc:
            print(f"ERROR on {clip_id}: {exc}")
            errors += 1

    total = len(metadata)
    successful = len(results)
    if total > 0 and (successful / total) < MIN_SUCCESS_RATE:
        raise RuntimeError(
            f"Rejection: only {successful}/{total} clips processed "
            f"(success rate {successful / total:.1%} < {MIN_SUCCESS_RATE:.0%})"
        )

    TRANSCRIPTS_WHISPER_V2.parent.mkdir(parents=True, exist_ok=True)
    with TRANSCRIPTS_WHISPER_V2.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    empties = sum(1 for r in results if r["is_empty"])
    hallucinations = sum(1 for r in results if r["is_hallucination"])
    inter_empties = sum(1 for r in results if r["any_intermediate_empty"])
    inter_halluc = sum(1 for r in results if r["any_intermediate_halluc"])

    n = max(successful, 1)
    print(f"\nWhisper (C001 chunked re-transcribe): {successful}/{total} ({errors} errors)")
    print(f"  Final empty:             {empties}/{successful} ({empties / n:.1%})")
    print(f"  Final hallucination:     {hallucinations}/{successful} ({hallucinations / n:.1%})")
    print(f"  Any intermediate empty:  {inter_empties}/{successful} ({inter_empties / n:.1%})")
    print(f"  Any intermediate halluc: {inter_halluc}/{successful} ({inter_halluc / n:.1%})")

    sub3 = [r for r in results if float(r["duration_s"]) < 3.0]  # type: ignore[arg-type]
    if sub3:
        sub3_inter_empty = sum(1 for r in sub3 if r["any_intermediate_empty"])
        sub3_n = len(sub3)
        sub3_pct = f"{sub3_inter_empty / sub3_n:.1%}"
        print(f"  Sub-3s intermediate empty rate: {sub3_inter_empty}/{sub3_n} ({sub3_pct})")

    lats = [float(r["latency_seconds"]) for r in results]  # type: ignore[arg-type]
    print(f"  Latency p50={np.percentile(lats, 50):.3f}s")
    print(f"Saved → {TRANSCRIPTS_WHISPER_V2}")


if __name__ == "__main__":
    main()
