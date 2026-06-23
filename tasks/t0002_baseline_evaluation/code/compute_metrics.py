"""Compute all five registered project metrics for both STT systems.

Reads transcripts from data/ and ground truth from t0001 dataset.
Writes results/metrics.json (explicit variant format) and
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

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import (
    ANALYSIS_OUTPUT,
    DEEPGRAM_TRANSCRIPTS,
    METRICS_JSON,
    RESULTS_DIR,
    WHISPER_TRANSCRIPTS,
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
    per_clip_wer: list[float] = []

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
    """Compute action-critical WER restricted to entity-span reference words.

    For each clip, build a reference string from entity-span words only and a
    hypothesis string from entity-span words only (those that appear in the
    hypothesis). This computes WER at the entity-token level rather than
    computing WER of entity tokens vs. full hypothesis text.

    Approach: for each entity span, check if any individual word from the span
    appears in the hypothesis (word-level match after normalisation). Count
    hits, substitutions (words in span not found in hyp), and deletions.

    Returns (aggregate_action_critical_wer, per_clip_list).
    """
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
                    clip_dels += 1  # reference word missing from hypothesis

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

    This is a heuristic approximation — documented limitation in metadata.
    """
    per_clip: list[float] = []

    for clip in clips:
        entity_spans = clip.entity_spans
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = normalise(str(hyp_raw))

        if len(entity_spans) == 0:
            # No entities to match — consider intent preserved (neutral)
            per_clip.append(1.0)
            continue

        # Check if any entity span appears in hypothesis
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


def compute_paired_significance(
    *,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    label_a: str = "system A",
    label_b: str = "system B",
) -> dict[str, Any]:
    """Paired BCa bootstrap significance test (one-sided: P(B >= A)).

    Computes: diff = scores_b - scores_a
    p_value = P(mean(diff) <= 0) = fraction of bootstrap means <= 0
    """
    diff = scores_b - scores_a
    result = bootstrap(
        (diff,),
        statistic=np.mean,
        method="BCa",
        n_resamples=BCa_N_RESAMPLES,
        paired=True,
        random_state=BCa_RANDOM_STATE,
    )
    # p-value: one-sided, P(B >= A) meaning fraction of bootstrap means where
    # the difference (B - A) is <= 0 (null: B is no better than A)
    boot_means = np.mean(
        diff[
            np.random.default_rng(BCa_RANDOM_STATE).integers(
                0, len(diff), size=(BCa_N_RESAMPLES, len(diff))
            )
        ],
        axis=1,
    )
    p_value = float(np.mean(boot_means <= 0))

    mean_diff = float(np.mean(diff))
    ci_low = float(result.confidence_interval.low)
    ci_high = float(result.confidence_interval.high)

    significant = p_value < 0.05
    interpretation = f"p={p_value:.4f} — " + (
        f"{label_b} significantly outperforms {label_a} on entity accuracy "
        f"at alpha=0.05 (mean diff={mean_diff:+.4f})"
        if significant
        else f"No significant difference between {label_b} and {label_a} "
        f"at alpha=0.05 (mean diff={mean_diff:+.4f})"
    )

    return {
        "p_value": p_value,
        "mean_difference": mean_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "method": "BCa bootstrap, one-sided, paired",
        "n_resamples": BCa_N_RESAMPLES,
        "seed": BCa_RANDOM_STATE,
        "significant_at_0_05": significant,
        "interpretation": interpretation,
        "note": (
            "p_value = fraction of bootstrap resamples where mean(B-A) <= 0. "
            "H0: B is no better than A."
        ),
    }


def build_accent_breakdown(
    *,
    clips: list[GoldClip],
    systems: list[SystemMetrics],
) -> list[dict[str, Any]]:
    """Build per-accent-group breakdown table."""
    accent_groups = sorted({c.accent_group for c in clips})
    rows: list[dict[str, Any]] = []

    clip_to_idx = {c.clip_id: i for i, c in enumerate(clips)}

    for group in accent_groups:
        group_clips = [c for c in clips if c.accent_group == group]
        group_indices = [clip_to_idx[c.clip_id] for c in group_clips]

        row: dict[str, Any] = {
            "accent_group": group,
            "n_clips": len(group_clips),
        }

        for sys in systems:
            scores_raw = [sys.entity_per_clip[i] for i in group_indices]
            scores_valid = [s for s in scores_raw if s is not None]
            mean_score = float(np.mean(scores_valid)) if len(scores_valid) > 0 else None
            row[f"entity_accuracy_{sys.variant_id}"] = mean_score

        rows.append(row)

    return rows


