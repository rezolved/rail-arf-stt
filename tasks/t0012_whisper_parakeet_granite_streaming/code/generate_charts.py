"""Generate benchmark charts for t0012 three-model production streaming results."""

from __future__ import annotations

import json
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import (  # noqa: E402
    METRICS_JSON,
    RESULTS_DIR,
    WHISPER_STREAMING_TRANSCRIPTS,
)

IMAGES_DIR = RESULTS_DIR / "images"


def load_results() -> tuple[dict, list]:
    """Load metrics.json and whisper streaming JSONL. Exit gracefully if not available."""
    if not METRICS_JSON.exists():
        print("Results not available yet — run GPU experiments first")
        sys.exit(0)
    if not WHISPER_STREAMING_TRANSCRIPTS.exists():
        print("Results not available yet — run GPU experiments first")
        sys.exit(0)

    with METRICS_JSON.open(encoding="utf-8") as fh:
        metrics = json.load(fh)

    whisper_clips = []
    with WHISPER_STREAMING_TRANSCRIPTS.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                whisper_clips.append(json.loads(line))

    return metrics, whisper_clips


def get_variant(metrics: dict, variant_id: str) -> dict:
    for v in metrics["variants"]:
        if v["variant_id"] == variant_id:
            return v["metrics"]
    raise KeyError(f"Variant {variant_id!r} not found in metrics.json")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    metrics, whisper_clips = load_results()

    ws = get_variant(metrics, "whisper-turbo-streaming")
    wb = get_variant(metrics, "whisper-turbo-batch")
    pk = get_variant(metrics, "parakeet-tdt-0.6b-v3-streaming-biased")
    gr = get_variant(metrics, "granite-speech-4.1-2b-streaming-biased")

    WHISPER_STREAM_COLOR = "#2f9e44"
    WHISPER_BATCH_COLOR = "#b2e09d"
    PARAKEET_COLOR = "#4dabf7"
    GRANITE_COLOR = "#f08c00"

    # ── Chart 1: Three-model accuracy comparison ─────────────────────────────────

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "Three-Model Accuracy — Production Streaming Mode (gold-92)",
        fontsize=13,
        fontweight="bold",
    )

    labels = [
        "Whisper\nstreaming",
        "Whisper\nbatch",
        "Parakeet\nstreaming",
        "Granite\nstreaming",
    ]
    colors = [WHISPER_STREAM_COLOR, WHISPER_BATCH_COLOR, PARAKEET_COLOR, GRANITE_COLOR]
    x = np.arange(4)

    metric_specs = [
        ("Entity Accuracy (overall)", "entity_accuracy_gold92"),
        ("Entity Accuracy (domain vocab)", "entity_accuracy_domain_vocab"),
        ("WER (lower = better)", "wer_gold92"),
    ]

    for ax, (title, key) in zip(axes, metric_specs, strict=True):
        vals = [ws[key] * 100, wb[key] * 100, pk[key] * 100, gr[key] * 100]
        bars = ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.5)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel("%")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylim(0, 115)
        ax.axvline(x=0.5, color="#dee2e6", linestyle="--", linewidth=1)
        for bar, val in zip(bars, vals, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = IMAGES_DIR / "chart_three_model_accuracy.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # ── Chart 2: Whisper streaming vs batch delta ─────────────────────────────────

    wd = metrics["whisper_streaming_vs_batch_delta"]
    delta_labels = ["ΔEA\n(pp)", "ΔEA_DV\n(pp)", "ΔWER\n(pp)", "ΔAC-WER\n(pp)", "ΔIP\n(pp)"]
    delta_vals = [
        wd["delta_entity_accuracy"] * 100,
        wd["delta_entity_accuracy_dv"] * 100,
        wd["delta_wer"] * 100,
        wd["delta_action_critical_wer"] * 100,
        wd["delta_intent_preservation"] * 100,
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle(
        "Whisper turbo: Streaming vs Batch Delta (streaming − batch)",
        fontsize=13,
        fontweight="bold",
    )
    bar_colors = [WHISPER_STREAM_COLOR if v >= 0 else "#e03131" for v in delta_vals]
    bars = ax.bar(delta_labels, delta_vals, color=bar_colors, edgecolor="white", width=0.5)
    ax.axhline(y=0, color="#343a40", linewidth=0.8)
    ax.set_ylabel("Percentage points")
    ax.set_ylim(-5, 5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, delta_vals, strict=True):
        ypos = bar.get_height() + 0.1 if val >= 0 else bar.get_height() - 0.4
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            ypos,
            f"{val:+.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out = IMAGES_DIR / "chart_whisper_streaming_vs_batch_delta.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # ── Chart 3: Latency distribution p50/p95/p99 ────────────────────────────────

    run_labels = [
        "Whisper\nstreaming",
        "Whisper\nbatch",
        "Parakeet\nstreaming",
        "Granite\nstreaming",
    ]
    p50_vals = [
        ws["latency_p50_seconds"],
        wb["latency_p50_seconds"],
        pk["latency_p50_seconds"],
        gr["latency_p50_seconds"],
    ]
    p95_vals = [
        ws["latency_p95_seconds"],
        wb["latency_p95_seconds"],
        pk["latency_p95_seconds"],
        gr["latency_p95_seconds"],
    ]
    p99_vals = [
        ws["latency_p99_seconds"],
        wb["latency_p99_seconds"],
        pk["latency_p99_seconds"],
        gr["latency_p99_seconds"],
    ]

    x2 = np.arange(4)
    width = 0.22
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.suptitle(
        "Latency Distribution — All Runs (Gold-92, H100 NVL)",
        fontsize=13,
        fontweight="bold",
    )
    b50 = ax.bar(x2 - width, p50_vals, width, label="p50", color="#2f9e44", edgecolor="white")
    ax.bar(x2, p95_vals, width, label="p95", color="#74c476", edgecolor="white")
    ax.bar(x2 + width, p99_vals, width, label="p99", color="#b2e09d", edgecolor="white")

    for bar, val in zip(b50, p50_vals, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val * 1000:.0f}ms",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

    ax.axhline(y=0.200, color="#e03131", linestyle="--", linewidth=1.2, label="200 ms target")
    ax.axhline(y=0.800, color="#f08c00", linestyle=":", linewidth=1.2, label="800 ms SLA")
    ax.set_xticks(x2)
    ax.set_xticklabels(run_labels, fontsize=9)
    ax.set_ylabel("Latency (seconds)")
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = IMAGES_DIR / "chart_latency_distribution.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # ── Chart 4: Whisper TTFD histogram ──────────────────────────────────────────

    ttfd_vals = [
        float(r["ttfd_seconds"]) * 1000 for r in whisper_clips if r.get("ttfd_seconds") is not None
    ]

    bins = [0, 500, 1000, 2000, max(max(ttfd_vals) + 1, 2001) if ttfd_vals else 5000]
    bin_labels = ["0–500 ms", "500 ms–1 s", "1–2 s", ">2 s"]

    counts, _ = np.histogram(ttfd_vals, bins=bins)
    pcts = counts / len(ttfd_vals) * 100 if ttfd_vals else counts * 0.0

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.suptitle(
        "Whisper turbo — Time-to-First-Delta (TTFD) Distribution",
        fontsize=13,
        fontweight="bold",
    )
    bars = ax.bar(bin_labels, pcts, color=WHISPER_STREAM_COLOR, edgecolor="white", width=0.6)
    ax.set_ylabel("% of clips")
    ax.set_xlabel("TTFD bucket")
    ax.set_ylim(0, 105)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    for bar, pct, cnt in zip(bars, pcts, counts, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{pct:.1f}%\n(n={cnt})",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out = IMAGES_DIR / "chart_whisper_ttfd.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # ── Chart 5: TTFD comparison — Whisper / Parakeet / Granite (chunked) ──────
    # Generated when at least parakeet_ttfd is present in metrics.json.

    pk_ttfd = metrics.get("parakeet_ttfd")
    gr_ttfd = metrics.get("granite_ttfd")
    if pk_ttfd is not None:
        ws_ttfd = metrics["whisper_ttfd"]
        ttfd_labels = ["p50", "p95", "p99"]

        series: list[tuple[str, list[float], str]] = [
            (
                "Whisper turbo",
                [ws_ttfd["p50"] * 1000, ws_ttfd["p95"] * 1000, ws_ttfd["p99"] * 1000],
                WHISPER_STREAM_COLOR,
            ),
            (
                "Parakeet chunked",
                [pk_ttfd["p50"] * 1000, pk_ttfd["p95"] * 1000, pk_ttfd["p99"] * 1000],
                PARAKEET_COLOR,
            ),
        ]
        if gr_ttfd is not None:
            series.append(
                (
                    "Granite chunked",
                    [gr_ttfd["p50"] * 1000, gr_ttfd["p95"] * 1000, gr_ttfd["p99"] * 1000],
                    GRANITE_COLOR,
                )
            )

        n_series = len(series)
        x5 = np.arange(len(ttfd_labels))
        w5 = 0.22 if n_series == 3 else 0.30
        offsets = np.linspace(-(n_series - 1) / 2, (n_series - 1) / 2, n_series) * w5

        fig, ax = plt.subplots(figsize=(9, 5))
        title = "Time-to-First-Delta — Chunked Re-Transcribe Mode"
        fig.suptitle(title, fontsize=13, fontweight="bold")

        for (label, vals, color), offset in zip(series, offsets, strict=True):
            bars = ax.bar(x5 + offset, vals, w5, label=label, color=color, edgecolor="white")
            for bar, val in zip(bars, vals, strict=True):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 3,
                    f"{val:.0f}ms",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                )

        ax.set_xticks(x5)
        ax.set_xticklabels(ttfd_labels)
        ax.set_ylabel("TTFD (ms)")
        ax.legend(fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        out = IMAGES_DIR / "chart_ttfd_comparison.png"
        fig.savefig(out, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {out}")

    print("\nAll charts generated.")


if __name__ == "__main__":
    main()
