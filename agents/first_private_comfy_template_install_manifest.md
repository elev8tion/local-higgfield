# Open Higgsfield AI: First Private Comfy Template Install Manifest

Last updated: 2026-03-19

This document turns the first private `ComfyUI` template into an installable manifest.

It answers:

- exactly which node repos to install first
- exactly which workflow files to keep first
- exactly where to place models
- exactly which env values the backend should point at

This is the first-wave manifest only.

## 1. First-Wave Node Repos

Install these first.

### A. Core `ComfyUI`

Use the latest `ComfyUI` build first.

Why:

- `Wan 2.2` support is documented as native/core workflow support in current Comfy docs
- official docs explicitly say to update `ComfyUI` and use the built-in `Workflow -> Browse Templates -> Video` templates for `Wan 2.2`

Use:

- `comfyanonymous/ComfyUI`

### B. Video I/O

Install:

- `Kosinkadink/ComfyUI-VideoHelperSuite`

Why:

- this is the standard video load/save utility layer in a large part of the Comfy ecosystem
- it gives stable video load/combine helpers for many exported workflows

### C. `LatentSync`

Install:

- `jiafuzeng/comfyui-LatentSync`

Why:

- this is the closest thing to the direct `LatentSync` Comfy path tied to the actual model family
- it is a better first choice than wrapper variants when the goal is fidelity to the original model

### D. `MuseTalk`

Install:

- `AIFSH/ComfyUI-MuseTalk_FSH`

Why:

- it is a working Comfy node path specifically for `MuseTalk`
- it clearly documents its additional package and model requirements
 
`MuseTalk` is no longer part of the first validation wave.
Keep it as the first second-wave add after `Wan 2.2 I2V` and `LatentSync` are proven.

## 2. First-Wave Node Repos Summary

Clone into:

```text
/workspace/ComfyUI/custom_nodes/
```

Target repos:

```text
https://github.com/comfyanonymous/ComfyUI
https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
https://github.com/jiafuzeng/comfyui-LatentSync
```

## 3. First-Wave Workflow Files

Keep only these first:

```text
/workspace/comfy/workflows/open_higgsfield/video.animate_image.wan_i2v.json
/workspace/comfy/workflows/open_higgsfield/lipsync.video_audio.latentsync.json
```

### Workflow meaning

- `video.animate_image.wan_i2v.json`
  - exported API workflow for `video.animate_image`
  - target model family: `Wan 2.2 I2V`
- `lipsync.video_audio.latentsync.json`
  - exported API workflow for `lipsync.video_audio`
  - target model family: `LatentSync`
## 4. First-Wave Model Placement

### A. `Wan 2.2 I2V`

For `Wan 2.2`, use the official Comfy folder layout:

```text
/workspace/comfy/ComfyUI/models/diffusion_models/
/workspace/comfy/ComfyUI/models/text_encoders/
/workspace/comfy/ComfyUI/models/vae/
```

For the first wave, the exact filenames depend on the chosen official `Wan 2.2 I2V` workflow you export, but the model family belongs in those three locations.

### B. `LatentSync`

Keep the `LatentSync` checkpoints in the node’s expected checkpoint area, or in the exact location the chosen node repo requires.

At minimum the original model family requires:

```text
latentsync_unet.pt
whisper/tiny.pt
```

If the chosen Comfy node expects more helper weights, keep them on persistent storage and do not rely on container-local temp download.

### C. `MuseTalk`

`MuseTalk` is deferred from first wave.
Keep its model tree planning, but do not install it before the first two workflows are proven.

## 5. Exact First Machine-Local Env Block

Use this on the worker where backend and `ComfyUI` both run during first-wave validation.

Use this block as the first-wave machine-local backend config:

```bash
OPEN_HIGGSFIELD_VIDEO_COMMAND=python3 -m backend.runners.comfy_video_runner --payload "{payload_path}" --output "{output_path}"
OPEN_HIGGSFIELD_LIPSYNC_COMMAND=python3 -m backend.runners.comfy_lipsync_runner --payload "{payload_path}" --output "{output_path}"

OPEN_HIGGSFIELD_COMFY_BASE_URL=http://127.0.0.1:18188
OPEN_HIGGSFIELD_COMFY_TOKEN=
OPEN_HIGGSFIELD_COMFY_POLL_INTERVAL=2.0
OPEN_HIGGSFIELD_COMFY_MAX_ATTEMPTS=300

OPEN_HIGGSFIELD_COMFY_VIDEO_GENERATE_WORKFLOW=
OPEN_HIGGSFIELD_COMFY_VIDEO_ANIMATE_IMAGE_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/video.animate_image.wan_i2v.json
OPEN_HIGGSFIELD_COMFY_VIDEO_TRANSFORM_WORKFLOW=
OPEN_HIGGSFIELD_COMFY_LIPSYNC_VIDEO_AUDIO_WORKFLOW=/workspace/comfy/workflows/open_higgsfield/lipsync.video_audio.latentsync.json
```

## 6. Exact First Template Setup Order

1. Install `ComfyUI`
2. Install `VideoHelperSuite`
3. Install `comfyui-LatentSync`
4. Restart `ComfyUI`
5. Confirm node imports are clean
6. Download first-wave models into persistent paths
7. Load and run each workflow directly inside `ComfyUI`
8. Export each workflow as API JSON
9. Save the workflow API JSON files into `/workspace/comfy/workflows/open_higgsfield`
10. Point backend env vars at those files
11. Run backend on the same worker
12. Switch backend to `comfy_bridge`
13. Test from the existing chat interface

## 7. Exact First Direct Comfy Validation

Before touching backend integration, confirm these 3 all run once inside raw `ComfyUI`:

1. `Wan 2.2 I2V`
   - one portrait image
   - output short `9:16` clip
2. `LatentSync`
   - one short source video
   - one short audio clip

If any workflow does not run directly inside `ComfyUI`, do not point the backend at it yet.

## 8. Exact First Backend Validation

After direct Comfy success:

1. switch runtime profile:

```bash
python3 -m backend.models.use_runtime_profile comfy_bridge
```

2. export machine-local env values
3. restart backend
4. run one app job for each:
   - `video.animate_image`
   - `lipsync.video_audio`

## 9. Exact “Not Yet” Node Repos

Do not install these in the first template unless one of your chosen workflows explicitly requires them:

- extra caption tooling nodes
- lyrics or subtitle compositor nodes
- large all-in-one utility packs
- second-wave Wan control/extend ecosystems
- `VACE`-specific extras
- experimental `LTX` wrappers

## 10. First Expansion After Success

After the first 3 workflows are stable, add in this order:

1. `Wan 2.2 S2V`
2. `Wan 2.2 Animate`
3. `Wan 2.1 VACE`
4. `MuseTalk`
5. explicit `video.extend`
6. captions
7. lyrics
