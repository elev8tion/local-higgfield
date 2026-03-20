# Open Higgsfield AI: Codebase Knowledge

Last updated: 2026-03-18

This document is the current source of truth for the repository as it exists today. It captures the real runtime shape, the active data flow, the remaining MuAPI-era coupling, and the safest refactor path toward a GPU-backed execution platform.

## Live Status

This section is the operational tracker. If any older analysis below conflicts with this section, treat this section as authoritative.

### Completed

- typed backend job/status schema added
- backend split into `jobs`, `storage`, `workers`, `models`, and `scheduler` seams
- local asset upload pipeline added
- `ImageStudio` moved onto typed local jobs
- `CinemaStudio` moved onto the local image job path
- `VideoStudio` moved onto typed local video jobs
- `LipSyncStudio` moved onto typed local lipsync jobs
- shared upload flow moved off the old external client path
- obsolete external key-gating UI removed from active runtime
- stale Vite MuAPI proxy removed
- backend model-capability exposure started via `/models`
- frontend model adapter added via `src/lib/modelCatalog.js`
- active runtime dependency on `src/lib/muapi.js` removed and file deleted
- backend job contract validation added before worker dispatch
- command-based video and lipsync runtimes can now load local command config from `backend/models/runtime_config.env`
- local repo-backed command runners added for video and lipsync so the command runtime seam is now wired by default
- typed job submission now infers legacy media URL params into `input_assets` so the stricter backend contract and existing studios stay aligned
- default local video and lipsync runners now perform real `ffmpeg`-based media processing instead of unconditional file copy fallback
- backend command runtime now parses structured JSON stdout from runners and merges that into job result metadata
- lightweight runner smoke test added at `backend/runners/smoke_test.py`
- remote HTTP bridge runners added for video and lipsync so the command seam can target external GPU services without changing the backend API
- stdlib mock remote worker service and remote bridge smoke test added so the remote handoff path can be validated locally without extra Python deps
- runtime profiles and a profile switcher added so the backend can move between local ffmpeg and remote bridge execution without manual env rewrites
- creator-focused feature board and model deployment plan drafted in `agents/model_plan.md`
- hardware board drafted in `agents/hardware_board.md`
- private GPU template blueprint drafted in `agents/private_gpu_template.md`
- deferred work tracker drafted in `agents/deferred_work.md`
- first-day GPU setup assets added under `gpu/`
- rented GPU persistence checklist drafted in `agents/rented_gpu_persistence.md`
- ComfyUI-backed runner path added so video and lipsync jobs can target a private remote Comfy template without changing the frontend API

### In Progress

- moving model ownership from static frontend metadata toward backend-fed capabilities
- replacing default local command runners with real GPU-backed video and lipsync execution runtimes
- preparing the command runtime seam for remote GPU worker handoff
- turning this file into a live implementation document instead of a one-time analysis dump

### Not Started

- persistent job store
- real scheduler/queue semantics
- packaged or supervised backend runtime from Electron
- remote GPU worker integration
- backend-owned full model registry replacing `src/lib/models.js`
- UI redesign pass after architecture stabilizes

### Known Temporary States

- video and lipsync now run through local repo command runners by default; those runners perform local `ffmpeg` processing but are still not model-based inference
- `src/lib/models.js` still exists as transitional frontend fallback metadata
- browser-side localStorage is still used for pending-job resume and upload history
- backend dependencies listed in `backend/requirements.txt` have not been installed in the current local Python environment

### Current Next Step

- point the `comfy_bridge` runtime profile at a private ComfyUI GPU template, replace the starter workflow JSON files with exported API workflows, and validate one end-to-end video job from the existing chat interface

### After That

- reduce frontend dependence on static `models.js` to a fallback-only role
- introduce persistent job storage and queue semantics

## Mission Context

Open Higgsfield AI is being transformed from a frontend that still carries external API assumptions into a modular AI platform where:

