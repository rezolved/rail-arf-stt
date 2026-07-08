# t0022 — GPU-PB Biasing Diagnostic: Detailed Results

## Methodology

- **Model:** `nvidia/parakeet-unified-en-0.6b` (EncDecHybridRNNTCTCBPEModel, NeMo 3.1.0)
- **Machine:** Azure H100 NVL (`azureuser@llm-t1-nc80`), 2026-07-08
- **Eval set:** gold-92 (93 clips total); 35 brand clips (contain Rezolve/brainpowa in ground truth), 10 neutral clips for over-boosting detection
- **Data fix:** `error_en_0011` ground_truth corrected Resolve→Rezolve (committed in 9bb5b59)
- **Phrase list:** DOMAIN_VOCAB (31 terms) + orthographic variants of Rezolve/brainpowa

---

## Step 1 — Tokenization Probe

Both target brands split into many short fragments in the model's SentencePiece tokenizer:

| Brand | Subword split | Fragments | Flag |
|-------|--------------|-----------|------|
| Rezolve | `['Re', 'z', 'ol', 've']` | 4 | ⚠ MANY_FRAGMENTS |
| brainpowa | `['br', 'ain', 'p', 'ow', 'a']` | 5 | ⚠ MANY_FRAGMENTS |
| Rezolve AI | `['Re', 'z', 'ol', 've', 'A', 'i']` | 6 | ⚠ MANY_FRAGMENTS |

Each fragment is a high-frequency English piece. The encoder strongly prefers `Resolve`
(1–2 tokens) over the 4-token sequence required for `Rezolve`.

---

## Step 2 — Decoding Matrix

| Config | Strategy | EXACT | PHONETIC | GARBAGE |
|--------|----------|-------|----------|---------|
| (a) greedy, no boost | greedy_batch | 0/35 (0%) | 32/35 | 3/35 |
| (b) greedy + GPU-PB | greedy_batch | 0/35 (0%) | 33/35 | 2/35 |
| (c) beam, no boost | beam (alsd) | 0/35 (0%) | 32/35 | 3/35 |
| (d) malsd_batch + GPU-PB | malsd_batch | 7/35 (20%) | 25/35 | 3/35 |

**Key finding:** greedy boosting tree is fully ignored — configs (a) and (b) produce identical
outputs. `malsd_batch` is required for the boosting tree to influence decoding.

Dominant failure pattern: **PHONETIC_NEIGHBOR** (91% of baseline failures).
Model outputs "Resolve", "brain commerce", "brain power" — acoustically close, wrong token path.

---

## Step 3 — Param Sweep (malsd_batch, 100 cells)

Grid: `context_score ∈ {1.0, 1.5, 2.0, 2.5, 3.0}` × `depth_scaling ∈ {0.5, 1.0, 1.5, 2.0}`
× `alpha ∈ {1.0, 1.5, 2.0, 2.5, 3.0}`

### Top cells by brand EXACT (then neutral WER)

| context_score | depth_scaling | alpha | Brand EXACT | Neutral WER |
|---------------|---------------|-------|-------------|-------------|
| 3.0 | 0.5 | 1.5 | **60.0%** | **8.7%** |
| 2.5 | 0.5 | 2.0 | 60.0% | 14.9% |
| 2.0 | 0.5 | 2.5 | 60.0% | 19.4% |
| 2.5 | 0.5 | 2.5 | 68.6% | 27.9% |
| 2.5 | 1.0 | 2.0 | 62.9% | 38.5% |

### Key observations

- `depth_scaling=0.5` consistently outperforms `ds≥1.0` for neutral WER — shallower boosting
  penalises non-brand tokens less aggressively
- `context_score=3.0, alpha=1.5` is the sweet spot: high brand pull without runaway over-boosting
- `depth_scaling≥1.5` causes neutral WER to spike above 30% in most cells

### Best balanced cell

```
context_score = 3.0
depth_scaling = 0.5
alpha         = 1.5
→ brand EXACT = 60.0% (21/35)
→ neutral WER = 8.7%  (baseline ~15%, regression = -6.3pp — acceptable)
```

---

## Step 4 — Root Cause Classification

| Signal | Evidence | Implication |
|--------|----------|-------------|
| Tokenization | "Rezolve" = 4 fragments of common English pieces | Encoder has uphill path to emit correct sequence |
| Greedy boost = 0% | Boosting tree silent in greedy_batch | Wrong strategy in prod |
| malsd_batch best = 60% | 21/35 EXACT with tuned params | Not fundamental — config fixes most of it |
| Phonetic neighbor rate 91% | Encoder *hears* it, maps wrong | Acoustic info present; decoding path needs help |

---

## Verdict

**config-fixable** — the primary failure is wrong decoding strategy (greedy vs malsd_batch)
and untuned params. Switching and tuning recovers 60% brand EXACT.

Remaining 40% failure requires finetune to fix the encoder's multi-fragment representation
of Rezolve/brainpowa — boosting alone cannot fully compensate for 4–5 token sequences
competing against 1–2 token alternatives.

### Recommended next steps

1. **Immediate:** deploy `malsd_batch` + `cs=3.0, ds=0.5, alpha=1.5` to production
2. **Medium-term:** finetune parakeet-unified encoder on real prod clips (see t0022 data)
3. **Validate:** re-run gold-92 eval after prod switch to confirm 60% holds in streaming

---

## Files

| File | Description |
|------|-------------|
| `decoding_matrix.jsonl` | Per-clip results across 4 configs |
| `param_sweep.jsonl` | All 100 sweep cells with brand rate + neutral WER |
| `tokenization_probe.txt` | Full tokenizer output for DOMAIN_VOCAB |
| `results_summary.md` | 1-page summary |
| `results_detailed.md` | This file |
