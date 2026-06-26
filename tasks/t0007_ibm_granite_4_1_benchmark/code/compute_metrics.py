"""Compute all metrics for IBM Granite Speech 4.1 2B variants and write results.

Reads transcripts from data/ and ground truth from t0001.
Compares vs Whisper large-v3 + initial_prompt baseline (t0004).
Writes results/metrics.json and data/analysis_output.json.
"""

from __future__ import annotations

import json
import string
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jiwer
import numpy as np
from scipy.stats import bootstrap  # type: ignore[attr-defined]

from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
)
from tasks.t0007_ibm_granite_4_1_benchmark.code.constants import DOMAIN_VOCAB
from tasks.t0007_ibm_granite_4_1_benchmark.code.load_dataset import load_gold92
from tasks.t0007_ibm_granite_4_1_benchmark.code.paths import (
    GRANITE_BATCH_TRANSCRIPTS,
    GRANITE_BIASED_TRANSCRIPTS,
    GRANITE_COMPILED_BIASED_TRANSCRIPTS,
    GRANITE_NAR_BIASED_TRANSCRIPTS,
    GRANITE_POSTPROC_BIASED_TRANSCRIPTS,
    RESULTS_DIR,
    T0004_WHISPER_BIASED_TRANSCRIPTS,
)

ANALYSIS_OUTPUT = Path(__file__).parents[1] / "data" / "analysis_output.json"
METRICS_JSON = RESULTS_DIR / "metrics.json"

BCa_N_RESAMPLES = 10_000
BCa_RANDOM_STATE = 42


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def bca_ci(
    per_clip_scores: np.ndarray,
    *,
    n_resamples: int = BCa_N_RESAMPLES,
    random_state: int = BCa_RANDOM_STATE,
) -> tuple[float, float]:
    try:
        result = bootstrap(
            (per_clip_scores,),
            statistic=np.mean,
            method="BCa",
            n_resamples=n_resamples,
            random_state=random_state,
        )
        low = float(result.confidence_interval.low)
        high = float(result.confidence_interval.high)
        if np.isnan(low) or np.isnan(high):
            raise ValueError("BCa NaN")
        return low, high
    except Exception:  # noqa: BLE001
        warnings.warn("BCa NaN — falling back to percentile", stacklevel=2)
        result = bootstrap(
            (per_clip_scores,),
            statistic=np.mean,
            method="percentile",
            n_resamples=n_resamples,
            random_state=random_state,
        )
        return float(result.confidence_interval.low), float(result.confidence_interval.high)


