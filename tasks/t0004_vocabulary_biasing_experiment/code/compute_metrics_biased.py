"""Compute all metrics for biased Whisper variants and write results.

Reads biased transcripts from data/ and ground truth from t0001 dataset.
Reuses t0002 baseline numbers directly from tasks/t0002_baseline_evaluation/results/metrics.json.
Writes results/metrics.json (explicit variant format, 4 variants) and
data/analysis_output.json.
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

from tasks.t0004_vocabulary_biasing_experiment.code.constants import DOMAIN_VOCAB
from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
    load_gold92,
)
from tasks.t0004_vocabulary_biasing_experiment.code.paths import (
    ANALYSIS_OUTPUT,
    METRICS_JSON,
    MOONSHINE_TRANSCRIPTS,
    RESULTS_DIR,
    T0002_WHISPER_TRANSCRIPTS,
    T0002_WHISPER_TURBO_TRANSCRIPTS,
    WHISPER_BIASED_TRANSCRIPTS,
    WHISPER_TURBO_BIASED_TRANSCRIPTS,
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
    """Compute entity accuracy for a single clip (all-or-nothing, Caubriere 2020).

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
        # All-or-nothing: exact span must appear in normalised hypothesis
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

    # Per-clip WER via individual processing
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
    """Compute intent preservation using rule-based proxy.

    An utterance preserves intent if at least one entity span from the reference
    appears in the hypothesis (set intersection non-empty).
    """
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


def compute_entity_accuracy_domain_vocab(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    domain_vocab: list[str],
) -> tuple[float, list[float | None]]:
    """Compute entity accuracy restricted to domain vocabulary terms.

    For each clip that contains at least one domain vocabulary term in its reference:
    - Check which domain terms from its reference appear correctly in the hypothesis
    - entity_accuracy_domain_vocab = (correct matches) / (total domain term occurrences in refs)

    Returns (aggregate, per_clip_scores) where per_clip_scores is None for clips
    that have no domain vocab terms in their reference.
    """
    domain_vocab_normalised = [normalise(term) for term in domain_vocab]

    per_clip: list[float | None] = []
    total_correct = 0
    total_occurrences = 0

    for clip in clips:
        ref_normalised = normalise(clip.reference_text)
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp_normalised = normalise(str(hyp_raw))

        # Find which domain terms appear in this clip's reference
        clip_domain_terms_in_ref = [
            term for term in domain_vocab_normalised if term in ref_normalised
        ]

        if len(clip_domain_terms_in_ref) == 0:
            per_clip.append(None)  # Clip has no domain vocab terms — exclude from aggregate
            continue

        # Check which appear in hypothesis
        clip_correct = sum(1 for term in clip_domain_terms_in_ref if term in hyp_normalised)
        clip_total = len(clip_domain_terms_in_ref)

        per_clip.append(clip_correct / clip_total if clip_total > 0 else 0.0)
        total_correct += clip_correct
        total_occurrences += clip_total

    aggregate = total_correct / total_occurrences if total_occurrences > 0 else 0.0
    return aggregate, per_clip


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
    entity_accuracy_domain_vocab: float
    entity_accuracy_domain_vocab_ci: tuple[float, float]
    domain_vocab_per_clip: list[float | None]


