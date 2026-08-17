"""Build a brand-word n-gram LM for shallow fusion with parakeet-tdt.

What this does:
  1. Collects text corpus: train manifest sentences + synthetic brand phrases
  2. Writes corpus.txt
  3. Calls KenLM (lmplz) to build a 3-gram ARPA file
  4. Converts ARPA → binary trie (fast at inference)

The binary trie is passed to NeMo's beam decoder via:
    model.change_decoding_strategy({
        "strategy": "beam",
        "beam": {
            "beam_size": 8,
            "ngram_lm_model": ".../brand.binary",
            "ngram_lm_alpha": 0.3,   # tune this
        }
    })

Usage:
    pip install kenlm  # or: apt install kenlm
    python tasks/t0025_parakeet_tdt_brand_finetune/code/build_brand_lm.py
    python tasks/t0025_parakeet_tdt_brand_finetune/code/build_brand_lm.py \
        --order 4 --alpha-test 0.2 0.3 0.5
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = TASK_DIR / "data"
LM_DIR = TASK_DIR / "lm"

BRAND_TERMS: list[str] = [
    "Rezolve",
    "brainpowa",
    "Brain Commerce",
    "Brain Checkout",
    "Purchase Suite",
    "GroupBy",
    "Bluedot",
    "ViSenze",
    "Smartpay",
    "Subsquid",
    "CrownPeak",
    "Dan Wagner",
    "Arthur Yao",
    "Richard Burchill",
    "Crispin Lowery",
    "Salman Ahmad",
    "Sauvik Banerjjee",
    "Mark Turner",
    "Peter Vesco",
    "Urmee Khan",
    "Anthony Sharp",
    "David Wright",
    "Steve Perry",
    "Derek Smith",
    "Justin King",
    "Christian Angermayer",
]

# Synthetic phrase templates — inject brand terms into common question patterns
TEMPLATES: list[str] = [
    "What is {term}?",
    "Tell me about {term}.",
    "How does {term} work?",
    "What does {term} do?",
    "Who is {term}?",
    "Can you explain {term}?",
    "Tell me more about {term}.",
    "What are {term} features?",
    "How does {term} help retailers?",
    "What is the {term} solution?",
    "{term} is an AI platform.",
    "{term} powers ecommerce search.",
    "I want to know about {term}.",
    "Can I get a demo of {term}?",
    "{term} integrates with existing systems.",
]


def load_manifest_texts(manifest: Path) -> list[str]:
    if not manifest.exists():
        return []
    with manifest.open() as fh:
        return [json.loads(line)["text"] for line in fh if line.strip()]


def build_corpus(train_texts: list[str]) -> list[str]:
    lines: list[str] = []

    # Real training sentences (highest weight — repeat 3×)
    lines.extend(train_texts * 3)

    # Synthetic brand phrases from templates
    for term in BRAND_TERMS:
        for tpl in TEMPLATES:
            lines.append(tpl.format(term=term))
        # Also bare term on its own line (teaches unigram/bigram)
        lines.append(term)
        lines.append(term.lower())

    return lines


def run(cmd: list[str], *, stdin_text: str | None = None) -> None:
    result = subprocess.run(
        cmd,
        input=stdin_text,
        text=True,
        capture_output=False,
    )
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=DATA_DIR / "train" / "manifest.jsonl")
    parser.add_argument("--out-dir", type=Path, default=LM_DIR)
    parser.add_argument("--order", type=int, default=3, help="n-gram order (3 or 4)")
    parser.add_argument(
        "--alpha-test",
        nargs="+",
        type=float,
        default=[0.2, 0.3, 0.5],
        help="LM alpha values to print reminder for eval grid search",
    )
    args = parser.parse_args()

    # Check kenlm available
    lmplz = shutil.which("lmplz")
    build_binary = shutil.which("build_binary")
    if lmplz is None:
        print("ERROR: lmplz not found. Install: pip install kenlm  or  apt install kenlm")
        print("       On gpu-azure: pip install https://github.com/kpu/kenlm/archive/master.zip")
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = args.out_dir / "corpus.txt"
    arpa_path = args.out_dir / f"brand_{args.order}gram.arpa"
    binary_path = args.out_dir / f"brand_{args.order}gram.binary"

    # Build corpus
    train_texts = load_manifest_texts(args.train)
    lines = build_corpus(train_texts)
    corpus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Corpus  : {len(lines)} lines → {corpus_path}")

    # Build ARPA
    print(f"Building {args.order}-gram ARPA ...")
    with corpus_path.open() as corpus_fh:
        result = subprocess.run(
            [lmplz, "-o", str(args.order), "--discount_fallback"],
            stdin=corpus_fh,
            stdout=arpa_path.open("w"),
            text=True,
        )
    if result.returncode != 0:
        sys.exit(result.returncode)
    print(f"ARPA    : {arpa_path}")

    # Build binary trie
    if build_binary is not None:
        print("Building binary trie ...")
        run([build_binary, "trie", str(arpa_path), str(binary_path)])
        print(f"Binary  : {binary_path}")
    else:
        print("WARNING: build_binary not found, skip binary. Use ARPA directly.")
        binary_path = arpa_path

    # Print eval grid reminder
    print(f"\n{'=' * 55}")
    print("Next step — eval with shallow fusion:")
    print(f"  LM model: {binary_path}")
    for alpha in args.alpha_test:
        print(
            f"  python eval_test.py --model best.nemo --lm {binary_path}"
            f" --lm-alpha {alpha} --label ft+biasing-a{alpha}"
        )
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
