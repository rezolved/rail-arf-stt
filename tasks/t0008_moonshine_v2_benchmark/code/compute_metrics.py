"""Compute all metrics for Moonshine v2 Medium on gold-92 benchmark.

Reads: data/moonshine_v2_medium_transcripts.json
Writes: results/metrics.json (flat format, 7 keys)
        data/analysis_output.json (full breakdown)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from tasks.t0008_moonshine_v2_benchmark.code.metrics_utils import (
    CYRILLIC_ANOMALY_CLIP,
    DOMAIN_VOCAB,
    BCa_N_RESAMPLES,
    BCa_RANDOM_STATE,
    GoldClip,
    bca_ci,
    compute_action_critical_wer,
    compute_entity_accuracy_domain_vocab,
    compute_intent_preservation,
    compute_latency_p50,
    compute_per_clip_entity_accuracy,
    compute_wer_batch,
    load_gold92,
)
from tasks.t0008_moonshine_v2_benchmark.code.paths import (
    ANALYSIS_OUTPUT,
    DATA_DIR,
    METRICS_JSON,
    MOONSHINE_V2_TRANSCRIPTS,
    RESULTS_DIR,
)


def load_transcripts(path: Path) -> dict[str, dict[str, Any]]:
    """Load transcript JSON file, returning dict keyed by clip_id."""
    with path.open(encoding="utf-8") as fh:
        records: list[dict[str, Any]] = json.load(fh)
    return {r["clip_id"]: r for r in records}


def compute_latency_by_stage(
    transcripts: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """Compute p50/p95/p99 latency per latency_stage."""
    by_stage: dict[str, list[float]] = {}
    for rec in transcripts.values():
        stage: str = rec.get("latency_stage", "warmed")
        lat = float(rec.get("latency_seconds", 0.0))
        by_stage.setdefault(stage, []).append(lat)

    result: dict[str, dict[str, float]] = {}
    for stage, lats in by_stage.items():
        arr = np.array(lats, dtype=float)
        result[stage] = {
            "p50": float(np.percentile(arr, 50)),
            "p95": float(np.percentile(arr, 95)),
            "p99": float(np.percentile(arr, 99)),
            "n": len(lats),
        }
    return result


def compute_subset_metrics(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    subset_name: str,
) -> dict[str, Any]:
    """Compute metrics for a subset of clips."""
    if not clips:
        return {"n_clips": 0, "subset": subset_name}

    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    # Entity accuracy (with anomaly exclusion)
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
    entity_ci = bca_ci(valid_entity) if len(valid_entity) > 1 else (0.0, 0.0)

    # WER
    aggregate_wer, wer_per_clip = compute_wer_batch(clips=clips, transcripts=transcripts)
    wer_arr = np.array(wer_per_clip, dtype=float)
    wer_ci = bca_ci(wer_arr) if len(wer_arr) > 1 else (0.0, 0.0)

    # Action-critical WER
    acwer, _ = compute_action_critical_wer(clips=clips, transcripts=transcripts)

    # Intent preservation
    intent, _ = compute_intent_preservation(clips=clips, transcripts=transcripts)

    # Domain vocab accuracy
    domain_vocab_acc, domain_vocab_per_clip = compute_entity_accuracy_domain_vocab(
        clips=clips,
        transcripts=transcripts,
        domain_vocab=DOMAIN_VOCAB,
    )
    domain_vocab_np = np.array(
        [np.nan if s is None else s for s in domain_vocab_per_clip], dtype=float
    )
    valid_domain = domain_vocab_np[~np.isnan(domain_vocab_np)]
    domain_vocab_ci = bca_ci(valid_domain) if len(valid_domain) > 1 else (0.0, 0.0)

    return {
        "subset": subset_name,
        "n_clips": len(clips),
        "entity_accuracy_gold92": round(entity_accuracy, 6),
        "entity_accuracy_ci_low": round(entity_ci[0], 6),
        "entity_accuracy_ci_high": round(entity_ci[1], 6),
        "wer_gold92": round(aggregate_wer, 6),
        "wer_ci_low": round(wer_ci[0], 6),
        "wer_ci_high": round(wer_ci[1], 6),
        "action_critical_wer_gold92": round(acwer, 6),
        "intent_preservation_gold92": round(intent, 6),
        "entity_accuracy_domain_vocab": round(domain_vocab_acc, 6),
        "entity_accuracy_domain_vocab_ci_low": round(domain_vocab_ci[0], 6),
        "entity_accuracy_domain_vocab_ci_high": round(domain_vocab_ci[1], 6),
    }


def main() -> None:
    """Compute all metrics and write output files."""
    from arf.scripts.utils.heartbeat import write_heartbeat

    write_heartbeat(
        task_id="t0008_moonshine_v2_benchmark", step_number=5, current_owner="implementation"
    )

    if not MOONSHINE_V2_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Transcripts not found at {MOONSHINE_V2_TRANSCRIPTS}. Run code/run_inference.py first."
        )

    print("Loading transcripts...")
    transcripts = load_transcripts(MOONSHINE_V2_TRANSCRIPTS)

    print("Loading gold-92 clips...")
    clips = load_gold92()
    print(f"Loaded {len(clips)} clips, {len(transcripts)} transcripts")

    # Check transcription failure rate
    total = len(clips)
    failures = sum(
        1 for clip in clips if not transcripts.get(clip.clip_id, {}).get("hypothesis", "").strip()
    )
    failure_rate = failures / total if total > 0 else 1.0
    print(f"Transcription failures: {failures}/{total} ({failure_rate:.1%})")

    if failure_rate >= 0.20:
        raise RuntimeError(
            f"Rejection criterion: transcription failure rate {failure_rate:.1%} >= 20%"
        )

    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    # Compute entity accuracy for all clips (with anomaly exclusion)
    print("Computing entity accuracy...")
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

    print(
        f"  entity_accuracy_gold92: {entity_accuracy:.4f} ({entity_ci[0]:.4f}-{entity_ci[1]:.4f})"
    )

    # WER
    print("Computing WER...")
    aggregate_wer, wer_per_clip = compute_wer_batch(clips=clips, transcripts=transcripts)
    wer_arr = np.array(wer_per_clip, dtype=float)
    wer_ci = bca_ci(wer_arr)
    print(f"  wer_gold92: {aggregate_wer:.4f} ({wer_ci[0]:.4f}-{wer_ci[1]:.4f})")

    if aggregate_wer > 0.6:
        raise RuntimeError(
            f"Rejection criterion triggered: WER={aggregate_wer:.3f} > 0.6. "
            "Transcription pipeline likely failed."
        )

    # Action-critical WER
    print("Computing action-critical WER...")
    acwer, acwer_per_clip = compute_action_critical_wer(clips=clips, transcripts=transcripts)
    acwer_arr = np.array(acwer_per_clip, dtype=float)
    acwer_ci = bca_ci(acwer_arr)
    print(f"  action_critical_wer_gold92: {acwer:.4f}")

    # Intent preservation
    print("Computing intent preservation...")
    intent, intent_per_clip = compute_intent_preservation(clips=clips, transcripts=transcripts)
    intent_arr = np.array(intent_per_clip, dtype=float)
    intent_ci = bca_ci(intent_arr)
    wrong_action_rate = 1.0 - intent
    print(f"  intent_preservation_gold92: {intent:.4f}")
    print(f"  wrong_action_rate_gold92: {wrong_action_rate:.4f}")

    # Latency p50
    latency_p50 = compute_latency_p50(transcripts)
    print(f"  latency_p50_seconds: {latency_p50:.3f}s")

    # Domain vocab entity accuracy
    print("Computing domain vocab entity accuracy...")
    domain_vocab_acc, domain_vocab_per_clip = compute_entity_accuracy_domain_vocab(
        clips=clips,
        transcripts=transcripts,
        domain_vocab=DOMAIN_VOCAB,
    )
    domain_vocab_np = np.array(
        [np.nan if s is None else s for s in domain_vocab_per_clip], dtype=float
    )
    valid_domain = domain_vocab_np[~np.isnan(domain_vocab_np)]
    domain_vocab_ci = bca_ci(valid_domain) if len(valid_domain) > 1 else (0.0, 0.0)
    print(
        f"  entity_accuracy_domain_vocab: {domain_vocab_acc:.4f} "
        f"({domain_vocab_ci[0]:.4f}-{domain_vocab_ci[1]:.4f})"
    )

    if domain_vocab_acc == 0.0:
        raise RuntimeError(
            "Rejection criterion: entity_accuracy_domain_vocab == 0.0 exactly. "
            "Domain vocabulary terms not recognized."
        )

    # Write metrics.json (legacy flat format)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics: dict[str, Any] = {
        "wer_gold92": round(aggregate_wer, 6),
        "entity_accuracy_gold92": round(entity_accuracy, 6),
        "entity_accuracy_domain_vocab": round(domain_vocab_acc, 6),
        "action_critical_wer_gold92": round(acwer, 6),
        "intent_preservation_gold92": round(intent, 6),
        "latency_p50_seconds": round(latency_p50, 4),
        "wrong_action_rate_gold92": round(wrong_action_rate, 6),
    }

    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    # Compute per-stage latency
    latency_by_stage = compute_latency_by_stage(transcripts)

    # Stratified metrics
    production_clips = [c for c in clips if c.accent_group == "production"]
    clean_clips = [c for c in clips if c.accent_group != "production"]
    print(f"\nProduction clips: {len(production_clips)}, Clean-voice clips: {len(clean_clips)}")

    production_metrics = compute_subset_metrics(
        clips=production_clips,
        transcripts=transcripts,
        subset_name="production",
    )
    clean_metrics = compute_subset_metrics(
        clips=clean_clips,
        transcripts=transcripts,
        subset_name="clean_voice",
    )
    all_metrics = compute_subset_metrics(
        clips=clips,
        transcripts=transcripts,
        subset_name="all",
    )

    # Per-clip analysis
    per_clip_analysis: list[dict[str, Any]] = []
    for i, clip in enumerate(clips):
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        rec = transcripts.get(clip.clip_id, {})
        per_clip_analysis.append(
            {
                "clip_id": clip.clip_id,
                "accent_group": clip.accent_group,
                "reference": clip.reference_text,
                "hypothesis": str(hyp_raw),
                "entity_accuracy": entity_scores_raw[i],
                "wer_local": wer_per_clip[i],
                "action_critical_wer": acwer_per_clip[i],
                "intent_preservation": intent_per_clip[i],
                "domain_vocab_accuracy": domain_vocab_per_clip[i],
                "latency_seconds": rec.get("latency_seconds", 0.0),
                "latency_stage": rec.get("latency_stage", "unknown"),
            }
        )

    # Write analysis_output.json
    analysis_output: dict[str, Any] = {
        "model": "UsefulSensors/moonshine-streaming-medium",
        "summary_table": {
            "all": all_metrics,
            "production": production_metrics,
            "clean_voice": clean_metrics,
        },
        "confidence_intervals": {
            "entity_accuracy_gold92": {
                "ci_low": round(entity_ci[0], 6),
                "ci_high": round(entity_ci[1], 6),
            },
            "wer_gold92": {
                "ci_low": round(wer_ci[0], 6),
                "ci_high": round(wer_ci[1], 6),
            },
            "action_critical_wer_gold92": {
                "ci_low": round(acwer_ci[0], 6),
                "ci_high": round(acwer_ci[1], 6),
            },
            "intent_preservation_gold92": {
                "ci_low": round(intent_ci[0], 6),
                "ci_high": round(intent_ci[1], 6),
            },
            "entity_accuracy_domain_vocab": {
                "ci_low": round(domain_vocab_ci[0], 6),
                "ci_high": round(domain_vocab_ci[1], 6),
            },
        },
        "latency_by_stage": latency_by_stage,
        "bootstrap_config": {
            "method": "BCa",
            "n_resamples": BCa_N_RESAMPLES,
            "random_state": BCa_RANDOM_STATE,
        },
        "failure_rate": round(failure_rate, 4),
        "n_clips": total,
        "anomaly_clips": [
            {
                "clip_id": CYRILLIC_ANOMALY_CLIP,
                "anomaly_type": "cyrillic_ground_truth_in_gold_set",
                "note": "Excluded from entity accuracy aggregate via np.nanmean.",
            }
        ],
        "per_clip_analysis": per_clip_analysis,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(analysis_output, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")

    # Print summary table
    print("\n=== SUMMARY ===")
    print(f"{'Metric':<40} {'Value':<12}")
    print("-" * 55)
    for key, val in metrics.items():
        print(f"  {key:<38} {val:.4f}")

    print("\nLatency by stage:")
    for stage, stats in latency_by_stage.items():
        print(f"  {stage}: p50={stats['p50']:.3f}s, p95={stats['p95']:.3f}s, n={stats['n']}")

    write_heartbeat(
        task_id="t0008_moonshine_v2_benchmark", step_number=5, current_owner="implementation"
    )


if __name__ == "__main__":
    main()
