"""Charts for t0026_biasing_on_finetune_ablation (REQ-12).

Three charts, all saved to `results/images/` at dpi=150 (`matplotlib.use("Agg")`, no display):

* `plot_brand_exact_rate_bar` — adapted from `tasks/t0014_granite_short_clip_robustness/code/
  generate_charts.py` lines 114-171 (grouped-bar-with-`yerr` pattern), swapping duration strata for
  the `overall`/`Rezolve`/`brainpowa` buckets and the 2-model offset for a 4-arm offset.
* `plot_arms_vs_frontier` — adapted from `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/
  make_charts.py` lines 39-99 (frontier-line-overlay pattern), replacing the 100-cell gray scatter
  with 4 labeled arm points.
* `plot_bc_confusion_heatmap` — new (no prior-task precedent), a 2x2 per-clip B-vs-C confusion
  matrix.

Usage (local, no GPU needed, after `run_ablation.py`'s full run and `mcnemar_test.py` have written
their results files):
    python -u tasks/t0026_biasing_on_finetune_ablation/code/make_charts.py
"""

import json
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tasks.t0026_biasing_on_finetune_ablation.code import paths

ARM_IDS: list[str] = ["A", "B", "C", "D"]
ARM_COLORS: dict[str, str] = {"A": "#9e9e9e", "B": "#1f77b4", "C": "#ff7f0e", "D": "#2ca02c"}
BUCKETS: list[str] = ["overall", "rezolve", "brainpowa"]
BUCKET_LABELS: dict[str, str] = {
    "overall": "Overall",
    "rezolve": "Rezolve",
    "brainpowa": "brainpowa (n=3)",
}
PERCENT_SCALE: float = 100.0


def _load_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() != ""
    ]


def plot_brand_exact_rate_bar(metrics: dict[str, Any], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_title("Brand EXACT rate by arm", fontsize=14, fontweight="bold")
    ax.set_ylabel("brand_exact_rate (%)")
    ax.set_xlabel("Brand bucket")

    n_buckets = len(BUCKETS)
    bar_width = 0.2
    x = np.arange(n_buckets)

    for a_idx, arm in enumerate(ARM_IDS):
        heights: list[float] = []
        for bucket in BUCKETS:
            rate = metrics[arm]["brand_exact_rate"][bucket]
            heights.append(0.0 if rate is None else rate * PERCENT_SCALE)
        offset = (a_idx - 1.5) * bar_width
        # No CI error bars: the brainpowa bucket has only 3 clips, too few to fabricate a
        # confidence interval on — omit yerr entirely rather than plot a misleading interval.
        ax.bar(x + offset, heights, bar_width, label=f"Arm {arm}", color=ARM_COLORS[arm])

    ax.set_xticks(x)
    ax.set_xticklabels([BUCKET_LABELS[b] for b in BUCKETS])
    ax.set_ylim(0, 105)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def plot_arms_vs_frontier(
    metrics: dict[str, Any],
    frontier: list[dict[str, Any]],
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(
        [c["neutral_wer"] * PERCENT_SCALE for c in frontier],
        [c["brand_exact_rate"] * PERCENT_SCALE for c in frontier],
        marker="o",
        color="#d62728",
        linewidth=2,
        label="unified biasing-only frontier (t0024)",
        zorder=1,
    )
    for arm in ARM_IDS:
        arm_metrics = metrics[arm]
        wer_pct = arm_metrics["neutral_wer"] * PERCENT_SCALE
        rate_pct = arm_metrics["brand_exact_rate"]["overall"] * PERCENT_SCALE
        ax.scatter(
            [wer_pct],
            [rate_pct],
            marker="*",
            s=250,
            color=ARM_COLORS[arm],
            label=f"Arm {arm}",
            zorder=2,
        )
        ax.annotate(
            f"Arm {arm}",
            (wer_pct, rate_pct),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9,
        )

    ax.set_xlabel("neutral_wer (%)")
    ax.set_ylabel("brand_exact_rate, overall (%)")
    ax.set_title("Arms A-D vs. the unified biasing-only Pareto frontier")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def plot_bc_confusion_heatmap(
    predictions_b: list[dict[str, Any]],
    predictions_c: list[dict[str, Any]],
    out_path: Path,
) -> None:
    c_by_clip_id = {row["clip_id"]: row for row in predictions_c}
    matrix = np.zeros((2, 2), dtype=int)
    for row_b in predictions_b:
        if row_b.get("brand") is None:
            continue
        row_c = c_by_clip_id[row_b["clip_id"]]
        b_correct = int(row_b.get("label") == "EXACT")
        c_correct = int(row_c.get("label") == "EXACT")
        matrix[1 - b_correct, 1 - c_correct] += 1

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["correct", "incorrect"])
    ax.set_yticklabels(["correct", "incorrect"])
    ax.set_xlabel("Arm C")
    ax.set_ylabel("Arm B")
    ax.set_title("Per-clip brand correctness: B vs C (n=43 brand clips)")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def main() -> None:
    paths.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    metrics = _load_json(paths.RESULTS_DIR / "ablation_metrics.json")
    frontier = _load_json(paths.PARETO_UNIFIED_JSON)["frontier"]
    predictions_b = _load_jsonl(paths.RESULTS_DIR / "arm_b_predictions.jsonl")
    predictions_c = _load_jsonl(paths.RESULTS_DIR / "arm_c_predictions.jsonl")

    plot_brand_exact_rate_bar(metrics, paths.IMAGES_DIR / "chart1_brand_exact_rate.png")
    plot_arms_vs_frontier(metrics, frontier, paths.IMAGES_DIR / "chart2_pareto_scatter.png")
    plot_bc_confusion_heatmap(
        predictions_b, predictions_c, paths.IMAGES_DIR / "chart3_bc_confusion_heatmap.png"
    )


if __name__ == "__main__":
    main()
