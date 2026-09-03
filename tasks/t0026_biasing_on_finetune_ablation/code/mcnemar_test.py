"""Paired McNemar test on per-clip brand correctness for B-vs-D and C-vs-D (REQ-9).

With n=43 brand-containing clips, aggregate percentage-point deltas between arms are not enough to
separate signal from noise (`task_description.md` "Key questions"). This computes the exact McNemar
test over the two most decision-relevant pairs — does adding biasing to the fine-tuned model (C->D)
or does adding fine-tuning to the biased base model (B->D) change which brand clips are transcribed
`EXACT`.

Usage (local, no GPU needed, after `run_ablation.py`'s full run has written all four
`results/arm_*_predictions.jsonl` files):
    python -u tasks/t0026_biasing_on_finetune_ablation/code/mcnemar_test.py
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scipy.stats import binomtest

from tasks.t0026_biasing_on_finetune_ablation.code import paths


@dataclass(frozen=True, slots=True)
class PairedTestResult:
    b: int
    c: int
    n_discordant: int
    p_value: float
    note: str | None


def _load_predictions(arm: str) -> dict[str, dict[str, Any]]:
    path = paths.RESULTS_DIR / f"arm_{arm.lower()}_predictions.jsonl"
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "":
            continue
        row = json.loads(line)
        records[row["clip_id"]] = row
    return records


def _is_correct(row: dict[str, Any]) -> bool:
    return row.get("label") == "EXACT"


def paired_mcnemar(
    *,
    first_arm_records: dict[str, dict[str, Any]],
    second_arm_records: dict[str, dict[str, Any]],
) -> PairedTestResult:
    """`b` = correct in first arm only, `c` = correct in second arm only (McNemar convention)."""
    shared_brand_clip_ids = sorted(
        clip_id
        for clip_id, row in first_arm_records.items()
        if row.get("brand") is not None and clip_id in second_arm_records
    )
    b_count = 0
    c_count = 0
    for clip_id in shared_brand_clip_ids:
        first_correct = _is_correct(first_arm_records[clip_id])
        second_correct = _is_correct(second_arm_records[clip_id])
        if first_correct and not second_correct:
            b_count += 1
        elif second_correct and not first_correct:
            c_count += 1

    n_discordant = b_count + c_count
    if n_discordant == 0:
        return PairedTestResult(
            b=b_count,
            c=c_count,
            n_discordant=0,
            p_value=1.0,
            note=(
                "No discordant pairs — both arms agree on every brand clip; test is uninformative."
            ),
        )
    result = binomtest(min(b_count, c_count), n_discordant, p=0.5, alternative="two-sided")
    return PairedTestResult(
        b=b_count,
        c=c_count,
        n_discordant=n_discordant,
        p_value=float(result.pvalue),
        note=None,
    )


def _result_to_dict(result: PairedTestResult) -> dict[str, Any]:
    return {
        "b": result.b,
        "c": result.c,
        "n_discordant": result.n_discordant,
        "p_value": result.p_value,
        "note": result.note,
    }


def main() -> None:
    predictions_by_arm = {arm: _load_predictions(arm) for arm in ("B", "C", "D")}

    b_vs_d = paired_mcnemar(
        first_arm_records=predictions_by_arm["B"],
        second_arm_records=predictions_by_arm["D"],
    )
    c_vs_d = paired_mcnemar(
        first_arm_records=predictions_by_arm["C"],
        second_arm_records=predictions_by_arm["D"],
    )

    out: dict[str, Any] = {
        "b_vs_d": _result_to_dict(b_vs_d),
        "c_vs_d": _result_to_dict(c_vs_d),
    }
    out_path: Path = paths.RESULTS_DIR / "mcnemar_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"b_vs_d: {out['b_vs_d']}")
    print(f"c_vs_d: {out['c_vs_d']}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
