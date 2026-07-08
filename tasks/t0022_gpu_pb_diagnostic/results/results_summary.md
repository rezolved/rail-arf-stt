# t0022 — GPU-PB Biasing Diagnostic: Results Summary

GPU-PB context biasing with the default `greedy_batch` strategy produces **0% brand EXACT** on
Rezolve/brainpowa clips — the boosting tree is ignored by greedy decoding. Switching to
`malsd_batch` + tuned params raises brand recognition to **60% EXACT** (21/35 clips) with
neutral WER of **8.7%** (baseline ~15%), confirming the failure is **config-fixable**, not
fundamental — though the encoder's multi-fragment tokenization makes brute-force boosting
necessary.

## Key Numbers

| Config | Strategy | Brand EXACT | Neutral WER |
|--------|----------|-------------|-------------|
| (a) greedy, no boost — baseline | greedy_batch | 0% (0/35) | ~15% |
| (b) greedy + GPU-PB — current prod | greedy_batch | 0% (0/35) | ~15% |
| (c) beam, no boost | beam (alsd) | 0% (0/35) | ~15% |
| (d) malsd_batch + GPU-PB | malsd_batch | 20% (7/35) | ~18% |
| **Best sweep cell** | malsd_batch | **60% (21/35)** | **8.7%** |

## Recommended Production Parameters

```python
strategy        = "malsd_batch"
beam_size       = 4
context_score   = 3.0
depth_scaling   = 0.5
alpha           = 1.5
```

## Model & Eval

- **Model:** `nvidia/parakeet-unified-en-0.6b` (EncDecHybridRNNTCTCBPEModel, NeMo 3.1.0)
- **Eval:** gold-92, 35 brand clips (Rezolve/brainpowa), 10 neutral clips
- **Machine:** Azure H100 NVL (`azureuser@llm-t1-nc80`), 2026-07-08

## Verdict

**config-fixable** — switch greedy → malsd_batch, tune params above.
Long-term: finetune encoder to fix multi-fragment tokenization of "Rezolve" and "brainpowa".
