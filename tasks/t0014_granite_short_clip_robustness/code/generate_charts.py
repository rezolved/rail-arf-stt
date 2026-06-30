"""Generate 3 charts from stratified analysis results.

Chart A: Short-clip failure rate (empty_rate + hallucination_rate) by duration and model.
Chart B: Stratified entity accuracy (grouped bar chart) with BCa CI error bars.
Chart C: Latency p50 by duration stratum (grouped bar chart).

Usage:
    uv run python -m arf.scripts.utils.run_with_logs --task-id t0014_granite_short_clip_robustness \
        -- uv run python -u tasks/t0014_granite_short_clip_robustness/code/generate_charts.py
"""

from __future__ import annotations

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")  # non-interactive backend for server

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    MODEL_GRANITE,
    MODEL_LABELS,
    MODEL_PARAKEET,
    MODEL_WHISPER,
    PRODUCTION_LATENCY_CONSTRAINT,
    STRATA_KEYS,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    CHART_ENTITY_ACCURACY,
    CHART_FAILURE_RATE,
    CHART_LATENCY,
    IMAGES_DIR,
    STRATIFIED_ANALYSIS_JSON,
)

MODELS = [MODEL_WHISPER, MODEL_PARAKEET, MODEL_GRANITE]
COLORS = {
    MODEL_WHISPER: "#2196F3",  # blue
    MODEL_PARAKEET: "#FF9800",  # orange
    MODEL_GRANITE: "#4CAF50",  # green
}
STRATUM_LABELS = {
    "lt_1s": "<1 s",
    "1_to_2s": "1–2 s",
    "2_to_3s": "2–3 s",
    "3_to_5s": "3–5 s\n(gold-92)",
    "5_to_10s": "5–10 s\n(gold-92)",
    "gt_10s": ">10 s\n(gold-92)",
}
DURATION_BIN_CENTERS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]  # synthetic bins only


def load_analysis() -> dict[str, object]:
    with STRATIFIED_ANALYSIS_JSON.open(encoding="utf-8") as fh:
        return json.load(fh)


def get_metric(analysis: dict[str, object], stratum: str, model: str, key: str) -> float | None:
    cell = analysis[stratum]["models"][model]  # type: ignore[index]
    val = cell.get(key)
    return float(val) if val is not None else None


