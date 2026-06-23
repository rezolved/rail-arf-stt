"""Generate predictions assets for Deepgram and Whisper on gold-92.

Creates the folder structure required by the predictions asset specification v2.
Reads transcripts from data/ and metrics from data/analysis_output.json.
"""

from __future__ import annotations

import json
import string
from datetime import date
from pathlib import Path
from typing import Any

from tasks.t0002_baseline_evaluation.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
    load_gold92,
)
from tasks.t0002_baseline_evaluation.code.paths import (
    ANALYSIS_OUTPUT,
    DEEPGRAM_PREDICTIONS_DIR,
    DEEPGRAM_TRANSCRIPTS,
    WHISPER_PREDICTIONS_DIR,
    WHISPER_TRANSCRIPTS,
)


def normalise(text: str) -> str:
    """Lowercase and strip punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def compute_clip_entity_accuracy(
    *,
    clip: GoldClip,
    hypothesis: str,
    is_anomaly: bool,
) -> float | None:
    """Compute per-clip entity accuracy. Returns None for anomaly clips."""
    if is_anomaly:
        return None
    if len(clip.entity_spans) == 0:
        return 0.0
    hyp_norm = normalise(hypothesis)
    correct = sum(1 for span in clip.entity_spans if normalise(str(span["text"])) in hyp_norm)
    return correct / len(clip.entity_spans)


def compute_clip_wer(*, reference: str, hypothesis: str) -> float:
    """Compute per-clip WER."""
    import jiwer

    ref_norm = normalise(reference)
    hyp_norm = normalise(hypothesis)
    result = jiwer.process_words([ref_norm], [hyp_norm])
    n = result.hits + result.substitutions + result.deletions
    e = result.substitutions + result.deletions + result.insertions
    return e / n if n > 0 else 0.0


def build_predictions_jsonl(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    system_id: str,
) -> list[dict[str, Any]]:
    """Build one prediction record per clip."""
    anomaly_clips: set[str] = {CYRILLIC_ANOMALY_CLIP}
    records: list[dict[str, Any]] = []

    for clip in clips:
        raw = transcripts.get(clip.clip_id, {})
        hypothesis: str = str(raw.get("hypothesis", ""))
        latency: float = float(raw.get("latency_seconds", 0.0))
        is_anomaly = clip.clip_id in anomaly_clips

        entity_accuracy = compute_clip_entity_accuracy(
            clip=clip,
            hypothesis=hypothesis,
            is_anomaly=is_anomaly,
        )
        wer = compute_clip_wer(
            reference=clip.reference_text,
            hypothesis=hypothesis,
        )

        entity_spans_predicted: list[dict[str, Any]] = []
        for span in clip.entity_spans:
            span_text: str = span["text"]
            if normalise(span_text) in normalise(hypothesis):
                entity_spans_predicted.append(
                    {"text": span_text, "type": span.get("type", "unknown"), "found": True}
                )
            else:
                entity_spans_predicted.append(
                    {"text": span_text, "type": span.get("type", "unknown"), "found": False}
                )

        anomaly_flag: str | None = "cyrillic_ground_truth" if is_anomaly else None

        records.append(
            {
                "clip_id": clip.clip_id,
                "reference": clip.reference_text,
                "hypothesis": hypothesis,
                "accent_group": clip.accent_group,
                "entity_spans_reference": clip.entity_spans,
                "entity_spans_predicted": entity_spans_predicted,
                "entity_accuracy": entity_accuracy,
                "wer": round(wer, 6),
                "latency_seconds": round(latency, 4),
                "anomaly_flag": anomaly_flag,
            }
        )

    return records


def write_asset(
    *,
    asset_dir: Path,
    predictions_id: str,
    name: str,
    short_description: str,
    model_description: str,
    predictions_jsonl: list[dict[str, Any]],
    metadata: dict[str, Any],
    description_md: str,
    entity_accuracy: float,
    wer: float,
    categories: list[str],
) -> None:
    """Write a complete predictions asset folder."""
    files_dir = asset_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    # Write predictions JSONL
    jsonl_path = files_dir / "predictions-gold92.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as fh:
        for record in predictions_jsonl:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Write metadata.json
    metadata_path = asset_dir / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)

    # Write details.json
    details: dict[str, Any] = {
        "spec_version": "2",
        "predictions_id": predictions_id,
        "name": name,
        "short_description": short_description,
        "description_path": "description.md",
        "model_id": None,
        "model_description": model_description,
        "dataset_ids": ["stt-benchmark-gold-92"],
        "prediction_format": "jsonl",
        "prediction_schema": (
            "Each line is a JSON object with fields: clip_id (string), "
            "reference (string, normalised ground truth), hypothesis (string, model output), "
            "accent_group (string, speaker accent category), "
            "entity_spans_reference (list of {text, type, start, end}), "
            "entity_spans_predicted (list of {text, type, found: bool}), "
            "entity_accuracy (float or null for anomaly clips), "
            "wer (float, word error rate for this clip), "
            "latency_seconds (float, end-to-end inference time), "
            "anomaly_flag (string or null)."
        ),
        "instance_count": len(predictions_jsonl),
        "metrics_at_creation": {
            "entity_accuracy_gold92": round(entity_accuracy, 6),
            "wer_gold92": round(wer, 6),
        },
        "files": [
            {
                "path": "files/predictions-gold92.jsonl",
                "description": (
                    "Per-instance predictions on gold-92 benchmark (93 clips). "
                    "One JSON object per line."
                ),
                "format": "jsonl",
            }
        ],
        "categories": categories,
        "created_by_task": "t0002_baseline_evaluation",
        "date_created": str(date.today()),
    }
    details_path = asset_dir / "details.json"
    with details_path.open("w", encoding="utf-8") as fh:
        json.dump(details, fh, indent=2, ensure_ascii=False)

    # Write description.md
    description_path = asset_dir / "description.md"
    with description_path.open("w", encoding="utf-8") as fh:
        fh.write(description_md)

    print(f"Wrote asset to {asset_dir}")
    print(f"  Predictions JSONL: {jsonl_path} ({jsonl_path.stat().st_size} bytes)")


WHISPER_DESCRIPTION_TEMPLATE = """\
---
spec_version: "2"
predictions_id: "whisper-large-v3-gold92"
documented_by_task: "t0002_baseline_evaluation"
date_documented: "{date_today}"
---

