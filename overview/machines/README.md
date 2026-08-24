# Machine Provisioning (3 machines)

**3** machines provisioned across **3** tasks. Total cost: **$301.64**.

**4** failed provisioning attempts wasted **$0.00** (57.1% failure rate).

## Summary

| Field | Value |
|-------|-------|
| Total machines | 3 |
| Total failed attempts | 4 |
| Failure rate | 57.1% |
| Avg provisioning time | 598s |
| Total cost | $301.64 |
| Total wasted cost | $0.00 |

## Cost by GPU Tier

| GPU | Total Cost (USD) |
|-----|-----------------|
| H100 NVL | $301.64 |

## Provider Breakdown

| Provider | Machines | Cost (USD) | Failure Rate |
|----------|----------|------------|--------------|
| azure_ml | 3 | $301.64 | 57.1% |

## Failure Reasons

| Reason | Count |
|--------|-------|
| Azure resource not found under workspace=finetuning-workspace, resource_group=rezolve-AI ('az ml compute show' -> 'Operation returned an invalid status Not Found'; not present in 'az ml compute list'). SSH to host alias FT-NC80-v3 (20.65.40.221:50000) also connection-timed-out. Pool config in project/azure_vm.json is stale for this entry. | 1 |
| Azure resource not found under workspace=finetuning-workspace, resource_group=rezolve-AI (not present in 'az ml compute list'). SSH to host alias FT-NC80-v1 (20.242.41.64:50000) also connection-timed-out. Pool config in project/azure_vm.json is stale for this entry. | 1 |
| Azure resource not found under workspace=finetuning-workspace, resource_group=rezolve-AI (not present in 'az ml compute list'). SSH to host alias FT-NC80-v2 (20.110.53.175:50000) also connection-timed-out. Pool config in project/azure_vm.json is stale for this entry. | 1 |
| First acquire attempt (azure_ml_vm acquire --vm-name FT-MC, which issues 'az ml compute start --no-wait') timed out: VM did not reach Running state within 480s (exit code 75, pool_busy.md written). A subsequent direct blocking 'az ml compute start' (outside the library, ~9 more minutes) succeeded in bringing it to Running. | 1 |

## Tasks

| Task | Machines | Cost (USD) | Failed | GPUs |
|------|----------|------------|--------|------|
| [`t0014_granite_short_clip_robustness`](../../overview/tasks/task_pages/t0014_granite_short_clip_robustness.md) | 1 | $0.00 | 0 | H100 NVL |
| [`t0015_streaming_buffer_interval`](../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) | 1 | $287.58 | 0 | H100 NVL |
| [`t0024_biasing_pareto_and_ft_biasing_ablation`](../../overview/tasks/task_pages/t0024_biasing_pareto_and_ft_biasing_ablation.md) | 1 | $14.06 | 4 | H100 NVL |
