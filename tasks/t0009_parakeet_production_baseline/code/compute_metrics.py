"""Compute metrics for Parakeet production-baseline variants vs Whisper t0004 and Granite t0007."""

from __future__ import annotations

import json
import string
from typing import Any

import jiwer
import numpy as np
from scipy.stats import bootstrap  # type: ignore[attr-defined]

from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
)
from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import load_gold92
from tasks.t0009_parakeet_production_baseline.code.constants import DOMAIN_VOCAB
from tasks.t0009_parakeet_production_baseline.code.paths import (
    ANALYSIS_OUTPUT,
    METRICS_JSON,
    PARAKEET_BATCH_TRANSCRIPTS,
    PARAKEET_BIASED_TRANSCRIPTS,
    RESULTS_DIR,
)

BCa_N_RESAMPLES = 10_000
BCa_RANDOM_STATE = 42


def normalise(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def bca_ci(arr: np.ndarray) -> tuple[float, float]:
    try:
        r = bootstrap(
            (arr,),
            statistic=np.mean,
            method="BCa",
            n_resamples=BCa_N_RESAMPLES,
            random_state=BCa_RANDOM_STATE,
        )
        lo, hi = float(r.confidence_interval.low), float(r.confidence_interval.high)
        if np.isnan(lo) or np.isnan(hi):
            raise ValueError
        return lo, hi
    except Exception:  # noqa: BLE001
        r = bootstrap(
            (arr,),
            statistic=np.mean,
            method="percentile",
            n_resamples=BCa_N_RESAMPLES,
            random_state=BCa_RANDOM_STATE,
        )
        return float(r.confidence_interval.low), float(r.confidence_interval.high)


def load_transcripts(path) -> dict[str, dict[str, Any]]:
    with open(path, encoding="utf-8") as fh:
        return {r["clip_id"]: r for r in json.load(fh)}


def entity_accuracy(
    clips: list[GoldClip], transcripts: dict, anomaly: set[str]
) -> tuple[float, list]:
    per: list[float | None] = []
    for c in clips:
        if c.clip_id in anomaly or not c.entity_spans:
            per.append(None if c.clip_id in anomaly else 0.0)
            continue
        hyp = normalise(str(transcripts.get(c.clip_id, {}).get("hypothesis", "")))
        correct = sum(1 for s in c.entity_spans if normalise(s["text"]) in hyp)
        per.append(correct / len(c.entity_spans))
    arr = np.array([np.nan if v is None else v for v in per])
    return float(np.nanmean(arr)), per


def domain_vocab_accuracy(clips: list[GoldClip], transcripts: dict) -> tuple[float, list]:
    vocab_norm = [normalise(t) for t in DOMAIN_VOCAB]
    per: list[float | None] = []
    total_c = total_n = 0
    for c in clips:
        ref = normalise(c.reference_text)
        hyp = normalise(str(transcripts.get(c.clip_id, {}).get("hypothesis", "")))
        present = [t for t in vocab_norm if t in ref]
        if not present:
            per.append(None)
            continue
        correct = sum(1 for t in present if t in hyp)
        per.append(correct / len(present))
        total_c += correct
        total_n += len(present)
    return (total_c / total_n if total_n > 0 else 0.0), per


def wer_batch(clips: list[GoldClip], transcripts: dict) -> tuple[float, list[float]]:
    refs = [normalise(c.reference_text) for c in clips]
    hyps = [normalise(str(transcripts.get(c.clip_id, {}).get("hypothesis", ""))) for c in clips]
    r = jiwer.process_words(refs, hyps)
    n = r.hits + r.substitutions + r.deletions
    agg = (r.substitutions + r.deletions + r.insertions) / n if n > 0 else 0.0
    per = []
    for ref, hyp in zip(refs, hyps, strict=True):
        ri = jiwer.process_words([ref], [hyp])
        ni = ri.hits + ri.substitutions + ri.deletions
        per.append((ri.substitutions + ri.deletions + ri.insertions) / ni if ni > 0 else 0.0)
    return agg, per


def ac_wer(clips: list[GoldClip], transcripts: dict) -> tuple[float, list[float]]:
    th = ts = td = 0
    per = []
    for c in clips:
        if not c.entity_spans:
            per.append(0.0)
            continue
        hyp_raw = str(transcripts.get(c.clip_id, {}).get("hypothesis", ""))
        hyp_words = set(normalise(hyp_raw).split())
        h = d = s = 0
        for span in c.entity_spans:
            for w in normalise(span["text"]).split():
                if w in hyp_words:
                    h += 1
                else:
                    d += 1
        ni = h + d + s
        per.append((d + s) / ni if ni > 0 else 0.0)
        th += h
        ts += s
        td += d
    tot = th + ts + td
    return (ts + td) / tot if tot > 0 else 0.0, per


def intent_preservation(clips: list[GoldClip], transcripts: dict) -> tuple[float, list[float]]:
    per = []
    for c in clips:
        hyp = normalise(str(transcripts.get(c.clip_id, {}).get("hypothesis", "")))
        if not c.entity_spans:
            per.append(1.0)
            continue
        per.append(1.0 if any(normalise(s["text"]) in hyp for s in c.entity_spans) else 0.0)
    return float(np.mean(per)), per


def latency_stats(transcripts: dict) -> dict[str, float]:
    lats = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    return {
        "p50": float(np.percentile(lats, 50)),
        "p95": float(np.percentile(lats, 95)),
        "p99": float(np.percentile(lats, 99)),
    }


def compute_and_print(
    label: str, clips: list[GoldClip], transcripts: dict, anomaly: set[str]
) -> dict[str, Any]:
    print(f"Computing metrics: {label} ...")

    ea, ea_per = entity_accuracy(clips, transcripts, anomaly)
    ea_arr = np.array([np.nan if v is None else v for v in ea_per])
    ea_ci = bca_ci(ea_arr[~np.isnan(ea_arr)])

    dv, dv_per = domain_vocab_accuracy(clips, transcripts)
    dv_arr = np.array([np.nan if v is None else v for v in dv_per])
    dv_valid = dv_arr[~np.isnan(dv_arr)]
    dv_ci = bca_ci(dv_valid) if len(dv_valid) > 1 else (0.0, 0.0)

    wer, wer_per = wer_batch(clips, transcripts)
    wer_ci = bca_ci(np.array(wer_per))

    acw, acw_per = ac_wer(clips, transcripts)

    ip, ip_per = intent_preservation(clips, transcripts)

    lat = latency_stats(transcripts)

    print(f"  entity_accuracy:       {ea:.4f} [{ea_ci[0]:.4f}-{ea_ci[1]:.4f}]")
    print(f"  entity_accuracy_dv:    {dv:.4f} [{dv_ci[0]:.4f}-{dv_ci[1]:.4f}]")
    print(f"  wer:                   {wer:.4f} [{wer_ci[0]:.4f}-{wer_ci[1]:.4f}]")
    print(f"  action_critical_wer:   {acw:.4f}")
    print(f"  intent_preservation:   {ip:.4f}")
    print(f"  latency p50/p95/p99:   {lat['p50']:.3f}s / {lat['p95']:.3f}s / {lat['p99']:.3f}s")

    return {
        "entity_accuracy": ea,
        "entity_accuracy_ci": ea_ci,
        "entity_per_clip": ea_per,
        "domain_vocab_accuracy": dv,
        "domain_vocab_ci": dv_ci,
        "domain_vocab_per_clip": dv_per,
        "wer": wer,
        "wer_ci": wer_ci,
        "wer_per_clip": wer_per,
        "action_critical_wer": acw,
        "acw_per_clip": acw_per,
        "intent_preservation": ip,
        "ip_per_clip": ip_per,
        "latency": lat,
    }


def main() -> None:
    clips = load_gold92()
    anomaly: set[str] = {CYRILLIC_ANOMALY_CLIP}

    for p, name in [(PARAKEET_BATCH_TRANSCRIPTS, "batch"), (PARAKEET_BIASED_TRANSCRIPTS, "biased")]:
        if not p.exists():
            raise RuntimeError(
                f"Parakeet {name} transcripts not found at {p}. Run run_parakeet.py first."
            )

    batch_t = load_transcripts(PARAKEET_BATCH_TRANSCRIPTS)
    biased_t = load_transcripts(PARAKEET_BIASED_TRANSCRIPTS)

    batch_m = compute_and_print(
        "Parakeet TDT 0.6b-v3 — unbiased (no prompt)", clips, batch_t, anomaly
    )
    biased_m = compute_and_print(
        "Parakeet TDT 0.6b-v3 — biased (production config)", clips, biased_t, anomaly
    )

    gain = {
        "delta_wer": round(biased_m["wer"] - batch_m["wer"], 6),
        "delta_entity_accuracy": round(biased_m["entity_accuracy"] - batch_m["entity_accuracy"], 6),
        "delta_domain_vocab_accuracy": round(
            biased_m["domain_vocab_accuracy"] - batch_m["domain_vocab_accuracy"], 6
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {
        "variants": [
            {
                "variant_id": "parakeet-tdt-0.6b-v3-unbiased",
                "label": "Parakeet TDT 0.6b-v3 — unbiased",
                "metrics": {
                    "entity_accuracy_gold92": round(batch_m["entity_accuracy"], 6),
                    "entity_accuracy_domain_vocab": round(batch_m["domain_vocab_accuracy"], 6),
                    "wer_gold92": round(batch_m["wer"], 6),
                    "action_critical_wer_gold92": round(batch_m["action_critical_wer"], 6),
                    "intent_preservation_gold92": round(batch_m["intent_preservation"], 6),
                    "latency_p50_seconds": round(batch_m["latency"]["p50"], 4),
                },
            },
            {
                "variant_id": "parakeet-tdt-0.6b-v3-biased",
                "label": "Parakeet TDT 0.6b-v3 — biased (production config)",
                "metrics": {
                    "entity_accuracy_gold92": round(biased_m["entity_accuracy"], 6),
                    "entity_accuracy_domain_vocab": round(biased_m["domain_vocab_accuracy"], 6),
                    "wer_gold92": round(biased_m["wer"], 6),
                    "action_critical_wer_gold92": round(biased_m["action_critical_wer"], 6),
                    "intent_preservation_gold92": round(biased_m["intent_preservation"], 6),
                    "latency_p50_seconds": round(biased_m["latency"]["p50"], 4),
                },
            },
        ],
        "biasing_gain": gain,
    }
    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    per_clip = []
    for i, c in enumerate(clips):
        per_clip.append(
            {
                "clip_id": c.clip_id,
                "reference": c.reference_text,
                "hypothesis_unbiased": str(batch_t.get(c.clip_id, {}).get("hypothesis", "")),
                "hypothesis_biased": str(biased_t.get(c.clip_id, {}).get("hypothesis", "")),
                "entity_accuracy_unbiased": batch_m["entity_per_clip"][i],
                "entity_accuracy_biased": biased_m["entity_per_clip"][i],
                "domain_vocab_unbiased": batch_m["domain_vocab_per_clip"][i],
                "domain_vocab_biased": biased_m["domain_vocab_per_clip"][i],
            }
        )
    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump({"per_clip": per_clip, "biasing_gain": gain}, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")

    whisker = {"ea": 0.460, "ea_dv": 0.945, "wer": 0.085, "acwer": 0.025, "ip": 0.989, "lat": 6.660}
    granite = {"ea": 0.402, "ea_dv": 0.986, "wer": 0.088, "acwer": 0.082, "ip": 0.925, "lat": 0.248}
    nemotron = {
        "ea": 0.248,
        "ea_dv": 0.182,
        "wer": 0.176,
        "acwer": 0.317,
        "ip": 0.903,
        "lat": 0.719,
    }

    print("\n=== FULL COMPARISON ===")
    print(f"{'Model':<42} {'EA':>7} {'EA_DV':>7} {'WER':>7} {'AC-WER':>7} {'IP':>7} {'Lat p50':>8}")
    print("-" * 92)
    for name, m in [
        ("Whisper large-v3 + prompt (t0004)", whisker),
        ("Granite 4.1 2B biased (t0007)", granite),
        ("Nemotron 3.5 batch (t0006)", nemotron),
    ]:
        print(
            f"{name:<42} {m['ea']:>7.4f} {m['ea_dv']:>7.4f} "
            f"{m['wer']:>7.4f} {m['acwer']:>7.4f} {m['ip']:>7.4f} {m['lat']:>7.3f}s"
        )
    for label, m in [("parakeet-unbiased", batch_m), ("parakeet-biased (production)", biased_m)]:
        print(
            f"{label:<42} {m['entity_accuracy']:>7.4f} {m['domain_vocab_accuracy']:>7.4f} "
            f"{m['wer']:>7.4f} {m['action_critical_wer']:>7.4f} "
            f"{m['intent_preservation']:>7.4f} {m['latency']['p50']:>7.3f}s"
        )
    print("\nBiasing gain (biased vs unbiased):")
    print(f"  ΔWER:            {gain['delta_wer']:+.4f}")
    print(f"  ΔEA:             {gain['delta_entity_accuracy']:+.4f}")
    print(f"  ΔDomain vocab:   {gain['delta_domain_vocab_accuracy']:+.4f}")


if __name__ == "__main__":
    main()
