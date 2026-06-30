"""Run Granite Speech 4.1 2B on short clips via production streaming simulation.

Uses the base class STTAdapter.transcribe_stream() default (accumulate-then-transcribe):
accumulates all PCM-16 chunks from a 32kB-chunk queue into a buffer, then calls
transcribe() once on the complete audio.

This structurally avoids VAD misfiring because no intermediate transcription pass fires
on partial buffers. The expected failure mode for sub-1s clips is empty output (insufficient
Q-Former embeddings), not hallucination.

Keyword prompt injection: "transcribe the speech to text. Keywords: <31 domain terms>"
(same as t0012 best variant).

Usage (on remote machine, conda stt active):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_granite_short_clips.py

    # Preflight check (10 clips only):
    python -u tasks/t0014_granite_short_clip_robustness/code/run_granite_short_clips.py --limit 10
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
    GRANITE_KEYWORD_PROMPT,
    GRANITE_MAX_NEW_TOKENS,
    GRANITE_WARMUP_CLIPS,
    REMOTE_GRANITE_MODEL,
    SAMPLE_RATE,
)
from tasks.t0014_granite_short_clip_robustness.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    BOH_PATTERNS_CSV,
    METADATA_JSONL,
    TRANSCRIPTS_GRANITE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Granite on short clips")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
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


def simulate_streaming_accumulate(audio_float32: np.ndarray) -> tuple[torch.Tensor, float]:
    """Chunk PCM-16 bytes and accumulate (mirrors STTAdapter.transcribe_stream default).

    Returns (wav_tensor [1, samples], t_first_chunk).
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
    wav_tensor = torch.from_numpy(pcm_reconstructed).unsqueeze(0)
    return wav_tensor, t_first_chunk


def load_model(device: str) -> tuple[object, object]:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    print(f"Loading model from {REMOTE_GRANITE_MODEL} ...")
    processor = AutoProcessor.from_pretrained(REMOTE_GRANITE_MODEL)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        REMOTE_GRANITE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()  # type: ignore[union-attr]
    print("Model loaded.")
    return model, processor


def transcribe_clip(
    model: object,
    processor: object,
    wav: torch.Tensor,
    prompt: str,
    device: str,
) -> str:
    tokenizer = processor.tokenizer  # type: ignore[union-attr]
    chat = [{"role": "user", "content": f"<|audio|>{prompt}"}]
    prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    model_inputs = processor(prompt_text, wav, device=device, return_tensors="pt").to(device)  # type: ignore[union-attr]

    with torch.inference_mode():
        output_ids = model.generate(  # type: ignore[union-attr]
            **model_inputs,
            max_new_tokens=GRANITE_MAX_NEW_TOKENS,
            do_sample=False,
            num_beams=1,
        )

    num_input = model_inputs["input_ids"].shape[-1]
    new_tokens = output_ids[0, num_input:].unsqueeze(0)
    decoded = tokenizer.batch_decode(new_tokens, add_special_tokens=False, skip_special_tokens=True)
    return decoded[0].strip()


def main() -> None:
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Prompt: '{GRANITE_KEYWORD_PROMPT[:80]}...'")

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
    model, processor = load_model(device)

    # Warmup
    print(f"Warming up ({GRANITE_WARMUP_CLIPS} clips) ...")
    warmup_wav = torch.zeros(1, SAMPLE_RATE, dtype=torch.float32)
    for _ in range(GRANITE_WARMUP_CLIPS):
        transcribe_clip(model, processor, warmup_wav, GRANITE_KEYWORD_PROMPT, device)
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
            wav_tensor, t_first_chunk = simulate_streaming_accumulate(audio_f32)

            transcript = transcribe_clip(
                model, processor, wav_tensor, GRANITE_KEYWORD_PROMPT, device
            )
            t_end = time.perf_counter()

            latency = t_end - t_first_chunk
            is_empty = len(transcript.strip()) == 0
            is_hallucination = detector.is_hallucination(
                transcript=transcript,
                reference_text=reference_text,
            )
            ttfd_seconds = latency if not is_empty else None

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
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                flag = "EMPTY" if is_empty else ("HALLUC" if is_hallucination else "ok")
                print(
                    f"  [{i + 1}/{len(metadata)}] {clip_id} ({duration_s}s): "
                    f"'{transcript[:50]}' lat={latency:.3f}s [{flag}]"
                )

            # Latency validation gate on first 10 clips
            if i == 9 and latency > 2.0:
                print(
                    f"WARNING: Granite latency {latency:.3f}s on 0.5s clip — "
                    "check HuggingFace Transformers fixed overhead"
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

    if successful > 0 and all(r["is_empty"] for r in results):
        raise RuntimeError("Rejection: all clips returned empty transcript — pipeline bug")

    # Save results
    TRANSCRIPTS_GRANITE.parent.mkdir(parents=True, exist_ok=True)
    with TRANSCRIPTS_GRANITE.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nGranite short clips: {successful}/{total} clips ({errors} errors)")
    empties = sum(1 for r in results if r["is_empty"])
    hallucinations = sum(1 for r in results if r["is_hallucination"])
    print(f"  Empty: {empties}/{successful} ({empties / max(successful, 1):.1%})")
    h_pct = hallucinations / max(successful, 1)
    print(f"  Hallucinations: {hallucinations}/{successful} ({h_pct:.1%})")

    lats = [float(r["latency_seconds"]) for r in results]  # type: ignore[arg-type]
    print(f"  Latency p50={np.percentile(lats, 50):.3f}s")
    print(f"Saved → {TRANSCRIPTS_GRANITE}")


if __name__ == "__main__":
    main()
