"""Pareto frontier charts for t0024 Part A (structural pattern copied from t0019's make_charts.py).

Usage (local, no GPU needed):
    uv run python -u tasks/t0024_biasing_pareto_and_ft_biasing_ablation/code/make_charts.py

Reads results/pareto_tdt.json and results/pareto_unified.json (written by pareto.py) plus the raw
sweep JSONL files, and writes results/images/pareto_tdt.png and results/images/pareto_unified.png.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tasks.t0024_biasing_pareto_and_ft_biasing_ablation.code import paths

ALL_CELLS_COLOR: str = "#9e9e9e"
FRONTIER_COLOR: str = "#d62728"
LIVE_PROD_COLOR: str = "#1f77b4"
PERCENT_SCALE: float = 100.0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip() != ""]


def _load_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def plot_pareto_chart(
    *,
    sweep_path: Path,
    report_path: Path,
    out_path: Path,
    title: str,
    show_live_prod: bool,
) -> None:
    rows = _load_jsonl(sweep_path)
    report = _load_json(report_path)
    frontier: list[dict[str, Any]] = report["frontier"]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(
        [r["neutral_wer"] * PERCENT_SCALE for r in rows],
        [r["brand_exact_rate"] * PERCENT_SCALE for r in rows],
        s=20,
        color=ALL_CELLS_COLOR,
        alpha=0.5,
        label="all cells",
        zorder=1,
    )
    ax.plot(
        [c["neutral_wer"] * PERCENT_SCALE for c in frontier],
        [c["brand_exact_rate"] * PERCENT_SCALE for c in frontier],
        marker="o",
        color=FRONTIER_COLOR,
        linewidth=2,
        label="frontier",
        zorder=2,
    )
    if show_live_prod:
        live_prod: dict[str, Any] = report["live_prod_point"]
        live_prod_wer = live_prod["neutral_wer"] * PERCENT_SCALE
        live_prod_brand = live_prod["brand_exact_rate"] * PERCENT_SCALE
        ax.scatter(
            [live_prod_wer],
            [live_prod_brand],
            marker="*",
            s=250,
            color=LIVE_PROD_COLOR,
            label="live prod",
            zorder=3,
        )
        ax.annotate(
            "live prod",
            (live_prod_wer, live_prod_brand),
            textcoords="offset points",
            xytext=(8, 8),
            color=LIVE_PROD_COLOR,
            fontsize=9,
        )

    ax.set_xlabel("neutral_wer (%)")
    ax.set_ylabel("brand_exact_rate (%)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {out_path}")


def main() -> None:
    paths.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plot_pareto_chart(
        sweep_path=paths.T0023_SWEEP,
        report_path=paths.RESULTS_DIR / "pareto_tdt.json",
        out_path=paths.IMAGES_DIR / "pareto_tdt.png",
        title="Parakeet TDT 0.6B v3 — brand_exact_rate vs neutral_wer (t0023 sweep)",
        show_live_prod=True,
    )
    plot_pareto_chart(
        sweep_path=paths.T0022_SWEEP,
        report_path=paths.RESULTS_DIR / "pareto_unified.json",
        out_path=paths.IMAGES_DIR / "pareto_unified.png",
        title="Parakeet Unified EN 0.6B — brand_exact_rate vs neutral_wer (t0022 sweep)",
        show_live_prod=False,
    )


if __name__ == "__main__":
    main()
