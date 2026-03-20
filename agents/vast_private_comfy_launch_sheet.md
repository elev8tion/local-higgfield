# Open Higgsfield AI: Vast Private Comfy Launch Sheet

Last updated: 2026-03-19

This is the exact launch sheet for the first private `ComfyUI` worker on Vast.ai.

It is based on Vast's current official docs for:

- RTX 5-series compatibility
- `ComfyUI` video-generation template guidance
- persistent storage behavior
- `PROVISIONING_SCRIPT`
- `PORTAL_CONFIG`
- Jupyter/direct access

## 1. Instance Type

Choose:

- `On-demand`

Do not choose for the first production bring-up:

- `Interruptible`

Why:

- Vast documents `On-demand` as the production/high-priority path
- `Interruptible` instances may be paused and are not the right first choice for a model/template bring-up

## 2. GPU

Choose:

- `RTX 5090`

Why:

- this is the first practical machine for the creator-video stack
- Vast explicitly documents special compatibility requirements for RTX 5-series

## 3. Template

Choose:

- Vast's recommended `ComfyUI` template

Do not:

- switch to a random community image for the first launch
- override the image with a different Docker image unless we later build our own image intentionally

Why:

- Vast's docs say the `ComfyUI` template is the recommended path for video generation
- the template includes:
  - SSH and Jupyter access
  - Instance Portal
  - token auth by default
  - provisioning support

## 4. Version / Image Rule

Keep:

- the template's `[Automatic]` version tag

Do not:

- manually switch to a different Docker image for the `5090`

Why:

- Vast explicitly warns that RTX 5-series requires compatible `CUDA 12.8` and `PyTorch 2.7+`
- they also explicitly warn not to change the Docker image if you want to preserve 5-series compatibility

## 5. Storage

Choose:

- `500GB` container storage if you are doing the first fast bring-up

If available and practical:

- also plan for a `Volume` on the same host later for model persistence beyond instance destruction

Important Vast behavior:

- container storage persists while the instance exists, including when stopped
- container storage is deleted when the instance is destroyed
- volumes survive instance destruction, but only on the same physical machine

So the practical first choice is:

- `500GB` container storage

The better persistence upgrade later is:

- same-host volume for models/workflows/caches

## 6. Recommended Launch Mode

Use:

- Jupyter or SSH launch mode

Practical preference:

- SSH for backend/dev work
- Jupyter/Instance Portal for easy browser access if needed

## 7. Exact Environment Variables To Set In Vast Template

Set these in the Vast template or instance environment variables section.

### Core Comfy

```bash
COMFYUI_ARGS=--disable-auto-launch --port 18188 --enable-cors-header
WEB_ENABLE_HTTPS=false
WEB_ENABLE_AUTH=true
OPEN_BUTTON_PORT=18188
```

### Provisioning

```bash
PROVISIONING_SCRIPT=<raw-script-url>
```

This should point to your private setup script that:

- clones this repo if missing
- installs first-wave custom nodes
- creates workflow folders
- optionally syncs workflow JSONs
- optionally exports env vars to `/etc/environment`

### Optional model auth

```bash
HF_TOKEN=<your-token-if-needed>
```

Use only if one or more model downloads require Hugging Face auth.

## 8. Exact First Provisioning Script Responsibilities

Your first Vast `PROVISIONING_SCRIPT` should do only this:

1. move to `/workspace`
2. activate `/venv/main`
3. clone or update `/workspace/Open-Higgsfield-AI`
4. clone required custom node repos into `/workspace/ComfyUI/custom_nodes` or the template's actual Comfy path
5. create:
   - `/workspace/comfy/workflows/open_higgsfield`
   - `/workspace/models/...`
   - `/workspace/logs`
6. export needed env vars to `/etc/environment`
7. optionally pull workflow JSON files from the repo into the workflow folder
8. optionally reload supervisor/portal if needed

Do not make the first provisioning script:

- download every large model family
- install second-wave tooling
- install captions/lyrics stack
- do heavyweight one-off experiments

## 9. Exact First Backend Mapping

The backend should point to the remote `ComfyUI` worker using the `comfy_bridge` profile.

The first-wave workflow mappings should be:

- `video.animate_image` -> `Wan 2.2 I2V`
- `lipsync.video_audio` -> `LatentSync`
- `lipsync.image_audio` -> `MuseTalk`

## 10. Exact First Env Block For Open Higgsfield On The Worker

Use this block in the machine-local env file:

```bash
OPEN_HIGGSFIELD_VIDEO_COMMAND=python3 -m backend.runners.comfy_video_runner --payload "{payload_path}" --output "{output_path}"
OPEN_HIGGSFIELD_LIPSYNC_COMMAND=python3 -m backend.runners.comfy_lipsync_runner --payload "{payload_path}" --output "{output_path}"

OPEN_HIGGSFIELD_COMFY_BASE_URL=http://127.0.0.1:18188
OPEN_HIGGSFIELD_COMFY_TOKEN=
OPEN_HIGGSFIELD_COMFY_POLL_INTERVAL=2.0
OPEN_HIGGSFIELD_COMFY_MAX_ATTEMPTS=300

OPEN_HIGGSFIELD_COMFY_VIDEO_ANIMATE_IMAGE_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/video.animate_image.wan_i2v.json
OPEN_HIGGSFIELD_COMFY_LIPSYNC_VIDEO_AUDIO_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/lipsync.video_audio.latentsync.json
OPEN_HIGGSFIELD_COMFY_LIPSYNC_IMAGE_AUDIO_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/lipsync.image_audio.musetalk.json
```

## 11. Exact First Launch Checklist

1. choose `On-demand`
2. choose `RTX 5090`
3. choose Vast recommended `ComfyUI` template
4. keep `[Automatic]` image/version behavior
5. set `500GB` storage
6. set `COMFYUI_ARGS`
7. set `OPEN_BUTTON_PORT=18188`
8. set `PROVISIONING_SCRIPT`
9. launch instance
10. confirm `ComfyUI` opens through Vast access path
11. confirm custom nodes loaded cleanly
12. run first 3 workflows directly in `ComfyUI`
13. export workflows as API JSON
14. point backend env vars at those workflow files
15. switch backend to `comfy_bridge`
16. test from the existing chat interface

## 12. Exact “Do Not Do” List

Do not:

- destroy the instance before backing up anything important
- assume container storage survives destruction
- switch Docker image on a `5090`
- choose `Interruptible` for the first serious setup
- install second-wave models before first-wave workflows are proven

## 13. Sources

- [Vast RTX 5 Series](https://docs.vast.ai/rtx-5-series)
- [Vast Video Generation / ComfyUI](https://docs.vast.ai/video-generation)
- [Vast Advanced Template Setup](https://docs.vast.ai/documentation/templates/advanced-setup)
- [Vast Storage Types](https://docs.vast.ai/documentation/instances/storage/types)
- [Vast Instance Types](https://docs.vast.ai/documentation/instances/choosing/instance-types)
- [Vast Jupyter](https://docs.vast.ai/documentation/instances/connect/jupyter)
- [Vast Docker Execution Environment](https://docs.vast.ai/documentation/instances/docker-environment)