def load_transcripts(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        records: list[dict[str, Any]] = json.load(fh)
    return {r["clip_id"]: r for r in records}


def compute_per_clip_entity_accuracy(
    *,
    clip: GoldClip,
    hypothesis: str,
    is_anomaly: bool,
) -> float | None:
    if is_anomaly:
        return None
    if len(clip.entity_spans) == 0:
        return 0.0
    hyp_norm = normalise(hypothesis)
    correct = sum(1 for span in clip.entity_spans if normalise(span["text"]) in hyp_norm)
    return correct / len(clip.entity_spans)


def compute_wer_batch(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    references = [normalise(c.reference_text) for c in clips]
    hypotheses = [
        normalise(str(transcripts.get(c.clip_id, {}).get("hypothesis", ""))) for c in clips
    ]
    result = jiwer.process_words(references, hypotheses)
    total_ref = result.hits + result.substitutions + result.deletions
    numer = result.substitutions + result.deletions + result.insertions
    agg_wer = numer / total_ref if total_ref > 0 else 0.0
    per_clip: list[float] = []
    for ref, hyp in zip(references, hypotheses, strict=True):
        r = jiwer.process_words([ref], [hyp])
        n = r.hits + r.substitutions + r.deletions
        per_clip.append((r.substitutions + r.deletions + r.insertions) / n if n > 0 else 0.0)
    return agg_wer, per_clip


def compute_action_critical_wer(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    total_hits = total_subs = total_dels = 0
    per_clip: list[float] = []
    for clip in clips:
        if len(clip.entity_spans) == 0:
            per_clip.append(0.0)
            continue
        hyp_raw = str(transcripts.get(clip.clip_id, {}).get("hypothesis", ""))
        hyp_words = set(normalise(hyp_raw).split())
        hits = dels = subs = 0
        for span in clip.entity_spans:
            for word in normalise(span["text"]).split():
                if word in hyp_words:
                    hits += 1
                else:
                    dels += 1
        n = hits + dels + subs
        per_clip.append((dels + subs) / n if n > 0 else 0.0)
        total_hits += hits
        total_subs += subs
        total_dels += dels
    total_n = total_hits + total_subs + total_dels
    return (total_subs + total_dels) / total_n if total_n > 0 else 0.0, per_clip


def compute_intent_preservation(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    per_clip: list[float] = []
    for clip in clips:
        hyp = normalise(str(transcripts.get(clip.clip_id, {}).get("hypothesis", "")))
        if len(clip.entity_spans) == 0:
            per_clip.append(1.0)
            continue
        matched = any(normalise(s["text"]) in hyp for s in clip.entity_spans)
        per_clip.append(1.0 if matched else 0.0)
    return float(np.mean(per_clip)) if per_clip else 0.0, per_clip


def compute_latency_stats(transcripts: dict[str, dict[str, Any]]) -> dict[str, float]:
    latencies = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    return {
        "p50": float(np.percentile(latencies, 50)),
        "p95": float(np.percentile(latencies, 95)),
        "p99": float(np.percentile(latencies, 99)),
    }


def compute_entity_accuracy_domain_vocab(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float | None]]:
    vocab_norm = [normalise(t) for t in DOMAIN_VOCAB]
    per_clip: list[float | None] = []
    total_correct = total_occ = 0
    for clip in clips:
        ref_norm = normalise(clip.reference_text)
        hyp_norm = normalise(str(transcripts.get(clip.clip_id, {}).get("hypothesis", "")))
        terms_in_ref = [t for t in vocab_norm if t in ref_norm]
        if len(terms_in_ref) == 0:
            per_clip.append(None)
            continue
        correct = sum(1 for t in terms_in_ref if t in hyp_norm)
        per_clip.append(correct / len(terms_in_ref))
        total_correct += correct
        total_occ += len(terms_in_ref)
    agg = total_correct / total_occ if total_occ > 0 else 0.0
    return agg, per_clip


@dataclass(frozen=True, slots=True)
class SystemMetrics:
    variant_id: str
    label: str
    entity_accuracy: float
    entity_accuracy_ci: tuple[float, float]
    entity_per_clip: list[float | None]
    wer: float
    wer_ci: tuple[float, float]
    action_critical_wer: float
    action_critical_wer_ci: tuple[float, float]
    intent_preservation: float
    intent_preservation_ci: tuple[float, float]
    latency: dict[str, float]
    entity_accuracy_domain_vocab: float
    entity_accuracy_domain_vocab_ci: tuple[float, float]
    domain_vocab_per_clip: list[float | None]


def compute_system_metrics(
    *,
    variant_id: str,
    label: str,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    anomaly_clips: set[str],
) -> SystemMetrics:
    print(f"Computing metrics: {label} ...")

    entity_raw: list[float | None] = [
        compute_per_clip_entity_accuracy(
            clip=c,
            hypothesis=str(transcripts.get(c.clip_id, {}).get("hypothesis", "")),
            is_anomaly=c.clip_id in anomaly_clips,
        )
        for c in clips
    ]
    entity_np = np.array([np.nan if s is None else s for s in entity_raw], dtype=float)
    entity_acc = float(np.nanmean(entity_np))
    valid_entity = entity_np[~np.isnan(entity_np)]
    entity_ci = bca_ci(valid_entity)

    agg_wer, wer_per_clip = compute_wer_batch(clips=clips, transcripts=transcripts)
    wer_ci = bca_ci(np.array(wer_per_clip, dtype=float))

    acwer, acwer_per_clip = compute_action_critical_wer(clips=clips, transcripts=transcripts)
    acwer_ci = bca_ci(np.array(acwer_per_clip, dtype=float))

    intent, intent_per_clip = compute_intent_preservation(clips=clips, transcripts=transcripts)
    intent_ci = bca_ci(np.array(intent_per_clip, dtype=float))

    latency = compute_latency_stats(transcripts)

    dv_acc, dv_per_clip = compute_entity_accuracy_domain_vocab(clips=clips, transcripts=transcripts)
    dv_np = np.array([np.nan if s is None else s for s in dv_per_clip], dtype=float)
    valid_dv = dv_np[~np.isnan(dv_np)]
    dv_ci = bca_ci(valid_dv) if len(valid_dv) > 1 else (0.0, 0.0)

    print(f"  entity_accuracy:       {entity_acc:.4f} [{entity_ci[0]:.4f}-{entity_ci[1]:.4f}]")
    print(f"  entity_accuracy_dv:    {dv_acc:.4f} [{dv_ci[0]:.4f}-{dv_ci[1]:.4f}]")
    print(f"  wer:                   {agg_wer:.4f} [{wer_ci[0]:.4f}-{wer_ci[1]:.4f}]")
    print(f"  action_critical_wer:   {acwer:.4f}")
    print(f"  intent_preservation:   {intent:.4f}")
    lat = latency
    print(f"  latency p50/p95/p99:   {lat['p50']:.3f}s / {lat['p95']:.3f}s / {lat['p99']:.3f}s")

    return SystemMetrics(
        variant_id=variant_id,
        label=label,
        entity_accuracy=entity_acc,
        entity_accuracy_ci=entity_ci,
        entity_per_clip=entity_raw,
        wer=agg_wer,
        wer_ci=wer_ci,
        action_critical_wer=acwer,
        action_critical_wer_ci=acwer_ci,
        intent_preservation=intent,
        intent_preservation_ci=intent_ci,
        latency=latency,
        entity_accuracy_domain_vocab=dv_acc,
        entity_accuracy_domain_vocab_ci=dv_ci,
        domain_vocab_per_clip=dv_per_clip,
    )


def main() -> None:
    clips = load_gold92()
    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}

    for path, name in [
        (GRANITE_BATCH_TRANSCRIPTS, "granite batch"),
        (GRANITE_BIASED_TRANSCRIPTS, "granite biased"),
    ]:
        if not path.exists():
            raise RuntimeError(f"{name} transcripts not found at {path}. Run inference first.")

    batch_transcripts = load_transcripts(GRANITE_BATCH_TRANSCRIPTS)
    biased_transcripts = load_transcripts(GRANITE_BIASED_TRANSCRIPTS)

    whisper_transcripts: dict[str, dict[str, Any]] | None = None
    if T0004_WHISPER_BIASED_TRANSCRIPTS.exists():
        whisper_transcripts = load_transcripts(T0004_WHISPER_BIASED_TRANSCRIPTS)
    else:
        warnings.warn(
            f"t0004 Whisper baseline not found at {T0004_WHISPER_BIASED_TRANSCRIPTS}. Skipping.",
            stacklevel=2,
        )

    systems: list[SystemMetrics] = []

    systems.append(
        compute_system_metrics(
            variant_id="granite-4.1-2b-batch",
            label="Granite Speech 4.1 2B — batch (no biasing)",
            clips=clips,
            transcripts=batch_transcripts,
            anomaly_clips=anomaly_clips,
        )
    )

    systems.append(
        compute_system_metrics(
            variant_id="granite-4.1-2b-biased",
            label="Granite Speech 4.1 2B — keyword biased",
            clips=clips,
            transcripts=biased_transcripts,
            anomaly_clips=anomaly_clips,
        )
    )

    opt_variants = [
        (
            GRANITE_NAR_BIASED_TRANSCRIPTS,
            "granite-4.1-2b-nar-biased",
            "Granite 4.1 2B NAR — biased",
        ),
        (
            GRANITE_COMPILED_BIASED_TRANSCRIPTS,
            "granite-4.1-2b-compiled-biased",
            "Granite 4.1 2B + torch.compile — biased",
        ),
        (
            GRANITE_POSTPROC_BIASED_TRANSCRIPTS,
            "granite-4.1-2b-postproc-biased",
            "Granite 4.1 2B + ext-keywords + postproc",
        ),
    ]
    for opt_path, opt_id, opt_label in opt_variants:
        if opt_path.exists():
            systems.append(
                compute_system_metrics(
                    variant_id=opt_id,
                    label=opt_label,
                    clips=clips,
                    transcripts=load_transcripts(opt_path),
                    anomaly_clips=anomaly_clips,
                )
            )

    if whisper_transcripts is not None:
        systems.append(
            compute_system_metrics(
                variant_id="whisper-large-v3-biased",
                label="Whisper Large v3 + initial_prompt (t0004 baseline)",
                clips=clips,
                transcripts=whisper_transcripts,
                anomaly_clips=anomaly_clips,
            )
        )

    for sys in systems:
        if sys.wer > 0.6:
            raise RuntimeError(f"Rejection: {sys.label} WER={sys.wer:.3f} > 0.6.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    variants: list[dict[str, Any]] = []
    for sys in systems:
        variants.append(
            {
                "variant_id": sys.variant_id,
                "label": sys.label,
                "metrics": {
                    "entity_accuracy_gold92": round(sys.entity_accuracy, 6),
                    "entity_accuracy_domain_vocab": round(sys.entity_accuracy_domain_vocab, 6),
                    "wer_gold92": round(sys.wer, 6),
                    "action_critical_wer_gold92": round(sys.action_critical_wer, 6),
                    "intent_preservation_gold92": round(sys.intent_preservation, 6),
                    "latency_p50_seconds": round(sys.latency["p50"], 4),
                    "latency_p95_seconds": round(sys.latency["p95"], 4),
                    "latency_p99_seconds": round(sys.latency["p99"], 4),
                },
            }
        )

    batch_sys = next(s for s in systems if s.variant_id == "granite-4.1-2b-batch")
    biased_sys = next(s for s in systems if s.variant_id == "granite-4.1-2b-biased")
    biasing_gain = {
        "delta_wer": round(biased_sys.wer - batch_sys.wer, 6),
        "delta_entity_accuracy": round(biased_sys.entity_accuracy - batch_sys.entity_accuracy, 6),
        "delta_entity_accuracy_domain_vocab": round(
            biased_sys.entity_accuracy_domain_vocab - batch_sys.entity_accuracy_domain_vocab, 6
        ),
    }

    metrics_json: dict[str, Any] = {"variants": variants, "biasing_gain": biasing_gain}
    METRICS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    per_clip_analysis: list[dict[str, Any]] = []
    transcripts_map = {
        "granite-4.1-2b-batch": batch_transcripts,
        "granite-4.1-2b-biased": biased_transcripts,
    }
    if whisper_transcripts is not None:
        transcripts_map["whisper-large-v3-biased"] = whisper_transcripts
    for opt_path, opt_id, _opt_label in [
        (GRANITE_NAR_BIASED_TRANSCRIPTS, "granite-4.1-2b-nar-biased", ""),
        (GRANITE_COMPILED_BIASED_TRANSCRIPTS, "granite-4.1-2b-compiled-biased", ""),
        (GRANITE_POSTPROC_BIASED_TRANSCRIPTS, "granite-4.1-2b-postproc-biased", ""),
    ]:
        if opt_path.exists():
            transcripts_map[opt_id] = load_transcripts(opt_path)

    for i, clip in enumerate(clips):
        row: dict[str, Any] = {
            "clip_id": clip.clip_id,
            "accent_group": clip.accent_group,
            "reference": clip.reference_text,
        }
        for sys in systems:
            row[f"hypothesis_{sys.variant_id}"] = str(
                transcripts_map[sys.variant_id].get(clip.clip_id, {}).get("hypothesis", "")
            )
            row[f"entity_accuracy_{sys.variant_id}"] = sys.entity_per_clip[i]
            row[f"domain_vocab_accuracy_{sys.variant_id}"] = sys.domain_vocab_per_clip[i]
        per_clip_analysis.append(row)

    analysis_output: dict[str, Any] = {
        "per_clip_analysis": per_clip_analysis,
        "biasing_gain": biasing_gain,
        "bootstrap_config": {
            "method": "BCa",
            "n_resamples": BCa_N_RESAMPLES,
            "random_state": BCa_RANDOM_STATE,
        },
        "anomaly_clips": [
            {"clip_id": CYRILLIC_ANOMALY_CLIP, "anomaly_type": "cyrillic_ground_truth"}
        ],
    }
    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(analysis_output, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")

    whisper_baseline = {"ea": 0.460, "ea_dv": 0.945, "wer": 0.085, "acwer": 0.025, "ip": 0.989}
    print("\n=== SUMMARY vs Whisper large-v3 + initial_prompt baseline ===")
    header = (
        f"{'Variant':<40} {'EA':>7} {'EA_DV':>7} {'WER':>7} {'AC-WER':>7} {'IP':>7} {'Lat p50':>8}"
    )
    print(header)
    print("-" * 90)
    print(
        f"{'Whisper Large v3 + initial_prompt':<40} "
        f"{whisper_baseline['ea']:>7.4f} {whisper_baseline['ea_dv']:>7.4f} "
        f"{whisper_baseline['wer']:>7.4f} {whisper_baseline['acwer']:>7.4f} "
        f"{whisper_baseline['ip']:>7.4f} {'6.660s':>8}"
    )
    for sys in systems:
        if sys.variant_id == "whisper-large-v3-biased":
            continue
        marker = " ← baseline" if sys.variant_id == "granite-4.1-2b-biased" else ""
        print(
            f"{sys.variant_id:<45} "
            f"{sys.entity_accuracy:>7.4f} {sys.entity_accuracy_domain_vocab:>7.4f} "
            f"{sys.wer:>7.4f} {sys.action_critical_wer:>7.4f} "
            f"{sys.intent_preservation:>7.4f} {sys.latency['p50']:>7.3f}s{marker}"
        )
    print("\nKeyword biasing gain (biased vs batch):")
    print(f"  ΔWER:              {biasing_gain['delta_wer']:+.4f}")
    print(f"  ΔEntity accuracy:  {biasing_gain['delta_entity_accuracy']:+.4f}")
    print(f"  ΔDomain vocab EA:  {biasing_gain['delta_entity_accuracy_domain_vocab']:+.4f}")


if __name__ == "__main__":
    main()
