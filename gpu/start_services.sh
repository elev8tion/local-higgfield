#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${ROOT_DIR:-/workspace/Open-Higgsfield-AI}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE_DIR/comfy/ComfyUI}"
BACKEND_VENV="${BACKEND_VENV:-$WORKSPACE_DIR/venvs/open-higgsfield-backend}"
COMFY_VENV="${COMFY_VENV:-$WORKSPACE_DIR/venvs/comfyui}"
HF_HOME="${HF_HOME:-$WORKSPACE_DIR/cache/huggingface}"
TORCH_HOME="${TORCH_HOME:-$WORKSPACE_DIR/cache/torch}"
LOG_DIR="${LOG_DIR:-$WORKSPACE_DIR/logs}"
OUTPUT_DIR="${OUTPUT_DIR:-$WORKSPACE_DIR/outputs}"

mkdir -p "$LOG_DIR" "$OUTPUT_DIR"

if [ -f "/workspace/gpu.env" ]; then
  # shellcheck disable=SC1091
  source "/workspace/gpu.env"
fi

export HF_HOME
export TORCH_HOME
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

pkill -f "ComfyUI/main.py" || true
pkill -f "uvicorn backend.server:app" || true

source "$COMFY_VENV/bin/activate"
nohup python "$COMFY_DIR/main.py" --listen 0.0.0.0 --port "${COMFY_PORT:-8188}" \
  >"$LOG_DIR/comfyui.log" 2>&1 &
deactivate

source "$BACKEND_VENV/bin/activate"
nohup python -m uvicorn backend.server:app --host 0.0.0.0 --port "${BACKEND_PORT:-8000}" \
  >"$LOG_DIR/backend.log" 2>&1 &
deactivate

cat <<EOF
Services started.
- ComfyUI: http://0.0.0.0:${COMFY_PORT:-8188}
- Backend: http://0.0.0.0:${BACKEND_PORT:-8000}
- Logs: $LOG_DIR
EOF
