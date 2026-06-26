"""Generate benchmark charts for t0007 results."""

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from paths import RESULTS_DIR  # noqa: E402

IMAGES_DIR = RESULTS_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ── Data ──────────────────────────────────────────────────────────────────────

BASELINES = [
    {  # noqa: E501
        "label": "Parakeet TDT\n0.6B prod",  # noqa: E501
        "ea": 0.232,
        "ea_dv": 0.333,
        "wer": 0.152,
        "ac_wer": 0.335,
        "ip": 0.871,
    },
    {
        "label": "Whisper\nlarge-v3",
        "ea": 0.460,
        "ea_dv": 0.945,
        "wer": 0.085,
        "ac_wer": 0.025,
        "ip": 0.989,
    },
]

VARIANTS = [
    {
        "label": "Granite 4.1 2B\nbatch",
        "ea": 0.19529,
        "ea_dv": 0.318841,
        "wer": 0.12337,
        "ac_wer": 0.43038,
        "ip": 0.849462,
        "lat_p50": 0.2497,
        "lat_p95": 0.4206,
        "lat_p99": 0.5041,
    },
    {
        "label": "Granite 4.1 2B\nkw-biased ★",
        "ea": 0.402174,
        "ea_dv": 0.985507,
        "wer": 0.088265,
        "ac_wer": 0.082278,
        "ip": 0.924731,
        "lat_p50": 0.2484,
        "lat_p95": 0.4003,
        "lat_p99": 0.4619,
    },
    {
        "label": "Granite 4.1 2B\n+torch.compile",
        "ea": 0.402174,
        "ea_dv": 0.985507,
        "wer": 0.088265,
        "ac_wer": 0.082278,
        "ip": 0.924731,
        "lat_p50": 0.2455,
        "lat_p95": 0.3958,
        "lat_p99": 0.4552,
    },
    {
        "label": "Granite 4.1 2B\next-kw+postproc",
        "ea": 0.391304,
        "ea_dv": 1.0,
        "wer": 0.092277,
        "ac_wer": 0.101266,
        "ip": 0.913978,  # noqa: E501
        "lat_p50": 0.2299,
        "lat_p95": 0.3836,
        "lat_p99": 0.4557,
    },
]

BASELINE_COLORS = ["#6c757d", "#adb5bd"]
VARIANT_COLORS = ["#4dabf7", "#2f9e44", "#74c476", "#b2e09d"]
HIGHLIGHT_IDX = 1  # kw-biased is the primary variant

# ── Chart 1: Accuracy metrics comparison ──────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle(
    "Granite Speech 4.1 2B vs Baselines — Gold-92 Accuracy Metrics", fontsize=13, fontweight="bold"
)

metric_specs = [  # noqa: E501
    ("Entity Accuracy (overall)", "ea", False),
    ("Entity Accuracy (domain vocab)", "ea_dv", False),
    ("WER (lower = better)", "wer", True),
]

all_entries = BASELINES + VARIANTS
all_labels = [e["label"] for e in all_entries]
colors = BASELINE_COLORS + VARIANT_COLORS

for ax, (title, key, _lower_better) in zip(axes, metric_specs, strict=True):
    values = [e[key] * 100 for e in all_entries]
    bar_colors = [
        "#e67700" if i == len(BASELINES) + HIGHLIGHT_IDX else c for i, c in enumerate(colors)
    ]
    bars = ax.bar(
        range(len(all_entries)), values, color=bar_colors, edgecolor="white", linewidth=0.5
    )
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylabel("%")
    ax.set_xticks(range(len(all_entries)))
    ax.set_xticklabels(all_labels, fontsize=7.5, rotation=0, ha="center")
    ax.set_ylim(0, 110)  # noqa: E501
    ax.axvline(x=len(BASELINES) - 0.5, color="#dee2e6", linestyle="--", linewidth=1)
    for bar, val in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
        )  # noqa: E501
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out_path = IMAGES_DIR / "chart_accuracy_comparison.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

# ── Chart 2: AC-WER + Intent Preservation ─────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
fig.suptitle(
    "Granite Speech 4.1 2B — Action-Critical Metrics vs Baselines", fontsize=13, fontweight="bold"
)

for ax, (title, key, _lower_better) in zip(
    axes,
    [
        ("Action-Critical WER (lower = better)", "ac_wer", True),
        ("Intent Preservation (higher = better)", "ip", False),
    ],
    strict=True,
):
    values = [e[key] * 100 for e in all_entries]
    bar_colors = [
        "#e67700" if i == len(BASELINES) + HIGHLIGHT_IDX else c for i, c in enumerate(colors)
    ]
    bars = ax.bar(
        range(len(all_entries)), values, color=bar_colors, edgecolor="white", linewidth=0.5
    )
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylabel("%")
    ax.set_xticks(range(len(all_entries)))
    ax.set_xticklabels(all_labels, fontsize=7.5, rotation=0, ha="center")
    ax.set_ylim(0, 115 if not _lower_better else max(values) * 1.25)
    ax.axvline(x=len(BASELINES) - 0.5, color="#dee2e6", linestyle="--", linewidth=1)
    for bar, val in zip(bars, values, strict=True):
        ax.text(  # noqa: E501
            bar.get_x() + bar.get_width() / 2,  # noqa: E501
            bar.get_height() + 0.8,  # noqa: E501
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
        )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out_path = IMAGES_DIR / "chart_action_critical_metrics.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

