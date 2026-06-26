"""Compute metrics for t0011 streaming results vs t0007/t0009 batch baselines."""

from __future__ import annotations

import json
import string
from pathlib import Path
from typing import Any

import jiwer
import numpy as np
from scipy.stats import bootstrap  # type: ignore[attr-defined]

from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
)
from tasks.t0006_nemotron_3_5_benchmark.code.load_dataset import load_gold92
from tasks.t0011_streaming_stt_benchmark.code.constants import DOMAIN_VOCAB
from tasks.t0011_streaming_stt_benchmark.code.paths import (
    ANALYSIS_OUTPUT,
    GRANITE_STREAMING_TRANSCRIPTS,
    METRICS_JSON,
    PARAKEET_STREAMING_TRANSCRIPTS,
    RESULTS_DIR,
)

BCa_N_RESAMPLES: int = 10_000
BCa_RANDOM_STATE: int = 42

# Batch baselines from t0007 (Granite kw-biased) and t0009 (Parakeet biased)
BASELINE_PARAKEET_BIASED: dict[str, float] = {
    "entity_accuracy_gold92": 0.232,
    "entity_accuracy_domain_vocab": 0.333,
    "wer_gold92": 0.152,
    "action_critical_wer_gold92": 0.335,
    "intent_preservation_gold92": 0.871,
    "latency_p50_seconds": 0.038,
}
BASELINE_GRANITE_BIASED: dict[str, float] = {
    "entity_accuracy_gold92": 0.402174,
    "entity_accuracy_domain_vocab": 0.985507,
    "wer_gold92": 0.088265,
    "action_critical_wer_gold92": 0.082278,
    "intent_preservation_gold92": 0.924731,
    "latency_p50_seconds": 0.2484,
}


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


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                result[r["clip_id"]] = r
    return result


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
        "mean": float(np.mean(lats)),
    }


def compute_all(
    label: str, clips: list[GoldClip], transcripts: dict, anomaly: set[str]
) -> dict[str, Any]:
    print(f"\nComputing metrics: {label} ...")

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

    print(f"  entity_accuracy:     {ea:.4f} [{ea_ci[0]:.4f}-{ea_ci[1]:.4f}]")
    print(f"  entity_accuracy_dv:  {dv:.4f}")
    print(f"  wer:                 {wer:.4f}")
    print(f"  action_critical_wer: {acw:.4f}")
    print(f"  intent_preservation: {ip:.4f}")
    print(f"  lat p50/p95/p99:     {lat['p50']:.3f}s / {lat['p95']:.3f}s / {lat['p99']:.3f}s")

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


def delta(streaming_val: float, batch_val: float) -> float:
    return round(streaming_val - batch_val, 6)


