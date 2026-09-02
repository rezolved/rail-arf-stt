"""Audio loading and transcription helpers for t0026_biasing_on_finetune_ablation.

Copied from `tasks/t0023_tdt_vs_unified_biasing/code/run.py` lines 145-183 (`load_audio`,
`_decode_output`, `transcribe`), per this task's `plan/plan.md` Approach section (REQ-10).
Adaptation: `clean_eval_v2` audio is already 16kHz (per t0021's DVC recording), so the
`soxr.resample` branch is expected to be unreachable in practice — kept as a guard, not removed.
"""

from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

SAMPLE_RATE: int = 16_000


def load_audio(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1)
    audio = data[:, 0] if data.ndim == 2 else data
    audio = audio.astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE).astype(np.float32)
    return audio


def _decode_output(o: Any, model: Any) -> str:
    if isinstance(o, str):
        return o
    if hasattr(o, "text") and isinstance(o.text, str):
        return o.text
    if hasattr(o, "y_sequence"):
        import torch

        seq = o.y_sequence
        ids = seq.tolist() if isinstance(seq, torch.Tensor | np.ndarray) else list(seq)
        try:
            return model.tokenizer.ids_to_text(ids)
        except Exception:
            return str(o)
    return str(o)


def transcribe(model: Any, clips: list[dict[str, Any]]) -> list[str]:
    audios = [c["audio"] for c in clips]
    outputs = model.transcribe(audios, batch_size=8, verbose=False)
    decoded: list[str] = []
    for o in outputs:
        if isinstance(o, list):
            o = o[0] if len(o) > 0 else ""
        decoded.append(_decode_output(o, model))
    return decoded
