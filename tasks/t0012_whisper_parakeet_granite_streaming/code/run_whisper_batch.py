"""Run Whisper large-v3-turbo in batch mode on gold-92 (baseline for streaming delta).

Uses HuggingFace transformers (PyTorch) — mirrors brainpowa production biasing via initial_prompt.
Latency definition matches run_whisper_streaming.py: wall-clock from first chunk to transcript.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings

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
    SAMPLE_RATE,
    STREAM_INTERVAL_BYTES,
    WHISPER_BEAM_SIZE,
    WHISPER_DEVICE,
    WHISPER_HF_MODEL_ID,
    WHISPER_MAX_NEW_TOKENS,
)
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import WHISPER_BATCH_TRANSCRIPTS

INITIAL_PROMPT = ", ".join(DOMAIN_VOCAB)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Whisper turbo batch on gold-92")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def load_audio_float32(path: object) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_float32(
    model: torch.nn.Module,
    processor: object,
    audio: np.ndarray,
    prompt_ids: torch.Tensor,
    forced_decoder_ids: list[list[int]],
) -> str:
    from transformers import AutoProcessor

    proc: AutoProcessor = processor  # type: ignore[assignment]
    inputs = proc(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt")
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
    return text


def main() -> None:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    args = parse_args()

    clips = load_gold92()
    process_clips = clips[: args.limit] if args.limit is not None else clips
    available = [c for c in process_clips if c.audio_path.exists()]
    missing = len(process_clips) - len(available)
    if missing > 0:
        warnings.warn(f"{missing} audio files not found — skipping", stacklevel=2)
    if len(available) == 0:
        raise RuntimeError("No audio files found. Run dvc pull first.")

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
    print("Model loaded.")

    # Warmup
    print("Warming up ...")
    warmup = np.zeros(SAMPLE_RATE, dtype=np.float32)
    transcribe_float32(model, processor, warmup, prompt_ids, forced_decoder_ids)
    print("Warmup done.")

    results: list[dict[str, object]] = []

    for i, clip in enumerate(available):
        audio = load_audio_float32(clip.audio_path)
        raw_bytes_len = len(audio) * BYTES_PER_SAMPLE
        n_chunks = int(np.ceil(raw_bytes_len / STREAM_INTERVAL_BYTES))
        audio_duration = len(audio) / SAMPLE_RATE

        # Timer starts at first-chunk delivery moment (fair comparison with streaming)
        t_first_chunk = time.perf_counter()
        hypothesis = transcribe_float32(model, processor, audio, prompt_ids, forced_decoder_ids)
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
                "audio_duration_seconds": audio_duration,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: "
                f"'{hypothesis[:60]}' lat={latency:.3f}s"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    WHISPER_BATCH_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with WHISPER_BATCH_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    print(f"\nWhisper turbo batch: {success}/{total} clips")
    print(
        f"  lat p50={np.percentile(lats, 50):.3f}s"
        f"  p95={np.percentile(lats, 95):.3f}s"
        f"  p99={np.percentile(lats, 99):.3f}s"
    )
    print(f"Saved → {WHISPER_BATCH_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