- the frontend is the control plane
- the backend owns job submission, scheduling, worker coordination, and outputs
- heavy inference runs on GPU infrastructure, not in the UI

Migration rule:

- preserve the product surface the app already has
- remove the old third-party or placeholder implementation under each feature
- reimplement each feature through our own job, worker, storage, and model pipeline
- treat existing studios and controls as capability targets, not as implementation to keep
- build future features on top of our infrastructure, not on top of legacy MuAPI-shaped contracts

The directive for this pass also allows a later UI refresh, but only after the execution architecture is stable. For now, the priority is preserving the working pipeline and making the system understandable enough to refactor safely.

## Codebase Map

```text
Open-Higgsfield-AI/
  backend/
    server.py
  electron/
    main.js
  src/
    main.js
    components/
      AuthModal.js
      CameraControls.js
      CinemaStudio.js
      Header.js
      ImageStudio.js
      LipSyncStudio.js
      SettingsModal.js
      Sidebar.js
      UploadPicker.js
      VideoStudio.js
    lib/
      localapi.js
      modelCatalog.js
      models.js
      pendingJobs.js
      promptUtils.js
      uploadHistory.js
    styles/
      global.css
      studio.css
      variables.css
    style.css
  public/
    assets/cinema/*.webp
    banner.png
    vite.svg
  docs/
    assets/*
  codetxt/
    AuthModal.txt
    2 draft read me overhaul update.txt
  README.md
  project_knowledge.md
  higgsfield_codex_directive.txt
  package.json
  vite.config.js
  postcss.config.js
  tailwind.config.js
  index.html
  afterPack.js
  models_dump.json
```

## Runtime-Critical Files

- `backend/server.py`
  The only backend service. Handles job creation, background processing, and output exposure.
- `src/main.js`
  Frontend bootstrap and router.
- `src/components/ImageStudio.js`
  Primary working integration with the local `/jobs` backend.
- `src/components/VideoStudio.js`
  Video studio now uses local typed jobs and local polling.
- `src/components/LipSyncStudio.js`
  Lipsync workflow now uses local typed jobs and local polling.
- `src/components/CinemaStudio.js`
  Prompt-driven cinematic image workflow routed through the local image job path.
- `src/lib/localapi.js`
  Local backend client for job creation, polling, result resolution, and asset uploads.
- `src/lib/modelCatalog.js`
  Transitional adapter between backend model-capability exposure and the legacy static frontend model catalog.
- `src/lib/models.js`
  Frontend-owned model registry and selector helpers.
- `electron/main.js`
  Desktop shell entrypoint.
- `package.json`
  Build, Electron packaging, and runtime packaging config.
- `vite.config.js`
  Frontend build config. Legacy MuAPI proxy has been removed.

## Current System Reality

The repo is already halfway through an architectural transition.

What is real today:

- There is a working image path using `ImageStudio -> localapi -> FastAPI /jobs -> output file -> UI polling`.
- `CinemaStudio` also uses the local image job path.
- `VideoStudio` and `LipSyncStudio` now submit local typed jobs and poll local job status.
- Shared uploads now flow through backend asset ingestion instead of a browser-side external client.
- The backend now exposes initial model-capability metadata through `/models`.
- The studios now import model data through `modelCatalog.js` instead of reading `models.js` directly.
- There is a single backend service in `backend/server.py`.
- Electron packages only the frontend shell and does not package or supervise the Python backend.
- The frontend no longer depends on the MuAPI client facade for active execution.
- The project docs describe a modular future system that does not yet exist in code.

What is not real yet:

- a scheduler layer
- persistent job storage
- dedicated workers
- model-specific routing
- a complete backend-owned model registry replacing frontend static model metadata
- packaged local backend execution inside the Electron app
- remote GPU orchestration

## Actual Data Flow

### Working image path

