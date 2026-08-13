# Azure ML compute pool busy

Task `t0024_biasing_pareto_and_ft_biasing_ablation` could not acquire a VM from
`project/azure_vm.json`.

## Attempts

* **FT-MC** (vm_start_timeout): VM FT-MC did not reach running state within 480s

## Resolution

* Check `#finetuning` Slack to see whether the finetuning team is using both VMs.
* Run
  `az ml compute show --name FT-NC80-v3 --workspace-name finetuning-workspace --resource-group rezolve-AI -o json`
  to confirm state.
* Once a VM is free, re-run the setup-machines step.