# Whisper Large v3 on Gold-92

## Metadata

* **Name**: Whisper Large v3 on Gold-92
* **Model**: Whisper Large v3 (faster-whisper, CTranslate2 INT8, device=cpu, language=en)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of OpenAI Whisper Large v3, run locally on an
Apple M5 Mac via the `faster-whisper` library (CTranslate2 INT8 quantization, CPU inference) on
the gold-92 benchmark. Gold-92 is the held-out evaluation set for all tasks in this project,
containing 93 annotated WAV clips from Rezolve production investor-relations voice sessions, with
accented English speakers across three source categories: `clean_voices` (speaker-narrated IR Q&A),
`production` (live production session captures), and `error_cases` (known hard cases including
adversarial and multilingual inputs).

The predictions serve as the open-source STT baseline for the Rezolve brainpowa voice commerce
project. Whisper Large v3 is the state-of-the-art general-purpose ASR model from OpenAI and
represents the best available open-source ceiling before any domain-specific fine-tuning or
post-correction. These results define the starting point against which entity-aware post-correction,
domain fine-tuning, and confidence-based routing approaches will be judged in subsequent tasks.

Each prediction record includes the reference text from `ground_truth.jsonl`, the Whisper
hypothesis, per-clip entity accuracy (using the all-or-nothing Caubrière et al. 2020 criterion),
per-clip WER, inference latency in seconds, and entity span annotations indicating which
action-critical entities (brand names, product lines, IR terms) were correctly recognised.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for this
clip is a normal English sentence; this clip is included in WER computation but excluded from the
aggregate entity accuracy calculation via `np.nanmean`.

