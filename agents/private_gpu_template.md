# Open Higgsfield AI: Private GPU Template Blueprint

Last updated: 2026-03-18

This is the first private template blueprint for the rented GPU machine.

It is intentionally scoped for the first serious creator-video deployment, not for every future model family at once.

Operational repo assets for this plan now exist in:

- [gpu/bootstrap.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/bootstrap.sh)
- [gpu/install_first_wave.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/install_first_wave.sh)
- [gpu/start_services.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/start_services.sh)
- [gpu/gpu.env.example](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/gpu.env.example)
- [gpu/first_day_checklist.md](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/first_day_checklist.md)

## Target Machine

- preferred first rental: `RTX 5090`
- preferred persistent disk: `500GB`
- minimum persistent disk: `300GB`

Why:

- the `5090` is a strong first machine for:
  - `Wan2.2-TI2V-5B`
  - `LatentSync`
  - `MuseTalk`
  - `WhisperX`
  - lighter `LTX` workflows
- `500GB` gives room for:
  - ComfyUI
  - node repos
  - caches
  - video outputs
  - the first model wave

## Template Goal

Bake in the tooling.

Do not bake in every large model weight.

That means:

- preinstall platform packages
- preinstall Python envs
- preinstall ComfyUI
- preinstall custom nodes
- preinstall our repo and runner bridge
- keep model downloads on persistent volume

## Base Image

Use a clean CUDA/PyTorch image, not a community workflow template.

Recommended baseline:

- Ubuntu `22.04`
- CUDA `12.x`
- Python `3.10` or `3.11`
- PyTorch matching the CUDA image

## System Packages

Install:

- `git`
- `ffmpeg`
- `wget`
- `curl`
- `unzip`
- `jq`
- `build-essential`
- `python3-pip`
- `python3-venv`
- `libgl1`
- `libglib2.0-0`

## Python / Runtime Layers

### 1. ComfyUI layer

Install:

- `ComfyUI`
- only the custom nodes required for:
  - Wan workflows
  - video load/save
  - first/last-frame workflows
  - subtitle burn-in helpers later if needed

Do not install a massive all-in-one node pack on day one.

### 2. Open Higgsfield backend layer

Install backend requirements from:

- [backend/requirements.txt](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/requirements.txt)

Plus likely post-process/runtime packages:

- `requests`
- `whisperx`
- `ffmpeg-python`
- `pydub`
- `srt`

### 3. Caption / lyric layer

Install:

- `WhisperX`
- lyric pipeline dependencies later

Do not overbuild the lyric stack into the first image if time matters.

## First Model Scope

Install first:

- `Wan2.2-TI2V-5B`
- `LatentSync`
- `WhisperX`

Optional in first wave:

- `MuseTalk`

Do not install first:

- `Wan 2.2 14B` family
- `Wan 2.1 VACE`
- `HunyuanImage-3.0`
- every `LTX` variant

Those belong to later waves after the first rented box is stable.

## Persistent Storage Layout

Use persistent volume paths like:

```text
/workspace/Open-Higgsfield-AI
/workspace/comfy/ComfyUI
/workspace/models/checkpoints
/workspace/models/wan
/workspace/models/lipsync
/workspace/models/whisper
/workspace/models/text_encoders
/workspace/models/vae
/workspace/cache/huggingface
/workspace/cache/torch
/workspace/outputs
/workspace/logs
```

## Environment Variables

Set:

```bash
HF_HOME=/workspace/cache/huggingface
TORCH_HOME=/workspace/cache/torch
OPEN_HIGGSFIELD_OUTPUT_DIR=/workspace/outputs
OPEN_HIGGSFIELD_LOG_DIR=/workspace/logs
```

Later remote-worker env vars belong in a machine-local env file, not hardcoded into the template.

## Runtime Profiles

For first launch:

- keep [backend/models/runtime_config.env](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/models/runtime_config.env) on `local_ffmpeg` locally
- on the GPU box, switch toward the dedicated remote/worker runner profile after services are installed

Use:

```bash
python3 -m backend.models.use_runtime_profile --list
python3 -m backend.models.use_runtime_profile local_ffmpeg
python3 -m backend.models.use_runtime_profile remote_bridge
```

## Startup Services

The machine should start two things:

1. `ComfyUI`
2. Open Higgsfield runner/backend bridge services

Suggested startup order:

1. mount persistent storage
2. export cache env vars
3. start ComfyUI
4. start runner/backend bridge
5. write logs to `/workspace/logs`

## What To Bake Into The Template

Bake in:

- OS packages
- Python
- ComfyUI
- custom nodes
- Open Higgsfield repo checkout
- backend code
- runner scripts
- startup scripts

Do not bake in:

- large model weights
- outputs
- ephemeral Hugging Face downloads if they can live on persistent storage

## First Boot Tasks

On first boot:

1. confirm GPU and CUDA visibility
2. confirm `ffmpeg`
3. confirm ComfyUI starts
4. confirm repo paths
5. download first model wave
6. run a local smoke test
7. connect runner profile

## First Test Wave

Only test these first:

1. `Wan2.2-TI2V-5B`
2. `LatentSync`
3. `WhisperX`

Why:

- keeps the first machine focused
- avoids long setup time
- avoids huge storage churn

## Expansion Wave

After first machine stability:

1. `Wan 2.2 Animate`
2. `Wan 2.2 S2V`
3. `Wan 2.1 VACE`
4. `LTX-2 / LTX-2.3`
5. `MuseTalk`

## Decision Summary

If moving quickly right now:

- machine: `RTX 5090`
- disk: `500GB`
- template: private
- initial model wave:
  - `Wan2.2-TI2V-5B`
  - `LatentSync`
  - `WhisperX`
