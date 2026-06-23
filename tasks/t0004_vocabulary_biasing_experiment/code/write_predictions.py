"""Write prediction assets for both biased Whisper variants.

Creates assets/predictions/whisper-large-v3-biased/ and
assets/predictions/whisper-turbo-biased/ with:
  - files/predictions-gold92.jsonl
  - details.json
  - description.md
"""

from __future__ import annotations

import json
import string
from pathlib import Path
from typing import Any

import jiwer

from tasks.t0004_vocabulary_biasing_experiment.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    GoldClip,
    load_gold92,
)
from tasks.t0004_vocabulary_biasing_experiment.code.paths import (
    MOONSHINE_PREDICTIONS_DIR,
    MOONSHINE_TRANSCRIPTS,
    WHISPER_BIASED_PREDICTIONS_DIR,
    WHISPER_BIASED_TRANSCRIPTS,
    WHISPER_TURBO_BIASED_PREDICTIONS_DIR,
    WHISPER_TURBO_BIASED_TRANSCRIPTS,
)


def normalise(text: str) -> str:
    """Lowercase and strip punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def compute_clip_wer(ref: str, hyp: str) -> float:
    """Compute WER for a single clip."""
    ref_norm = normalise(ref)
    hyp_norm = normalise(hyp)
    result = jiwer.process_words([ref_norm], [hyp_norm])
    ref_words = result.hits + result.substitutions + result.deletions
    errors = result.substitutions + result.deletions + result.insertions
    return errors / ref_words if ref_words > 0 else 0.0


def compute_entity_accuracy(*, clip: GoldClip, hypothesis: str, is_anomaly: bool) -> float | None:
    """Compute entity accuracy for a single clip."""
    if is_anomaly:
        return None
    entity_spans = clip.entity_spans
    if len(entity_spans) == 0:
        return 0.0
    hyp_norm = normalise(hypothesis)
    correct = sum(1 for span in entity_spans if normalise(span["text"]) in hyp_norm)
    return correct / len(entity_spans)


def write_prediction_asset(
    *,
    predictions_id: str,
    name: str,
    short_description: str,
    model_description: str,
    output_dir: Path,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    latency_p50: float,
    entity_accuracy_gold92: float,
    wer_gold92: float,
) -> None:
    """Write a complete prediction asset folder."""
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    anomaly_clips = {CYRILLIC_ANOMALY_CLIP}

    # Write predictions-gold92.jsonl
    pred_path = files_dir / "predictions-gold92.jsonl"
    with pred_path.open("w", encoding="utf-8") as fh:
        for clip in clips:
            hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
            hyp = str(hyp_raw)
            latency = float(transcripts.get(clip.clip_id, {}).get("latency_seconds", 0.0))
            is_anomaly = clip.clip_id in anomaly_clips

            wer = compute_clip_wer(clip.reference_text, hyp)
            ea = compute_entity_accuracy(clip=clip, hypothesis=hyp, is_anomaly=is_anomaly)

            entity_spans_ref = clip.entity_spans
            entity_spans_pred = [
                {
                    "text": span["text"],
                    "type": span["type"],
                    "found": normalise(span["text"]) in normalise(hyp),
                }
                for span in entity_spans_ref
            ]

            record: dict[str, Any] = {
                "clip_id": clip.clip_id,
                "reference": clip.reference_text,
                "hypothesis": hyp,
                "accent_group": clip.accent_group,
                "entity_spans_reference": entity_spans_ref,
                "entity_spans_predicted": entity_spans_pred,
                "entity_accuracy": ea,
                "wer": round(wer, 6),
                "latency_seconds": round(latency, 4),
                "anomaly_flag": "cyrillic_ground_truth" if is_anomaly else None,
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

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
            "Each line is a JSON object with fields: clip_id (string), reference (string, "
            "normalised ground truth), hypothesis (string, model output), accent_group (string, "
            "speaker accent category), entity_spans_reference (list of {text, type, start, end}), "
            "entity_spans_predicted (list of {text, type, found: bool}), entity_accuracy "
            "(float or null for anomaly clips), wer (float, word error rate for this clip), "
            "latency_seconds (float, end-to-end inference time), anomaly_flag (string or null)."
        ),
        "instance_count": 93,
        "metrics_at_creation": {
            "entity_accuracy_gold92": round(entity_accuracy_gold92, 6),
            "wer_gold92": round(wer_gold92, 6),
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
        "categories": ["stt-evaluation", "whisper-finetuning"],
        "created_by_task": "t0004_vocabulary_biasing_experiment",
        "date_created": "2026-06-23",
    }

    with (output_dir / "details.json").open("w", encoding="utf-8") as fh:
        json.dump(details, fh, indent=2, ensure_ascii=False)

    print(f"Wrote {pred_path} ({len(clips)} records)")
    print(f"Wrote {output_dir / 'details.json'}")


def write_description_md(
    *,
    output_dir: Path,
    predictions_id: str,
    name: str,
    model_description_long: str,
    entity_accuracy: float,
    wer: float,
    latency_p50: float,
) -> None:
    """Write description.md for a biased prediction asset."""
    content = f"""---
