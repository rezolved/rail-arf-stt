"""Metric utilities for t0008_moonshine_v2_benchmark.

Functions copied (not imported) from tasks/t0004_vocabulary_biasing_experiment/code/.
Also includes GoldClip dataclass and load_gold92() function from t0004 load_dataset.py.
"""

from __future__ import annotations

import json
import re
import string
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jiwer
import numpy as np
from scipy.stats import bootstrap  # type: ignore[attr-defined]

from tasks.t0008_moonshine_v2_benchmark.code.paths import (
    GOLD92_AUDIO,
    GOLD_SET_JSONL,
    GROUND_TRUTH_JSONL,
)

# Bootstrap config constants
BCa_N_RESAMPLES = 10_000
BCa_RANDOM_STATE = 42  # Per plan: use 42 (not the framework default 12345)

# Domain vocabulary (31 terms)
DOMAIN_VOCAB: list[str] = [
    "Rezolve",
    "Rezolve Ai",
    "NASDAQ",
    "brainpowa",
    "Agentic",
    "Brain Checkout",
    "Brain Commerce",
    "Purchase Suite",
    "GroupBy",
    "Bluedot",
    "ViSenze",
    "Smartpay",
    "Subsquid",
    "CrownPeak",
    "Hallucinations",
    "Zero Hallucinations",
    "Dan Wagner",
    "Arthur Yao",
    "Richard Burchill",
    "Crispin Lowery",
    "Salman Ahmad",
    "Sauvik Banerjjee",
    "Mark Turner",
    "Peter Vesco",
    "Urmee Khan",
    "Anthony Sharp",
    "David Wright",
    "Steve Perry",
    "Derek Smith",
    "Justin King",
    "Christian Angermayer",
]

CYRILLIC_ANOMALY_CLIP = "error_en_0005"


@dataclass(frozen=True, slots=True)
class GoldClip:
    """A single gold-92 benchmark clip with reference annotation."""

    clip_id: str
    reference_text: str
    entity_spans: list[dict[str, Any]]
    accent_group: str
    audio_path: Path


def normalise(text: str) -> str:
    """Lowercase and strip punctuation. Applied to both reference and hypothesis."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def bca_ci(
    per_clip_scores: np.ndarray,
    *,
    n_resamples: int = BCa_N_RESAMPLES,
    random_state: int = BCa_RANDOM_STATE,
) -> tuple[float, float]:
    """Compute BCa bootstrap 95% CI with NaN guard fallback to percentile."""
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
            raise ValueError("BCa returned NaN — falling back to percentile")
        return low, high
    except Exception:  # noqa: BLE001
        warnings.warn("BCa NaN guard triggered — using percentile bootstrap", stacklevel=2)
        result = bootstrap(
            (per_clip_scores,),
            statistic=np.mean,
            method="percentile",
            n_resamples=n_resamples,
            random_state=random_state,
        )
        return (
            float(result.confidence_interval.low),
            float(result.confidence_interval.high),
        )


def compute_per_clip_entity_accuracy(
    *,
    clip: GoldClip,
    hypothesis: str,
    is_anomaly: bool,
) -> float | None:
    """Compute entity accuracy for a single clip (all-or-nothing, Caubriere 2020).

    Returns None for anomaly clips (excluded from aggregate via np.nanmean).
    Returns 0.0 for clips with no entity spans (neutral contribution).
    """
    if is_anomaly:
        return None

    entity_spans = clip.entity_spans
    if len(entity_spans) == 0:
        return 0.0

    hyp_normalised = normalise(hypothesis)
    correct = 0
    total = len(entity_spans)

    for span in entity_spans:
        span_text: str = span["text"]
        span_normalised = normalise(span_text)
        # All-or-nothing: exact span must appear in normalised hypothesis
        if span_normalised in hyp_normalised:
            correct += 1

    return correct / total


def compute_wer_batch(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute full-transcript WER over all clips (batch jiwer call).

    Returns (aggregate_wer, per_clip_wer_list).
    """
    references: list[str] = []
    hypotheses: list[str] = []

    for clip in clips:
        ref = normalise(clip.reference_text)
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = normalise(str(hyp_raw))
        references.append(ref)
        hypotheses.append(hyp)

    result = jiwer.process_words(references, hypotheses)

    total_ref_words = result.hits + result.substitutions + result.deletions
    total_errors = result.substitutions + result.deletions + result.insertions
    aggregate_wer = total_errors / total_ref_words if total_ref_words > 0 else 0.0

    # Per-clip WER via individual processing
    per_clip_wer: list[float] = []
    for ref, hyp in zip(references, hypotheses, strict=True):
        clip_result = jiwer.process_words([ref], [hyp])
        ref_words = clip_result.hits + clip_result.substitutions + clip_result.deletions
        errors = clip_result.substitutions + clip_result.deletions + clip_result.insertions
        per_clip_wer.append(errors / ref_words if ref_words > 0 else 0.0)

    return aggregate_wer, per_clip_wer


