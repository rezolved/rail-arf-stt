"""Full-93-clip run with expanded phrase list on top of the winning (baseline) hyperparam config.

The hyperparam sweep (run_hyperparam_sweep.py + run_hyperparam_sweep_narrow.py,
results/hyperparam_sweep.jsonl + hyperparam_sweep_narrow.jsonl) was a null result: near-baseline
alpha/depth_scaling values move nothing, and far-from-baseline values wreck WER. So the config
carried forward is the production default (alpha=1.0, depth_scaling=2.0). This script re-runs
gold-92 with that config plus phrase_expansion.EXTRA_SURFACE_VARIANTS added to the boosted phrase
list (t0019 Step 4 / REQ-3), and compares against the baseline predictions already saved at
data/hyperparam_top2/alpha1.0_depth2.0/predictions.jsonl (from run_top2_full.py).

Usage (remote, conda env stt active, PYTHONPATH=repo root):
    python -u tasks/t0019_parakeet_biasing_improvement/code/run_phrase_expansion_full.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tasks.t0017_parakeet_biasing_buffer_replacement.code.compute_and_write_metrics import (
    compute_entity_accuracy,
    compute_entity_accuracy_domain_vocab,
    compute_wer,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.constants import (
    DOMAIN_VOCAB,
    HF_PARAKEET_UNIFIED,
    PARAKEET_BOOSTING_ALPHA,
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_DEPTH_SCALING,
    PARAKEET_USE_BPE_DROPOUT,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import BOH_PATTERNS_CSV
from tasks.t0017_parakeet_biasing_buffer_replacement.code.run_parakeet_buffer_sweep import (
    expand_casing_variants,
    load_audio_float32,
    load_gold92_clips,
    transcribe_buffer,
)
from tasks.t0019_parakeet_biasing_improvement.code.phrase_expansion import (
    expand_with_surface_variants,
)

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data" / "best_hyperparam_phrase_expansion"
RESULTS_DIR = TASK_DIR / "results"
BASELINE_PREDICTIONS = (
    TASK_DIR / "data" / "hyperparam_top2" / "alpha1.0_depth2.0" / "predictions.jsonl"
)


def apply_boosting(model: Any, phrases: tuple[str, ...]) -> None:
    import copy as copy_module

    from omegaconf import OmegaConf, open_dict

    cfg = copy_module.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree.key_phrases_list", list(phrases), force_add=True)
    OmegaConf.update(
        cfg, "greedy.boosting_tree.context_score", PARAKEET_CONTEXT_SCORE, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.depth_scaling", PARAKEET_DEPTH_SCALING, force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.use_bpe_dropout", PARAKEET_USE_BPE_DROPOUT, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", PARAKEET_BOOSTING_ALPHA, force_add=True)
    model.change_decoding_strategy(cfg)


def score_predictions(path: Path) -> dict[str, Any]:
    transcripts: dict[str, dict[str, Any]] = {}
    reference: dict[str, dict[str, Any]] = {}
    clip_ids: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            clip_id = row["clip_id"]
            clip_ids.append(clip_id)
            transcripts[clip_id] = row
            reference[clip_id] = {"reference_text": row["reference_text"]}
    return {
        "wer": compute_wer(clip_ids, transcripts, reference),
        "ea": compute_entity_accuracy(clip_ids, transcripts, reference),
        "ea_dv": compute_entity_accuracy_domain_vocab(clip_ids, transcripts, reference),
        "n_clips": len(clip_ids),
    }


def main() -> None:
    import torch
    from nemo.collections.asr.models import ASRModel

    boh_patterns = load_boh_patterns(BOH_PATTERNS_CSV)
    detector = HallucinationDetector(boh_patterns)

    clips = load_gold92_clips(limit=None)
    print(f"Full run: {len(clips)} clips")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {HF_PARAKEET_UNIFIED} ...")
    model = ASRModel.from_pretrained(model_name=HF_PARAKEET_UNIFIED, map_location=device)
    model = model.to(device)
    model.eval()

    warmup_audio = load_audio_float32(clips[0]["audio_path"])
    for _ in range(3):
        transcribe_buffer(model, warmup_audio)

    base_phrases = expand_casing_variants(DOMAIN_VOCAB)
    expanded_phrases = expand_with_surface_variants(base_phrases)
    print(
        f"Phrases: base={len(base_phrases)} expanded={len(expanded_phrases)} "
        f"(+{len(expanded_phrases) - len(base_phrases)} surface variants)"
    )
    apply_boosting(model, expanded_phrases)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "predictions.jsonl"
    rows: list[dict[str, Any]] = []
    errors = 0
    for i, clip_info in enumerate(clips):
        try:
            audio_f32 = load_audio_float32(clip_info["audio_path"])
            text = transcribe_buffer(model, audio_f32)
            reference_text = clip_info["reference_text"]
            is_halluc = detector.is_hallucination(transcript=text, reference_text=reference_text)
            rows.append(
                {
                    "clip_id": clip_info["clip_id"],
                    "transcript": text,
                    "reference_text": reference_text,
                    "is_empty": len(text.strip()) == 0,
                    "is_hallucination": is_halluc,
                }
            )
        except Exception as exc:
            print(f"ERROR on {clip_info['clip_id']}: {exc}")
            errors += 1
        if (i + 1) % 20 == 0:
            print(f"  [{i + 1}/{len(clips)}]")

    success_rate = len(rows) / len(clips) if clips else 0.0
    if success_rate < 0.80:
        raise RuntimeError(f"Rejection: success rate {success_rate:.1%} < 80%")

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Saved {len(rows)} rows -> {out_path} (errors={errors})")

    expansion_scores = score_predictions(out_path)
    print("\n=== SUMMARY ===")
    print(
        f"  phrase-expansion: WER={expansion_scores['wer']:.3f} EA={expansion_scores['ea']:.3f} "
        f"EA-DV={expansion_scores['ea_dv']:.3f} n={expansion_scores['n_clips']}"
    )

    if BASELINE_PREDICTIONS.exists():
        baseline_scores = score_predictions(BASELINE_PREDICTIONS)
        print(
            f"  baseline (no expansion): WER={baseline_scores['wer']:.3f} "
            f"EA={baseline_scores['ea']:.3f} EA-DV={baseline_scores['ea_dv']:.3f} "
            f"n={baseline_scores['n_clips']}"
        )
        print(
            f"  delta: WER={expansion_scores['wer'] - baseline_scores['wer']:+.3f} "
            f"EA-DV={expansion_scores['ea_dv'] - baseline_scores['ea_dv']:+.3f}"
        )
    else:
        print(f"  WARNING: baseline predictions not found at {BASELINE_PREDICTIONS}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "phrase_expansion_full93.json"
    with out_json.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "phrase_expansion": expansion_scores,
                "baseline": score_predictions(BASELINE_PREDICTIONS)
                if BASELINE_PREDICTIONS.exists()
                else None,
                "n_base_phrases": len(base_phrases),
                "n_expanded_phrases": len(expanded_phrases),
            },
            fh,
            indent=2,
        )
    print(f"Saved -> {out_json}")


if __name__ == "__main__":
    main()
