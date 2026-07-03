"""Full-93-clip confirmation run for the top-2 hyperparam configs from Step 3 screening (t0019).

Reuses t0017's transcription/boosting helpers and official metric functions (WER, EA, EA-DV) so
numbers are directly comparable to the t0017 biased baseline (WER 11.0%, EA-DV 34.8%).

Usage (remote, conda env stt active, PYTHONPATH=repo root):
    python -u tasks/t0019_parakeet_biasing_improvement/code/run_top2_full.py
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
    PARAKEET_CONTEXT_SCORE,
    PARAKEET_USE_BPE_DROPOUT,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.hallucination_detector import (
    HallucinationDetector,
    load_boh_patterns,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.paths import (
    BOH_PATTERNS_CSV,
)
from tasks.t0017_parakeet_biasing_buffer_replacement.code.run_parakeet_buffer_sweep import (
    expand_casing_variants,
    load_audio_float32,
    load_gold92_clips,
    transcribe_buffer,
)

# Top-2 configs selected from results/hyperparam_sweep.jsonl 20-clip screening (2026-07-02).
TOP2_CONFIGS: list[dict[str, float]] = [
    {"alpha": 3.0, "depth_scaling": 3.0},
    {"alpha": 2.0, "depth_scaling": 4.0},
]
BASELINE_CONFIG: dict[str, float] = {"alpha": 1.0, "depth_scaling": 2.0}

TASK_DIR = Path(__file__).parents[1]
DATA_DIR = TASK_DIR / "data" / "hyperparam_top2"
RESULTS_DIR = TASK_DIR / "results"


def config_slug(config: dict[str, float]) -> str:
    return f"alpha{config['alpha']:.1f}_depth{config['depth_scaling']:.1f}"


def apply_config(model: Any, phrases: tuple[str, ...], config: dict[str, float]) -> None:
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
        cfg, "greedy.boosting_tree.depth_scaling", config["depth_scaling"], force_add=True
    )
    OmegaConf.update(
        cfg, "greedy.boosting_tree.use_bpe_dropout", PARAKEET_USE_BPE_DROPOUT, force_add=True
    )
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", config["alpha"], force_add=True)
    model.change_decoding_strategy(cfg)


def run_full_config(
    model: Any,
    clips: list[dict[str, Any]],
    config: dict[str, float],
    phrases: tuple[str, ...],
    detector: HallucinationDetector,
) -> Path:
    apply_config(model, phrases, config)
    slug = config_slug(config)
    out_dir = DATA_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "predictions.jsonl"

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
            print(f"  [{i + 1}/{len(clips)}] {slug}")

    success_rate = len(rows) / len(clips) if clips else 0.0
    if success_rate < 0.80:
        raise RuntimeError(f"Rejection: {slug} success rate {success_rate:.1%} < 80%")

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Saved {len(rows)} rows -> {out_path} (errors={errors})")
    return out_path


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

    phrases = expand_casing_variants(DOMAIN_VOCAB)

    all_scores: dict[str, Any] = {}

    print("\n=== BASELINE (alpha=1.0, depth_scaling=2.0) — reproduction control ===")
    baseline_path = run_full_config(model, clips, BASELINE_CONFIG, phrases, detector)
    all_scores["baseline"] = {**score_predictions(baseline_path), **BASELINE_CONFIG}

    for config in TOP2_CONFIGS:
        slug = config_slug(config)
        print(f"\n=== {slug} ===")
        path = run_full_config(model, clips, config, phrases, detector)
        all_scores[slug] = {**score_predictions(path), **config}

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RESULTS_DIR / "hyperparam_top2_full93.json"
    with out_json.open("w", encoding="utf-8") as fh:
        json.dump(all_scores, fh, indent=2)

    print("\n=== SUMMARY (full 93 clips) ===")
    for name, scores in all_scores.items():
        print(
            f"  {name}: WER={scores['wer']:.3f} EA={scores['ea']:.3f} "
            f"EA-DV={scores['ea_dv']:.3f} n={scores['n_clips']}"
        )
    print(f"\nSaved -> {out_json}")


if __name__ == "__main__":
    main()
