"""Hallucination detection for STT outputs using BoH top-30 patterns.

Uses Aho-Corasick string matching (via pyahocorasick) when available,
falling back to substring search. Detects known Whisper hallucination
patterns from the DSP-AGH/ICASSP2025_Whisper_Hallucination dataset.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tasks.t0014_granite_short_clip_robustness.code.constants import BOH_FALLBACK_PATTERNS


def load_boh_patterns(csv_path: Path) -> list[str]:
    """Load BoH hallucination patterns from CSV file.

    The DSP-AGH CSV has columns: pattern, count (or similar).
    Falls back to hardcoded patterns if file does not exist.
    """
    if not csv_path.exists():
        print(f"WARNING: BoH CSV not found at {csv_path}, using fallback patterns")
        return BOH_FALLBACK_PATTERNS

    patterns: list[str] = []
    try:
        with csv_path.open(encoding="utf-8") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                pattern = row[0].strip()
                if pattern and not pattern.startswith("#"):
                    patterns.append(pattern)
    except Exception as exc:
        print(f"WARNING: Failed to parse BoH CSV ({exc}), using fallback patterns")
        return BOH_FALLBACK_PATTERNS

    if len(patterns) < 5:
        print(f"WARNING: Only {len(patterns)} BoH patterns loaded, using fallback")
        return BOH_FALLBACK_PATTERNS

    # Take top 30
    return patterns[:30]


class HallucinationDetector:
    """Detect hallucinations in STT transcripts using BoH pattern matching."""

    def __init__(self, patterns: list[str]) -> None:
        self._patterns = [p.lower() for p in patterns if p.strip()]
        self._automaton: object | None = None
        self._build_automaton()

    def _build_automaton(self) -> None:
        try:
            import ahocorasick  # type: ignore[import-untyped]

            A = ahocorasick.Automaton()
            for idx, pattern in enumerate(self._patterns):
                A.add_word(pattern, (idx, pattern))
            A.make_automaton()
            self._automaton = A
            print(f"BoH: Aho-Corasick automaton built with {len(self._patterns)} patterns")
        except ImportError:
            print("WARNING: ahocorasick not available, using substring search")

    def matches_pattern(self, text: str) -> bool:
        """Return True if text matches any known hallucination pattern."""
        lower = text.lower()
        if self._automaton is not None:
            for _ in self._automaton.iter(lower):  # type: ignore[union-attr]
                return True
            return False
        # Fallback: substring search
        return any(p in lower for p in self._patterns)

    def is_hallucination(
        self,
        transcript: str,
        reference_text: str,
    ) -> bool:
        """Flag hallucination: non-empty transcript with no reference words and BoH match.

        Criteria (all three must be true):
        1. transcript is non-empty after stripping
        2. transcript shares no words with reference (or reference is empty)
        3. transcript matches a known BoH hallucination pattern
        """
        text = transcript.strip()
        if not text:
            return False

        # If reference is empty (edge cases), any non-empty output could be hallucination
        # Check only pattern match in that case
        if not reference_text.strip():
            return self.matches_pattern(text)

        # Check if any reference word appears in transcript
        ref_words = {w.lower().strip(".,!?;:'\"") for w in reference_text.split() if len(w) > 2}
        trans_words = {w.lower().strip(".,!?;:'\"") for w in text.split()}
        has_reference_word = bool(ref_words & trans_words)

        if has_reference_word:
            return False

        return self.matches_pattern(text)
