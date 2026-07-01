# Reserved Machine Not Destroyed — RM-E001 Expected

## Summary

Machine `llm-t1-nc80` (Azure ML, 2×H100 NVL) is a **reserved Azure instance** that must NOT be
deallocated. This is an explicit user instruction: the machine is shared across tasks and is kept
alive between runs.

## Why destroyed_at is null

`destroyed_at: null` is **intentional**. The teardown step logged machine usage and cost estimates
but did not issue a deallocation command. The machine remains running for use by subsequent tasks.

## Verificator conflict

`verify_machines_destroyed.py` will report `RM-E001` (no destroyed_at timestamp). This error is
expected and accepted for reserved-pool machines. The verificator has no exemption mechanism for
reserved instances.

**This intervention file documents that the RM-E001 error is not a billing emergency.** The machine
is a reserved instance with fixed subscription billing — it does not accumulate per-minute charges
when idle.

## Cost accounting

- Duration apportioned to this task: 20.6 hours (2026-06-30T11:02Z to 2026-07-01T07:37Z)
- Rate: $13.96/hr (fixed pool rate from project/azure_vm.json)
- Apportioned cost: $287.58

Actual billing is at the Azure subscription level; this is a cost allocation estimate only.

## Action required

None. Resume downstream steps (results, reporting). The RM-E001 warning in reporting should be noted
as accepted and expected.
