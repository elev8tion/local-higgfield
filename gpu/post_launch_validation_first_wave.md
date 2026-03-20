# First-Wave Post-Launch Validation

Use this after the Vast instance finishes provisioning.

## 1. Confirm Vast/Comfy base

- open the Vast `Open` button
- confirm `ComfyUI` loads
- confirm the port is the intended `18188`
- confirm the actual Comfy path on disk is `/workspace/ComfyUI`

## 2. Confirm custom nodes loaded

Inside the machine:

```bash
cd /workspace/ComfyUI/custom_nodes
ls
```

Expected first-wave repos:

- `ComfyUI-VideoHelperSuite`
- `comfyui-LatentSync`

## 3. Confirm workflow folder exists

```bash
ls /workspace/comfy/workflows/open_higgsfield
```

Expected starter files:

- `lipsync.video_audio.latentsync.json`
- `video.animate_image.wan_i2v.json`

## 4. Install first-wave models

Install only:

- `Wan 2.2 I2V`
- `LatentSync`

Do not install second-wave models yet.

## 5. Direct Comfy workflow proof

Run each workflow directly in `ComfyUI` before backend wiring:

1. `Wan 2.2 I2V`
2. `LatentSync`

## 6. Export real API workflows

After each workflow succeeds in raw `ComfyUI`:

- export as API JSON
- overwrite the starter file in `/workspace/comfy/workflows/open_higgsfield`

## 7. Apply backend bridge config

Use:

- [backend_worker_env_first_wave.txt](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/backend_worker_env_first_wave.txt)

and:

```bash
python3 -m backend.models.use_runtime_profile comfy_bridge
```

## 8. Restart backend

Restart the backend on the same worker after the env is in place.

Do not split backend and ComfyUI across machines yet.

## 9. End-to-end product tests

From the existing app/chat interface, run:

1. one `video.animate_image` job
2. one `lipsync.video_audio` job

## 10. Do not freeze the template yet

Do not consider the template final until:

- both first-wave workflows run in raw `ComfyUI`
- both first-wave workflows run through the backend bridge
- outputs return into the normal app result flow

## 11. First-wave architecture rule

For the first proof path:

- frontend may stay remote or local
- backend should run on the worker
- ComfyUI should run on the same worker

That removes one unnecessary failure layer during validation.

`MuseTalk` is deferred to the second wave.
