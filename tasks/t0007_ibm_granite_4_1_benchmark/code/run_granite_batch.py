"""Run IBM Granite Speech 4.1 2B in batch mode (no biasing) on all 93 gold-92 clips.

Model: ibm-granite/granite-speech-4.1-2b via HuggingFace Transformers.
Saves outputs to data/granite_batch_transcripts.json.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import soundfile as sf
import torch
import torchaudio

from tasks.t0007_ibm_granite_4_1_benchmark.code.constants import (
    MAX_NEW_TOKENS,
    MODEL_LOCAL_DIR,
    PROMPT_UNBIASED,
    SAMPLE_RATE,
    WARMUP_CLIPS,
)
from tasks.t0007_ibm_granite_4_1_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0007_ibm_granite_4_1_benchmark.code.paths import GRANITE_BATCH_TRANSCRIPTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(  # noqa: E501
        description="Run Granite Speech 4.1 2B batch inference on gold-92"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit clips for validation")
    return parser.parse_args()


def load_model(device: str) -> tuple:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    print(f"Loading model from {MODEL_LOCAL_DIR} ...")
    processor = AutoProcessor.from_pretrained(MODEL_LOCAL_DIR)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        MODEL_LOCAL_DIR,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()
    print("Model loaded.")
    return model, processor


def load_audio(path: Path) -> torch.Tensor:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    wav = torch.from_numpy(data.T).float()  # [1, samples]
    if sr != SAMPLE_RATE:
        wav = torchaudio.functional.resample(wav, sr, SAMPLE_RATE)
    return wav


def transcribe_clip(
    model,
    processor,
    wav: torch.Tensor,
    prompt: str,
    device: str,
) -> str:
    tokenizer = processor.tokenizer
    chat = [{"role": "user", "content": f"<|audio|>{prompt}"}]
    prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

    model_inputs = processor(prompt_text, wav, device=device, return_tensors="pt").to(device)

    with torch.inference_mode():
        output_ids = model.generate(
            **model_inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            num_beams=1,
        )

    num_input = model_inputs["input_ids"].shape[-1]  # noqa: E501
    new_tokens = output_ids[0, num_input:].unsqueeze(0)
    return tokenizer.batch_decode(new_tokens, add_special_tokens=False, skip_special_tokens=True)[
        0
    ].strip()


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

    # Warmup
    print(f"Warming up on {WARMUP_CLIPS} clips ...")
    for clip in available[:WARMUP_CLIPS]:
        wav = load_audio(clip.audio_path)
        transcribe_clip(model, processor, wav, PROMPT_UNBIASED, device)
    print("Warmup done.")

    results: list[dict[str, object]] = []
    for i, clip in enumerate(available):
        wav = load_audio(clip.audio_path)

        t0 = time.perf_counter()
        hypothesis = transcribe_clip(model, processor, wav, PROMPT_UNBIASED, device)
        latency = time.perf_counter() - t0

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"WARNING: anomaly clip {clip.clip_id} — Cyrillic ground truth.")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,  # noqa: E501
                "latency_seconds": latency,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: '{hypothesis[:60]}' ({latency:.2f}s)"
            )

    total = len(available)
    success = sum(1 for r in results if r["hypothesis"])
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: only {success}/{total} clips have non-empty hypotheses.")

    GRANITE_BATCH_TRANSCRIPTS.parent.mkdir(parents=True, exist_ok=True)
    with GRANITE_BATCH_TRANSCRIPTS.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\nDone: {success}/{total} clips transcribed")
    print(f"Saved to {GRANITE_BATCH_TRANSCRIPTS}")

    print("\n--- First 5 results ---")
    for r in results[:5]:
        print(f"  {r['clip_id']}: '{str(r['hypothesis'])[:80]}' ({r['latency_seconds']:.3f}s)")


if __name__ == "__main__":
    main()
