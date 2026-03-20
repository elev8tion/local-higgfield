# First Day Checklist

## Machine

- rent the `RTX 5090`
- attach `500GB` persistent storage
- mount the workspace volume at `/workspace`

## Repo

```bash
cd /workspace
git clone <your-repo-url> Open-Higgsfield-AI
cd /workspace/Open-Higgsfield-AI
cp gpu/gpu.env.example /workspace/gpu.env
```

Edit `/workspace/gpu.env`.

## Base Setup

```bash
bash gpu/bootstrap.sh
bash gpu/install_first_wave.sh
```

## First-Wave Model Scope

Install only:

- `Wan2.2-TI2V-5B`
- `LatentSync`
- `WhisperX`
- optional `MuseTalk`

Do not install heavier second-wave models yet.

## Services

```bash
bash gpu/start_services.sh
```

Verify:

- ComfyUI is reachable on `8188`
- backend is reachable on `8000`
- logs exist in `/workspace/logs`

## Comfy Bridge Mode

Once your private `ComfyUI` template is reachable and has the right models/custom nodes installed:

```bash
python3 -m backend.models.use_runtime_profile comfy_bridge
```

Then fill `backend/models/runtime_config.env` or `/workspace/gpu.env` machine-local values for:

- `OPEN_HIGGSFIELD_COMFY_BASE_URL`
- one workflow JSON path per job type you want to expose first

Recommended first exposed workflows:

- `video.animate_image`
- `lipsync.video_audio`
- `lipsync.image_audio`

This lets the existing chat interface call your remote `ComfyUI` worker without exposing `ComfyUI` itself to end users.

## Smoke Checks

Run local smoke tests from the repo:

```bash
python3 -m backend.runners.smoke_test
python3 -m backend.runners.remote_smoke_test
python3 -m backend.runners.comfy_smoke_test
```

## Deferred Later

Tracked in:

- [agents/deferred_work.md](/Users/kcdacre8tor/Open-Higgsfield-AI/agents/deferred_work.md)
