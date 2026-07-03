"""Charts for t0019: hyperparam sweep heatmap + 3-approach condition comparison.

Usage (local, no GPU needed):
    uv run python -u tasks/t0019_parakeet_biasing_improvement/code/make_charts.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TASK_DIR = Path(__file__).parents[1]
RESULTS_DIR = TASK_DIR / "results"
IMAGES_DIR = RESULTS_DIR / "images"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def plot_hyperparam_heatmap() -> None:
    wide = load_jsonl(RESULTS_DIR / "hyperparam_sweep.jsonl")
    narrow = load_jsonl(RESULTS_DIR / "hyperparam_sweep_narrow.jsonl")

    alphas = sorted({round(r["alpha"], 2) for r in wide + narrow})
    depths = sorted({round(r["depth_scaling"], 2) for r in wide + narrow})

    grid = np.full((len(depths), len(alphas)), np.nan)
    lookup = {
        (round(r["alpha"], 2), round(r["depth_scaling"], 2)): r["ea_dv_20clip"]
        for r in wide + narrow
    }
    for i, depth in enumerate(depths):
        for j, alpha in enumerate(alphas):
            if (alpha, depth) in lookup:
                grid[i, j] = lookup[(alpha, depth)]

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(grid, cmap="viridis", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(alphas)))
    ax.set_xticklabels([str(a) for a in alphas])
    ax.set_yticks(range(len(depths)))
    ax.set_yticklabels([str(d) for d in depths])
    ax.set_xlabel("alpha (boosting_tree_alpha)")
    ax.set_ylabel("depth_scaling")
    ax.set_title(
        "20-clip screening EA-DV across GPU-PB hyperparameter grid\n(wide + narrow sweep, t0019)"
    )

    for i in range(len(depths)):
        for j in range(len(alphas)):
            if not np.isnan(grid[i, j]):
                ax.text(
                    j, i, f"{grid[i, j]:.2f}", ha="center", va="center", color="white", fontsize=8
                )

    # Mark baseline
    if 1.0 in alphas and 2.0 in depths:
        j0, i0 = alphas.index(1.0), depths.index(2.0)
        ax.add_patch(
            plt.Rectangle((j0 - 0.5, i0 - 0.5), 1, 1, fill=False, edgecolor="red", linewidth=3)
        )
        ax.text(j0, i0 - 0.7, "baseline", ha="center", color="red", fontsize=9, fontweight="bold")

    fig.colorbar(im, ax=ax, label="EA-DV (20-clip screening)")
    fig.tight_layout()
    out_path = IMAGES_DIR / "hyperparam_sweep_heatmap.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def plot_condition_comparison() -> None:
    with (RESULTS_DIR / "metrics.json").open(encoding="utf-8") as fh:
        metrics = json.load(fh)

    order = [
        "baseline",
        "hyperparam-alpha3.0-depth3.0",
        "hyperparam-alpha2.0-depth4.0",
        "phrase-expansion",
        "posthoc-replacement-check",
    ]
    labels = [
        "Baseline\n(biasing only)",
        "Hyperparam\nα=3.0/d=3.0\n(rejected)",
        "Hyperparam\nα=2.0/d=4.0\n(rejected)",
        "Phrase\nexpansion\n(null result)",
        "Post-hoc\nreplacement\n(winner)",
    ]
    variants = {v["variant_id"]: v for v in metrics["variants"]}

    wer = [variants[v]["metrics"]["wer_gold92"] * 100 for v in order]
    ea = [variants[v]["metrics"]["entity_accuracy_gold92"] * 100 for v in order]
    ea_dv = [variants[v]["metrics"]["entity_accuracy_domain_vocab"] * 100 for v in order]

    x = np.arange(len(order))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, wer, width, label="WER %", color="#d62728")
    ax.bar(x, ea, width, label="Entity Accuracy %", color="#1f77b4")
    ax.bar(x + width, ea_dv, width, label="Entity Accuracy Domain-Vocab %", color="#2ca02c")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("%")
    ax.set_title("t0019: biasing-improvement approaches vs baseline (gold-92, 93 clips)")
    ax.legend()
    ax.axhline(34.8, color="gray", linestyle="--", linewidth=1, label="_nolegend_")
    ax.text(len(order) - 0.5, 36, "t0017 EA-DV baseline (34.8%)", fontsize=8, color="gray")

    for i, _v in enumerate(order):
        ax.text(i - width, wer[i] + 1, f"{wer[i]:.1f}", ha="center", fontsize=7)
        ax.text(i, ea[i] + 1, f"{ea[i]:.1f}", ha="center", fontsize=7)
        ax.text(i + width, ea_dv[i] + 1, f"{ea_dv[i]:.1f}", ha="center", fontsize=7)

    fig.tight_layout()
    out_path = IMAGES_DIR / "condition_comparison.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plot_hyperparam_heatmap()
    plot_condition_comparison()


if __name__ == "__main__":
    main()
