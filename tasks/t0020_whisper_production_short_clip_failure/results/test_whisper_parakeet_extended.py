"""
Whisper + Parakeet-unified-en-0.6b chunked re-transcribe test: 0.5s – 30s clips.

Both models run the same production streaming loop:
  accumulate 32kB chunks → transcribe growing buffer → track intermediate failures.

Parakeet config mirrors brainpowa-realtime-api ParakeetSTT:
  - NeMo model.transcribe()
  - GPU-PB boosting with domain vocab (alpha=1.0)
  - same stream_interval_bytes = 32kB

Whisper config mirrors WhisperSTT:
  - HuggingFace Transformers (faster-whisper blocked by ctranslate2 GPU bug on this host)
  - vad_filter via HF pipeline, initial_prompt = domain vocab
"""

import contextlib
import copy
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

# ── paths ─────────────────────────────────────────────────────────────────────
T0014_DIR = Path("/home/azureuser/rail-arf-stt/tasks/t0014_granite_short_clip_robustness")
GOLD92_DIR = Path(
    "/home/azureuser/rail-arf-stt/tasks/t0001_stt_benchmark/assets/dataset"
    "/stt-benchmark-gold-92/files"
)
OUT_JSONL = Path("/tmp/whisper_parakeet_results.jsonl")
OUT_SUMMARY = Path("/tmp/whisper_parakeet_summary.txt")

PARAKEET_MODEL_ID = "nvidia/parakeet-unified-en-0.6b"
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"
DEVICE = "cuda:0"
SAMPLE_RATE = 16_000
CHUNK_BYTES = 32_768  # 32kB = ~1s at 16kHz PCM-16

DOMAIN_VOCAB = [
    "Rezolve",
    "Rezolve Ai",
    "NASDAQ",
    "brainpowa",
    "brainpowa AI",
    "AI Foundry",
    "Shopify Plus",
    "Adobe Commerce",
    "Salesforce Commerce Cloud",
    "conversational AI",
    "voice AI",
    "agentic AI",
    "agentic commerce",
    "omnichannel",
    "multimodal",
    "product recommendation",
    "intent detection",
    "entity recognition",
    "product catalog",
    "inventory",
    "fulfillment",
    "shopping assistant",
    "voice assistant",
    "smart speaker",
    "cross-channel",
    "real-time",
    "low-latency",
    "NLU",
    "ASR",
    "SKU",
    "E-commerce",
]
INITIAL_PROMPT = ", ".join(DOMAIN_VOCAB)
BOH_PATTERNS = [
    "thanks for watching",
    "subscribe",
    "[music]",
    "[applause]",
    "[laughter]",
    "thank you for watching",
    "thank you.",
    "please subscribe",
    "like and subscribe",
    "see you next time",
    "kenya",
    "known,",
]
BOOSTING_ALPHA = 1.0
CONTEXT_SCORE = 1.0
DEPTH_SCALING = 2.0
random.seed(42)


# ── helpers ───────────────────────────────────────────────────────────────────
def load_wav(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), always_2d=True)
    if data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    audio = data[:, 0].astype(np.float32)
    if sr != SAMPLE_RATE:
        import soxr

        audio = soxr.resample(audio, sr, SAMPLE_RATE)
    return audio


def trim(audio: np.ndarray, dur_s: float) -> np.ndarray:
    n = int(dur_s * SAMPLE_RATE)
    if len(audio) >= n:
        return audio[:n]
    return np.concatenate([audio, np.zeros(n - len(audio), dtype=np.float32)])


def is_hallucination(text: str, ref: str) -> bool:
    if not text:
        return False
    tl = text.lower()
    if any(p in tl for p in BOH_PATTERNS):
        return True
    ref_words = set(ref.lower().split())
    txt_words = set(tl.split())
    return bool(ref_words and not ref_words & txt_words)


