"""Head-to-head comparison on clean production clips (no train overlap).

Runs two configurations of parakeet-unified-en-0.6b on 21 production clips
that are NOT in gold-92 or the finetune training set:
  A — base model + GPU-PB TurboBias (same config as t0015)
  B — finetuned checkpoint, no biasing

Usage (on gpu-azure, conda env stt):
    python -u tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py
    python -u tasks/t0021_parakeet_finetune_vs_biasing/code/run_clean_eval.py --limit 5
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import string
import tempfile
import time
from pathlib import Path
from typing import Any

import soundfile as sf
from omegaconf import OmegaConf, open_dict

from tasks.t0021_parakeet_finetune_vs_biasing.code.constants import DOMAIN_VOCAB
from tasks.t0021_parakeet_finetune_vs_biasing.code.paths import (
    DATA_DIR,
    FINETUNED_NEMO,
)

# Biasing hyperparams — same as t0015 production defaults
BOOSTING_ALPHA: float = 1.0
CONTEXT_SCORE: float = 1.0
DEPTH_SCALING: float = 2.0
USE_BPE_DROPOUT: bool = True

HF_UNIFIED: str = "nvidia/parakeet-unified-en-0.6b"

CLEAN_EVAL_DIR: Path = DATA_DIR / "clean_eval"
CLEAN_EVAL_AUDIO_DIR: Path = DATA_DIR / "clean_eval_audio"
MANIFEST: Path = CLEAN_EVAL_DIR / "manifest.jsonl"
OUT_BIASED: Path = DATA_DIR / "clean_eval_biased.jsonl"
OUT_FINETUNED: Path = DATA_DIR / "clean_eval_finetuned.jsonl"
OUT_COMPARISON: Path = DATA_DIR / "clean_eval_comparison.json"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


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
    ref_words = set(normalise(ref).split())
    hyp_words = set(normalise(hyp).split())
    if len(ref_words) == 0:
        return 1.0
    return len(ref_words & hyp_words) / len(ref_words)


def domain_vocab_accuracy(ref: str, hyp: str, vocab: list[str]) -> float | None:
    ref_n = normalise(ref)
    hyp_n = normalise(hyp)
    present = [t for t in vocab if normalise(t) in ref_n]
    if len(present) == 0:
        return None
    matched = sum(1 for t in present if normalise(t) in hyp_n)
    return matched / len(present)


# ---------------------------------------------------------------------------
# Model helpers
# ---------------------------------------------------------------------------


def _ensure_transcribe_cfg(model: Any) -> None:
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


def transcribe(model: Any, audio_path: str) -> tuple[str, float]:
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
    return (hyp.text.strip() if hasattr(hyp, "text") else str(hyp).strip()), latency


def apply_boosting(model: Any, phrases: tuple[str, ...]) -> None:
    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree.key_phrases_list", list(phrases), force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.context_score", CONTEXT_SCORE, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.depth_scaling", DEPTH_SCALING, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.use_bpe_dropout", USE_BPE_DROPOUT, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", BOOSTING_ALPHA, force_add=True)
    model.change_decoding_strategy(cfg)


def expand_casing_variants(phrases: list[str]) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return tuple(out)


# ---------------------------------------------------------------------------
# Eval loop
# ---------------------------------------------------------------------------


def run_eval(
    model: Any,
    clips: list[dict[str, Any]],
    *,
    label: str,
    out_path: Path,
) -> dict[str, Any]:
    wer_vals: list[float] = []
    ea_dv_vals: list[float] = []
    records: list[dict[str, Any]] = []

    with out_path.open("w") as fh:
        for i, clip in enumerate(clips):
            audio_path = str(CLEAN_EVAL_AUDIO_DIR / clip["audio_filename"])
            ref = clip["reference_text"]

            try:
                transcript, latency = transcribe(model, audio_path)
                with sf.SoundFile(audio_path) as f:
                    dur = f.frames / f.samplerate
            except Exception as exc:
                print(f"  [{i + 1:2d}/{len(clips)}] ERROR {clip['clip_id']}: {exc}")
                transcript, latency, dur = "", 0.0, 0.0

            w = wer(ref, transcript) if ref else None
            ea_dv = domain_vocab_accuracy(ref, transcript, DOMAIN_VOCAB) if ref else None

            rec = {
                "clip_id": clip["clip_id"],
                "reference_text": ref,
                "transcript": transcript,
                "wer": round(w, 4) if w is not None else None,
                "ea_dv": round(ea_dv, 4) if ea_dv is not None else None,
                "latency_seconds": round(latency, 4),
                "duration_s": round(dur, 3),
            }
            fh.write(json.dumps(rec) + "\n")
            records.append(rec)

            if w is not None:
                wer_vals.append(w)
            if ea_dv is not None:
                ea_dv_vals.append(ea_dv)

            status = "✓" if (w or 0) < 0.05 else ("~" if (w or 0) < 0.2 else "✗")
            ea_dv_str = f"ea_dv={ea_dv:.3f}" if ea_dv is not None else "ea_dv=N/A"
            wer_str = f"wer={w:.3f}" if w is not None else "wer=N/A"
            print(f"  [{i + 1:2d}/{len(clips)}] {status} {wer_str} {ea_dv_str}  {clip['clip_id']}")

    agg: dict[str, Any] = {
        "label": label,
        "n_clips": len(clips),
        "n_with_ref": len(wer_vals),
        "n_with_domain": len(ea_dv_vals),
        "wer": round(sum(wer_vals) / len(wer_vals), 4) if wer_vals else None,
        "ea_dv": round(sum(ea_dv_vals) / len(ea_dv_vals), 4) if ea_dv_vals else None,
    }
    print(f"\n{label}: WER={agg['wer']} EA-DV={agg['ea_dv']}  ({len(ea_dv_vals)} domain clips)")
    return agg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--checkpoint", type=Path, default=FINETUNED_NEMO)
    args = parser.parse_args()

    if not MANIFEST.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST}")
    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")

    clips = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    if args.limit is not None:
        clips = clips[: args.limit]

    print(f"Clean eval clips : {len(clips)}")
    print(f"Biased model     : {HF_UNIFIED} + TurboBias alpha={BOOSTING_ALPHA}")
    print(f"Finetuned model  : {args.checkpoint}")
    print()

    import nemo.collections.asr as nemo_asr

    # --- Run A: biased ---
    print("=" * 60)
    print("Run A — parakeet-unified + TurboBias")
    print("=" * 60)
    model_a = nemo_asr.models.ASRModel.from_pretrained(HF_UNIFIED)
    model_a.eval()
    phrases = expand_casing_variants(DOMAIN_VOCAB)
    apply_boosting(model_a, phrases)
    agg_a = run_eval(model_a, clips, label="biased", out_path=OUT_BIASED)
    del model_a

    print()

    # --- Run B: finetuned ---
    print("=" * 60)
    print("Run B — parakeet-unified finetuned (no biasing)")
    print("=" * 60)
    model_b = nemo_asr.models.ASRModel.restore_from(str(args.checkpoint))
    model_b.eval()
    agg_b = run_eval(model_b, clips, label="finetuned", out_path=OUT_FINETUNED)
    del model_b

    # --- Comparison ---
    print()
    print("=" * 60)
    print("COMPARISON (clean production clips, no train overlap)")
    print("=" * 60)
    for metric in ("wer", "ea_dv"):
        a_val = agg_a[metric]
        b_val = agg_b[metric]
        if a_val is None or b_val is None:
            print(f"  {metric.upper():8s}: A={a_val}  B={b_val}")
            continue
        if metric == "wer":
            delta = a_val - b_val  # positive = finetuned better
            winner = "finetuned" if delta > 0 else "biased"
        else:
            delta = b_val - a_val  # positive = finetuned better
            winner = "finetuned" if delta > 0 else "biased"
        tag = metric.upper()
        row = f"biased={a_val:.4f}  finetuned={b_val:.4f}  Δ={delta:+.4f}  winner={winner}"
        print(f"  {tag:8s}: {row}")

    comparison = {"biased": agg_a, "finetuned": agg_b}
    OUT_COMPARISON.write_text(json.dumps(comparison, indent=2))
    print(f"\nComparison written: {OUT_COMPARISON}")


if __name__ == "__main__":
    main()
