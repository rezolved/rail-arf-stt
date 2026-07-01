"""Metrics computation for t0015: WER, entity accuracy, entity accuracy domain vocab.

Adapted from tasks/t0012_whisper_parakeet_granite_streaming/code/compute_metrics.py.
"""

from __future__ import annotations

import json
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jiwer
import numpy as np

from tasks.t0015_streaming_buffer_interval.code.constants import CYRILLIC_ANOMALY_CLIP, DOMAIN_VOCAB


@dataclass(frozen=True, slots=True)
class GoldClip:
    """A single gold-92 clip with reference annotation."""

    clip_id: str
    reference_text: str
    entity_spans: list[dict[str, Any]]
    audio_path: Path


def normalise(text: str) -> str:
    """Lowercase and strip punctuation for metric computation."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def load_clips(
    *,
    ground_truth_path: Path,
    gold_set_path: Path,
    audio_dir: Path,
) -> list[GoldClip]:
    """Load all gold-92 clips from ground_truth.jsonl and audio directory."""
    import re

    # Load ground truth
    gt_map: dict[str, dict[str, Any]] = {}
    with ground_truth_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            gt_map[record["clip_id"]] = record

    clips: list[GoldClip] = []

    # Known entity patterns for heuristic span inference (mirrors t0004)
    entity_patterns: list[tuple[str, str]] = [
        (r"\bRezolve AI\b", "brand"),
        (r"\bRezolve\b", "brand"),
        (r"\bbrainpowa\b", "product"),
        (r"\bSalesforce Commerce Cloud\b", "product"),
        (r"\bShopify Plus\b", "product"),
        (r"\bAdobe Commerce\b", "product"),
        (r"\bAdobe\b", "brand"),
        (r"\bShopify\b", "brand"),
        (r"\bSalesforce\b", "brand"),
        (r"\bNASDAQ\b", "ir_term"),
        (r"\bAI Foundry\b", "product"),
        (r"\bNLU\b", "tech_term"),
        (r"\bASR\b", "tech_term"),
        (r"\bSKU\b", "retail_term"),
    ]

    for clip_id, record in gt_map.items():
        reference_text = record.get("reference_text", "")
        audio_path = audio_dir / f"{clip_id}.wav"

        # Infer entity spans from reference text
        entity_spans: list[dict[str, Any]] = []
        seen_spans: set[str] = set()
        for pattern, entity_type in entity_patterns:
            for m in re.finditer(pattern, reference_text, re.IGNORECASE):
                span_text = m.group(0)
                key = span_text.lower()
                if key not in seen_spans:
                    seen_spans.add(key)
                    entity_spans.append(
                        {
                            "text": span_text,
                            "type": entity_type,
                            "start": m.start(),
                            "end": m.end(),
                        }
                    )

        clips.append(
            GoldClip(
                clip_id=clip_id,
                reference_text=reference_text,
                entity_spans=entity_spans,
                audio_path=audio_path,
            )
        )

    return clips


def compute_wer(
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute overall WER and per-clip WER list."""
    refs = [normalise(c.reference_text) for c in clips]
    hyps = [normalise(str(transcripts.get(c.clip_id, {}).get("transcript", ""))) for c in clips]
    result = jiwer.process_words(refs, hyps)
    n = result.hits + result.substitutions + result.deletions
    agg = (result.substitutions + result.deletions + result.insertions) / n if n > 0 else 0.0
    per_clip: list[float] = []
    for ref, hyp in zip(refs, hyps, strict=True):
        ri = jiwer.process_words([ref], [hyp])
        ni = ri.hits + ri.substitutions + ri.deletions
        per_clip.append((ri.substitutions + ri.deletions + ri.insertions) / ni if ni > 0 else 0.0)
    return agg, per_clip


def compute_entity_accuracy(
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    *,
    anomaly_ids: set[str] | None = None,
) -> tuple[float, list[float | None]]:
    """Compute entity accuracy (EA): fraction of entity spans present in hypothesis."""
    if anomaly_ids is None:
        anomaly_ids = {CYRILLIC_ANOMALY_CLIP}

    per_clip: list[float | None] = []
    for c in clips:
        if c.clip_id in anomaly_ids:
            per_clip.append(None)
            continue
        if len(c.entity_spans) == 0:
            per_clip.append(0.0)
            continue
        hyp = normalise(str(transcripts.get(c.clip_id, {}).get("transcript", "")))
        correct = sum(1 for s in c.entity_spans if normalise(s["text"]) in hyp)
        per_clip.append(correct / len(c.entity_spans))

    arr = np.array([np.nan if v is None else v for v in per_clip])
    return float(np.nanmean(arr)), per_clip


def compute_entity_accuracy_domain_vocab(
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float | None]]:
    """Compute entity accuracy restricted to domain vocabulary terms."""
    vocab_norm = [normalise(t) for t in DOMAIN_VOCAB]
    total_correct = 0
    total_present = 0
    per_clip: list[float | None] = []

    for c in clips:
        ref = normalise(c.reference_text)
        hyp = normalise(str(transcripts.get(c.clip_id, {}).get("transcript", "")))
        present_terms = [t for t in vocab_norm if t in ref]
        if len(present_terms) == 0:
            per_clip.append(None)
            continue
        correct = sum(1 for t in present_terms if t in hyp)
        per_clip.append(correct / len(present_terms))
        total_correct += correct
        total_present += len(present_terms)

    agg = total_correct / total_present if total_present > 0 else 0.0
    return agg, per_clip


def compute_metrics_for_interval(
    label: str,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compute all metrics for a single model × interval combination."""
    wer, wer_per = compute_wer(clips, transcripts)
    ea, ea_per = compute_entity_accuracy(clips, transcripts)
    ea_dv, ea_dv_per = compute_entity_accuracy_domain_vocab(clips, transcripts)

    lats = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    ttfds = [
        float(r["ttfd_seconds"]) for r in transcripts.values() if r.get("ttfd_seconds") is not None
    ]

    lat_p50 = float(np.percentile(lats, 50)) if lats else 0.0
    lat_p95 = float(np.percentile(lats, 95)) if lats else 0.0
    ttfd_p50 = float(np.percentile(ttfds, 50)) if ttfds else 0.0
    ttfd_p95 = float(np.percentile(ttfds, 95)) if ttfds else 0.0

    print(
        f"  {label}: WER={wer:.4f} EA={ea:.4f} EA-DV={ea_dv:.4f} "
        f"lat_p50={lat_p50:.3f}s ttfd_p50={ttfd_p50:.3f}s"
    )

    return {
        "label": label,
        "wer": round(wer, 6),
        "entity_accuracy": round(ea, 6),
        "entity_accuracy_domain_vocab": round(ea_dv, 6),
        "latency_p50_seconds": round(lat_p50, 4),
        "latency_p95_seconds": round(lat_p95, 4),
        "ttfd_p50_seconds": round(ttfd_p50, 4),
        "ttfd_p95_seconds": round(ttfd_p95, 4),
        "n_clips": len(transcripts),
    }


def load_jsonl_by_clip_id(path: Path) -> dict[str, dict[str, Any]]:
    """Load a JSONL file into a dict keyed by clip_id."""
    result: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            result[r["clip_id"]] = r
    return result
