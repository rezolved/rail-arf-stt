"""Optimization benchmark for IBM Granite Speech 4.1 2B biased.

Runs three optimization variants vs the t0007 biased baseline:
  1. NAR variant (granite-speech-4.1-2b-nar) — non-autoregressive, faster generation
  2. torch.compile on base model — JIT compilation, free speed gain
  3. Base model + extended keywords + post-processing — quality improvement

All three use keyword biasing (same DOMAIN_VOCAB prompt as t0007 biased baseline).
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import soundfile as sf
import torch
import torchaudio

from tasks.t0007_ibm_granite_4_1_benchmark.code.constants import (
    DOMAIN_VOCAB,
    MAX_NEW_TOKENS,
    PROMPT_BIASED_PREFIX,
    SAMPLE_RATE,
    WARMUP_CLIPS,
)
from tasks.t0007_ibm_granite_4_1_benchmark.code.load_dataset import (
    CYRILLIC_ANOMALY_CLIP,
    load_gold92,
)
from tasks.t0007_ibm_granite_4_1_benchmark.code.paths import (
    GRANITE_COMPILED_BIASED_TRANSCRIPTS,
    GRANITE_NAR_BIASED_TRANSCRIPTS,
    GRANITE_POSTPROC_BIASED_TRANSCRIPTS,
)

NAR_MODEL_LOCAL_DIR = "/home/azureuser/granite-model/granite-speech-4.1-2b-nar"

# Extended domain vocab: original + phonetic/common-misrecognition variants
DOMAIN_VOCAB_EXTENDED: list[str] = DOMAIN_VOCAB + [
    "brainpower",  # common misrecognition of "brainpowa"
    "brain powa",  # space variant
    "Rezolve AI",  # explicit compound
    "resolve AI",  # common misrecognition
    "Resolve",  # model often produces this instead of Rezolve
]

# Post-processing: conservative regex replacements for known misrecognitions
# Pattern → canonical. Applied case-insensitively on the hypothesis.
POSTPROC_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bbrain\s*pow[aer]+[a-z]*\b", "brainpowa"),  # brainpowa / brainpower / brain power
    (r"\bbrain\s*commerc[a-z]*\b", "brainpowa"),  # braincommerce (French accent artefact)
    (r"\bresol+ve?\s+(?=ai\b)", "Rezolve "),  # resolve AI → Rezolve AI
    (r"\bresol[a-z]*(?!\s+ai)\b", "Rezolve"),  # resol/resolv/resolve → Rezolve
    (r"\bnasda+q?\b", "NASDAQ"),  # nasdak / nasdaaq
    (r"\banthrop+ic\b", "Anthropic"),
    (r"\bllam+a\b", "Llama"),
]

_POSTPROC_RE = [(re.compile(p, re.IGNORECASE), r) for p, r in POSTPROC_REPLACEMENTS]


def apply_postproc(text: str) -> str:
    for pattern, replacement in _POSTPROC_RE:
        text = pattern.sub(replacement, text)
    return text


def build_biased_prompt(vocab: list[str]) -> str:
    return PROMPT_BIASED_PREFIX + ", ".join(vocab)


def load_audio(path: Path) -> torch.Tensor:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    wav = torch.from_numpy(data.T).float()
    if sr != SAMPLE_RATE:
        wav = torchaudio.functional.resample(wav, sr, SAMPLE_RATE)
    return wav


def transcribe_clip(model, processor, wav: torch.Tensor, prompt: str, device: str) -> str:
    tokenizer = processor.tokenizer
    chat = [{"role": "user", "content": f"<|audio|>{prompt}"}]
    prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    model_inputs = processor(prompt_text, wav, device=device, return_tensors="pt").to(device)
    with torch.inference_mode():
        output_ids = model.generate(
            **model_inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False, num_beams=1
        )
    num_input = model_inputs["input_ids"].shape[-1]
    new_tokens = output_ids[0, num_input:].unsqueeze(0)
    decoded = tokenizer.batch_decode(new_tokens, add_special_tokens=False, skip_special_tokens=True)
    return decoded[0].strip()


def run_variant(
    model,
    processor,
    clips: list,
    prompt: str,
    output_path: Path,
    device: str,
    *,
    postproc: bool = False,
) -> None:
    available = [c for c in clips if c.audio_path.exists()]

    # Warmup
    for clip in available[:WARMUP_CLIPS]:
        transcribe_clip(model, processor, load_audio(clip.audio_path), prompt, device)

    results: list[dict] = []
    for i, clip in enumerate(available):
        wav = load_audio(clip.audio_path)
        t0 = time.perf_counter()
        hypothesis = transcribe_clip(model, processor, wav, prompt, device)
        latency = time.perf_counter() - t0

        if postproc:
            hypothesis = apply_postproc(hypothesis)

        if clip.clip_id == CYRILLIC_ANOMALY_CLIP:
            print(f"  WARNING: anomaly clip {clip.clip_id}")

        results.append(
            {
                "clip_id": clip.clip_id,
                "hypothesis": hypothesis,
                "latency_seconds": latency,
            }
        )

        if (i + 1) % 10 == 0 or i == 0:
            print(
                f"  [{i + 1}/{len(available)}] {clip.clip_id}: '{hypothesis[:60]}' ({latency:.3f}s)"
            )

    success = sum(1 for r in results if r["hypothesis"])
    total = len(results)
    if total > 0 and success / total < 0.8:
        raise RuntimeError(f"Rejection: {success}/{total} non-empty.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"  Done: {success}/{total} → {output_path.name}")


def load_model(local_dir: str, device: str, *, trust_remote_code: bool = False) -> tuple:
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    print(f"  Loading from {local_dir} ...")
    processor = AutoProcessor.from_pretrained(local_dir, trust_remote_code=trust_remote_code)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        local_dir, dtype=torch.bfloat16, device_map=device, trust_remote_code=trust_remote_code
    )
    model.eval()
    return model, processor


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    clips = load_gold92()

    biased_prompt = build_biased_prompt(DOMAIN_VOCAB)
    biased_prompt_extended = build_biased_prompt(DOMAIN_VOCAB_EXTENDED)

    # ── Variant 1: NAR model ───────────────────────────────────────────
    # NAR uses relative imports in its custom code, which are incompatible with
    # transformers 4.57.6 trust_remote_code loading. Load via HF hub id instead.
    print("\n=== Variant 1: NAR model (granite-speech-4.1-2b-nar) ===")
    try:
        from transformers import AutoModelForSpeechSeq2Seq
        from transformers import AutoProcessor as AP

        proc_nar = AP.from_pretrained(
            "ibm-granite/granite-speech-4.1-2b-nar", trust_remote_code=True, local_files_only=True
        )
        model_nar = AutoModelForSpeechSeq2Seq.from_pretrained(
            "ibm-granite/granite-speech-4.1-2b-nar",
            dtype=torch.bfloat16,
            device_map=device,
            trust_remote_code=True,
            local_files_only=True,
        )
        model_nar.eval()
        run_variant(
            model_nar, proc_nar, clips, biased_prompt, GRANITE_NAR_BIASED_TRANSCRIPTS, device
        )  # noqa: E501
        del model_nar, proc_nar
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"  NAR load failed ({type(e).__name__}: {e}) — skipping variant 1.")

    # ── Variant 2: Base model + torch.compile ─────────────────────────
    print("\n=== Variant 2: Base model + torch.compile ===")
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    BASE_DIR = "/home/azureuser/granite-model/granite-speech-4.1-2b"
    proc_base = AutoProcessor.from_pretrained(BASE_DIR)
    model_base = AutoModelForSpeechSeq2Seq.from_pretrained(
        BASE_DIR, dtype=torch.bfloat16, device_map=device
    )
    model_base.eval()
    print("  Compiling model (torch.compile mode=default) ...")
    model_base = torch.compile(model_base, mode="default")
    run_variant(
        model_base, proc_base, clips, biased_prompt, GRANITE_COMPILED_BIASED_TRANSCRIPTS, device
    )
    del model_base, proc_base
    torch.cuda.empty_cache()

    # ── Variant 3: Base model + extended keywords + post-processing ────
    print("\n=== Variant 3: Extended keywords + post-processing ===")
    proc_ext = AutoProcessor.from_pretrained(BASE_DIR)
    model_ext = AutoModelForSpeechSeq2Seq.from_pretrained(
        BASE_DIR, dtype=torch.bfloat16, device_map=device
    )
    model_ext.eval()
    ext_delta = len(DOMAIN_VOCAB_EXTENDED) - len(DOMAIN_VOCAB)
    print(f"  Extended vocab: {len(DOMAIN_VOCAB_EXTENDED)} terms (+{ext_delta} vs baseline)")
    print(f"  Post-proc rules: {len(POSTPROC_REPLACEMENTS)}")
    run_variant(
        model_ext,
        proc_ext,
        clips,
        biased_prompt_extended,
        GRANITE_POSTPROC_BIASED_TRANSCRIPTS,
        device,
        postproc=True,
    )
    del model_ext, proc_ext
    torch.cuda.empty_cache()

    print("\nAll optimization variants complete.")


if __name__ == "__main__":
    main()
