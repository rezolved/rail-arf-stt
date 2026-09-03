"""Fix `clean_eval_v2/manifest.jsonl`'s absolute macOS audio paths for this machine (REQ-4).

`tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_v2/manifest.jsonl` stores
`audio_filepath` as absolute paths from the annotator's laptop
(`/Users/margotiamanova/Desktop/...`). This script rewrites each `audio_filepath` to point at
`paths.T0021_AUDIO_DIR / <basename>` — resolved fresh on whichever machine this script runs on —
and writes the corrected 91 rows to this task's own gitignored `data/` directory. `t0021`'s original
manifest and DVC-tracked audio are never modified.

Usage:
    python -u tasks/t0026_biasing_on_finetune_ablation/code/fix_manifest.py
"""

import json
from pathlib import Path
from typing import Any

from tasks.t0026_biasing_on_finetune_ablation.code import paths

EXPECTED_ROW_COUNT: int = 91


def _fix_row(row: dict[str, Any]) -> dict[str, Any]:
    original_name = Path(row["audio_filepath"]).name
    fixed_row = dict(row)
    fixed_row["audio_filepath"] = str(paths.T0021_AUDIO_DIR / original_name)
    return fixed_row


def main() -> None:
    lines = paths.T0021_MANIFEST.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, Any]] = [json.loads(line) for line in lines if line.strip() != ""]
    fixed_rows: list[dict[str, Any]] = [_fix_row(row) for row in rows]

    paths.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with paths.FIXED_MANIFEST.open("w", encoding="utf-8") as out:
        for row in fixed_rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    assert len(fixed_rows) == EXPECTED_ROW_COUNT, (
        f"expected {EXPECTED_ROW_COUNT} rows, got {len(fixed_rows)}"
    )
    missing = [
        row["audio_filepath"] for row in fixed_rows if not Path(row["audio_filepath"]).exists()
    ]
    assert len(missing) == 0, f"{len(missing)} audio_filepath(s) do not resolve: {missing[:5]}"

    print(f"Fixed manifest: {len(fixed_rows)}/{EXPECTED_ROW_COUNT} rows resolve to existing files")


if __name__ == "__main__":
    main()
