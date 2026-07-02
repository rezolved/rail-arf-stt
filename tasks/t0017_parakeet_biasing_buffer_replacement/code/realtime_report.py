"""Compute real-time-paced latency metrics and render bar charts.

Separate from the compute-only run.

Reads data/realtime_latency/*.jsonl, writes results/metrics_realtime.json and two bar charts:
  * rt_ttfd_by_interval.png       — TTFD (real-time) p50/p95 vs buffer interval (winner unified)
  * rt_finalization_by_interval.png — finalization p50/p95 vs buffer interval (winner unified)

Does NOT touch metrics.json or the compute-only charts.

Usage (repo root): python -u tasks/t0017_parakeet_biasing_buffer_replacement/code/realtime_report.py
"""

from __future__ import annotations

import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import BUFFER_INTERVALS_MS
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import (
    DATA_DIR,
    IMAGES_DIR,
    RESULTS_DIR,
)

RT_DIR = DATA_DIR / "realtime_latency"
METRICS_RT_JSON = RESULTS_DIR / "metrics_realtime.json"

C_WINNER = "#2f80ed"
C_P95 = "#a9c9f5"
C_PROD = "#8892a6"
GRID = "#e6e6e6"


def _pctile(rows: list[dict], key: str, p: float) -> float:
    vals = [float(r[key]) for r in rows]
    return float(np.percentile(vals, p)) if vals else 0.0


def load(path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)


def _labels(ax, bars, fmt) -> None:
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2, h, fmt.format(h), ha="center", va="bottom", fontsize=8
        )


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    variants: list[dict] = []
    uni_by_interval: dict[int, list[dict]] = {}
    for interval in BUFFER_INTERVALS_MS:
        path = RT_DIR / f"unified_{interval}ms.jsonl"
        if not path.exists():
            print(f"MISSING {path}")
            continue
        rows = load(path)
        uni_by_interval[interval] = rows
        variants.append(
            {
                "variant_id": f"unified-{interval}ms-realtime",
                "model": "parakeet-unified-en-0.6b",
                "interval_ms": interval,
                "n_clips": len(rows),
                "ttfd_realtime_p50_s": round(_pctile(rows, "ttfd_realtime_s", 50), 4),
                "ttfd_realtime_p95_s": round(_pctile(rows, "ttfd_realtime_s", 95), 4),
                "finalization_p50_s": round(_pctile(rows, "finalization_s", 50), 4),
                "finalization_p95_s": round(_pctile(rows, "finalization_s", 95), 4),
                "behind_realtime_p95_s": round(_pctile(rows, "behind_realtime_s", 95), 4),
            }
        )

    tdt_path = RT_DIR / "tdt_1000ms.jsonl"
    if tdt_path.exists():
        rows = load(tdt_path)
        variants.append(
            {
                "variant_id": "tdt-1000ms-realtime",
                "model": "parakeet-tdt-0.6b-v3",
                "interval_ms": 1000,
                "n_clips": len(rows),
                "ttfd_realtime_p50_s": round(_pctile(rows, "ttfd_realtime_s", 50), 4),
                "ttfd_realtime_p95_s": round(_pctile(rows, "ttfd_realtime_s", 95), 4),
                "finalization_p50_s": round(_pctile(rows, "finalization_s", 50), 4),
                "finalization_p95_s": round(_pctile(rows, "finalization_s", 95), 4),
                "behind_realtime_p95_s": round(_pctile(rows, "behind_realtime_s", 95), 4),
            }
        )

    with METRICS_RT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(
            {"variants": variants, "note": "real-time-paced, 20ms frames, gold-92 subset"},
            fh,
            indent=2,
        )
    print(f"Wrote {METRICS_RT_JSON} ({len(variants)} variants)")

    intervals = [i for i in BUFFER_INTERVALS_MS if i in uni_by_interval]
    ttfd_p50 = [round(_pctile(uni_by_interval[i], "ttfd_realtime_s", 50), 3) for i in intervals]
    ttfd_p95 = [round(_pctile(uni_by_interval[i], "ttfd_realtime_s", 95), 3) for i in intervals]
    fin_p50 = [round(_pctile(uni_by_interval[i], "finalization_s", 50), 3) for i in intervals]
    fin_p95 = [round(_pctile(uni_by_interval[i], "finalization_s", 95), 3) for i in intervals]

    # Chart A: TTFD real-time by interval (p50 + p95 grouped bars)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = range(len(intervals))
    w = 0.4
    b1 = ax.bar([i - w / 2 for i in x], ttfd_p50, w, label="TTFD p50", color=C_WINNER)
    b2 = ax.bar([i + w / 2 for i in x], ttfd_p95, w, label="TTFD p95", color=C_P95)
    _labels(ax, b1, "{:.2f}")
    _labels(ax, b2, "{:.2f}")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(i) for i in intervals])
    ax.set_xlabel("buffer interval (ms)")
    ax.set_ylabel("time-to-first-word (s), real-time paced")
    ax.set_title(
        "Real-time TTFD grows with buffer interval — winner parakeet-unified\n"
        "(bigger buffer = slower first partial)"
    )
    ax.legend(frameon=False)
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "rt_ttfd_by_interval.png", dpi=140)
    plt.close(fig)

    # Chart B: finalization by interval (p50 + p95)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    b1 = ax.bar([i - w / 2 for i in x], fin_p50, w, label="finalization p50", color=C_WINNER)
    b2 = ax.bar([i + w / 2 for i in x], fin_p95, w, label="finalization p95", color=C_P95)
    _labels(ax, b1, "{:.2f}")
    _labels(ax, b2, "{:.2f}")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(i) for i in intervals])
    ax.set_xlabel("buffer interval (ms)")
    ax.set_ylabel("finalization latency (s) after speech ends")
    ax.set_title(
        "Real-time finalization latency vs buffer interval — winner parakeet-unified\n"
        "(near-flat: final pass cost is interval-independent)"
    )
    ax.legend(frameon=False)
    _style(ax)
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / "rt_finalization_by_interval.png", dpi=140)
    plt.close(fig)

    print(f"Charts written to {IMAGES_DIR}")
    # console table
    print(f"\n{'interval':>8} {'ttfd_p50':>9} {'ttfd_p95':>9} {'fin_p50':>8} {'fin_p95':>8}")
    for i, t50, t95, f50, f95 in zip(intervals, ttfd_p50, ttfd_p95, fin_p50, fin_p95, strict=True):
        print(f"{i:>8} {t50:>9.3f} {t95:>9.3f} {f50:>8.3f} {f95:>8.3f}")


if __name__ == "__main__":
    main()
