"""Buffer interval sweep for multitalker-parakeet-streaming-0.6b-v1 on gold-92.

The multitalker model has internal VAD/segmentation. We test all 3 buffer intervals,
but the model's internal logic determines segment boundaries — the interval controls
how often we flush accumulated audio to the model, not when it outputs text.

GPU-PB TurboBias applied if supported.

Usage (on remote machine, conda env stt active):
    python -u tasks/t0015_streaming_buffer_interval/code/run_multitalker_buffer_sweep.py
    python -u tasks/t0015_streaming_buffer_interval/code/run_multitalker_buffer_sweep.py --limit 5
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from tasks.t0015_streaming_buffer_interval.code.constants import (
    BUFFER_INTERVALS_MS,
    CHUNK_SIZE_BYTES,
    DOMAIN_VOCAB,
    HF_MULTITALKER,
    INTERVAL_BYTES,
    MIN_SUCCESS_RATE,
    MODEL_MULTITALKER,
    PARAKEET_BOOSTING_ALPHA,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_DEPTH_SCALING,
    PARAKEET_USE_BPE_DROPOUT,
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
    MULTITALKER_DIR,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multitalker Parakeet buffer sweep")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of clips")
    return parser.parse_args()


def expand_casing_variants(phrases: list[str]) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)


def apply_boosting(model: Any, phrases: tuple[str, ...], *, alpha: float) -> None:
    """Attempt to apply GPU-PB TurboBias. Silently skips if unsupported."""
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(
        cfg,
        "greedy.boosting_tree.key_phrases_list",
        list(phrases) if phrases else None,
        force_add=True,
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.context_score", PARAKEET_CONTEXT_SCORE, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.depth_scaling", PARAKEET_DEPTH_SCALING, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.use_bpe_dropout", PARAKEET_USE_BPE_DROPOUT, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)


def load_audio_float32(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def patch_multitalker_forward(model: Any) -> None:
    """Patch _transcribe_forward to handle missing speaker targets gracefully.

    The EncDecMultiTalkerRNNTBPEModel._transcribe_forward() tries to unpack
    `additional_args` as `(spk_targets, bg_spk_targets)`, but the standard
    transcribe() dataloader does not provide speaker targets in the batch.
    This patch passes None for both targets (single-speaker transcription mode).
    """
    import types

    from nemo.collections.asr.models.rnnt_models import EncDecRNNTModel
    from nemo.collections.asr.parts.mixins import TranscribeConfig

    def _patched_transcribe_forward(self: Any, batch: Any, trcfg: TranscribeConfig) -> Any:
        signal, signal_len, transcript, transcript_len, *additional_args = batch
        if len(additional_args) >= 2:
            spk_targets = additional_args[0]
            bg_spk_targets = additional_args[1]
        else:
            # No speaker targets in batch — use None (single-speaker mode)
            spk_targets = None
            bg_spk_targets = None
        self.set_speaker_targets(spk_targets, bg_spk_targets)
        batch = (signal, signal_len, transcript, transcript_len)
        return EncDecRNNTModel._transcribe_forward(self, batch, trcfg)

    model._transcribe_forward = types.MethodType(_patched_transcribe_forward, model)
    print("Multitalker: patched _transcribe_forward for missing speaker targets")


def transcribe_buffer(model: Any, audio_float32: np.ndarray) -> str:
    """Transcribe accumulated buffer. Returns final transcript."""
    try:
        outputs = model.transcribe([audio_float32], batch_size=1, verbose=False)
        first = outputs[0] if outputs else ""
        return (getattr(first, "text", first) or "").strip()
    except Exception as exc:
        print(f"  transcribe error: {exc}")
        return ""


def _extract_delta(previous: str, current: str) -> str:
    """Extract text delta from streaming transcription."""
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
    model: Any,
    clips: list[dict[str, Any]],
    *,
    interval_ms: int,
    detector: HallucinationDetector,
) -> list[dict[str, Any]]:
    """Run one interval sweep for the multitalker model."""
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
                    acc_f32 = (
                        np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32)
                        / 32767.0
                    )
                    text = transcribe_buffer(model, acc_f32)
                    delta_text = _extract_delta(prev_transcript, text)
                    if delta_text.strip():
                        if ttfd is None:
                            assert t_first_chunk is not None
                            ttfd = time.perf_counter() - t_first_chunk
                        prev_transcript = text

            # Final pass on complete buffer
            assert t_first_chunk is not None
            final_f32 = (
                np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            )
            final_text = transcribe_buffer(model, final_f32)
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
                    "model_has_internal_vad": True,
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
    import torch

    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Model: {MODEL_MULTITALKER}")

    # Load BoH patterns
    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)
    print(f"BoH: {len(boh_patterns)} patterns loaded")

    # Load clips
    clips = load_gold92_clips(limit=args.limit)
    print(f"Clips: {len(clips)}")

    # Load model
    from nemo.collections.asr.models import ASRModel

    print(f"Loading {MODEL_MULTITALKER} from HuggingFace ...")
    model = ASRModel.from_pretrained(model_name=HF_MULTITALKER, map_location=device)
    model = model.to(device)
    model.eval()

    # Patch _transcribe_forward to handle missing speaker targets
    patch_multitalker_forward(model)

    # Apply GPU-PB TurboBias (best-effort — may not be supported)
    phrases = expand_casing_variants(DOMAIN_VOCAB)
    try:
        apply_boosting(model, phrases, alpha=PARAKEET_BOOSTING_ALPHA)
        print(f"Boosting: {len(phrases)} phrase variants, alpha={PARAKEET_BOOSTING_ALPHA}")
    except Exception as exc:
        print(f"NOTE: Boosting not applied to multitalker ({exc}) — proceeding without")

    # Warmup
    print("Warming up ...")
    warmup_audio = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(3):
        transcribe_buffer(model, warmup_audio)
    print("Warmup done.")

    # Run sweep
    MULTITALKER_DIR.mkdir(parents=True, exist_ok=True)

    for interval_ms in BUFFER_INTERVALS_MS:
        print(f"\n=== {MODEL_MULTITALKER} | interval={interval_ms}ms ===")
        results = run_buffer_sweep(model, clips, interval_ms=interval_ms, detector=detector)

        out_path = MULTITALKER_DIR / f"predictions_{interval_ms}ms.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for r in results:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved → {out_path}")

    print(f"\nDone. Results in {MULTITALKER_DIR}")


if __name__ == "__main__":
    main()
