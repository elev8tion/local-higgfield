## Grounded Senior Workflow

Use these rules for all planning, implementation, refactors, GPU setup, workflow design, and status updates in this repo.

This project is not a generic app build.
It is a staged migration from placeholder and external-provider behavior toward a backend-owned, GPU-backed execution platform.

The operating standard here is senior-level, grounded delivery:

- smallest correct next step
- clear boundaries
- no fake certainty
- no overbuilding
- no claiming a workflow is done before it is actually verified

## Core Operating Rules

1. Prefer the smallest correct next step.
2. Separate `must do now` from `could do later`.
3. Do not add phases, wrappers, adapters, or abstractions unless the code clearly needs them.
4. Keep shared logic shared and keep runtime-specific behavior local to the runtime.
5. Say when something is unverified, partially proven, provider-dependent, or only documented but not yet run.
6. Do not overstate deployment, testing, runtime readiness, or GPU validation.
7. Treat rented GPU state as disposable unless it is explicitly persisted.

## Project-Specific Senior Rules

### Frontend vs execution boundary

- The app UI is the control plane.
- `ComfyUI` is an execution engine, not the product UI.
- Do not blur those roles.
- Keep user-facing behavior in the app, not in raw `ComfyUI`.

### Backend boundary

- Preserve the backend job contract unless there is a strong reason to change it.
- Prefer evolving runner implementations behind the contract rather than rewriting the frontend.
- If a feature can fit the current job contract cleanly, use that path first.
- If it cannot, call that out directly and define the missing contract instead of hiding it.

### Workflow scope

- First-wave workflows should stay narrow and testable.
- Do not install or wire second-wave models before the first-wave path is proven.
- One stable workflow is better than three half-wired ones.
- A direct `ComfyUI` proof should happen before backend integration.

### Rented GPU discipline

- Never assume instance-local work is saved unless it is pushed, templated, or on persistent storage.
- Distinguish clearly between:
  - saved in GitHub
  - saved on persistent storage
  - saved in a reusable template
  - lost if the instance is destroyed
- Avoid long native build detours on rented GPUs if a template-based Comfy path is cleaner.

### Planning discipline

- Do not plan the entire end-state when the next real blocker is one workflow or one machine launch.
- Choose the first proof path that reduces uncertainty fastest.
- Prefer "prove one real end-to-end path" over "prepare every possible future path."

## Good Senior Patterns For This Repo

- Keep the backend API stable while swapping execution layers underneath it.
- Keep runtime profiles simple and explicit.
- Prefer one clean runner per runtime path over a large optional mega-runner.
- Keep first-wave model ownership and workflow files explicit.
- Use documentation as operational truth only if it is kept current with the code.
- When something is only a starter template or placeholder, label it as such.

## What To Push Back On

Push back when a request would:

- add abstraction before the current path is proven
- duplicate the same logic across backend runners or docs
- confuse the app UI with `ComfyUI`
- treat a documented plan as if it were a live verified deployment
- widen the first-wave scope before first-wave validation is complete
- add GPU setup complexity that is not justified by the current stage

## Communication Rules

- Be direct.
- Be concrete.
- Use simple answers when the question is simple.
- If something is unknown, say it plainly.
- If something is recommended but not proven, say that plainly too.
- If proposing a workflow, explain the tradeoff in one sentence and stop.

## Status Language

Use these distinctions consistently:

- `implemented`
  - code or docs exist in the repo
- `validated`
  - it has actually been run and checked
- `prepared`
  - the path exists, but live execution is still pending
- `deferred`
  - intentionally not in current scope

Do not collapse those into one another.

## Default Decision Bias

When multiple paths are possible:

1. choose the path with the least hidden state
2. choose the path easiest to validate end-to-end
3. choose the path easiest to preserve on rented infrastructure
4. only then optimize for broader future flexibility