def compute_action_critical_wer(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute action-critical WER restricted to entity-span reference words."""
    total_hits = total_subs = total_dels = 0
    per_clip: list[float] = []

    for clip in clips:
        entity_spans = clip.entity_spans
        if len(entity_spans) == 0:
            per_clip.append(0.0)
            continue

        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp_words = set(normalise(str(hyp_raw)).split())

        clip_hits = clip_subs = clip_dels = 0

        for span in entity_spans:
            span_text: str = span["text"]
            span_words = normalise(span_text).split()
            for word in span_words:
                if word in hyp_words:
                    clip_hits += 1
                else:
                    clip_dels += 1

        n = clip_hits + clip_dels + clip_subs
        clip_wer = (clip_dels + clip_subs) / n if n > 0 else 0.0
        per_clip.append(clip_wer)

        total_hits += clip_hits
        total_subs += clip_subs
        total_dels += clip_dels

    total_n = total_hits + total_subs + total_dels
    aggregate = (total_subs + total_dels) / total_n if total_n > 0 else 0.0
    return aggregate, per_clip


def compute_intent_preservation(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
) -> tuple[float, list[float]]:
    """Compute intent preservation using rule-based proxy.

    An utterance preserves intent if at least one entity span from the reference
    appears in the hypothesis (set intersection non-empty).
    """
    per_clip: list[float] = []

    for clip in clips:
        entity_spans = clip.entity_spans
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp = normalise(str(hyp_raw))

        if len(entity_spans) == 0:
            per_clip.append(1.0)
            continue

        matched_any = False
        for span in entity_spans:
            span_text: str = span["text"]
            if normalise(span_text) in hyp:
                matched_any = True
                break

        per_clip.append(1.0 if matched_any else 0.0)

    aggregate = float(np.mean(per_clip)) if len(per_clip) > 0 else 0.0
    return aggregate, per_clip


def compute_latency_p50(transcripts: dict[str, dict[str, Any]]) -> float:
    """Compute p50 latency from transcript records."""
    latencies = [float(r.get("latency_seconds", 0.0)) for r in transcripts.values()]
    return float(np.percentile(latencies, 50)) if len(latencies) > 0 else 0.0


def compute_entity_accuracy_domain_vocab(
    *,
    clips: list[GoldClip],
    transcripts: dict[str, dict[str, Any]],
    domain_vocab: list[str],
) -> tuple[float, list[float | None]]:
    """Compute entity accuracy restricted to domain vocabulary terms.

    For each clip that contains at least one domain vocabulary term in its reference:
    - Check which domain terms from its reference appear correctly in the hypothesis
    - entity_accuracy_domain_vocab = (correct matches) / (total domain term occurrences in refs)

    Returns (aggregate, per_clip_scores) where per_clip_scores is None for clips
    that have no domain vocab terms in their reference.
    """
    domain_vocab_normalised = [normalise(term) for term in domain_vocab]

    per_clip: list[float | None] = []
    total_correct = 0
    total_occurrences = 0

    for clip in clips:
        ref_normalised = normalise(clip.reference_text)
        hyp_raw = transcripts.get(clip.clip_id, {}).get("hypothesis", "")
        hyp_normalised = normalise(str(hyp_raw))

        # Find which domain terms appear in this clip's reference
        clip_domain_terms_in_ref = [
            term for term in domain_vocab_normalised if term in ref_normalised
        ]

        if len(clip_domain_terms_in_ref) == 0:
            per_clip.append(None)  # Clip has no domain vocab terms — exclude from aggregate
            continue

        # Check which appear in hypothesis
        clip_correct = sum(1 for term in clip_domain_terms_in_ref if term in hyp_normalised)
        clip_total = len(clip_domain_terms_in_ref)

        per_clip.append(clip_correct / clip_total if clip_total > 0 else 0.0)
        total_correct += clip_correct
        total_occurrences += clip_total

    aggregate = total_correct / total_occurrences if total_occurrences > 0 else 0.0
    return aggregate, per_clip


def _load_gold_set_accent_groups(gold_set_path: Path) -> dict[str, str]:
    """Load accent group mapping from gold_set.jsonl."""
    accent_groups: dict[str, str] = {}
    with gold_set_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            clip_id: str = record["clip_id"]
            source: str = record.get("source", "unknown")
            accent_groups[clip_id] = source
    return accent_groups


def _infer_entity_spans(reference_text: str, clip_id: str) -> list[dict[str, Any]]:  # noqa: ARG001
    """Infer entity spans from reference text using known domain entity patterns.

    This is a heuristic approach: since ground_truth.jsonl does not include
    entity_spans, we detect known entity patterns from the Rezolve IR domain.
    """
    spans: list[dict[str, Any]] = []
    text = reference_text

    # Known brand/product entities in the Rezolve IR domain
    entity_patterns: list[tuple[str, str]] = [
        (r"\bRezolve AI\b", "brand"),
        (r"\bRezolve\b", "brand"),
        (r"\bbrainpowa\b", "product"),
        (r"\bBrain Commerce\b", "product"),
        (r"\bBrainpowa\b", "product"),
        (r"\bBrain Power\b", "product"),
        (r"\bSalesforce Commerce Cloud\b", "product"),
        (r"\bShopify Plus\b", "product"),
        (r"\bAdobe Commerce\b", "product"),
        (r"\bAdobe\b", "brand"),
        (r"\bShopify\b", "brand"),
        (r"\bSalesforce\b", "brand"),
        (r"\bAmazon\b", "brand"),
        (r"\bGoogle\b", "brand"),
        (r"\bMicrosoft\b", "brand"),
        (r"\b20-F\b", "ir_term"),
        (r"\b10-K\b", "ir_term"),
        (r"\bSEO\b", "ir_term"),
        (r"\bAPI\b", "ir_term"),
        (r"\bAI\b", "ir_term"),
        (r"\bROI\b", "ir_term"),
        (r"\bKPI\b", "ir_term"),
    ]

    for pattern, entity_type in entity_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            spans.append(
                {
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "type": entity_type,
                }
            )

    return spans


def load_gold92(
    *,
    ground_truth_path: Path = GROUND_TRUTH_JSONL,
    gold_set_path: Path = GOLD_SET_JSONL,
    audio_dir: Path = GOLD92_AUDIO,
) -> list[GoldClip]:
    """Load all 93 gold-92 benchmark clips.

    Uses ground_truth.jsonl as canonical reference. Loads accent_group from
    gold_set.jsonl for stratification. Infers entity_spans from reference text
    using domain heuristics (ground_truth.jsonl does not include explicit spans).

    Returns:
        List of GoldClip objects, one per clip, sorted by clip_id.
    """
    # Load accent groups from gold_set.jsonl for stratification
    accent_groups = _load_gold_set_accent_groups(gold_set_path=gold_set_path)

    clips: list[GoldClip] = []
    with ground_truth_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record: dict[str, Any] = json.loads(line)
            clip_id: str = record["clip_id"]
            reference_text: str = record["ground_truth"]

            if clip_id == CYRILLIC_ANOMALY_CLIP:
                warnings.warn(
                    f"Clip {clip_id} has Cyrillic ground truth '{reference_text}' — "
                    "known annotation error. Including in run with anomaly flag.",
                    stacklevel=2,
                )

            entity_spans = _infer_entity_spans(reference_text=reference_text, clip_id=clip_id)
            accent_group = accent_groups.get(clip_id, "unknown")
            audio_path = audio_dir / f"{clip_id}.wav"

            clips.append(
                GoldClip(
                    clip_id=clip_id,
                    reference_text=reference_text,
                    entity_spans=entity_spans,
                    accent_group=accent_group,
                    audio_path=audio_path,
                )
            )

    clips.sort(key=lambda c: c.clip_id)
    return clips
