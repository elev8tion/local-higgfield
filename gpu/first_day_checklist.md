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

## Smoke Checks

Run local smoke tests from the repo:

```bash
python3 -m backend.runners.smoke_test
python3 -m backend.runners.remote_smoke_test
```

## Deferred Later

Tracked in:

- [agents/deferred_work.md](/Users/kcdacre8tor/Open-Higgsfield-AI/agents/deferred_work.md)
