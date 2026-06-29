"""Compute metrics for t0012: Whisper turbo, Parakeet, Granite on gold-92."""

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
from tasks.t0012_whisper_parakeet_granite_streaming.code.constants import DOMAIN_VOCAB
from tasks.t0012_whisper_parakeet_granite_streaming.code.paths import (
    ANALYSIS_OUTPUT,
    GRANITE_CHUNKED_TRANSCRIPTS,
    GRANITE_STREAMING_TRANSCRIPTS,
    METRICS_JSON,
    PARAKEET_CHUNKED_TRANSCRIPTS,
    PARAKEET_STREAMING_TRANSCRIPTS,
    RESULTS_DIR,
    WHISPER_BATCH_TRANSCRIPTS,
    WHISPER_STREAMING_TRANSCRIPTS,
)

BCa_N_RESAMPLES: int = 10_000
BCa_RANDOM_STATE: int = 42

# t0011 streaming baselines (Parakeet and Granite accumulate-then-transcribe)
BASELINE_PARAKEET_STREAMING: dict[str, float] = {
    "entity_accuracy_gold92": 0.2315,
    "entity_accuracy_domain_vocab": 0.3333,
    "wer_gold92": 0.1525,
    "action_critical_wer_gold92": 0.3354,
    "intent_preservation_gold92": 0.8710,
    "latency_p50_seconds": 0.041,
}
BASELINE_GRANITE_STREAMING: dict[str, float] = {
    "entity_accuracy_gold92": 0.4109,
    "entity_accuracy_domain_vocab": 0.9710,
    "wer_gold92": 0.0883,
    "action_critical_wer_gold92": 0.0759,
    "intent_preservation_gold92": 0.9355,
    "latency_p50_seconds": 0.250,
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


def ttfd_stats(transcripts: dict) -> dict[str, float]:
    ttfds = [
        float(r["ttfd_seconds"]) for r in transcripts.values() if r.get("ttfd_seconds") is not None
    ]
    if not ttfds:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}
    return {
        "p50": float(np.percentile(ttfds, 50)),
        "p95": float(np.percentile(ttfds, 95)),
        "p99": float(np.percentile(ttfds, 99)),
        "mean": float(np.mean(ttfds)),
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


def delta(a: float, b: float) -> float:
    return round(a - b, 6)


def main() -> None:
    required = [
        (WHISPER_STREAMING_TRANSCRIPTS, "whisper streaming"),
        (WHISPER_BATCH_TRANSCRIPTS, "whisper batch"),
        (PARAKEET_STREAMING_TRANSCRIPTS, "parakeet streaming"),
        (GRANITE_STREAMING_TRANSCRIPTS, "granite streaming"),
    ]
    for path, name in required:
        if not path.exists():
            raise RuntimeError(  # noqa: TRY003
                f"{name} transcripts not found at {path}. Run the corresponding script first."
            )

    clips = load_gold92()
    anomaly: set[str] = {CYRILLIC_ANOMALY_CLIP}

    whisper_stream_t = load_jsonl(WHISPER_STREAMING_TRANSCRIPTS)
    whisper_batch_t = load_jsonl(WHISPER_BATCH_TRANSCRIPTS)
    parakeet_t = load_jsonl(PARAKEET_STREAMING_TRANSCRIPTS)
    granite_t = load_jsonl(GRANITE_STREAMING_TRANSCRIPTS)

    parakeet_chunked_t: dict | None = None
    if PARAKEET_CHUNKED_TRANSCRIPTS.exists():
        parakeet_chunked_t = load_jsonl(PARAKEET_CHUNKED_TRANSCRIPTS)
        print(f"Parakeet chunked transcripts found: {PARAKEET_CHUNKED_TRANSCRIPTS}")

    granite_chunked_t: dict | None = None
    if GRANITE_CHUNKED_TRANSCRIPTS.exists():
        granite_chunked_t = load_jsonl(GRANITE_CHUNKED_TRANSCRIPTS)
        print(f"Granite chunked transcripts found: {GRANITE_CHUNKED_TRANSCRIPTS}")

    whisper_stream_m = compute_all("Whisper turbo — streaming", clips, whisper_stream_t, anomaly)
    whisper_batch_m = compute_all("Whisper turbo — batch", clips, whisper_batch_t, anomaly)
    parakeet_m = compute_all("Parakeet TDT 0.6b-v3 — streaming biased", clips, parakeet_t, anomaly)
    granite_m = compute_all("Granite Speech 4.1 2B — streaming biased", clips, granite_t, anomaly)

    parakeet_chunked_m: dict[str, Any] | None = None
    if parakeet_chunked_t is not None:
        parakeet_chunked_m = compute_all(
            "Parakeet TDT 0.6b-v3 — chunked re-transcribe biased",
            clips,
            parakeet_chunked_t,
            anomaly,
        )

    granite_chunked_m: dict[str, Any] | None = None
    if granite_chunked_t is not None:
        granite_chunked_m = compute_all(
            "Granite Speech 4.1 2B — chunked re-transcribe biased",
            clips,
            granite_chunked_t,
            anomaly,
        )

    whisper_ttfd = ttfd_stats(whisper_stream_t)
    print(
        f"\nWhisper TTFD: p50={whisper_ttfd['p50']:.3f}s"
        f"  p95={whisper_ttfd['p95']:.3f}s"
        f"  p99={whisper_ttfd['p99']:.3f}s"
    )
    if parakeet_chunked_t is not None:
        pk_ttfd = ttfd_stats(parakeet_chunked_t)
        print(
            f"Parakeet chunked TTFD: p50={pk_ttfd['p50']:.3f}s"
            f"  p95={pk_ttfd['p95']:.3f}s"
            f"  p99={pk_ttfd['p99']:.3f}s"
        )
    if granite_chunked_t is not None:
        gr_ttfd = ttfd_stats(granite_chunked_t)
        print(
            f"Granite chunked TTFD: p50={gr_ttfd['p50']:.3f}s"
            f"  p95={gr_ttfd['p95']:.3f}s"
            f"  p99={gr_ttfd['p99']:.3f}s"
        )

    def build_variant(variant_id: str, label: str, m: dict[str, Any]) -> dict[str, Any]:
        return {
            "variant_id": variant_id,
            "label": label,
            "metrics": {
                "entity_accuracy_gold92": round(m["entity_accuracy"], 6),
                "entity_accuracy_domain_vocab": round(m["domain_vocab_accuracy"], 6),
                "wer_gold92": round(m["wer"], 6),
                "action_critical_wer_gold92": round(m["action_critical_wer"], 6),
                "intent_preservation_gold92": round(m["intent_preservation"], 6),
                "latency_p50_seconds": round(m["latency"]["p50"], 4),
                "latency_p95_seconds": round(m["latency"]["p95"], 4),
                "latency_p99_seconds": round(m["latency"]["p99"], 4),
            },
        }

    variants: list[dict[str, Any]] = [
        build_variant("whisper-turbo-streaming", "Whisper turbo — streaming", whisper_stream_m),
        build_variant("whisper-turbo-batch", "Whisper turbo — batch", whisper_batch_m),
        build_variant(
            "parakeet-tdt-0.6b-v3-streaming-biased",
            "Parakeet TDT 0.6b-v3 — streaming biased",
            parakeet_m,
        ),
        build_variant(
            "granite-speech-4.1-2b-streaming-biased",
            "Granite Speech 4.1 2B — streaming biased",
            granite_m,
        ),
    ]
    if parakeet_chunked_m is not None:
        variants.append(
            build_variant(
                "parakeet-tdt-0.6b-v3-chunked-biased",
                "Parakeet TDT 0.6b-v3 — chunked re-transcribe biased",
                parakeet_chunked_m,
            )
        )
    if granite_chunked_m is not None:
        variants.append(
            build_variant(
                "granite-speech-4.1-2b-chunked-biased",
                "Granite Speech 4.1 2B — chunked re-transcribe biased",
                granite_chunked_m,
            )
        )

    metrics: dict[str, Any] = {
        "variants": variants,
        "whisper_ttfd": whisper_ttfd,
        "parakeet_ttfd": ttfd_stats(parakeet_chunked_t) if parakeet_chunked_t is not None else None,
        "granite_ttfd": ttfd_stats(granite_chunked_t) if granite_chunked_t is not None else None,
        "whisper_streaming_vs_batch_delta": {
            "delta_entity_accuracy": delta(
                whisper_stream_m["entity_accuracy"], whisper_batch_m["entity_accuracy"]
            ),
            "delta_entity_accuracy_dv": delta(
                whisper_stream_m["domain_vocab_accuracy"], whisper_batch_m["domain_vocab_accuracy"]
            ),
            "delta_wer": delta(whisper_stream_m["wer"], whisper_batch_m["wer"]),
            "delta_action_critical_wer": delta(
                whisper_stream_m["action_critical_wer"], whisper_batch_m["action_critical_wer"]
            ),
            "delta_intent_preservation": delta(
                whisper_stream_m["intent_preservation"], whisper_batch_m["intent_preservation"]
            ),
            "delta_latency_p50": delta(
                whisper_stream_m["latency"]["p50"], whisper_batch_m["latency"]["p50"]
            ),
        },
        "parakeet_vs_t0011_delta": {
            "delta_entity_accuracy": delta(
                parakeet_m["entity_accuracy"],
                BASELINE_PARAKEET_STREAMING["entity_accuracy_gold92"],
            ),
            "delta_wer": delta(parakeet_m["wer"], BASELINE_PARAKEET_STREAMING["wer_gold92"]),
            "delta_latency_p50": delta(
                parakeet_m["latency"]["p50"], BASELINE_PARAKEET_STREAMING["latency_p50_seconds"]
            ),
        },
        "granite_vs_t0011_delta": {
            "delta_entity_accuracy": delta(
                granite_m["entity_accuracy"],
                BASELINE_GRANITE_STREAMING["entity_accuracy_gold92"],
            ),
            "delta_wer": delta(granite_m["wer"], BASELINE_GRANITE_STREAMING["wer_gold92"]),
            "delta_latency_p50": delta(
                granite_m["latency"]["p50"], BASELINE_GRANITE_STREAMING["latency_p50_seconds"]
            ),
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
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
                "hypothesis_whisper_streaming": str(
                    whisper_stream_t.get(c.clip_id, {}).get("hypothesis", "")
                ),
                "hypothesis_whisper_batch": str(
                    whisper_batch_t.get(c.clip_id, {}).get("hypothesis", "")
                ),
                "hypothesis_parakeet_streaming": str(
                    parakeet_t.get(c.clip_id, {}).get("hypothesis", "")
                ),
                "hypothesis_granite_streaming": str(
                    granite_t.get(c.clip_id, {}).get("hypothesis", "")
                ),
                "latency_whisper_streaming_seconds": float(
                    whisper_stream_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),
                "ttfd_whisper_seconds": float(
                    whisper_stream_t.get(c.clip_id, {}).get("ttfd_seconds", 0.0) or 0.0
                ),
                "latency_whisper_batch_seconds": float(
                    whisper_batch_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),
                "latency_parakeet_seconds": float(
                    parakeet_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),
                "latency_granite_seconds": float(
                    granite_t.get(c.clip_id, {}).get("latency_seconds", 0.0)
                ),
                "num_chunks": int(whisper_stream_t.get(c.clip_id, {}).get("num_chunks", 0)),
                "audio_duration_seconds": float(
                    whisper_stream_t.get(c.clip_id, {}).get("audio_duration_seconds", 0.0)
                ),
            }
        )

    ANALYSIS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ANALYSIS_OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump({"per_clip": per_clip}, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {ANALYSIS_OUTPUT}")

    # Summary table
    col = 44
    cols = f"{'EA':>7} {'EA_DV':>7} {'WER':>7} {'AC-WER':>7} {'IP':>7} {'Lat p50':>8}"
    print(f"\n{'Model':<{col}} {cols}")
    print("-" * 97)
    rows = [
        ("Whisper turbo — streaming", whisper_stream_m),
        ("Whisper turbo — batch", whisper_batch_m),
        ("Parakeet TDT 0.6b-v3 — streaming biased", parakeet_m),
        ("Granite Speech 4.1 2B — streaming biased", granite_m),
    ]
    if parakeet_chunked_m is not None:
        rows.append(("Parakeet TDT 0.6b-v3 — chunked re-transcribe biased", parakeet_chunked_m))
    if granite_chunked_m is not None:
        rows.append(("Granite Speech 4.1 2B — chunked re-transcribe biased", granite_chunked_m))
    for name, m in rows:
        print(
            f"{name:<{col}}"
            f" {m['entity_accuracy']:>7.4f}"
            f" {m['domain_vocab_accuracy']:>7.4f}"
            f" {m['wer']:>7.4f}"
            f" {m['action_critical_wer']:>7.4f}"
            f" {m['intent_preservation']:>7.4f}"
            f" {m['latency']['p50']:>7.3f}s"
        )

    wd = metrics["whisper_streaming_vs_batch_delta"]
    print("\n=== WHISPER STREAMING vs BATCH DELTA ===")
    print(f"  ΔEA:          {wd['delta_entity_accuracy']:+.4f}")
    print(f"  ΔEA_DV:       {wd['delta_entity_accuracy_dv']:+.4f}")
    print(f"  ΔWER:         {wd['delta_wer']:+.4f}")
    print(f"  ΔAC-WER:      {wd['delta_action_critical_wer']:+.4f}")
    print(f"  ΔIP:          {wd['delta_intent_preservation']:+.4f}")
    print(f"  ΔLat p50:     {wd['delta_latency_p50']:+.3f}s")

    print(f"\nWhisper TTFD: p50={whisper_ttfd['p50']:.3f}s  p95={whisper_ttfd['p95']:.3f}s")
    if parakeet_chunked_t is not None:
        pk_t = ttfd_stats(parakeet_chunked_t)
        print(f"Parakeet chunked TTFD: p50={pk_t['p50']:.3f}s  p95={pk_t['p95']:.3f}s")
    if granite_chunked_t is not None:
        gr_t = ttfd_stats(granite_chunked_t)
        print(f"Granite chunked TTFD: p50={gr_t['p50']:.3f}s  p95={gr_t['p95']:.3f}s")


if __name__ == "__main__":
    main()
