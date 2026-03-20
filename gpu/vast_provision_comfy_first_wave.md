# Vast First-Wave Provisioning Script

Use this script as the `PROVISIONING_SCRIPT` value in Vast:

- [gpu/vast_provision_comfy_first_wave.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/vast_provision_comfy_first_wave.sh)

## Raw GitHub URL

Use the raw URL for the current `main` branch file:

```text
https://raw.githubusercontent.com/elev8tion/local-higgfield/main/gpu/vast_provision_comfy_first_wave.sh
```

## What it does

- clones or updates this repo into `/workspace/Open-Higgsfield-AI`
- clones the first-wave custom nodes:
  - `ComfyUI-VideoHelperSuite`
  - `comfyui-LatentSync`
- creates the first-wave workflow directory
- copies starter workflow JSON files into the worker path
- installs available Python requirements files
- exports the first-wave `Open Higgsfield` `ComfyUI` env block
- reuses Vast's `/venv/main` when available instead of inventing another first-wave Python env

## What it does not do

- download all models
- configure second-wave workflows
- solve every custom-node dependency edge case
- validate a workflow automatically

## Required next steps after launch

1. open `ComfyUI`
2. verify the custom nodes load cleanly
3. install model files for:
   - `Wan 2.2 I2V`
   - `LatentSync`
4. run each workflow directly in `ComfyUI`
5. export the real API workflows over the starter placeholder JSON files
6. run the backend on the same worker for the first validation wave
7. point the backend/runtime profile at those real workflow files

`MuseTalk` is intentionally deferred from the first wave.
It remains a second-wave workflow after the worker path is proven with `Wan 2.2 I2V` and `LatentSync`.
