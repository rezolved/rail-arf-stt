"""Run Granite Speech 4.1 2B in production chunked re-transcribe mode on gold-92.

Mirrors the chunked streaming pattern from ParakeetSTT.transcribe_stream() in brainpowa:
  - Every STREAM_INTERVAL_BYTES of accumulated PCM-16 audio: transcribe full buffer,
    extract delta (word-level LCP matching), yield delta if non-empty.
  - Final transcribe on complete audio after all chunks delivered.
  - Latency: wall-clock from first chunk to final transcript returned.
  - TTFD: first chunk to first non-empty delta.

Complements run_streaming_granite.py (accumulate-then-transcribe) to enable
fair latency and TTFD comparison against Parakeet chunked.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0012_whisper_parakeet_granite_streaming.code.constants import (
    BYTES_PER_SAMPLE,
    DOMAIN_VOCAB,
    GRANITE_MAX_NEW_TOKENS,
    GRANITE_MODEL_LOCAL_DIR,
    GRANITE_PROMPT_BIASED_PREFIX,
    GRANITE_WARMUP_CLIPS,
    SAMPLE_RATE,
    STREAM_INTERVAL_BYTES,
)
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import GRANITE_CHUNKED_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Granite chunked re-transcribe on gold-92")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def build_biased_prompt(vocab: list[str]) -> str:
    return GRANITE_PROMPT_BIASED_PREFIX + ", ".join(vocab)


def load_model(device: str) -> tuple:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    print(f"Loading model from {GRANITE_MODEL_LOCAL_DIR} ...")
    processor = AutoProcessor.from_pretrained(GRANITE_MODEL_LOCAL_DIR)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        GRANITE_MODEL_LOCAL_DIR,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()
    print("Model loaded.")
    return model, processor


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_buffer(
    model: object, processor: object, audio_float32: np.ndarray, prompt: str, device: str
) -> str:
    wav = torch.from_numpy(audio_float32).unsqueeze(0)
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


def _extract_delta(previous: str, current: str) -> str:
    """Word-level LCP delta extraction — mirrors WhisperSTT._extract_delta() from brainpowa."""
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


def main() -> None:
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    clips = load_gold92()
    process_clips = clips[: args.limit] if args.limit is not None else clips
    available = [c for c in process_clips if c.audio_path.exists()]
    missing = len(process_clips) - len(available)
    if missing > 0:
        warnings.warn(f"{missing} audio files not found — skipping", stacklevel=2)
    if len(available) == 0:
        raise RuntimeError("No audio files found. Run dvc pull first.")

    model, processor = load_model(device)

    biased_prompt = build_biased_prompt(DOMAIN_VOCAB)
    print(f"Prompt: '{biased_prompt[:100]}...'")

    print(f"Warming up on {GRANITE_WARMUP_CLIPS} clips ...")
    for clip in available[:GRANITE_WARMUP_CLIPS]:
        audio_f32 = load_audio_float32(clip.audio_path)
        transcribe_buffer(model, processor, audio_f32, biased_prompt, device)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    num_chunks_per_clip: list[int] = []

    for i, clip in enumerate(available):
        audio_float32 = load_audio_float32(clip.audio_path)
        raw_bytes_len = len(audio_float32) * BYTES_PER_SAMPLE
        n_chunks = int(np.ceil(raw_bytes_len / STREAM_INTERVAL_BYTES))
        num_chunks_per_clip.append(n_chunks)
        audio_duration = len(audio_float32) / SAMPLE_RATE

        # Simulate streaming: deliver int16 PCM chunks, accumulate, re-transcribe per interval
        pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
        raw_bytes = pcm_int16.tobytes()

        accumulated = bytearray()
        bytes_since_last: int = 0
        prev_transcript: str = ""
        t_first_chunk: float | None = None
        ttfd: float | None = None

        offset = 0
        while offset < len(raw_bytes):
            chunk = raw_bytes[offset : offset + STREAM_INTERVAL_BYTES]
            if t_first_chunk is None:
                t_first_chunk = time.perf_counter()
            accumulated.extend(chunk)
            bytes_since_last += len(chunk)
            offset += STREAM_INTERVAL_BYTES

            if bytes_since_last >= STREAM_INTERVAL_BYTES:
                bytes_since_last = 0
                acc_float = (
                    np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
                )
                text = transcribe_buffer(model, processor, acc_float, biased_prompt, device)
                delta_text = _extract_delta(prev_transcript, text)
                if delta_text.strip():
                    if ttfd is None:
                        ttfd = time.perf_counter() - t_first_chunk  # type: ignore[operator]
                    prev_transcript = text

        # Final transcribe on complete buffer
        assert t_first_chunk is not None
        final_float = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
        final_text = transcribe_buffer(model, processor, final_float, biased_prompt, device)
        t_end = time.perf_counter()
        latency = t_end - t_first_chunk

        if ttfd is None:
            ttfd = latency

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": final_text,
                "latency_seconds": latency,
                "ttfd_seconds": ttfd,
                "num_chunks": n_chunks,
                "audio_duration_seconds": audio_duration,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: "
                f"'{final_text[:60]}' lat={latency:.3f}s ttfd={ttfd:.3f}s chunks={n_chunks}"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    GRANITE_CHUNKED_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with GRANITE_CHUNKED_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    ttfds = [float(r["ttfd_seconds"]) for r in results]
    print(f"\nGranite chunked: {success}/{total} clips")
    print(
        f"  lat  p50={np.percentile(lats, 50):.3f}s"
        f"  p95={np.percentile(lats, 95):.3f}s"
        f"  p99={np.percentile(lats, 99):.3f}s"
    )
    print(f"  ttfd p50={np.percentile(ttfds, 50):.3f}s  p95={np.percentile(ttfds, 95):.3f}s")
    print(f"  avg chunks/clip: {np.mean(num_chunks_per_clip):.1f}")
    print(f"Saved → {GRANITE_CHUNKED_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