spec_version: "2"
predictions_id: "{predictions_id}"
documented_by_task: "t0004_vocabulary_biasing_experiment"
date_documented: "2026-06-23"
---
# {name}

## Metadata

* **Name**: {name}
* **Model**: {model_description_long}
* **Datasets**: stt-benchmark-gold-92
* **Format**: jsonl
* **Instances**: 93
* **Created by**: t0004_vocabulary_biasing_experiment

## Overview

These predictions capture the per-instance output of {model_description_long} on the gold-92
benchmark, using vocabulary biasing via Whisper's `initial_prompt` parameter. The experiment is
part of task t0004 which ablates the effect of a 31-term domain vocabulary injected as initial
context to Whisper before decoding begins.

The gold-92 benchmark contains 93 annotated WAV clips from Rezolve production investor-relations
voice sessions, with accented English speakers across three source categories: `clean_voices`
(speaker-narrated IR Q&A), `production` (live production session captures), and `error_cases`
(known hard cases). The vocabulary prompt includes key brand names (Rezolve, brainpowa), product
lines (Brain Commerce, Brain Checkout), partner names (GroupBy, Bluedot, ViSenze), and people
names (Dan Wagner, Arthur Yao, etc.) that appear in the domain.

These biased predictions are compared against the t0002 baselines (without initial_prompt) to
quantify how much domain vocabulary injection improves entity accuracy, particularly on the 31
domain-specific terms. The comparison reveals whether Whisper's attention to these terms can
be meaningfully shifted by context priming alone, without any fine-tuning or training.

One clip (`error_en_0005`) is flagged with `anomaly_flag: "cyrillic_ground_truth"` due to its
Cyrillic ground truth in `gold_set.jsonl`. The canonical `ground_truth.jsonl` reference for this
clip is a normal English sentence; this clip is included in WER computation but excluded from the
aggregate entity accuracy calculation via `np.nanmean`.

## Model

{model_description_long} run locally via `faster-whisper` (CTranslate2 INT8 quantization, CPU
inference, language='en') on Apple M5 Mac. The key difference from the t0002 baseline is the
addition of `initial_prompt` set to the 31-term domain vocabulary string:

```
Rezolve, Rezolve Ai, NASDAQ, brainpowa, Agentic, Brain Checkout, Brain Commerce, Purchase Suite,
GroupBy, Bluedot, ViSenze, Smartpay, Subsquid, CrownPeak, Hallucinations, Zero Hallucinations,
Dan Wagner, Arthur Yao, Richard Burchill, Crispin Lowery, Salman Ahmad, Sauvik Banerjjee,
Mark Turner, Peter Vesco, Urmee Khan, Anthony Sharp, David Wright, Steve Perry, Derek Smith,
Justin King, Christian Angermayer
```

