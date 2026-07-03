"""Post-hoc string-replacement feasibility check for hard biasing misses (t0019 Step 5 / REQ-4).

Boosting (hyperparam sweep + phrase expansion, both null results — see
results/hyperparam_sweep*.jsonl and results/phrase_expansion_full93.json) cannot fix Parakeet's
dominant confusion: "Rezolve" is consistently transcribed as "Resolve" regardless of GPU-PB
config. This script estimates the ceiling of a deterministic post-decode string-replacement pass
(the `stt_replacements` channel already used elsewhere in brainpowa-realtime-api, separate from
GPU-PB boosting) applied on top of the Step 4 transcripts. This is a feasibility measurement only —
it does not wire into the real production routing pipeline.

Usage (local, no GPU needed — pure text post-processing):
    uv run python -u tasks/t0019_parakeet_biasing_improvement/code/posthoc_replacement_check.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tasks.t0017_parakeet_biasing_buffer_replacement.code.compute_and_write_metrics import (
    compute_entity_accuracy,
    compute_entity_accuracy_domain_vocab,
    compute_wer,
)

TASK_DIR = Path(__file__).parents[1]
INPUT_PREDICTIONS = TASK_DIR / "data" / "best_hyperparam_phrase_expansion" / "predictions.jsonl"
OUTPUT_PREDICTIONS_DIR = TASK_DIR / "data" / "posthoc_check"
RESULTS_DIR = TASK_DIR / "results"
OUTPUT_JSON = RESULTS_DIR / "posthoc_replacement_check.json"

# (pattern, replacement) applied case-insensitively, whole-word, longest-first.
REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bResolve\s+A\.?I\.?\b", "Rezolve Ai"),
    (r"\bResolve\b", "Rezolve"),
    (r"\bbrain\s+power\b", "brainpowa"),
    (r"\bGentic\s+commerce\b", "agentic commerce"),
]


def apply_replacements(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in REPLACEMENTS:
        text, n = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
        count += n
    return text, count


def load_predictions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def score(rows: list[dict[str, Any]], *, transcript_key: str) -> dict[str, Any]:
    clip_ids = [r["clip_id"] for r in rows]
    transcripts = {r["clip_id"]: {"transcript": r[transcript_key]} for r in rows}
    reference = {r["clip_id"]: {"reference_text": r["reference_text"]} for r in rows}
    return {
        "wer": compute_wer(clip_ids, transcripts, reference),
        "ea": compute_entity_accuracy(clip_ids, transcripts, reference),
        "ea_dv": compute_entity_accuracy_domain_vocab(clip_ids, transcripts, reference),
        "n_clips": len(clip_ids),
    }


def main() -> None:
    if not INPUT_PREDICTIONS.exists():
        raise FileNotFoundError(f"Missing Step 4 predictions at {INPUT_PREDICTIONS}")

    rows = load_predictions(INPUT_PREDICTIONS)
    print(f"Loaded {len(rows)} predictions from {INPUT_PREDICTIONS}")

    total_replacements = 0
    for row in rows:
        replaced_text, n = apply_replacements(row["transcript"])
        row["transcript_posthoc"] = replaced_text
        total_replacements += n

    before = score(rows, transcript_key="transcript")
    after = score(rows, transcript_key="transcript_posthoc")

    print(f"\nBEFORE:  WER={before['wer']:.3f} EA={before['ea']:.3f} EA-DV={before['ea_dv']:.3f}")
    print(f"AFTER:   WER={after['wer']:.3f} EA={after['ea']:.3f} EA-DV={after['ea_dv']:.3f}")
    print(f"Replacements applied: {total_replacements} across {len(rows)} clips")

    OUTPUT_PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_PREDICTIONS_DIR / "predictions.jsonl"
    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Saved -> {out_path}")

    result = {
        "ea_dv_before": before["ea_dv"],
        "ea_dv_after": after["ea_dv"],
        "wer_before": before["wer"],
        "wer_after": after["wer"],
        "ea_before": before["ea"],
        "ea_after": after["ea"],
        "n_replacements_applied": total_replacements,
        "n_clips": before["n_clips"],
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"Saved -> {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
