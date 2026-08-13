---
spec_version: "3"
task_id: "t0017_parakeet_biasing_buffer_replacement"
step_number: 8
step_name: "setup-machines"
status: "completed"
started_at: "2026-07-01T21:15:00Z"
completed_at: "2026-07-01T21:20:00Z"
---
## Summary

Reused the reserved Azure H100 NVL instance `llm-t1-nc80` provisioned for t0015; no new machine was
created. Both candidate checkpoints were already present in the HF cache on that machine.

## Actions Taken

1. Confirmed `llm-t1-nc80` (2xH100 NVL, ssh alias `gpu-azure`) is live and reachable.
2. Confirmed both `nvidia/parakeet-tdt-0.6b-v3` and `nvidia/parakeet-unified-en-0.6b` are cached
   under `/home/azureuser/.cache/huggingface/hub/` on the remote.

## Outputs

No new machine provisioned — reused existing reserved instance.

## Issues

No issues encountered.
