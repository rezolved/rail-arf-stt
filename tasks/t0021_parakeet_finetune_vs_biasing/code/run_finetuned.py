"""Run finetuned parakeet-unified-en-0.6b on gold-92 and write predictions JSONL.

Transcribes all 93 gold-92 clips with the finetuned .nemo checkpoint (no biasing).
Output format matches t0015 predictions for direct metric comparison.

Usage (on gpu-azure, conda env stt):
    python -u tasks/t0021_parakeet_finetune_vs_biasing/code/run_finetuned.py
    python -u tasks/t0021_parakeet_finetune_vs_biasing/code/run_finetuned.py --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
import string
import tempfile
import time
from pathlib import Path

import soundfile as sf
from omegaconf import OmegaConf, open_dict

from tasks.t0021_parakeet_finetune_vs_biasing.code.constants import DOMAIN_VOCAB
from tasks.t0021_parakeet_finetune_vs_biasing.code.paths import (
    DATA_DIR,
    FINETUNED_NEMO,
    GOLD92_AUDIO_DIR,
    GOLD92_GROUND_TRUTH,
    PREDICTIONS_FINETUNED,
)


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def wer(ref: str, hyp: str) -> float:
    import jiwer

    if not ref.strip():
        return 0.0
    return jiwer.wer(normalise(ref), normalise(hyp))


def entity_accuracy(ref: str, hyp: str) -> float:
    """Heuristic entity accuracy: fraction of reference words found in hypothesis."""
    ref_words = set(normalise(ref).split())
    hyp_words = set(normalise(hyp).split())
    if not ref_words:
        return 1.0
    return len(ref_words & hyp_words) / len(ref_words)


def domain_vocab_accuracy(ref: str, hyp: str, vocab: list[str]) -> float | None:
    """Fraction of domain vocab terms present in ref that also appear in hyp."""
    ref_n = normalise(ref)
    hyp_n = normalise(hyp)
    present_in_ref = [term for term in vocab if normalise(term) in ref_n]
    if not present_in_ref:
        return None
    matched = sum(1 for term in present_in_ref if normalise(term) in hyp_n)
    return matched / len(present_in_ref)


def _ensure_transcribe_cfg(model) -> None:
    if model.cfg.get("validation_ds") is None:
        with open_dict(model.cfg):
            model.cfg.validation_ds = OmegaConf.create({"use_start_end_token": False})


def _mono_path(audio_path: str) -> tuple[str, bool]:
    try:
        with sf.SoundFile(audio_path) as f:
            if f.channels <= 1:
                return audio_path, False
        data, sr = sf.read(audio_path, always_2d=True)
        mono = data.mean(axis=1)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, mono, sr)
            return tmp.name, True
    except Exception:
        return audio_path, False


def transcribe(model, audio_path: str) -> tuple[str, float]:
    """Return (transcript, latency_seconds)."""
    _ensure_transcribe_cfg(model)
    path, is_temp = _mono_path(audio_path)
    try:
        t0 = time.perf_counter()
        result = model.transcribe([path])
        latency = time.perf_counter() - t0
    finally:
        if is_temp:
            os.unlink(path)
    hyp = result[0]
    if hasattr(hyp, "text"):
        return hyp.text.strip(), latency
    return str(hyp).strip(), latency


def duration_seconds(audio_path: str) -> float:
    with sf.SoundFile(audio_path) as f:
        return f.frames / f.samplerate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=FINETUNED_NEMO,
        help="Path to .nemo checkpoint",
    )
    args = parser.parse_args()

    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")

    # Load ground truth
    gt: dict[str, str] = {}
    with GOLD92_GROUND_TRUTH.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            gt[rec["clip_id"]] = rec.get("ground_truth", rec.get("reference_text", ""))

    # Discover clips
    clip_ids = sorted(gt.keys())
    if args.limit:
        clip_ids = clip_ids[: args.limit]

    print(f"Checkpoint : {args.checkpoint}")
    print(f"Gold-92    : {GOLD92_AUDIO_DIR}")
    print(f"Clips      : {len(clip_ids)}")
    print(f"Output     : {PREDICTIONS_FINETUNED}")
    print()

    print("Loading model...")
    import nemo.collections.asr as nemo_asr

    model = nemo_asr.models.ASRModel.restore_from(str(args.checkpoint))
    model.eval()
    print("Model loaded.\n")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    wer_vals: list[float] = []
    ea_vals: list[float] = []
    ea_dv_vals: list[float] = []
    latency_vals: list[float] = []

    with PREDICTIONS_FINETUNED.open("w") as out:
        for i, clip_id in enumerate(clip_ids):
            audio_path = str(GOLD92_AUDIO_DIR / f"{clip_id}.wav")
            ref = gt.get(clip_id, "")

            try:
                transcript, latency = transcribe(model, audio_path)
                dur = duration_seconds(audio_path)
            except Exception as exc:
                print(f"  [{i + 1:2d}/{len(clip_ids)}] ERROR {clip_id}: {exc}")
                transcript, latency, dur = "", 0.0, 0.0

            is_empty = not transcript.strip()
            w = wer(ref, transcript) if ref else None
            ea = entity_accuracy(ref, transcript) if ref else None
            ea_dv = domain_vocab_accuracy(ref, transcript, DOMAIN_VOCAB) if ref else None

            rec = {
                "clip_id": clip_id,
                "duration_s": round(dur, 3),
                "transcript": transcript,
                "reference_text": ref,
                "is_empty": is_empty,
                "is_hallucination": False,
                "ttfd_seconds": round(latency, 4),
                "latency_seconds": round(latency, 4),
                "interval_ms": None,
                "n_chunks": 1,
                "n_inferences": 1,
            }
            out.write(json.dumps(rec) + "\n")

            if w is not None:
                wer_vals.append(w)
            if ea is not None:
                ea_vals.append(ea)
            if ea_dv is not None:
                ea_dv_vals.append(ea_dv)
            latency_vals.append(latency)

            status = "✓" if (w or 0) < 0.05 else ("~" if (w or 0) < 0.2 else "✗")
            wer_str = f"wer={w:.3f}" if w is not None else "wer=N/A"
            ea_dv_str = f"ea_dv={ea_dv:.3f}" if ea_dv is not None else "ea_dv=N/A"
            print(f"  [{i + 1:2d}/{len(clip_ids)}] {status} {wer_str} {ea_dv_str}  {clip_id}")

    print()
    print("=" * 60)
    print(f"AGGREGATE ({len(wer_vals)} clips with reference)")
    print("=" * 60)
    if wer_vals:
        print(f"  WER   : {sum(wer_vals) / len(wer_vals):.4f}")
    if ea_vals:
        print(f"  EA    : {sum(ea_vals) / len(ea_vals):.4f}")
    if ea_dv_vals:
        n_dv = len(ea_dv_vals)
        print(f"  EA-DV : {sum(ea_dv_vals) / n_dv:.4f}  ({n_dv} clips with domain terms)")
    if latency_vals:
        lats = sorted(latency_vals)
        p50 = lats[len(lats) // 2]
        print(f"  Latency p50: {p50:.3f}s")
    print()
    print(f"Predictions written: {PREDICTIONS_FINETUNED}")


if __name__ == "__main__":
    main()
