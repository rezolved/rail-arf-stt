"""False positive test: does boosting convert verb 'resolve' → 'Rezolve'?

Runs unified model (malsd_batch, recommended params) on 15 synthetic clips
where ground truth is the verb "to resolve" in neutral sentences.
Reports how many clips get falsely transcribed as "Rezolve".
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (  # noqa: E402
    DOMAIN_VOCAB,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "false_positive"
AUDIO_DIR = DATA_DIR / "audio"
MANIFEST = DATA_DIR / "manifest.jsonl"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSONL = RESULTS_DIR / "false_positive.jsonl"
OUTPUT_MD = RESULTS_DIR / "false_positive.md"

UNIFIED_MODEL = "nvidia/parakeet-unified-en-0.6b"

# Recommended params from validation
BOOST_PARAMS = {
    "context_score": 3.0,
    "depth_scaling": 0.5,
    "alpha": 1.5,
}

REZOLVE_PATTERN = re.compile(r"\brezolve\b", re.IGNORECASE)


def _expand_casing_variants(phrases: list[str]) -> list[str]:
    """Match prod behavior: add lowercase and Capitalized variants."""
    result: list[str] = []
    for p in phrases:
        result.append(p)
        result.append(p.lower())
        result.append(p.capitalize())
    return list(dict.fromkeys(result))


def load_manifest() -> list[dict]:
    clips = []
    with MANIFEST.open() as f:
        for line in f:
            line = line.strip()
            if line:
                item = json.loads(line)
                item["audio_filepath"] = str(AUDIO_DIR / item["audio_filepath"])
                clips.append(item)
    return clips


def _set_malsd(model: Any, phrases: list[str] | None) -> None:
    import copy

    from omegaconf import OmegaConf, open_dict  # type: ignore[import]

    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "malsd_batch"
    OmegaConf.update(cfg, "beam.beam_size", 4, force_add=True)
    OmegaConf.update(cfg, "beam.return_best_hypothesis", True, force_add=True)
    if phrases:
        cs = BOOST_PARAMS["context_score"]
        ds = BOOST_PARAMS["depth_scaling"]
        al = BOOST_PARAMS["alpha"]
        OmegaConf.update(cfg, "beam.boosting_tree.key_phrases_list", phrases, force_add=True)
        OmegaConf.update(cfg, "beam.boosting_tree.context_score", cs, force_add=True)
        OmegaConf.update(cfg, "beam.boosting_tree.depth_scaling", ds, force_add=True)
        OmegaConf.update(cfg, "beam.boosting_tree_alpha", al, force_add=True)
    model.change_decoding_strategy(cfg)


def run_config(
    model: Any,
    clips: list[dict],
    label: str,
    use_boost: bool,
) -> list[dict]:
    print(f"\n--- {label} ---")

    if use_boost:
        phrases = _expand_casing_variants(list(DOMAIN_VOCAB))
        cs = BOOST_PARAMS["context_score"]
        ds = BOOST_PARAMS["depth_scaling"]
        al = BOOST_PARAMS["alpha"]
        _set_malsd(model, phrases)
        print(f"  boost: cs={cs} ds={ds} alpha={al}  phrases={len(phrases)}")
    else:
        _set_malsd(model, None)
        print("  boost: OFF")

    # Patch missing validation_ds (None when loaded from pretrained with no dataset config)
    from omegaconf import OmegaConf, open_dict  # type: ignore[import]

    if model.cfg.get("validation_ds") is None:
        with open_dict(model.cfg):
            model.cfg.validation_ds = OmegaConf.create({})

    audio_paths = [c["audio_filepath"] for c in clips]
    outputs = model.transcribe(audio_paths, batch_size=8, verbose=False)

    def _to_str(t: Any) -> str:
        if hasattr(t, "text"):
            return str(t.text)
        if isinstance(t, list):
            return str(t[0].text if hasattr(t[0], "text") else t[0]) if t else ""
        return str(t)

    transcripts = [_to_str(t) for t in outputs]

    results = []
    for clip, transcript in zip(clips, transcripts, strict=False):
        is_fp = bool(REZOLVE_PATTERN.search(transcript))
        results.append(
            {
                "file": Path(clip["audio_filepath"]).name,
                "reference": clip["text"],
                "hypothesis": transcript,
                "false_positive": is_fp,
                "label": label,
            }
        )
        status = "FP!" if is_fp else "ok"
        print(f"  [{status}] {Path(clip['audio_filepath']).name}: {transcript!r}")

    return results


def main() -> None:
    import nemo.collections.asr as nemo_asr  # type: ignore[import]
    import torch  # type: ignore[import]

    clips = load_manifest()
    print(f"Loaded {len(clips)} clips from {MANIFEST}")

    print(f"\nLoading {UNIFIED_MODEL}...")
    model = nemo_asr.models.ASRModel.from_pretrained(UNIFIED_MODEL)
    model = model.cuda() if torch.cuda.is_available() else model
    model.eval()

    no_boost = run_config(model, clips, "unified malsd NO boost", use_boost=False)
    with_boost = run_config(model, clips, "unified malsd WITH boost", use_boost=True)

    # Save raw JSONL
    with OUTPUT_JSONL.open("w") as f:
        for row in no_boost + with_boost:
            f.write(json.dumps(row) + "\n")

    # Build markdown report
    no_boost_fp = sum(1 for r in no_boost if r["false_positive"])
    with_boost_fp = sum(1 for r in with_boost if r["false_positive"])
    n = len(clips)

    lines: list[str] = [
        "# t0023 — False Positive Test: verb 'resolve' → 'Rezolve'",
        "",
        f"**Clips:** {n} synthetic sentences, ground truth = verb 'to resolve'  ",
        "**Model:** parakeet-unified-en-0.6b  ",
        f"**Boost params:** cs={BOOST_PARAMS['context_score']} "
        f"ds={BOOST_PARAMS['depth_scaling']} alpha={BOOST_PARAMS['alpha']}",
        "",
        "## Summary",
        "",
        "| Config | False positives | Rate |",
        "|--------|----------------|------|",
        f"| malsd NO boost | {no_boost_fp}/{n} | {no_boost_fp / n:.0%} |",
        f"| malsd WITH boost | {with_boost_fp}/{n} | {with_boost_fp / n:.0%} |",
        "",
        "## Per-clip results",
        "",
        "| File | Reference | No-boost hypothesis | Boost hypothesis | FP? |",
        "|------|-----------|--------------------|-----------------|----|",
    ]

    no_boost_map = {r["file"]: r for r in no_boost}
    for row in with_boost:
        nb = no_boost_map[row["file"]]
        fp_mark = "**YES**" if row["false_positive"] else "no"
        ref = row["reference"]
        lines.append(
            f"| {row['file']} | {ref} | {nb['hypothesis']} | {row['hypothesis']} | {fp_mark} |"
        )

    lines += [
        "",
        "## Verdict",
        "",
    ]
    if with_boost_fp == 0:
        lines.append(
            "**No false positives.** Boosting does NOT convert verb 'resolve' → 'Rezolve'."
        )
    elif with_boost_fp <= 2:
        lines.append(
            f"**Low risk.** {with_boost_fp}/{n} clips falsely transcribed as 'Rezolve'. "
            "Acceptable — only synthetic TTS, real speech risk may differ."
        )
    else:
        lines.append(
            f"**HIGH RISK.** {with_boost_fp}/{n} clips falsely transcribed as 'Rezolve'. "
            "Consider reducing context_score or adding 'resolve' to a suppression list."
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n")
    print(f"\nSaved: {OUTPUT_JSONL}")
    print(f"Saved: {OUTPUT_MD}")

    print(f"\n=== RESULT: no-boost FP={no_boost_fp}/{n}  boost FP={with_boost_fp}/{n} ===")


if __name__ == "__main__":
    main()
