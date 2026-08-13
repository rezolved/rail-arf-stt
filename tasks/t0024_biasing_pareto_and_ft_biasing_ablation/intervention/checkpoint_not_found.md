# Part B checkpoint not found — Part B deferred

**Resolution: user-approved deferral.** Part A (Pareto-frontier analysis, no GPU) proceeds normally
in step 9. Part B (fine-tuned + biased inference run) is deferred pending human resolution of the
checkpoint's actual location.

## What happened

Step 8 (`setup-machines`) acquired `FT-MC` from the pool in `project/azure_vm.json` and verified it
end-to-end: SSH reachable, 2x `NVIDIA H100 NVL` (95830 MiB) confirmed via `nvidia-smi`, CUDA 12.2
confirmed via `nvcc`, repo/branch rsynced to `FT-MC:~/rail-arf-stt-t0024/` (2238 files, all
dependency task dirs present).

Part B's precondition — the existing fine-tuned checkpoint at
`/mnt/finetune-checkpoints/parakeet-unified-finetuned-best.nemo` (per t0021's `code/paths.py` and
this task's `plan.md` Step 8) — was **not present** on FT-MC, and could not be located anywhere
reachable:

* A full filesystem search (`find / -xdev -iname '*.nemo'`) on FT-MC found zero `.nemo` files.
* `/mnt` on FT-MC is confirmed to be the VM's **ephemeral local disk**
  (`/mnt/EPHEMERAL_DISK_DATALOSS_WARNING.txt` present, freshly created at this boot) — content
  written there by a previous task on a *different* VM does not carry over.
* t0021's `results/results_detailed.md` only records a generic `"gpu-azure"` machine label with no
  specific pool VM name, so there's no way to know from that record which VM originally held the
  checkpoint.
* The `stt` conda env referenced by t0021/t0022/t0023 also does not exist on FT-MC (only
  `base, azureml_py310_sdkv2, azureml_py38_PT_TF, gemma, jupyter_env, mount_env, qwen3-trl` are
  present) — consistent with FT-MC never having been used for this project before.
* Checked `FT-ARF-v3` (same `Standard_NC80adis_H100_v5` instance type) as a long shot — it is
  unrelated: created 2026-07-14 (after t0021 ran on 2026-07-07) and never referenced anywhere in
  this repo. Not pursued further (it's outside this project's declared pool).
* The checkpoint is not DVC-tracked in this repo (only `clean_eval_audio.dvc` is under
  `t0021_parakeet_finetune_vs_biasing/data/`).

**Conclusion**: this is a genuine data-provenance gap — the checkpoint most likely still exists on
whichever of `FT-NC80-v3` / `FT-NC80-v1` / `FT-NC80-v2` actually ran t0021's fine-tuning, but those
VM names no longer exist in Azure (see below), so the checkpoint is currently unreachable through
this project's pool. It is not a machine-selection problem and not something step 9 should keep
chasing — a human needs to either locate the checkpoint (check whether the finetuning team renamed
rather than deleted the VM, check any backup/export the t0021 author may have made) or accept it
must be regenerated, which is out of scope for this task's Part B as scoped.

## Separate, secondary finding: pool config is stale (infra fix, NOT for this task branch)

`project/azure_vm.json` lists 4 VMs in priority order: `FT-NC80-v3` (1) → `FT-NC80-v1` (2) →
`FT-NC80-v2` (3) → `FT-MC` (4). As of 2026-08-13,
`az ml compute list --workspace-name finetuning-workspace --resource-group rezolve-AI` shows only
`FT-MC` exists among these four — the other three are gone (renamed or decommissioned since the pool
config was copied from `rail-arf-finetuning` in June 2026). `azure_ml_vm.py`'s `get_compute_state()`
returns `UNKNOWN` for a missing VM rather than erroring immediately, so a full priority walk burns
~8 minutes per dead entry (~24 minutes total) before reaching `FT-MC`. This should be fixed on
`main` (refresh `project/azure_vm.json` against current Azure state, and/or make `azure_ml_vm.py`
fail fast on a "Not Found" `az ml compute show` instead of polling `_wait_for_state` for the full
8-minute timeout) — **not** as part of this task's branch.

## Separate, secondary finding: DVC auth blocked on FT-MC

`dvc pull tasks/t0021_parakeet_finetune_vs_biasing/data/clean_eval_audio` failed with
`AuthenticationFailed` on FT-MC. The `.dvc/config.local` copied over (from the local main-repo
checkout) carries a stale/rejected connection string, and per `docs/dvc-data-workflow.md` the
current default auth path is `az login` (`AzureCliCredential` via `DefaultAzureCredential`) — but
FT-MC had no active `az login` session, no managed identity (`az login --identity` →
`Identity not found`), and no service-principal env vars. This is independent of the checkpoint
blocker and would need either an interactive `az login` on a pool VM once, or a fresh connection
string from the team vault. The 21 clean-eval WAV clips were **not** pulled onto FT-MC as a result.

## Machine disposition

FT-MC's own Azure-side idle-shutdown safety net (`idle_time_before_shutdown: 60 min`) auto-stopped
the VM at `2026-08-13T09:32:38Z` (`last_operation: Stop, IdleShutdown`) before any explicit teardown
call was needed. No task lock was ever placed on it (the `azure_ml_vm.py acquire` library call
itself never returned success — see `failed_attempts` in `machine_log.json`), so there was nothing
for `azure_ml_vm.py teardown` to release. Total billed time ≈ 1.01 hours (~$14.06) — see
`machine_log.json` for the final figures.

## For step 9 (implementation)

* **Part A**: proceed as planned — pure local analysis of `t0022`'s `results/param_sweep.jsonl` and
  `t0023`'s `results/tdt_sweep.jsonl`. No GPU, no remote machine needed.
* **Part B**: **do not attempt.** Do not re-provision a machine, do not search further for the
  checkpoint. Treat it as deferred pending a human locating (or deciding to regenerate) the t0021
  checkpoint.