# ── Chart 3: Latency (Granite variants only + Parakeet reference) ─────────────

fig, ax = plt.subplots(figsize=(9, 5))
fig.suptitle(
    "Granite Speech 4.1 2B — Inference Latency (Gold-92, H100 NVL)", fontsize=13, fontweight="bold"
)

lat_entries = [
    {"label": "Parakeet TDT\n0.6B prod\n(reference)", "p50": 0.038, "p95": None, "p99": None},
    *VARIANTS,
]
lat_labels = [e["label"] for e in lat_entries]  # noqa: E501
lat_colors = ["#6c757d"] + VARIANT_COLORS
# noqa: E501
x = np.arange(len(lat_entries))
width = 0.25

p50_vals = [e["lat_p50"] if "lat_p50" in e else e.get("p50") for e in lat_entries]
p95_vals = [e.get("lat_p95") for e in lat_entries]
p99_vals = [e.get("lat_p99") for e in lat_entries]

bars50 = ax.bar(
    x - width, [v or 0 for v in p50_vals], width, label="p50", color="#2f9e44", edgecolor="white"
)
bars95 = ax.bar(
    x, [v or 0 for v in p95_vals], width, label="p95", color="#74c476", edgecolor="white"
)
bars99 = ax.bar(
    x + width, [v or 0 for v in p99_vals], width, label="p99", color="#b2e09d", edgecolor="white"
)

# Annotate p50 only
for bar, val in zip(bars50, p50_vals, strict=True):
    if val:
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
ax.set_ylabel("Latency (seconds)")
ax.set_xticks(x)
ax.set_xticklabels(lat_labels, fontsize=8)
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 0.65)  # noqa: E501

plt.tight_layout()
out_path = IMAGES_DIR / "chart_latency.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

# ── Chart 4: Biasing gain ──────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(7, 4.5))
fig.suptitle(
    "Keyword Biasing Gain: biased vs. batch (Granite Speech 4.1 2B)", fontsize=12, fontweight="bold"
)

gain_metrics = [
    "ΔWER\n(pp, lower=better)",
    "ΔEntity\nAccuracy (pp)",
    "ΔDomain-Vocab\nAccuracy (pp)",
]
gain_values = [-3.5, 20.7, 66.7]
bar_colors_gain = ["#2f9e44" if v < 0 else "#e67700" for v in gain_values]
# WER lower is better so negative delta = green, positive accuracy = orange

bars = ax.bar(gain_metrics, gain_values, color=bar_colors_gain, edgecolor="white", width=0.5)
ax.axhline(y=0, color="#343a40", linewidth=0.8)
for bar, val in zip(bars, gain_values, strict=True):
    ypos = bar.get_height() + 1.0 if val >= 0 else bar.get_height() - 3.5
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        ypos,
        f"{val:+.1f} pp",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
ax.set_ylabel("Percentage points")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(-10, 80)

plt.tight_layout()
out_path = IMAGES_DIR / "chart_biasing_gain.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

# ── Chart 5: Stratified EA by accent group ────────────────────────────────────

with open(RESULTS_DIR.parent / "data" / "analysis_output.json") as f:
    analysis = json.load(f)

clips = analysis["per_clip_analysis"]
groups = {"production": [], "clean-voice": [], "error-cases": []}
for clip in clips:
    g = clip.get("accent_group", "")
    ea = clip.get("entity_accuracy_granite-4.1-2b-biased")
    if g in groups and ea is not None:
        groups[g].append(ea)

group_labels = ["Production\n(accented, n=34)", "Clean-voice\n(n=46)", "Error-cases\n(n=13)"]
group_means = [np.mean(groups[g]) * 100 if groups[g] else 0 for g in groups]

fig, ax = plt.subplots(figsize=(7, 4.5))
fig.suptitle(
    "Granite 4.1 2B kw-biased — Entity Accuracy by Accent Group", fontsize=12, fontweight="bold"
)

bars = ax.bar(
    group_labels, group_means, color=["#f08c00", "#2f9e44", "#4dabf7"], edgecolor="white", width=0.5
)
ax.axhline(y=40.2, color="#e03131", linestyle="--", linewidth=1.2, label="Overall mean 40.2%")
for bar, val in zip(bars, group_means, strict=True):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1.0,
        f"{val:.1f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
ax.set_ylabel("Entity Accuracy (%)")
ax.set_ylim(0, 90)
ax.legend(fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out_path = IMAGES_DIR / "chart_stratified_ea.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

print("\nAll charts generated.")
