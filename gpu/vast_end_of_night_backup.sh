#!/usr/bin/env bash
set -euo pipefail

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_root="/workspace/nightly_backups/open_higgsfield_${timestamp}"
artifact_root="${backup_root}/artifacts"

repo_root="/workspace/Open-Higgsfield-AI"
comfy_root="/workspace/ComfyUI"
workflow_root="/workspace/comfy/workflows/open_higgsfield"

mkdir -p "${artifact_root}"

copy_if_exists() {
  local src="$1"
  local dest_dir="$2"
  if [[ -e "${src}" ]]; then
    mkdir -p "${dest_dir}"
    cp -R "${src}" "${dest_dir}/"
  fi
}

write_git_info() {
  local target="$1"
  local out="$2"
  if [[ -d "${target}/.git" ]]; then
    {
      echo "path=${target}"
      git -C "${target}" remote -v || true
      git -C "${target}" rev-parse HEAD || true
      git -C "${target}" status --short || true
    } > "${out}"
  fi
}

{
  echo "date=$(date --iso-8601=seconds)"
  echo "hostname=$(hostname)"
  echo "python_main=$(command -v python || true)"
  echo "python_main_version=$((python --version) 2>&1 || true)"
  echo "venv_main=/venv/main"
} > "${backup_root}/system.txt"

write_git_info "${repo_root}" "${backup_root}/repo_git.txt"
write_git_info "${comfy_root}" "${backup_root}/comfy_git.txt"

mkdir -p "${backup_root}/custom_nodes"
for node_dir in \
  "${comfy_root}/custom_nodes/ComfyUI-VideoHelperSuite" \
  "${comfy_root}/custom_nodes/comfyui-LatentSync" \
  "${comfy_root}/custom_nodes/ComfyUI-MuseTalk_FSH"; do
  if [[ -d "${node_dir}" ]]; then
    node_name="$(basename "${node_dir}")"
    write_git_info "${node_dir}" "${backup_root}/custom_nodes/${node_name}.txt"
  fi
done

if [[ -d "${workflow_root}" ]]; then
  mkdir -p "${artifact_root}/workflows"
  cp -R "${workflow_root}/." "${artifact_root}/workflows/"
fi

copy_if_exists "${repo_root}/backend/workflows/comfy" "${artifact_root}"
copy_if_exists "${repo_root}/gpu" "${artifact_root}"

mkdir -p "${artifact_root}/logs"
copy_if_exists "/workspace/logs/backend.log" "${artifact_root}/logs"
copy_if_exists "/workspace/logs/comfyui.log" "${artifact_root}/logs"

mkdir -p "${artifact_root}/manifests"
find "${comfy_root}/models" -type f 2>/dev/null | sort > "${artifact_root}/manifests/comfy_models_manifest.txt" || true
find "${comfy_root}/custom_nodes" -maxdepth 2 -type f \( -name "*.py" -o -name "requirements*.txt" -o -name "*.json" \) 2>/dev/null | sort > "${artifact_root}/manifests/custom_node_files_manifest.txt" || true
pip freeze > "${artifact_root}/manifests/pip_freeze_main.txt" || true

cat > "${backup_root}/README.txt" <<EOF
This backup intentionally excludes large model weights and caches.

Saved:
- workflow JSON files
- gpu provisioning docs/scripts
- backend comfy workflow templates
- worker/backend logs
- model and custom-node file manifests
- git remotes / commit SHAs for repo, ComfyUI, and key custom nodes
- pip freeze from /venv/main

If you destroy the instance, this archive must be copied off the worker first.
EOF

archive_path="/workspace/nightly_backups/open_higgsfield_${timestamp}.tar.gz"
tar -C "/workspace/nightly_backups" -czf "${archive_path}" "open_higgsfield_${timestamp}"

echo "Backup complete:"
echo "  directory: ${backup_root}"
echo "  archive:   ${archive_path}"