1. User opens `ImageStudio`.
2. UI gathers prompt and settings.
3. `src/lib/localapi.js` sends `POST http://localhost:8000/jobs`.
4. `backend/server.py` creates an in-memory job record.
5. A background Python thread runs `process_job(job_id)`.
6. The worker loads SDXL Turbo, generates an image, and saves `/tmp/<job_id>.png`.
7. Job state is updated in memory.
8. Frontend polls `GET /jobs/{job_id}` until status becomes `completed`.
9. UI displays the result via `/outputs/...`.

### Non-image paths today

Video, lipsync, and cinema now submit local typed jobs through the same backend contract as image.

Current caveat:

- video and lipsync job types now route through command-configurable backend runtimes
- those command values are now prewired to local repo runners through `backend/models/runtime_config.env`
- the default local runners now use `ffmpeg` to synthesize text-to-video output, build image-to-video clips, transform videos, and mux lipsync media inputs, with copy fallback only if `ffmpeg` is unavailable or a command fails
- a real GPU runner can now preserve the same backend API by writing the output file and optionally printing structured JSON metadata on stdout
- a remote GPU worker can now be integrated through the included HTTP bridge runners by swapping the configured command and providing submit/status URLs
- the contract, storage flow, and polling model are now on our pipeline
- the real GPU-backed execution layer for those job types still needs to be implemented

## Backend Findings

### `backend/server.py`

Current behavior:

- FastAPI app with CORS restricted to `http://localhost:5173`
- Static mount: `/outputs` points to `/tmp`
- Global in-memory `jobs` dictionary
- `POST /jobs` accepts `{ type, prompt }`
- `GET /jobs/{job_id}` returns the raw job record
- Background execution uses `threading.Thread`

### Job lifecycle today

Current states:

- `queued`
- `processing`
- `completed`

Missing states and controls:

- `failed`
- `cancelled`
- retries
- timeouts
- persistence
- queue depth or worker ownership

### Execution behavior

Each job:

- imports `diffusers` and `torch` inside the worker
- loads `AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo")`
- chooses `cuda` only if available
- generates one image
- writes the result to `/tmp`

### Backend risks

- The model is loaded per job, which is expensive and will not scale.
- Exceptions are not handled, so failures can leave jobs stuck in `processing`.
- All state is in memory, so restart loses every job.
- The `type` field is accepted but ignored.
- `/tmp` is ephemeral and not application-scoped storage.
- The current thread-per-job approach is not a real worker system.
- CORS is configured for Vite dev, not packaged Electron.

## Frontend Findings

### Architecture

The frontend is plain JavaScript with direct DOM composition. There is no framework-level state layer. Navigation is event-driven and view replacement happens in `src/main.js`.

This keeps the app simple, but also means each studio file contains a lot of mixed responsibility:

- UI rendering
- local state
- dropdown/modal logic
- transport calls
- polling
- result history
- persistence

### `src/main.js`

- Bootstraps the app
- Renders `Header`
- Swaps studios into `contentArea`
- Lazy-loads `VideoStudio`, `CinemaStudio`, and `LipSyncStudio`

Weakness:

- no central route or lifecycle management
- studio cleanup is implicit

### `src/components/ImageStudio.js`

This is the most important frontend file because it is the only studio actively talking to the local backend.

Observations:

- uses `createJob` and `getJob` from `localapi.js`
- still imports `muapi`, `AuthModal`, and pending-job helpers
- mixes old MuAPI persistence assumptions with the new local job path
- is a large, monolithic controller/view

Conclusion:

This is the closest thing to the future architecture, but it still contains migration leftovers.

### `src/components/VideoStudio.js`

Observations:

- supports t2v, i2v, and v2v modes in one file
- depends on `muapi`
- stores pending jobs in localStorage
- expects polling through the MuAPI-style client facade

Conclusion:

Video is still on the old architecture and should eventually move to the same local-job contract as image.

### `src/components/LipSyncStudio.js`

