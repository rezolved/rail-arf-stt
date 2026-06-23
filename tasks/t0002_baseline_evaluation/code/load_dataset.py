"""Load the gold-92 benchmark dataset.

Uses ground_truth.jsonl as the canonical reference (NOT gold_set.jsonl, which has
normalisation inconsistencies). Also loads accent_group from gold_set.jsonl for
stratification.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tasks.t0002_baseline_evaluation.code.paths import (
    GOLD92_AUDIO,
    GOLD_SET_JSONL,
    GROUND_TRUTH_JSONL,
)

CYRILLIC_ANOMALY_CLIP = "error_en_0005"


@dataclass(frozen=True, slots=True)
class GoldClip:
    """A single gold-92 benchmark clip with reference annotation."""

    clip_id: str
    reference_text: str
    entity_spans: list[dict[str, Any]]
    accent_group: str
    audio_path: Path


def _load_gold_set_accent_groups(gold_set_path: Path) -> dict[str, str]:
    """Load accent group mapping from gold_set.jsonl."""
    accent_groups: dict[str, str] = {}
    with gold_set_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            clip_id: str = record["clip_id"]
            source: str = record.get("source", "unknown")
            accent_groups[clip_id] = source
    return accent_groups


def _infer_entity_spans(reference_text: str, clip_id: str) -> list[dict[str, Any]]:
    """Infer entity spans from reference text using known domain entity patterns.

    This is a heuristic approach: since ground_truth.jsonl does not include
    entity_spans, we detect known entity patterns from the Rezolve IR domain.
    """
    import re

    spans: list[dict[str, Any]] = []
    text = reference_text

    # Known brand/product entities in the Rezolve IR domain
    entity_patterns: list[tuple[str, str]] = [
        (r"\bRezolve AI\b", "brand"),
        (r"\bRezolve\b", "brand"),
        (r"\bbrainpowa\b", "product"),
        (r"\bBrain Commerce\b", "product"),
        (r"\bBrainpowa\b", "product"),
        (r"\bBrain Power\b", "product"),
        (r"\bSalesforce Commerce Cloud\b", "product"),
        (r"\bShopify Plus\b", "product"),
        (r"\bAdobe Commerce\b", "product"),
        (r"\bAdobe\b", "brand"),
        (r"\bShopify\b", "brand"),
        (r"\bSalesforce\b", "brand"),
        (r"\bAmazon\b", "brand"),
        (r"\bGoogle\b", "brand"),
        (r"\bMicrosoft\b", "brand"),
        (r"\b20-F\b", "ir_term"),
        (r"\b10-K\b", "ir_term"),
        (r"\bSEO\b", "ir_term"),
        (r"\bAPI\b", "ir_term"),
        (r"\bAI\b", "ir_term"),
        (r"\bROI\b", "ir_term"),
        (r"\bKPI\b", "ir_term"),
    ]

    for pattern, entity_type in entity_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            spans.append(
                {
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "type": entity_type,
                }
            )

    return spans


def load_gold92(
    *,
    ground_truth_path: Path = GROUND_TRUTH_JSONL,
    gold_set_path: Path = GOLD_SET_JSONL,
    audio_dir: Path = GOLD92_AUDIO,
) -> list[GoldClip]:
    """Load all 93 gold-92 benchmark clips.

    Uses ground_truth.jsonl as canonical reference. Loads accent_group from
    gold_set.jsonl for stratification. Infers entity_spans from reference text
    using domain heuristics (ground_truth.jsonl does not include explicit spans).

    Returns:
        List of GoldClip objects, one per clip, sorted by clip_id.
    """
    # Load accent groups from gold_set.jsonl for stratification
    accent_groups = _load_gold_set_accent_groups(gold_set_path=gold_set_path)

    clips: list[GoldClip] = []
    with ground_truth_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record: dict[str, Any] = json.loads(line)
            clip_id: str = record["clip_id"]
            reference_text: str = record["ground_truth"]

            if clip_id == CYRILLIC_ANOMALY_CLIP:
                warnings.warn(
                    f"Clip {clip_id} has Cyrillic ground truth '{reference_text}' — "
                    "known annotation error. Including in run with anomaly flag.",
                    stacklevel=2,
                )

            entity_spans = _infer_entity_spans(reference_text=reference_text, clip_id=clip_id)
            accent_group = accent_groups.get(clip_id, "unknown")
            audio_path = audio_dir / f"{clip_id}.wav"

            clips.append(
                GoldClip(
                    clip_id=clip_id,
                    reference_text=reference_text,
                    entity_spans=entity_spans,
                    accent_group=accent_group,
                    audio_path=audio_path,
                )
            )

    clips.sort(key=lambda c: c.clip_id)
    return clips


if __name__ == "__main__":
    loaded = load_gold92()
    print(f"Loaded {len(loaded)} clips")
    assert len(loaded) == 93, f"Expected 93, got {len(loaded)}"  # noqa: S101
    print("Sample clip:", loaded[0])
    print("Accent groups:", {c.accent_group for c in loaded})
    print("PASS")
