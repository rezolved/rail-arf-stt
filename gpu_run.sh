#!/usr/bin/env bash
# Usage: ./gpu_run.sh <task_id> <python_script_path>
# Example: ./gpu_run.sh t0006_nemotron_3_5_benchmark tasks/t0006_nemotron_3_5_benchmark/code/run.py
#
# Syncs project to GPU server, runs script, pulls results back.

set -euo pipefail

TASK_ID="${1:-}"
SCRIPT="${2:-}"
REMOTE_HOST="gpu-azure"
REMOTE_DIR="/home/azureuser/rail-arf-stt"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "$TASK_ID" || -z "$SCRIPT" ]]; then
    echo "Usage: $0 <task_id> <python_script>"
    echo "Example: $0 t0006_nemotron_3_5_benchmark tasks/t0006.../code/run.py"
    exit 1
fi

echo "==> [1/3] Syncing code to $REMOTE_HOST..."
rsync -av --progress \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='.mypy_cache/' \
    --exclude='.ruff_cache/' \
    --exclude='.pytest_cache/' \
    --exclude='*.egg-info/' \
    --exclude='.DS_Store' \
    --exclude='tasks/*/ctx/' \
    --exclude='*.log' \
    "$LOCAL_DIR/" "$REMOTE_HOST:$REMOTE_DIR/"

echo ""
echo "==> [2/3] Running $SCRIPT on GPU server..."
ssh "$REMOTE_HOST" bash -c "
    source /home/azureuser/miniconda3/etc/profile.d/conda.sh
    conda activate stt
    cd $REMOTE_DIR
    PYTHONPATH=$REMOTE_DIR python -u $SCRIPT
"

echo ""
echo "==> [3/3] Pulling results back..."
rsync -av --progress \
    "$REMOTE_HOST:$REMOTE_DIR/tasks/$TASK_ID/" \
    "$LOCAL_DIR/tasks/$TASK_ID/"

echo ""
echo "Done. Results in: tasks/$TASK_ID/"