Observations:

- supports image + audio and video + audio workflows
- depends on `muapi.uploadFile` and `muapi.processLipSync`
- stores pending work in localStorage

Conclusion:

Lipsync remains coupled to a fake or legacy transport layer and is not integrated with the actual backend.

### `src/components/CinemaStudio.js`

Observations:

- prompt composition is more advanced here than elsewhere
- uses `CameraControls` and `promptUtils`
- still calls `muapi.generateImage`

Conclusion:

The cinematic prompt system is valuable domain logic, but execution is still pointed at the wrong abstraction.

### `src/components/UploadPicker.js`

Observations:

- solid candidate for reuse
- handles upload UI, history, thumbnails, and multi-select behavior
- transport is hardcoded to `muapi.uploadFile`

Conclusion:

This should survive the refactor, but the uploader must become injectable or backend-backed.

### Auth and settings modals

`AuthModal.js` and `SettingsModal.js` are still built around storing a MuAPI API key in localStorage.

These components were migration debt. They have now been repurposed away from external API keys toward local runtime messaging and backend information.

## Library Findings

### `src/lib/localapi.js`

Current role:

- creates typed jobs
- fetches job status and results
- uploads assets
- resolves output URLs
- waits for completion in shared polling helpers
- exposes backend model-capability fetches

Current weakness:

- hardcoded backend URL: `http://localhost:8000`
- browser-side polling is still implemented in the frontend instead of a more centralized state layer

### `src/lib/modelCatalog.js`

Current role:

- adapter layer in front of `models.js`
- exposes backend model-capability loading and caching
- lets studios depend on a stable catalog module instead of importing the raw generated model dump directly

Conclusion:

This is the correct transition seam for moving model ownership out of the frontend without rewriting every studio at once.

### `src/lib/models.js`

Current role:

- frontend-owned model registry
- selectors and schema helpers for studios

Current weakness:

- registry is static and large
- likely drifts from actual backend capability
- makes the frontend the source of truth for execution metadata

Conclusion:

This should eventually move behind a backend model-registry API.

Important note:

- `models.js` still contains legacy MuAPI-era text in some generated titles, prompts, and metadata examples
- that text is not part of the active execution path anymore
- during registry extraction, treat those strings as stale source metadata and not as product requirements
- the backend registry should keep only capability-relevant fields: job type, parameter schema, defaults, asset requirements, worker compatibility, and implementation status
- backend registry exposure has now started via `/models`
- studios now depend on `modelCatalog.js`, which still uses `models.js` as transitional fallback data

### `src/lib/pendingJobs.js`

Current role:

- localStorage-based persistence of pending local jobs

Current weakness:

- duplicates job-state concerns that should ultimately belong to the backend
- still uses a localStorage resume model rather than a backend-backed queue view

### `src/lib/uploadHistory.js`

Current role:

- upload history persistence
- thumbnail generation

Conclusion:

Useful utility. Lower-risk to keep, though the data format may need versioning later.

### `src/lib/muapi.js`

Status:

- removed from the active codebase after the execution paths were migrated to the local backend pipeline

Meaning:

- there is no longer a frontend runtime facade representing an external inference provider
- any future execution client should be added as an explicit backend transport or worker integration, not as a return to MuAPI-shaped browser code

### `src/lib/promptUtils.js`

Current role:

- cinematic prompt vocabulary
- prompt composition helper

Conclusion:

This is one of the cleanest reusable modules in the repo. It should remain, but the naming should become model-agnostic.

## Electron and Packaging Findings

### `electron/main.js`

Current role:

- creates the Electron window
- loads `dist/index.html`
- opens external links in system browser

Important runtime assumption:

- `webSecurity: false` is enabled so a file-origin page can call external or local APIs

This is a shortcut, not a durable production architecture.

### `package.json`

Important facts:

- packages `dist/**/*` and `electron/**/*`
- does not package the Python backend
- does not package models
- does not define any backend startup logic

