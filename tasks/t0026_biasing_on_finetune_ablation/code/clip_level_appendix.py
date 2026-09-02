"""Clip-level mechanism appendix: clips fixed by exactly one lever (REQ-13 data source).

Selects every brand-containing clip where exactly one of arm B (biasing) or arm C (fine-tuning) is
`EXACT` and the other is not, and records all four arms' hypotheses/labels so the per-clip mechanism
is inspectable rather than inferred from aggregates alone.

Usage (local, no GPU needed, after `run_ablation.py`'s full run has written all four
`results/arm_*_predictions.jsonl` files):
    python -u tasks/t0026_biasing_on_finetune_ablation/code/clip_level_appendix.py
"""

import json
from typing import Any

from tasks.t0026_biasing_on_finetune_ablation.code import paths


def _load_predictions(arm: str) -> dict[str, dict[str, Any]]:
    path = paths.RESULTS_DIR / f"arm_{arm.lower()}_predictions.jsonl"
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "":
            continue
        row = json.loads(line)
        records[row["clip_id"]] = row
    return records


def main() -> None:
    predictions_by_arm = {arm: _load_predictions(arm) for arm in ("A", "B", "C", "D")}
    brand_clip_ids = sorted(
        clip_id for clip_id, row in predictions_by_arm["A"].items() if row.get("brand") is not None
    )

    appendix: list[dict[str, Any]] = []
    for clip_id in brand_clip_ids:
        b_correct = predictions_by_arm["B"][clip_id].get("label") == "EXACT"
        c_correct = predictions_by_arm["C"][clip_id].get("label") == "EXACT"
        if b_correct == c_correct:
            continue  # not "fixed by exactly one lever"
        appendix.append(
            {
                "clip_id": clip_id,
                "ref": predictions_by_arm["A"][clip_id]["ref"],
                "hyp_a": predictions_by_arm["A"][clip_id]["hyp"],
                "hyp_b": predictions_by_arm["B"][clip_id]["hyp"],
                "hyp_c": predictions_by_arm["C"][clip_id]["hyp"],
                "hyp_d": predictions_by_arm["D"][clip_id]["hyp"],
                "label_a": predictions_by_arm["A"][clip_id]["label"],
                "label_b": predictions_by_arm["B"][clip_id]["label"],
                "label_c": predictions_by_arm["C"][clip_id]["label"],
                "label_d": predictions_by_arm["D"][clip_id]["label"],
            }
        )

    out_path = paths.RESULTS_DIR / "clip_level_appendix.json"
    out_path.write_text(json.dumps(appendix, indent=2), encoding="utf-8")
    print(f"{len(appendix)}/{len(brand_clip_ids)} brand clips fixed by exactly one lever (B xor C)")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
