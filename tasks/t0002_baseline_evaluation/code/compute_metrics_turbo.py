"""Compute metrics for Whisper turbo and merge into results/metrics.json.

Reads whisper_turbo_transcripts.json, computes all five registered metrics
with BCa bootstrap confidence intervals, and appends a whisper-turbo variant
to results/metrics.json alongside any existing variants.
"""

from __future__ import annotations

import json
import string
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jiwer
import numpy as np
from scipy.stats import bootstrap  # type: ignore[attr-defined]

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import (
    ANALYSIS_OUTPUT,
    METRICS_JSON,
    RESULTS_DIR,
    WHISPER_TURBO_TRANSCRIPTS,
)

BCa_N_RESAMPLES = 10_000
BCa_RANDOM_STATE = 42  # Per plan: use 42 (not the framework default 12345)


def normalise(text: str) -> str:
    """Lowercase and strip punctuation. Applied to both reference and hypothesis."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def bca_ci(
    per_clip_scores: np.ndarray,
    *,
    n_resamples: int = BCa_N_RESAMPLES,
    random_state: int = BCa_RANDOM_STATE,
) -> tuple[float, float]:
    """Compute BCa bootstrap 95% CI with NaN guard fallback to percentile."""
    try:
        result = bootstrap(
            (per_clip_scores,),
            statistic=np.mean,
            method="BCa",
            n_resamples=n_resamples,
            random_state=random_state,
        )
        low = float(result.confidence_interval.low)
        high = float(result.confidence_interval.high)
        if np.isnan(low) or np.isnan(high):
            raise ValueError("BCa returned NaN — falling back to percentile")
        return low, high
    except Exception:  # noqa: BLE001
        warnings.warn("BCa NaN guard triggered — using percentile bootstrap", stacklevel=2)
        result = bootstrap(
            (per_clip_scores,),
            statistic=np.mean,
            method="percentile",
            n_resamples=n_resamples,
            random_state=random_state,
        )
        return (
            float(result.confidence_interval.low),
            float(result.confidence_interval.high),
        )


def load_transcripts(path: Path) -> dict[str, dict[str, Any]]:
    """Load transcript JSON file, returning dict keyed by clip_id."""
    with path.open(encoding="utf-8") as fh:
        records: list[dict[str, Any]] = json.load(fh)
    return {r["clip_id"]: r for r in records}


def compute_per_clip_entity_accuracy(
    *,
    clip: GoldClip,
    hypothesis: str,
    is_anomaly: bool,
) -> float | None:
    """Compute entity accuracy for a single clip (all-or-nothing, Caubrière 2020).

    Returns None for anomaly clips (excluded from aggregate via np.nanmean).
    Returns 0.0 for clips with no entity spans (neutral contribution).
    """
    if is_anomaly:
        return None

    entity_spans = clip.entity_spans
    if len(entity_spans) == 0:
        return 0.0

    hyp_normalised = normalise(hypothesis)
    correct = 0
    total = len(entity_spans)

    for span in entity_spans:
        span_text: str = span["text"]
        span_normalised = normalise(span_text)
        if span_normalised in hyp_normalised:
            correct += 1

    return correct / total


def compute_wer_batch(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute full-transcript WER over all clips (batch jiwer call).

    Returns (aggregate_wer, per_clip_wer_list).
    """
    references: list[str] = []
    hypotheses: list[str] = []

    for clip in clips:
        ref = normalise(clip.reference_text)
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = normalise(str(hyp_raw))
        references.append(ref)
        hypotheses.append(hyp)

    result = jiwer.process_words(references, hypotheses)

    total_ref_words = result.hits + result.substitutions + result.deletions
    total_errors = result.substitutions + result.deletions + result.insertions
    aggregate_wer = total_errors / total_ref_words if total_ref_words > 0 else 0.0

    per_clip_wer: list[float] = []
    for ref, hyp in zip(references, hypotheses, strict=True):
        clip_result = jiwer.process_words([ref], [hyp])
        ref_words = clip_result.hits + clip_result.substitutions + clip_result.deletions
        errors = clip_result.substitutions + clip_result.deletions + clip_result.insertions
        per_clip_wer.append(errors / ref_words if ref_words > 0 else 0.0)

    return aggregate_wer, per_clip_wer


