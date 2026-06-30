"""Synthesize short clips from gold-92 WAV files for short-clip robustness testing.

Creates 40-60 short WAV clips (0.5-3.0 s) trimmed from gold-92 audio files at 6 duration bins.
Also creates 2 edge-case clips: 0.5 s silence and 0.5 s background noise.
Saves clips to data/short_clips/ and metadata to data/short_clips_metadata.jsonl.

Usage:
    uv run python -m arf.scripts.utils.run_with_logs --task-id t0014_granite_short_clip_robustness \
        -- uv run python -u tasks/t0014_granite_short_clip_robustness/code/synthesize_clips.py
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from tasks.t0014_granite_short_clip_robustness.code.constants import (
    CLIPS_PER_BIN,
    DURATION_BINS,
    SAMPLE_RATE,
)
from tasks.t0014_granite_short_clip_robustness.code.paths import (
    GOLD92_AUDIO_DIR,
    GOLD92_GROUND_TRUTH,
    METADATA_JSONL,
    SHORT_CLIPS_DIR,
)


@dataclass(frozen=True, slots=True)
class ClipMetadata:
    clip_id: str
    source_clip_id: str
    duration_s: float
    reference_text: str


def load_ground_truth() -> dict[str, str]:
    """Load gold-92 ground truth transcripts keyed by clip_id."""
    gt: dict[str, str] = {}
    with GOLD92_GROUND_TRUTH.open(encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line.strip())
            gt[record["clip_id"]] = record["ground_truth"]
    return gt


def load_audio_float32(path: Path) -> tuple[np.ndarray, int]:
    """Load WAV file as float32 mono array."""
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    return audio, sr


def get_duration(path: Path) -> float:
    """Get audio duration in seconds."""
    info = sf.info(str(path))
    return info.duration


def save_wav(audio: np.ndarray, path: Path, sample_rate: int = SAMPLE_RATE) -> None:
    """Save float32 audio as 16kHz mono PCM-16 WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm_int16 = (audio * 32767).clip(-32768, 32767).astype(np.int16)
    sf.write(str(path), pcm_int16, samplerate=sample_rate, subtype="PCM_16")


def estimate_rms(audio: np.ndarray) -> float:
    """Estimate RMS energy of audio clip."""
    return float(np.sqrt(np.mean(audio**2)))