Conclusion:

The packaged app is frontend-only unless the backend is started separately.

### `vite.config.js`

Current state:

- the legacy proxy to MuAPI has been removed

Conclusion:

The frontend dev config no longer routes through external inference assumptions.

### `afterPack.js`

Current role:

- ad-hoc macOS codesigning

Conclusion:

Packaging support is minimal and unrelated to backend execution.

## Styling and UI System Findings

### Current styling state

- `src/style.css` imports `global.css` and `studio.css`
- `global.css` defines Tailwind theme tokens and utilities
- `variables.css` defines a second token system
- `variables.css` is not imported by the main stylesheet

### Result

There is design-token drift:

- active theme tokens live in `global.css`
- legacy tokens still exist in `variables.css`
- some legacy CSS in `studio.css` references the older variable set

This is not urgent for the execution refactor, but it should be cleaned up before the later UI redesign pass.

## Dependency on Legacy MuAPI Concepts

Legacy concepts still embedded in the app:

- MuAPI API key storage
- MuAPI auth modal
- MuAPI settings modal
- MuAPI client facade
- MuAPI upload flow
- MuAPI request/polling assumptions
- Vite proxy to MuAPI

This is the largest cross-cutting migration issue in the repo.

## Gap Between Current and Target Architecture

### Target

```text
frontend/
  components/
  api/
  state/

backend/
  server.py
  jobs/
  scheduler/
  workers/
  models/
  storage/
```

### Current

```text
backend/
  server.py

src/
  components/
  lib/
```

### Main gaps

- no modular backend boundaries
- no dedicated workers
- no scheduler
- no storage layer
- frontend still owns execution assumptions
- model registry lives in the UI
- most studios are not yet on the local job system

## Feature Preservation Rule

The refactor is not a feature reduction project.

The correct migration strategy is:

1. inventory the capabilities the current app already exposes
2. preserve those capabilities at the product level
3. remove the legacy implementation path behind them
4. replace that implementation with our own backend pipeline
5. use the replacement as the foundation for expansion

That means the goal is not to keep MuAPI-era code alive. The goal is to keep the app's feature set alive while swapping the execution engine underneath it.

### Current capability targets to preserve

- image generation
- image-to-image workflows
- video generation
- image-to-video workflows
- video-to-video workflows
- lipsync workflows
- cinematic prompt construction and camera control abstractions
- upload selection and asset reuse
- job polling and result presentation
- model selection and parameter selection in each studio

### What should be removed over time

- MuAPI-specific client contracts
- MuAPI key storage and gating
- fake transport stubs
- frontend-owned execution assumptions
- ad hoc localStorage job persistence where backend job state should exist

### What should replace it

- our own typed job schema
- our own upload and asset handoff pipeline
- our own scheduler and worker ownership by task type
- our own model registry and capability exposure
- our own output storage and retrieval contract
- our own status, failure, and retry handling
- our own GPU execution path, local or remote

Already removed from active runtime:

- the MuAPI client facade in `src/lib/muapi.js`
- MuAPI key prompts in `AuthModal.js`
- MuAPI key settings in `SettingsModal.js`
- the Vite MuAPI proxy in `vite.config.js`

## Migration Matrix

This matrix translates current product features into replacement targets inside our own pipeline.

