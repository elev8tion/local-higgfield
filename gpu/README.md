# GPU Setup

This folder contains the first practical setup artifacts for the rented GPU machine.

Use this for the first private template and first-machine bring-up.

## Files

- [bootstrap.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/bootstrap.sh)
  - installs base OS packages and Python tooling
- [install_first_wave.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/install_first_wave.sh)
  - prepares workspace layout, Python envs, ComfyUI, backend deps, and first-wave runtime packages
- [start_services.sh](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/start_services.sh)
  - starts ComfyUI and the Open Higgsfield backend services
- [gpu.env.example](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/gpu.env.example)
  - machine-local environment file template
- [first_day_checklist.md](/Users/kcdacre8tor/Open-Higgsfield-AI/gpu/first_day_checklist.md)
  - step-by-step bring-up order for the first rented machine

## Intended First Machine

- `RTX 5090`
- `500GB` persistent disk preferred
- initial model wave:
  - `Wan2.2-TI2V-5B`
  - `LatentSync`
  - `WhisperX`
  - optional `MuseTalk`

## Usage

On the rented machine:

```bash
cd /workspace/Open-Higgsfield-AI
cp gpu/gpu.env.example /workspace/gpu.env
$EDITOR /workspace/gpu.env
bash gpu/bootstrap.sh
bash gpu/install_first_wave.sh
bash gpu/start_services.sh
```

Anything not implemented yet is tracked in:

- [agents/deferred_work.md](/Users/kcdacre8tor/Open-Higgsfield-AI/agents/deferred_work.md)
