"""Generate benchmark charts for t0011 streaming results."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from tasks.t0011_streaming_stt_benchmark.code.paths import RESULTS_DIR  # noqa: E402

IMAGES_DIR = RESULTS_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ── Data ─────────────────────────────────────────────────────────────────────

BATCH = {
    "parakeet": {
        "ea": 0.232,
        "ea_dv": 0.333,
        "wer": 0.152,
        "ac_wer": 0.335,
        "ip": 0.871,
        "lat": 0.038,
    },  # noqa: E501
    "granite": {
        "ea": 0.402,
        "ea_dv": 0.986,
        "wer": 0.088,
        "ac_wer": 0.082,
        "ip": 0.925,
        "lat": 0.248,
    },  # noqa: E501
}
STREAMING = {
    "parakeet": {
        "ea": 0.2315,
        "ea_dv": 0.3333,
        "wer": 0.1525,
        "ac_wer": 0.3354,
        "ip": 0.8710,
        "lat": 0.041,
        "lat_p95": 0.049,
        "lat_p99": 0.060,
    },  # noqa: E501
    "granite": {
        "ea": 0.4109,
        "ea_dv": 0.9710,
        "wer": 0.0883,
        "ac_wer": 0.0759,
        "ip": 0.9355,
        "lat": 0.250,
        "lat_p95": 0.404,
        "lat_p99": 0.470,
    },  # noqa: E501
}

PARAKEET_COLOR_BATCH = "#adb5bd"
PARAKEET_COLOR_STREAM = "#4dabf7"
GRANITE_COLOR_BATCH = "#6c757d"
GRANITE_COLOR_STREAM = "#2f9e44"

# ── Chart 1: Accuracy streaming vs batch ──────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle(
    "Streaming vs Batch — Accuracy Metrics (gold-92)",
    fontsize=13,
    fontweight="bold",
)

metric_specs = [
    ("Entity Accuracy (overall)", "ea"),
    ("Entity Accuracy (domain vocab)", "ea_dv"),
    ("WER (lower = better)", "wer"),
]

x = np.arange(4)
labels = ["Parakeet\nbatch", "Parakeet\nstreaming", "Granite\nbatch", "Granite\nstreaming"]
colors = [PARAKEET_COLOR_BATCH, PARAKEET_COLOR_STREAM, GRANITE_COLOR_BATCH, GRANITE_COLOR_STREAM]

for ax, (title, key) in zip(axes, metric_specs, strict=True):
    vals = [
        BATCH["parakeet"][key] * 100,
        STREAMING["parakeet"][key] * 100,
        BATCH["granite"][key] * 100,
        STREAMING["granite"][key] * 100,
    ]
    bars = ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylabel("%")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 115)
    ax.axvline(x=1.5, color="#dee2e6", linestyle="--", linewidth=1)
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
out = IMAGES_DIR / "chart_accuracy_streaming_vs_batch.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out}")

# ── Chart 2: Latency distribution p50/p95/p99 ────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
fig.suptitle(
    "Latency Distribution — Streaming (Gold-92, H100 NVL)",
    fontsize=13,
    fontweight="bold",
)

x2 = np.arange(2)
width = 0.22
p50_vals = [STREAMING["parakeet"]["lat"], STREAMING["granite"]["lat"]]
p95_vals = [STREAMING["parakeet"]["lat_p95"], STREAMING["granite"]["lat_p95"]]
p99_vals = [STREAMING["parakeet"]["lat_p99"], STREAMING["granite"]["lat_p99"]]

b50 = ax.bar(x2 - width, p50_vals, width, label="p50", color="#2f9e44", edgecolor="white")
b95 = ax.bar(x2, p95_vals, width, label="p95", color="#74c476", edgecolor="white")
b99 = ax.bar(x2 + width, p99_vals, width, label="p99", color="#b2e09d", edgecolor="white")

for bar, val in zip(b50, p50_vals, strict=True):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val * 1000:.0f}ms",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
    )

ax.axhline(y=0.200, color="#e03131", linestyle="--", linewidth=1.2, label="200 ms target")
ax.axhline(y=0.800, color="#f08c00", linestyle=":", linewidth=1.2, label="800 ms SLA")
ax.set_xticks(x2)
ax.set_xticklabels(
    ["Parakeet TDT 0.6b-v3\n(streaming biased)", "Granite Speech 4.1 2B\n(streaming biased)"],
    fontsize=10,
)  # noqa: E501
ax.set_ylabel("Latency (seconds)")
ax.legend(fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 0.65)

plt.tight_layout()
out = IMAGES_DIR / "chart_latency_distribution.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out}")

# ── Chart 3: Streaming delta ──────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle(
    "Streaming vs Batch Delta (streaming − batch)",
    fontsize=13,
    fontweight="bold",
)

delta_metrics = ["ΔEA\n(pp)", "ΔEA_DV\n(pp)", "ΔWER\n(pp)", "ΔAC-WER\n(pp)", "ΔIP\n(pp)"]

parakeet_deltas = [
    (STREAMING["parakeet"]["ea"] - BATCH["parakeet"]["ea"]) * 100,
    (STREAMING["parakeet"]["ea_dv"] - BATCH["parakeet"]["ea_dv"]) * 100,
    (STREAMING["parakeet"]["wer"] - BATCH["parakeet"]["wer"]) * 100,
    (STREAMING["parakeet"]["ac_wer"] - BATCH["parakeet"]["ac_wer"]) * 100,
    (STREAMING["parakeet"]["ip"] - BATCH["parakeet"]["ip"]) * 100,
]
granite_deltas = [
    (STREAMING["granite"]["ea"] - BATCH["granite"]["ea"]) * 100,
    (STREAMING["granite"]["ea_dv"] - BATCH["granite"]["ea_dv"]) * 100,
    (STREAMING["granite"]["wer"] - BATCH["granite"]["wer"]) * 100,
    (STREAMING["granite"]["ac_wer"] - BATCH["granite"]["ac_wer"]) * 100,
    (STREAMING["granite"]["ip"] - BATCH["granite"]["ip"]) * 100,
]

for ax, (model, deltas) in zip(
    axes,
    [("Parakeet TDT 0.6b-v3", parakeet_deltas), ("Granite Speech 4.1 2B", granite_deltas)],
    strict=True,
):
    bar_colors = ["#2f9e44" if v >= 0 else "#e03131" for v in deltas]
    bars = ax.bar(delta_metrics, deltas, color=bar_colors, edgecolor="white", width=0.5)
    ax.axhline(y=0, color="#343a40", linewidth=0.8)
    ax.set_title(model, fontsize=11, fontweight="bold")
    ax.set_ylabel("Percentage points")
    ax.set_ylim(-3, 3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, deltas, strict=True):
        ypos = bar.get_height() + 0.08 if val >= 0 else bar.get_height() - 0.25
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
out = IMAGES_DIR / "chart_streaming_delta.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out}")

print("\nAll charts generated.")