def main() -> None:
    random.seed(42)
    np.random.seed(42)

    SHORT_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    ground_truth = load_ground_truth()
    print(f"Loaded {len(ground_truth)} gold-92 ground truth entries")

    # Collect available audio files with their durations
    audio_files = sorted(GOLD92_AUDIO_DIR.glob("*.wav"))
    print(f"Found {len(audio_files)} gold-92 audio files")

    clip_info: list[tuple[str, float, float]] = []  # (clip_id, duration_s, rms)
    for wav_path in audio_files:
        clip_id = wav_path.stem
        dur = get_duration(wav_path)
        # Quick RMS estimate (load first 1s only)
        audio, _ = load_audio_float32(wav_path)
        rms = estimate_rms(audio[:SAMPLE_RATE])
        clip_info.append((clip_id, dur, rms))

    clip_info.sort(key=lambda x: x[1])  # sort by duration
    print(f"Duration range: {clip_info[0][1]:.2f}s to {clip_info[-1][1]:.2f}s")

    all_metadata: list[ClipMetadata] = []
    used_sources: dict[float, list[str]] = {b: [] for b in DURATION_BINS}

    # For each duration bin, select CLIPS_PER_BIN source clips
    for target_dur in DURATION_BINS:
        # All source clips are long enough to trim
        eligible = [(cid, dur, rms) for cid, dur, rms in clip_info if dur >= target_dur + 0.1]
        if len(eligible) < CLIPS_PER_BIN:
            print(f"WARNING: only {len(eligible)} clips eligible for {target_dur}s bin")

        # Select variety: speech-rich (high RMS), silence-heavy (low RMS), and random
        eligible_sorted_rms = sorted(eligible, key=lambda x: x[2])
        selected: list[str] = []

        # 2 lowest RMS (silence-heavy), 2 highest RMS (speech-rich), rest random
        low_rms = [cid for cid, _, _ in eligible_sorted_rms[:3]]
        high_rms = [cid for cid, _, _ in eligible_sorted_rms[-3:]]
        all_cids = [cid for cid, _, _ in eligible]

        for cid in high_rms[:2]:
            if cid not in selected:
                selected.append(cid)
        for cid in low_rms[:2]:
            if cid not in selected:
                selected.append(cid)

        # Fill rest randomly without replacement
        remaining = [c for c in all_cids if c not in selected]
        random.shuffle(remaining)
        for cid in remaining:
            if len(selected) >= CLIPS_PER_BIN:
                break
            selected.append(cid)

        used_sources[target_dur] = selected

        for source_id in selected:
            wav_path = GOLD92_AUDIO_DIR / f"{source_id}.wav"
            audio, sr = load_audio_float32(wav_path)

            # Trim to target_dur from clip start
            n_samples = int(target_dur * sr)
            trimmed = audio[:n_samples]

            clip_id = f"{source_id}_{target_dur}s"
            out_path = SHORT_CLIPS_DIR / f"{clip_id}.wav"
            save_wav(trimmed, out_path, sample_rate=sr)

            ref_text = ground_truth.get(source_id, "")
            all_metadata.append(
                ClipMetadata(
                    clip_id=clip_id,
                    source_clip_id=source_id,
                    duration_s=target_dur,
                    reference_text=ref_text,
                )
            )
            print(
                f"  Created {clip_id}: {target_dur}s from {source_id} (ref: '{ref_text[:40]}...')"
            )

    # Edge case 1: 0.5 s silence
    silence = np.zeros(int(0.5 * SAMPLE_RATE), dtype=np.float32)
    silence_path = SHORT_CLIPS_DIR / "edge_silence_0.5s.wav"
    save_wav(silence, silence_path)
    all_metadata.append(
        ClipMetadata(
            clip_id="edge_silence_0.5s",
            source_clip_id="synthetic",
            duration_s=0.5,
            reference_text="",
        )
    )
    print("  Created edge_silence_0.5s: 0.5s synthetic silence")

    # Edge case 2: 0.5 s background noise (noisiest gold clip — highest overall RMS)
    noisiest_cid = sorted(clip_info, key=lambda x: x[2], reverse=True)[0][0]
    noise_path = GOLD92_AUDIO_DIR / f"{noisiest_cid}.wav"
    noise_audio, _ = load_audio_float32(noise_path)
    noise_clip = noise_audio[: int(0.5 * SAMPLE_RATE)]
    noise_out = SHORT_CLIPS_DIR / "edge_noise_0.5s.wav"
    save_wav(noise_clip, noise_out)
    all_metadata.append(
        ClipMetadata(
            clip_id="edge_noise_0.5s",
            source_clip_id=noisiest_cid,
            duration_s=0.5,
            reference_text=ground_truth.get(noisiest_cid, ""),
        )
    )
    print(f"  Created edge_noise_0.5s: 0.5s noise from {noisiest_cid}")

    # Verify all created files
    wav_count = len(list(SHORT_CLIPS_DIR.glob("*.wav")))
    print(f"\nTotal WAV files created: {wav_count}")
    print(f"Total metadata rows: {len(all_metadata)}")

    if wav_count < 40:
        raise RuntimeError(f"Expected >= 40 clips, got {wav_count}. Check source clip count.")

    # Write metadata JSONL
    METADATA_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with METADATA_JSONL.open("w", encoding="utf-8") as fh:
        for meta in all_metadata:
            fh.write(
                json.dumps(
                    {
                        "clip_id": meta.clip_id,
                        "source_clip_id": meta.source_clip_id,
                        "duration_s": meta.duration_s,
                        "reference_text": meta.reference_text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"Metadata saved → {METADATA_JSONL}")
    print("\nDuration bin summary:")
    for dur in DURATION_BINS:
        count = sum(1 for m in all_metadata if m.duration_s == dur)
        print(f"  {dur}s: {count} clips")
    edge_count = sum(
        1 for m in all_metadata if m.source_clip_id == "synthetic" or "edge" in m.clip_id
    )
    print(f"  Edge cases: {edge_count} clips")


if __name__ == "__main__":
    main()
