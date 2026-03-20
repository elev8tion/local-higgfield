# Open Higgsfield AI: First Private Comfy Template Checklist

Last updated: 2026-03-19

This is the exact first private `ComfyUI` template checklist for the rented GPU path.

The goal is:

- keep `ComfyUI` as the hidden execution engine
- keep your chat interface as the only user-facing UI
- avoid re-downloading models every time
- avoid native model bring-up pain on disposable rented GPUs

This checklist is intentionally narrow.

It is for the first private creator-video template, not every future workflow.

## 1. Machine

Use:

- `RTX 5090`
- `500GB` persistent storage

If `500GB` is not available:

- `300GB` is the minimum

Do not choose:

- a tiny disk
- a template that hides too much setup state from you
- a community image as the long-term production base

## 2. Base Template Shape

Start from:

- clean `ComfyUI`-capable CUDA image
- Ubuntu `22.04` or `24.04`
- CUDA `12.x`
- Python already working

The private template should contain:

- `ComfyUI`
- your required custom nodes
- your workflow JSON files
- your model folders on persistent storage
- this repo cloned into `/workspace/Open-Higgsfield-AI`

## 3. First Workflow Scope

Only install and wire these first:

1. `video.animate_image`
   - first real workflow: `Wan 2.2 I2V`
2. `lipsync.video_audio`
   - first real workflow: `LatentSync`

Do not start by wiring:

- `lipsync.image_audio`
- `video.extend`
- captions
- lyrics
- `Wan 2.2 S2V`
- `Wan 2.2 Animate`
- `Wan 2.1 VACE`

Those belong to the second wave.

## 4. Exact Folder Layout

Use this layout on persistent storage:

```text
/workspace/Open-Higgsfield-AI
/workspace/ComfyUI
/workspace/ComfyUI/custom_nodes
/workspace/comfy/workflows/open_higgsfield
/workspace/models/checkpoints
/workspace/models/clip
/workspace/models/clip_vision
/workspace/models/diffusion_models
/workspace/models/text_encoders
/workspace/models/vae
/workspace/models/loras
/workspace/models/audio
/workspace/models/insightface
/workspace/cache/huggingface
/workspace/cache/torch
/workspace/outputs
/workspace/logs
```

Use persistent storage for:

- models
- caches
- outputs
- custom nodes
- workflow JSONs

Do not rely on container-local temp paths for anything expensive to rebuild.

## 5. Exact First Custom Node Scope

Install only what the first 3 workflows need.

### Required base utility nodes

Install:

- video load/save nodes
- any workflow helper nodes required by your chosen exported workflows

At minimum, expect to need a video I/O node pack for:

- load video
- save video
- frame sequence handling

### First model-specific node scope

Install nodes needed for:

- `Wan 2.2 I2V`
- `LatentSync`
- `MuseTalk`

Do not install giant all-in-one node packs unless one is truly required by a chosen workflow.

Rule:

- install only the repos required by the exact exported workflows you plan to use first

## 6. Exact First Model Scope

Install only:

- `Wan 2.2 I2V`
- `LatentSync`

Optional:

- lightweight helper assets those workflows require

Do not install yet:

- `Wan 2.2 S2V`
- `Wan 2.2 Animate`
- `Wan 2.1 VACE`
- `LTX` family
- premium image stack

## 7. Exact Workflow Files To Store

Create and keep these workflow JSON files on the GPU machine:

```text
/workspace/comfy/workflows/open_higgsfield/video.animate_image.wan_i2v.json
/workspace/comfy/workflows/open_higgsfield/lipsync.video_audio.latentsync.json
```

These should be:

- exported `ComfyUI` API workflows
- tested directly in `ComfyUI` first
- then referenced by the backend bridge

Do not point the backend at a workflow that has not already succeeded once in raw `ComfyUI`.

## 8. Workflow Output Rule

Each workflow should produce:

- one primary media output

