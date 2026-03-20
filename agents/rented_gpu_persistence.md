# Open Higgsfield AI: Rented GPU Persistence Checklist

Last updated: 2026-03-19

This file exists for one reason:

Rented GPU compute is disposable unless state is preserved deliberately.

From now on, every rented GPU session should end by checking this list.

## Four Kinds of "Saved"

There are four different meanings of saved:

### 1. Saved in GitHub

This means:

- code is committed
- code is pushed
- docs are pushed
- scripts are pushed

If the instance dies, GitHub state survives.

Examples:

- backend code
- setup scripts
- planning docs
- runner code

### 2. Saved on Persistent Volume

This means:

- files live on attached storage that survives instance restart/replacement

If the instance dies but the volume survives, these survive.

Examples:

- model weights
- caches
- outputs
- repo clone
- venvs / conda envs if stored on the volume

### 3. Saved in a Private Template / Snapshot

This means:

- a reusable machine image exists
- OS packages are already installed
- Python envs and tools may already be installed

If a new instance is created from the template, base setup is restored quickly.

Examples:

- ComfyUI
- ffmpeg
- system packages
- prebuilt runtime layers

### 4. Not Actually Saved

This means:

- only running in RAM / current shell / current instance
- not pushed
- not snapshotted
- not stored on persistent volume

If the instance dies, it is gone.

Examples:

- current shell state
- running tmux session
- active build process
- downloaded files on ephemeral root disk only

## End-of-Session Checklist

Before ending any rented GPU session:

### A. Save code and docs

- commit local repo changes
- push to GitHub
- verify latest commit is on remote

### B. Save machine-local notes

- write a short session note:
  - what worked
  - what failed
  - exact blocker
  - next command to run

Store this in the repo or on persistent volume.

### C. Verify persistent storage location

Confirm the important items are on persistent volume, not only on ephemeral disk:

- repo clone
- model repos
- model weights
- Hugging Face cache
- Torch cache
- outputs
- logs
- env files

### D. Preserve environment reproducibility

Export or record:

- conda env names
- Python versions
- critical install commands
- special torch/CUDA versions

At minimum store:

- exact commands used
- package exceptions or workarounds

### E. Decide whether template/snapshot is needed

If the machine is in a good state:

- make a private template or snapshot

Especially after:

- system package installs
- working ComfyUI setup
- working Python envs
- working model runtime proof

### F. Kill or ignore temporary processes intentionally

Record whether a process is:

- safe to kill
- safe to leave
- required to continue later

Never assume a running process means work is saved.

## What Must Be Preserved For This Project

### Always push to GitHub

- repo code
- backend changes
- runner code
- setup scripts
- planning docs

### Always keep on persistent volume

- `/workspace/Open-Higgsfield-AI`
- `/workspace/model_repos`
- `/workspace/venvs` or conda env metadata
- `/workspace/cache/huggingface`
- `/workspace/cache/torch`
- `/workspace/models`
- `/workspace/outputs`
- `/workspace/logs`
- `/workspace/gpu.env`

### Strongly consider snapshot/template after success

- after first successful `LatentSync` run
- after first successful `Wan` run
- after ComfyUI + backend + model stack is stable

## Minimum Recovery Data To Save

If short on time, save at least:

1. pushed repo
2. session note
3. persistent volume paths
4. exact env names
5. exact model download commands
6. exact blocker

## Session Note Template

Use this structure:

```text
Date:
Machine:
Persistent volume path:

Working:
- ...

Installed:
- ...

Model downloads completed:
- ...

Blocked on:
- ...

Next command:
- ...
```

## Project-Specific Warning

For this project, the biggest risk is assuming:

- "the tmux session still exists"
- "the machine is still running"
- "the install logs are visible"

means the work is preserved.

That is not enough.

The work is only really preserved if it is in:

- GitHub
- persistent volume
- template/snapshot
- explicit saved notes
