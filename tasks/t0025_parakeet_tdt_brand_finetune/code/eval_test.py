"""Evaluate parakeet-tdt checkpoint on test set (47 clips).

Reports: overall WER + brand-word accuracy (Rezolve, Brain Commerce, etc.)

Usage:
    python tasks/t0025_parakeet_tdt_brand_finetune/code/eval_test.py \
        --model /mnt/finetune-checkpoints-t0025/parakeet-tdt-finetuned-best.nemo

    # compare base model vs finetuned:
    python eval_test.py --model nvidia/parakeet-tdt-0.6b-v3 --label base
    python eval_test.py --model /mnt/.../best.nemo           --label finetuned
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parents[1]
TEST_MANIFEST = TASK_DIR / "data" / "test" / "manifest.jsonl"

BRAND_TERMS = [
    "rezolve",
    "brainpowa",
    "brain commerce",
    "brain checkout",
    "purchase suite",
    "groupby",
    "bluedot",
    "visenze",
    "smartpay",
    "subsquid",
    "crownpeak",
]


def wer(ref: str, hyp: str) -> float:
    r, h = ref.lower().split(), hyp.lower().split()
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = (
                d[i - 1][j - 1]
                if r[i - 1] == h[j - 1]
                else 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])
            )
    return d[len(r)][len(h)] / max(len(r), 1)


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower().strip())


def brand_hit(text: str, term: str) -> bool:
    t = f" {norm(text)} "
    return f" {term} " in t or t.strip().startswith(term)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help=".nemo path or HF model name")
    parser.add_argument("--test", type=Path, default=TEST_MANIFEST)
    parser.add_argument("--label", default="model")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    import nemo.collections.asr as nemo_asr

    if args.model.endswith(".nemo") or Path(args.model).exists():
        model = nemo_asr.models.EncDecTDTBPEModel.restore_from(args.model)
    else:
        model = nemo_asr.models.EncDecTDTBPEModel.from_pretrained(args.model)
    model.eval()

    with args.test.open() as fh:
        clips = [json.loads(line) for line in fh if line.strip()]
    audio_paths = [c["audio_filepath"] for c in clips]
    refs = [c["text"] for c in clips]

    print(f"Transcribing {len(clips)} clips with [{args.label}] ...")
    hyps = model.transcribe(audio_paths, batch_size=args.batch_size)

    # WER
    total_wer = sum(wer(r, h) for r, h in zip(refs, hyps, strict=True)) / len(refs)

    # Brand accuracy per term
    print(f"\n{'=' * 55}")
    print(f"[{args.label}]  test clips: {len(clips)}")
    print(f"WER (avg)    : {total_wer:.3f}")
    print("\nBrand-word accuracy:")
    for term in BRAND_TERMS:
        term_clips = [(r, h) for r, h in zip(refs, hyps, strict=True) if brand_hit(r, term)]
        if not term_clips:
            continue
        correct = sum(1 for r, h in term_clips if brand_hit(h, term))
        print(f"  {term:<20} {correct}/{len(term_clips)}  ({100 * correct / len(term_clips):.0f}%)")

    # Per-clip detail
    print(f"\n{'─' * 55}")
    for c, ref, hyp in zip(clips, refs, hyps, strict=True):
        w = wer(ref, hyp)
        flag = "✓" if w < 0.1 else ("~" if w < 0.4 else "✗")
        print(f"{flag} [{c.get('source', '?')[:3]}] {Path(c['audio_filepath']).name}")
        print(f"  REF: {ref}")
        print(f"  HYP: {hyp}")

    print(f"\n[{args.label}] WER={total_wer:.3f}")


if __name__ == "__main__":
    main()
