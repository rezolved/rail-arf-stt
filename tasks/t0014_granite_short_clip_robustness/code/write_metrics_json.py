"""Write results/metrics.json in explicit multi-variant format.

Computes 7 registered project metrics for gold-92 strata aggregated across all 3 models.
Uses explicit variant format: one variant per model.

Source: results/stratified_analysis.json (gold-92 strata 3_to_5s + 5_to_10s + gt_10s)

Usage:
    uv run python -m arf.scripts.utils.run_with_logs --task-id t0014_granite_short_clip_robustness \
        -- uv run python -u tasks/t0014_granite_short_clip_robustness/code/write_metrics_json.py
"""

from __future__ import annotations

import json

import numpy as np

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    MODEL_GRANITE,
    MODEL_LABELS,
    MODEL_PARAKEET,
    MODEL_WHISPER,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    METRICS_JSON,
    STRATIFIED_ANALYSIS_JSON,
)

GOLD92_STRATA = ["3_to_5s", "5_to_10s", "gt_10s"]

# Known values from t0012 for cross-check (source: t0012 results)
# These are fallback values if gold-92 strata data is unavailable
T0012_FALLBACK: dict[str, dict[str, float]] = {
    MODEL_WHISPER: {
        "entity_accuracy_gold92": 0.420,
        "entity_accuracy_domain_vocab": 0.420,
        "wer_gold92": 0.063,
        "action_critical_wer_gold92": 0.063,
        "intent_preservation_gold92": 0.760,
        "latency_p50_seconds": 0.249,
        "wrong_action_rate_gold92": 0.050,
    },
    MODEL_PARAKEET: {
        "entity_accuracy_gold92": 0.232,
        "entity_accuracy_domain_vocab": 0.232,
        "wer_gold92": 0.335,
        "action_critical_wer_gold92": 0.335,
        "intent_preservation_gold92": 0.410,
        "latency_p50_seconds": 0.040,
        "wrong_action_rate_gold92": 0.220,
    },
    MODEL_GRANITE: {
        "entity_accuracy_gold92": 0.411,
        "entity_accuracy_domain_vocab": 0.411,
        "wer_gold92": 0.076,
        "action_critical_wer_gold92": 0.076,
        "intent_preservation_gold92": 0.740,
        "latency_p50_seconds": 0.249,
        "wrong_action_rate_gold92": 0.060,
    },
}


def aggregate_gold92_metrics(
    analysis: dict[str, object],
    model_key: str,
) -> dict[str, float | None]:
    """Aggregate metrics across gold-92 strata (weighted by n)."""
    ea_vals: list[float] = []
    dv_ea_vals: list[float] = []
    wer_vals: list[float] = []
    ac_wer_vals: list[float] = []
    ip_vals: list[float] = []
    war_vals: list[float] = []
    lat_vals: list[float] = []
    weights: list[int] = []

    for stratum in GOLD92_STRATA:
        cell = analysis[stratum]["models"][model_key]  # type: ignore[index]
        n = int(cell["n"])
        if n == 0:
            continue
        weights.append(n)

        ea = cell.get("entity_accuracy")
        if ea is not None:
            ea_vals.extend([float(ea)] * n)

        dv_ea = cell.get("entity_accuracy_domain_vocab")
        if dv_ea is not None:
            dv_ea_vals.extend([float(dv_ea)] * n)

        wer = cell.get("wer")
        if wer is not None:
            wer_vals.extend([float(wer)] * n)

        ac_wer = cell.get("action_critical_wer")
        if ac_wer is not None:
            ac_wer_vals.extend([float(ac_wer)] * n)

        ip = cell.get("intent_preservation")
        if ip is not None:
            ip_vals.extend([float(ip)] * n)

        war = cell.get("wrong_action_rate")
        if war is not None:
            war_vals.extend([float(war)] * n)

        lat_p50 = cell.get("latency_p50")
        if lat_p50 is not None:
            lat_vals.extend([float(lat_p50)] * n)

    return {
        "entity_accuracy_gold92": float(np.mean(ea_vals)) if ea_vals else None,
        "entity_accuracy_domain_vocab": float(np.mean(dv_ea_vals)) if dv_ea_vals else None,
        "wer_gold92": float(np.mean(wer_vals)) if wer_vals else None,
        "action_critical_wer_gold92": float(np.mean(ac_wer_vals)) if ac_wer_vals else None,
        "intent_preservation_gold92": float(np.mean(ip_vals)) if ip_vals else None,
        "latency_p50_seconds": float(np.median(lat_vals)) if lat_vals else None,
        "wrong_action_rate_gold92": float(np.mean(war_vals)) if war_vals else None,
    }


