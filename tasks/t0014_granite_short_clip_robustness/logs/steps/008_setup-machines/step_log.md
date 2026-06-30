---
spec_version: "3"
task_id: "t0014_granite_short_clip_robustness"
step_number: 8
step_name: "setup-machines"
status: "completed"
started_at: "2026-06-29T13:32:44Z"
completed_at: "2026-06-30T00:00:00Z"
---
## Summary

The Azure H100 NVL machine (`azureuser@llm-t1-nc80`) was verified live and ready for task execution.
SSH connectivity confirmed, GPU verified as 2x NVIDIA H100 NVL, conda env `stt` active with NeMo
3.1.0, Parakeet TDT 0.6b-v3 loading from HuggingFace cache, and Granite Speech 4.1 2B present at
`/home/azureuser/granite-model/granite-speech-4.1-2b`. This step recovers a stuck `in_progress`
state — the machine was already provisioned and verified before the step log was written.

## Actions Taken

1. Verified SSH connectivity to `azureuser@llm-t1-nc80` (hostname: llm-t1-nc80, Azure H100 NVL
   pool).
2. Confirmed GPU hardware: 2x NVIDIA H100 NVL via `nvidia-smi`.
3. Confirmed conda env `stt` exists at `/home/azureuser/miniconda3/envs/stt`.
4. Verified NeMo version 3.1.0 installed in `stt` env.
5. Verified Parakeet TDT 0.6b-v3 loads from HuggingFace cache (`nvidia/parakeet-tdt-0.6b-v3`).
6. Confirmed Granite Speech 4.1 2B model directory at
   `/home/azureuser/granite-model/granite-speech-4.1-2b`.
7. Verified Whisper is available in the `stt` env (used in prior task t0012).
8. Wrote `machine_log.json` with all required fields per `remote_machines_specification.md` v5.

## Outputs

- `logs/steps/008_setup-machines/machine_log.json` — machine provisioning record (Azure ML, H100
  NVL, all verification fields populated)
- `logs/steps/008_setup-machines/step_log.md` — this file

## Issues

Step was stuck `in_progress` since 2026-06-29T13:32:44Z with no step log or machine_log written
(likely an agent crash immediately after prestep). Recovered by writing the required output files
from verified machine state. No provisioning work was needed — the machine was already live and
fully prepared when recovery was performed.