def main() -> None:
    for path, name in [
        (PARAKEET_STREAMING_TRANSCRIPTS, "parakeet"),
        (GRANITE_STREAMING_TRANSCRIPTS, "granite"),
    ]:
        if not path.exists():
            raise RuntimeError(
                f"{name} transcripts not found at {path}. Run run_streaming_{name}.py first."
            )  # noqa: E501

    clips = load_gold92()
    anomaly: set[str] = {CYRILLIC_ANOMALY_CLIP}

    parakeet_t = load_jsonl(PARAKEET_STREAMING_TRANSCRIPTS)
    granite_t = load_jsonl(GRANITE_STREAMING_TRANSCRIPTS)

    parakeet_m = compute_all("Parakeet TDT 0.6b-v3 — streaming biased", clips, parakeet_t, anomaly)
    granite_m = compute_all("Granite Speech 4.1 2B — streaming biased", clips, granite_t, anomaly)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {
        "variants": [
            {
                "variant_id": "parakeet-tdt-0.6b-v3-streaming-biased",
                "label": "Parakeet TDT 0.6b-v3 — streaming biased",
                "metrics": {
                    "entity_accuracy_gold92": round(parakeet_m["entity_accuracy"], 6),
                    "entity_accuracy_domain_vocab": round(parakeet_m["domain_vocab_accuracy"], 6),
                    "wer_gold92": round(parakeet_m["wer"], 6),
                    "action_critical_wer_gold92": round(parakeet_m["action_critical_wer"], 6),
                    "intent_preservation_gold92": round(parakeet_m["intent_preservation"], 6),
                    "latency_p50_seconds": round(parakeet_m["latency"]["p50"], 4),
                },
            },
            {
                "variant_id": "granite-speech-4.1-2b-streaming-biased",
                "label": "Granite Speech 4.1 2B — streaming biased",
                "metrics": {
                    "entity_accuracy_gold92": round(granite_m["entity_accuracy"], 6),
                    "entity_accuracy_domain_vocab": round(granite_m["domain_vocab_accuracy"], 6),
                    "wer_gold92": round(granite_m["wer"], 6),
                    "action_critical_wer_gold92": round(granite_m["action_critical_wer"], 6),
                    "intent_preservation_gold92": round(granite_m["intent_preservation"], 6),
                    "latency_p50_seconds": round(granite_m["latency"]["p50"], 4),
                },
            },
        ],
        "streaming_vs_batch_delta": {
            "parakeet": {
                "delta_entity_accuracy": delta(
                    parakeet_m["entity_accuracy"],
                    BASELINE_PARAKEET_BIASED["entity_accuracy_gold92"],
                ),  # noqa: E501
                "delta_entity_accuracy_dv": delta(
                    parakeet_m["domain_vocab_accuracy"],
                    BASELINE_PARAKEET_BIASED["entity_accuracy_domain_vocab"],
                ),  # noqa: E501
                "delta_wer": delta(parakeet_m["wer"], BASELINE_PARAKEET_BIASED["wer_gold92"]),
                "delta_action_critical_wer": delta(
                    parakeet_m["action_critical_wer"],
                    BASELINE_PARAKEET_BIASED["action_critical_wer_gold92"],
                ),  # noqa: E501
                "delta_intent_preservation": delta(
                    parakeet_m["intent_preservation"],
                    BASELINE_PARAKEET_BIASED["intent_preservation_gold92"],
                ),  # noqa: E501
                "delta_latency_p50": delta(
                    parakeet_m["latency"]["p50"], BASELINE_PARAKEET_BIASED["latency_p50_seconds"]
                ),  # noqa: E501
            },
            "granite": {
                "delta_entity_accuracy": delta(
                    granite_m["entity_accuracy"], BASELINE_GRANITE_BIASED["entity_accuracy_gold92"]
                ),  # noqa: E501
                "delta_entity_accuracy_dv": delta(
                    granite_m["domain_vocab_accuracy"],
                    BASELINE_GRANITE_BIASED["entity_accuracy_domain_vocab"],
                ),  # noqa: E501
                "delta_wer": delta(granite_m["wer"], BASELINE_GRANITE_BIASED["wer_gold92"]),
                "delta_action_critical_wer": delta(
                    granite_m["action_critical_wer"],
                    BASELINE_GRANITE_BIASED["action_critical_wer_gold92"],
                ),  # noqa: E501
                "delta_intent_preservation": delta(
                    granite_m["intent_preservation"],
                    BASELINE_GRANITE_BIASED["intent_preservation_gold92"],
                ),  # noqa: E501
                "delta_latency_p50": delta(
                    granite_m["latency"]["p50"], BASELINE_GRANITE_BIASED["latency_p50_seconds"]
                ),  # noqa: E501
            },
        },
    }

    with METRICS_JSON.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"\nWrote {METRICS_JSON}")

    # Per-clip analysis
    per_clip = []
    for c in clips:
        per_clip.append(
            {
                "clip_id": c.clip_id,
                "reference": c.reference_text,
                "hypothesis_parakeet_streaming": str(
                    parakeet_t.get(c.clip_id, {}).get("hypothesis", "")
                ),  # noqa: E501
                "hypothesis_granite_streaming": str(
                    granite_t.get(c.clip_id, {}).get("hypothesis", "")
                ),  # noqa: E501
                "latency_parakeet_seconds": float(
                    parakeet_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),  # noqa: E501
                "latency_granite_seconds": float(
                    granite_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),  # noqa: E501
                "num_chunks": int(parakeet_t.get(c.clip_id, {}).get("num_chunks", 0)),
                "audio_duration_seconds": float(
                    parakeet_t.get(c.clip_id, {}).get("audio_duration_seconds", 0.0)
                ),  # noqa: E501
            }
        )

    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(
            {"per_clip": per_clip, "streaming_vs_batch_delta": metrics["streaming_vs_batch_delta"]},
            fh,
            indent=2,
            ensure_ascii=False,
        )  # noqa: E501
    print(f"Wrote {ANALYSIS_OUTPUT}")

    # Summary table
    print("\n=== STREAMING vs BATCH COMPARISON ===")
    print(f"{'Model':<42} {'EA':>7} {'EA_DV':>7} {'WER':>7} {'AC-WER':>7} {'IP':>7} {'Lat p50':>8}")
    print("-" * 95)
    rows = [
        ("Parakeet biased — batch (t0009)", BASELINE_PARAKEET_BIASED),
        ("Granite 4.1 2B biased — batch (t0007)", BASELINE_GRANITE_BIASED),
    ]
    for name, m in rows:
        print(
            f"{name:<42} {m['entity_accuracy_gold92']:>7.4f} {m['entity_accuracy_domain_vocab']:>7.4f} "  # noqa: E501
            f"{m['wer_gold92']:>7.4f} {m['action_critical_wer_gold92']:>7.4f} "
            f"{m['intent_preservation_gold92']:>7.4f} {m['latency_p50_seconds']:>7.3f}s"
        )
    streaming_rows = [
        ("Parakeet biased — streaming (t0011)", parakeet_m),
        ("Granite 4.1 2B biased — streaming (t0011)", granite_m),
    ]
    for name, m in streaming_rows:
        print(
            f"{name:<42} {m['entity_accuracy']:>7.4f} {m['domain_vocab_accuracy']:>7.4f} "
            f"{m['wer']:>7.4f} {m['action_critical_wer']:>7.4f} "
            f"{m['intent_preservation']:>7.4f} {m['latency']['p50']:>7.3f}s"
        )

    print("\n=== STREAMING DELTA (streaming − batch) ===")
    for model_key, baseline_label in [("parakeet", "Parakeet"), ("granite", "Granite")]:
        d = metrics["streaming_vs_batch_delta"][model_key]
        print(f"\n{baseline_label}:")
        print(f"  ΔEA:          {d['delta_entity_accuracy']:+.4f}")
        print(f"  ΔEA_DV:       {d['delta_entity_accuracy_dv']:+.4f}")
        print(f"  ΔWER:         {d['delta_wer']:+.4f}")
        print(f"  ΔAC-WER:      {d['delta_action_critical_wer']:+.4f}")
        print(f"  ΔIP:          {d['delta_intent_preservation']:+.4f}")
        print(f"  ΔLat p50:     {d['delta_latency_p50']:+.3f}s")


if __name__ == "__main__":
    main()
