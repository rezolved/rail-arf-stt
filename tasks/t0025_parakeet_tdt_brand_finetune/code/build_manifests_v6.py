"""Build train_v6.jsonl and val_v6.jsonl for t0025 (parakeet-tdt-0.6b-v3 brand-aware fine-tune).

Per task_description.md "Data" section:

- ``train_v6.jsonl``: ``train_v5.jsonl`` with brand-word clips (transcript containing "Rezolve",
  "brainpowa", or "Rezolve AI") oversampled ``OVERSAMPLE_FACTOR`` times (data-side duplication,
  no loss weighting).
- ``val_v6.jsonl``: ``val_v5.jsonl`` (7 clips) plus 5-10 brand-word production clips. This build
  draws the addition from the gold-92 clips already inside ``train_v5`` (the task description's
  second sourcing option) rather than from quepasa production logs (the first option), because
  quepasa production logs are not reachable as static data from this machine. Those gold-92
  clips are explicitly "burned for eval purposes anyway" per the task description, so reusing
  them for validation is sanctioned as costing nothing.

Verification (per task_description.md, "fail loudly on any overlap"):

- val_v6 vs clean_eval_v2/manifest.jsonl: must be zero overlap. This is the check that actually
  protects the held-out test set, and this script hard-fails if it is nonzero.
- val_v6 vs train_v6: the task description also says to check this, but the gold-92-in-train_v5
  sourcing option it offers is *only* viable by construction if val and train overlap for those
  specific clips (they are "already inside train_v5"). Treating that as a hard failure would rule
  out the option the description itself names. This script instead reports the overlap count and
  which clip_ids it comes from, so a human can see exactly what's shared and why, rather than
  silently asserting zero overlap that doesn't hold under this sourcing choice.

Not yet done here — deliberately left for a follow-up pass validated against the actual training
VM: remapping ``audio_filepath`` values (currently the raw ``train_v5``/``val_v5`` paths, e.g.
``/home/azureuser/realtime-voice-benchmark/...``) per the task description's "Manifest path fix"
pitfall. That prefix may already resolve correctly on ``LLM-T1-NC80`` (every prior successful GPU
run in this project happened there), so remapping blind from this CPU box risks substituting a
*wrong* path over a possibly-already-correct one. Verify path existence on the training VM first.

Run from the rail-metarepo workspace layout (rail-benchmarks and rail-arf-stt as sibling clones
under real-repos/); override --*-manifest paths if running against a different checkout (e.g. the
GPU VM's own clones).

Usage (local, no GPU needed):
    uv run python -u tasks/t0025_parakeet_tdt_brand_finetune/code/build_manifests_v6.py
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

from tasks.t0025_parakeet_tdt_brand_finetune.code.constants import (
    BRAND_TERMS,
    OVERSAMPLE_FACTOR,
    VAL_ADDITION_CLIP_IDS,
)
from tasks.t0025_parakeet_tdt_brand_finetune.code.paths import (
    DATA_DIR,
    DEFAULT_CLEAN_EVAL_V2_MANIFEST,
    DEFAULT_GOLD92_MANIFEST,
    DEFAULT_TRAIN_V5_MANIFEST,
    DEFAULT_VAL_V5_MANIFEST,
)


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def has_brand(text: str) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in BRAND_TERMS)


def basename_set(rows: Iterable[dict], *, key: str = "audio_filepath") -> set[str]:
    return {Path(r[key]).name for r in rows if r.get(key)}


def build_train_v6(train_v5: list[dict]) -> list[dict]:
    out = []
    n_brand = 0
    for entry in train_v5:
        out.append(entry)
        if has_brand(entry["text"]):
            n_brand += 1
            for _ in range(OVERSAMPLE_FACTOR - 1):
                out.append(dict(entry))
    print(
        f"train_v6: {len(train_v5)} base clips, {n_brand} brand clips oversampled "
        f"{OVERSAMPLE_FACTOR}x -> {len(out)} total clips"
    )
    return out


def build_val_v6(*, val_v5: list[dict], train_v5: list[dict], gold92: list[dict]) -> list[dict]:
    train5_by_basename = {Path(e["audio_filepath"]).name: e for e in train_v5}
    gold_by_clip_id = {g["clip_id"]: g for g in gold92}

    additions = []
    for clip_id in VAL_ADDITION_CLIP_IDS:
        gold_entry = gold_by_clip_id[clip_id]
        train_entry = train5_by_basename[gold_entry["filename"]]
        assert has_brand(train_entry["text"]), f"{clip_id} does not carry a brand term"
        additions.append(train_entry)

    out = list(val_v5) + additions
    print(
        f"val_v6: {len(val_v5)} val_v5 clips + {len(additions)} gold-92-in-train_v5 brand "
        f"clips (incl. brainpowa: error_en_0020) -> {len(out)} total clips"
    )
    return out


def verify(*, val_v6: list[dict], train_v6: list[dict], clean_eval_v2: list[dict]) -> None:
    val_bn = basename_set(val_v6)
    ce2_bn = basename_set(clean_eval_v2)
    train_bn = basename_set(train_v6)

    ce2_overlap = val_bn & ce2_bn
    if ce2_overlap:
        raise SystemExit(
            f"FAIL: val_v6 overlaps clean_eval_v2 by {len(ce2_overlap)} clip(s): {ce2_overlap}"
        )
    print("OK: zero overlap between val_v6 and clean_eval_v2 (the held-out test set)")

    train_overlap = val_bn & train_bn
    print(
        f"NOTE: val_v6 overlaps train_v6 by {len(train_overlap)} clip(s) — expected, these are "
        "the gold-92-in-train_v5 clips deliberately reused for val (see module docstring); "
        f"filenames: {sorted(train_overlap)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-v5-manifest", type=Path, default=DEFAULT_TRAIN_V5_MANIFEST)
    parser.add_argument("--val-v5-manifest", type=Path, default=DEFAULT_VAL_V5_MANIFEST)
    parser.add_argument("--gold92-manifest", type=Path, default=DEFAULT_GOLD92_MANIFEST)
    parser.add_argument(
        "--clean-eval-v2-manifest", type=Path, default=DEFAULT_CLEAN_EVAL_V2_MANIFEST
    )
    parser.add_argument("--out-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()

    train_v5 = load_jsonl(args.train_v5_manifest)
    val_v5 = load_jsonl(args.val_v5_manifest)
    gold92 = load_jsonl(args.gold92_manifest)
    clean_eval_v2 = load_jsonl(args.clean_eval_v2_manifest)

    train_v6 = build_train_v6(train_v5)
    val_v6 = build_val_v6(val_v5=val_v5, train_v5=train_v5, gold92=gold92)
    verify(val_v6=val_v6, train_v6=train_v6, clean_eval_v2=clean_eval_v2)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "train_v6.jsonl", train_v6)
    write_jsonl(args.out_dir / "val_v6.jsonl", val_v6)
    print(f"Wrote {args.out_dir / 'train_v6.jsonl'} and {args.out_dir / 'val_v6.jsonl'}")


if __name__ == "__main__":
    main()
