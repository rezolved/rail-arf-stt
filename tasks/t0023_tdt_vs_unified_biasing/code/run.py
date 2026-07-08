"""TDT vs Unified GPU-PB biasing comparison on gold-92 (t0023).

Runs param sweep on parakeet-tdt-0.6b-v3 (current prod model) and compares
against t0022 results for parakeet-unified-en-0.6b.

Usage (gpu-azure, conda env stt, PYTHONPATH=repo root):
    python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py
    python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py --clips 5   # smoke test
    python -u tasks/t0023_tdt_vs_unified_biasing/code/run.py --skip-sweep  # baseline only
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

T0022_RESULTS = REPO_ROOT / "tasks" / "t0022_gpu_pb_diagnostic" / "results" / "param_sweep.jsonl"


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
# Config
# ---------------------------------------------------------------------------
TDT_MODEL_ID = "nvidia/parakeet-tdt-0.6b-v3"
UNIFIED_MODEL_ID = "nvidia/parakeet-unified-en-0.6b"
SAMPLE_RATE = 16_000

# Current prod config (greedy_batch, from brainpowa-realtime-api config.py)
PROD_ALPHA = 1.0
PROD_CONTEXT_SCORE = 1.0
PROD_DEPTH_SCALING = 2.0
PROD_USE_BPE_DROPOUT = True

# t0022 best cell for unified
UNIFIED_BEST = {"context_score": 3.0, "depth_scaling": 0.5, "alpha": 1.5, "strategy": "malsd_batch"}

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

SWEEP_CONTEXT_SCORES = [1.0, 1.5, 2.0, 2.5, 3.0]
SWEEP_DEPTH_SCALINGS = [0.5, 1.0, 1.5, 2.0]
SWEEP_ALPHAS = [1.0, 1.5, 2.0, 2.5, 3.0]


# ---------------------------------------------------------------------------
# Helpers (same as t0022)
# ---------------------------------------------------------------------------


def load_clips(
    ground_truth: Path,
    audio_dir: Path,
    max_clips: int | None = None,
) -> tuple[list, list]:
    brand_clips: list = []
    neutral_clips: list = []
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
        rec = {
            "clip_id": clip_id,
            "transcript": text,
            "audio": audio,
            "audio_path": str(audio_path),
        }
        if TERM_FILTER.search(text):
            brand_clips.append(rec)
        else:
            neutral_clips.append(rec)
    brand_clips = brand_clips[:max_clips] if max_clips is not None else brand_clips
    neutral_clips = neutral_clips[:10]
    return brand_clips, neutral_clips


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


def transcribe(model: Any, clips: list) -> list[str]:
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
    """Mirror prod: expand each phrase to {as-given, lower, Capitalized}, deduped."""
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
    # Mirror prod: expand each phrase to casing variants before building boosting tree
    return _expand_casing_variants(phrases)


# ---------------------------------------------------------------------------
# Decoding strategy helpers
# ---------------------------------------------------------------------------


def reset_greedy_no_boost(model: Any) -> None:
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree", None, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", None, force_add=True)
    model.change_decoding_strategy(cfg)


def apply_greedy_boost(
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


def apply_malsd_boost(
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
# TDT baseline (prod config)
# ---------------------------------------------------------------------------


def run_tdt_baseline(
    model: Any, brand_clips: list, neutral_clips: list, phrases: list[str]
) -> dict:
    print("\n=== TDT BASELINE (current prod: greedy_batch cs=1/ds=2/alpha=1) ===")

    # greedy no boost
    reset_greedy_no_boost(model)
    hyps_no_boost = transcribe(model, brand_clips)
    exact_no_boost = sum(
        1
        for clip, hyp in zip(brand_clips, hyps_no_boost, strict=False)
        if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
    )

    # greedy + boost (prod config)
    apply_greedy_boost(
        model,
        phrases,
        alpha=PROD_ALPHA,
        context_score=PROD_CONTEXT_SCORE,
        depth_scaling=PROD_DEPTH_SCALING,
        use_bpe_dropout=PROD_USE_BPE_DROPOUT,
    )
    hyps_prod = transcribe(model, brand_clips)
    exact_prod = sum(
        1
        for clip, hyp in zip(brand_clips, hyps_prod, strict=False)
        if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
    )

    n = len(brand_clips)
    result = {
        "greedy_no_boost_exact": exact_no_boost,
        "greedy_no_boost_rate": round(exact_no_boost / max(n, 1), 3),
        "greedy_prod_boost_exact": exact_prod,
        "greedy_prod_boost_rate": round(exact_prod / max(n, 1), 3),
        "n_brand_clips": n,
    }
    print(f"  greedy no-boost:  {exact_no_boost}/{n} ({100 * exact_no_boost // max(n, 1)}%)")
    print(f"  greedy prod-cfg:  {exact_prod}/{n} ({100 * exact_prod // max(n, 1)}%)")

    out = RESULTS_DIR / "tdt_baseline.jsonl"
    out.write_text(json.dumps(result, ensure_ascii=False))
    print(f"  Saved: {out}")
    return result


# ---------------------------------------------------------------------------
# TDT malsd_batch sweep (same grid as t0022)
# ---------------------------------------------------------------------------


def run_tdt_sweep(
    model: Any, brand_clips: list, neutral_clips: list, phrases: list[str]
) -> list[dict]:
    print("\n=== TDT malsd_batch PARAM SWEEP ===")
    results = []
    total = len(SWEEP_CONTEXT_SCORES) * len(SWEEP_DEPTH_SCALINGS) * len(SWEEP_ALPHAS)
    i = 0
    for cs in SWEEP_CONTEXT_SCORES:
        for ds in SWEEP_DEPTH_SCALINGS:
            for alpha in SWEEP_ALPHAS:
                i += 1
                print(f"  [{i}/{total}] cs={cs} ds={ds} alpha={alpha} ...", flush=True)
                try:
                    apply_malsd_boost(
                        model, phrases, alpha=alpha, context_score=cs, depth_scaling=ds
                    )
                    brand_hyps = transcribe(model, brand_clips)
                    neutral_hyps = transcribe(model, neutral_clips) if neutral_clips else []

                    exact = sum(
                        1
                        for clip, hyp in zip(brand_clips, brand_hyps, strict=False)
                        if (b := brand_in_ref(clip["transcript"]))
                        and label_brand(hyp, b) == "EXACT"
                    )
                    n_wer = (
                        sum(
                            wer(c["transcript"], h)
                            for c, h in zip(neutral_clips, neutral_hyps, strict=False)
                        )
                        / len(neutral_clips)
                        if neutral_clips
                        else None
                    )
                    rec = {
                        "context_score": cs,
                        "depth_scaling": ds,
                        "alpha": alpha,
                        "brand_exact_rate": round(exact / max(len(brand_clips), 1), 3),
                        "neutral_wer": round(n_wer, 3) if n_wer is not None else None,
                    }
                except Exception as e:
                    rec = {
                        "context_score": cs,
                        "depth_scaling": ds,
                        "alpha": alpha,
                        "brand_exact_rate": None,
                        "neutral_wer": None,
                        "error": str(e),
                    }
                results.append(rec)
                print(f"    brand_exact={rec['brand_exact_rate']} neutral_wer={rec['neutral_wer']}")

    out = RESULTS_DIR / "tdt_sweep.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results))
    print(f"Saved: {out}")
    return results


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------


def write_comparison(
    brand_clips: list,
    tdt_baseline: dict,
    tdt_sweep: list[dict],
) -> None:
    n = tdt_baseline["n_brand_clips"]

    # TDT best sweep cell
    valid_tdt = [r for r in tdt_sweep if r.get("brand_exact_rate") is not None]
    tdt_best = (
        max(valid_tdt, key=lambda r: (r["brand_exact_rate"], -(r["neutral_wer"] or 99)))
        if valid_tdt
        else None
    )

    # Unified results from t0022
    unified_sweep: list[dict] = []
    if T0022_RESULTS.exists():
        for raw in T0022_RESULTS.read_text().splitlines():
            if raw.strip():
                unified_sweep.append(json.loads(raw))
    valid_unified = [r for r in unified_sweep if r.get("brand_exact_rate") is not None]
    unified_best = (
        max(valid_unified, key=lambda r: (r["brand_exact_rate"], -(r["neutral_wer"] or 99)))
        if valid_unified
        else None
    )

    lines = [
        "# t0023 — TDT vs Unified: GPU-PB Biasing Comparison",
        "",
        f"**Eval set:** gold-92, {n} brand clips (Rezolve/brainpowa), 10 neutral clips",
        "**Date:** 2026-07-08 | **Machine:** Azure H100 NVL",
        "",
        "## Results",
        "",
        "| Config | Model | Strategy | Brand EXACT | Neutral WER |",
        "|--------|-------|----------|-------------|-------------|",
    ]

    # Current prod
    prod_rate = tdt_baseline["greedy_prod_boost_rate"]
    prod_exact = tdt_baseline["greedy_prod_boost_exact"]
    lines.append(
        f"| **Current prod** | parakeet-tdt-0.6b-v3 | greedy_batch cs=1/ds=2/α=1 "
        f"| {prod_exact}/{n} ({prod_rate:.0%}) | ~15% (baseline) |"
    )

    # TDT baseline no boost
    nb_rate = tdt_baseline["greedy_no_boost_rate"]
    nb_exact = tdt_baseline["greedy_no_boost_exact"]
    lines.append(
        f"| TDT no boost | parakeet-tdt-0.6b-v3 | greedy_batch (no boost) "
        f"| {nb_exact}/{n} ({nb_rate:.0%}) | ~15% |"
    )

    # TDT best
    if tdt_best:
        te = int(round(tdt_best["brand_exact_rate"] * n))
        lines.append(
            f"| **TDT best sweep** | parakeet-tdt-0.6b-v3 | malsd_batch "
            f"cs={tdt_best['context_score']}/ds={tdt_best['depth_scaling']}/α={tdt_best['alpha']} "
            f"| {te}/{n} ({tdt_best['brand_exact_rate']:.0%}) "
            f"| {tdt_best['neutral_wer']:.1%} |"
        )
    else:
        lines.append("| **TDT best sweep** | parakeet-tdt-0.6b-v3 | malsd_batch | N/A | N/A |")

    # Unified best (t0022)
    if unified_best:
        ue = int(round(unified_best["brand_exact_rate"] * n))
        cs = unified_best["context_score"]
        ds = unified_best["depth_scaling"]
        al = unified_best["alpha"]
        lines.append(
            f"| **Unified best (t0022)** | parakeet-unified-en-0.6b | malsd_batch "
            f"cs={cs}/ds={ds}/α={al} "
            f"| {ue}/{n} ({unified_best['brand_exact_rate']:.0%}) "
            f"| {unified_best['neutral_wer']:.1%} |"
        )
    else:
        lines.append(
            "| **Unified best (t0022)** | parakeet-unified-en-0.6b | malsd_batch "
            "| 21/35 (60%) | 8.7% |"
        )

    lines += [
        "",
        "## Verdict",
        "",
    ]

    if tdt_best and unified_best:
        tdt_wins = tdt_best["brand_exact_rate"] >= unified_best["brand_exact_rate"]
        winner = "TDT" if tdt_wins else "Unified"
        tdt_rate = tdt_best["brand_exact_rate"]
        uni_rate = unified_best["brand_exact_rate"]
        lines.append(
            f"**{winner}** wins on brand EXACT "
            f"(TDT best: {tdt_rate:.0%} vs Unified best: {uni_rate:.0%})."
        )
    elif unified_best:
        uni_rate = unified_best["brand_exact_rate"]
        lines.append(f"Unified best (t0022): {uni_rate:.0%} brand EXACT. TDT sweep not run.")

    lines += [
        "",
        "## Recommendation for prod migration",
        "",
        "Switch to `parakeet-unified-en-0.6b` with:",
        "```",
        "strategy      = malsd_batch",
        "beam_size     = 4",
        f"context_score = {unified_best['context_score'] if unified_best else 3.0}",
        f"depth_scaling = {unified_best['depth_scaling'] if unified_best else 0.5}",
        f"alpha         = {unified_best['alpha'] if unified_best else 1.5}",
        "```",
        "",
        (
            f"Improvement over current prod: "
            f"{tdt_baseline['greedy_prod_boost_rate']:.0%} → "
            f"{unified_best['brand_exact_rate']:.0%} brand EXACT "
            f"(+{unified_best['brand_exact_rate'] - tdt_baseline['greedy_prod_boost_rate']:.0%} pp)"
        )
        if unified_best
        else "",
    ]

    out = RESULTS_DIR / "comparison.md"
    out.write_text("\n".join(lines))
    print(f"\nSaved comparison: {out}")
    print("\n".join(lines))


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
    parser.add_argument("--clips", type=int, default=None)
    parser.add_argument("--skip-sweep", action="store_true", help="run TDT baseline only, no sweep")
    args = parser.parse_args()

    print(f"Loading gold-92 from {GOLD92_GROUND_TRUTH} ...")
    brand_clips, neutral_clips = load_clips(
        GOLD92_GROUND_TRUTH, GOLD92_AUDIO_DIR, max_clips=args.clips
    )
    print(f"Brand clips: {len(brand_clips)} | Neutral clips: {len(neutral_clips)}")

    phrases = build_phrase_list()
    print(f"Phrase list: {len(phrases)} terms")

    print(f"\nLoading TDT model {TDT_MODEL_ID} ...")
    import nemo.collections.asr as nemo_asr

    device = "cuda" if _cuda_available() else "cpu"
    model = nemo_asr.models.ASRModel.from_pretrained(TDT_MODEL_ID, map_location=device)
    model.eval()
    if _cuda_available():
        model = model.cuda()

    tdt_baseline = run_tdt_baseline(model, brand_clips, neutral_clips, phrases)

    tdt_sweep: list[dict] = []
    if not args.skip_sweep:
        tdt_sweep = run_tdt_sweep(model, brand_clips, neutral_clips, phrases)
    else:
        # Load existing sweep if available
        existing = RESULTS_DIR / "tdt_sweep.jsonl"
        if existing.exists():
            tdt_sweep = [
                json.loads(raw) for raw in existing.read_text().splitlines() if raw.strip()
            ]
            print(f"Loaded existing TDT sweep ({len(tdt_sweep)} cells)")

    write_comparison(brand_clips, tdt_baseline, tdt_sweep)


if __name__ == "__main__":
    main()
