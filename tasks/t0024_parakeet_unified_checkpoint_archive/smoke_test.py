"""Smoke test: verify parakeet-unified-v5 checkpoint loads and transcribes."""

import sys
import time
from pathlib import Path

NEMO_PATH = Path(__file__).parent / "assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo"


def main() -> None:
    if not NEMO_PATH.exists():
        print(f"ERROR: checkpoint not found at {NEMO_PATH}")
        print("Run: dvc pull tasks/t0024_parakeet_unified_checkpoint_archive/assets/model/parakeet-unified-v5/files/parakeet-unified-finetuned-best.nemo.dvc")
        sys.exit(1)

    print(f"Checkpoint found: {NEMO_PATH} ({NEMO_PATH.stat().st_size / 1e9:.2f} GB)")

    print("Importing NeMo...")
    try:
        import nemo.collections.asr as nemo_asr
    except ImportError:
        print("ERROR: nemo not installed. Run: pip install nemo_toolkit[asr]")
        sys.exit(1)

    print(f"Loading checkpoint from {NEMO_PATH}...")
    t0 = time.time()
    model = nemo_asr.models.ASRModel.restore_from(str(NEMO_PATH), map_location="cuda")
    model.eval()
    load_time = time.time() - t0
    print(f"Loaded in {load_time:.1f}s")
    print(f"Model type: {type(model).__name__}")

    # Minimal transcribe test with silence (no real audio needed)
    import torch
    import numpy as np

    print("Running transcribe on 1s silence...")
    silence = np.zeros(16000, dtype=np.float32)
    tmp_wav = Path("/tmp/silence_smoke.wav")

    import soundfile as sf
    sf.write(str(tmp_wav), silence, 16000)

    t1 = time.time()
    transcripts = model.transcribe([str(tmp_wav)])
    infer_time = time.time() - t1
    print(f"Transcribed in {infer_time:.2f}s → '{transcripts[0]}'")
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