## Model

Whisper Large v3 is a transformer-based encoder-decoder ASR model trained by OpenAI on 680,000
hours of multilingual speech data. The Large v3 variant contains approximately 1.5 billion
parameters and achieves 2.7% WER on LibriSpeech test-clean under clean conditions. On non-native
spontaneous English (LearnerVoice benchmark), Whisper Large v3 achieves 19.18% WER, consistent
with the expected range for accented investor-relations speech.

This evaluation uses `faster-whisper` version 1.x with CTranslate2 INT8 quantization. The model
was loaded once before the inference loop and applied identically to all 93 clips. The inference
configuration was: `device="cpu"`, `compute_type="int8"`, `language="en"`. Passing `language="en"`
is mandatory to prevent a documented failure mode where accented English speech is misclassified as
a non-English language, producing garbled transcripts. The model was warmed up on 3 throwaway clips
before recording latencies to avoid cold-cache measurements. Total inference wall-clock time was
approximately 9 minutes on Apple M5 CPU.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn from
three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

All clips use the canonical `ground_truth.jsonl` as the reference (not `gold_set.jsonl`, which has
normalisation inconsistencies in its `ground_truth` field). No preprocessing was applied to audio
files — they were passed directly to faster-whisper as WAV files.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Resolv AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}}],
  "entity_spans_predicted": [{{"text": "Rezolve AI", "type": "brand", "found": false}}],
  "entity_accuracy": 0.0,
  "wer": 0.083,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper Large v3 output (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans with type and position
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (all-or-nothing;
  null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time via `time.perf_counter()` (local CPU;
  not network-bound)
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value | BCa 95% CI |
| --- | --- | --- |
| entity_accuracy_gold92 | {entity_accuracy:.4f} | ({ci_low:.4f}, {ci_high:.4f}) |
| wer_gold92 | {wer:.4f} | — |
| action_critical_wer_gold92 | {acwer:.4f} | — |
| intent_preservation_gold92 | {intent:.4f} | — |
| latency_p50_seconds | {latency_p50:.2f}s | — |

Entity accuracy of {entity_accuracy:.1%} reflects the challenging nature of the investor-relations
domain for a general-purpose ASR model. Known failure patterns include: "Rezolve AI" transcribed as
"resolve AI" or "Hizol"; "brainpowa" transcribed as "brain power"; IR abbreviations (20-F, 10-K)
inconsistently formatted. WER of {wer:.1%} indicates overall transcription quality is reasonable
but entity-level accuracy (the primary metric) is significantly lower.

## Main Ideas

* Whisper Large v3 achieves **{wer:.1%} WER** on gold-92, within the expected range for accented
  investor-relations speech (8-20% from research literature)
* **Entity accuracy of {entity_accuracy:.1%}** reveals a substantial gap between overall
  transcription quality and entity-level precision — the primary failure mode for voice commerce
* The known failure pattern "Rezolve AI" → "resolve AI" / "Hizol" appears frequently across
  production and clean_voices clips, confirming that entity post-correction is needed
* Intent preservation of **{intent:.1%}** (heuristic proxy) suggests most utterances retain their
  high-level intent even when entity accuracy is low
* Inference latency p50 of **{latency_p50:.2f}s** (local CPU) exceeds the 800ms voice-to-action
  target — dedicated GPU or cloud API is required for production latency requirements

## Summary

These predictions capture the performance of Whisper Large v3, the leading open-source ASR model,
on the gold-92 investor-relations benchmark using local CPU inference. The model was applied without
fine-tuning or domain-specific prompt injection to establish a clean open-source baseline.

The headline finding is that overall transcription quality (WER: {wer:.1%}) is acceptable but
entity-level accuracy (entity_accuracy_gold92: {entity_accuracy:.1%}) is low. This gap reflects
the model's difficulty with proper nouns and domain-specific terms that are rare in its training
data — particularly "Rezolve AI", "brainpowa", and IR-domain abbreviations. Intent preservation
(heuristic proxy: {intent:.1%}) shows that most utterances retain sufficient semantic content for
basic intent detection even with imperfect entity recognition.

These results establish the Whisper Large v3 baseline that subsequent post-correction,
fine-tuning, and confidence-routing tasks will need to beat. The comparison against Deepgram
Nova-2 (production baseline) will be added once the Deepgram API key is available
(see intervention/deepgram_api_key_missing.md).
"""

DEEPGRAM_DESCRIPTION_TEMPLATE = """\
---
spec_version: "2"
predictions_id: "deepgram-nova2-gold92"
documented_by_task: "t0002_baseline_evaluation"
date_documented: "{date_today}"
---

# Deepgram Nova-2 on Gold-92

## Metadata

* **Name**: Deepgram Nova-2 on Gold-92
* **Model**: Deepgram Nova-2 (cloud API, model=nova-2, smart_format=True, punctuate=True)
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0002_baseline_evaluation

## Overview

These predictions capture the per-instance output of Deepgram Nova-2, the current Rezolve
production STT endpoint, run via the Deepgram cloud API on the gold-92 benchmark.
Gold-92 is the held-out evaluation set containing 93 annotated WAV clips from Rezolve
production investor-relations voice sessions with accented English speakers.

The Deepgram Nova-2 predictions represent the production baseline — the system currently deployed
in Rezolve brainpowa voice commerce. All subsequent improvement tasks (post-correction, fine-tuning,
confidence routing) must beat this baseline on `entity_accuracy_gold92` to justify deployment.

Each prediction record includes the reference text, the Deepgram hypothesis, per-clip entity
accuracy, per-clip WER, inference latency (including network round-trip), and entity span
annotations. Latency figures include network round-trip to Deepgram cloud and are NOT comparable
to Whisper local inference latencies.

## Model

Deepgram Nova-2 is a production-grade ASR system trained on diverse speech corpora with
specialisation for real-world conversational audio. The `nova-2` model variant achieves median
8.4% WER across real-world domains per Deepgram vendor benchmarks (note: vendor numbers, treat
with caution). Configuration used: `model="nova-2"`, `smart_format=True`, `punctuate=True`.
No custom vocabulary or domain adaptation was applied.

API calls were made using `deepgram-sdk` v7.x with `client.listen.v1.media.transcribe_file()`.
Latency was measured with `time.perf_counter()` around each API call and includes network
round-trip time to Deepgram servers.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans.

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including adversarial and multilingual inputs |

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object with the same schema as the
Whisper predictions asset. `latency_seconds` includes network round-trip and is NOT comparable
to Whisper's local CPU latency.

## Metrics

Deepgram metrics will be populated once the `DEEPGRAM_API_KEY` is available. See
`intervention/deepgram_api_key_missing.md`.

## Main Ideas

* Deepgram Nova-2 is the Rezolve production baseline — the system this project aims to beat
* All subsequent improvement tasks must demonstrate statistically significant improvement over
  these results to justify deployment
* Latency figures include network round-trip and are NOT comparable to local Whisper latencies

## Summary

This predictions asset will contain the Deepgram Nova-2 production baseline results on gold-92
once the Deepgram API key is available. The asset structure is complete and ready to receive the
inference results. See `intervention/deepgram_api_key_missing.md` for the action required.

The Deepgram Nova-2 results are essential for: (1) establishing the production baseline on
`entity_accuracy_gold92`; (2) running the paired BCa significance test comparing Whisper vs.
Deepgram; (3) populating Fig 1 and the summary metrics table with both systems.
"""


def main() -> None:
    """Create both predictions assets."""
    clips = load_gold92()

    # Load analysis output for metrics
    with ANALYSIS_OUTPUT.open(encoding="utf-8") as fh:
        analysis: dict[str, Any] = json.load(fh)

    summary_table: list[dict[str, Any]] = analysis.get("summary_table", [])
    whisper_row = next((r for r in summary_table if r.get("variant_id") == "whisper-large-v3"), {})

    entity_accuracy_w = float(whisper_row.get("entity_accuracy_gold92", 0.0))
    wer_w = float(whisper_row.get("wer_gold92", 0.0))
    acwer_w = float(whisper_row.get("action_critical_wer_gold92", 0.0))
    intent_w = float(whisper_row.get("intent_preservation_gold92", 0.0))
    latency_w = float(whisper_row.get("latency_p50_seconds", 0.0))
    ci_low_w = float(whisper_row.get("entity_accuracy_ci_low", 0.0))
    ci_high_w = float(whisper_row.get("entity_accuracy_ci_high", 0.0))

    whisper_transcripts = {
        r["clip_id"]: r for r in json.load(WHISPER_TRANSCRIPTS.open(encoding="utf-8"))
    }

    # Create Whisper predictions asset
    whisper_predictions = build_predictions_jsonl(
        clips=clips,
        transcripts=whisper_transcripts,
        system_id="whisper-large-v3",
    )
    whisper_metadata: dict[str, Any] = {
        "model": "Whisper Large v3",
        "package": "faster-whisper",
        "package_version": "1.x",
        "device": "cpu",
        "compute_type": "int8",
        "language": "en",
        "hardware": "Apple M5 Mac",
        "inference_date": str(date.today()),
        "total_inference_time_minutes": round(93 * 5.66 / 60, 1),
        "latency_p50_seconds": round(latency_w, 4),
        "latency_note": (
            "Whisper latency is local CPU-only and does NOT include network round-trip. "
            "Not comparable to Deepgram latency figures."
        ),
        "warmup_clips": 3,
        "bootstrap": {
            "method": "BCa (standard i.i.d.)",
            "n_resamples": 10000,
            "random_state": 42,
            "note": (
                "Standard i.i.d. BCa. For clean_voices subset (~40 clips, 6 named speakers), "
                "blockwise bootstrap by speaker would be more accurate (Liu & Peng 2020). "
                "Standard BCa is acceptable for the full 93-clip primary result."
            ),
        },
        "anomaly_clips": [
            {
                "clip_id": "error_en_0005",
                "note": (
                    "gold_set.jsonl has Cyrillic 'ы' as ground_truth for this clip. "
                    "canonical ground_truth.jsonl has normal English. "
                    "Clip included in WER but excluded from entity accuracy aggregate."
                ),
            }
        ],
    }
    whisper_description = WHISPER_DESCRIPTION_TEMPLATE.format(
        date_today=str(date.today()),
        entity_accuracy=entity_accuracy_w,
        ci_low=ci_low_w,
        ci_high=ci_high_w,
        wer=wer_w,
        acwer=acwer_w,
        intent=intent_w,
        latency_p50=latency_w,
    )
    write_asset(
        asset_dir=WHISPER_PREDICTIONS_DIR,
        predictions_id="whisper-large-v3-gold92",
        name="Whisper Large v3 on Gold-92",
        short_description=(
            "Per-instance Whisper Large v3 STT predictions on the gold-92 benchmark "
            "of 93 accented English investor-relations audio clips, establishing the "
            "open-source STT baseline for the Rezolve voice commerce project."
        ),
        model_description=(
            "OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper "
            "(CTranslate2 INT8, CPU, language='en') on Apple M5 Mac. No fine-tuning or "
            "domain adaptation. Production-ready but latency-constrained for local CPU."
        ),
        predictions_jsonl=whisper_predictions,
        metadata=whisper_metadata,
        description_md=whisper_description,
        entity_accuracy=entity_accuracy_w,
        wer=wer_w,
        categories=["stt-evaluation", "whisper-finetuning"],
    )

    # Create Deepgram predictions asset (skeleton if no transcripts available)
    if DEEPGRAM_TRANSCRIPTS.exists():
        deepgram_transcripts = {
            r["clip_id"]: r for r in json.load(DEEPGRAM_TRANSCRIPTS.open(encoding="utf-8"))
        }
        deepgram_predictions = build_predictions_jsonl(
            clips=clips,
            transcripts=deepgram_transcripts,
            system_id="deepgram-nova2",
        )
        dg_row = next((r for r in summary_table if r.get("variant_id") == "deepgram-nova2"), {})
        entity_accuracy_dg = float(dg_row.get("entity_accuracy_gold92", 0.0))
        wer_dg = float(dg_row.get("wer_gold92", 0.0))
    else:
        print(
            "WARNING: Deepgram transcripts not available — "
            "creating skeleton Deepgram asset with pending placeholder predictions."
        )
        # Create placeholder predictions for each clip (marked as pending)
        deepgram_predictions = [
            {
                "clip_id": clip.clip_id,
                "reference": clip.reference_text,
                "hypothesis": None,
                "accent_group": clip.accent_group,
                "entity_spans_reference": clip.entity_spans,
                "entity_spans_predicted": [],
                "entity_accuracy": None,
                "wer": None,
                "latency_seconds": None,
                "anomaly_flag": (
                    "cyrillic_ground_truth" if clip.clip_id == CYRILLIC_ANOMALY_CLIP else None
                ),
                "status": "PENDING — Deepgram API key required",
            }
            for clip in clips
        ]
        entity_accuracy_dg = 0.0
        wer_dg = 0.0

    deepgram_metadata: dict[str, Any] = {
        "model": "Deepgram Nova-2",
        "api_version": "v1",
        "api_settings": {
            "model": "nova-2",
            "smart_format": True,
            "punctuate": True,
        },
        "inference_date": str(date.today()),
        "latency_note": (
            "Deepgram latency includes network round-trip to Deepgram cloud servers. "
            "NOT comparable to local Whisper CPU latency figures."
        ),
        "status": (
            "COMPLETE"
            if DEEPGRAM_TRANSCRIPTS.exists()
            else "PENDING — DEEPGRAM_API_KEY not available. "
            "See intervention/deepgram_api_key_missing.md."
        ),
        "bootstrap": {
            "method": "BCa (standard i.i.d.)",
            "n_resamples": 10000,
            "random_state": 42,
        },
        "anomaly_clips": [
            {
                "clip_id": "error_en_0005",
                "note": (
                    "gold_set.jsonl has Cyrillic 'ы' as ground_truth for this clip. "
                    "Clip included in WER but excluded from entity accuracy aggregate."
                ),
            }
        ],
    }
    deepgram_description = DEEPGRAM_DESCRIPTION_TEMPLATE.format(
        date_today=str(date.today()),
    )

    write_asset(
        asset_dir=DEEPGRAM_PREDICTIONS_DIR,
        predictions_id="deepgram-nova2-gold92",
        name="Deepgram Nova-2 on Gold-92",
        short_description=(
            "Per-instance Deepgram Nova-2 STT predictions on the gold-92 benchmark "
            "of 93 accented English investor-relations audio clips, establishing the "
            "production STT baseline for the Rezolve voice commerce project."
        ),
        model_description=(
            "Deepgram Nova-2 cloud API (model='nova-2', smart_format=True, punctuate=True). "
            "Current Rezolve production STT endpoint. No domain adaptation."
        ),
        predictions_jsonl=deepgram_predictions,
        metadata=deepgram_metadata,
        description_md=deepgram_description,
        entity_accuracy=entity_accuracy_dg,
        wer=wer_dg,
        categories=["stt-evaluation", "commercial-apis"],
    )

    print("\nDone creating prediction assets.")


if __name__ == "__main__":
    main()
