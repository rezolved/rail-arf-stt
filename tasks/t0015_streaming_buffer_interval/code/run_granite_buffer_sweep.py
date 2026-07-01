"""Buffer interval sweep for Granite Speech 4.1 2B on gold-92.

Granite uses keyword prompt injection for biasing (no NeMo GPU-PB).
For each interval, accumulates PCM-16 into a growing buffer and re-transcribes
every N ms, recording TTFD and final latency.

Usage (on remote machine, conda env stt active):
    python -u tasks/t0015_streaming_buffer_interval/code/run_granite_buffer_sweep.py
    python -u tasks/t0015_streaming_buffer_interval/code/run_granite_buffer_sweep.py --limit 5
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch

from tasks.t0015_streaming_buffer_interval.code.constants import (
    BUFFER_INTERVALS_MS,
    CHUNK_SIZE_BYTES,
    GRANITE_KEYWORD_PROMPT,
    GRANITE_MAX_NEW_TOKENS,
    GRANITE_WARMUP_CLIPS,
    INTERVAL_BYTES,
    MIN_SUCCESS_RATE,
    MODEL_GRANITE,
    REMOTE_GRANITE_MODEL,
    SAMPLE_RATE,
)
from tasks.t0015_streaming_buffer_interval.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0015_streaming_buffer_interval.code.paths import (
    BOH_PATTERNS_CSV,
    GOLD92_AUDIO_DIR,
    GOLD92_GROUND_TRUTH,
    GRANITE_DIR,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Granite buffer interval sweep")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
    return parser.parse_args()


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def load_model(device: str) -> tuple[object, object]:
    """Load Granite Speech 4.1 2B model and processor."""
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    print(f"Loading Granite from {REMOTE_GRANITE_MODEL} ...")
    processor = AutoProcessor.from_pretrained(REMOTE_GRANITE_MODEL)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        REMOTE_GRANITE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()  # type: ignore[union-attr]
    print("Granite loaded.")
    return model, processor


def transcribe_wav(
    model: object,
    processor: object,
    wav: torch.Tensor,
    prompt: str,
    device: str,
) -> str:
    """Run Granite inference on a wav tensor."""
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
    """Extract new text delta from streaming transcript."""
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


def load_gold92_clips(*, limit: int | None = None) -> list[dict[str, Any]]:
    clips: list[dict[str, Any]] = []
    with GOLD92_GROUND_TRUTH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            clip_id = record["clip_id"]
            audio_path = GOLD92_AUDIO_DIR / f"{clip_id}.wav"
            if not audio_path.exists():
                continue
            clips.append(
                {
                    "clip_id": clip_id,
                    "reference_text": record.get("reference_text", ""),
                    "audio_path": audio_path,
                }
            )
    if limit is not None:
        clips = clips[:limit]
    return clips


def run_buffer_sweep(
    model: object,
    processor: object,
    clips: list[dict[str, Any]],
    *,
    interval_ms: int,
    detector: HallucinationDetector,
    device: str,
) -> list[dict[str, Any]]:
    """Run one buffer interval sweep for Granite."""
    interval_bytes = INTERVAL_BYTES[interval_ms]
    results: list[dict[str, Any]] = []
    errors = 0

    for i, clip_info in enumerate(clips):
        clip_id = clip_info["clip_id"]
        reference_text = clip_info["reference_text"]
        audio_path = clip_info["audio_path"]

        if not audio_path.exists():
            print(f"WARNING: {audio_path} not found — skipping")
            errors += 1
            continue

        try:
            audio_f32 = load_audio_float32(audio_path)
            duration_s = len(audio_f32) / SAMPLE_RATE

            pcm_int16 = (audio_f32 * 32767).clip(-32768, 32767).astype(np.int16)
            raw_bytes = pcm_int16.tobytes()

            accumulated = bytearray()
            bytes_since_last_inference: int = 0
            prev_transcript: str = ""
            t_first_chunk: float | None = None
            ttfd: float | None = None

            offset = 0
            while offset < len(raw_bytes):
                chunk = raw_bytes[offset : offset + CHUNK_SIZE_BYTES]
                if t_first_chunk is None:
                    t_first_chunk = time.perf_counter()
                accumulated.extend(chunk)
                bytes_since_last_inference += len(chunk)
                offset += CHUNK_SIZE_BYTES

                if bytes_since_last_inference >= interval_bytes:
                    bytes_since_last_inference = 0
                    pcm_rec = (
                        np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32)
                        / 32767.0
                    )
                    wav_tensor = torch.from_numpy(pcm_rec).unsqueeze(0)
                    try:
                        text = transcribe_wav(
                            model, processor, wav_tensor, GRANITE_KEYWORD_PROMPT, device
                        )
                    except Exception as exc:
                        print(f"  Granite inference error at interval: {exc}")
                        text = ""
                    delta_text = _extract_delta(prev_transcript, text)
                    if delta_text.strip():
                        if ttfd is None:
                            assert t_first_chunk is not None
                            ttfd = time.perf_counter() - t_first_chunk
                        prev_transcript = text

            # Final transcribe on complete buffer
            assert t_first_chunk is not None
            final_pcm = (
                np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            )
            final_wav = torch.from_numpy(final_pcm).unsqueeze(0)
            final_text = transcribe_wav(model, processor, final_wav, GRANITE_KEYWORD_PROMPT, device)
            t_end = time.perf_counter()
            latency = t_end - t_first_chunk

            if ttfd is None:
                ttfd = latency

            is_empty = len(final_text.strip()) == 0
            is_hallucination = detector.is_hallucination(
                transcript=final_text,
                reference_text=reference_text,
            )

            n_chunks = int(np.ceil(len(raw_bytes) / CHUNK_SIZE_BYTES))
            n_inferences = int(np.ceil(len(raw_bytes) / interval_bytes))

            results.append(
                {
                    "clip_id": clip_id,
                    "duration_s": round(duration_s, 3),
                    "transcript": final_text,
                    "reference_text": reference_text,
                    "is_empty": is_empty,
                    "is_hallucination": is_hallucination,
                    "ttfd_seconds": round(ttfd, 4),
                    "latency_seconds": round(latency, 4),
                    "interval_ms": interval_ms,
                    "n_chunks": n_chunks,
                    "n_inferences": n_inferences,
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                flag = "EMPTY" if is_empty else ("HALLUC" if is_hallucination else "ok")
                print(
                    f"  [{i + 1}/{len(clips)}] {clip_id} ({duration_s:.1f}s): "
                    f"'{final_text[:50]}' lat={latency:.3f}s ttfd={ttfd:.3f}s [{flag}]"
                )

        except Exception as exc:
            print(f"ERROR on {clip_id}: {exc}")
            errors += 1

    total = len(clips)
    successful = len(results)
    if total > 0 and (successful / total) < MIN_SUCCESS_RATE:
        raise RuntimeError(
            f"Rejection: only {successful}/{total} clips processed "
            f"({successful / total:.1%} < {MIN_SUCCESS_RATE:.0%})"
        )

    empties = sum(1 for r in results if r["is_empty"])
    hallucs = sum(1 for r in results if r["is_hallucination"])
    lats = [r["latency_seconds"] for r in results]
    ttfds = [r["ttfd_seconds"] for r in results]
    print(
        f"  interval={interval_ms}ms: {successful}/{total} clips, "
        f"empty={empties}, halluc={hallucs}, "
        f"lat_p50={np.percentile(lats, 50):.3f}s, ttfd_p50={np.percentile(ttfds, 50):.3f}s"
    )
    return results


def main() -> None:
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Model: {MODEL_GRANITE}")
    print(f"Prompt: '{GRANITE_KEYWORD_PROMPT[:80]}...'")

    # Load BoH patterns
    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)
    print(f"BoH: {len(boh_patterns)} patterns loaded")

    # Load clips
    clips = load_gold92_clips(limit=args.limit)
    print(f"Clips: {len(clips)}")

    # Load model
    model, processor = load_model(device)

    # Warmup
    print(f"Warming up ({GRANITE_WARMUP_CLIPS} clips) ...")
    warmup_wav = torch.zeros(1, SAMPLE_RATE, dtype=torch.float32)
    for _ in range(GRANITE_WARMUP_CLIPS):
        transcribe_wav(model, processor, warmup_wav, GRANITE_KEYWORD_PROMPT, device)
    print("Warmup done.")

    # Run sweep
    GRANITE_DIR.mkdir(parents=True, exist_ok=True)

    for interval_ms in BUFFER_INTERVALS_MS:
        print(f"\n=== {MODEL_GRANITE} | interval={interval_ms}ms ===")
        results = run_buffer_sweep(
            model,
            processor,
            clips,
            interval_ms=interval_ms,
            detector=detector,
            device=device,
        )

        out_path = GRANITE_DIR / f"predictions_{interval_ms}ms.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for r in results:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved → {out_path}")

    print(f"\nDone. Results in {GRANITE_DIR}")


if __name__ == "__main__":
    main()
