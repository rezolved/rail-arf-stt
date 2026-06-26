"""FunASR Paraformer benchmark on gold-92.

Run 1: Paraformer-large English — batch, no biasing.
Run 2: SeACo-Paraformer-large English — contextual hotword biasing
       (same 31-term domain vocab as t0007).

FunASR API:
    model = AutoModel(model=MODEL_ID, device="cuda")
    result = model.generate(input=audio_path, hotword="kw1 kw2 ...")  # hotword="" for no biasing

Hotwords: space-separated string. SeACo attends to hotword tokens during decoding (deep biasing).
Models auto-downloaded from ModelScope to ~/.cache/modelscope on first run.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from tasks.t0010_funasr_paraformer_benchmark.code.constants import (
    DOMAIN_VOCAB,
    MODEL_ID,
    WARMUP_CLIPS,
)
from tasks.t0010_funasr_paraformer_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0010_funasr_paraformer_benchmark.code.paths import (
    PARAFORMER_BATCH_TRANSCRIPTS,
    PARAFORMER_BIASED_TRANSCRIPTS,
)


def build_hotword_string(vocab: list[str]) -> str:
    return " ".join(vocab)


def extract_text(result: list[dict]) -> str:
    if not result:
        return ""
    return result[0].get("text", "").strip()


def run_variant(
    model,
    clips: list,
    output_path: Path,
    *,
    hotword: str = "",
    label: str,
) -> None:

    print(f"Warmup ({WARMUP_CLIPS} clips) ...")
    import contextlib

    for clip in clips[:WARMUP_CLIPS]:
        if clip.audio_path.exists():
            with contextlib.suppress(Exception):
                model.generate(input=str(clip.audio_path), cache={}, hotword=hotword, is_final=True)

    results: list[dict] = []
    available = [c for c in clips if c.audio_path.exists()]
    for i, clip in enumerate(available):
        t0 = time.perf_counter()
        try:
            raw = model.generate(
                input=str(clip.audio_path), cache={}, hotword=hotword, is_final=True
            )
            latency = time.perf_counter() - t0
            hypothesis = extract_text(raw)
        except Exception as exc:
            latency = time.perf_counter() - t0
            print(
                f"  WARNING: clip {clip.clip_id} failed "
                f"({type(exc).__name__}: {exc}) — empty hypothesis"
            )
            hypothesis = ""

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"  WARNING: anomaly clip {clip.clip_id}")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: '{hypothesis[:60]}' ({latency:.3f}s)"
            )

    success = sum(1 for r in results if r["hypothesis"])
    total = len(results)
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: {success}/{total} non-empty.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"  Done ({label}): {success}/{total} → {output_path.name}")


def main() -> None:
    import torch
    from funasr import AutoModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    clips = load_gold92()
    hotword_str = build_hotword_string(DOMAIN_VOCAB)
    print(f"Hotword string ({len(DOMAIN_VOCAB)} terms): '{hotword_str[:80]}...'")

    print(f"\nLoading {MODEL_ID} (shared for both runs) ...")
    model = AutoModel(model=MODEL_ID, device=device, disable_update=True)

    # Run 1: batch, no biasing
    print("\n=== Run 1: Paraformer-large — batch, no biasing ===")
    run_variant(
        model,
        clips,
        PARAFORMER_BATCH_TRANSCRIPTS,
        hotword="",
        label="batch",
    )

    # Run 2: hotword biasing (same model, hotword controls shallow-fusion)
    print("\n=== Run 2: Paraformer-large — hotword biasing ===")
    run_variant(
        model,
        clips,
        PARAFORMER_BIASED_TRANSCRIPTS,
        hotword=hotword_str,
        label="biased",
    )

    print("\nAll runs complete.")


if __name__ == "__main__":
    main()