Best practice:

- one output node per workflow
- save to Comfy output
- make sure it appears in `ComfyUI` history as a downloadable media output

That is what the current bridge expects.

## 9. Exact Backend Runtime Profile

On the worker machine, switch to:

```bash
python3 -m backend.models.use_runtime_profile comfy_bridge
```

That makes the backend use:

- [backend/runners/comfy_video_runner.py](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/runners/comfy_video_runner.py)
- [backend/runners/comfy_lipsync_runner.py](/Users/kcdacre8tor/Open-Higgsfield-AI/backend/runners/comfy_lipsync_runner.py)

## 10. Exact Env Vars To Fill

Fill these in the machine-local env:

```bash
OPEN_HIGGSFIELD_VIDEO_COMMAND=python3 -m backend.runners.comfy_video_runner --payload "{payload_path}" --output "{output_path}"
OPEN_HIGGSFIELD_LIPSYNC_COMMAND=python3 -m backend.runners.comfy_lipsync_runner --payload "{payload_path}" --output "{output_path}"

OPEN_HIGGSFIELD_COMFY_BASE_URL=http://127.0.0.1:18188
OPEN_HIGGSFIELD_COMFY_TOKEN=
OPEN_HIGGSFIELD_COMFY_POLL_INTERVAL=2.0
OPEN_HIGGSFIELD_COMFY_MAX_ATTEMPTS=300

OPEN_HIGGSFIELD_COMFY_VIDEO_ANIMATE_IMAGE_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/video.animate_image.wan_i2v.json
OPEN_HIGGSFIELD_COMFY_LIPSYNC_VIDEO_AUDIO_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/lipsync.video_audio.latentsync.json
```

Leave these empty for the first wave:

```bash
OPEN_HIGGSFIELD_COMFY_VIDEO_GENERATE_WORKFLOW=
OPEN_HIGGSFIELD_COMFY_VIDEO_TRANSFORM_WORKFLOW=
```

## 11. Exact First Validation Order

Validate in this order:

1. confirm `ComfyUI` opens
2. confirm both first-wave workflows run directly in `ComfyUI`
3. export each workflow as API JSON
4. store the exported JSON in `/workspace/comfy/workflows/open_higgsfield`
5. point the env vars at those files
6. run the backend on the same worker
7. switch backend profile to `comfy_bridge`
8. restart backend
9. run one backend job per workflow from the existing chat interface

Do not skip direct `ComfyUI` validation first.
Do not split backend and ComfyUI onto separate machines during the first proof path.

## 12. Exact First End-to-End Tests

Run exactly these 3 product-path tests:

### Test 1

- feature: `video.animate_image`
- workflow: `Wan 2.2 I2V`
- input: one ultra-real portrait image
- output target: short `9:16` creator clip

### Test 2

- feature: `lipsync.video_audio`
- workflow: `LatentSync`
- input: one short source video + one audio clip
- output target: synced creator clip

## 13. Exact “Do Not Add Yet” List

Do not add these to the first private template:

- `lipsync.image_audio`
- `Wan 2.2 S2V`
- `Wan 2.2 Animate`
- `Wan 2.1 VACE`
- captions pipeline
- lyrics pipeline
- multi-output workflows
- subtitle text artifacts
- `video.extend`

That keeps the first template small enough to stabilize.

## 14. Exact Second-Wave Additions

After the first 3 workflows work through the backend:

1. add `lipsync.image_audio` with `MuseTalk`
2. add `Wan 2.2 S2V`
3. add `Wan 2.2 Animate`
4. add `Wan 2.1 VACE`
5. add explicit `video.extend`
6. add captions
7. add lyrics

## 15. Bottom Line

The first private `ComfyUI` template should be:

- one machine
- one persistent model/cache layout
- 3 real workflows
- backend pointed at those workflows
- no unnecessary second-wave models

That is the fastest stable path from rented GPU to working product integration.
