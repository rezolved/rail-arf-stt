"""Run the 2x2 GPU-PB biasing x parakeet-unified fine-tuning ablation (t0026).

Four arms on the same `clean_eval_v2` clips, one shared scoring function (REQ-1, REQ-5, REQ-6):

    A — base model,      no boosting tree (`malsd_batch`)
    B — base model,      boosting tree (`malsd_batch` + GPU-PB, t0024's selected cell)
    C — fine-tuned model, no boosting tree (`malsd_batch`)
    D — fine-tuned model, boosting tree (`malsd_batch` + GPU-PB, t0024's selected cell)

All four arms use `malsd_batch` decoding (REQ-2) so the decoder strategy is never confounded with
the biasing effect. The biasing cell is read from `paths.PARETO_UNIFIED_JSON` and asserted to match
the frontier-selected cell rather than re-swept (REQ-3).

Usage (GPU machine, conda env `stt`, `CUDA_VISIBLE_DEVICES=1` set in the shell environment):
    python -u tasks/t0026_biasing_on_finetune_ablation/code/run_ablation.py
    python -u tasks/t0026_biasing_on_finetune_ablation/code/run_ablation.py --limit 2 --arms A,B,C,D
"""

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tasks.t0026_biasing_on_finetune_ablation.code import audio_io, boosting, paths, scoring
from tasks.t0026_biasing_on_finetune_ablation.code.constants import SELECTED_CELL

BASE_MODEL_ID: str = "nvidia/parakeet-unified-en-0.6b"
ARM_IDS: list[str] = ["A", "B", "C", "D"]
ARM_USES_FINETUNED: dict[str, bool] = {"A": False, "B": False, "C": True, "D": True}
ARM_USES_BOOST: dict[str, bool] = {"A": False, "B": True, "C": False, "D": True}

# Source: tasks/t0024_biasing_pareto_and_ft_biasing_ablation/results/pareto_unified.json
EXPECTED_SELECTED_CELL: dict[str, float] = {
    "context_score": 3.0,
    "depth_scaling": 0.5,
    "alpha": 1.5,
    "brand_exact_rate": 0.6,
    "neutral_wer": 0.087,
}


@dataclass(frozen=True, slots=True)
class ManifestRow:
    clip_id: str
    ref: str
    source: str
    audio_filepath: Path


@dataclass(frozen=True, slots=True)
class PredictionRecord:
    clip_id: str
    ref: str
    hyp: str
    brand: str | None
    label: str | None
    wer: float | None
    latency_seconds: float
    source: str


@dataclass(frozen=True, slots=True)
class ArmMetrics:
    brand_exact_rate_overall: float | None
    brand_exact_rate_rezolve: float | None
    brand_exact_rate_brainpowa: float | None
    neutral_wer: float | None
    overall_wer: float | None
    avg_inference_time_per_item_seconds: float
    n_clips: int
    n_brand_clips: int
    n_neutral_clips: int
    successful_requests: int
    total_requests: int


@dataclass(frozen=True, slots=True)
class ArmRunOutput:
    records: list[PredictionRecord]
    metrics: ArmMetrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--arms", type=str, default="A,B,C,D")
    parser.add_argument("--checkpoint", type=Path, default=paths.FT_CHECKPOINT)
    return parser.parse_args()


def load_manifest_rows(*, manifest_path: Path, limit: int | None) -> list[ManifestRow]:
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    raw_rows = [json.loads(line) for line in lines if line.strip() != ""]
    if limit is not None:
        raw_rows = raw_rows[:limit]
    return [
        ManifestRow(
            clip_id=row["clip_id"],
            ref=row["text"],
            source=row["source"],
            audio_filepath=Path(row["audio_filepath"]),
        )
        for row in raw_rows
    ]


def _assert_selected_cell_unchanged() -> None:
    data: dict[str, Any] = json.loads(paths.PARETO_UNIFIED_JSON.read_text(encoding="utf-8"))
    actual = data["selected_cell"]
    assert actual == EXPECTED_SELECTED_CELL, (
        f"t0024's selected_cell has drifted from this task's hardcoded copy: "
        f"expected {EXPECTED_SELECTED_CELL}, found {actual}"
    )
    assert {
        "context_score": actual["context_score"],
        "depth_scaling": actual["depth_scaling"],
        "alpha": actual["alpha"],
    } == SELECTED_CELL, "constants.SELECTED_CELL does not match pareto_unified.json's selected_cell"