def compute_system_metrics(
    *,
    variant_id: str,
    label: str,
    model_dim: str,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    anomaly_clips: set[str],
    domain_vocab: list[str],
) -> SystemMetrics:
    """Compute all metrics for a single STT system."""
    print(f"Computing metrics for {label}...")

    # Entity accuracy (per clip, with NaN for anomaly clips)
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

    # Replace None with NaN for numpy
    entity_scores_np = np.array(
        [np.nan if s is None else s for s in entity_scores_raw], dtype=float
    )
    entity_accuracy = float(np.nanmean(entity_scores_np))

    # BCa CI uses only non-NaN scores
    valid_entity = entity_scores_np[~np.isnan(entity_scores_np)]
    entity_ci = bca_ci(valid_entity)

    # WER
    aggregate_wer, wer_per_clip = compute_wer_batch(clips=clips, transcripts=transcripts)
    wer_arr = np.array(wer_per_clip, dtype=float)
    wer_ci = bca_ci(wer_arr)

    # Action-critical WER
    acwer, acwer_per_clip = compute_action_critical_wer(clips=clips, transcripts=transcripts)
    acwer_arr = np.array(acwer_per_clip, dtype=float)
    acwer_ci = bca_ci(acwer_arr)

    # Intent preservation
    intent, intent_per_clip = compute_intent_preservation(clips=clips, transcripts=transcripts)
    intent_arr = np.array(intent_per_clip, dtype=float)
    intent_ci = bca_ci(intent_arr)

    # Latency p50
    latency_p50 = compute_latency_p50(transcripts=transcripts)

    # Domain vocab entity accuracy
    domain_vocab_acc, domain_vocab_per_clip = compute_entity_accuracy_domain_vocab(
        clips=clips,
        transcripts=transcripts,
        domain_vocab=domain_vocab,
    )
    domain_vocab_np = np.array(
        [np.nan if s is None else s for s in domain_vocab_per_clip], dtype=float
    )
    valid_domain = domain_vocab_np[~np.isnan(domain_vocab_np)]
    domain_vocab_ci = bca_ci(valid_domain) if len(valid_domain) > 1 else (0.0, 0.0)

    print(f"  entity_accuracy: {entity_accuracy:.4f} ({entity_ci[0]:.4f}-{entity_ci[1]:.4f})")
    print(f"  wer: {aggregate_wer:.4f} ({wer_ci[0]:.4f}-{wer_ci[1]:.4f})")
    print(f"  action_critical_wer: {acwer:.4f} ({acwer_ci[0]:.4f}-{acwer_ci[1]:.4f})")
    print(f"  intent_preservation: {intent:.4f} ({intent_ci[0]:.4f}-{intent_ci[1]:.4f})")
    print(f"  latency_p50: {latency_p50:.3f}s")
    print(
        f"  entity_accuracy_domain_vocab: {domain_vocab_acc:.4f} "
        f"({domain_vocab_ci[0]:.4f}-{domain_vocab_ci[1]:.4f})"
    )

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
        entity_accuracy_domain_vocab=domain_vocab_acc,
        entity_accuracy_domain_vocab_ci=domain_vocab_ci,
        domain_vocab_per_clip=domain_vocab_per_clip,
    )


def build_production_entity_accuracy(
    *,
    clips: list[GoldClip],
    systems: list[SystemMetrics],
) -> dict[str, Any]:
    """Compute entity accuracy for production clips only.

    Production clips have accent_group == 'production' in gold_set.jsonl.
    This is a derived metric not written to metrics.json — only to analysis_output.json.
    """
    production_clips = [c for c in clips if c.accent_group == "production"]
    clip_to_idx = {c.clip_id: i for i, c in enumerate(clips)}

    result: dict[str, Any] = {
        "n_clips": len(production_clips),
        "clip_ids": [c.clip_id for c in production_clips],
    }

    for sys in systems:
        scores = [sys.entity_per_clip[clip_to_idx[c.clip_id]] for c in production_clips]
        valid = [s for s in scores if s is not None]
        mean = float(np.mean(valid)) if valid else None
        result[f"entity_accuracy_production_{sys.variant_id}"] = mean

    return result


def compute_per_term_accuracy(
    *,
    clips: list[GoldClip],
    transcripts_by_variant: dict[str, dict[str, dict[str, Any]]],
    domain_vocab: list[str],
    variant_ids: list[str],
) -> list[dict[str, Any]]:
    """Compute per-term domain vocabulary accuracy for each variant."""
    domain_vocab_normalised = [normalise(term) for term in domain_vocab]
    rows: list[dict[str, Any]] = []

    for term, term_norm in zip(domain_vocab, domain_vocab_normalised, strict=True):
        clips_with_term = [c for c in clips if term_norm in normalise(c.reference_text)]
        row: dict[str, Any] = {
            "term": term,
            "n_clips_in_ref": len(clips_with_term),
        }
        for variant_id in variant_ids:
            transcripts = transcripts_by_variant[variant_id]
            correct = 0
            for clip in clips_with_term:
                hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
                if term_norm in normalise(str(hyp_raw)):
                    correct += 1
            total = len(clips_with_term)
            row[f"correct_{variant_id}"] = correct
            row[f"accuracy_{variant_id}"] = round(correct / total, 4) if total > 0 else None
        rows.append(row)

    return rows


