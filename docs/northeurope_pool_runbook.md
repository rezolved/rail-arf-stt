# Runbook: LLM-T1-NC80 (northeurope) in the acquire pool

**Version**: 1

How an agent connects `LLM-T1-NC80` (northeurope, `brainpowa-northeurope`) into the `azure_ml_vm`
acquire pool and uses it reliably across stop/start cycles, given it is a shared box other people
use directly rather than a dedicated ARF task-pool VM.

## What makes this VM different from `FT-NC80-*`

`FT-NC80-v1/v2/v3` and `FT-MC` (`finetuning-workspace`, eastus2) are dedicated ARF pool boxes: every
user of them goes through `azure_ml_vm acquire`, so the lock-file mechanism
(`~/.arf-locks/$TASK_ID.lock`) sees every claimant.

`LLM-T1-NC80` is different: Margarita, Mohan, and others SSH into it directly for manual fine-tuning
work, without ever placing an ARF lock. The lock-file check alone cannot see that kind of occupancy
— a VM with zero ARF locks could still have a human mid-training-run on it.

`project/azure_vm.json` marks this with `requires_coordination_if_running: true`
(`arf/scripts/utils/azure_ml_vm.py`, `_attempt_acquire_one`): the rule is **if it is already
Running, coordinate before claiming; if it is Stopped, it is safe to acquire** (starting a stopped
VM is not racing anyone by definition). Concretely:

* VM state `Stopped` → `acquire` starts it itself and proceeds normally.
* VM state `Running` when the acquire attempt begins → `acquire` refuses this VM immediately with
  `failure_phase: "human_coordination_required"`, without touching locks, and falls through to the
  next pool entry (or writes `pool_busy.md` if this was the last one). Check `#finetuning` Slack (or
  just ask) before manually confirming it is free and re-running.

## Step 1 — Pool entry (`project/azure_vm.json`)

Already present:

```json
{
  "name": "LLM-T1-NC80",
  "workspace": "brainpowa-northeurope",
  "resource_group": "rezolve-AI",
  "ssh_host_alias": "LLM-T1-NC80",
  "hourly_cost_usd": 13.96,
  "priority": 5,
  "notes": "...",
  "requires_coordination_if_running": true
}
```

Priority `5` (tried last) — this pool's real primaries are the `finetuning-workspace` boxes;
`LLM-T1-NC80` is a last-resort fallback specifically because it is shared human-use compute.

## Step 2 — SSH alias (`~/.ssh/config`)

`azure_ml_vm` connects only through `ssh_host_alias`. The alias must exist locally:

```sshconfig
Host LLM-T1-NC80
   HostName 40.127.196.254
   IdentityFile ~/.ssh/id_rsa_azureml_ftmc
   Port 50000
   User azureuser
   StrictHostKeyChecking accept-new
   UserKnownHostsFile /dev/null
   LogLevel ERROR
```

`StrictHostKeyChecking accept-new` + `UserKnownHostsFile /dev/null` prevent the
`REMOTE HOST IDENTIFICATION HAS CHANGED` failure when Azure reuses a public IP for a different host
after a restart.

## Step 3 (CRITICAL) — Refresh HostName after every start

Azure ML compute instances **can be assigned a new public IP on every stop→start**. `azure_ml_vm`
uses a static `ssh_host_alias` and does not refresh the IP, so after a restart the alias may point
at a dead IP and `_wait_for_ssh` fails with `failure_phase="ssh_connect"`.

Always run this immediately after the VM reaches `Running`, before any SSH:

```bash
NEWIP=$(az ml compute show --name LLM-T1-NC80 \
  --workspace-name brainpowa-northeurope --resource-group rezolve-AI \
  -o json | python3 -c "import sys,json;print((json.load(sys.stdin).get('network_settings') or {}).get('public_ip_address'))")

python3 - "$NEWIP" <<'PY'
import re, sys, pathlib
ip = sys.argv[1]
cfg = pathlib.Path.home() / ".ssh" / "config"
text = cfg.read_text()
text = re.sub(r"(?ms)^(Host LLM-T1-NC80\n(?:[^\n]*\n)*?\s*HostName )\S+",
              lambda m: m.group(1) + ip, text)
cfg.write_text(text)
print("HostName ->", ip)
PY

ssh LLM-T1-NC80 'echo OK $(hostname)'
```

## Step 4 — Preflight is automatic, but here is what it does

`azure_ml_vm.acquire()` runs `arf/scripts/utils/remote_preflight.sh` over SSH before placing the
task lock (`LESSONS.md` Lessons 10 and 11):

* Repairs `/mnt/cache/persist` to point at
  `/mnt/batch/tasks/shared/LS_root/mounts/clusters/$(hostname)/code` if it does not already —
  `brainpowa-northeurope` is a separate workspace from `finetuning-workspace`, so this is a
  distinct, independently-mounted Azure Files share.
* Enables and verifies `loginctl enable-linger azureuser`, so a detached `tmux` job survives SSH
  disconnect.

A VM that fails either check is rejected with `failure_phase: "preflight"` and never locked.

## Do not touch data left by manual use

Fine-tune checkpoints from manual sessions live at `/mnt/finetune-checkpoints/` on this box (e.g.
`parakeet-unified-finetuned-best.nemo`) — this is **not** the ARF persistent-storage path from Step
4 and is not covered by any DVC push. Never delete or overwrite anything under that path from an ARF
task; treat it as someone else's working directory that happens to share the machine.
