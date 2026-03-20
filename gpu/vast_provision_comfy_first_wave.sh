#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"
REPO_DIR="${REPO_DIR:-$WORKSPACE_DIR/Open-Higgsfield-AI}"
COMFY_DIR="${COMFY_DIR:-$WORKSPACE_DIR/ComfyUI}"
CUSTOM_NODES_DIR="${CUSTOM_NODES_DIR:-$COMFY_DIR/custom_nodes}"
WORKFLOW_DIR="${WORKFLOW_DIR:-$WORKSPACE_DIR/comfy/workflows/open_higgsfield}"
MODEL_ROOT="${MODEL_ROOT:-$WORKSPACE_DIR/models}"
LOG_DIR="${LOG_DIR:-$WORKSPACE_DIR/logs}"
CACHE_DIR="${CACHE_DIR:-$WORKSPACE_DIR/cache}"
REPO_URL="${OPEN_HIGGSFIELD_REPO_URL:-https://github.com/elev8tion/local-higgfield.git}"
REPO_BRANCH="${OPEN_HIGGSFIELD_REPO_BRANCH:-main}"

export HF_HOME="${HF_HOME:-$CACHE_DIR/huggingface}"
export TORCH_HOME="${TORCH_HOME:-$CACHE_DIR/torch}"

echo "[open-higgsfield] starting first-wave Vast provisioning"

mkdir -p \
  "$WORKSPACE_DIR" \
  "$CUSTOM_NODES_DIR" \
  "$WORKFLOW_DIR" \
  "$MODEL_ROOT/checkpoints" \
  "$MODEL_ROOT/clip" \
  "$MODEL_ROOT/clip_vision" \
  "$MODEL_ROOT/diffusion_models" \
  "$MODEL_ROOT/text_encoders" \
  "$MODEL_ROOT/vae" \
  "$MODEL_ROOT/audio" \
  "$MODEL_ROOT/insightface" \
  "$HF_HOME" \
  "$TORCH_HOME" \
  "$LOG_DIR"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "[open-higgsfield] cloning repo into $REPO_DIR"
  git clone --branch "$REPO_BRANCH" "$REPO_URL" "$REPO_DIR"
else
  echo "[open-higgsfield] updating repo at $REPO_DIR"
  git -C "$REPO_DIR" fetch origin
  git -C "$REPO_DIR" checkout "$REPO_BRANCH"
  git -C "$REPO_DIR" pull --ff-only origin "$REPO_BRANCH"
fi

sync_repo() {
  local url="$1"
  local target="$2"

  if [ ! -d "$target/.git" ]; then
    echo "[open-higgsfield] cloning $url -> $target"
    git clone "$url" "$target"
  else
    echo "[open-higgsfield] updating $target"
    git -C "$target" pull --ff-only || true
  fi
}

sync_repo "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite" "$CUSTOM_NODES_DIR/ComfyUI-VideoHelperSuite"
sync_repo "https://github.com/jiafuzeng/comfyui-LatentSync" "$CUSTOM_NODES_DIR/comfyui-LatentSync"
sync_repo "https://github.com/AIFSH/ComfyUI-MuseTalk_FSH" "$CUSTOM_NODES_DIR/ComfyUI-MuseTalk_FSH"

echo "[open-higgsfield] syncing starter workflow templates"
cp "$REPO_DIR/backend/workflows/comfy/video.animate_image.json" "$WORKFLOW_DIR/video.animate_image.wan_i2v.json"
cp "$REPO_DIR/backend/workflows/comfy/lipsync.video_audio.json" "$WORKFLOW_DIR/lipsync.video_audio.latentsync.json"
cp "$REPO_DIR/backend/workflows/comfy/lipsync.image_audio.json" "$WORKFLOW_DIR/lipsync.image_audio.musetalk.json"

if command -v python3 >/dev/null 2>&1; then
  if [ -f "$COMFY_DIR/requirements.txt" ]; then
    echo "[open-higgsfield] installing base ComfyUI Python requirements"
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip install -r "$COMFY_DIR/requirements.txt" || true
  fi

  for req in \
    "$CUSTOM_NODES_DIR/ComfyUI-VideoHelperSuite/requirements.txt" \
    "$CUSTOM_NODES_DIR/comfyui-LatentSync/requirements.txt" \
    "$CUSTOM_NODES_DIR/ComfyUI-MuseTalk_FSH/requirements.txt"
  do
    if [ -f "$req" ]; then
      echo "[open-higgsfield] installing node requirements from $req"
      python3 -m pip install -r "$req" || true
    fi
  done
fi

cat >/tmp/open-higgsfield-comfy-env.sh <<EOF
export HF_HOME="$HF_HOME"
export TORCH_HOME="$TORCH_HOME"
export OPEN_HIGGSFIELD_VIDEO_COMMAND='python3 -m backend.runners.comfy_video_runner --payload "{payload_path}" --output "{output_path}"'
export OPEN_HIGGSFIELD_LIPSYNC_COMMAND='python3 -m backend.runners.comfy_lipsync_runner --payload "{payload_path}" --output "{output_path}"'
export OPEN_HIGGSFIELD_COMFY_BASE_URL='http://127.0.0.1:18188'
export OPEN_HIGGSFIELD_COMFY_POLL_INTERVAL='2.0'
export OPEN_HIGGSFIELD_COMFY_MAX_ATTEMPTS='300'
export OPEN_HIGGSFIELD_COMFY_VIDEO_ANIMATE_IMAGE_WORKFLOW='$WORKFLOW_DIR/video.animate_image.wan_i2v.json'
export OPEN_HIGGSFIELD_COMFY_LIPSYNC_VIDEO_AUDIO_WORKFLOW='$WORKFLOW_DIR/lipsync.video_audio.latentsync.json'
export OPEN_HIGGSFIELD_COMFY_LIPSYNC_IMAGE_AUDIO_WORKFLOW='$WORKFLOW_DIR/lipsync.image_audio.musetalk.json'
EOF

if [ -w /etc/environment ]; then
  grep -q "OPEN_HIGGSFIELD_COMFY_BASE_URL" /etc/environment || cat /tmp/open-higgsfield-comfy-env.sh >> /etc/environment || true
fi

echo "[open-higgsfield] first-wave Vast provisioning complete"
echo "[open-higgsfield] workflow directory: $WORKFLOW_DIR"
echo "[open-higgsfield] custom nodes directory: $CUSTOM_NODES_DIR"
echo "[open-higgsfield] repo directory: $REPO_DIR"
