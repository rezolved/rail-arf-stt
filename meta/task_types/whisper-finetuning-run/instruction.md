# Whisper Fine-Tuning Run Instructions

## Planning Guidelines

- Specify the base checkpoint (e.g., `openai/whisper-large-v3`), training framework
  (Hugging Face Transformers + PEFT/LoRA, or full fine-tune), and compute target
  (Mac Metal MPS for small runs, Azure H100 VM for full runs).
- Define the train/validation split from DVC-tracked production audio. Gold-92 must be in
  neither split — it is the held-out test set.
- Estimate GPU-hours and cost. A LoRA run on a single H100 for ~1 h costs ~$14; a full
  fine-tune of large-v3 may take 4-8 h. Document this in the plan before provisioning.
- Include a data-scale experiment in the plan (e.g., 25%, 50%, 100% of training data) to
  answer Research Question 5 about minimum viable dataset size.

## Implementation Guidelines

- Use the Mac Metal (MPS) path for quick iteration (≤100 clips, LoRA). Only provision an
  Azure H100 VM when the training set exceeds what MPS can handle in under 2 h.
- Save checkpoints every N steps to the task results directory, tracked by DVC. Do not commit
  checkpoint bytes to git.
- After training, run an `stt-benchmark-run` on gold-92 using the fine-tuned checkpoint to
  produce the full set of registered project metrics.
- Run a general-WER regression check using a public English test set (e.g., LibriSpeech
  test-clean) alongside the gold-92 evaluation so regression is detectable.
- Tear down Azure VMs promptly after the evaluation step completes.

## Common Pitfalls

1. Including gold-92 clips in the training or validation split — always cross-check clip IDs
   against `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/files/gold_set.jsonl`.
2. Forgetting to `dvc push` checkpoints before the PR merges — teammates cannot reproduce results
   without the checkpoint.
3. Not running the general-WER regression check — a fine-tuned model may improve entity accuracy
   but regress on everyday speech.
4. Over-fitting to the training split without a validation curve — monitor validation loss to
   decide early stopping.

## Related Skills

- `/implementation` — main execution skill
- `/setup-remote-machine` — provision Azure H100 VM when needed
- `/research-code` — review Hugging Face Whisper fine-tuning examples
