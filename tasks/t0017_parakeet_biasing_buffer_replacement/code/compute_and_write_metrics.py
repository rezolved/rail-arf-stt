"""Compute biased metrics for parakeet-tdt vs parakeet-unified across all buffer intervals.

Reads prediction JSONL files from data/ and computes WER, EA, EA-DV, latency p50/p95, and TTFD
p50/p95 for each model x interval. Writes results/metrics.json in explicit multi-variant format.

Usage (repo root, PYTHONPATH set):
    python -u tasks/t0017_parakeet_biasing_buffer_replacement/code/compute_and_write_metrics.py
"""

from __future__ import annotations

import json
import string
from pathlib import Path
from typing import Any

import jiwer
import numpy as np

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (
    BUFFER_INTERVALS_MS,
    CYRILLIC_ANOMALY_CLIP,
    DOMAIN_VOCAB,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import (
    GOLD92_GROUND_TRUTH,
    METRICS_JSON,
    RESULTS_DIR,
    predictions_path,
)

MODEL_DISPLAY_NAMES: dict[str, str] = {
    "parakeet-tdt": "parakeet-tdt-0.6b-v3",
    "parakeet-unified": "parakeet-unified-en-0.6b",
}

ENTITY_PATTERNS: list[str] = [
    r"\bRezolve AI\b",
    r"\bRezolve\b",
    r"\bbrainpowa\b",
    r"\bSalesforce Commerce Cloud\b",
    r"\bShopify Plus\b",
    r"\bAdobe Commerce\b",
    r"\bAdobe\b",
    r"\bShopify\b",
    r"\bSalesforce\b",
    r"\bNASDAQ\b",
    r"\bAI Foundry\b",
    r"\bNLU\b",
    r"\bASR\b",
    r"\bSKU\b",
]


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def load_gold92_reference() -> dict[str, dict[str, Any]]:
    ref: dict[str, dict[str, Any]] = {}
    with GOLD92_GROUND_TRUTH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if "ground_truth" in record and "reference_text" not in record:
                record["reference_text"] = record["ground_truth"]
            ref[record["clip_id"]] = record
    return ref


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            result[r["clip_id"]] = r
    return result


def compute_wer(
    clip_ids: list[str],
    transcripts: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
) -> float:
    refs = [normalise(reference[c]["reference_text"]) for c in clip_ids]
    hyps = [normalise(str(transcripts.get(c, {}).get("transcript", ""))) for c in clip_ids]
    result = jiwer.process_words(refs, hyps)
    n = result.hits + result.substitutions + result.deletions
    return (result.substitutions + result.deletions + result.insertions) / n if n > 0 else 0.0


def compute_entity_accuracy(
    clip_ids: list[str],
    transcripts: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
) -> float:
    import re

    scores: list[float] = []
    for clip_id in clip_ids:
        if clip_id == CYRILLIC_ANOMALY_CLIP:
            continue
        ref_text = reference.get(clip_id, {}).get("reference_text", "")
        hyp = normalise(str(transcripts.get(clip_id, {}).get("transcript", "")))

        spans: list[str] = []
        seen: set[str] = set()
        for pattern in ENTITY_PATTERNS:
            for m in re.finditer(pattern, ref_text, re.IGNORECASE):
                key = m.group(0).lower()
                if key not in seen:
                    seen.add(key)
                    spans.append(m.group(0))

        if len(spans) == 0:
            continue
        correct = sum(1 for s in spans if normalise(s) in hyp)
        scores.append(correct / len(spans))

    return float(np.mean(scores)) if scores else 0.0


def compute_entity_accuracy_domain_vocab(
    clip_ids: list[str],
    transcripts: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
) -> float:
    vocab_norm = [normalise(t) for t in DOMAIN_VOCAB]
    total_correct = 0
    total_present = 0
    for clip_id in clip_ids:
        ref = normalise(reference.get(clip_id, {}).get("reference_text", ""))
        hyp = normalise(str(transcripts.get(clip_id, {}).get("transcript", "")))
        present = [t for t in vocab_norm if t in ref]
        if len(present) == 0:
            continue
        correct = sum(1 for t in present if t in hyp)
        total_correct += correct
        total_present += len(present)
    return total_correct / total_present if total_present > 0 else 0.0


def compute_all_metrics(
    clip_ids: list[str],
    transcripts: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
    *,
    label: str,
) -> dict[str, Any]:
    wer = compute_wer(clip_ids, transcripts, reference)
    ea = compute_entity_accuracy(clip_ids, transcripts, reference)
    ea_dv = compute_entity_accuracy_domain_vocab(clip_ids, transcripts, reference)

    lats = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    ttfds = [
        float(r["ttfd_seconds"]) for r in transcripts.values() if r.get("ttfd_seconds") is not None
    ]

    lat_p50 = float(np.percentile(lats, 50)) if lats else 0.0
    lat_p95 = float(np.percentile(lats, 95)) if lats else 0.0
    ttfd_p50 = float(np.percentile(ttfds, 50)) if ttfds else 0.0
    ttfd_p95 = float(np.percentile(ttfds, 95)) if ttfds else 0.0

    empty_count = sum(1 for r in transcripts.values() if r.get("is_empty", False))
    halluc_count = sum(1 for r in transcripts.values() if r.get("is_hallucination", False))

    print(
        f"  {label}: WER={wer:.4f} EA={ea:.4f} EA-DV={ea_dv:.4f} "
        f"lat_p50={lat_p50:.3f}s ttfd_p50={ttfd_p50:.3f}s empty={empty_count} halluc={halluc_count}"
    )

    return {
        "wer": round(wer, 6),
        "entity_accuracy": round(ea, 6),
        "entity_accuracy_domain_vocab": round(ea_dv, 6),
        "latency_p50_seconds": round(lat_p50, 4),
        "latency_p95_seconds": round(lat_p95, 4),
        "ttfd_p50_seconds": round(ttfd_p50, 4),
        "ttfd_p95_seconds": round(ttfd_p95, 4),
        "empty_count": empty_count,
        "hallucination_count": halluc_count,
        "n_clips": len(transcripts),
    }


def main() -> None:
    reference = load_gold92_reference()
    clip_ids = list(reference.keys())
    print(f"Reference clips: {len(clip_ids)}")

    variants: list[dict[str, Any]] = []
    missing: list[str] = []

    for model_slug, model_display in MODEL_DISPLAY_NAMES.items():
        for interval_ms in BUFFER_INTERVALS_MS:
            path = predictions_path(model_slug, interval_ms)
            if not path.exists():
                print(f"WARNING: {path} not found — skipping {model_slug} {interval_ms}ms")
                missing.append(f"{model_slug} {interval_ms}ms")
                continue
            transcripts = load_jsonl(path)
            label = f"{model_display} | {interval_ms}ms"
            variant_id = f"{model_slug}-{interval_ms}ms"
            metrics = compute_all_metrics(clip_ids, transcripts, reference, label=label)
            variants.append(
                {
                    "variant_id": variant_id,
                    "label": label,
                    "model": model_display,
                    "interval_ms": interval_ms,
                    "dimensions": {
                        "model": model_display,
                        "buffer_interval_ms": str(interval_ms),
                    },
                    "metrics": {
                        "wer_gold92": metrics["wer"],
                        "entity_accuracy_gold92": metrics["entity_accuracy"],
                        "entity_accuracy_domain_vocab": metrics["entity_accuracy_domain_vocab"],
                        "latency_p50_seconds": metrics["latency_p50_seconds"],
                        "latency_p95_seconds": metrics["latency_p95_seconds"],
                        "ttfd_p50_seconds": metrics["ttfd_p50_seconds"],
                        "ttfd_p95_seconds": metrics["ttfd_p95_seconds"],
                    },
                    "diagnostics": {
                        "empty_count": metrics["empty_count"],
                        "hallucination_count": metrics["hallucination_count"],
                        "n_clips": metrics["n_clips"],
                    },
                }
            )

    if missing:
        print(f"\nWARNING: {len(missing)} combinations missing: {missing}")

    output = {"variants": variants}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2)
    print(f"\nWrote {METRICS_JSON} ({len(variants)} variants)")

    col = 34
    header = f"{'Variant':<{col}} {'WER':>7} {'EA':>7} {'EA-DV':>7} {'Lat p50':>8} {'TTFD p50':>9}"
    print(f"\n{header}")
    print("-" * (col + 42))
    for v in variants:
        m = v["metrics"]
        print(
            f"{v['label']:<{col}}"
            f" {m['wer_gold92']:>7.4f}"
            f" {m['entity_accuracy_gold92']:>7.4f}"
            f" {m['entity_accuracy_domain_vocab']:>7.4f}"
            f" {m['latency_p50_seconds']:>7.3f}s"
            f" {m['ttfd_p50_seconds']:>8.3f}s"
        )


if __name__ == "__main__":
    main()
