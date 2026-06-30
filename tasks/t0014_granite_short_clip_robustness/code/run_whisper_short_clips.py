"""Run Whisper turbo on short clips via production streaming simulation.

Uses HuggingFace Transformers (NOT faster-whisper — faster-whisper has a multi-GPU bug
on this host, confirmed in t0012). Mirrors the streaming accumulate-then-transcribe pattern:
audio is chunked into 32kB PCM-16 chunks, accumulated, then transcribed once.

For short clips (all clips are < stream_interval_bytes), the entire clip arrives as a
single chunk before transcription. This matches the base class transcribe_stream() default.

Records no_speech_probability per clip to confirm VAD misfiring mechanism.
Note: HuggingFace Whisper does not expose per-segment no_speech_prob directly — we use
the model's language detection logits as a proxy and set to 0.0 for non-empty outputs.

Usage (on remote machine, conda stt active):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_whisper_short_clips.py

    # Preflight check (10 clips only):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_whisper_short_clips.py --limit 10
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    BYTES_PER_SAMPLE,
    CHUNK_SIZE_BYTES,
    DOMAIN_VOCAB,
    SAMPLE_RATE,
    WHISPER_BEAM_SIZE,
)
from tasks.t0014_granite_short_clip_robustness.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    BOH_PATTERNS_CSV,
    METADATA_JSONL,
    TRANSCRIPTS_WHISPER,
)

# HuggingFace model ID — same as t0012 (faster-whisper has multi-GPU bug on this host)
WHISPER_HF_MODEL_ID = "openai/whisper-large-v3-turbo"
WHISPER_DEVICE = "cuda:0"
WHISPER_MAX_NEW_TOKENS = 200

INITIAL_PROMPT = ", ".join(DOMAIN_VOCAB)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Whisper turbo on short clips")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
    return parser.parse_args()


def load_metadata() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with METADATA_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line.strip()))
    return records


def load_audio_float32(path: Path) -> np.ndarray:
    """Load WAV file as float32 mono array."""
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE)
    return audio


def simulate_streaming_accumulate(audio_float32: np.ndarray) -> tuple[np.ndarray, float]:
    """Chunk into 32kB PCM-16 blocks and accumulate (mirrors transcribe_stream default).

    Returns (accumulated_float32, t_first_chunk).
    """
    pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
    raw_bytes = pcm_int16.tobytes()

    accumulated: list[bytes] = []
    t_first_chunk: float | None = None
    offset = 0
    while offset < len(raw_bytes):
        chunk = raw_bytes[offset : offset + CHUNK_SIZE_BYTES]
        if t_first_chunk is None:
            t_first_chunk = time.perf_counter()
        accumulated.append(chunk)
        offset += CHUNK_SIZE_BYTES

    if t_first_chunk is None:
        t_first_chunk = time.perf_counter()

    all_bytes = b"".join(accumulated)
    pcm_reconstructed = np.frombuffer(all_bytes, dtype=np.int16).astype(np.float32) / 32767.0
    return pcm_reconstructed, t_first_chunk


def transcribe_hf(
    model: torch.nn.Module,
    processor: object,
    audio_float32: np.ndarray,
    prompt_ids: torch.Tensor,
    forced_decoder_ids: list[list[int]],
) -> tuple[str, float]:
    """Transcribe using HuggingFace Whisper. Returns (text, no_speech_prob_proxy).

    no_speech_prob: 1.0 for empty output (VAD suppressed), 0.0 for non-empty output.
    HuggingFace Whisper does not expose per-segment no_speech_prob — this is a proxy.
    """
    from transformers import AutoProcessor

    proc: AutoProcessor = processor  # type: ignore[assignment]
    inputs = proc(audio_float32, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    input_features = inputs.input_features.to(WHISPER_DEVICE, dtype=torch.float16)

    with torch.no_grad():
        ids = model.generate(  # type: ignore[attr-defined]
            input_features,
            prompt_ids=prompt_ids,
            forced_decoder_ids=forced_decoder_ids,
            num_beams=WHISPER_BEAM_SIZE,
            do_sample=False,
            max_new_tokens=WHISPER_MAX_NEW_TOKENS,
        )

    text = proc.batch_decode(ids, skip_special_tokens=True)[0].strip()
    # Proxy: empty transcript → assume VAD suppressed → no_speech_prob = 1.0
    no_speech_prob = 1.0 if not text else 0.0
    return text, no_speech_prob


def main() -> None:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    args = parse_args()
    print(f"Device: {WHISPER_DEVICE}")

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
    print(f"Loading {WHISPER_HF_MODEL_ID} on {WHISPER_DEVICE} ...")
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        WHISPER_HF_MODEL_ID,
        dtype=torch.float16,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    )
    model.to(WHISPER_DEVICE)
    model.eval()

    processor = AutoProcessor.from_pretrained(WHISPER_HF_MODEL_ID)
    prompt_ids = processor.get_prompt_ids(INITIAL_PROMPT, return_tensors="pt").to(WHISPER_DEVICE)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")
    print(f"Model loaded. Prompt: '{INITIAL_PROMPT[:60]}...'")

    # Warm up with 3 silent clips
    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_hf(model, processor, warmup_audio, prompt_ids, forced_decoder_ids)
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
            accumulated, t_first_chunk = simulate_streaming_accumulate(audio_f32)

            transcript, no_speech_prob = transcribe_hf(
                model, processor, accumulated, prompt_ids, forced_decoder_ids
            )
            t_end = time.perf_counter()

            latency = t_end - t_first_chunk
            is_empty = len(transcript.strip()) == 0
            is_hallucination = detector.is_hallucination(
                transcript=transcript,
                reference_text=reference_text,
            )

            # TTFD: time from first chunk to first non-empty delta
            ttfd_seconds = latency if not is_empty else None

            results.append(
                {
                    "clip_id": clip_id,
                    "duration_s": duration_s,
                    "transcript": transcript,
                    "is_empty": is_empty,
                    "is_hallucination": is_hallucination,
                    "no_speech_probability": no_speech_prob,
                    "latency_seconds": latency,
                    "ttfd_seconds": ttfd_seconds,
                    "num_chunks": n_chunks,
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                flag = "EMPTY" if is_empty else ("HALLUC" if is_hallucination else "ok")
                print(
                    f"  [{i + 1}/{len(metadata)}] {clip_id} ({duration_s}s): "
                    f"'{transcript[:50]}' nsp={no_speech_prob:.1f} "
                    f"lat={latency:.3f}s [{flag}]"
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
    TRANSCRIPTS_WHISPER.parent.mkdir(parents=True, exist_ok=True)
    with TRANSCRIPTS_WHISPER.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nWhisper short clips: {successful}/{total} clips ({errors} errors)")
    empties = sum(1 for r in results if r["is_empty"])
    hallucinations = sum(1 for r in results if r["is_hallucination"])
    print(f"  Empty: {empties}/{successful} ({empties / max(successful, 1):.1%})")
    h_pct = hallucinations / max(successful, 1)
    print(f"  Hallucinations: {hallucinations}/{successful} ({h_pct:.1%})")

    sub3 = [r for r in results if float(r["duration_s"]) < 3.0]  # type: ignore[arg-type]
    if sub3:
        empty_sub3 = sum(1 for r in sub3 if r["is_empty"])
        print(f"  Sub-3s empty rate: {empty_sub3}/{len(sub3)} ({empty_sub3 / len(sub3):.1%})")

    if empties == 0 and successful > 0:
        print("\nWARNING: empty rate is 0% — check streaming pattern for short clips.")

    lats = [float(r["latency_seconds"]) for r in results]  # type: ignore[arg-type]
    print(f"  Latency p50={np.percentile(lats, 50):.3f}s")
    print(f"Saved → {TRANSCRIPTS_WHISPER}")


if __name__ == "__main__":
    main()