The `initial_prompt` is passed as a fake prior transcript, influencing the decoder's attention
toward these token sequences. This is Whisper's built-in mechanism for domain adaptation without
any weight updates. Configuration: `beam_size=5`, `language="en"`, `device="cpu"`,
`compute_type="int8"`. The model was warmed up on 3 throwaway clips before recording latencies.

## Data

The evaluation dataset is `stt-benchmark-gold-92`, produced by task `t0001_stt_benchmark`. It
contains 93 WAV audio clips with annotated ground-truth transcripts and entity spans, drawn from
three source categories:

| Source | N clips | Description |
| --- | --- | --- |
| `clean_voices` | ~40 | Speaker-narrated IR Q&A, 6 named speakers, ~5-7 clips each |
| `production` | ~40 | Live Rezolve production voice session captures |
| `error_cases` | ~13 | Known hard cases including accented, adversarial, multilingual inputs |

No preprocessing was applied to audio files before passing to faster-whisper.

## Prediction Format

Each line of `files/predictions-gold92.jsonl` is a JSON object:

```json
{{
  "clip_id": "French_NoemieMarciano__en-NoemieMarciano-q01",
  "reference": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "hypothesis": "How does Rezolve AI improve product discovery for enterprise retailers?",
  "accent_group": "clean_voices",
  "entity_spans_reference": [{{"text": "Rezolve AI", "type": "brand", "start": 8, "end": 18}}],
  "entity_spans_predicted": [{{"text": "Rezolve AI", "type": "brand", "found": true}}],
  "entity_accuracy": 1.0,
  "wer": 0.0,
  "latency_seconds": 5.32,
  "anomaly_flag": null
}}
```

Fields:

* `clip_id` — unique clip identifier matching the WAV filename stem
* `reference` — canonical ground truth from `ground_truth.jsonl`
* `hypothesis` — raw Whisper output with vocabulary biasing (not normalised)
* `accent_group` — speaker source category (`clean_voices`, `production`, `error_cases`)
* `entity_spans_reference` — list of detected action-critical entity spans
* `entity_spans_predicted` — same spans with `found: bool` indicating presence in hypothesis
* `entity_accuracy` — fraction of entity spans correctly reproduced (null for anomaly clips)
* `wer` — per-clip word error rate after normalisation (lowercase + strip punctuation)
* `latency_seconds` — end-to-end inference time measured with `time.perf_counter()`
* `anomaly_flag` — `"cyrillic_ground_truth"` for `error_en_0005`, null otherwise

## Metrics

| Metric | Value |
| --- | --- |
| entity_accuracy_gold92 | {entity_accuracy:.4f} |
| wer_gold92 | {wer:.4f} |
| latency_p50_seconds | {latency_p50:.2f}s |

Compare with t0002 baselines: Whisper Large v3 baseline achieved entity_accuracy=0.2518,
wer=0.1003; Whisper turbo baseline achieved entity_accuracy=0.2518, wer=0.1063.

## Main Ideas

* Vocabulary biasing via `initial_prompt` is a zero-cost inference-time intervention that requires
  no model fine-tuning, making it immediately applicable in production deployments
* The 31-term domain vocabulary specifically targets brand names, product lines, and people names
  that Whisper's general training data rarely surfaces in investor-relations contexts
* Performance gain (if any) on `entity_accuracy_domain_vocab` directly quantifies the impact of
  vocabulary injection on the exact terms that matter for voice commerce entity recognition
* Any WER regression from biasing is a risk — the initial_prompt can cause Whisper to hallucinate
  terms not spoken if the context is too domain-specific

## Summary

These predictions capture Whisper inference on gold-92 with domain vocabulary injected as
`initial_prompt`. The experiment ablates whether Whisper's decoder can be guided to prefer
domain-specific spellings of brands and names without any weight updates. The 31-term vocabulary
covers the key entities in the Rezolve IR domain that appear most frequently in production voice
sessions.