def compute_action_critical_wer(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute action-critical WER restricted to entity-span reference words."""
    total_hits = total_subs = total_dels = 0
    per_clip: list[float] = []

    for clip in clips:
        entity_spans = clip.entity_spans
        if len(entity_spans) == 0:
            per_clip.append(0.0)
            continue

        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp_words = set(normalise(str(hyp_raw)).split())

        clip_hits = clip_subs = clip_dels = 0

        for span in entity_spans:
            span_text: str = span["text"]
            span_words = normalise(span_text).split()
            for word in span_words:
                if word in hyp_words:
                    clip_hits += 1
                else:
                    clip_dels += 1

        n = clip_hits + clip_dels + clip_subs
        clip_wer = (clip_dels + clip_subs) / n if n > 0 else 0.0
        per_clip.append(clip_wer)

        total_hits += clip_hits
        total_subs += clip_subs
        total_dels += clip_dels

    total_n = total_hits + total_subs + total_dels
    aggregate = (total_subs + total_dels) / total_n if total_n > 0 else 0.0
    return aggregate, per_clip


def compute_intent_preservation(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute intent preservation using rule-based proxy."""
    per_clip: list[float] = []

    for clip in clips:
        entity_spans = clip.entity_spans
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = normalise(str(hyp_raw))

        if len(entity_spans) == 0:
            per_clip.append(1.0)
            continue

        matched_any = False
        for span in entity_spans:
            span_text: str = span["text"]
            if normalise(span_text) in hyp:
                matched_any = True
                break

        per_clip.append(1.0 if matched_any else 0.0)

    aggregate = float(np.mean(per_clip)) if len(per_clip) > 0 else 0.0
    return aggregate, per_clip


def compute_latency_p50(transcripts: dict[str, dict[str, Any]]) -> float:
    """Compute p50 latency from transcript records."""
    latencies = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    return float(np.percentile(latencies, 50)) if len(latencies) > 0 else 0.0


@dataclass(frozen=True, slots=True)
class SystemMetrics:
    """All computed metrics for one STT system."""

    variant_id: str
    label: str
    model_dim: str
    entity_accuracy: float
    entity_accuracy_ci: tuple[float, float]
    entity_per_clip: list[float | None]
    wer: float
    wer_ci: tuple[float, float]
    wer_per_clip: list[float]
    action_critical_wer: float
    action_critical_wer_ci: tuple[float, float]
    action_critical_per_clip: list[float]
    intent_preservation: float
    intent_preservation_ci: tuple[float, float]
    intent_per_clip: list[float]
    latency_p50: float


def compute_system_metrics(
    *,
    variant_id: str,
    label: str,
    model_dim: str,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    anomaly_clips: set[str],
) -> SystemMetrics:
    """Compute all metrics for a single STT system."""
    print(f"Computing metrics for {label}...")

    entity_scores_raw: list[float | None] = []
    for clip in clips:
        is_anomaly = clip.clip_id in anomaly_clips
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        score = compute_per_clip_entity_accuracy(
            clip=clip,
            hypothesis=str(hyp_raw),
            is_anomaly=is_anomaly,
        )
        entity_scores_raw.append(score)

    entity_scores_np = np.array(
        [np.nan if s is None else s for s in entity_scores_raw], dtype=float
    )
    entity_accuracy = float(np.nanmean(entity_scores_np))

    valid_entity = entity_scores_np[~np.isnan(entity_scores_np)]
    entity_ci = bca_ci(valid_entity)

    aggregate_wer, wer_per_clip = compute_wer_batch(clips=clips, transcripts=transcripts)
    wer_arr = np.array(wer_per_clip, dtype=float)
    wer_ci = bca_ci(wer_arr)

    acwer, acwer_per_clip = compute_action_critical_wer(clips=clips, transcripts=transcripts)
    acwer_arr = np.array(acwer_per_clip, dtype=float)
    acwer_ci = bca_ci(acwer_arr)

    intent, intent_per_clip = compute_intent_preservation(clips=clips, transcripts=transcripts)
    intent_arr = np.array(intent_per_clip, dtype=float)
    intent_ci = bca_ci(intent_arr)

    latency_p50 = compute_latency_p50(transcripts=transcripts)

    print(f"  entity_accuracy: {entity_accuracy:.4f} ({entity_ci[0]:.4f}-{entity_ci[1]:.4f})")
    print(f"  wer: {aggregate_wer:.4f} ({wer_ci[0]:.4f}-{wer_ci[1]:.4f})")
    print(f"  action_critical_wer: {acwer:.4f} ({acwer_ci[0]:.4f}-{acwer_ci[1]:.4f})")
    print(f"  intent_preservation: {intent:.4f} ({intent_ci[0]:.4f}-{intent_ci[1]:.4f})")
    print(f"  latency_p50: {latency_p50:.3f}s")

    return SystemMetrics(
        variant_id=variant_id,
        label=label,
        model_dim=model_dim,
        entity_accuracy=entity_accuracy,
        entity_accuracy_ci=entity_ci,
        entity_per_clip=entity_scores_raw,
        wer=aggregate_wer,
        wer_ci=wer_ci,
        wer_per_clip=wer_per_clip,
        action_critical_wer=acwer,
        action_critical_wer_ci=acwer_ci,
        action_critical_per_clip=acwer_per_clip,
        intent_preservation=intent,
        intent_preservation_ci=intent_ci,
        intent_per_clip=intent_per_clip,
        latency_p50=latency_p50,
    )


def main() -> None:
    """Compute Whisper turbo metrics and merge into metrics.json."""
    if not WHISPER_TURBO_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Whisper turbo transcripts not found at {WHISPER_TURBO_TRANSCRIPTS}. "
            "Run code/run_whisper_turbo.py first."
        )

    clips = load_gold92()
    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    transcripts = load_transcripts(WHISPER_TURBO_TRANSCRIPTS)

    sys_metrics = compute_system_metrics(
        variant_id="whisper-turbo",
        label="Whisper turbo",
        model_dim="whisper-turbo",
        clips=clips,
        transcripts=transcripts,
        anomaly_clips=anomaly_clips,
    )

    # Rejection criteria checks
    if sys_metrics.entity_accuracy == 0.0:
        print(
            "WARNING: entity_accuracy=0.0 for Whisper turbo. "
            "Check entity span annotations and normalisation."
        )
    if sys_metrics.wer > 0.6:
        raise RuntimeError(
            f"Rejection criterion triggered: Whisper turbo WER={sys_metrics.wer:.3f} > 0.6. "
            "Transcription pipeline likely failed — check audio files and reference."
        )

    # Load existing metrics.json if present (to merge)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    existing_variants: list[dict[str, Any]] = []
    if METRICS_JSON.exists():
        with METRICS_JSON.open(encoding="utf-8") as fh:
            existing: dict[str, Any] = json.load(fh)
        existing_variants = existing.get("variants", [])
        # Remove any stale whisper-turbo variant to avoid duplicates
        existing_variants = [v for v in existing_variants if v.get("variant_id") != "whisper-turbo"]

    turbo_variant: dict[str, Any] = {
        "variant_id": sys_metrics.variant_id,
        "label": sys_metrics.label,
        "dimensions": {"model": sys_metrics.model_dim},
        "metrics": {
            "entity_accuracy_gold92": round(sys_metrics.entity_accuracy, 6),
            "wer_gold92": round(sys_metrics.wer, 6),
            "action_critical_wer_gold92": round(sys_metrics.action_critical_wer, 6),
            "intent_preservation_gold92": round(sys_metrics.intent_preservation, 6),
            "latency_p50_seconds": round(sys_metrics.latency_p50, 4),
        },
    }

    merged_variants = existing_variants + [turbo_variant]
    metrics_json: dict[str, Any] = {"variants": merged_variants}

    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    # Update analysis_output.json if it exists — append turbo to summary_table
    if ANALYSIS_OUTPUT.exists():
        with ANALYSIS_OUTPUT.open(encoding="utf-8") as fh:
            analysis: dict[str, Any] = json.load(fh)

        # Remove any stale turbo row from summary_table
        summary_table: list[dict[str, Any]] = analysis.get("summary_table", [])
        summary_table = [r for r in summary_table if r.get("variant_id") != "whisper-turbo"]

        ea_ci_half = (sys_metrics.entity_accuracy_ci[1] - sys_metrics.entity_accuracy_ci[0]) / 2
        wer_ci_half = (sys_metrics.wer_ci[1] - sys_metrics.wer_ci[0]) / 2
        acwer_ci_half = (
            sys_metrics.action_critical_wer_ci[1] - sys_metrics.action_critical_wer_ci[0]
        ) / 2
        intent_ci_half = (
            sys_metrics.intent_preservation_ci[1] - sys_metrics.intent_preservation_ci[0]
        ) / 2

        summary_table.append(
            {
                "system": sys_metrics.label,
                "variant_id": sys_metrics.variant_id,
                "entity_accuracy_gold92": sys_metrics.entity_accuracy,
                "entity_accuracy_ci_low": sys_metrics.entity_accuracy_ci[0],
                "entity_accuracy_ci_high": sys_metrics.entity_accuracy_ci[1],
                "entity_accuracy_ci_half": ea_ci_half,
                "wer_gold92": sys_metrics.wer,
                "wer_ci_low": sys_metrics.wer_ci[0],
                "wer_ci_high": sys_metrics.wer_ci[1],
                "wer_ci_half": wer_ci_half,
                "action_critical_wer_gold92": sys_metrics.action_critical_wer,
                "action_critical_wer_ci_low": sys_metrics.action_critical_wer_ci[0],
                "action_critical_wer_ci_high": sys_metrics.action_critical_wer_ci[1],
                "action_critical_wer_ci_half": acwer_ci_half,
                "intent_preservation_gold92": sys_metrics.intent_preservation,
                "intent_preservation_ci_low": sys_metrics.intent_preservation_ci[0],
                "intent_preservation_ci_high": sys_metrics.intent_preservation_ci[1],
                "intent_preservation_ci_half": intent_ci_half,
                "latency_p50_seconds": sys_metrics.latency_p50,
            }
        )
        analysis["summary_table"] = summary_table

        with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
            json.dump(analysis, fh, indent=2, ensure_ascii=False)
        print(f"Updated {ANALYSIS_OUTPUT}")

    print("\nDone.")


if __name__ == "__main__":
    main()