| Capability | Current UI Surface | Current Implementation | Target Job Type | Target Backend Owner | Replacement Goal |
| --- | --- | --- | --- | --- | --- |
| text-to-image | `ImageStudio` | local `/jobs` plus migration leftovers | `image.generate` | `workers/image_worker` | keep working path, clean transport and schema |
| image-to-image | `ImageStudio` | MuAPI-shaped UI/model assumptions | `image.transform` | `workers/image_worker` | move edits and references to our job contract |
| text-to-video | `VideoStudio` | local typed job + placeholder video worker | `video.generate` | `workers/video_worker` | replace placeholder worker with real video execution |
| image-to-video | `VideoStudio` | local typed job + backend asset ingest | `video.animate_image` | `workers/video_worker` | replace placeholder worker with real image-to-video execution |
| video-to-video | `VideoStudio` | local typed job + backend asset ingest | `video.transform` | `workers/video_worker` | replace placeholder worker with real video transform execution |
| image lipsync | `LipSyncStudio` | local typed job + placeholder lipsync worker | `lipsync.image_audio` | `workers/lipsync_worker` | replace placeholder worker with real portrait + audio execution |
| video lipsync | `LipSyncStudio` | local typed job + placeholder lipsync worker | `lipsync.video_audio` | `workers/lipsync_worker` | replace placeholder worker with real video + audio execution |
| cinematic prompting | `CinemaStudio` + `CameraControls` | local image job with cinematic params | `image.generate` with cinematic params | `workers/image_worker` | preserve camera/lens/focal controls on our backend |
| asset upload and reuse | `UploadPicker` | backend asset ingest + localStorage history | `asset.upload` or direct asset ingest | `storage/assets` | replace local-only convenience history with backend-aware asset management later |
| job polling and result state | all studios | local `/jobs` + localStorage resume polling | `job.status` | `jobs/` | one status model across all task types |
| model selection | all studios | frontend-owned `models.js` | `models.list` / `models.describe` | `models/registry` | backend becomes source of truth |

## Implementation Checklist

This is the concrete checklist to prepare the replacement.

### 1. Freeze the feature surface

- treat `ImageStudio`, `VideoStudio`, `LipSyncStudio`, and `CinemaStudio` as product contracts
- preserve visible controls, inputs, and result views unless there is a strong reason to change them later
- document any feature that is currently fake or partially wired so it is not mistaken for complete backend support

### 2. Define the backend job contract

- create a typed job schema that covers:
- `image.generate`
- `image.transform`
- `video.generate`
- `video.animate_image`
- `video.transform`
- `lipsync.image_audio`
- `lipsync.video_audio`
- standardize shared job fields:
- `job_id`
- `type`
- `status`
- `created_at`
- `updated_at`
- `input_assets`
- `params`
- `result_assets`
- `error`
- add lifecycle states:
- `queued`
- `processing`
- `completed`
- `failed`
- `cancelled`

### 3. Define backend ownership by module

- `backend/jobs/`
  owns job records, validation, and status transitions
- `backend/scheduler/`
  owns routing from job type to worker
- `backend/workers/image_worker.py`
  owns text-to-image and image-to-image execution
- `backend/workers/video_worker.py`
  owns text-to-video, image-to-video, and video-to-video execution
- `backend/workers/lipsync_worker.py`
  owns portrait/video + audio lipsync execution
- `backend/models/`
  owns model descriptors and compatibility metadata
- `backend/storage/`
  owns asset ingest, output paths, and retrieval rules

### 4. Replace shared frontend transport first

- expand `src/lib/localapi.js` into a typed API client instead of a hardcoded image-only helper
- move upload operations out of MuAPI assumptions and into backend asset endpoints
- centralize polling/status logic so studios stop reimplementing it

### 5. Migrate shared utilities before studio internals

- make `UploadPicker` accept an injected uploader/client instead of calling `muapi.uploadFile`
- keep `uploadHistory.js` only as a local UI convenience, not as the system of record
- preserve `promptUtils.js` and `CameraControls.js`, but route execution through our backend
- repurpose `AuthModal` and `SettingsModal` away from API keys toward backend/runtime settings or remove them once obsolete

### 6. Migrate studios in safest order

1. `ImageStudio`
   Remove migration leftovers and make it the canonical job-client pattern.
2. `CinemaStudio`
   Reuse the image pipeline with cinematic params instead of a separate image path.
3. `VideoStudio`
   Replace all t2v, i2v, and v2v calls with typed local video jobs.
