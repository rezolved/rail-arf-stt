---
spec_version: "3"
task_id: "t0015_streaming_buffer_interval"
step_number: 10
step_name: "teardown"
status: "completed"
started_at: "2026-07-01T07:37:54Z"
completed_at: "2026-07-01T07:40:00Z"
---
## Summary

Logged machine usage for llm-t1-nc80 (Azure ML, 2×H100 NVL reserved instance). Machine was not
deallocated per explicit project policy — it is a shared reserved instance kept alive across tasks.
Cost estimate of $287.58 (20.6 hours × $13.96/hr) recorded in `results/costs.json` and
`results/remote_machines_used.json`.

## Actions Taken

1. Updated `logs/steps/008_setup-machines/machine_log.json` with `total_duration_hours: 20.6` and
   `total_cost_usd: 287.58`; `destroyed_at` remains `null` because the reserved instance was not
   deallocated per explicit user instruction.
2. Created `results/costs.json` with `total_cost_usd: 287.58` (breakdown: `azure-ml-2xh100: 287.58`)
   and a note explaining the reserved-instance cost-allocation methodology.
3. Created `results/remote_machines_used.json` with one entry for `llm-t1-nc80` (2×H100 NVL, 20.6
   hours, $287.58).
4. Ran `verify_machines_destroyed` — received expected `RM-E001` (no destroyed_at) because the
   instance is a reserved Azure pool VM that must stay provisioned. Created
   `intervention/reserved_machine_not_destroyed.md` documenting the accepted discrepancy.
5. Updated `checkpoint.md` with teardown summary and next-step notes for step 11 (results).

## Outputs

- `logs/steps/008_setup-machines/machine_log.json` — updated with duration and cost estimate
- `results/costs.json` — total_cost_usd: 287.58, breakdown: azure-ml-2xh100
- `results/remote_machines_used.json` — one entry: llm-t1-nc80, 2xH100 NVL, 20.6h, $287.58
- `intervention/reserved_machine_not_destroyed.md` — accepted RM-E001 documentation

## Issues

`verify_machines_destroyed` reports `RM-E001` because `destroyed_at` is null. This is intentional
and expected: the machine is a reserved Azure pool instance that is kept alive per project policy.
The error is documented and accepted in `intervention/reserved_machine_not_destroyed.md`. No billing
emergency exists — reserved instances do not accrue per-minute charges when idle.
