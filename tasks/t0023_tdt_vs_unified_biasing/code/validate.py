"""Final validation: current prod vs recommended config on all 93 gold-92 clips (t0023).

Baseline:    nvidia/parakeet-tdt-0.6b-v3   + greedy_batch + cs=1.0 / ds=2.0 / alpha=1.0
Recommended: nvidia/parakeet-unified-en-0.6b + malsd_batch  + cs=3.0 / ds=0.5 / alpha=1.5

Usage (gpu-azure, conda env stt, PYTHONPATH=repo root):
    python -u tasks/t0023_tdt_vs_unified_biasing/code/validate.py
    python -u tasks/t0023_tdt_vs_unified_biasing/code/validate.py --clips 10  # smoke
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parents[3]
TASK_DIR = Path(__file__).parents[1]
RESULTS_DIR = TASK_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def _find_gold92() -> tuple[Path, Path]:
    candidates = [
        REPO_ROOT
        / "tasks"
        / "t0001_stt_benchmark"
        / "assets"
        / "dataset"
        / "stt-benchmark-gold-92"
        / "files",
        Path.home()
        / "rail-arf-stt"
        / "tasks"
        / "t0001_stt_benchmark"
        / "assets"
        / "dataset"
        / "stt-benchmark-gold-92"
        / "files",
    ]
    for base in candidates:
        gt = base / "ground_truth.jsonl"
        audio = base / "audio"
        if gt.exists() and audio.exists():
            return gt, audio
    raise FileNotFoundError(f"gold-92 not found; tried: {candidates}")


GOLD92_GROUND_TRUTH, GOLD92_AUDIO_DIR = _find_gold92()

sys.path.insert(0, str(REPO_ROOT))
from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (  # noqa: E402
    DOMAIN_VOCAB,
)

# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------
BASELINE_MODEL = "nvidia/parakeet-tdt-0.6b-v3"
NEW_MODEL = "nvidia/parakeet-unified-en-0.6b"

BASELINE_LABEL = "TDT greedy_batch cs=1.0/ds=2.0/α=1.0 (current prod)"
NEW_LABEL = "Unified malsd_batch cs=3.0/ds=0.5/α=1.5 (recommended)"

TARGET_BRANDS = ["Rezolve", "brainpowa"]
BRAND_VARIANTS = {
    "Rezolve": ["Rezolve", "Rezolve AI", "rezolve"],
    "brainpowa": ["brainpowa", "Brain Powa", "Brain Power", "Brainpowa", "brain powa"],
}
PHONETIC_PATTERNS = {
    "Rezolve": re.compile(r"\bresolve\b|\brezolve\b|\brezolv\b|\bresolved\b", re.I),
    "brainpowa": re.compile(r"\bbrain.?pow|\bbrain.?com|\bbrainpow|\bbraincom|\bbrain pow", re.I),
}
EXACT_PATTERNS = {
    "Rezolve": re.compile(r"\bRezolve\b"),
    "brainpowa": re.compile(r"\bbrainpowa\b", re.I),
}
TERM_FILTER = re.compile(r"rezolve|resolve|brainpowa|brain.?pow|brain.?com", re.I)

SAMPLE_RATE = 16_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_all_clips(
    ground_truth: Path,
    audio_dir: Path,
    max_clips: int | None = None,
) -> list[dict]:
    """Load ALL gold-92 clips (no filtering). Returns list with brand_clip=True/False."""
    clips: list[dict] = []
    for line in ground_truth.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        clip_id = d["clip_id"]
        text = d.get("ground_truth", d.get("transcript", ""))
        audio_path = audio_dir / f"{clip_id}.wav"
        if not audio_path.exists():
            continue
        try:
            audio = load_audio(audio_path)
        except Exception:
            continue
        clips.append(
            {
                "clip_id": clip_id,
                "transcript": text,
                "audio": audio,
                "is_brand": bool(TERM_FILTER.search(text)),
            }
        )
    if max_clips is not None:
        clips = clips[:max_clips]
    return clips


def load_audio(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1)
    audio = data[:, 0] if data.ndim == 2 else data
    audio = audio.astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def _decode_output(o: Any, model: Any) -> str:
    if isinstance(o, str):
        return o
    if hasattr(o, "text") and isinstance(o.text, str):
        return o.text
    if hasattr(o, "y_sequence"):
        import torch

        seq = o.y_sequence
        ids = seq.tolist() if isinstance(seq, (torch.Tensor, np.ndarray)) else list(seq)
        try:
            return model.tokenizer.ids_to_text(ids)
        except Exception:
            return str(o)
    return str(o)


def transcribe_all(model: Any, clips: list[dict]) -> list[str]:
    audios = [c["audio"] for c in clips]
    outputs = model.transcribe(audios, batch_size=8, verbose=False)
    decoded = []
    for o in outputs:
        if isinstance(o, list):
            o = o[0] if len(o) > 0 else ""
        decoded.append(_decode_output(o, model))
    return decoded


def label_brand(hyp: str, brand: str) -> str:
    if EXACT_PATTERNS[brand].search(hyp):
        return "EXACT"
    if PHONETIC_PATTERNS[brand].search(hyp):
        return "PHONETIC"
    return "GARBAGE"


def brand_in_ref(ref: str) -> str | None:
    for brand in TARGET_BRANDS:
        if EXACT_PATTERNS[brand].search(ref):
            return brand
        if PHONETIC_PATTERNS[brand].search(ref):
            return brand
    return None


def wer(ref: str, hyp: str) -> float:
    _word = re.compile(r"[a-z0-9']+")
    r = _word.findall(ref.lower())
    h = _word.findall(hyp.lower())
    if not r and not h:
        return 0.0
    if not r:
        return 1.0
    d = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        prev, d[0] = d[0], i
        for j, hw in enumerate(h, 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (rw != hw))
            prev = cur
    return d[len(h)] / len(r)


def _expand_casing_variants(phrases: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        for variant in (phrase, phrase.lower(), phrase[:1].upper() + phrase[1:]):
            if variant and variant not in seen:
                seen.add(variant)
                out.append(variant)
    return out


def build_phrase_list() -> list[str]:
    phrases: list[str] = list(DOMAIN_VOCAB)
    for variants in BRAND_VARIANTS.values():
        for v in variants:
            if v not in phrases:
                phrases.append(v)
    return _expand_casing_variants(phrases)


# ---------------------------------------------------------------------------
# Decoding strategy setters
# ---------------------------------------------------------------------------


def set_greedy_boost(
    model: Any,
    phrases: list[str],
    *,
    alpha: float,
    context_score: float,
    depth_scaling: float,
    use_bpe_dropout: bool = True,
) -> None:
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree.key_phrases_list", phrases, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.context_score", context_score, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.depth_scaling", depth_scaling, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.use_bpe_dropout", use_bpe_dropout, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)


def set_malsd_boost(
    model: Any,
    phrases: list[str],
    *,
    alpha: float,
    context_score: float,
    depth_scaling: float,
) -> None:
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "malsd_batch"
    OmegaConf.update(cfg, "beam.beam_size", 4, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.key_phrases_list", phrases, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.context_score", context_score, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree.depth_scaling", depth_scaling, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree_alpha", alpha, force_add=True)
    model.change_decoding_strategy(cfg)


# ---------------------------------------------------------------------------
# Evaluate one config on all clips
# ---------------------------------------------------------------------------


def evaluate(model: Any, clips: list[dict], label: str) -> dict:
    print(f"\n{'=' * 60}")
    print(f"Evaluating: {label}")
    print(f"{'=' * 60}")

    hyps = transcribe_all(model, clips)

    brand_clips = [(c, h) for c, h in zip(clips, hyps, strict=False) if c["is_brand"]]
    neutral_clips = [(c, h) for c, h in zip(clips, hyps, strict=False) if not c["is_brand"]]

    # Brand metrics
    brand_exact = brand_phonetic = brand_garbage = 0
    brand_wer_sum = 0.0
    for clip, hyp in brand_clips:
        brand = brand_in_ref(clip["transcript"])
        if brand:
            v = label_brand(hyp, brand)
            if v == "EXACT":
                brand_exact += 1
            elif v == "PHONETIC":
                brand_phonetic += 1
            else:
                brand_garbage += 1
        brand_wer_sum += wer(clip["transcript"], hyp)

    # Neutral metrics
    neutral_wer_sum = sum(wer(c["transcript"], h) for c, h in neutral_clips)

    # Overall WER
    overall_wer_sum = sum(wer(c["transcript"], h) for c, h in zip(clips, hyps, strict=False))

    n_brand = len(brand_clips)
    n_neutral = len(neutral_clips)
    n_total = len(clips)

    result = {
        "label": label,
        "n_total": n_total,
        "n_brand": n_brand,
        "n_neutral": n_neutral,
        "brand_exact": brand_exact,
        "brand_exact_rate": round(brand_exact / max(n_brand, 1), 3),
        "brand_phonetic": brand_phonetic,
        "brand_garbage": brand_garbage,
        "brand_wer": round(brand_wer_sum / max(n_brand, 1), 3),
        "neutral_wer": round(neutral_wer_sum / max(n_neutral, 1), 3),
        "overall_wer": round(overall_wer_sum / max(n_total, 1), 3),
        "per_clip": [
            {
                "clip_id": c["clip_id"],
                "ref": c["transcript"],
                "hyp": h,
                "is_brand": c["is_brand"],
                "wer": round(wer(c["transcript"], h), 3),
                "brand_verdict": (
                    label_brand(h, brand_in_ref(c["transcript"]))
                    if c["is_brand"] and brand_in_ref(c["transcript"])
                    else "N/A"
                ),
            }
            for c, h in zip(clips, hyps, strict=False)
        ],
    }

    print(f"  Brand EXACT:   {brand_exact}/{n_brand} ({result['brand_exact_rate']:.0%})")
    print(f"  Brand PHONETIC:{brand_phonetic}/{n_brand}")
    print(f"  Brand GARBAGE: {brand_garbage}/{n_brand}")
    print(f"  Brand WER:     {result['brand_wer']:.1%}")
    print(f"  Neutral WER:   {result['neutral_wer']:.1%}  ({n_neutral} clips)")
    print(f"  Overall WER:   {result['overall_wer']:.1%}  ({n_total} clips)")
    return result


# ---------------------------------------------------------------------------
# Write final report
# ---------------------------------------------------------------------------


def write_report(baseline: dict, new_cfg: dict) -> None:
    n = baseline["n_total"]
    nb = baseline["n_brand"]
    nn = baseline["n_neutral"]

    def delta(new_val: float, base_val: float, pct: bool = True) -> str:
        d = new_val - base_val
        sign = "+" if d >= 0 else ""
        if pct:
            return f"{sign}{d:.1%}"
        return f"{sign}{d:.3f}"

    lines = [
        "# t0023 — Validation: Current Prod vs Recommended Config",
        "",
        f"**Eval:** all {n} gold-92 clips ({nb} brand, {nn} neutral) | Azure H100 | 2026-07-08",
        "",
        "## Summary",
        "",
        "| Metric | Current prod | Recommended | Delta |",
        "|--------|-------------|-------------|-------|",
        f"| Brand EXACT ({nb} clips) "
        f"| {baseline['brand_exact']}/{nb} ({baseline['brand_exact_rate']:.0%}) "
        f"| {new_cfg['brand_exact']}/{nb} ({new_cfg['brand_exact_rate']:.0%}) "
        f"| **{delta(new_cfg['brand_exact_rate'], baseline['brand_exact_rate'])}** |",
        f"| Brand PHONETIC "
        f"| {baseline['brand_phonetic']}/{nb} "
        f"| {new_cfg['brand_phonetic']}/{nb} | — |",
        f"| Brand GARBAGE "
        f"| {baseline['brand_garbage']}/{nb} "
        f"| {new_cfg['brand_garbage']}/{nb} | — |",
        f"| Brand WER "
        f"| {baseline['brand_wer']:.1%} "
        f"| {new_cfg['brand_wer']:.1%} "
        f"| {delta(new_cfg['brand_wer'], baseline['brand_wer'])} |",
        f"| Neutral WER ({nn} clips) "
        f"| {baseline['neutral_wer']:.1%} "
        f"| {new_cfg['neutral_wer']:.1%} "
        f"| {delta(new_cfg['neutral_wer'], baseline['neutral_wer'])} |",
        f"| Overall WER ({n} clips) "
        f"| {baseline['overall_wer']:.1%} "
        f"| {new_cfg['overall_wer']:.1%} "
        f"| {delta(new_cfg['overall_wer'], baseline['overall_wer'])} |",
        "",
        "## Config",
        "",
        "| | Baseline | Recommended |",
        "|---|---|---|",
        "| Model | parakeet-tdt-0.6b-v3 | parakeet-unified-en-0.6b |",
        "| Strategy | greedy_batch | malsd_batch |",
        "| context_score | 1.0 | 3.0 |",
        "| depth_scaling | 2.0 | 0.5 |",
        "| alpha | 1.0 | 1.5 |",
        "",
        "## Verdict",
        "",
    ]

    brand_improvement = new_cfg["brand_exact_rate"] - baseline["brand_exact_rate"]
    neutral_delta = new_cfg["neutral_wer"] - baseline["neutral_wer"]

    if brand_improvement > 0.3 and neutral_delta < 0.1:
        verdict = "SHIP IT — large brand gain, neutral WER acceptable"
    elif brand_improvement > 0.3 and neutral_delta < 0.2:
        verdict = "SHIP WITH MONITORING — large brand gain, mild neutral WER regression"
    elif brand_improvement > 0.3:
        verdict = "REVIEW — large brand gain but significant neutral WER regression"
    else:
        verdict = "INCONCLUSIVE — insufficient brand improvement"

    lines += [
        f"**{verdict}**",
        "",
        f"- Brand EXACT: {baseline['brand_exact_rate']:.0%} → {new_cfg['brand_exact_rate']:.0%} "
        f"({delta(new_cfg['brand_exact_rate'], baseline['brand_exact_rate'])})",
        f"- Neutral WER: {baseline['neutral_wer']:.1%} → {new_cfg['neutral_wer']:.1%} "
        f"({delta(new_cfg['neutral_wer'], baseline['neutral_wer'])})",
        f"- Overall WER: {baseline['overall_wer']:.1%} → {new_cfg['overall_wer']:.1%} "
        f"({delta(new_cfg['overall_wer'], baseline['overall_wer'])})",
    ]

    out = RESULTS_DIR / "validation.md"
    out.write_text("\n".join(lines))

    # Per-clip detail
    detail_rows = []
    for b, n_row in zip(baseline["per_clip"], new_cfg["per_clip"], strict=False):
        detail_rows.append(
            {
                "clip_id": b["clip_id"],
                "ref": b["ref"],
                "is_brand": b["is_brand"],
                "baseline_hyp": b["hyp"],
                "baseline_wer": b["wer"],
                "baseline_verdict": b["brand_verdict"],
                "new_hyp": n_row["hyp"],
                "new_wer": n_row["wer"],
                "new_verdict": n_row["brand_verdict"],
            }
        )
    detail_out = RESULTS_DIR / "validation_per_clip.jsonl"
    detail_out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in detail_rows))

    print("\n" + "\n".join(lines))
    print(f"\nSaved: {out}")
    print(f"Saved per-clip: {detail_out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clips", type=int, default=None, help="limit total clips (smoke)")
    args = parser.parse_args()

    print(f"Loading gold-92 from {GOLD92_GROUND_TRUTH} ...")
    clips = load_all_clips(GOLD92_GROUND_TRUTH, GOLD92_AUDIO_DIR, max_clips=args.clips)
    n_brand = sum(1 for c in clips if c["is_brand"])
    n_neutral = sum(1 for c in clips if not c["is_brand"])
    print(f"Total clips: {len(clips)} | Brand: {n_brand} | Neutral: {n_neutral}")

    phrases = build_phrase_list()
    print(f"Phrase list: {len(phrases)} terms (with casing variants)")

    device = "cuda" if _cuda_available() else "cpu"

    # ------------------------------------------------------------------
    # 1. Baseline: TDT + greedy_batch (current prod)
    # ------------------------------------------------------------------
    print(f"\nLoading baseline model {BASELINE_MODEL} ...")
    import nemo.collections.asr as nemo_asr

    tdt_model = nemo_asr.models.ASRModel.from_pretrained(BASELINE_MODEL, map_location=device)
    tdt_model.eval()
    if _cuda_available():
        tdt_model = tdt_model.cuda()

    set_greedy_boost(
        tdt_model,
        phrases,
        alpha=1.0,
        context_score=1.0,
        depth_scaling=2.0,
        use_bpe_dropout=True,
    )
    baseline_result = evaluate(tdt_model, clips, BASELINE_LABEL)

    out = RESULTS_DIR / "validation_baseline.jsonl"
    out.write_text(
        json.dumps(
            {k: v for k, v in baseline_result.items() if k != "per_clip"}, ensure_ascii=False
        )
    )

    # Free TDT model memory before loading unified
    del tdt_model
    try:
        import torch

        torch.cuda.empty_cache()
    except Exception:
        pass

    # ------------------------------------------------------------------
    # 2. Recommended: Unified + malsd_batch + cs=3.0/ds=0.5/α=1.5
    # ------------------------------------------------------------------
    print(f"\nLoading recommended model {NEW_MODEL} ...")
    unified_model = nemo_asr.models.ASRModel.from_pretrained(NEW_MODEL, map_location=device)
    unified_model.eval()
    if _cuda_available():
        unified_model = unified_model.cuda()

    set_malsd_boost(
        unified_model,
        phrases,
        alpha=1.5,
        context_score=3.0,
        depth_scaling=0.5,
    )
    new_result = evaluate(unified_model, clips, NEW_LABEL)

    out2 = RESULTS_DIR / "validation_new.jsonl"
    out2.write_text(
        json.dumps({k: v for k, v in new_result.items() if k != "per_clip"}, ensure_ascii=False)
    )

    # ------------------------------------------------------------------
    # 3. Final report
    # ------------------------------------------------------------------
    write_report(baseline_result, new_result)


if __name__ == "__main__":
    main()