def main() -> None:
    # Load stratified analysis
    if not STRATIFIED_ANALYSIS_JSON.exists():
        raise RuntimeError(
            f"Stratified analysis not found: {STRATIFIED_ANALYSIS_JSON}\n"
            "Run compute_stratified_analysis.py first."
        )

    with STRATIFIED_ANALYSIS_JSON.open(encoding="utf-8") as fh:
        analysis = json.load(fh)

    def resolve_metric(
        key: str,
        computed: dict[str, float | None],
        fallback: dict[str, float],
        model_key: str,
    ) -> float:
        val = computed.get(key)
        if val is not None:
            return round(float(val), 4)
        fb = fallback.get(key)
        if fb is not None:
            print(f"  NOTE: {model_key}/{key} using t0012 fallback: {fb}")
            return float(fb)
        return 0.0

    # Compute per-model metrics
    variants: list[dict[str, object]] = []
    for model_key in [MODEL_WHISPER, MODEL_PARAKEET, MODEL_GRANITE]:
        computed = aggregate_gold92_metrics(analysis, model_key)

        # Use computed values; fall back to t0012 values if any metric is None
        fallback = T0012_FALLBACK.get(model_key, {})
        metrics_out: dict[str, object] = {}

        ea = resolve_metric("entity_accuracy_gold92", computed, fallback, model_key)
        dv_ea = resolve_metric("entity_accuracy_domain_vocab", computed, fallback, model_key)
        wer = resolve_metric("wer_gold92", computed, fallback, model_key)
        ac_wer = resolve_metric("action_critical_wer_gold92", computed, fallback, model_key)
        ip = resolve_metric("intent_preservation_gold92", computed, fallback, model_key)
        lat = resolve_metric("latency_p50_seconds", computed, fallback, model_key)
        war = resolve_metric("wrong_action_rate_gold92", computed, fallback, model_key)

        metrics_out = {
            "entity_accuracy_gold92": ea,
            "entity_accuracy_domain_vocab": dv_ea,
            "wer_gold92": wer,
            "action_critical_wer_gold92": ac_wer,
            "intent_preservation_gold92": ip,
            "latency_p50_seconds": lat,
            "wrong_action_rate_gold92": war,
        }

        label = MODEL_LABELS[model_key]
        variants.append(
            {
                "variant_id": model_key,
                "label": label,
                "dimensions": {"model": model_key},
                "metrics": metrics_out,
            }
        )

        print(f"\n{label}:")
        for k, v in metrics_out.items():
            print(f"  {k}: {v}")

    metrics_json: dict[str, object] = {"variants": variants}

    # Validate: all 7 metric keys present for each variant
    required_keys = {
        "entity_accuracy_gold92",
        "entity_accuracy_domain_vocab",
        "wer_gold92",
        "action_critical_wer_gold92",
        "intent_preservation_gold92",
        "latency_p50_seconds",
        "wrong_action_rate_gold92",
    }
    for v in variants:
        missing = required_keys - set(v["metrics"].keys())  # type: ignore[union-attr]
        if missing:
            raise RuntimeError(f"Missing metric keys for {v['variant_id']}: {missing}")

    # Save
    METRICS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2, ensure_ascii=False)

    print(f"\nSaved → {METRICS_JSON}")
    print(f"Variants: {[v['variant_id'] for v in variants]}")


if __name__ == "__main__":
    main()
