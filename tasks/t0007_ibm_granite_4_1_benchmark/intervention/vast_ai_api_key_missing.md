---
created_at: "2026-06-25T00:00:00Z"
step: "008_setup-machines"
phase: "Phase 1 pre-flight"
blocker: "vast_ai_api_key_missing"
---
# Intervention: Vast.ai API Key Not Configured

## Problem

The `setup-remote-machine` skill Phase 1 pre-flight check failed because the Vast.ai API key is
not configured. The plan for `t0007_ibm_granite_4_1_benchmark` (Section 5, Remote Machines)
specifies `provider: vast_ai` with an A100 80GB GPU, but neither of the two accepted credential
sources is present:

1. `~/.config/vastai/vast_api_key` — file does not exist
2. `VAST_API_KEY` environment variable — not set in the shell environment

## What Was Checked

- `~/.config/vastai/vast_api_key` — missing
- `VAST_API_KEY` env var — not set
- `.env` files in the project root and `REZOLVE AI/` directory — no `VAST_API_KEY` entry found
- The Nebius API key (`NEBIUS_API_KEY`) is present in `REZOLVE AI/.env`, but the Nebius CLI
  binary (`nebius`) is not installed, so the Nebius provider is also unavailable

## Resolution Required

To unblock this step, choose one of the following options:

### Option A: Configure Vast.ai (recommended per plan)

1. Log in to https://cloud.vast.ai/account/ and copy your API key
2. Run:
   ```bash
   cd "/Users/margotiamanova/Desktop/REZOLVE AI/rail-arf-stt-worktrees/t0007_ibm_granite_4_1_benchmark"
   uv run vastai set api-key YOUR_API_KEY_HERE
   ```
   This writes the key to `~/.config/vastai/vast_api_key`
3. Re-run the setup-remote-machine skill

### Option B: Set VAST_API_KEY in environment

```bash
export VAST_API_KEY="your-key-here"
```

Then re-run the setup-remote-machine skill within the same shell session.

### Option C: Switch provider to Nebius

If Vast.ai access is not available, the plan can be amended to `provider: nebius` with
`gpu_class: H100`. Prerequisites:
1. Install the Nebius CLI: https://nebius.com/docs/cli/quickstart
2. Authenticate: `nebius iam get-access-token`
3. Update `tasks/t0007_ibm_granite_4_1_benchmark/plan/plan.md` Section 5 to `provider: nebius`
4. Re-run the setup-remote-machine skill

Note: Nebius H100 at ~$2/hr would still be within the $3–8 budget estimate for a 1-hour job.

## Budget Status at Time of Intervention

- Total budget: $2,000.00
- Spent: $2.50
- Remaining: $1,997.50
- Stop threshold reached: false
- This task is well within budget limits

## Next Step

After configuring credentials per one of the options above, delete this file and re-run
`/setup-remote-machine` for task `t0007_ibm_granite_4_1_benchmark`.