def _load_audio_clips(rows: list[ManifestRow]) -> list[dict[str, Any]]:
    """Load audio once, shared across all four arms (REQ-1: identical inputs per arm)."""
    loaded: list[dict[str, Any]] = []
    for row in rows:
        try:
            audio = audio_io.load_audio(row.audio_filepath)
        except Exception as exc:  # noqa: BLE001 - record failure, do not crash the whole run
            print(f"  [WARN] failed to decode audio for {row.clip_id}: {exc}")
            audio = None
        loaded.append(
            {"clip_id": row.clip_id, "ref": row.ref, "source": row.source, "audio": audio}
        )
    return loaded


def _load_model(*, arm: str, checkpoint_path: Path) -> Any:
    import nemo.collections.asr as nemo_asr
    import torch

    if ARM_USES_FINETUNED[arm]:
        model = nemo_asr.models.ASRModel.restore_from(str(checkpoint_path))
    else:
        model = nemo_asr.models.ASRModel.from_pretrained(BASE_MODEL_ID)
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
    return model


def run_arm(
    *,
    arm: str,
    loaded_clips: list[dict[str, Any]],
    checkpoint_path: Path,
    phrases: list[str],
) -> ArmRunOutput:
    print(f"\n=== Arm {arm} (finetuned={ARM_USES_FINETUNED[arm]}, boost={ARM_USES_BOOST[arm]}) ===")
    total_requests = len(loaded_clips)
    decodable = [c for c in loaded_clips if c["audio"] is not None]

    model = _load_model(arm=arm, checkpoint_path=checkpoint_path)
    if ARM_USES_BOOST[arm]:
        boosting.apply_malsd_boost(
            model,
            phrases,
            alpha=SELECTED_CELL["alpha"],
            context_score=SELECTED_CELL["context_score"],
            depth_scaling=SELECTED_CELL["depth_scaling"],
        )
    else:
        boosting.apply_malsd_no_boost(model)

    start = time.perf_counter()
    try:
        hyps = audio_io.transcribe(model, decodable)
        transcribe_failed = False
    except Exception as exc:  # noqa: BLE001 - a whole-arm transcribe failure is a real result
        print(f"  [ERROR] arm {arm} transcribe() raised: {exc}")
        hyps = [""] * len(decodable)
        transcribe_failed = True
    elapsed = time.perf_counter() - start
    # ponytail: batched transcribe() gives one wall-clock time for the whole arm, not per clip;
    # every record in this arm is stamped with the same average, not a true per-clip latency.
    avg_latency = elapsed / len(decodable) if len(decodable) > 0 else 0.0

    hyp_by_clip_id: dict[str, str] = {c["clip_id"]: h for c, h in zip(decodable, hyps, strict=True)}
    successful_requests = 0 if transcribe_failed else len(decodable)

    records: list[PredictionRecord] = []
    for clip in loaded_clips:
        hyp = hyp_by_clip_id.get(clip["clip_id"], "")
        brand = scoring.brand_in_ref(clip["ref"])
        label = scoring.label_brand(hyp, brand) if brand is not None else None
        w = scoring.wer(clip["ref"], hyp) if clip["audio"] is not None else None
        records.append(
            PredictionRecord(
                clip_id=clip["clip_id"],
                ref=clip["ref"],
                hyp=hyp,
                brand=brand,
                label=label,
                wer=w,
                latency_seconds=round(avg_latency, 4),
                source=clip["source"],
            )
        )

    metrics = _aggregate_metrics(
        records=records,
        avg_inference_time_per_item_seconds=avg_latency,
        successful_requests=successful_requests,
        total_requests=total_requests,
    )
    print(
        f"  brand_exact_rate overall={metrics.brand_exact_rate_overall} "
        f"neutral_wer={metrics.neutral_wer} overall_wer={metrics.overall_wer} "
        f"successful={metrics.successful_requests}/{metrics.total_requests}"
    )
    return ArmRunOutput(records=records, metrics=metrics)


