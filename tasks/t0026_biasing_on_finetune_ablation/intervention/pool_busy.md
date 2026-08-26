# Azure ML compute pool — blocked on a provisioner bug fix

Task `t0026_biasing_on_finetune_ablation` step 8 (`setup-machines`) cannot acquire `LLM-T1-NC80`
yet. This is **not** a pool-contention conflict with `t0025_parakeet_tdt_brand_finetune` (confirmed:
`t0025`'s `task.json` status is `not_started`, it has no `checkpoint.md`, and no worktree for it
exists) and the VM is not held by a human (confirmed via
`az ml compute show --name LLM-T1-NC80 --workspace-name brainpowa-northeurope --resource-group rezolve-AI`:
`last_operation` is `Stop`/`Succeeded`, i.e. currently `Stopped` and not billing).

## Attempts

* **Attempt 1** (`vm_start_timeout`): `az ml compute start` issued, VM did not reach `Running`
  within the provisioner's 480s/8min internal deadline. Cleanup re-stopped it. No cost incurred.
* **Attempt 2** (`ssh_connect`): a real bug was found and fixed first — `~/.ssh/config` had the host
  alias lowercased (`llm-t1-nc80`) instead of `LLM-T1-NC80`, which the provisioner's SSH check
  requires exact-case. After that fix, the VM reached `Running` and SSH resolution worked, but the
  attempt still failed with `ssh_connect`.
* **Attempt 3**: reproduced the same `ssh_connect` failure, confirming a structural bug rather than
  a one-off flake.

## Root cause

`arf/scripts/utils/azure_ml_vm.py`'s `acquire()` shares **one** deadline between "wait for VM
`Running`" and "wait for SSH up." A slow boot eats most of the budget before the SSH wait even
starts, so SSH almost never gets enough time on its own. This is a real provisioner bug, not pool
contention or user error.

## Resolution in progress

A fix is being developed on infra branch `infra/vm-ssh-deadline` (worktree
`real-repos/rail-arf-stt-worktrees/infra_vm-ssh-deadline`) via the `/self-improvement` skill, per
Critical Rule 1 (infra fixes land as their own PR to `main`, never inline on a task branch). The fix
gives the SSH wait its own independent deadline once VM-`Running` is reached.

**Do not retry `acquire()` on this task branch until `infra/vm-ssh-deadline` merges to `main` and
this worktree rebases/picks up the fix.** Once merged, re-run the `setup-machines` step (fresh
`/setup-remote-machine` subagent) to retry the acquire.
