---
spec_version: "3"
task_id: "t0015_streaming_buffer_interval"
step_number: 8
step_name: "setup-machines"
status: "completed"
started_at: "2026-06-30T10:59:32Z"
completed_at: "2026-06-30T11:10:00Z"
---
## Summary

Reserved Azure H100 NVL machine (llm-t1-nc80, 2×H100 NVL, 880 GB RAM) verified live via SSH. All
four required models confirmed present on the machine: parakeet-tdt-0.6b-v3 (pre-cached),
parakeet-unified-en-0.6b (downloaded 2.47 GB), multitalker-parakeet-streaming-0.6b-v1 (downloaded
2.49 GB), and Granite Speech 4.1 2B (pre-existing at /home/azureuser/granite-model/). GPU smoke gate
passed with torch.cuda.device_count()==2, CUDA 12.2, NeMo 3.1.0+dcd7153.

## Actions Taken

1. Ran prestep — step status set to in_progress, step folder created at
   logs/steps/008_setup-machines/.
2. Verified budget: $2.50 spent of $2,000.00 total; $1,997.50 remaining; stop threshold not reached;
   estimated 5-hour GPU spend (~$69.80) is within budget.
3. Confirmed SSH connectivity to llm-t1-nc80 (40.127.196.254:50000, azureuser, id_rsa_mohan).
4. Verified GPUs via nvidia-smi: 2× NVIDIA H100 NVL, 95,830 MiB each, driver 535.274.02.
5. Verified CUDA: nvcc 12.2.140.
6. Verified conda env `stt` with NeMo 3.1.0+dcd7153.
7. Checked HuggingFace cache — nvidia/parakeet-tdt-0.6b-v3 pre-existing.
8. Downloaded nvidia/parakeet-unified-en-0.6b (2.47 GB) to HF cache.
9. Downloaded nvidia/multitalker-parakeet-streaming-0.6b-v1 (2.49 GB) to HF cache.
10. Confirmed Granite Speech 4.1 2B at /home/azureuser/granite-model/granite-speech-4.1-2b
    (safetensors format, pre-existing from t0014).
11. Ran GPU smoke test: torch.cuda.device_count()==2 — PASS.
12. Wrote machine_log.json to logs/steps/008_setup-machines/machine_log.json.

## Outputs

- `tasks/t0015_streaming_buffer_interval/logs/steps/008_setup-machines/machine_log.json` — machine
  provisioning record with GPU verification, model inventory, and smoke gate result.
- `tasks/t0015_streaming_buffer_interval/logs/steps/008_setup-machines/step_log.md` — this file.

## Issues

Machine llm-t1-nc80 uses a non-standard SSH port (50000) and private key (id_rsa_mohan). The `az`
CLI is not installed on the local orchestration machine; SSH-based verification was used instead
(same approach as t0014). Machine was already running (reserved instance, no per-minute billing
start cost). VM is left running for implementation step; teardown step will handle deallocation.