def build_summary_table(
    *,
    clips: list[GoldClip],
    systems: list[SystemMetrics],
) -> list[dict[str, Any]]:
    """Build summary metrics table."""
    rows: list[dict[str, Any]] = []
    for sys in systems:
        ea_ci_half = (sys.entity_accuracy_ci[1] - sys.entity_accuracy_ci[0]) / 2
        wer_ci_half = (sys.wer_ci[1] - sys.wer_ci[0]) / 2
        acwer_ci_half = (sys.action_critical_wer_ci[1] - sys.action_critical_wer_ci[0]) / 2
        intent_ci_half = (sys.intent_preservation_ci[1] - sys.intent_preservation_ci[0]) / 2
        rows.append(
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
                "action_critical_wer_ci_low": sys.action_critical_wer_ci[0],
                "action_critical_wer_ci_high": sys.action_critical_wer_ci[1],
                "action_critical_wer_ci_half": acwer_ci_half,
                "intent_preservation_gold92": sys.intent_preservation,
                "intent_preservation_ci_low": sys.intent_preservation_ci[0],
                "intent_preservation_ci_high": sys.intent_preservation_ci[1],
                "intent_preservation_ci_half": intent_ci_half,
                "latency_p50_seconds": sys.latency_p50,
            }
        )
    return rows


def build_contrastive_examples(
    *,
    clips: list[GoldClip],
    systems: list[SystemMetrics],
    transcripts_map: dict[str, dict[str, Any]],
    n_examples: int = 15,
) -> list[dict[str, Any]]:
    """Build contrastive examples for the results document."""
    primary = systems[0]

    examples: list[dict[str, Any]] = []
    clip_to_idx = {c.clip_id: i for i, c in enumerate(clips)}

    def make_example(clip: GoldClip, category: str) -> dict[str, Any]:
        idx = clip_to_idx[clip.clip_id]
        example: dict[str, Any] = {
            "clip_id": clip.clip_id,
            "reference": clip.reference_text,
            "category": category,
            "accent_group": clip.accent_group,
        }
        for sys in systems:
            hyp = str(transcripts_map[sys.variant_id].get(clip.clip_id, {}).get("hypothesis", ""))
            ea = sys.entity_per_clip[idx]
            example[f"hypothesis_{sys.variant_id}"] = hyp
            example[f"entity_accuracy_{sys.variant_id}"] = ea
        return example

    entity_scores_0 = [s if s is not None else 0.0 for s in primary.entity_per_clip]

    # Best cases for primary system (top 3)
    sorted_by_ea_desc = sorted(range(len(clips)), key=lambda i: entity_scores_0[i], reverse=True)
    for i in sorted_by_ea_desc[:3]:
        examples.append(make_example(clips[i], "best_case"))

    # Worst cases (bottom 3, excluding anomaly)
    sorted_by_ea_asc = sorted(range(len(clips)), key=lambda i: entity_scores_0[i])
    added_worst = 0
    for i in sorted_by_ea_asc:
        if clips[i].clip_id not in {CYRILLIC_ANOMALY_CLIP}:
            examples.append(make_example(clips[i], "worst_case"))
            added_worst += 1
            if added_worst >= 3:
                break

    # Boundary cases (entity accuracy near 0.5)
    sorted_by_boundary = sorted(range(len(clips)), key=lambda i: abs(entity_scores_0[i] - 0.5))
    for i in sorted_by_boundary[:3]:
        examples.append(make_example(clips[i], "boundary"))

    # Random sample
    rng = np.random.default_rng(42)
    random_indices = rng.choice(len(clips), size=min(6, len(clips)), replace=False)
    for i in random_indices:
        if len(examples) < n_examples:
            examples.append(make_example(clips[int(i)], "random"))

    return examples[:n_examples]


