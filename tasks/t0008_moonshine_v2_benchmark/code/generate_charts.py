"""Generate comparison charts for Moonshine v2 Medium benchmark.

Produces 4 charts in results/images/:
1. entity_accuracy_domain_vocab_comparison.png
2. wer_comparison.png
3. action_critical_wer_comparison.png
4. latency_distribution.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from tasks.t0008_moonshine_v2_benchmark.code.paths import (
    ANALYSIS_OUTPUT,
    IMAGES_DIR,
    METRICS_JSON,
)

# Whisper baselines (from prior tasks)
WHISPER_BASELINE_ENTITY_ACCURACY_DOMAIN_VOCAB = 0.945
WHISPER_BASELINE_WER = 0.085
WHISPER_BASELINE_ACTION_CRITICAL_WER = 0.025


def load_metrics(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def make_bar_comparison(
    *,
    title: str,
    ylabel: str,
    systems: list[str],
    values: list[float],
    error_bars: list[tuple[float, float]] | None = None,
    output_path: Path,
    higher_is_better: bool = True,
    baseline_value: float | None = None,
    baseline_label: str = "Whisper Baseline",
) -> None:
    """Create a bar chart comparing systems with optional error bars and baseline."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(systems))
    colors = ["#2196F3", "#FF9800"]

    if error_bars is not None:
        yerr_low = [max(0.0, v - eb[0]) for v, eb in zip(values, error_bars, strict=True)]
        yerr_high = [max(0.0, eb[1] - v) for v, eb in zip(values, error_bars, strict=True)]
        yerr = [yerr_low, yerr_high]
    else:
        yerr = None

    bars = ax.bar(
        x,
        values,
        color=colors[: len(systems)],
        width=0.5,
        yerr=yerr,
        capsize=5,
        error_kw={"elinewidth": 2, "ecolor": "black"},
        alpha=0.85,
    )

    # Add value labels on bars
    for bar, val in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.005,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    # Add baseline reference line
    if baseline_value is not None:
        ax.axhline(
            y=baseline_value,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"{baseline_label} ({baseline_value:.3f})",
        )
        ax.legend(fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylim(0, 1.1 * max(values + ([baseline_value] if baseline_value else [])))
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")


def make_latency_chart(
    *,
    latency_by_stage: dict,
    output_path: Path,
) -> None:
    """Create a grouped bar chart showing latency across stages."""
    stage_order = ["cold_start", "warmup", "warmed"]
    stages_present = [s for s in stage_order if s in latency_by_stage]

    metrics = ["p50", "p95", "p99"]
    metric_labels = ["p50", "p95", "p99"]
    colors = ["#4CAF50", "#FF9800", "#F44336"]

    x = np.arange(len(stages_present))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))

    for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors, strict=True)):
        vals = [latency_by_stage[s][metric] for s in stages_present]
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=label, color=color, alpha=0.85)
        for bar, val in zip(bars, vals, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.005,
                f"{val:.2f}s",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xlabel("Latency Stage", fontsize=12)
    ax.set_ylabel("Latency (seconds)", fontsize=12)
    ax.set_title(
        "Moonshine v2 Medium — Latency Distribution by Stage",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xticks(x)
    stage_display = {"cold_start": "Cold Start", "warmup": "Warmup", "warmed": "Warmed"}
    ax.set_xticklabels([stage_display.get(s, s) for s in stages_present], fontsize=11)
    ax.legend(title="Percentile", fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # Annotate n per stage
    for i, stage in enumerate(stages_present):
        n = latency_by_stage[stage].get("n", 0)
        ax.text(
            x[i],
            -0.05,
            f"n={n}",
            ha="center",
            va="top",
            fontsize=9,
            color="gray",
            transform=ax.get_xaxis_transform(),
        )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")


def main() -> None:
    """Generate all 4 benchmark charts."""
    metrics = load_metrics(METRICS_JSON)
    analysis = load_metrics(ANALYSIS_OUTPUT)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    cis = analysis.get("confidence_intervals", {})
    entity_dv_ci = cis.get("entity_accuracy_domain_vocab", {})

    # 1. entity_accuracy_domain_vocab comparison
    moonshine_dv = metrics["entity_accuracy_domain_vocab"]
    make_bar_comparison(
        title="Entity Accuracy (Domain Vocab) — Moonshine v2 Medium vs Whisper Baseline",
        ylabel="Entity Accuracy (Domain Vocab)",
        systems=["Moonshine v2 Medium"],
        values=[moonshine_dv],
        error_bars=[
            (
                entity_dv_ci.get("ci_low", moonshine_dv),
                entity_dv_ci.get("ci_high", moonshine_dv),
            )
        ],
        output_path=IMAGES_DIR / "entity_accuracy_domain_vocab_comparison.png",
        higher_is_better=True,
        baseline_value=WHISPER_BASELINE_ENTITY_ACCURACY_DOMAIN_VOCAB,
        baseline_label="Whisper Baseline",
    )

    # 2. WER comparison
    moonshine_wer = metrics["wer_gold92"]
    wer_ci = cis.get("wer_gold92", {})
    make_bar_comparison(
        title="Word Error Rate (WER) — Moonshine v2 Medium vs Whisper Baseline",
        ylabel="WER (lower is better)",
        systems=["Moonshine v2 Medium"],
        values=[moonshine_wer],
        error_bars=[
            (
                wer_ci.get("ci_low", moonshine_wer),
                wer_ci.get("ci_high", moonshine_wer),
            )
        ],
        output_path=IMAGES_DIR / "wer_comparison.png",
        higher_is_better=False,
        baseline_value=WHISPER_BASELINE_WER,
        baseline_label="Whisper Baseline",
    )

    # 3. Action-critical WER comparison
    moonshine_acwer = metrics["action_critical_wer_gold92"]
    acwer_ci = cis.get("action_critical_wer_gold92", {})
    make_bar_comparison(
        title="Action-Critical WER — Moonshine v2 Medium vs Whisper Baseline",
        ylabel="Action-Critical WER (lower is better)",
        systems=["Moonshine v2 Medium"],
        values=[moonshine_acwer],
        error_bars=[
            (
                acwer_ci.get("ci_low", moonshine_acwer),
                acwer_ci.get("ci_high", moonshine_acwer),
            )
        ],
        output_path=IMAGES_DIR / "action_critical_wer_comparison.png",
        higher_is_better=False,
        baseline_value=WHISPER_BASELINE_ACTION_CRITICAL_WER,
        baseline_label="Whisper Baseline",
    )

    # 4. Latency distribution by stage
    latency_by_stage = analysis.get("latency_by_stage", {})
    make_latency_chart(
        latency_by_stage=latency_by_stage,
        output_path=IMAGES_DIR / "latency_distribution.png",
    )

    print("\nAll charts generated.")


if __name__ == "__main__":
    main()