def generate_chart_a(analysis: dict[str, object]) -> None:
    """Short-clip failure rate by duration and model — line chart (synthetic clips only)."""
    synthetic_strata = ["lt_1s", "1_to_2s", "2_to_3s"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Short-Clip Failure Rate by Duration and Model", fontsize=14, fontweight="bold")

    # Use 6 duration bins mapped to strata
    strata_to_bins: dict[str, list[float]] = {
        "lt_1s": [0.5],
        "1_to_2s": [1.0, 1.5],
        "2_to_3s": [2.0, 2.5, 3.0],
    }

    for ax_idx, metric_key in enumerate(["empty_rate", "hallucination_rate"]):
        ax = axes[ax_idx]
        metric_label = "Empty Rate (%)" if metric_key == "empty_rate" else "Hallucination Rate (%)"
        ax.set_title(metric_label)
        ax.set_xlabel("Duration (s)")
        ax.set_ylabel("%")

        for model in MODELS:
            xs: list[float] = []
            ys: list[float] = []
            for stratum in synthetic_strata:
                val = get_metric(analysis, stratum, model, metric_key)
                if val is not None:
                    for bin_center in strata_to_bins[stratum]:
                        xs.append(bin_center)
                        ys.append(float(val) * 100)

            if xs:
                label = MODEL_LABELS[model]
                ax.plot(xs, ys, marker="o", label=label, color=COLORS[model], linewidth=2)

        ax.legend()
        ax.set_xticks(DURATION_BIN_CENTERS)
        ax.set_ylim(-5, 105)
        ax.grid(axis="y", alpha=0.3)
        ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(CHART_FAILURE_RATE), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved → {CHART_FAILURE_RATE}")


def generate_chart_b(analysis: dict[str, object]) -> None:
    """Stratified entity accuracy — grouped bar chart with BCa CI error bars."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_title("Stratified Entity Accuracy by Duration", fontsize=14, fontweight="bold")
    ax.set_ylabel("Entity Accuracy (%)")
    ax.set_xlabel("Duration Stratum")

    n_strata = len(STRATA_KEYS)
    bar_width = 0.25
    x = np.arange(n_strata)

    for m_idx, model in enumerate(MODELS):
        heights: list[float] = []
        yerr_lo: list[float] = []
        yerr_hi: list[float] = []

        for stratum in STRATA_KEYS:
            ea = get_metric(analysis, stratum, model, "entity_accuracy")
            heights.append((ea or 0.0) * 100)

            # Add BCa CI error bars for gold-92 strata
            cell = analysis[stratum]["models"][model]  # type: ignore[index]
            ci = cell.get("entity_accuracy_ci_95")
            if ci is not None and ea is not None:
                yerr_lo.append(max(0.0, (ea - ci[0]) * 100))
                yerr_hi.append(max(0.0, (ci[1] - ea) * 100))
            else:
                yerr_lo.append(0.0)
                yerr_hi.append(0.0)

        offset = (m_idx - 1) * bar_width
        ax.bar(
            x + offset,
            heights,
            bar_width,
            label=MODEL_LABELS[model],
            color=COLORS[model],
            alpha=0.85,
            yerr=[yerr_lo, yerr_hi],
            error_kw={"capsize": 3, "elinewidth": 1},
        )

    ax.set_xticks(x)
    ax.set_xticklabels([STRATUM_LABELS[s] for s in STRATA_KEYS], fontsize=9)
    ax.legend(loc="upper right")
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.3)
    ax.axvline(x=2.5, color="gray", linestyle="--", linewidth=1, label="gold-92 boundary")

    # Annotation: gold-92 vs synthetic
    ax.text(0.5, 105, "← Synthetic clips", ha="center", fontsize=8, color="gray")
    ax.text(4.0, 105, "Gold-92 clips →", ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(CHART_ENTITY_ACCURACY), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved → {CHART_ENTITY_ACCURACY}")


def generate_chart_c(analysis: dict[str, object]) -> None:
    """Latency p50 by duration stratum — grouped bar chart."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_title("Latency p50 by Duration Stratum", fontsize=14, fontweight="bold")
    ax.set_ylabel("Latency p50 (seconds)")
    ax.set_xlabel("Duration Stratum")

    n_strata = len(STRATA_KEYS)
    bar_width = 0.25
    x = np.arange(n_strata)

    for m_idx, model in enumerate(MODELS):
        heights: list[float] = []
        for stratum in STRATA_KEYS:
            lat = get_metric(analysis, stratum, model, "latency_p50")
            heights.append(lat or 0.0)

        offset = (m_idx - 1) * bar_width
        ax.bar(
            x + offset,
            heights,
            bar_width,
            label=MODEL_LABELS[model],
            color=COLORS[model],
            alpha=0.85,
        )

    # Production latency constraint reference line
    ax.axhline(
        y=PRODUCTION_LATENCY_CONSTRAINT,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Production constraint ({PRODUCTION_LATENCY_CONSTRAINT:.1f}s)",
    )

    ax.set_xticks(x)
    ax.set_xticklabels([STRATUM_LABELS[s] for s in STRATA_KEYS], fontsize=9)
    ax.legend(loc="upper right")
    ax.set_ylim(0, max(PRODUCTION_LATENCY_CONSTRAINT * 2, 1.5))
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(CHART_LATENCY), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved → {CHART_LATENCY}")


def main() -> None:
    if not STRATIFIED_ANALYSIS_JSON.exists():
        raise RuntimeError(
            f"Stratified analysis not found: {STRATIFIED_ANALYSIS_JSON}\n"
            "Run compute_stratified_analysis.py first."
        )

    analysis = load_analysis()
    print("Generating charts ...")

    generate_chart_a(analysis)
    generate_chart_b(analysis)
    generate_chart_c(analysis)

    print("\nAll 3 charts generated:")
    print(f"  A: {CHART_FAILURE_RATE}")
    print(f"  B: {CHART_ENTITY_ACCURACY}")
    print(f"  C: {CHART_LATENCY}")


if __name__ == "__main__":
    main()