def main() -> None:
    """Main entry point: compute all metrics and write output files."""
    clips = load_gold92()
    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    # Determine which systems to compute (Deepgram only if transcripts exist)
    systems_to_run: list[tuple[str, str, str, Path]] = []

    if DEEPGRAM_TRANSCRIPTS.exists():
        systems_to_run.append(
            ("deepgram-nova2", "Deepgram Nova-2", "deepgram-nova-2", DEEPGRAM_TRANSCRIPTS)
        )
    else:
        print(
            "WARNING: data/deepgram_transcripts.json not found — "
            "skipping Deepgram metrics. Set DEEPGRAM_API_KEY and run "
            "run_deepgram.py to generate this file."
        )

    systems_to_run.append(
        ("whisper-large-v3", "Whisper Large v3", "whisper-large-v3", WHISPER_TRANSCRIPTS)
    )

    if not WHISPER_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Whisper transcripts not found at {WHISPER_TRANSCRIPTS}. "
            "Run code/run_whisper.py first."
        )

    # Load all transcripts
    transcripts_by_system: dict[str, dict[str, dict[str, Any]]] = {}
    for variant_id, _label, _dim, path in systems_to_run:
        transcripts_by_system[variant_id] = load_transcripts(path=path)

    # Compute metrics for each system
    computed_systems: list[SystemMetrics] = []
    for variant_id, label, model_dim, _ in systems_to_run:
        sys_metrics = compute_system_metrics(
            variant_id=variant_id,
            label=label,
            model_dim=model_dim,
            clips=clips,
            transcripts=transcripts_by_system[variant_id],
            anomaly_clips=anomaly_clips,
        )
        computed_systems.append(sys_metrics)

    # Rejection criteria checks
    for sys in computed_systems:
        if sys.entity_accuracy == 0.0:
            print(
                f"WARNING: entity_accuracy=0.0 for {sys.label}. "
                "Check entity span annotations and normalisation."
            )
        if sys.wer > 0.6:
            raise RuntimeError(
                f"Rejection criterion triggered: {sys.label} WER={sys.wer:.3f} > 0.6. "
                "Transcription pipeline likely failed — check audio files and reference."
            )

    # Paired significance test (only if both systems computed)
    significance_result: dict[str, Any] | None = None
    if len(computed_systems) >= 2:
        dg_sys = next((s for s in computed_systems if s.variant_id == "deepgram-nova2"), None)
        wh_sys = next((s for s in computed_systems if s.variant_id == "whisper-large-v3"), None)
        if dg_sys is not None and wh_sys is not None:
            dg_entity = np.array(
                [np.nan if s is None else s for s in dg_sys.entity_per_clip], dtype=float
            )
            wh_entity = np.array(
                [np.nan if s is None else s for s in wh_sys.entity_per_clip], dtype=float
            )
            # Use only non-NaN pairs
            valid_mask = ~np.isnan(dg_entity) & ~np.isnan(wh_entity)
            significance_result = compute_paired_significance(
                scores_a=dg_entity[valid_mask],
                scores_b=wh_entity[valid_mask],
                label_a="Deepgram Nova-2",
                label_b="Whisper Large v3",
            )
            print(f"\nSignificance test: {significance_result['interpretation']}")
    else:
        significance_result = {
            "p_value": None,
            "method": "BCa bootstrap, paired",
            "n_resamples": BCa_N_RESAMPLES,
            "seed": BCa_RANDOM_STATE,
            "interpretation": (
                "Significance test not run: Deepgram transcripts unavailable. "
                "Set DEEPGRAM_API_KEY and re-run."
            ),
            "note": "REQ-5 partially blocked pending Deepgram API key.",
        }

    # Write results/metrics.json (explicit variant format)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    variants: list[dict[str, Any]] = []
    for sys in computed_systems:
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
                },
            }
        )

    # Note: only 'variants' is allowed at top level in explicit variant format (TM-E003)
    # Omission rationale for wrong_action_rate_gold92 and Deepgram status go in
    # data/analysis_output.json, not in metrics.json.
    metrics_json: dict[str, Any] = {"variants": variants}

    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    # Build analysis output
    anomaly_clips_list: list[dict[str, Any]] = [
        {
            "clip_id": CYRILLIC_ANOMALY_CLIP,
            "anomaly_type": "cyrillic_ground_truth_in_gold_set",
            "note": (
                "gold_set.jsonl has Cyrillic 'ы' as ground_truth for this clip; "
                "canonical ground_truth.jsonl has normal English. "
                "Clip included in WER computation but excluded from entity accuracy aggregate."
            ),
        }
    ]

    summary_table = build_summary_table(clips=clips, systems=computed_systems)

    transcripts_map_for_examples: dict[str, dict[str, Any]] = {
        variant_id: transcripts_by_system[variant_id]
        for variant_id, _label, _dim, _path in systems_to_run
    }
    contrastive_examples = build_contrastive_examples(
        clips=clips,
        systems=computed_systems,
        transcripts_map=transcripts_map_for_examples,
    )

    accent_breakdown = build_accent_breakdown(
        clips=clips,
        systems=computed_systems,
    )

    analysis_output: dict[str, Any] = {
        "summary_table": summary_table,
        "accent_breakdown": accent_breakdown,
        "significance_test": significance_result,
        "anomaly_clips": anomaly_clips_list,
        "contrastive_examples": contrastive_examples,
        "intent_preservation_method": (
            "Rule-based proxy: intent preserved if at least one entity span from the reference "
            "appears in the normalised hypothesis. Limitation: does not model action type or "
            "slot agreement — only entity presence. A downstream task should implement proper "
            "intent classification."
        ),
        "omitted_metrics": {
            "wrong_action_rate_gold92": (
                "Requires a confidence-routing policy (threshold, routing logic). "
                "Not in scope for this baseline task."
            )
        },
        "bootstrap_config": {
            "method": "BCa",
            "n_resamples": BCa_N_RESAMPLES,
            "random_state": BCa_RANDOM_STATE,
            "note": (
                "Standard i.i.d. BCa used. For the clean_voices subset (~40 clips, 6 named "
                "speakers), blockwise bootstrap by speaker would be more accurate per Liu & "
                "Peng 2020. Standard BCa is acceptable for the full 93-clip primary result."
            ),
        },
    }

    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(analysis_output, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")
    print("\nDone.")


if __name__ == "__main__":
    main()
