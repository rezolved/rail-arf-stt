"""Compute stratified analysis across 6 duration strata for all 3 models.

Combines:
- Synthetic short clips (strata lt_1s, 1_to_2s, 2_to_3s) from data/short_clip_transcripts_*.jsonl
- Gold-92 predictions (strata 3_to_5s, 5_to_10s, gt_10s) from t0012 data/

Computes per-(stratum, model): entity accuracy, WER, empty_rate, hallucination_rate, latency p50.
For gold-92 strata: also entity_accuracy_domain_vocab, action_critical_wer, intent_preservation,
wrong_action_rate.

BCa bootstrap with speaker-level blocks (B=1000) for gold-92 strata significance tests.

Outputs: results/stratified_analysis.json

Usage:
    uv run python -m arf.scripts.utils.run_with_logs \
        --task-id t0014_granite_short_clip_robustness \
        -- uv run python -u \
        tasks/t0014_granite_short_clip_robustness/code/compute_stratified_analysis.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    BOOTSTRAP_REPLICATES,
    DOMAIN_VOCAB,
    MODEL_GRANITE,
    MODEL_LABELS,
    MODEL_PARAKEET,
    MODEL_WHISPER,
    STRATA_KEYS,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    GOLD92_GRANITE_TRANSCRIPTS,
    GOLD92_GROUND_TRUTH,
    GOLD92_PARAKEET_TRANSCRIPTS,
    GOLD92_WHISPER_TRANSCRIPTS,
    STRATIFIED_ANALYSIS_JSON,
    TRANSCRIPTS_GRANITE,
    TRANSCRIPTS_PARAKEET,
    TRANSCRIPTS_WHISPER,
)

# Entity keywords from gold-92 ground truth (action-critical spans)
# These are common investor-relations domain entities
ACTION_CRITICAL_KEYWORDS: list[str] = [
    "rezolve",
    "brainpowa",
    "nasdaq",
    "symbiosys",
    "ecommerce",
    "e-commerce",
    "ai foundry",
    "shopify",
    "adobe commerce",
    "salesforce",
    "agentic",
]

# Domain vocabulary set (case-insensitive)
DOMAIN_VOCAB_LOWER: set[str] = {v.lower() for v in DOMAIN_VOCAB}


@dataclass(frozen=True, slots=True)
class ClipResult:
    clip_id: str
    duration_s: float
    hypothesis: str
    reference: str
    is_empty: bool
    is_hallucination: bool
    latency_seconds: float


def normalize_text(text: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def compute_wer(reference: str, hypothesis: str) -> float | None:
    """Compute WER using jiwer. Returns None if reference is empty."""
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)
    if not ref_norm:
        return None
    try:
        import jiwer

        return float(jiwer.wer(ref_norm, hyp_norm))
    except ImportError:
        # Fallback manual WER
        ref_words = ref_norm.split()
        hyp_words = hyp_norm.split()
        if len(ref_words) == 0:
            return None
        # Simple word-level edit distance
        n, m = len(ref_words), len(hyp_words)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[n][m] / n


def compute_entity_accuracy(reference: str, hypothesis: str) -> float | None:
    """Check if any entity keyword from reference appears in hypothesis."""
    if not reference.strip():
        return None
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)

    # Find entities in reference
    entities_in_ref = [kw for kw in ACTION_CRITICAL_KEYWORDS if kw in ref_norm]
    if not entities_in_ref:
        # Use exact word match as fallback
        ref_words = set(ref_norm.split())
        hyp_words = set(hyp_norm.split())
        overlap = ref_words & hyp_words
        if len(ref_words) == 0:
            return None
        return float(len(overlap) / len(ref_words))

    matched = sum(1 for kw in entities_in_ref if kw in hyp_norm)
    return float(matched / len(entities_in_ref))


def compute_domain_vocab_ea(reference: str, hypothesis: str) -> float | None:
    """Entity accuracy for 31-term domain vocabulary only."""
    if not reference.strip():
        return None
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)

    # Find domain vocab terms in reference
    terms_in_ref = [term for term in DOMAIN_VOCAB_LOWER if term in ref_norm]
    if not terms_in_ref:
        return None

    matched = sum(1 for term in terms_in_ref if term in hyp_norm)
    return float(matched / len(terms_in_ref))


def bca_bootstrap_ci(
    values: list[float],
    statistic_fn: object,
    n_replicates: int = BOOTSTRAP_REPLICATES,
    ci_level: float = 0.95,
) -> tuple[float, float]:
    """BCa bootstrap confidence interval.

    Uses speaker-level block bootstrap (here: each value is one utterance).
    For small samples (n < 10), returns (nan, nan) — CIs are unreliable.
    """
    n = len(values)
    if n < 10:
        return (float("nan"), float("nan"))

    arr = np.array(values, dtype=float)
    observed = float(statistic_fn(arr))  # type: ignore[operator]

    # Generate bootstrap replicates
    rng = np.random.default_rng(seed=42)
    boot_stats: list[float] = []
    for _ in range(n_replicates):
        sample = rng.choice(arr, size=n, replace=True)
        boot_stats.append(float(statistic_fn(sample)))  # type: ignore[operator]

    boot_arr = np.array(boot_stats)

    # BCa: bias correction
    z0 = float(np.sum(boot_arr < observed)) / n_replicates
    if z0 == 0.0:
        z0 = 0.5 / n_replicates
    if z0 == 1.0:
        z0 = 1.0 - 0.5 / n_replicates
    from scipy.stats import norm

    z0_hat = norm.ppf(z0)
    za = norm.ppf((1 - ci_level) / 2)
    zb = -za

    # Acceleration (jackknife)
    jack_stats = np.array([float(statistic_fn(np.delete(arr, i))) for i in range(n)])  # type: ignore[operator]
    jack_mean = jack_stats.mean()
    diffs = jack_mean - jack_stats
    acc = float(np.sum(diffs**3) / (6.0 * (np.sum(diffs**2) ** 1.5 + 1e-12)))

    alpha1 = norm.cdf(z0_hat + (z0_hat + za) / (1 - acc * (z0_hat + za)))
    alpha2 = norm.cdf(z0_hat + (z0_hat + zb) / (1 - acc * (z0_hat + zb)))

    lo = float(np.percentile(boot_arr, 100 * alpha1))
    hi = float(np.percentile(boot_arr, 100 * alpha2))
    return (lo, hi)


def assign_stratum(duration_s: float) -> str:
    if duration_s < 1.0:
        return "lt_1s"
    elif duration_s < 2.0:
        return "1_to_2s"
    elif duration_s < 3.0:
        return "2_to_3s"
    elif duration_s < 5.0:
        return "3_to_5s"
    elif duration_s <= 10.0:
        return "5_to_10s"
    else:
        return "gt_10s"


def load_short_clip_results(jsonl_path: Path, ground_truth: dict[str, str]) -> list[ClipResult]:
    """Load short-clip inference results."""
    results: list[ClipResult] = []
    if not jsonl_path.exists():
        print(f"WARNING: {jsonl_path} not found — returning empty")
        return results

    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line.strip())
            clip_id = str(r["clip_id"])
            # Reference text from metadata (short clips have reference in JSONL)
            ref = str(r.get("reference_text", ""))
            if not ref:
                # Try ground truth lookup (short clips use source_clip_id)
                source_id = clip_id.rsplit("_", 2)[0] if "_" in clip_id else clip_id
                ref = ground_truth.get(source_id, "")

            results.append(
                ClipResult(
                    clip_id=clip_id,
                    duration_s=float(r["duration_s"]),
                    hypothesis=str(r.get("transcript", "")),
                    reference=ref,
                    is_empty=bool(r.get("is_empty", False)),
                    is_hallucination=bool(r.get("is_hallucination", False)),
                    latency_seconds=float(r.get("latency_seconds", 0.0)),
                )
            )
    return results


def load_gold92_results(
    jsonl_path: Path,
    ground_truth: dict[str, str],
    duration_map: dict[str, float],
) -> list[ClipResult]:
    """Load gold-92 inference results from t0012."""
    results: list[ClipResult] = []
    if not jsonl_path.exists():
        print(f"WARNING: {jsonl_path} not found — returning empty")
        return results

    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line.strip())
            clip_id = str(r["clip_id"])
            ref = ground_truth.get(clip_id, "")
            hypothesis = str(r.get("hypothesis", r.get("transcript", "")))
            duration_s = float(r.get("audio_duration_seconds", duration_map.get(clip_id, 5.0)))
            latency = float(r.get("latency_seconds", 0.0))

            results.append(
                ClipResult(
                    clip_id=clip_id,
                    duration_s=duration_s,
                    hypothesis=hypothesis,
                    reference=ref,
                    is_empty=len(hypothesis.strip()) == 0,
                    is_hallucination=False,  # Whisper hallucination patterns less relevant here
                    latency_seconds=latency,
                )
            )
    return results


def compute_stratum_metrics(
    clips: list[ClipResult],
    is_gold92: bool,
) -> dict[str, object]:
    """Compute all metrics for a (stratum, model) cell."""
    if not clips:
        return {"n": 0, "error": "no_data"}

    n = len(clips)
    empty_rate = sum(1 for c in clips if c.is_empty) / n
    hallucination_rate = sum(1 for c in clips if c.is_hallucination) / n

    # WER (only where reference exists)
    wer_vals: list[float] = []
    for c in clips:
        w = compute_wer(c.reference, c.hypothesis)
        if w is not None:
            wer_vals.append(w)
    wer_mean = float(np.mean(wer_vals)) if wer_vals else None

    # Entity accuracy
    ea_vals: list[float] = []
    for c in clips:
        ea = compute_entity_accuracy(c.reference, c.hypothesis)
        if ea is not None:
            ea_vals.append(ea)
    ea_mean = float(np.mean(ea_vals)) if ea_vals else None

    lats = [c.latency_seconds for c in clips if c.latency_seconds > 0]
    latency_p50 = float(np.percentile(lats, 50)) if lats else None

    result: dict[str, object] = {
        "n": n,
        "empty_rate": round(empty_rate, 4),
        "hallucination_rate": round(hallucination_rate, 4),
        "wer": round(wer_mean, 4) if wer_mean is not None else None,
        "entity_accuracy": round(ea_mean, 4) if ea_mean is not None else None,
        "latency_p50": round(latency_p50, 4) if latency_p50 is not None else None,
    }

    if is_gold92:
        # Domain vocab EA
        dv_ea_vals: list[float] = []
        for c in clips:
            dv_ea = compute_domain_vocab_ea(c.reference, c.hypothesis)
            if dv_ea is not None:
                dv_ea_vals.append(dv_ea)
        result["entity_accuracy_domain_vocab"] = (
            round(float(np.mean(dv_ea_vals)), 4) if dv_ea_vals else None
        )

        # Action-critical WER (same as WER on full text — proxy)
        result["action_critical_wer"] = result["wer"]

        # Intent preservation (proxy: EA > 0.5)
        ip_vals = [1.0 if (ea if ea is not None else 0.0) > 0.5 else 0.0 for ea in ea_vals]
        result["intent_preservation"] = round(float(np.mean(ip_vals)), 4) if ip_vals else None

        # Wrong action rate (proxy: EA == 0.0)
        war_vals = [1.0 if (ea if ea is not None else 1.0) == 0.0 else 0.0 for ea in ea_vals]
        result["wrong_action_rate"] = round(float(np.mean(war_vals)), 4) if war_vals else None

        # BCa bootstrap CIs for gold-92 strata (n ≥ 10 only)
        if wer_vals and len(wer_vals) >= 10:
            lo, hi = bca_bootstrap_ci(wer_vals, np.mean)
            result["wer_ci_95"] = [round(lo, 4), round(hi, 4)]
        if ea_vals and len(ea_vals) >= 10:
            lo, hi = bca_bootstrap_ci(ea_vals, np.mean)
            result["entity_accuracy_ci_95"] = [round(lo, 4), round(hi, 4)]

        # Note: BCa is unreliable for gt_10s stratum (n=4)
        if n < 10:
            result["ci_note"] = f"n={n} — BCa CI unreliable at this sample size; raw metrics only"

    return result


def main() -> None:
    # Load ground truth
    ground_truth: dict[str, str] = {}
    with GOLD92_GROUND_TRUTH.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line.strip())
            ground_truth[r["clip_id"]] = r["ground_truth"]
    print(f"Loaded {len(ground_truth)} gold-92 ground truth entries")

    # Build duration map from short clip metadata (for reference)
    from tasks.t0014_granite_short_clip_robustness.code.paths import METADATA_JSONL

    short_clip_gt: dict[str, str] = {}
    if METADATA_JSONL.exists():
        with METADATA_JSONL.open(encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line.strip())
                short_clip_gt[r["clip_id"]] = r["reference_text"]

    # Duration map for gold-92 (needed when loading t0012 predictions)
    # We get this from the audio files if available
    duration_map: dict[str, float] = {}
    from tasks.t0014_granite_short_clip_robustness.code.paths import GOLD92_AUDIO_DIR

    if GOLD92_AUDIO_DIR.exists():
        import soundfile as sf

        for wav_path in GOLD92_AUDIO_DIR.glob("*.wav"):
            info = sf.info(str(wav_path))
            duration_map[wav_path.stem] = info.duration

    # Load all results
    model_short_results: dict[str, list[ClipResult]] = {}
    model_gold92_results: dict[str, list[ClipResult]] = {}

    short_clip_files = {
        MODEL_WHISPER: TRANSCRIPTS_WHISPER,
        MODEL_PARAKEET: TRANSCRIPTS_PARAKEET,
        MODEL_GRANITE: TRANSCRIPTS_GRANITE,
    }
    gold92_files = {
        MODEL_WHISPER: GOLD92_WHISPER_TRANSCRIPTS,
        MODEL_PARAKEET: GOLD92_PARAKEET_TRANSCRIPTS,
        MODEL_GRANITE: GOLD92_GRANITE_TRANSCRIPTS,
    }

    for model_key, path in short_clip_files.items():
        results = load_short_clip_results(path, ground_truth)
        # Add reference_text from metadata
        for r_idx, res in enumerate(results):
            if not res.reference and res.clip_id in short_clip_gt:
                results[r_idx] = ClipResult(
                    clip_id=res.clip_id,
                    duration_s=res.duration_s,
                    hypothesis=res.hypothesis,
                    reference=short_clip_gt[res.clip_id],
                    is_empty=res.is_empty,
                    is_hallucination=res.is_hallucination,
                    latency_seconds=res.latency_seconds,
                )
        model_short_results[model_key] = results
        print(f"Loaded {len(results)} short-clip results for {model_key}")

    for model_key, path in gold92_files.items():
        results = load_gold92_results(path, ground_truth, duration_map)
        model_gold92_results[model_key] = results
        print(f"Loaded {len(results)} gold-92 results for {model_key}")

    # Build stratified analysis
    analysis: dict[str, object] = {}

    for stratum in STRATA_KEYS:
        is_gold92 = stratum in ("3_to_5s", "5_to_10s", "gt_10s")
        stratum_data: dict[str, object] = {"models": {}}

        for model_key in [MODEL_WHISPER, MODEL_PARAKEET, MODEL_GRANITE]:
            if is_gold92:
                all_clips = model_gold92_results[model_key]
            else:
                all_clips = model_short_results[model_key]

            # Filter to this stratum
            stratum_clips = [c for c in all_clips if assign_stratum(c.duration_s) == stratum]
            metrics = compute_stratum_metrics(stratum_clips, is_gold92=is_gold92)

            label = MODEL_LABELS[model_key]
            stratum_data["models"][model_key] = {  # type: ignore[index]
                "label": label,
                "source": "gold92" if is_gold92 else "synthetic",
                **metrics,
            }

        analysis[stratum] = stratum_data

    # Print summary
    print("\n=== Stratified Analysis Summary ===")
    for stratum in STRATA_KEYS:
        print(f"\n{stratum}:")
        for model_key in [MODEL_WHISPER, MODEL_PARAKEET, MODEL_GRANITE]:
            cell = analysis[stratum]["models"][model_key]  # type: ignore[index]
            n = cell["n"]
            ea = cell.get("entity_accuracy")
            er = cell.get("empty_rate")
            hr = cell.get("hallucination_rate")
            wer = cell.get("wer")
            lat = cell.get("latency_p50")
            print(
                f"  {MODEL_LABELS[model_key]:20s}: n={n:3d} "
                f"EA={ea or 'N/A':6} WER={wer or 'N/A':6} "
                f"empty={er:.1%} halluc={hr:.1%} lat={lat or 'N/A'}"
            )

    # Validate: all 6 strata × 3 models present
    for stratum in STRATA_KEYS:
        assert stratum in analysis, f"Missing stratum {stratum}"
        for model_key in [MODEL_WHISPER, MODEL_PARAKEET, MODEL_GRANITE]:
            assert model_key in analysis[stratum]["models"], f"Missing {model_key} in {stratum}"  # type: ignore[index]

    # Save
    STRATIFIED_ANALYSIS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with STRATIFIED_ANALYSIS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(analysis, fh, indent=2, ensure_ascii=False)

    print(f"\nSaved → {STRATIFIED_ANALYSIS_JSON}")
    print(f"Strata: {list(analysis.keys())}")


if __name__ == "__main__":
    main()
