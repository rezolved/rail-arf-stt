"""Generate required charts for t0002_baseline_evaluation.

Chart 1: Grouped bar chart comparing primary metrics for both systems with BCa CI error bars.
Chart 2: Per-utterance scatter plot of entity accuracy coloured by accent group.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from tasks.t0002_baseline_evaluation.code.paths import (
    ANALYSIS_OUTPUT,
    RESULTS_IMAGES_DIR,
)

matplotlib.use("Agg")  # Non-interactive backend for file output

DPI = 150
FIGURE_SIZE_BAR = (10, 6)
FIGURE_SIZE_SCATTER = (8, 8)

# Colour palette consistent across both charts
PALETTE: dict[str, str] = {
    "Deepgram Nova-2": "#2196F3",  # Blue
    "Whisper Large v3": "#FF9800",  # Orange
}

ACCENT_GROUP_PALETTE: dict[str, str] = {
    "clean_voices": "#4CAF50",  # Green
    "production": "#9C27B0",  # Purple
    "error_cases": "#F44336",  # Red
    "unknown": "#9E9E9E",  # Grey
}


def load_analysis() -> dict[str, Any]:
    """Load analysis output."""
    with ANALYSIS_OUTPUT.open(encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


def generate_bar_chart(
    *,
    analysis: dict[str, Any],
    output_path: Path,
) -> None:
    """Generate Chart 1: grouped bar chart comparing primary metrics with BCa CI error bars.

    Metrics: entity_accuracy_gold92, wer_gold92, action_critical_wer_gold92
    """
    summary_table: list[dict[str, Any]] = analysis.get("summary_table", [])

    if len(summary_table) == 0:
        print("WARNING: No summary table data available — generating placeholder chart")

    metric_configs: list[tuple[str, str]] = [
        ("entity_accuracy_gold92", "Entity Accuracy"),
        ("wer_gold92", "WER"),
        ("action_critical_wer_gold92", "Action-Critical WER"),
    ]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_BAR)

    n_metrics = len(metric_configs)
    n_systems = len(summary_table)
    bar_width = 0.35 if n_systems > 1 else 0.5

    x_positions = np.arange(n_metrics)

    for sys_idx, sys_row in enumerate(summary_table):
        system_label: str = str(sys_row.get("system", f"System {sys_idx + 1}"))
        color = PALETTE.get(system_label, f"C{sys_idx}")
        offset = (sys_idx - (n_systems - 1) / 2) * bar_width

        values: list[float] = []
        yerr_lower: list[float] = []
        yerr_upper: list[float] = []

        for metric_key, _metric_label in metric_configs:
            val = float(sys_row.get(metric_key, 0.0))
            ci_low = float(sys_row.get(f"{metric_key}_ci_low", val))
            ci_high = float(sys_row.get(f"{metric_key}_ci_high", val))
            values.append(val)
            yerr_lower.append(max(0.0, val - ci_low))
            yerr_upper.append(max(0.0, ci_high - val))

        ax.bar(
            x_positions + offset,
            values,
            bar_width,
            label=system_label,
            color=color,
            alpha=0.85,
            yerr=[yerr_lower, yerr_upper],
            capsize=5,
            error_kw={"elinewidth": 1.5, "capthick": 1.5},
        )

    ax.set_xlabel("Metric", fontsize=12)
    ax.set_ylabel("Score (lower is better for WER metrics)", fontsize=12)
    ax.set_title(
        "Figure 1: Primary metric comparison — Deepgram Nova-2 vs Whisper Large v3 on gold-92.",
        fontsize=11,
        pad=15,
    )
    ax.set_xticks(x_positions)
    ax.set_xticklabels([label for _, label in metric_configs], fontsize=11)
    ax.set_ylim(0.0, 1.1)
    ax.axhline(y=1.0, color="grey", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.legend(fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Chart 1 to {output_path} ({output_path.stat().st_size:,} bytes)")


def generate_scatter_chart(
    *,
    analysis: dict[str, Any],
    output_path: Path,
) -> None:
    """Generate Chart 2: per-utterance entity accuracy scatter plot coloured by accent group.

    x-axis: entity accuracy for first system (or Deepgram if available)
    y-axis: entity accuracy for Whisper
    Points coloured by accent_group.
    """
    # Try to get per-clip entity accuracy from predictions JSONL if available
    whisper_ea: dict[str, float | None] = {}
    deepgram_ea: dict[str, float | None] = {}
    accent_groups: dict[str, str] = {}

    # Load Whisper predictions for per-clip data
    whisper_pred_path = Path(
        "tasks/t0002_baseline_evaluation/assets/predictions/"
        "whisper-large-v3-gold92/files/predictions-gold92.jsonl"
    )
    if whisper_pred_path.exists():
        with whisper_pred_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record: dict[str, Any] = json.loads(line)
                clip_id: str = record["clip_id"]
                ea = record.get("entity_accuracy")
                whisper_ea[clip_id] = float(ea) if ea is not None else None
                accent_groups[clip_id] = str(record.get("accent_group", "unknown"))

    # Load Deepgram predictions if available
    deepgram_pred_path = Path(
        "tasks/t0002_baseline_evaluation/assets/predictions/"
        "deepgram-nova2-gold92/files/predictions-gold92.jsonl"
    )
    has_deepgram = False
    if deepgram_pred_path.exists():
        with deepgram_pred_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                clip_id = record["clip_id"]
                ea = record.get("entity_accuracy")
                # Only count as real data if hypothesis is not None
                if record.get("hypothesis") is not None and ea is not None:
                    deepgram_ea[clip_id] = float(ea)
                    has_deepgram = True

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SCATTER)

    if has_deepgram and len(deepgram_ea) > 0:
        # Full scatter: x=Deepgram, y=Whisper
        x_label = "Deepgram Nova-2 entity accuracy per clip"
        y_label = "Whisper Large v3 entity accuracy per clip"

        for group, color in ACCENT_GROUP_PALETTE.items():
            group_clips = [cid for cid, ag in accent_groups.items() if ag == group]
            if len(group_clips) == 0:
                continue
            xs = [deepgram_ea.get(cid, 0.0) or 0.0 for cid in group_clips]
            ys = [whisper_ea.get(cid, 0.0) or 0.0 for cid in group_clips]
            ax.scatter(xs, ys, c=color, label=group, alpha=0.7, s=50, edgecolors="white")

        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5, label="y=x (equal performance)")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
    else:
        # Single-system scatter: show Whisper entity accuracy by clip index
        x_label = "Clip index (sorted by Whisper entity accuracy)"
        y_label = "Whisper Large v3 entity accuracy"

        sorted_clips = sorted(whisper_ea.keys(), key=lambda c: whisper_ea.get(c) or 0.0)

        for group, color in ACCENT_GROUP_PALETTE.items():
            group_clip_ids = [cid for cid in sorted_clips if accent_groups.get(cid) == group]
            if len(group_clip_ids) == 0:
                continue
            xs = [sorted_clips.index(cid) for cid in group_clip_ids]
            ys = [whisper_ea.get(cid) or 0.0 for cid in group_clip_ids]
            ax.scatter(xs, ys, c=color, label=group, alpha=0.7, s=50, edgecolors="white")

        ax.set_xlabel("Clip index (sorted by entity accuracy)", fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(
        "Figure 2: Per-utterance entity accuracy correlation — "
        "clips above diagonal favour Whisper.",
        fontsize=11,
        pad=15,
    )
    ax.legend(fontsize=10, loc="upper left")
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Chart 2 to {output_path} ({output_path.stat().st_size:,} bytes)")


def main() -> None:
    """Generate both required charts."""
    analysis = load_analysis()

    bar_chart_path = RESULTS_IMAGES_DIR / "fig1_primary_metrics_comparison.png"
    scatter_chart_path = RESULTS_IMAGES_DIR / "fig2_per_utterance_entity_accuracy.png"

    generate_bar_chart(analysis=analysis, output_path=bar_chart_path)
    generate_scatter_chart(analysis=analysis, output_path=scatter_chart_path)

    print("\nChart generation complete.")
    print(f"  Chart 1: {bar_chart_path}")
    print(f"  Chart 2: {scatter_chart_path}")


if __name__ == "__main__":
    main()
