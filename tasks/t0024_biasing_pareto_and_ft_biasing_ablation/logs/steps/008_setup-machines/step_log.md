---
spec_version: "3"
task_id: "t0024_biasing_pareto_and_ft_biasing_ablation"
step_number: 8
step_name: "setup-machines"
status: "completed"
started_at: "2026-08-13T08:03:06Z"
completed_at: "2026-08-13T09:32:38Z"
---
## Summary

Provisioned and fully verified `FT-MC` from the Azure ML H100 pool (`project/azure_vm.json`) for
Part B's fine-tuned + biased inference run, but Part B's required preconditions — the t0021
fine-tuned checkpoint and the `stt` conda env — were not present on the machine or locatable
anywhere reachable. The user was consulted and decided to defer Part B and proceed with Part A only;
the machine was torn down (auto-stopped via idle-shutdown) with no runaway cost.

## Actions Taken

1. Walked the Azure ML pool priority order from `project/azure_vm.json` (`FT-NC80-v3` → `FT-NC80-v1`
   → `FT-NC80-v2` → `FT-MC`); the first three entries no longer exist in Azure
   (`az ml compute show`/`list` confirm absent under
   `workspace=finetuning-workspace, resource_group=rezolve-AI`) — stale pool config, logged as a
   secondary finding, not fixed on this branch.
2. Acquired `FT-MC` (first attempt via `azure_ml_vm acquire` hit an 8-minute `vm_start_timeout`; a
   direct blocking `az ml compute start` subsequently brought it to `Running`). Verified SSH, 2x
   `NVIDIA H100 NVL` via `nvidia-smi`, and CUDA 12.2 via `nvcc`.
3. Rsynced the repo/branch to `FT-MC:~/rail-arf-stt-t0024/` (2238 files); confirmed
   `t0021`/`t0022`/`t0023`/`t0024` task folders present and resolve identically to the local
   checkout.
4. Searched for Part B's preconditions: full filesystem search (`find / -xdev -iname '*.nemo'`)
   found zero checkpoint files; `/mnt` on `FT-MC` is confirmed ephemeral local disk (dataloss
   warning file present, fresh at this boot); the `stt` conda env referenced by t0021/t0022/t0023 is
   absent (only
   `base, azureml_py310_sdkv2, azureml_py38_PT_TF, gemma, jupyter_env, mount_env, qwen3-trl` exist).
   t0021's results only record a generic `"gpu-azure"` label with no specific pool VM name, so the
   VM that actually ran t0021 cannot be identified. `dvc pull` for the clean-eval WAVs also failed
   with `AuthenticationFailed` (stale `.dvc/config.local`, no `az login` session on `FT-MC`) — a
   separate, secondary finding.
5. Escalated the checkpoint/env gap to the user via the coordinator. User decision: defer Part B,
   tear down `FT-MC` now, proceed with Part A only in step 9. Wrote up the full investigation in
   `intervention/checkpoint_not_found.md`.
6. `FT-MC` was never locked by the task (the library `acquire` call never returned success — the VM
   was brought up via a manual `az ml compute start` outside the library), so no experiment ran and
   no explicit teardown call was needed. Azure's own idle-shutdown (60 min) auto-stopped the VM at
   `2026-08-13T09:32:38Z` before any explicit teardown. Recorded final cost/duration
   (`total_duration_hours: 1.0075`, `total_cost_usd: 14.06`) in `machine_log.json`.

## Outputs

* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/logs/steps/008_setup-machines/machine_log.json`
  — full lifecycle record for `FT-MC`, including all 4 `failed_attempts` (3 stale pool entries + the
  `FT-MC` start timeout), `destroyed_at`, `total_duration_hours`, `total_cost_usd`, and
  `blocker_status`/`teardown_status` narrative fields.
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/intervention/checkpoint_not_found.md` — full
  writeup of the checkpoint/env gap, the stale `project/azure_vm.json` pool entries, and the DVC
  auth issue; states the user-approved resolution and Part A/B guidance for step 9.
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/intervention/pool_busy.md` — historical record
  of the earlier transient `FT-MC` start-timeout, left as-is (superseded by the successful second
  acquire attempt).
* `tasks/t0024_biasing_pareto_and_ft_biasing_ablation/checkpoint.md` — updated with this step's
  history, the Part B deferral cross-step decision, and Next Step Notes for step 9.

## Issues

Part B's required preconditions (t0021 fine-tuned `.nemo` checkpoint, `stt` conda env) could not be
located on any reachable machine — a genuine data-provenance gap (3 of 4 declared pool VMs no longer
exist in Azure, and t0021's own results do not record which pool VM it ran on). This is not a
machine-selection failure: `FT-MC` was provisioned and verified successfully from an infrastructure
standpoint. Resolved via user-approved deferral of Part B; Part A is unaffected and proceeds in step
9\. Full detail in `intervention/checkpoint_not_found.md`.
