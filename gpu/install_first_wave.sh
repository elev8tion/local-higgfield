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
MODEL_DIR="${MODEL_DIR:-$WORKSPACE_DIR/models}"

mkdir -p \
  "$WORKSPACE_DIR/venvs" \
  "$WORKSPACE_DIR/comfy" \
  "$WORKSPACE_DIR/cache/huggingface" \
  "$WORKSPACE_DIR/cache/torch" \
  "$WORKSPACE_DIR/models/checkpoints" \
  "$WORKSPACE_DIR/models/wan" \
  "$WORKSPACE_DIR/models/lipsync" \
  "$WORKSPACE_DIR/models/whisper" \
  "$WORKSPACE_DIR/models/text_encoders" \
  "$WORKSPACE_DIR/models/vae" \
  "$LOG_DIR" \
  "$OUTPUT_DIR"

if [ ! -d "$ROOT_DIR/.git" ]; then
  echo "Expected repo at $ROOT_DIR"
  exit 1
fi

if [ ! -d "$COMFY_DIR/.git" ]; then
  git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY_DIR"
fi

if [ ! -d "$COMFY_VENV" ]; then
  python3 -m venv "$COMFY_VENV"
fi

if [ ! -d "$BACKEND_VENV" ]; then
  python3 -m venv "$BACKEND_VENV"
fi

source "$COMFY_VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "$COMFY_DIR/requirements.txt"
deactivate

source "$BACKEND_VENV/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "$ROOT_DIR/backend/requirements.txt"
python -m pip install \
  requests \
  whisperx \
  ffmpeg-python \
  pydub \
  srt
deactivate

cat <<EOF
First-wave install complete.

Still required manually on persistent storage:
- first-wave model downloads
- Comfy custom nodes needed for Wan workflows
- machine-local env file at /workspace/gpu.env
EOF
