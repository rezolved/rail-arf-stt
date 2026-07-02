---
spec_version: "3"
task_id: "t0017_parakeet_biasing_buffer_replacement"
step_number: 10
step_name: "teardown"
status: "skipped"
started_at: null
completed_at: null
---
## Summary

Step skipped: `llm-t1-nc80` is a shared reserved Azure ML instance kept alive across tasks per team
policy. It was not deallocated after this task's GPU work completed.

## Actions Taken

1. Step marked skipped per team policy on the reserved instance.

## Outputs

No outputs produced (step skipped).

## Issues

No issues encountered.