The headline finding (available in `tasks/t0004_vocabulary_biasing_experiment/results/metrics.json`)
shows the effect size of vocabulary biasing on entity_accuracy_gold92 and
entity_accuracy_domain_vocab relative to the t0002 baselines. Even small improvements in entity
accuracy are meaningful for
the voice commerce use case, where downstream intent routing depends critically on correct entity
recognition.
"""
    desc_path = output_dir / "description.md"
    with desc_path.open("w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Wrote {desc_path}")


def load_transcripts(path: Path) -> dict[str, dict[str, Any]]:
    """Load transcript JSON file, returning dict keyed by clip_id."""
    with path.open(encoding="utf-8") as fh:
        records: list[dict[str, Any]] = json.load(fh)
    return {r["clip_id"]: r for r in records}


def compute_aggregate_metrics(
    *, clips: list[GoldClip], transcripts: dict[str, dict[str, Any]]
) -> tuple[float, float, float]:
    """Compute entity accuracy, WER, and latency p50."""
    import numpy as np

    anomaly_clips = {CYRILLIC_ANOMALY_CLIP}
    entity_scores: list[float | None] = []
    latencies: list[float] = []

    references: list[str] = []
    hypotheses: list[str] = []

    for clip in clips:
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = str(hyp_raw)
        latencies.append(float(transcripts.get(clip.clip_id, {}).get("latency_seconds", 0.0)))
        references.append(normalise(clip.reference_text))
        hypotheses.append(normalise(hyp))
        ea = compute_entity_accuracy(
            clip=clip, hypothesis=hyp, is_anomaly=clip.clip_id in anomaly_clips
        )
        entity_scores.append(ea)

    entity_np = np.array([np.nan if s is None else s for s in entity_scores])
    entity_accuracy = float(np.nanmean(entity_np))

    result = jiwer.process_words(references, hypotheses)
    total_ref = result.hits + result.substitutions + result.deletions
    total_err = result.substitutions + result.deletions + result.insertions
    wer = total_err / total_ref if total_ref > 0 else 0.0

    latency_p50 = float(np.percentile(latencies, 50)) if latencies else 0.0

    return entity_accuracy, wer, latency_p50


def main() -> None:
    """Write prediction assets for both biased variants."""
    if not WHISPER_BIASED_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Biased transcripts not found at {WHISPER_BIASED_TRANSCRIPTS}. "
            "Run code/run_whisper_biased.py first."
        )
    if not WHISPER_TURBO_BIASED_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Turbo biased transcripts not found at {WHISPER_TURBO_BIASED_TRANSCRIPTS}. "
            "Run code/run_whisper_turbo_biased.py first."
        )

    if not MOONSHINE_TRANSCRIPTS.exists():
        raise RuntimeError(
            f"Moonshine transcripts not found at {MOONSHINE_TRANSCRIPTS}. "
            "Run code/run_moonshine_small.py first."
        )

    clips = load_gold92()
    whisper_biased = load_transcripts(WHISPER_BIASED_TRANSCRIPTS)
    turbo_biased = load_transcripts(WHISPER_TURBO_BIASED_TRANSCRIPTS)

    # Compute aggregate metrics for each variant
    ea_lv3, wer_lv3, lat_lv3 = compute_aggregate_metrics(clips=clips, transcripts=whisper_biased)
    ea_turbo, wer_turbo, lat_turbo = compute_aggregate_metrics(
        clips=clips, transcripts=turbo_biased
    )

    print("=== Whisper Large v3 biased ===")
    write_prediction_asset(
        predictions_id="whisper-large-v3-biased",
        name="Whisper Large v3 + Vocabulary Bias on Gold-92",
        short_description=(
            "Per-instance Whisper Large v3 STT predictions on gold-92 with 31-term domain "
            "vocabulary injected via initial_prompt, ablating vocabulary biasing against "
            "t0002 baseline."
        ),
        model_description=(
            "OpenAI Whisper Large v3 (~1.5B parameters) run locally via faster-whisper "
            "(CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to "
            "a 31-term domain vocabulary string covering Rezolve brand names, product lines, "
            "and key people. No fine-tuning applied."
        ),
        output_dir=WHISPER_BIASED_PREDICTIONS_DIR,
        clips=clips,
        transcripts=whisper_biased,
        latency_p50=lat_lv3,
        entity_accuracy_gold92=ea_lv3,
        wer_gold92=wer_lv3,
    )
    write_description_md(
        output_dir=WHISPER_BIASED_PREDICTIONS_DIR,
        predictions_id="whisper-large-v3-biased",
        name="Whisper Large v3 + Vocabulary Bias on Gold-92",
        model_description_long="Whisper Large v3 (~1.5B parameters, faster-whisper INT8)",
        entity_accuracy=ea_lv3,
        wer=wer_lv3,
        latency_p50=lat_lv3,
    )

    print("\n=== Whisper turbo biased ===")
    write_prediction_asset(
        predictions_id="whisper-turbo-biased",
        name="Whisper Turbo + Vocabulary Bias on Gold-92",
        short_description=(
            "Per-instance Whisper turbo STT predictions on gold-92 with 31-term domain "
            "vocabulary injected via initial_prompt, ablating vocabulary biasing against "
            "t0002 baseline."
        ),
        model_description=(
            "OpenAI Whisper turbo (~809M parameters) run locally via faster-whisper "
            "(CTranslate2 INT8, CPU, language='en', beam_size=5) with initial_prompt set to "
            "a 31-term domain vocabulary string covering Rezolve brand names, product lines, "
            "and key people. No fine-tuning applied."
        ),
        output_dir=WHISPER_TURBO_BIASED_PREDICTIONS_DIR,
        clips=clips,
        transcripts=turbo_biased,
        latency_p50=lat_turbo,
        entity_accuracy_gold92=ea_turbo,
        wer_gold92=wer_turbo,
    )
    write_description_md(
        output_dir=WHISPER_TURBO_BIASED_PREDICTIONS_DIR,
        predictions_id="whisper-turbo-biased",
        name="Whisper Turbo + Vocabulary Bias on Gold-92",
        model_description_long="Whisper turbo (~809M parameters, faster-whisper INT8)",
        entity_accuracy=ea_turbo,
        wer=wer_turbo,
        latency_p50=lat_turbo,
    )

    moonshine = load_transcripts(MOONSHINE_TRANSCRIPTS)
    ea_moon, wer_moon, lat_moon = compute_aggregate_metrics(clips=clips, transcripts=moonshine)

    print("\n=== Moonshine base (no biasing) ===")
    write_prediction_asset(
        predictions_id="moonshine-base-gold92",
        name="Moonshine Base on Gold-92 (no vocabulary biasing)",
        short_description=(
            "Per-instance Moonshine base ONNX STT predictions on gold-92. No vocabulary biasing "
            "— Moonshine does not support initial_prompt. Plain baseline for comparison with "
            "biased Whisper variants."
        ),
        model_description=(
            "UsefulSensors/moonshine-base (~60M parameters) run via useful-moonshine-onnx "
            "(ONNX, CPU, 16 kHz). No vocabulary biasing supported. Note: UsefulSensors has no "
            "'small' variant; 'base' is the closest equivalent."
        ),
        output_dir=MOONSHINE_PREDICTIONS_DIR,
        clips=clips,
        transcripts=moonshine,
        latency_p50=lat_moon,
        entity_accuracy_gold92=ea_moon,
        wer_gold92=wer_moon,
    )
    write_description_md(
        output_dir=MOONSHINE_PREDICTIONS_DIR,
        predictions_id="moonshine-base-gold92",
        name="Moonshine Base on Gold-92 (no vocabulary biasing)",
        model_description_long="UsefulSensors Moonshine base (~60M parameters, ONNX CPU)",
        entity_accuracy=ea_moon,
        wer=wer_moon,
        latency_p50=lat_moon,
    )

    print("\nDone. All prediction assets written.")


if __name__ == "__main__":
    main()
