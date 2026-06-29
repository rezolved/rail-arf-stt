"""Run Whisper large-v3-turbo in production streaming mode on gold-92.

Mirrors WhisperSTT.transcribe_stream() from brainpowa-realtime-api exactly:
  - Every STREAM_INTERVAL_BYTES of accumulated PCM-16 audio: transcribe full buffer,
    extract delta (word-level LCP matching), yield delta if non-empty.
  - Final transcribe on complete audio after all chunks delivered.
  - Latency: wall-clock from first chunk to final transcript returned.
  - Extra: time-to-first-delta (TTFD) — first chunk to first non-empty delta.

Uses HuggingFace transformers (PyTorch) — faster-whisper (ctranslate2) has a multi-GPU
bug on this host.
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
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import WHISPER_STREAMING_TRANSCRIPTS

INITIAL_PROMPT = ", ".join(DOMAIN_VOCAB)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Whisper turbo streaming on gold-92")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def _extract_delta(previous: str, current: str) -> str:
    """Return new portion of current that extends beyond previous.

    Exact copy of WhisperSTT._extract_delta() from brainpowa-realtime-api.
    Word-level LCP matching — robust to Whisper re-punctuation / re-capitalisation.
    """
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


def load_audio_float32(path: object) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def transcribe_buffer(
    model: torch.nn.Module,
    processor: object,
    audio_float32: np.ndarray,
    prompt_ids: torch.Tensor,
    forced_decoder_ids: list[list[int]],
) -> str:
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
    return proc.batch_decode(ids, skip_special_tokens=True)[0].strip()


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
    print(f"Model loaded. prompt: '{INITIAL_PROMPT[:60]}...'")

    # Warmup
    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    transcribe_buffer(model, processor, warmup_audio, prompt_ids, forced_decoder_ids)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    num_chunks_per_clip: list[int] = []

    for i, clip in enumerate(available):
        audio_float32 = load_audio_float32(clip.audio_path)
        raw_bytes_len = len(audio_float32) * BYTES_PER_SAMPLE
        n_chunks = int(np.ceil(raw_bytes_len / STREAM_INTERVAL_BYTES))
        num_chunks_per_clip.append(n_chunks)
        audio_duration = len(audio_float32) / SAMPLE_RATE

        # Simulate streaming: deliver int16 PCM chunks, accumulate, transcribe per interval
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
                # Reconstruct float32 from accumulated int16 bytes for HF processor
                acc_pcm = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32)
                acc_float = acc_pcm / 32767.0
                text = transcribe_buffer(  # noqa: E501
                    model, processor, acc_float, prompt_ids, forced_decoder_ids
                )
                delta_text = _extract_delta(prev_transcript, text)
                if delta_text.strip():
                    if ttfd is None:
                        ttfd = time.perf_counter() - t_first_chunk  # type: ignore[operator]
                    prev_transcript = text

        # Final transcribe on complete buffer
        assert t_first_chunk is not None
        final_float = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
        final_text = transcribe_buffer(  # noqa: E501
            model, processor, final_float, prompt_ids, forced_decoder_ids
        )
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

    WHISPER_STREAMING_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with WHISPER_STREAMING_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    lats = [float(r["latency_seconds"]) for r in results]
    ttfds = [float(r["ttfd_seconds"]) for r in results]
    print(f"\nWhisper turbo streaming: {success}/{total} clips")
    print(
        f"  lat  p50={np.percentile(lats, 50):.3f}s"
        f"  p95={np.percentile(lats, 95):.3f}s"
        f"  p99={np.percentile(lats, 99):.3f}s"
    )
    print(f"  ttfd p50={np.percentile(ttfds, 50):.3f}s  p95={np.percentile(ttfds, 95):.3f}s")
    print(f"  avg chunks/clip: {np.mean(num_chunks_per_clip):.1f}")
    print(f"Saved → {WHISPER_STREAMING_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