def _rate(*, numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _mean(values: list[float]) -> float | None:
    return None if len(values) == 0 else sum(values) / len(values)


def _aggregate_metrics(
    *,
    records: list[PredictionRecord],
    avg_inference_time_per_item_seconds: float,
    successful_requests: int,
    total_requests: int,
) -> ArmMetrics:
    brand_records = [r for r in records if r.brand is not None]
    neutral_records = [r for r in records if r.brand is None]
    rezolve_records = [r for r in brand_records if r.brand == "Rezolve"]
    brainpowa_records = [r for r in brand_records if r.brand == "brainpowa"]

    overall_wers = [r.wer for r in records if r.wer is not None]
    neutral_wers = [r.wer for r in neutral_records if r.wer is not None]

    return ArmMetrics(
        brand_exact_rate_overall=_rate(
            numerator=sum(1 for r in brand_records if r.label == "EXACT"),
            denominator=len(brand_records),
        ),
        brand_exact_rate_rezolve=_rate(
            numerator=sum(1 for r in rezolve_records if r.label == "EXACT"),
            denominator=len(rezolve_records),
        ),
        brand_exact_rate_brainpowa=_rate(
            numerator=sum(1 for r in brainpowa_records if r.label == "EXACT"),
            denominator=len(brainpowa_records),
        ),
        neutral_wer=_mean(neutral_wers),
        overall_wer=_mean(overall_wers),
        avg_inference_time_per_item_seconds=avg_inference_time_per_item_seconds,
        n_clips=len(records),
        n_brand_clips=len(brand_records),
        n_neutral_clips=len(neutral_records),
        successful_requests=successful_requests,
        total_requests=total_requests,
    )


def _metrics_to_dict(metrics: ArmMetrics) -> dict[str, Any]:
    return {
        "brand_exact_rate": {
            "overall": metrics.brand_exact_rate_overall,
            "rezolve": metrics.brand_exact_rate_rezolve,
            "brainpowa": metrics.brand_exact_rate_brainpowa,
        },
        "neutral_wer": metrics.neutral_wer,
        "overall_wer": metrics.overall_wer,
        "avg_inference_time_per_item_seconds": metrics.avg_inference_time_per_item_seconds,
        "n_clips": metrics.n_clips,
        "n_brand_clips": metrics.n_brand_clips,
        "n_neutral_clips": metrics.n_neutral_clips,
        "successful_requests": metrics.successful_requests,
        "total_requests": metrics.total_requests,
    }


def main() -> None:
    args = parse_args()
    requested_arms = args.arms.split(",")
    for arm in requested_arms:
        assert arm in ARM_IDS, f"unknown arm {arm!r}, expected one of {ARM_IDS}"

    _assert_selected_cell_unchanged()

    rows = load_manifest_rows(manifest_path=paths.FIXED_MANIFEST, limit=args.limit)
    print(f"Loaded {len(rows)} manifest rows (limit={args.limit})")
    loaded_clips = _load_audio_clips(rows)
    phrases = scoring.build_phrase_list()
    print(f"Phrase list: {len(phrases)} terms")

    paths.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_metrics: dict[str, dict[str, Any]] = {}
    for arm in requested_arms:
        arm_output = run_arm(
            arm=arm,
            loaded_clips=loaded_clips,
            checkpoint_path=args.checkpoint,
            phrases=phrases,
        )
        out_path = paths.RESULTS_DIR / f"arm_{arm.lower()}_predictions.jsonl"
        with out_path.open("w", encoding="utf-8") as out:
            for record in arm_output.records:
                out.write(
                    json.dumps(
                        {
                            "clip_id": record.clip_id,
                            "ref": record.ref,
                            "hyp": record.hyp,
                            "brand": record.brand,
                            "label": record.label,
                            "wer": record.wer,
                            "latency_seconds": record.latency_seconds,
                            "source": record.source,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"  Wrote {out_path}")
        all_metrics[arm] = _metrics_to_dict(arm_output.metrics)

    metrics_path = paths.RESULTS_DIR / "ablation_metrics.json"
    if args.limit is None and set(requested_arms) == set(ARM_IDS):
        # Full run over all four arms: write the canonical metrics file.
        metrics_path.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
        print(f"\nWrote {metrics_path}")
    else:
        print(
            f"\nValidation run (limit={args.limit}, arms={requested_arms}) — not overwriting "
            f"{metrics_path}"
        )


if __name__ == "__main__":
    main()
