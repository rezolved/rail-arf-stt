"""Generate predictions-gold92.jsonl for the whisper-turbo-gold92 asset.

Reads whisper_turbo_transcripts.json and gold-92 annotations, then writes
per-instance prediction records matching the whisper-large-v3-gold92 schema.
"""

from __future__ import annotations

import json
import string
from typing import Any

import jiwer

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import (
    WHISPER_TURBO_PREDICTIONS_DIR,
    WHISPER_TURBO_TRANSCRIPTS,
)

OUTPUT_JSONL = WHISPER_TURBO_PREDICTIONS_DIR / "files" / "predictions-gold92.jsonl"


def normalise(text: str) -> str:
    """Lowercase and strip punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def compute_per_clip_wer(reference: str, hypothesis: str) -> float:
    """Compute per-clip WER after normalisation."""
    ref = normalise(reference)
    hyp = normalise(hypothesis)
    result = jiwer.process_words([ref], [hyp])
    ref_words = result.hits + result.substitutions + result.deletions
    errors = result.substitutions + result.deletions + result.insertions
    return errors / ref_words if ref_words > 0 else 0.0


def main() -> None:
    """Write per-instance predictions JSONL for whisper-turbo-gold92."""
    if not WHISPER_TURBO_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Whisper turbo transcripts not found at {WHISPER_TURBO_TRANSCRIPTS}. "
            "Run code/run_whisper_turbo.py first."
        )

    with WHISPER_TURBO_TRANSCRIPTS.open(encoding="utf-8") as fh:
        raw_transcripts: list[dict[str, Any]] = json.load(fh)
    transcripts = {r["clip_id"]: r for r in raw_transcripts}

    clips = load_gold92()

    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for clip in clips:
        hyp_raw = str(transcripts.get(clip.clip_id, {}).get("hypothesis", ""))
        latency = float(transcripts.get(clip.clip_id, {}).get("latency_seconds", 0.0))
        is_anomaly = clip.clip_id == CYRILLIC_ANOMALY_CLIP

        # Per-clip WER
        wer = compute_per_clip_wer(clip.reference_text, hyp_raw)

        # Entity accuracy (all-or-nothing, None for anomaly)
        entity_accuracy: float | None
        entity_spans_predicted: list[dict[str, Any]] = []
        if is_anomaly:
            entity_accuracy = None
        elif len(clip.entity_spans) == 0:
            entity_accuracy = 0.0
        else:
            hyp_norm = normalise(hyp_raw)
            correct = 0
            for span in clip.entity_spans:
                span_text: str = span["text"]
                found = normalise(span_text) in hyp_norm
                entity_spans_predicted.append(
                    {"text": span_text, "type": span.get("type", ""), "found": found}
                )
                if found:
                    correct += 1
            entity_accuracy = correct / len(clip.entity_spans)

        # Build entity_spans_predicted if not already built (anomaly or no spans)
        if not entity_spans_predicted and not is_anomaly:
            for span in clip.entity_spans:
                span_text = span["text"]
                entity_spans_predicted.append(
                    {"text": span_text, "type": span.get("type", ""), "found": False}
                )

        records.append(
            {
                "clip_id": clip.clip_id,
                "reference": clip.reference_text,
                "hypothesis": hyp_raw,
                "accent_group": clip.accent_group,
                "entity_spans_reference": list(clip.entity_spans),
                "entity_spans_predicted": entity_spans_predicted,
                "entity_accuracy": (
                    round(entity_accuracy, 6) if entity_accuracy is not None else None
                ),
                "wer": round(wer, 6),
                "latency_seconds": round(latency, 4),
                "anomaly_flag": "cyrillic_ground_truth" if is_anomaly else None,
            }
        )

    with OUTPUT_JSONL.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} records to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()