4. `LipSyncStudio`
   Replace both lipsync modes with typed local lipsync jobs.

Status:

- this migration sequence is now completed at the contract level
- the remaining work is replacing placeholder backend workers with real execution modules

### 7. Preserve UX while swapping internals

- keep current user flows recognizable
- map current controls to backend params instead of deleting them
- keep result panels and polling feedback while changing the transport underneath
- do not block migration on final UI polish

### 8. Create explicit deprecation targets

- `AuthModal.js`
- `SettingsModal.js`
- MuAPI-specific pending job semantics in `pendingJobs.js`

These should be removed only after the replacement path is working.

## Immediate Build Plan

If implementation starts now, use this order:

1. design the typed job payloads and status schema
2. split `backend/server.py` into `jobs`, `storage`, and worker-routing seams without changing current image behavior
3. replace the old external client layer with a single local client layer
4. convert `UploadPicker` to use our asset pipeline
5. make `ImageStudio` the clean reference implementation
6. port `CinemaStudio` onto the same image job path
7. port `VideoStudio` onto typed video jobs
8. port `LipSyncStudio` onto typed lipsync jobs
9. remove obsolete MuAPI key/config UX
10. clean up stale frontend model ownership now that backend model-capability exposure has begun

## Recommended Refactor Sequence

This sequence is intended to preserve the current working image path while making the rest of the system converge.

### Phase 1: Stabilize the current backend contract

- extract job record management out of `backend/server.py`
- add explicit failure handling
- add structured job schema beyond `{ type, prompt }`
- stop loading models per job where possible
- replace raw `/tmp` assumptions with an app storage module

### Phase 2: Unify frontend transport

- define one job contract for image, video, lipsync, and cinema tasks
- move shared polling/submission/history logic into reusable frontend modules
- remove MuAPI API key gating from studios
- preserve current studio capabilities while swapping in our own execution path underneath them

### Phase 3: Introduce backend modularity

- split backend into `jobs/`, `scheduler/`, `workers/`, `models/`, and `storage/`
- add worker ownership by job type
- make model loading persistent at worker scope

### Phase 4: Move the model registry to the backend

- make backend the source of truth for available models and schemas
- let the UI fetch model capabilities instead of hardcoding them

### Phase 5: Package or manage backend runtime explicitly

- decide whether Electron manages a local Python process or talks to a remote GPU service
- stop relying on `webSecurity: false` as the integration mechanism
- make packaged-app runtime explicit and testable

### Phase 6: UI redesign

Only after the above is stable:

- clean up token duplication
- remove legacy CSS drift
- redesign the UI lightly to better reflect the finished system you are building

## Safest Immediate Priorities

If the goal is to start implementation without breaking the working path, the best next actions are:

1. document and preserve the current image job flow
2. inventory every existing studio capability that must survive the migration
3. remove fake/legacy transport assumptions from shared frontend utilities
4. design a typed local job schema that can represent image, video, lipsync, and cinematic tasks
5. split `backend/server.py` without changing its external behavior first

## Files That Are Supporting, Not Source of Truth

- `README.md`
- `project_knowledge.md`
- `models_dump.json`
- `codetxt/*`
- `docs/assets/*`

These are useful references, but they do not describe the exact runtime as reliably as the code does.

## Summary

Open Higgsfield AI already has the beginning of the right architecture, but only the image path is truly on it.

The current system is best described as:

- a strong desktop/frontend control plane
- a single experimental FastAPI backend
- one real local job path for images
- several legacy or stubbed execution paths for video, lipsync, uploads, and cinematic generation

The central refactor problem is not the UI itself. It is the split between:

- the emerging local job system
- the older MuAPI-shaped frontend assumptions

The migration rule is:

- keep the features
- replace the implementation
- build on our pipeline afterward

Solve that split first, then modularize the backend, then redesign the UI once the machine underneath it is real.