def main() -> None:
    """Main entry point: compute all metrics and write output files."""
    clips = load_gold92()
    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    # Check required transcript files
    if not WHISPER_BIASED_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Biased transcripts not found at {WHISPER_BIASED_TRANSCRIPTS}. "
            "Run code/run_whisper_biased.py first."
        )
    if not WHISPER_TURBO_BIASED_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Turbo biased transcripts not found at {WHISPER_TURBO_BIASED_TRANSCRIPTS}. "
            "Run code/run_whisper_turbo_biased.py first."
        )
    if not T0002_WHISPER_TRANSCRIPTS.exists():
        raise RuntimeError(f"t0002 Whisper transcripts not found at {T0002_WHISPER_TRANSCRIPTS}.")
    if not T0002_WHISPER_TURBO_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"t0002 Whisper turbo transcripts not found at {T0002_WHISPER_TURBO_TRANSCRIPTS}."
        )
    if not MOONSHINE_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Moonshine transcripts not found at {MOONSHINE_TRANSCRIPTS}. "
            "Run code/run_moonshine_small.py first."
        )

    # Load all transcripts
    whisper_biased_transcripts = load_transcripts(WHISPER_BIASED_TRANSCRIPTS)
    turbo_biased_transcripts = load_transcripts(WHISPER_TURBO_BIASED_TRANSCRIPTS)
    whisper_baseline_transcripts = load_transcripts(T0002_WHISPER_TRANSCRIPTS)
    turbo_baseline_transcripts = load_transcripts(T0002_WHISPER_TURBO_TRANSCRIPTS)
    moonshine_transcripts = load_transcripts(MOONSHINE_TRANSCRIPTS)

    # Compute metrics for each system
    systems: list[SystemMetrics] = []

    systems.append(
        compute_system_metrics(
            variant_id="whisper-large-v3",
            label="Whisper Large v3 (baseline)",
            model_dim="whisper-large-v3",
            clips=clips,
            transcripts=whisper_baseline_transcripts,
            anomaly_clips=anomaly_clips,
            domain_vocab=DOMAIN_VOCAB,
        )
    )

    systems.append(
        compute_system_metrics(
            variant_id="whisper-large-v3-biased",
            label="Whisper Large v3 + vocab bias",
            model_dim="whisper-large-v3",
            clips=clips,
            transcripts=whisper_biased_transcripts,
            anomaly_clips=anomaly_clips,
            domain_vocab=DOMAIN_VOCAB,
        )
    )

    systems.append(
        compute_system_metrics(
            variant_id="whisper-turbo",
            label="Whisper turbo (baseline)",
            model_dim="whisper-turbo",
            clips=clips,
            transcripts=turbo_baseline_transcripts,
            anomaly_clips=anomaly_clips,
            domain_vocab=DOMAIN_VOCAB,
        )
    )

    systems.append(
        compute_system_metrics(
            variant_id="whisper-turbo-biased",
            label="Whisper turbo + vocab bias",
            model_dim="whisper-turbo",
            clips=clips,
            transcripts=turbo_biased_transcripts,
            anomaly_clips=anomaly_clips,
            domain_vocab=DOMAIN_VOCAB,
        )
    )

    systems.append(
        compute_system_metrics(
            variant_id="moonshine-base",
            label="Moonshine base (no biasing — model doesn't support initial_prompt)",
            model_dim="moonshine-base",
            clips=clips,
            transcripts=moonshine_transcripts,
            anomaly_clips=anomaly_clips,
            domain_vocab=DOMAIN_VOCAB,
        )
    )

    # Rejection criteria checks
    for sys in systems:
        if sys.wer > 0.6:
            raise RuntimeError(
                f"Rejection criterion triggered: {sys.label} WER={sys.wer:.3f} > 0.6. "
                "Transcription pipeline likely failed."
            )

    # Write results/metrics.json (explicit variant format, 4 variants)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    variants: list[dict[str, Any]] = []
    for sys in systems:
        variants.append(
            {
                "variant_id": sys.variant_id,
                "label": sys.label,
                "dimensions": {"model": sys.model_dim},
                "metrics": {
                    "entity_accuracy_gold92": round(sys.entity_accuracy, 6),
                    "wer_gold92": round(sys.wer, 6),
                    "action_critical_wer_gold92": round(sys.action_critical_wer, 6),
                    "intent_preservation_gold92": round(sys.intent_preservation, 6),
                    "latency_p50_seconds": round(sys.latency_p50, 4),
                    "entity_accuracy_domain_vocab": round(sys.entity_accuracy_domain_vocab, 6),
                },
            }
        )

    metrics_json: dict[str, Any] = {"variants": variants}

    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    # Build analysis output
    transcripts_by_variant: dict[str, dict[str, dict[str, Any]]] = {
        "whisper-large-v3": whisper_baseline_transcripts,
        "whisper-large-v3-biased": whisper_biased_transcripts,
        "whisper-turbo": turbo_baseline_transcripts,
        "whisper-turbo-biased": turbo_biased_transcripts,
        "moonshine-base": moonshine_transcripts,
    }
    variant_ids = [
        "whisper-large-v3",
        "whisper-large-v3-biased",
        "whisper-turbo",
        "whisper-turbo-biased",
        "moonshine-base",
    ]

    per_term_accuracy = compute_per_term_accuracy(
        clips=clips,
        transcripts_by_variant=transcripts_by_variant,
        domain_vocab=DOMAIN_VOCAB,
        variant_ids=variant_ids,
    )

    production_accuracy = build_production_entity_accuracy(clips=clips, systems=systems)

    # Summary table
    summary_table: list[dict[str, Any]] = []
    for sys in systems:
        ea_ci_half = (sys.entity_accuracy_ci[1] - sys.entity_accuracy_ci[0]) / 2
        wer_ci_half = (sys.wer_ci[1] - sys.wer_ci[0]) / 2
        dv_ci = sys.entity_accuracy_domain_vocab_ci
        dv_ci_half = (dv_ci[1] - dv_ci[0]) / 2
        summary_table.append(
            {
                "system": sys.label,
                "variant_id": sys.variant_id,
                "entity_accuracy_gold92": sys.entity_accuracy,
                "entity_accuracy_ci_low": sys.entity_accuracy_ci[0],
                "entity_accuracy_ci_high": sys.entity_accuracy_ci[1],
                "entity_accuracy_ci_half": ea_ci_half,
                "wer_gold92": sys.wer,
                "wer_ci_low": sys.wer_ci[0],
                "wer_ci_high": sys.wer_ci[1],
                "wer_ci_half": wer_ci_half,
                "action_critical_wer_gold92": sys.action_critical_wer,
                "intent_preservation_gold92": sys.intent_preservation,
                "latency_p50_seconds": sys.latency_p50,
                "entity_accuracy_domain_vocab": sys.entity_accuracy_domain_vocab,
                "entity_accuracy_domain_vocab_ci_low": dv_ci[0],
                "entity_accuracy_domain_vocab_ci_high": dv_ci[1],
                "entity_accuracy_domain_vocab_ci_half": dv_ci_half,
            }
        )

    # Per-clip analysis (biased variants only, for conciseness)
    per_clip_analysis: list[dict[str, Any]] = []
    for i, clip in enumerate(clips):
        row: dict[str, Any] = {
            "clip_id": clip.clip_id,
            "accent_group": clip.accent_group,
            "reference": clip.reference_text,
        }
        for sys in systems:
            row[f"hypothesis_{sys.variant_id}"] = str(
                transcripts_by_variant[sys.variant_id].get(clip.clip_id, {}).get("hypothesis", "")
            )
            row[f"entity_accuracy_{sys.variant_id}"] = sys.entity_per_clip[i]
            row[f"domain_vocab_accuracy_{sys.variant_id}"] = sys.domain_vocab_per_clip[i]
        per_clip_analysis.append(row)

    analysis_output: dict[str, Any] = {
        "summary_table": summary_table,
        "production_entity_accuracy": production_accuracy,
        "per_term_domain_vocab_accuracy": per_term_accuracy,
        "per_clip_analysis": per_clip_analysis,
        "bootstrap_config": {
            "method": "BCa",
            "n_resamples": BCa_N_RESAMPLES,
            "random_state": BCa_RANDOM_STATE,
        },
        "domain_vocab_note": (
            "entity_accuracy_domain_vocab is computed only over the 31 domain terms "
            "that appear in gold-92 ground truth. Per-clip score is None for clips "
            "with no domain terms in their reference."
        ),
        "anomaly_clips": [
            {
                "clip_id": CYRILLIC_ANOMALY_CLIP,
                "anomaly_type": "cyrillic_ground_truth_in_gold_set",
                "note": (
                    "Excluded from entity accuracy aggregate via np.nanmean. "
                    "Included in WER computation."
                ),
            }
        ],
    }

    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(analysis_output, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")
    print("\nDone.")

    # Print summary comparison
    print("\n=== SUMMARY ===")
    print(f"{'Variant':<35} {'EA':<8} {'EA_DV':<8} {'WER':<8} {'IP':<8} {'Lat_p50':<8}")
    print("-" * 80)
    for sys in systems:
        print(
            f"{sys.variant_id:<35} "
            f"{sys.entity_accuracy:.4f}  "
            f"{sys.entity_accuracy_domain_vocab:.4f}  "
            f"{sys.wer:.4f}  "
            f"{sys.intent_preservation:.4f}  "
            f"{sys.latency_p50:.2f}s"
        )


if __name__ == "__main__":
    main()
