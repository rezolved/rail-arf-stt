"""Run Granite Speech 4.1 2B with production streaming simulation on gold-92.

Streaming simulation:
  - WAV audio split into STREAM_INTERVAL_BYTES chunks (32 kB = ~1 s at 16 kHz int16)
  - Chunks accumulated in-memory (no sleep) — mirrors STTAdapter.transcribe_stream() pattern
  - Latency clock starts at first chunk delivery, ends when transcription returns
  - Biasing: keyword prompt injection ("transcribe ... Keywords: ...") — t0007 best variant
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
import torchaudio

from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0011_streaming_stt_benchmark.code.constants import (
    BYTES_PER_SAMPLE,
    DOMAIN_VOCAB,
    GRANITE_MAX_NEW_TOKENS,
    GRANITE_MODEL_LOCAL_DIR,
    GRANITE_PROMPT_BIASED_PREFIX,
    GRANITE_WARMUP_CLIPS,
    SAMPLE_RATE,
    STREAM_INTERVAL_BYTES,
)
from tasks.t0011_streaming_stt_benchmark.code.paths import GRANITE_STREAMING_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Granite streaming simulation on gold-92")
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


def load_audio_torch(path: Path) -> torch.Tensor:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    wav = torch.from_numpy(data.T).float()  # [1, samples]
    if sr != SAMPLE_RATE:
        wav = torchaudio.functional.resample(wav, sr, SAMPLE_RATE)
    return wav


def load_audio_float32(path: Path) -> np.ndarray:
    """Load as float32 numpy for PCM chunking."""
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def simulate_streaming(audio_float32: np.ndarray) -> tuple[torch.Tensor, float]:
    """Chunk audio into STREAM_INTERVAL_BYTES int16 PCM frames, accumulate, return torch tensor.

    Returns (accumulated_wav_tensor [1, samples], t_first_chunk).
    Latency clock starts at first chunk delivery.
    """
    pcm_int16 = (audio_float32 * 32767).clip(-32768, 32767).astype(np.int16)
    raw_bytes = pcm_int16.tobytes()

    accumulated: list[bytes] = []
    t_first_chunk: float | None = None
    offset = 0
    while offset < len(raw_bytes):
        chunk = raw_bytes[offset : offset + STREAM_INTERVAL_BYTES]
        if t_first_chunk is None:
            t_first_chunk = time.perf_counter()
        accumulated.append(chunk)
        offset += STREAM_INTERVAL_BYTES

    all_bytes = b"".join(accumulated)
    pcm_reconstructed = np.frombuffer(all_bytes, dtype=np.int16).astype(np.float32) / 32767.0
    wav_tensor = torch.from_numpy(pcm_reconstructed).unsqueeze(0)  # [1, samples]

    assert t_first_chunk is not None
    return wav_tensor, t_first_chunk


def transcribe_clip(model, processor, wav: torch.Tensor, prompt: str, device: str) -> str:
    tokenizer = processor.tokenizer
    chat = [{"role": "user", "content": f"<|audio|>{prompt}"}]
    prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

    model_inputs = processor(prompt_text, wav, device=device, return_tensors="pt").to(device)

    with torch.inference_mode():
        output_ids = model.generate(
            **model_inputs,
            max_new_tokens=GRANITE_MAX_NEW_TOKENS,
            do_sample=False,
            num_beams=1,
        )

    num_input = model_inputs["input_ids"].shape[-1]
    new_tokens = output_ids[0, num_input:].unsqueeze(0)
    return tokenizer.batch_decode(new_tokens, add_special_tokens=False, skip_special_tokens=True)[
        0
    ].strip()  # noqa: E501


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
    print(f"Keywords: {len(DOMAIN_VOCAB)} terms")

    print(f"Warming up on {GRANITE_WARMUP_CLIPS} clips ...")
    for clip in available[:GRANITE_WARMUP_CLIPS]:
        wav = load_audio_torch(clip.audio_path)
        transcribe_clip(model, processor, wav, biased_prompt, device)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    num_chunks_per_clip: list[int] = []

    for i, clip in enumerate(available):
        audio_f32 = load_audio_float32(clip.audio_path)
        wav_tensor, t_first_chunk = simulate_streaming(audio_f32)

        n_chunks = int(np.ceil(len(audio_f32) * BYTES_PER_SAMPLE / STREAM_INTERVAL_BYTES))
        num_chunks_per_clip.append(n_chunks)

        hypothesis = transcribe_clip(model, processor, wav_tensor, biased_prompt, device)
        t_end = time.perf_counter()
        latency = t_end - t_first_chunk

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
                "num_chunks": n_chunks,
                "audio_duration_seconds": len(audio_f32) / SAMPLE_RATE,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: "
                f"'{hypothesis[:60]}' lat={latency:.3f}s chunks={n_chunks}"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    GRANITE_STREAMING_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with GRANITE_STREAMING_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    print(f"\nGranite streaming: {success}/{total} clips")
    print(
        f"  lat p50={np.percentile(lats, 50):.3f}s  p95={np.percentile(lats, 95):.3f}s  p99={np.percentile(lats, 99):.3f}s"  # noqa: E501
    )
    print(f"  avg chunks/clip: {np.mean(num_chunks_per_clip):.1f}")
    print(f"Saved → {GRANITE_STREAMING_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
