"""GPU-PB biasing diagnostic for parakeet-unified-en-0.6b (t0022).

Determines whether brand-recognition failure (Rezolve / brainpowa) is config-fixable
or fundamental (acoustic/tokenization).

Usage (on GPU box, PYTHONPATH=repo root, conda env stt):
    python -u tasks/t0022_gpu_pb_diagnostic/code/diagnostic.py
    python -u tasks/t0022_gpu_pb_diagnostic/code/diagnostic.py --clips 5   # smoke test
    python -u tasks/t0022_gpu_pb_diagnostic/code/diagnostic.py --skip-sweep # fast run
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


# Gold-92 dataset (primary eval set — held-out, inference only, no tuning)
def _find_gold92() -> tuple[Path, Path, Path]:
    """Return (ground_truth.jsonl, audio_dir, gold_set.jsonl)."""
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
            return gt, audio, base / "gold_set.jsonl"
    raise FileNotFoundError(f"gold-92 not found; tried: {candidates}")


GOLD92_GROUND_TRUTH, GOLD92_AUDIO_DIR, GOLD92_GOLD_SET = _find_gold92()

# Reuse domain vocab from t0017
sys.path.insert(0, str(REPO_ROOT))
from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (  # noqa: E402
    DOMAIN_VOCAB,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL_ID = "nvidia/parakeet-unified-en-0.6b"
SAMPLE_RATE = 16_000

TARGET_BRANDS = ["Rezolve", "brainpowa"]
BRAND_VARIANTS = {
    "Rezolve": ["Rezolve", "Rezolve AI", "rezolve"],
    "brainpowa": ["brainpowa", "Brain Powa", "Brain Power", "Brainpowa", "brain powa"],
}
# Phonetic near-misses that count as PHONETIC (not EXACT, not GARBAGE)
PHONETIC_PATTERNS = {
    "Rezolve": re.compile(r"\bresolve\b|\brezolve\b|\brezolv\b|\bresolved\b", re.I),
    "brainpowa": re.compile(r"\bbrain.?pow|\bbrain.?com|\bbrainpow|\bbraincom|\bbrain pow", re.I),
}
EXACT_PATTERNS = {
    "Rezolve": re.compile(r"\bRezolve\b"),
    "brainpowa": re.compile(r"\bbrainpowa\b", re.I),
}

TERM_FILTER = re.compile(r"rezolve|resolve|brainpowa|brain.?pow|brain.?com", re.I)

BASE_ALPHA = 1.0
BASE_CONTEXT_SCORE = 1.0
BASE_DEPTH_SCALING = 2.0
BASE_USE_BPE_DROPOUT = True

SWEEP_CONTEXT_SCORES = [1.0, 1.5, 2.0, 2.5, 3.0]
SWEEP_DEPTH_SCALINGS = [0.5, 1.0, 1.5, 2.0]
SWEEP_ALPHAS = [1.0, 1.5, 2.0, 2.5, 3.0]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_clips(
    ground_truth: Path,
    audio_dir: Path,
    max_clips: int | None = None,
) -> tuple[list, list]:
    """Return (brand_clips, neutral_clips) from gold-92 ground_truth.jsonl."""
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
    """Decode any NeMo transcription output to a plain string."""
    if isinstance(o, str):
        return o
    # Hypothesis object (beam/malsd_batch)
    if hasattr(o, "text") and isinstance(o.text, str):
        return o.text
    if hasattr(o, "y_sequence"):
        import numpy as np
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
        # malsd_batch / beam returns list of Hypothesis per clip
        if isinstance(o, list):
            o = o[0] if len(o) > 0 else ""
        decoded.append(_decode_output(o, model))
    return decoded


def apply_greedy_boosting(
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


def reset_greedy_no_boost(model: Any) -> None:
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree", None, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", None, force_add=True)
    model.change_decoding_strategy(cfg)


def apply_beam_no_boost(model: Any) -> None:
    from omegaconf import OmegaConf, open_dict

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "beam"
    OmegaConf.update(cfg, "beam.beam_size", 4, force_add=True)
    OmegaConf.update(cfg, "beam.boosting_tree", None, force_add=True)
    model.change_decoding_strategy(cfg)


def apply_beam_boosting(
    model: Any, phrases: list[str], *, alpha: float, context_score: float, depth_scaling: float
) -> None:
    # NeMo requires malsd_batch for beam + boosting_tree (beam strategy raises)
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


def label_brand(hyp: str, brand: str) -> str:
    if EXACT_PATTERNS[brand].search(hyp):
        return "EXACT"
    if PHONETIC_PATTERNS[brand].search(hyp):
        return "PHONETIC"
    return "GARBAGE"


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


def brand_in_ref(ref: str) -> str | None:
    for brand in TARGET_BRANDS:
        if EXACT_PATTERNS[brand].search(ref):
            return brand
        if PHONETIC_PATTERNS[brand].search(ref):
            return brand
    return None


# ---------------------------------------------------------------------------
# Step 1 — Tokenization probe
# ---------------------------------------------------------------------------


def step_tokenization(model: Any) -> None:
    print("\n" + "=" * 60)
    print("STEP 1 — TOKENIZATION PROBE")
    print("=" * 60)

    tokenizer = model.tokenizer
    probe_terms = list(dict.fromkeys(TARGET_BRANDS + DOMAIN_VOCAB))
    lines = []
    flagged = []

    for term in probe_terms:
        try:
            ids = tokenizer.text_to_ids(term)
            pieces = [tokenizer.ids_to_text([i]) for i in ids]
        except Exception as e:
            pieces = [f"ERROR:{e}"]
            ids = []

        flag = ""
        if len(ids) > 3:
            flag = " ⚠ MANY_FRAGMENTS"
        elif any(len(p) <= 2 for p in pieces):
            flag = " ⚠ SHORT_PIECES"

        line = f"  {term!r:40s}  {pieces}  ids={ids}{flag}"
        lines.append(line)
        print(line)
        if flag:
            flagged.append(term)

    out = RESULTS_DIR / "tokenization_probe.txt"
    out.write_text("\n".join(lines))
    print(f"\nFlagged ({len(flagged)}): {flagged}")
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Step 2+3 — Decoding matrix + per-brand verdicts
# ---------------------------------------------------------------------------


def step_decoding_matrix(
    model: Any, brand_clips: list, neutral_clips: list, all_phrases: list[str]
) -> dict:
    print("\n" + "=" * 60)
    print("STEP 2 — DECODING MATRIX (4 configs)")
    print("=" * 60)

    configs = {
        "a_greedy_no_boost": lambda: reset_greedy_no_boost(model),
        "b_greedy_boost": lambda: apply_greedy_boosting(
            model,
            all_phrases,
            alpha=BASE_ALPHA,
            context_score=BASE_CONTEXT_SCORE,
            depth_scaling=BASE_DEPTH_SCALING,
        ),
        "c_beam_no_boost": lambda: apply_beam_no_boost(model),
        "d_beam_boost": lambda: apply_beam_boosting(
            model,
            all_phrases,
            alpha=BASE_ALPHA,
            context_score=BASE_CONTEXT_SCORE,
            depth_scaling=BASE_DEPTH_SCALING,
        ),
    }

    all_results: dict[str, list[str]] = {}
    for cfg_name, setup_fn in configs.items():
        print(f"\n  Config {cfg_name} ...", flush=True)
        try:
            setup_fn()
            hyps = transcribe(model, brand_clips)
            all_results[cfg_name] = hyps
            # count brand hits
            hits = sum(
                1
                for clip, hyp in zip(brand_clips, hyps, strict=False)
                if brand_in_ref(clip["transcript"])
                and label_brand(hyp, brand_in_ref(clip["transcript"]) or "Rezolve") == "EXACT"
            )
            print(f"    brand_exact={hits}/{len(brand_clips)}")
        except Exception as e:
            print(f"    FAILED: {e}")
            all_results[cfg_name] = ["ERROR"] * len(brand_clips)

    # Save per-clip matrix
    matrix_rows = []
    for i, clip in enumerate(brand_clips):
        row = {
            "clip_id": clip.get("clip_id", f"clip_{i}"),
            "reference": clip["transcript"],
            "brand_in_ref": brand_in_ref(clip["transcript"]),
        }
        for cfg_name, hyps in all_results.items():
            hyp = hyps[i] if i < len(hyps) else "ERROR"
            brand = brand_in_ref(clip["transcript"])
            row[cfg_name] = hyp
            row[f"{cfg_name}_verdict"] = label_brand(hyp, brand) if brand else "N/A"
        matrix_rows.append(row)

    out = RESULTS_DIR / "decoding_matrix.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in matrix_rows))
    print(f"\nSaved: {out}")
    return all_results


# ---------------------------------------------------------------------------
# Step 4 — Param sweep (config d: beam + boost)
# ---------------------------------------------------------------------------


def step_param_sweep(
    model: Any, brand_clips: list, neutral_clips: list, all_phrases: list[str]
) -> list[dict]:
    print("\n" + "=" * 60)
    print("STEP 4 — PARAM SWEEP (beam + boost)")
    print("=" * 60)

    results = []
    total = len(SWEEP_CONTEXT_SCORES) * len(SWEEP_DEPTH_SCALINGS) * len(SWEEP_ALPHAS)
    i = 0
    for cs in SWEEP_CONTEXT_SCORES:
        for ds in SWEEP_DEPTH_SCALINGS:
            for alpha in SWEEP_ALPHAS:
                i += 1
                print(f"  [{i}/{total}] cs={cs} ds={ds} alpha={alpha} ...", flush=True)
                try:
                    apply_beam_boosting(
                        model, all_phrases, alpha=alpha, context_score=cs, depth_scaling=ds
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

    out = RESULTS_DIR / "param_sweep.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results))
    print(f"Saved: {out}")
    return results


# ---------------------------------------------------------------------------
# Step 5 — Summary
# ---------------------------------------------------------------------------


def step_summary(brand_clips: list, matrix_results: dict, sweep_results: list) -> None:
    print("\n" + "=" * 60)
    print("STEP 5 — SUMMARY")
    print("=" * 60)

    lines = ["# t0022 GPU-PB Diagnostic — Summary\n"]

    # Per-config brand recognition
    lines.append("## Brand recognition rate per config\n")
    lines.append("| Config | EXACT | PHONETIC | GARBAGE |")
    lines.append("|--------|-------|----------|---------|")
    for cfg_name in matrix_results:
        hyps = matrix_results[cfg_name]
        counts = {"EXACT": 0, "PHONETIC": 0, "GARBAGE": 0}
        total = 0
        for clip, hyp in zip(brand_clips, hyps, strict=False):
            brand = brand_in_ref(clip["transcript"])
            if not brand:
                continue
            v = label_brand(hyp, brand)
            counts[v] += 1
            total += 1
        if total:
            lines.append(
                f"| {cfg_name} | {counts['EXACT']}/{total} ({100 * counts['EXACT'] // total}%) "
                f"| {counts['PHONETIC']}/{total} | {counts['GARBAGE']}/{total} |"
            )

    # Greedy→beam delta
    if "a_greedy_no_boost" in matrix_results and "c_beam_no_boost" in matrix_results:
        g_exact = sum(
            1
            for clip, hyp in zip(brand_clips, matrix_results["a_greedy_no_boost"], strict=False)
            if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
        )
        b_exact = sum(
            1
            for clip, hyp in zip(brand_clips, matrix_results["c_beam_no_boost"], strict=False)
            if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
        )
        delta = b_exact - g_exact
        lines.append(f"\nGreedy→beam delta (no boost): {delta:+d} clips exact")

    # Best sweep cell
    valid_sweep = [r for r in sweep_results if r.get("brand_exact_rate") is not None]
    if valid_sweep:
        best = max(valid_sweep, key=lambda r: r["brand_exact_rate"])
        lines.append(
            f"\nBest sweep cell: cs={best['context_score']} ds={best['depth_scaling']} "
            f"alpha={best['alpha']} → brand_exact={best['brand_exact_rate']} "
            f"neutral_wer={best['neutral_wer']}"
        )

    # Dominant failure label (from greedy no-boost = baseline)
    if "a_greedy_no_boost" in matrix_results:
        phonetic = garbage = 0
        for clip, hyp in zip(brand_clips, matrix_results["a_greedy_no_boost"], strict=False):
            brand = brand_in_ref(clip["transcript"])
            if not brand:
                continue
            v = label_brand(hyp, brand)
            if v == "PHONETIC":
                phonetic += 1
            elif v == "GARBAGE":
                garbage += 1
        dominant = "PHONETIC_NEIGHBOR" if phonetic >= garbage else "GARBAGE"
        lines.append(f"\nDominant baseline failure: {dominant}")
        if dominant == "PHONETIC_NEIGHBOR":
            lines.append("  → encoder hears the brand but maps to wrong token; boosting may help")
        else:
            lines.append("  → encoder produces unrelated output; acoustic representation is absent")

    # Final verdict
    boost_gain = 0
    no_boost_rate = 0.0
    boost_rate = 0.0
    total_brand = sum(1 for c in brand_clips if brand_in_ref(c["transcript"]))
    has_both = "a_greedy_no_boost" in matrix_results and "b_greedy_boost" in matrix_results
    if total_brand and has_both:
        no_boost_exact = sum(
            1
            for clip, hyp in zip(brand_clips, matrix_results["a_greedy_no_boost"], strict=False)
            if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
        )
        boost_exact = sum(
            1
            for clip, hyp in zip(brand_clips, matrix_results["b_greedy_boost"], strict=False)
            if (b := brand_in_ref(clip["transcript"])) and label_brand(hyp, b) == "EXACT"
        )
        boost_gain = boost_exact - no_boost_exact
        no_boost_rate = no_boost_exact / total_brand
        boost_rate = boost_exact / total_brand

    lines.append(
        f"\nGreedy boost gain: {boost_gain:+d} clips ({no_boost_rate:.0%} → {boost_rate:.0%})"
    )

    if boost_gain >= 3 or (valid_sweep and best["brand_exact_rate"] > no_boost_rate + 0.15):
        verdict = "config-fixable (use beam / tune params)"
    else:
        verdict = "fundamental (encoder doesn't represent the brand -> needs fine-tuning)"

    lines.append(f"\n**VERDICT: {verdict}**")
    print("\n".join(lines))

    out = RESULTS_DIR / "summary.md"
    out.write_text("\n".join(lines))
    print(f"\nSaved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clips", type=int, default=None, help="limit brand clips (smoke test)")
    parser.add_argument("--skip-sweep", action="store_true", help="skip param sweep")
    parser.add_argument(
        "--sweep-only",
        action="store_true",
        help="run only param sweep (skip tokenization + decoding matrix)",
    )
    args = parser.parse_args()

    print(f"Loading gold-92 clips from {GOLD92_GROUND_TRUTH} ...")
    brand_clips, neutral_clips = load_clips(
        GOLD92_GROUND_TRUTH, GOLD92_AUDIO_DIR, max_clips=args.clips
    )
    print(f"Brand clips: {len(brand_clips)} | Neutral clips: {len(neutral_clips)}")

    print(f"\nLoading model {MODEL_ID} ...")
    import nemo.collections.asr as nemo_asr

    model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
        MODEL_ID, map_location="cuda" if _cuda_available() else "cpu"
    )
    model.eval()
    if _cuda_available():
        model = model.cuda()

    # Build phrase list: DOMAIN_VOCAB + orthographic brand variants
    all_phrases: list[str] = list(DOMAIN_VOCAB)
    for variants in BRAND_VARIANTS.values():
        for v in variants:
            if v not in all_phrases:
                all_phrases.append(v)

    matrix_results: dict = {}
    sweep_results: list[dict] = []

    if args.sweep_only:
        sweep_results = step_param_sweep(model, brand_clips, neutral_clips, all_phrases)
        # load previous matrix for summary
        matrix_path = RESULTS_DIR / "decoding_matrix.jsonl"
        if matrix_path.exists():
            rows = [json.loads(raw) for raw in matrix_path.read_text().splitlines() if raw.strip()]
            for cfg in ("a_greedy_no_boost", "b_greedy_boost", "c_beam_no_boost", "d_beam_boost"):
                matrix_results[cfg] = [r.get(cfg, "") for r in rows]
    else:
        step_tokenization(model)
        matrix_results = step_decoding_matrix(model, brand_clips, neutral_clips, all_phrases)
        if not args.skip_sweep:
            sweep_results = step_param_sweep(model, brand_clips, neutral_clips, all_phrases)

    step_summary(brand_clips, matrix_results, sweep_results)


def _cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


if __name__ == "__main__":
    main()
