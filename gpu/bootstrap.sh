#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found; this script expects an Ubuntu/Debian base image."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y \
  git \
  ffmpeg \
  wget \
  curl \
  unzip \
  jq \
  build-essential \
  python3-pip \
  python3-venv \
  python3-dev \
  libgl1 \
  libglib2.0-0

python3 -m pip install --upgrade pip setuptools wheel

echo "Base bootstrap complete."