def pcm_chunks(audio: np.ndarray):
    pcm = (audio * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
    for i in range(0, len(pcm), CHUNK_BYTES):
        yield pcm[i : i + CHUNK_BYTES]


# ── Whisper transcription ─────────────────────────────────────────────────────
def load_whisper():
    print(f"Loading Whisper {WHISPER_MODEL_ID} ...")
    model = (
        AutoModelForSpeechSeq2Seq.from_pretrained(
            WHISPER_MODEL_ID,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        .to(DEVICE)
        .eval()
    )
    processor = AutoProcessor.from_pretrained(WHISPER_MODEL_ID)
    prompt_ids = processor.get_prompt_ids(INITIAL_PROMPT, return_tensors="pt").to(DEVICE)
    forced_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")
    # warmup
    warmup = np.zeros(SAMPLE_RATE, dtype=np.float32)
    for _ in range(2):
        _transcribe_whisper(model, processor, warmup, prompt_ids, forced_ids)
    print("Whisper ready.")
    return model, processor, prompt_ids, forced_ids


def _transcribe_whisper(model, processor, audio, prompt_ids, forced_ids) -> str:
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    features = inputs.input_features.to(DEVICE, dtype=torch.float16)
    with torch.no_grad():
        ids = model.generate(
            features,
            prompt_ids=prompt_ids,
            forced_decoder_ids=forced_ids,
            num_beams=1,
            do_sample=False,
            max_new_tokens=200,
        )
    return processor.batch_decode(ids, skip_special_tokens=True)[0].strip()


# ── Parakeet transcription ────────────────────────────────────────────────────
def _expand_casing(phrases):
    out, seen = [], set()
    for p in phrases:
        for v in (p, p.lower(), p[:1].upper() + p[1:]):
            if v and v not in seen:
                seen.add(v)
                out.append(v)
    return tuple(out)


def load_parakeet():
    print(f"Loading Parakeet {PARAKEET_MODEL_ID} ...")
    from nemo.collections.asr.models import ASRModel
    from omegaconf import OmegaConf, open_dict

    model = ASRModel.from_pretrained(model_name=PARAKEET_MODEL_ID)
    model = model.to(DEVICE)
    model.eval()

    # apply GPU-PB boosting with domain vocab
    phrases = _expand_casing(DOMAIN_VOCAB)
    cfg = copy.deepcopy(model.cfg.decoding)
    with open_dict(cfg):
        cfg.strategy = "greedy_batch"
    OmegaConf.update(cfg, "greedy.boosting_tree.key_phrases_list", list(phrases), force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.context_score", CONTEXT_SCORE, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.depth_scaling", DEPTH_SCALING, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree.use_bpe_dropout", True, force_add=True)
    OmegaConf.update(cfg, "greedy.boosting_tree_alpha", BOOSTING_ALPHA, force_add=True)
    model.change_decoding_strategy(cfg)

    # warmup
    warm = np.zeros(SAMPLE_RATE, dtype=np.float32)
    model.transcribe([warm], batch_size=1, verbose=False)
    print("Parakeet ready.")
    return model


def _transcribe_parakeet(model, audio_float32: np.ndarray) -> str:
    outputs = model.transcribe([audio_float32], batch_size=1, verbose=False)
    first = outputs[0] if outputs else ""
    return (getattr(first, "text", first) or "").strip()


# ── generic chunked re-transcribe loop ───────────────────────────────────────
def run_chunked(transcribe_fn, audio: np.ndarray, ref: str) -> dict:
    """transcribe_fn(audio_float32) -> str"""
    accumulated = bytearray()
    bytes_since = 0
    intermediates = []
    t0 = time.perf_counter()

    for chunk in pcm_chunks(audio):
        accumulated.extend(chunk)
        bytes_since += len(chunk)
        if bytes_since >= CHUNK_BYTES:
            bytes_since = 0
            buf = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
            text = transcribe_fn(buf)
            intermediates.append(
                {
                    "bytes": len(accumulated),
                    "text": text,
                    "is_empty": len(text) == 0,
                    "is_hallucination": is_hallucination(text, ref),
                }
            )

    final_buf = np.frombuffer(bytes(accumulated), dtype=np.int16).astype(np.float32) / 32767.0
    final_text = transcribe_fn(final_buf)
    latency = time.perf_counter() - t0

    return {
        "transcript": final_text,
        "is_empty": len(final_text) == 0,
        "is_hallucination": is_hallucination(final_text, ref),
        "any_intermediate_empty": any(x["is_empty"] for x in intermediates),
        "any_intermediate_halluc": any(x["is_hallucination"] for x in intermediates),
        "intermediate_count": len(intermediates),
        "latency_seconds": round(latency, 3),
    }


# ── build clip list ───────────────────────────────────────────────────────────
clips = []  # (clip_id, duration_s, audio, reference_text)

# 0.5–3s: t0014 synthetic clips
meta_path = T0014_DIR / "data/short_clips_metadata.jsonl"
for line in meta_path.read_text().splitlines():
    if not line.strip():
        continue
    m = json.loads(line)
    path = T0014_DIR / "data/short_clips" / f"{m['clip_id']}.wav"
    if path.exists():
        clips.append(
            (m["clip_id"], float(m["duration_s"]), load_wav(path), str(m["reference_text"]))  # noqa: E501
        )

# 5–30s: gold-92
gt_map = {}
for line in (GOLD92_DIR / "ground_truth.jsonl").read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        gt_map[r["clip_id"]] = r.get("transcript", "")

gold_wavs = sorted((GOLD92_DIR / "audio").glob("*.wav"))
gold_audio = {}
for w in gold_wavs:
    with contextlib.suppress(Exception):
        gold_audio[w.stem] = load_wav(w)

gold_cids = list(gold_audio.keys())
random.shuffle(gold_cids)

TARGET_BINS = [5, 10, 15, 20, 25, 30]
CLIPS_PER_BIN = 7

for target_dur in TARGET_BINS:
    added = 0
    used = set()
    pool = [c for c in gold_cids if c not in used]
    random.shuffle(pool)
    for cid in pool:
        if added >= CLIPS_PER_BIN:
            break
        audio = gold_audio[cid]
        dur = len(audio) / SAMPLE_RATE
        if target_dur <= 13.7:
            if dur < target_dur * 0.7:
                continue
            seg = trim(audio, target_dur)
            ref = gt_map.get(cid, "")
        else:
            concat = audio.copy()
            ref_parts = [gt_map.get(cid, "")]
            pool2 = [c for c in gold_cids if c not in used and c != cid]
            random.shuffle(pool2)
            for cid2 in pool2:
                if len(concat) / SAMPLE_RATE >= target_dur:
                    break
                concat = np.concatenate([concat, gold_audio[cid2]])
                ref_parts.append(gt_map.get(cid2, ""))
                used.add(cid2)
            if len(concat) / SAMPLE_RATE < target_dur * 0.9:
                continue
            seg = trim(concat, target_dur)
            ref = " ".join(r for r in ref_parts if r)
            cid = f"concat_{target_dur}s_{cid[:12]}"
        clips.append((cid, float(target_dur), seg, ref))
        used.add(cid)
        added += 1

print(f"Total clips: {len(clips)}")
dur_dist = defaultdict(int)
for _, d, _, _ in clips:
    dur_dist[d] += 1
for d in sorted(dur_dist):
    print(f"  {d}s: {dur_dist[d]} clips")

# ── load models ───────────────────────────────────────────────────────────────
w_model, w_proc, w_prompt, w_forced = load_whisper()
p_model = load_parakeet()


def whisper_fn(audio):
    return _transcribe_whisper(w_model, w_proc, audio, w_prompt, w_forced)


def parakeet_fn(audio):
    return _transcribe_parakeet(p_model, audio)


# ── run ───────────────────────────────────────────────────────────────────────
print(f"\nRunning {len(clips)} clips × 2 models ...\n")
results = []

for i, (cid, dur, audio, ref) in enumerate(clips):
    rw = run_chunked(whisper_fn, audio, ref)
    rp = run_chunked(parakeet_fn, audio, ref)

    def flags(r):
        f = ""
        if r["any_intermediate_empty"]:
            f += " INT-EMPTY"
        if r["any_intermediate_halluc"]:
            f += " INT-HALLUC"
        if r["is_empty"]:
            f += " FINAL-EMPTY"
        if r["is_hallucination"]:
            f += " FINAL-HALLUC"
        return f.strip() or "ok"

    print(f"  [{i + 1:3d}/{len(clips)}] {dur:4.1f}s  n={rw['intermediate_count']}")
    print(f"    W: '{rw['transcript'][:55]}'  {flags(rw)}")
    print(f"    P: '{rp['transcript'][:55]}'  {flags(rp)}")

    results.append(
        {
            "clip_id": cid,
            "duration_s": dur,
            "whisper": {k: v for k, v in rw.items() if k != "intermediates"},
            "parakeet": {k: v for k, v in rp.items() if k != "intermediates"},
        }
    )

OUT_JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n")

# ── summary ───────────────────────────────────────────────────────────────────
bins = defaultdict(list)
for r in results:
    bins[r["duration_s"]].append(r)


def pct(n, total):
    return f"{n}/{total} {n / total:4.0%}" if total else "0/0   0%"


lines = [
    "=== Whisper vs Parakeet-unified: chunked re-transcribe failure rates ===",
    "",
    f"{'dur':>5}  {'n':>3}  {'W int_h%':>9}  {'W fin_h%':>9}  {'W empty%':>9}  "
    f"{'P int_h%':>9}  {'P fin_h%':>9}  {'P empty%':>9}  {'n_inter':>7}",
    "-" * 85,
]
for dur in sorted(bins):
    c = bins[dur]
    n = len(c)
    wi = sum(1 for x in c if x["whisper"]["any_intermediate_halluc"])
    wf = sum(1 for x in c if x["whisper"]["is_hallucination"])
    we = sum(1 for x in c if x["whisper"]["is_empty"])
    pi = sum(1 for x in c if x["parakeet"]["any_intermediate_halluc"])
    pf = sum(1 for x in c if x["parakeet"]["is_hallucination"])
    pe = sum(1 for x in c if x["parakeet"]["is_empty"])
    nc = sorted(x["whisper"]["intermediate_count"] for x in c)
    p50 = nc[len(nc) // 2]
    lines.append(
        f"{dur:>5.1f}  {n:>3}  "
        f"{wi:>3}/{n}{wi / n:>4.0%}  {wf:>3}/{n}{wf / n:>4.0%}  {we:>3}/{n}{we / n:>4.0%}  "
        f"{pi:>3}/{n}{pi / n:>4.0%}  {pf:>3}/{n}{pf / n:>4.0%}  {pe:>3}/{n}{pe / n:>4.0%}  "
        f"{p50:>7}"
    )

summary = "\n".join(lines)
print("\n" + summary)
OUT_SUMMARY.write_text(summary + "\n")
print(f"\nSaved → {OUT_JSONL}\nSummary → {OUT_SUMMARY}")
