"""Render polished bar charts for t0017 from results/metrics.json.

Charts (all bar):
  1. accuracy_comparison.png   — WER / EA / EA-DV, parakeet-tdt vs parakeet-unified (grouped bars).
  2. reliability_comparison.png — empty-output count on gold-92 (grouped bars).
  3. winner_latency_by_interval.png — latency p50 of the winner across buffer intervals (bars).
  4. latency_comparison.png     — latency p50 tdt vs unified at prod 1000ms (bars).

Usage (repo root): python -u tasks/t0017_parakeet_biasing_buffer_replacement/code/make_charts.py
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import BUFFER_INTERVALS_MS
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import IMAGES_DIR, METRICS_JSON

WINNER = "parakeet-unified-en-0.6b"
PROD = "parakeet-tdt-0.6b-v3"

# Palette
C_PROD = "#8892a6"  # muted grey-blue = incumbent
C_WINNER = "#2f80ed"  # blue = winner
C_ACCENT = "#27ae60"  # green
GRID = "#e6e6e6"


def _style(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)


def _labels(ax: plt.Axes, bars, fmt: str) -> None:
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2, h, fmt.format(h), ha="center", va="bottom", fontsize=9
        )


def main() -> None:
    with METRICS_JSON.open(encoding="utf-8") as fh:
        variants = json.load(fh)["variants"]

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold"})

    def m(model: str, interval: int) -> dict:
        return next(v for v in variants if v["model"] == model and v["interval_ms"] == interval)[
            "metrics"
        ]

    def d(model: str, interval: int) -> dict:
        return next(v for v in variants if v["model"] == model and v["interval_ms"] == interval)[
            "diagnostics"
        ]

    tdt, uni = m(PROD, 1000), m(WINNER, 1000)

    # ---- Chart 1: accuracy grouped bars ----
    fig, ax = plt.subplots(figsize=(9, 5.2))
    keys = ["wer_gold92", "entity_accuracy_gold92", "entity_accuracy_domain_vocab"]
    labels = ["WER\n(lower better)", "Entity Accuracy", "Entity Acc\n(domain vocab)"]
    x = range(len(keys))
    w = 0.38
    b1 = ax.bar(
        [i - w / 2 for i in x],
        [tdt[k] for k in keys],
        w,
        label="parakeet-tdt-0.6b-v3 (prod)",
        color=C_PROD,
    )
    b2 = ax.bar(
        [i + w / 2 for i in x],
        [uni[k] for k in keys],
        w,
        label="parakeet-unified-en-0.6b (winner)",
        color=C_WINNER,
    )
    _labels(ax, b1, "{:.3f}")
    _labels(ax, b2, "{:.3f}")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("score")
    ax.set_ylim(0, 0.45)
    ax.set_title("Biased accuracy on gold-92  ·  GPU-PB TurboBias (31-term Rezolve vocab)")
    ax.legend(frameon=False, loc="upper right")
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "accuracy_comparison.png", dpi=140)
    plt.close(fig)

    # ---- Chart 2: reliability (empty outputs) ----
    fig, ax = plt.subplots(figsize=(6.5, 5))
    names = ["parakeet-tdt\n(prod)", "parakeet-unified\n(winner)"]
    empties = [d(PROD, 1000)["empty_count"], d(WINNER, 1000)["empty_count"]]
    bars = ax.bar(names, empties, color=[C_PROD, C_WINNER], width=0.55)
    _labels(ax, bars, "{:.0f}")
    ax.set_ylabel("empty transcripts (of 93 clips)")
    ax.set_ylim(0, max(empties) + 1.5)
    ax.set_title("Reliability — empty outputs on gold-92 (lower better)")
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "reliability_comparison.png", dpi=140)
    plt.close(fig)

    # ---- Chart 3: winner latency by interval (bars) ----
    fig, ax = plt.subplots(figsize=(9, 5.2))
    lat = [m(WINNER, i)["latency_p50_seconds"] for i in BUFFER_INTERVALS_MS]
    bars = ax.bar([str(i) for i in BUFFER_INTERVALS_MS], lat, color=C_WINNER, width=0.6)
    _labels(ax, bars, "{:.3f}")
    ax.set_xlabel("buffer interval (ms)")
    ax.set_ylabel("compute latency p50 (s)")
    ax.set_ylim(0, max(lat) * 1.25)
    ax.set_title(
        f"Winner {WINNER} — compute latency p50 vs buffer interval\n"
        "(accuracy identical across all intervals)"
    )
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "winner_latency_by_interval.png", dpi=140)
    plt.close(fig)

    # ---- Chart 4: latency model comparison @1000ms ----
    fig, ax = plt.subplots(figsize=(6.5, 5))
    lats = [tdt["latency_p50_seconds"], uni["latency_p50_seconds"]]
    bars = ax.bar(names, lats, color=[C_PROD, C_WINNER], width=0.55)
    _labels(ax, bars, "{:.3f}s")
    ax.axhline(0.8, color="#c0392b", linestyle="--", linewidth=1.2)
    ax.text(
        1.45,
        0.8,
        "800ms voice-to-action budget",
        color="#c0392b",
        ha="right",
        va="bottom",
        fontsize=9,
    )
    ax.set_ylabel("compute latency p50 (s)")
    ax.set_ylim(0, 0.9)
    ax.set_title("Compute latency p50 @1000ms buffer (lower better)")
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "latency_comparison.png", dpi=140)
    plt.close(fig)

    print(f"Charts written to {IMAGES_DIR}")


if __name__ == "__main__":
    main()
